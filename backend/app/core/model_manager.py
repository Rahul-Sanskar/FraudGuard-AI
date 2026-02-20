"""
Central model manager for safe model loading and fallback handling.
Ensures the application never crashes due to missing model files.
"""
import os
import logging
from pathlib import Path
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)


class ModelManager:
    """
    Centralized model management with safe loading and fallback support.
    """
    
    def __init__(self):
        # Determine base directory (works in Docker and local)
        self.BASE_DIR = Path(__file__).resolve().parent.parent.parent
        self.MODEL_DIR = self.BASE_DIR / "ml_models"
        
        # Create ml_models directory if it doesn't exist
        self.MODEL_DIR.mkdir(parents=True, exist_ok=True)
        logger.info(f"Model directory: {self.MODEL_DIR}")
        
        # Model storage URL from environment (optional)
        self.model_storage_url = os.getenv("MODEL_STORAGE_URL", "")
        
        # Track which models are available
        self.available_models: Dict[str, bool] = {}
        
        self._check_models()
    
    def _check_models(self) -> None:
        """Check which model files are present."""
        expected_models = [
            "deepfake_model_enhanced.pt",
            "document_model.pt",
            "voice_spoof_model.pt"
        ]
        
        logger.info("=" * 60)
        logger.info("MODEL AVAILABILITY CHECK")
        logger.info("=" * 60)
        
        for model_name in expected_models:
            model_path = self.MODEL_DIR / model_name
            exists = model_path.exists()
            self.available_models[model_name] = exists
            
            if exists:
                size_mb = model_path.stat().st_size / (1024 * 1024)
                logger.info(f"✅ {model_name}: Found ({size_mb:.1f} MB)")
            else:
                logger.warning(f"❌ {model_name}: Not found - will use mock predictions")
        
        logger.info("=" * 60)
        
        # Log summary
        available_count = sum(self.available_models.values())
        total_count = len(expected_models)
        
        if available_count == 0:
            logger.warning("⚠️  NO MODELS FOUND - All services will use mock predictions")
            logger.warning("⚠️  Upload models to ml_models/ or set MODEL_STORAGE_URL")
        elif available_count < total_count:
            logger.warning(f"⚠️  PARTIAL MODELS: {available_count}/{total_count} available")
        else:
            logger.info(f"✅ ALL MODELS AVAILABLE: {available_count}/{total_count}")
    
    def get_model_path(self, model_name: str) -> Path:
        """Get the full path to a model file."""
        return self.MODEL_DIR / model_name
    
    def is_model_available(self, model_name: str) -> bool:
        """Check if a specific model is available."""
        return self.available_models.get(model_name, False)
    
    def safe_load_model(
        self,
        model_name: str,
        load_function: callable,
        device: Any
    ) -> Optional[Any]:
        """
        Safely load a model with fallback to None if not available.
        
        Args:
            model_name: Name of the model file
            load_function: Function to load the model
            device: PyTorch device (cpu/cuda)
        
        Returns:
            Loaded model or None if unavailable
        """
        model_path = self.get_model_path(model_name)
        
        if not model_path.exists():
            logger.warning(f"Model file not found: {model_path}")
            logger.warning(f"Service will use mock predictions for {model_name}")
            return None
        
        try:
            logger.info(f"Loading model: {model_name}")
            model = load_function(model_path, device)
            logger.info(f"✅ Successfully loaded: {model_name}")
            return model
        except Exception as e:
            logger.error(f"❌ Failed to load {model_name}: {e}")
            logger.warning(f"Service will use mock predictions for {model_name}")
            return None
    
    def download_model_from_url(self, model_name: str, url: str) -> bool:
        """
        Download a model from a URL (future implementation).
        
        Args:
            model_name: Name of the model file
            url: URL to download from
        
        Returns:
            True if successful, False otherwise
        """
        # Placeholder for future implementation
        logger.info(f"Model download not yet implemented: {model_name} from {url}")
        return False
    
    def get_status(self) -> Dict[str, Any]:
        """Get model availability status."""
        return {
            "model_directory": str(self.MODEL_DIR),
            "models": self.available_models,
            "total_models": len(self.available_models),
            "available_models": sum(self.available_models.values()),
            "storage_url_configured": bool(self.model_storage_url)
        }


# Global instance
model_manager = ModelManager()
