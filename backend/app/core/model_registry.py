"""
Central model registry for lazy loading and memory management.
Ensures only one model is loaded in memory at a time.
"""
import torch
import logging
from pathlib import Path
from typing import Optional, Any, Callable
from threading import Lock
from app.core.config import settings

logger = logging.getLogger(__name__)


class ModelRegistry:
    """
    Singleton registry for managing ML model loading and memory.
    
    Features:
    - Lazy loading: Models loaded only on first use
    - Single model in memory: Unloads previous model before loading new one
    - Thread-safe: Uses lock to prevent concurrent loading
    - Memory cleanup: Calls torch.cuda.empty_cache() after unloading
    """
    
    _instance = None
    _lock = Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self._initialized = True
        self.current_model_name: Optional[str] = None
        self.current_model: Optional[Any] = None
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model_dir = Path(settings.MODEL_PATH)
        
        # Ensure model directory exists
        self.model_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"ModelRegistry initialized - Device: {self.device}")
        logger.info(f"Model directory: {self.model_dir}")
    
    def _unload_current_model(self) -> None:
        """Unload currently loaded model and free memory."""
        if self.current_model is not None:
            logger.info(f"Unloading model: {self.current_model_name}")
            
            # Delete model reference
            del self.current_model
            self.current_model = None
            self.current_model_name = None
            
            # Force garbage collection
            import gc
            gc.collect()
            
            # Clear CUDA cache if using GPU
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
                logger.info("CUDA cache cleared")
            
            logger.info("Model unloaded and memory freed")
    
    def load_model(
        self,
        model_name: str,
        load_function: Callable[[Path, torch.device], Any],
        force_reload: bool = False
    ) -> Any:
        """
        Load a model with lazy loading and memory management.
        
        Args:
            model_name: Name of the model file (e.g., "deepfake_model_enhanced.pt")
            load_function: Function that loads the model given (path, device)
            force_reload: If True, reload even if already loaded
        
        Returns:
            Loaded model
        
        Raises:
            FileNotFoundError: If model file doesn't exist
            RuntimeError: If model loading fails
        """
        with self._lock:
            # Check if model already loaded
            if not force_reload and self.current_model_name == model_name:
                logger.info(f"Model '{model_name}' already loaded - reusing")
                return self.current_model
            
            # Check if model file exists
            model_path = self.model_dir / model_name
            if not model_path.exists():
                error_msg = f"Model file not found: {model_path}"
                logger.error(error_msg)
                raise FileNotFoundError(error_msg)
            
            # Unload previous model if different
            if self.current_model_name and self.current_model_name != model_name:
                logger.info(f"Switching from '{self.current_model_name}' to '{model_name}'")
                self._unload_current_model()
            
            # Load new model
            logger.info(f"Loading model: {model_name}")
            logger.info(f"Model path: {model_path}")
            logger.info(f"File size: {model_path.stat().st_size / 1024 / 1024:.2f} MB")
            
            try:
                model = load_function(model_path, self.device)
                
                # Store reference
                self.current_model = model
                self.current_model_name = model_name
                
                logger.info(f"✅ Model '{model_name}' loaded successfully")
                return model
                
            except Exception as e:
                logger.error(f"Failed to load model '{model_name}': {e}")
                logger.exception("Full traceback:")
                raise RuntimeError(f"Model loading failed: {e}") from e
    
    def get_current_model(self) -> Optional[Any]:
        """Get currently loaded model without loading."""
        return self.current_model
    
    def get_current_model_name(self) -> Optional[str]:
        """Get name of currently loaded model."""
        return self.current_model_name
    
    def is_model_loaded(self, model_name: str) -> bool:
        """Check if a specific model is currently loaded."""
        return self.current_model_name == model_name and self.current_model is not None
    
    def unload_all(self) -> None:
        """Unload all models and free memory."""
        with self._lock:
            if self.current_model is not None:
                self._unload_current_model()
                logger.info("All models unloaded")
    
    def get_status(self) -> dict:
        """Get current registry status."""
        return {
            "current_model": self.current_model_name,
            "model_loaded": self.current_model is not None,
            "device": str(self.device),
            "model_directory": str(self.model_dir)
        }


# Global singleton instance
model_registry = ModelRegistry()
