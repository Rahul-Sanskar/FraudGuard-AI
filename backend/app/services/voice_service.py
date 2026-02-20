"""
Voice spoofing detection service.
"""
import torch
import numpy as np
from pathlib import Path
from typing import Tuple
import io
import subprocess
import tempfile
import os
import shutil
from app.core.logging import get_logger
from app.core.config import settings
from app.models.architectures import Wav2Vec2VoiceModel, load_model_with_state_dict

logger = get_logger(__name__)

# Try to import audio processing libraries
try:
    import librosa
    import soundfile as sf
    AUDIO_LIBS_AVAILABLE = True
except ImportError:
    AUDIO_LIBS_AVAILABLE = False
    logger.warning("librosa or soundfile not installed. Voice analysis will use mock predictions.")
    logger.warning("Install with: pip install librosa soundfile")

# Check if ffmpeg is available
FFMPEG_AVAILABLE = shutil.which("ffmpeg") is not None
if FFMPEG_AVAILABLE:
    logger.info("✅ FFmpeg found in PATH")
else:
    logger.warning("⚠️ FFmpeg not found in PATH. Voice analysis may fail for webm files.")


def convert_webm_to_wav(webm_path: str) -> str:
    """
    Convert WEBM audio to WAV using FFmpeg.
    
    Args:
        webm_path: Path to input WEBM file
        
    Returns:
        Path to output WAV file (16kHz mono)
    """
    wav_path = webm_path.replace(".webm", ".wav")
    
    command = [
        "ffmpeg",
        "-y",  # Overwrite output file
        "-i", webm_path,  # Input file
        "-ac", "1",  # Mono audio
        "-ar", "16000",  # 16kHz sample rate
        wav_path  # Output file
    ]
    
    try:
        subprocess.run(
            command,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=True,
            timeout=30
        )
        logger.info(f"✅ Converted WEBM to WAV: {wav_path}")
        return wav_path
    except subprocess.CalledProcessError as e:
        logger.error(f"FFmpeg conversion failed: {e}")
        raise
    except subprocess.TimeoutExpired:
        logger.error("FFmpeg conversion timed out")
        raise


