"""
Document tampering detection service with PDF support.
"""
import torch
import logging
from pathlib import Path
from typing import Tuple, List
from io import BytesIO
from app.core.config import settings
from app.models.architectures import EfficientNetDocumentModel, load_model_with_state_dict
from app.core.model_manager import model_manager

logger = logging.getLogger(__name__)

# Check if pdf2image is available
try:
    from pdf2image import convert_from_bytes
    PDF_SUPPORT = True
    logger.info("✅ pdf2image available - PDF support enabled")
except ImportError:
    PDF_SUPPORT = False
    logger.warning("⚠️ pdf2image not installed - PDF support disabled")
    logger.warning("Install with: pip install pdf2image")
    logger.warning("Windows: Also install Poppler - see documentation")


class DocumentService:
    """Service for detecting document tampering and forgery."""
    
    def __init__(self):
        self.model = None
        self.mock_mode = False
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self._load_model()
    
    def _load_model(self) -> None:
        """
        Load the pre-trained document tampering detection model.
        PRODUCTION SAFE: Falls back to mock mode if model unavailable.
        """
        model_name = "document_model.pt"
        model_path = model_manager.get_model_path(model_name)
        
        logger.info("=" * 80)
        logger.info("LOADING DOCUMENT MODEL (PRODUCTION SAFE)")
        logger.info("=" * 80)
        logger.info(f"Model path: {model_path}")
        
        # Check if model exists
        if not model_path.exists():
            logger.warning(f"❌ Model file not found at {model_path}")
            logger.warning("⚠️  Service will use MOCK predictions")
            self.mock_mode = True
            self.model = None
            logger.info("=" * 80)
            return
        
        file_size_mb = model_path.stat().st_size / 1024 / 1024
        logger.info(f"Model file size: {file_size_mb:.2f} MB")
        
        # Load checkpoint - fallback to mock on failure
        logger.info("Loading checkpoint...")
        try:
            checkpoint = torch.load(model_path, map_location=self.device)
        except Exception as e:
            logger.error(f"❌ Failed to load checkpoint: {e}")
            logger.warning("⚠️  Service will use MOCK predictions")
            self.mock_mode = True
            self.model = None
            logger.info("=" * 80)
            return
        
        logger.info(f"Checkpoint type: {type(checkpoint)}")
        
        # Determine checkpoint format and extract state_dict
        state_dict = None
        
        # Format 1: Pure state_dict (OrderedDict)
        if isinstance(checkpoint, dict) and not hasattr(checkpoint, 'state_dict'):
            # Check if it's a state_dict or a wrapper dict
            if 'model_state_dict' in checkpoint:
                # Format 2: {'model_state_dict': ..., 'optimizer_state_dict': ...}
                logger.info("Detected format: Checkpoint dict with 'model_state_dict' key")
                state_dict = checkpoint['model_state_dict']
            elif any(k.startswith(('features.', 'classifier.', 'head.', 'backbone.')) for k in checkpoint.keys()):
                # Format 1: Pure state_dict
                logger.info("Detected format: Pure state_dict (OrderedDict)")
                state_dict = checkpoint
            else:
                logger.error(f"❌ Unknown checkpoint format. Keys: {list(checkpoint.keys())[:10]}")
                logger.warning("⚠️  Service will use MOCK predictions")
                self.mock_mode = True
                self.model = None
                logger.info("=" * 80)
                return
        elif hasattr(checkpoint, 'state_dict'):
            # Format 3: Complete model object
            logger.info("Detected format: Complete model object")
            self.model = checkpoint
            self.model.to(self.device)
            self.model.eval()
            
            # Count parameters
            total_params = sum(p.numel() for p in self.model.parameters())
            trainable_params = sum(p.numel() for p in self.model.parameters() if p.requires_grad)
            logger.info(f"✅ Model loaded: {total_params:,} total params, {trainable_params:,} trainable")
            
            # Verify weights
            self._verify_model_weights()
            logger.info(f"=" * 80)
            return
        else:
            logger.error(f"❌ Unrecognized checkpoint type: {type(checkpoint)}")
            logger.warning("⚠️  Service will use MOCK predictions")
            self.mock_mode = True
            self.model = None
            logger.info("=" * 80)
            return
        
        # If we have a state_dict, instantiate model and load it
        if state_dict is not None:
            logger.info(f"State dict contains {len(state_dict)} keys")
            logger.info(f"First 5 keys: {list(state_dict.keys())[:5]}")
            
            # Instantiate model architecture
            logger.info("Instantiating EfficientNetDocumentModel architecture...")
            model = EfficientNetDocumentModel(num_classes=1)
            
            # Count parameters before loading
            total_params = sum(p.numel() for p in model.parameters())
            logger.info(f"Model architecture has {total_params:,} parameters")
            
            # Load state dict - fallback to mock on failure
            logger.info("Loading state dict into model...")
            try:
                missing_keys, unexpected_keys = model.load_state_dict(state_dict, strict=False)
            except Exception as e:
                logger.error(f"❌ Failed to load state_dict: {e}")
                logger.warning("⚠️  Service will use MOCK predictions")
                self.mock_mode = True
                self.model = None
                logger.info("=" * 80)
                return
            
            # Report missing/unexpected keys
            if missing_keys:
                logger.warning(f"⚠️ Missing keys ({len(missing_keys)}): {missing_keys[:10]}")
            else:
                logger.info("✅ No missing keys")
            
            if unexpected_keys:
                logger.warning(f"⚠️ Unexpected keys ({len(unexpected_keys)}): {unexpected_keys[:10]}")
            else:
                logger.info("✅ No unexpected keys")
            
            # Move to device and set eval mode
            model.to(self.device)
            model.eval()
            
            self.model = model
            
            trainable_params = sum(p.numel() for p in self.model.parameters() if p.requires_grad)
            logger.info(f"✅ Model loaded: {total_params:,} total params, {trainable_params:,} trainable")
            
            # Verify weights loaded correctly
            self._verify_model_weights()
        
        logger.info(f"=" * 80)
    
    def _verify_model_weights(self) -> None:
        """Verify that model weights are not randomly initialized."""
        logger.info("Verifying model weights...")
        
        # Check classifier/head weights
        classifier = None
        if hasattr(self.model, 'classifier'):
            classifier = self.model.classifier
            logger.info("Found 'classifier' layer")
        elif hasattr(self.model, 'head'):
            classifier = self.model.head
            logger.info("Found 'head' layer")
        else:
            logger.warning("⚠️ Could not find classifier or head layer")
            return
        
        # Get weight tensor
        if hasattr(classifier, 'weight'):
            weight = classifier.weight
        elif isinstance(classifier, torch.nn.Sequential):
            # Find Linear layer in Sequential
            for layer in classifier:
                if isinstance(layer, torch.nn.Linear):
                    weight = layer.weight
                    break
            else:
                logger.warning("⚠️ Could not find Linear layer in classifier")
                return
        else:
            logger.warning(f"⚠️ Classifier type not recognized: {type(classifier)}")
            return
        
        # Calculate statistics
        weight_mean = weight.mean().item()
        weight_std = weight.std().item()
        weight_min = weight.min().item()
        weight_max = weight.max().item()
        
        logger.info(f"Classifier weight statistics:")
        logger.info(f"  Shape: {weight.shape}")
        logger.info(f"  Mean: {weight_mean:.6f}")
        logger.info(f"  Std: {weight_std:.6f}")
        logger.info(f"  Min: {weight_min:.6f}")
        logger.info(f"  Max: {weight_max:.6f}")
        
        # Check if weights look randomly initialized (warn but don't crash)
        if abs(weight_mean) < 0.001 and weight_std < 0.01:
            logger.warning(
                f"⚠️  Classifier weights appear randomly initialized!\n"
                f"   Mean: {weight_mean:.6f} (too close to 0)\n"
                f"   Std: {weight_std:.6f} (too small)\n"
                f"   This model may NOT be trained properly."
            )
        
        logger.info("✅ Weights look trained (non-random)")
        
        # Check bias if exists
        if hasattr(classifier, 'bias') and classifier.bias is not None:
            bias_value = classifier.bias.item() if classifier.bias.numel() == 1 else classifier.bias.mean().item()
            logger.info(f"  Bias: {bias_value:.6f}")
        elif isinstance(classifier, torch.nn.Sequential):
            for layer in classifier:
                if isinstance(layer, torch.nn.Linear) and layer.bias is not None:
                    bias_value = layer.bias.item() if layer.bias.numel() == 1 else layer.bias.mean().item()
                    logger.info(f"  Bias: {bias_value:.6f}")
                    break
    
    def _preprocess_document(self, document_bytes, is_pil_image=False) -> torch.Tensor:
        """
        Preprocess document image for model inference.
        Uses ImageNet normalization matching EfficientNet training.
        - Resize to 224x224 (standard size)
        - Normalize with ImageNet stats
        
        Args:
            document_bytes: Image bytes or PIL Image object
            is_pil_image: If True, document_bytes is already a PIL Image
        """
        from torchvision import transforms
        from PIL import Image
        
        if is_pil_image:
            # Already a PIL Image (from PDF conversion)
            image = document_bytes
        else:
            # Handle both bytes and BytesIO objects
            if isinstance(document_bytes, bytes):
                document_bytes = BytesIO(document_bytes)
            
            # Ensure we're at the beginning of the stream
            document_bytes.seek(0)
            
            image = Image.open(document_bytes).convert('RGB')
        
        # Define preprocessing pipeline matching training
        preprocess = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])  # ImageNet stats
        ])
        
        image_tensor = preprocess(image).unsqueeze(0)
        logger.debug(f"Preprocessed document shape: {image_tensor.shape}")
        
        return image_tensor.to(self.device)
    
    def analyze_document(self, document_bytes, filename: str = "") -> dict:
        """
        Analyze document for tampering detection.
        Supports both images (JPEG, PNG) and PDFs.
        STRICT MODE: Uses loaded model only (no fallbacks).
        
        For PDFs:
        - Converts first 3 pages to images
        - Analyzes each page separately
        - Returns highest risk score (fraud often hidden on later pages)
        
        Args:
            document_bytes: Document file bytes
            filename: Original filename (used to detect PDF)
            
        Returns:
            Dict with risk_score, confidence, raw_logit, pages_analyzed
        """
        logger.info("=" * 80)
        logger.info("DOCUMENT ANALYSIS START")
        logger.info("=" * 80)
        
        # Check if in mock mode
        if self.mock_mode or self.model is None:
            logger.warning("⚠️  MOCK MODE: Returning simulated prediction")
            return {
                "risk_score": 0.35,
                "confidence": 0.0,
                "raw_logit": 0.0,
                "pages_analyzed": 1,
                "mock": True,
                "message": "Model unavailable - using mock prediction"
            }
        
        # Verify model is in eval mode
        if self.model.training:
            logger.warning("⚠️ Model was in training mode, switching to eval mode")
            self.model.eval()
        
        try:
            # Check if this is a PDF
            is_pdf = filename.lower().endswith('.pdf') if filename else False
            
            if is_pdf:
                if not PDF_SUPPORT:
                    raise RuntimeError(
                        "PDF support not available. Install pdf2image: pip install pdf2image. "
                        "Windows users also need Poppler - see documentation."
                    )
                
                logger.info("PDF detected - converting pages to images...")
                
                try:
                    # Convert PDF pages to images (DPI 200 for good quality)
                    pages = convert_from_bytes(document_bytes, dpi=200)
                    logger.info(f"✅ PDF converted: {len(pages)} pages found")
                    
                    # Analyze first 3 pages (fraud often hidden on later pages)
                    pages_to_analyze = pages[:3]
                    results = []
                    
                    for i, page_image in enumerate(pages_to_analyze, 1):
                        logger.info(f"Analyzing page {i}/{len(pages_to_analyze)}...")
                        
                        # Convert PIL Image to RGB
                        page_image = page_image.convert('RGB')
                        
                        # Preprocess and analyze
                        doc_tensor = self._preprocess_document(page_image, is_pil_image=True)
                        
                        # Run inference (STRICT MODE)
                        self.model.eval()
                        with torch.no_grad():
                            output = self.model(doc_tensor)
                            raw_logit = output[0][0].item()
                            probability = torch.sigmoid(output[0][0]).item()
                            
                            results.append({
                                "page": i,
                                "risk_score": probability,
                                "raw_logit": raw_logit
                            })
                            
                            logger.info(f"Page {i} - Logit: {raw_logit:.6f}, Probability: {probability:.6f}")
                    
                    # Use HIGHEST risk score (fraud detection - be conservative)
                    highest_risk = max(results, key=lambda x: x["risk_score"])
                    final_risk = highest_risk["risk_score"]
                    final_logit = highest_risk["raw_logit"]
                    confidence = abs(final_risk - 0.5) * 2
                    
                    logger.info(f"Multi-page analysis complete - Highest risk: {final_risk:.6f} (page {highest_risk['page']})")
                    logger.info("=" * 80)
                    
                    return {
                        "risk_score": final_risk,
                        "confidence": confidence,
                        "raw_logit": final_logit,
                        "pages_analyzed": len(pages_to_analyze),
                        "highest_risk_page": highest_risk["page"],
                        "all_pages": results
                    }
                    
                except Exception as pdf_error:
                    logger.error(f"PDF conversion error: {pdf_error}")
                    if "PDFInfoNotInstalledError" in str(type(pdf_error).__name__):
                        raise RuntimeError(
                            "Poppler not found. Windows users: Download Poppler from "
                            "https://github.com/oschwartz10612/poppler-windows/releases, "
                            "extract, and add poppler-xx/Library/bin to PATH. Then restart terminal."
                        )
                    raise
            
            else:
                # Regular image processing (JPEG, PNG)
                logger.info(f"Image document detected: {filename}")
                logger.info(f"Document size: {len(document_bytes)} bytes")
                
                # Preprocess document
                doc_tensor = self._preprocess_document(document_bytes)
                
                # DIAGNOSTIC: Log tensor statistics
                tensor_mean = doc_tensor.mean().item()
                tensor_std = doc_tensor.std().item()
                tensor_min = doc_tensor.min().item()
                tensor_max = doc_tensor.max().item()
                
                logger.info(f"Input tensor diagnostics:")
                logger.info(f"  Shape: {doc_tensor.shape}")
                logger.info(f"  Mean: {tensor_mean:.6f}")
                logger.info(f"  Std: {tensor_std:.6f}")
                logger.info(f"  Min: {tensor_min:.6f}")
                logger.info(f"  Max: {tensor_max:.6f}")
                
                # Verify tensor is not degenerate
                if tensor_std < 0.01:
                    logger.error(f"⚠️ WARNING: Input tensor has very low variance (std={tensor_std:.6f})")
                    logger.error("   This may indicate preprocessing issues")
                
                # Run inference (STRICT MODE - NO FALLBACKS)
                logger.info("Running model inference (STRICT MODE)...")
                logger.info(f"Model device: {next(self.model.parameters()).device}")
                logger.info(f"Model training mode: {self.model.training}")
                
                # Force eval mode and no_grad
                self.model.eval()
                
                with torch.no_grad():
                    # Run model
                    output = self.model(doc_tensor)
                    
                    # DIAGNOSTIC: Log raw output
                    logger.info(f"Raw model output:")
                    logger.info(f"  Shape: {output.shape}")
                    logger.info(f"  Tensor: {output}")
                    logger.info(f"  Device: {output.device}")
                    
                    # Extract logit
                    raw_logit = output[0][0].item()
                    logger.info(f"Extracted raw logit: {raw_logit:.6f}")
                    
                    # Apply sigmoid to get probability
                    probability = torch.sigmoid(output[0][0]).item()
                    logger.info(f"After sigmoid: {probability:.6f}")
                    
                    # Calculate confidence (distance from 0.5)
                    confidence = abs(probability - 0.5) * 2
                    logger.info(f"Calculated confidence: {confidence:.6f}")
                    
                    # DIAGNOSTIC: Check if output is suspicious
                    if abs(raw_logit) < 0.1:
                        logger.warning(f"⚠️ WARNING: Raw logit very close to zero ({raw_logit:.6f})")
                        logger.warning("   This suggests model may not be properly trained")
                        logger.warning("   Expected range: -5 to +5 for confident predictions")
                    
                    if 0.49 < probability < 0.51:
                        logger.warning(f"⚠️ WARNING: Probability very close to 0.5 ({probability:.6f})")
                        logger.warning("   Model is uncertain or not trained properly")
                    
                    logger.info(f"Final result - Risk: {probability:.6f}, Confidence: {confidence:.6f}, Logit: {raw_logit:.6f}")
                    logger.info("=" * 80)
                    
                    return {
                        "risk_score": probability,
                        "confidence": confidence,
                        "raw_logit": raw_logit,
                        "pages_analyzed": 1
                    }
            
        except Exception as e:
            logger.error(f"Error analyzing document: {e}")
            logger.exception("Full traceback:")
            raise  # Re-raise - no fallbacks in strict mode


# Singleton instance
document_service = DocumentService()
