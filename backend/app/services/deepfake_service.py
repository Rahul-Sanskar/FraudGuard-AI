"""
Deepfake detection service for image and video analysis.
"""
import torch
import numpy as np
from pathlib import Path
from typing import Tuple
from PIL import Image
import cv2
from io import BytesIO
from app.core.logging import get_logger
from app.core.config import settings
from app.models.architectures import EfficientNetDeepfakeModel, load_model_with_state_dict
from app.services.anti_spoof_service import AntiSpoofDetector

logger = get_logger(__name__)


class DeepfakeService:
    """Service for detecting deepfake images and videos with anti-spoofing."""
    
    def __init__(self):
        self.model_path = Path(settings.MODEL_PATH) / "deepfake_model_enhanced.pt"
        self.model = None
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.anti_spoof = AntiSpoofDetector()
        self._load_model()
    
    def _load_model(self) -> None:
        """Load the pre-trained deepfake detection model."""
        try:
            if self.model_path.exists():
                logger.info(f"Loading deepfake model from {self.model_path}")
                
                # Load the model checkpoint
                checkpoint = torch.load(self.model_path, map_location=self.device)
                
                # Check if it's a state_dict (OrderedDict) or complete model
                if isinstance(checkpoint, dict) and not hasattr(checkpoint, 'state_dict'):
                    # It's a state_dict - need to instantiate architecture
                    logger.info("Detected state_dict format. Loading with EfficientNet architecture...")
                    
                    try:
                        # Instantiate the model architecture
                        model = EfficientNetDeepfakeModel(num_classes=2)
                        
                        # Load the state dict
                        model.load_state_dict(checkpoint, strict=False)
                        model.to(self.device)
                        model.eval()
                        
                        self.model = model
                        logger.info(f"✅ Deepfake model loaded successfully from {self.model_path}")
                        
                        # Verify model weights loaded correctly
                        if hasattr(model, 'head') and hasattr(model.head, '6'):
                            classifier_weight = model.head[6].weight
                            logger.info(f"Classifier weight mean: {classifier_weight.mean().item():.6f}")
                            logger.info(f"Classifier weight std: {classifier_weight.std().item():.6f}")
                    except Exception as e:
                        logger.error(f"Error loading state_dict: {e}")
                        logger.warning("Using mock predictions.")
                        self.model = None
                else:
                    # Model saved as complete object
                    self.model = checkpoint
                    self.model.to(self.device)
                    self.model.eval()
                    logger.info(f"✅ Deepfake model loaded successfully from {self.model_path}")
            else:
                logger.warning(f"Model not found at {self.model_path}. Using mock predictions.")
        except Exception as e:
            logger.error(f"Error loading deepfake model: {e}")
            logger.warning("Using mock predictions.")
            self.model = None
    
    def _preprocess_image(self, image_bytes) -> torch.Tensor:
        """
        Preprocess image for model inference.
        CRITICAL: Must match training preprocessing exactly.
        - Resize to 224x224 (standard ImageNet size)
        - Normalize with ImageNet stats: mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]
        """
        from torchvision import transforms
        
        # Handle both bytes and BytesIO objects
        if isinstance(image_bytes, bytes):
            image_bytes = BytesIO(image_bytes)
        
        # Ensure we're at the beginning of the stream
        image_bytes.seek(0)
        
        image = Image.open(image_bytes).convert('RGB')
        
        # Define preprocessing pipeline (MUST match training)
        # Using ImageNet normalization for EfficientNet models
        preprocess = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        ])
        
        image_tensor = preprocess(image).unsqueeze(0)
        
        # Debug: Print tensor statistics to verify preprocessing
        logger.info(f"Tensor stats - min: {image_tensor.min():.3f}, max: {image_tensor.max():.3f}, mean: {image_tensor.mean():.3f}")
        logger.debug(f"Preprocessed image shape: {image_tensor.shape}")
        
        return image_tensor.to(self.device)
    
    def analyze_image(self, image_bytes, is_live: bool = False) -> dict:
        """
        Analyze an image for deepfake detection with optional anti-spoofing.
        
        Args:
            image_bytes: Image data as bytes or BytesIO
            is_live: If True, runs anti-spoofing (screen detection) for live webcam.
                     If False, skips anti-spoofing for static uploads.
        
        Pipeline:
        1. Run anti-spoofing checks (ONLY if is_live=True)
        2. Run deepfake model inference
        3. Combine scores with weighted fusion (or use model score only if not live)
        
        Returns:
            Dict with risk_score, confidence, raw_logit, and explanations
        """
        logger.info(f"=== IMAGE ANALYSIS START (is_live={is_live}) ===")
        
        try:
            if self.model is None:
                logger.warning("Model not loaded, using mock prediction")
                return {
                    "risk_score": 0.15,
                    "confidence": 0.85,
                    "raw_logit": -1.73
                }
            
            # STEP 1: Anti-spoofing (ONLY for live webcam)
            spoof_score = 0.0
            screen_score = 0.0
            glare_score = 0.0
            flatness_score = 0.0
            motion_score = 0.0
            color_score = 0.0
            anti_spoof_data = None
            
            if is_live:
                # Convert image to OpenCV format for anti-spoofing
                if isinstance(image_bytes, bytes):
                    image_bytes_copy = BytesIO(image_bytes)
                else:
                    image_bytes.seek(0)
                    image_bytes_copy = BytesIO(image_bytes.read())
                    image_bytes.seek(0)
                
                # Load as PIL then convert to OpenCV
                pil_image = Image.open(image_bytes_copy).convert('RGB')
                frame = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)
                
                # Run anti-spoofing checks
                logger.info("Running anti-spoofing detection (LIVE MODE)...")
                spoof_results = self.anti_spoof.analyze_frame(frame)
                
                screen_score = spoof_results["screen_pattern"]
                glare_score = spoof_results["screen_glare"]
                flatness_score = spoof_results["screen_flatness"]
                motion_score = spoof_results["motion_anomaly"]
                color_score = spoof_results["color_distortion"]
                spoof_score = spoof_results["combined_spoof_score"]
                
                logger.info(f"Anti-spoof scores - Screen: {screen_score:.3f}, Glare: {glare_score:.3f}, Flatness: {flatness_score:.3f}, Motion: {motion_score:.3f}, Color: {color_score:.3f}")
                logger.info(f"Combined spoof score: {spoof_score:.3f}")
                
                # ========================================
                # HARD ANTI-SPOOF GATE (CRITICAL)
                # ========================================
                # If screen replay artifacts detected, immediately return HIGH RISK
                # Do NOT run model inference - screen detection overrides everything
                
                if screen_score > 0.45 or flatness_score > 0.55:
                    logger.warning("🚨 SCREEN REPLAY DETECTED - HARD OVERRIDE ACTIVATED")
                    logger.warning(f"   Screen pattern: {screen_score:.3f} (threshold: 0.45)")
                    logger.warning(f"   Screen flatness: {flatness_score:.3f} (threshold: 0.55)")
                    logger.warning("   Bypassing model inference - returning HIGH RISK")
                    
                    # Build explanation
                    explanations = []
                    if screen_score > 0.45:
                        explanations.append("Phone/monitor screen artifacts detected (moire patterns, grid noise)")
                    if flatness_score > 0.55:
                        explanations.append("Flat surface detected (lack of natural facial depth)")
                    if glare_score > 0.4:
                        explanations.append("Display glare pattern detected")
                    
                    explanation_text = "; ".join(explanations) + ". REPLAY ATTACK DETECTED."
                    
                    logger.info("=== IMAGE ANALYSIS COMPLETE (ANTI-SPOOF OVERRIDE) ===")
                    
                    return {
                        "risk_score": 0.92,  # 92% risk
                        "confidence": 0.90,  # 90% confidence
                        "raw_logit": 2.5,
                        "explanation": explanation_text,
                        "anti_spoof": {
                            "screen_pattern": screen_score,
                            "screen_glare": glare_score,
                            "screen_flatness": flatness_score,
                            "motion_anomaly": motion_score,
                            "color_distortion": color_score,
                            "combined": spoof_score,
                            "override_triggered": True
                        },
                        "model_score": None  # Model not run
                    }
                
                logger.info("No screen replay detected - proceeding with model inference...")
                
                anti_spoof_data = {
                    "screen_pattern": screen_score,
                    "screen_glare": glare_score,
                    "screen_flatness": flatness_score,
                    "motion_anomaly": motion_score,
                    "color_distortion": color_score,
                    "combined": spoof_score,
                    "override_triggered": False
                }
            else:
                logger.info("Static upload mode - SKIPPING anti-spoofing checks")
            
            # STEP 2: Run deepfake model inference
            logger.info("Running deepfake model inference...")
            image_tensor = self._preprocess_image(image_bytes)
            
            # Run inference with no gradient computation
            self.model.eval()
            with torch.no_grad():
                output = self.model(image_tensor)
                logger.info(f"Model output shape: {output.shape}")
                logger.info(f"Raw output: {output}")
                
                # Handle 2-class output (Real vs Fake)
                if output.shape[-1] == 2:
                    # Apply softmax to get probabilities
                    probabilities = torch.softmax(output, dim=-1)
                    
                    # Log both class probabilities
                    class_0_prob = probabilities[0][0].item()
                    class_1_prob = probabilities[0][1].item()
                    logger.info(f"Class 0 prob: {class_0_prob:.3f}, Class 1 prob: {class_1_prob:.3f}")
                    
                    # REVERSED labels: class_0=fake, class_1=real
                    real_prob = class_1_prob
                    fake_prob = class_0_prob
                    model_score = fake_prob
                    
                    logger.info(f"Model prediction - Real: {real_prob:.3f}, Fake: {fake_prob:.3f}")
                    
                else:
                    # Single output - use sigmoid
                    raw_logit = output[0][0].item()
                    model_score = torch.sigmoid(output[0][0]).item()
                    logger.info(f"Single output - Logit: {raw_logit:.3f}, Sigmoid: {model_score:.3f}")
            
            # STEP 3: Combine model score with anti-spoofing scores (if live mode)
            if is_live:
                # Weighted fusion: 60% model, 40% anti-spoofing
                final_score = (
                    0.60 * model_score +
                    0.40 * spoof_score
                )
                final_score = min(final_score, 1.0)
                logger.info(f"Score fusion (LIVE) - Model: {model_score:.3f}, Spoof: {spoof_score:.3f}, Final: {final_score:.3f}")
            else:
                # Static mode: use model score only
                final_score = model_score
                logger.info(f"Score (STATIC) - Model only: {model_score:.3f}")
            
            # STEP 4: Generate explanation
            explanations = []
            
            if is_live:
                # Live mode: include anti-spoofing indicators
                if screen_score > 0.5:
                    explanations.append("Screen replay artifacts detected (moire patterns)")
                if glare_score > 0.4:
                    explanations.append("Display glare pattern detected")
                if motion_score > 0.6:
                    explanations.append("Low natural facial motion detected")
                if color_score > 0.5:
                    explanations.append("Color distortion typical of screen displays")
            
            if model_score > 0.7:
                explanations.append("Deepfake model detected synthetic features")
            
            if not explanations:
                if final_score < 0.3:
                    explanations.append("Image appears authentic with natural characteristics")
                else:
                    explanations.append("Some suspicious patterns detected")
            
            explanation_text = "; ".join(explanations)
            
            # Calculate confidence
            confidence = max(final_score, 1.0 - final_score)
            
            logger.info(f"Final result - Risk: {final_score:.3f}, Confidence: {confidence:.3f}")
            logger.info(f"Explanation: {explanation_text}")
            logger.info("=== IMAGE ANALYSIS COMPLETE ===")
            
            result = {
                "risk_score": final_score,
                "confidence": confidence,
                "raw_logit": output[0][1].item() if output.shape[-1] == 2 else output[0][0].item(),
                "explanation": explanation_text,
                "model_score": model_score
            }
            
            # Add anti-spoof data only if live mode
            if is_live and anti_spoof_data:
                result["anti_spoof"] = anti_spoof_data
            
            return result
            
        except Exception as e:
            logger.error(f"Error analyzing image: {e}")
            logger.exception("Full traceback:")
            raise
    
    def analyze_video(self, video_bytes: bytes) -> dict:
        """
        Analyze a video for deepfake detection.
        Extracts frames, analyzes each, and aggregates results.
        
        Returns:
            Dict with risk_score, confidence, frame_count, highest_frame_score
        """
        try:
            if self.model is None:
                logger.warning("Model not loaded, using mock prediction")
                return {
                    "risk_score": 0.25,
                    "confidence": 0.78,
                    "frame_count": 0,
                    "highest_frame_score": 0.25
                }
            
            # Save video bytes to temporary file
            import tempfile
            with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False) as tmp_file:
                tmp_file.write(video_bytes)
                tmp_path = tmp_file.name
            
            try:
                # Open video with OpenCV
                cap = cv2.VideoCapture(tmp_path)
                if not cap.isOpened():
                    raise ValueError("Could not open video file")
                
                frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
                fps = cap.get(cv2.CAP_PROP_FPS)
                
                logger.info(f"Video: {frame_count} frames, {fps:.2f} FPS")
                
                # Extract every Nth frame (e.g., every 10th frame)
                frame_interval = max(1, int(fps / 3))  # ~3 frames per second
                frame_scores = []
                
                frame_idx = 0
                analyzed_count = 0
                
                while True:
                    ret, frame = cap.read()
                    if not ret:
                        break
                    
                    # Analyze every Nth frame
                    if frame_idx % frame_interval == 0:
                        # Convert BGR to RGB
                        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                        
                        # Convert to PIL Image
                        pil_image = Image.fromarray(frame_rgb)
                        
                        # Convert to bytes
                        img_byte_arr = BytesIO()
                        pil_image.save(img_byte_arr, format='JPEG')
                        img_byte_arr.seek(0)
                        
                        # Analyze frame
                        result = self.analyze_image(img_byte_arr)
                        frame_scores.append(result["risk_score"])
                        analyzed_count += 1
                        
                        logger.debug(f"Frame {frame_idx}: score={result['risk_score']:.3f}")
                    
                    frame_idx += 1
                
                cap.release()
                
                if not frame_scores:
                    raise ValueError("No frames could be analyzed")
                
                # Calculate final risk score: mean of top 20% scores
                frame_scores_sorted = sorted(frame_scores, reverse=True)
                top_20_percent = max(1, len(frame_scores_sorted) // 5)
                top_scores = frame_scores_sorted[:top_20_percent]
                
                final_risk_score = np.mean(top_scores)
                highest_score = max(frame_scores)
                confidence = 0.85  # High confidence for video analysis
                
                logger.info(
                    f"Video analysis complete: {analyzed_count} frames analyzed, "
                    f"risk_score={final_risk_score:.3f}, highest={highest_score:.3f}"
                )
                
                return {
                    "risk_score": float(final_risk_score),
                    "confidence": confidence,
                    "frame_count": analyzed_count,
                    "highest_frame_score": float(highest_score)
                }
                
            finally:
                # Clean up temporary file
                import os
                try:
                    os.unlink(tmp_path)
                except:
                    pass
            
        except Exception as e:
            logger.error(f"Error analyzing video: {e}")
            logger.exception("Full traceback:")
            raise


# Singleton instance
deepfake_service = DeepfakeService()