class VoiceService:
    """Service for detecting voice spoofing and synthetic audio."""
    
    def __init__(self):
        self.model_path = Path(settings.MODEL_PATH) / "voice_spoof_model.pt"
        self.model = None
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self._load_model()
    
    def _load_model(self) -> None:
        """Load the pre-trained voice spoofing detection model."""
        try:
            if self.model_path.exists():
                logger.info(f"Loading voice model from {self.model_path}")
                
                # Load the model checkpoint
                checkpoint = torch.load(self.model_path, map_location=self.device)
                
                # Check if it's a state_dict (OrderedDict) or complete model
                if isinstance(checkpoint, dict) and not hasattr(checkpoint, 'state_dict'):
                    # It's a state_dict - need to instantiate architecture
                    logger.info("Detected state_dict format. Loading with Wav2Vec2 architecture...")
                    
                    try:
                        # Instantiate the model architecture
                        model = Wav2Vec2VoiceModel(num_classes=1)
                        
                        # Load the state dict
                        model.load_state_dict(checkpoint, strict=False)
                        model.to(self.device)
                        model.eval()
                        
                        self.model = model
                        logger.info(f"✅ Voice model loaded successfully from {self.model_path}")
                        
                        # Verify model weights loaded correctly
                        if hasattr(model, 'classifier') and len(model.classifier) > 4:
                            classifier_weight = model.classifier[4].weight
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
                    logger.info(f"✅ Voice model loaded successfully from {self.model_path}")
            else:
                logger.warning(f"Model not found at {self.model_path}. Using mock predictions.")
        except Exception as e:
            logger.error(f"Error loading voice model: {e}")
            logger.warning("Using mock predictions.")
            self.model = None
    
    def _preprocess_audio(self, audio_bytes: bytes) -> torch.Tensor:
        """
        Preprocess audio for Wav2Vec2 model inference.
        Pipeline: WEBM → WAV (via FFmpeg) → Load with librosa → Tensor
        
        Args:
            audio_bytes: Raw audio file bytes (WEBM format from browser)
            
        Returns:
            Preprocessed audio tensor ready for model input
        """
        if not AUDIO_LIBS_AVAILABLE:
            raise ImportError("librosa and soundfile are required for audio processing")
        
        if not FFMPEG_AVAILABLE:
            raise RuntimeError("FFmpeg is required but not found in PATH")
        
        webm_path = None
        wav_path = None
        
        try:
            # Step 1: Save WEBM bytes to temp file
            with tempfile.NamedTemporaryFile(delete=False, suffix=".webm") as f:
                f.write(audio_bytes)
                webm_path = f.name
            
            logger.info(f"Saved WEBM to temp file: {webm_path}")
            
            # Step 2: Convert WEBM to WAV using FFmpeg
            wav_path = convert_webm_to_wav(webm_path)
            
            # Step 3: Load WAV with librosa (now it's a standard WAV file)
            audio, sr = librosa.load(wav_path, sr=16000, mono=True)
            logger.info(f"Loaded audio: sr={sr}Hz, shape={audio.shape}")
            
            # Step 4: Pad or trim to 4 seconds (64000 samples at 16kHz)
            target_length = 4 * 16000  # 4 seconds
            if len(audio) < target_length:
                # Pad with zeros
                audio = np.pad(audio, (0, target_length - len(audio)), mode='constant')
                logger.info(f"Padded audio to {target_length} samples")
            elif len(audio) > target_length:
                # Trim to 4 seconds
                audio = audio[:target_length]
                logger.info(f"Trimmed audio to {target_length} samples")
            
            # Step 5: Normalize audio
            if audio.max() > 0:
                audio = audio / np.abs(audio).max()
            
            # Step 6: Convert to tensor
            audio_tensor = torch.from_numpy(audio).float()
            
            # Add batch dimension
            audio_tensor = audio_tensor.unsqueeze(0)
            
            logger.info(f"✅ Audio preprocessed successfully: shape={audio_tensor.shape}, sr={sr}Hz, duration=4s")
            logger.info(f"Audio length: {len(audio)} samples")
            logger.info(f"Sample rate: {sr} Hz")
            
            return audio_tensor
            
        except Exception as e:
            logger.error(f"❌ Error preprocessing audio: {e}")
            logger.exception("Full traceback:")
            raise
        finally:
            # Clean up temp files
            if webm_path and os.path.exists(webm_path):
                try:
                    os.unlink(webm_path)
                    logger.debug(f"Cleaned up temp file: {webm_path}")
                except Exception as e:
                    logger.warning(f"Could not delete temp file {webm_path}: {e}")
            
            if wav_path and os.path.exists(wav_path):
                try:
                    os.unlink(wav_path)
                    logger.debug(f"Cleaned up temp file: {wav_path}")
                except Exception as e:
                    logger.warning(f"Could not delete temp file {wav_path}: {e}")
    
    def _optimize_audio(self, audio_path: str) -> Tuple[np.ndarray, int, dict]:
        """
        Optimize audio for inference:
        - Convert to mono
        - Resample to 16kHz
        - Normalize amplitude
        - Trim silence > 2 seconds
        - Limit to 30 seconds (keep center segment)
        
        Args:
            audio_path: Path to audio file
            
        Returns:
            Tuple of (audio_array, sample_rate, metadata)
        """
        if not AUDIO_LIBS_AVAILABLE:
            raise ImportError("librosa and soundfile required for audio optimization")
        
        logger.info(f"Optimizing audio from: {audio_path}")
        
        # Load audio (librosa automatically converts to mono and resamples)
        audio, sr = librosa.load(audio_path, sr=16000, mono=True)
        
        duration_original = len(audio) / sr
        logger.info(f"Original audio: {duration_original:.2f}s, {sr}Hz, {len(audio)} samples")
        
        # Check if audio is too long (> 5 minutes)
        if duration_original > 300:  # 5 minutes
            raise ValueError(
                f"Audio too long: {duration_original:.1f}s (max 5 minutes). "
                f"Please upload a shorter audio file."
            )
        
        # Normalize amplitude to [-1, 1]
        if audio.max() > 0:
            audio = audio / np.abs(audio).max()
            logger.info("✅ Normalized amplitude")
        
        # Trim silence longer than 2 seconds
        # top_db: threshold in dB below reference to consider as silence
        audio_trimmed, _ = librosa.effects.trim(audio, top_db=20, frame_length=2048, hop_length=512)
        
        # Remove long silences (> 2 seconds)
        intervals = librosa.effects.split(audio_trimmed, top_db=20, frame_length=2048, hop_length=512)
        
        if len(intervals) > 0:
            # Keep only non-silent segments
            audio_segments = []
            for start, end in intervals:
                segment = audio_trimmed[start:end]
                audio_segments.append(segment)
            
            audio = np.concatenate(audio_segments) if audio_segments else audio_trimmed
            logger.info(f"✅ Trimmed silence: {len(intervals)} segments kept")
        else:
            audio = audio_trimmed
        
        duration_after_trim = len(audio) / sr
        logger.info(f"After trimming: {duration_after_trim:.2f}s")
        
        # Limit to 30 seconds (keep center segment if longer)
        max_duration = 30  # seconds
        max_samples = max_duration * sr
        
        if len(audio) > max_samples:
            # Keep center segment
            center = len(audio) // 2
            half_window = max_samples // 2
            start = max(0, center - half_window)
            end = min(len(audio), center + half_window)
            audio = audio[start:end]
            logger.info(f"✅ Limited to {max_duration}s (kept center segment)")
        
        duration_final = len(audio) / sr
        logger.info(f"Final audio: {duration_final:.2f}s, {len(audio)} samples")
        
        metadata = {
            "duration_original": duration_original,
            "duration_processed": duration_final,
            "sample_rate": sr,
            "samples": len(audio),
            "trimmed": duration_original != duration_after_trim,
            "limited": duration_after_trim > max_duration
        }
        
        return audio, sr, metadata
    
    def analyze_audio_file(self, audio_path: str) -> dict:
        """
        Analyze audio file with automatic optimization.
        Handles large files by streaming and optimizing before inference.
        
        Args:
            audio_path: Path to audio file (any format supported by librosa/ffmpeg)
            
        Returns:
            Dict with risk_score, confidence, raw_logit, duration info
        """
        logger.info("=" * 80)
        logger.info("VOICE ANALYSIS START (WITH AUDIO OPTIMIZATION)")
        logger.info("=" * 80)
        
        try:
            # Check if libraries are available
            if not AUDIO_LIBS_AVAILABLE:
                raise ImportError("librosa and soundfile required. Install with: pip install librosa soundfile")
            
            # Check if model is loaded
            if self.model is None:
                raise RuntimeError("Voice model not loaded. Cannot perform analysis.")
            
            # Get file size
            file_size_mb = os.path.getsize(audio_path) / 1024 / 1024
            logger.info(f"Audio file size: {file_size_mb:.2f} MB")
            
            # Optimize audio (convert, resample, trim, limit)
            audio, sr, metadata = self._optimize_audio(audio_path)
            
            logger.info(f"Audio optimization complete:")
            logger.info(f"  Original duration: {metadata['duration_original']:.2f}s")
            logger.info(f"  Processed duration: {metadata['duration_processed']:.2f}s")
            logger.info(f"  Sample rate: {metadata['sample_rate']}Hz")
            logger.info(f"  Samples: {metadata['samples']}")
            
            # Pad or trim to 4 seconds for model input
            target_length = 4 * sr  # 4 seconds
            if len(audio) < target_length:
                # Pad with zeros
                audio = np.pad(audio, (0, target_length - len(audio)), mode='constant')
                logger.info(f"Padded audio to {target_length} samples (4s)")
            elif len(audio) > target_length:
                # Take first 4 seconds
                audio = audio[:target_length]
                logger.info(f"Trimmed audio to {target_length} samples (4s)")
            
            # Normalize again after padding/trimming
            if audio.max() > 0:
                audio = audio / np.abs(audio).max()
            
            # Convert to tensor
            audio_tensor = torch.from_numpy(audio).float()
            audio_tensor = audio_tensor.unsqueeze(0)  # Add batch dimension: [1, samples]
            audio_tensor = audio_tensor.to(self.device)
            
            logger.info(f"Input tensor shape: {audio_tensor.shape}")
            logger.info(f"Tensor stats - min: {audio_tensor.min():.3f}, max: {audio_tensor.max():.3f}, mean: {audio_tensor.mean():.3f}")
            
            # Run inference
            logger.info("Running Wav2Vec2 inference...")
            self.model.eval()
            
            with torch.no_grad():
                output = self.model(audio_tensor)
                logger.info(f"Model output shape: {output.shape}")
                logger.info(f"Raw output: {output}")
                
                # Handle single output (spoofing score)
                if output.shape[-1] == 1:
                    # Single output - use sigmoid
                    raw_logit = output[0][0].item()
                    probability = torch.sigmoid(output[0][0]).item()
                    confidence = abs(probability - 0.5) * 2
                    
                    logger.info(f"✅ Prediction - Logit: {raw_logit:.3f}, Probability: {probability:.3f}, Confidence: {confidence:.3f}")
                    
                else:
                    # Multiple outputs - use softmax
                    probabilities = torch.softmax(output, dim=-1)
                    spoof_prob = probabilities[0][1].item() if output.shape[-1] == 2 else probabilities[0][0].item()
                    confidence = torch.max(probabilities).item()
                    raw_logit = output[0][1].item() if output.shape[-1] == 2 else output[0][0].item()
                    probability = spoof_prob
                    
                    logger.info(f"✅ Prediction - Spoof prob: {spoof_prob:.3f}, Confidence: {confidence:.3f}")
            
            logger.info("=" * 80)
            
            return {
                "risk_score": probability,
                "confidence": confidence,
                "raw_logit": raw_logit,
                "duration_original": metadata["duration_original"],
                "duration_processed": metadata["duration_processed"],
                "sample_rate": metadata["sample_rate"]
            }
            
        except Exception as e:
            logger.error(f"Error analyzing audio file: {e}")
            logger.exception("Full traceback:")
            raise
    
    def analyze_audio(self, audio_bytes: bytes) -> dict:
        """
        Analyze audio for voice spoofing detection.
        
        Returns:
            Dict with risk_score, confidence, raw_logit
        """
        logger.info("=== VOICE ANALYSIS START ===")
        logger.info(f"Received audio bytes: {len(audio_bytes)} bytes")
        
        try:
            # Check if libraries are available
            logger.info(f"AUDIO_LIBS_AVAILABLE: {AUDIO_LIBS_AVAILABLE}")
            logger.info(f"FFMPEG_AVAILABLE: {FFMPEG_AVAILABLE}")
            
            if not AUDIO_LIBS_AVAILABLE:
                logger.error("Audio processing libraries not available!")
                return {
                    "risk_score": 0.20,
                    "confidence": 0.80,
                    "raw_logit": -1.39,
                    "note": "Audio libraries not installed - using mock prediction"
                }
            
            if not FFMPEG_AVAILABLE:
                logger.error("FFmpeg not available!")
                return {
                    "risk_score": 0.20,
                    "confidence": 0.80,
                    "raw_logit": -1.39,
                    "note": "FFmpeg not found - using mock prediction"
                }
            
            # Check if model is loaded
            logger.info(f"Model loaded: {self.model is not None}")
            if self.model is None:
                logger.warning("Voice model not loaded, using mock prediction")
                return {
                    "risk_score": 0.20,
                    "confidence": 0.80,
                    "raw_logit": -1.39,
                    "note": "Model not loaded - using mock prediction"
                }
            
            logger.info("Starting audio analysis with real model...")
            logger.info("Converting WEBM to WAV using FFmpeg...")
            
            # Preprocess audio (WEBM → WAV → Tensor)
            audio_tensor = self._preprocess_audio(audio_bytes)
            audio_tensor = audio_tensor.to(self.device)
            logger.info(f"Input tensor shape: {audio_tensor.shape}")
            
            # Run inference with no gradient computation
            logger.info("Running Wav2Vec2 inference...")
            self.model.eval()
            with torch.no_grad():
                output = self.model(audio_tensor)
                logger.info(f"Model output shape: {output.shape}")
                logger.info(f"Raw output: {output}")
                
                # Handle single output (spoofing score)
                if output.shape[-1] == 1:
                    # Single output - use sigmoid
                    raw_logit = output[0][0].item()
                    probability = torch.sigmoid(output[0][0]).item()
                    confidence = abs(probability - 0.5) * 2
                    
                    logger.info(f"✅ Prediction generated - Logit: {raw_logit:.3f}, Sigmoid: {probability:.3f}")
                    logger.info("=== VOICE ANALYSIS COMPLETE (REAL MODEL) ===")
                    
                    return {
                        "risk_score": probability,
                        "confidence": confidence,
                        "raw_logit": raw_logit
                    }
                else:
                    # Multiple outputs - use softmax
                    probabilities = torch.softmax(output, dim=-1)
                    spoof_prob = probabilities[0][1].item() if output.shape[-1] == 2 else probabilities[0][0].item()
                    confidence = torch.max(probabilities).item()
                    raw_logit = output[0][1].item() if output.shape[-1] == 2 else output[0][0].item()
                    
                    logger.info(f"✅ Prediction generated - Spoof prob: {spoof_prob:.3f}, Confidence: {confidence:.3f}")
                    logger.info("=== VOICE ANALYSIS COMPLETE (REAL MODEL) ===")
                    
                    return {
                        "risk_score": spoof_prob,
                        "confidence": confidence,
                        "raw_logit": raw_logit
                    }
            
        except Exception as e:
            logger.error(f"!!! ERROR analyzing audio: {e}")
            logger.exception("Full traceback:")
            logger.info("=== VOICE ANALYSIS FAILED - RETURNING MOCK ===")
            # Return mock prediction instead of raising
            return {
                "risk_score": 0.20,
                "confidence": 0.80,
                "raw_logit": -1.39,
                "error": str(e),
                "note": "Error occurred during analysis - using mock prediction"
            }


# Singleton instance
voice_service = VoiceService()
