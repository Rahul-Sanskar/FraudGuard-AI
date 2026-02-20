"""
API endpoints for fraud detection analysis.
"""
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, Form
from sqlalchemy.orm import Session
from datetime import datetime
from io import BytesIO

from app.models.schemas import AnalysisResponse, HealthResponse
from app.models.database import FraudLog
from app.db.session import get_db
from app.services.deepfake_service import deepfake_service
from app.services.voice_service import voice_service
from app.services.document_service import document_service
from app.services.email_service import email_service
from app.core.logging import get_logger
from app.core.config import settings
from app.core.model_registry import model_registry

logger = get_logger(__name__)
router = APIRouter()


def calculate_risk_level(score: float) -> str:
    """
    Convert risk score to risk level with calibrated thresholds.
    
    Thresholds:
    - < 0.3: Low risk
    - 0.3 - 0.7: Medium risk
    - > 0.7: High risk
    """
    if score < 0.3:
        return "Low"
    elif score < 0.7:
        return "Medium"
    else:
        return "High"


def log_analysis(db: Session, input_type: str, response: AnalysisResponse) -> None:
    """Log analysis result to database."""
    try:
        log_entry = FraudLog(
            input_type=input_type,
            risk_score=response.risk_score,
            prediction=response.prediction,
            confidence=response.confidence
        )
        db.add(log_entry)
        db.commit()
        logger.info(f"Logged {input_type} analysis to database")
    except Exception as e:
        logger.error(f"Error logging to database: {e}")
        db.rollback()


@router.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """Health check endpoint with model status."""
    return HealthResponse(
        status="healthy",
        version=settings.VERSION,
        timestamp=datetime.utcnow()
    )


@router.get("/health/models")
async def health_check_models():
    """
    Detailed health check endpoint showing model loading status.
    Returns status of all ML models with lazy loading info.
    """
    registry_status = model_registry.get_status()
    
    return {
        "status": "healthy",
        "model_directory": registry_status["model_directory"],
        "current_loaded_model": registry_status["current_model"],
        "lazy_loading": "enabled",
        "models": {
            "deepfake": {
                "name": deepfake_service.model_name,
                "currently_loaded": model_registry.is_model_loaded(deepfake_service.model_name),
                "device": str(registry_status["device"])
            },
            "voice": {
                "name": voice_service.model_name,
                "currently_loaded": model_registry.is_model_loaded(voice_service.model_name),
                "device": str(registry_status["device"])
            },
            "document": {
                "name": document_service.model_name,
                "currently_loaded": model_registry.is_model_loaded(document_service.model_name),
                "device": str(registry_status["device"])
            },
            "email": {
                "loaded": email_service.model is not None,
                "model_name": "ProsusAI/finbert",
                "device": str(email_service.device)
            }
        },
        "timestamp": datetime.utcnow()
    }


@router.post("/analyze/image", response_model=AnalysisResponse)
async def analyze_image(
    file: UploadFile = File(...),
    is_live: bool = Form(False),  # True for live webcam, False for static uploads
    db: Session = Depends(get_db)
) -> AnalysisResponse:
    """
    Analyze image for deepfake detection.
    
    Args:
        file: Image file to analyze
        is_live: True if from live webcam (enables anti-spoofing), False for static uploads
    """
    
    # Validate content type
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail=f"File must be an image (got {file.content_type})")
    
    try:
        contents = await file.read()
        
        if len(contents) > settings.MAX_FILE_SIZE:
            raise HTTPException(status_code=400, detail="File too large")
        
        # Validate that PIL can open the image
        from PIL import Image
        import io
        try:
            test_image = Image.open(io.BytesIO(contents))
            test_image.verify()  # Verify it's a valid image
            logger.info(f"Image validated: {test_image.size}, mode: {test_image.mode}, is_live: {is_live}")
        except Exception as img_error:
            logger.error(f"Invalid image file: {img_error}")
            raise HTTPException(status_code=400, detail=f"Cannot identify image file: {str(img_error)}")
        
        # Pass bytes directly with is_live flag
        # Anti-spoofing (screen detection) only runs if is_live=True
        result = deepfake_service.analyze_image(contents, is_live=is_live)
        
        risk_score = result["risk_score"]
        confidence = result["confidence"]
        raw_logit = result.get("raw_logit", 0.0)
        
        # Build explanation
        if is_live and result.get("anti_spoof", {}).get("override_triggered", False):
            # Anti-spoof gate triggered (live webcam only)
            explanation = result.get("explanation", "Screen replay attack detected")
        else:
            explanation = f"Image analysis detected {'potential deepfake manipulation' if risk_score > 0.5 else 'authentic content'} with {confidence*100:.1f}% confidence. Raw logit: {raw_logit:.3f}"
        
        response = AnalysisResponse(
            risk_score=risk_score,
            prediction=calculate_risk_level(risk_score),
            confidence=confidence,
            explanation=explanation
        )
        
        log_analysis(db, "image", response)
        return response
        
    except HTTPException:
        raise
    except FileNotFoundError as e:
        logger.error(f"Model file not found: {e}")
        raise HTTPException(status_code=503, detail="Model not available. Please contact administrator.")
    except RuntimeError as e:
        logger.error(f"Model loading failed: {e}")
        raise HTTPException(status_code=503, detail="Model loading failed. Please try again later.")
    except Exception as e:
        logger.error(f"Error in image analysis: {e}")
        logger.exception("Full traceback:")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/analyze/video", response_model=AnalysisResponse)
async def analyze_video(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
) -> AnalysisResponse:
    """Analyze video for deepfake detection."""
    
    if not file.content_type.startswith("video/"):
        raise HTTPException(status_code=400, detail="File must be a video")
    
    try:
        contents = await file.read()
        
        if len(contents) > settings.MAX_FILE_SIZE * 5:  # 50MB for videos
            raise HTTPException(status_code=400, detail="File too large")
        
        result = deepfake_service.analyze_video(contents)
        
        risk_score = result["risk_score"]
        confidence = result["confidence"]
        frame_count = result.get("frame_count", 0)
        highest_score = result.get("highest_frame_score", 0.0)
        
        response = AnalysisResponse(
            risk_score=risk_score,
            prediction=calculate_risk_level(risk_score),
            confidence=confidence,
            explanation=f"Video analysis detected {'potential deepfake manipulation' if risk_score > 0.5 else 'authentic content'} with {confidence*100:.1f}% confidence. Analyzed {frame_count} frames. Highest frame score: {highest_score:.3f}"
        )
        
        log_analysis(db, "video", response)
        return response
        
    except FileNotFoundError as e:
        logger.error(f"Model file not found: {e}")
        raise HTTPException(status_code=503, detail="Model not available. Please contact administrator.")
    except RuntimeError as e:
        logger.error(f"Model loading failed: {e}")
        raise HTTPException(status_code=503, detail="Model loading failed. Please try again later.")
    except Exception as e:
        logger.error(f"Error in video analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/analyze/audio", response_model=AnalysisResponse)
async def analyze_audio(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
) -> AnalysisResponse:
    """
    Analyze audio for voice spoofing detection.
    Supports large files with automatic optimization:
    - Streaming upload (no size limit during upload)
    - Automatic compression and optimization
    - Rejects only if audio > 5 minutes after loading
    """
    import tempfile
    import os
    
    # Accept both audio/* and video/webm (webm can be video container with audio)
    if not (file.content_type.startswith("audio/") or file.content_type == "video/webm"):
        raise HTTPException(status_code=400, detail=f"File must be an audio file (got {file.content_type})")
    
    temp_file_path = None
    
    try:
        logger.info(f"Receiving audio file: {file.filename} ({file.content_type})")
        
        # Stream upload to temporary file (handles large files)
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as temp_file:
            temp_file_path = temp_file.name
            
            # Read and write in 1MB chunks
            chunk_size = 1024 * 1024  # 1MB
            total_size = 0
            
            while True:
                chunk = await file.read(chunk_size)
                if not chunk:
                    break
                temp_file.write(chunk)
                total_size += len(chunk)
            
            logger.info(f"Uploaded {total_size / 1024 / 1024:.2f} MB to temporary file")
        
        # Analyze audio with automatic optimization
        result = voice_service.analyze_audio_file(temp_file_path)
        
        risk_score = result["risk_score"]
        confidence = result["confidence"]
        raw_logit = result.get("raw_logit", 0.0)
        duration_original = result.get("duration_original", 0)
        duration_processed = result.get("duration_processed", 0)
        
        # Build explanation
        explanation = (
            f"Audio analysis detected {'potential voice spoofing' if risk_score > 0.5 else 'authentic voice'} "
            f"with {confidence*100:.1f}% confidence. "
        )
        
        if duration_original != duration_processed:
            explanation += f"Audio optimized: {duration_original:.1f}s → {duration_processed:.1f}s. "
        
        explanation += f"Raw logit: {raw_logit:.3f}"
        
        response = AnalysisResponse(
            risk_score=risk_score,
            prediction=calculate_risk_level(risk_score),
            confidence=confidence,
            explanation=explanation
        )
        
        log_analysis(db, "audio", response)
        return response
        
    except ValueError as e:
        # Audio too long or invalid
        logger.error(f"Audio validation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except FileNotFoundError as e:
        logger.error(f"Model file not found: {e}")
        raise HTTPException(status_code=503, detail="Model not available. Please contact administrator.")
    except RuntimeError as e:
        logger.error(f"Model loading failed: {e}")
        raise HTTPException(status_code=503, detail="Model loading failed. Please try again later.")
    except Exception as e:
        logger.error(f"Error in audio analysis: {e}")
        logger.exception("Full traceback:")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        # Clean up temporary file
        if temp_file_path and os.path.exists(temp_file_path):
            try:
                os.unlink(temp_file_path)
                logger.debug(f"Cleaned up temporary file: {temp_file_path}")
            except Exception as e:
                logger.warning(f"Could not delete temp file {temp_file_path}: {e}")



@router.post("/analyze/document", response_model=AnalysisResponse)
async def analyze_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
) -> AnalysisResponse:
    """Analyze document for tampering detection. Supports images and PDFs."""
    
    allowed_types = ["application/pdf", "image/jpeg", "image/png"]
    if file.content_type not in allowed_types:
        raise HTTPException(status_code=400, detail="File must be PDF or image")
    
    try:
        contents = await file.read()
        
        if len(contents) > settings.MAX_FILE_SIZE:
            raise HTTPException(status_code=400, detail="File too large")
        
        # Pass filename to service for PDF detection
        result = document_service.analyze_document(contents, filename=file.filename)
        
        risk_score = result["risk_score"]
        confidence = result["confidence"]
        raw_logit = result.get("raw_logit", 0.0)
        pages_analyzed = result.get("pages_analyzed", 1)
        
        # Generate explanation based on file type
        if file.filename.lower().endswith('.pdf'):
            explanation = (
                f"PDF document analysis: {pages_analyzed} page(s) analyzed. "
                f"{'Potential tampering or forgery detected' if risk_score > 0.5 else 'Document appears authentic'} "
                f"with {confidence*100:.1f}% confidence. "
            )
            if pages_analyzed > 1:
                highest_page = result.get("highest_risk_page", 1)
                explanation += f"Highest risk found on page {highest_page}. "
            explanation += f"Raw logit: {raw_logit:.3f}"
        else:
            explanation = (
                f"Document analysis detected "
                f"{'potential tampering or forgery' if risk_score > 0.5 else 'authentic document'} "
                f"with {confidence*100:.1f}% confidence. Raw logit: {raw_logit:.3f}"
            )
        
        response = AnalysisResponse(
            risk_score=risk_score,
            prediction=calculate_risk_level(risk_score),
            confidence=confidence,
            explanation=explanation
        )
        
        log_analysis(db, "document", response)
        return response
        
    except RuntimeError as e:
        # PDF/Poppler errors
        logger.error(f"Runtime error in document analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    except FileNotFoundError as e:
        logger.error(f"Model file not found: {e}")
        raise HTTPException(status_code=503, detail="Model not available. Please contact administrator.")
    except Exception as e:
        logger.error(f"Error in document analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/analyze/email", response_model=AnalysisResponse)
async def analyze_email(
    email_text: str = Form(...),
    db: Session = Depends(get_db)
) -> AnalysisResponse:
    """Analyze email for C-suite impersonation detection."""
    
    if not email_text or len(email_text) < 10:
        raise HTTPException(status_code=400, detail="Email text too short")
    
    try:
        probability, confidence, breakdown = email_service.analyze_email(email_text)
        
        # Generate explanation based on BEC override or normal analysis
        if breakdown.get('bec_override', False):
            explanation = (
                f"Business Email Compromise pattern detected (payment + authority manipulation). "
                f"Rule score: {breakdown['rule_score']:.2f}. "
                f"HIGH RISK: Email contains suspicious payment/banking requests with executive authority impersonation."
            )
        else:
            model_score_text = f", Model score: {breakdown['model_score']:.2f}" if breakdown['model_score'] is not None else ""
            if probability > 0.7:
                explanation = (
                    f"High-risk email fraud pattern detected with {confidence*100:.1f}% confidence. "
                    f"Rule score: {breakdown['rule_score']:.2f}{model_score_text}. "
                    f"Email contains suspicious authority impersonation and/or payment manipulation indicators."
                )
            elif probability > 0.3:
                explanation = (
                    f"Medium-risk email pattern detected with {confidence*100:.1f}% confidence. "
                    f"Rule score: {breakdown['rule_score']:.2f}{model_score_text}. "
                    f"Email contains some suspicious indicators but may be legitimate."
                )
            else:
                explanation = (
                    f"Email appears legitimate with {confidence*100:.1f}% confidence. "
                    f"Rule score: {breakdown['rule_score']:.2f}{model_score_text}."
                )
        
        response = AnalysisResponse(
            risk_score=probability,
            prediction=calculate_risk_level(probability),
            confidence=confidence,
            explanation=explanation
        )
        
        log_analysis(db, "email", response)
        return response
        
    except Exception as e:
        logger.error(f"Error in email analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/test-voice-status")
async def test_voice_status():
    """Test voice service status."""
    from app.services.voice_service import AUDIO_LIBS_AVAILABLE
    
    return {
        "AUDIO_LIBS_AVAILABLE": AUDIO_LIBS_AVAILABLE,
        "model_name": voice_service.model_name,
        "currently_loaded": model_registry.is_model_loaded(voice_service.model_name),
        "device": str(model_registry.device)
    }


@router.get("/debug")
async def debug_info():
    """Debug endpoint to check model status and device."""
    import torch as torch_module
    import sys
    
    # Check if librosa is available
    try:
        import librosa
        import soundfile as sf
        audio_libs = "installed"
        librosa_version = librosa.__version__
        soundfile_version = sf.__version__
    except ImportError as e:
        audio_libs = f"not installed: {str(e)}"
        librosa_version = "N/A"
        soundfile_version = "N/A"
    
    return {
        "device": {
            "cuda_available": torch_module.cuda.is_available(),
            "cuda_device_count": torch_module.cuda.device_count() if torch_module.cuda.is_available() else 0,
            "current_device": str(deepfake_service.device)
        },
        "python": {
            "version": sys.version,
            "executable": sys.executable
        },
        "audio_libraries": {
            "status": audio_libs,
            "librosa_version": librosa_version,
            "soundfile_version": soundfile_version,
            "AUDIO_LIBS_AVAILABLE": voice_service.__class__.__module__ + " check"
        },
        "models": {
            "deepfake": {
                "name": deepfake_service.model_name,
                "currently_loaded": model_registry.is_model_loaded(deepfake_service.model_name)
            },
            "voice": {
                "name": voice_service.model_name,
                "currently_loaded": model_registry.is_model_loaded(voice_service.model_name)
            },
            "document": {
                "name": document_service.model_name,
                "currently_loaded": model_registry.is_model_loaded(document_service.model_name)
            },
            "email": {
                "loaded": email_service.model is not None,
                "model_name": "ProsusAI/finbert"
            }
        },
        "test_inference": {
            "deepfake": _test_deepfake_inference(),
            "document": _test_document_inference()
        }
    }


@router.post("/test-image")
async def test_image_processing(file: UploadFile = File(...)):
    """Test endpoint to debug image processing."""
    try:
        contents = await file.read()
        logger.info(f"Received file: {file.filename}, size: {len(contents)} bytes, type: {file.content_type}")
        
        # Test PIL can open it
        from PIL import Image
        from io import BytesIO
        
        img = Image.open(BytesIO(contents))
        logger.info(f"PIL opened image: {img.size}, mode: {img.mode}")
        
        # Test preprocessing
        result = deepfake_service.analyze_image(contents)
        logger.info(f"Analysis result: {result}")
        
        return {
            "status": "success",
            "file_size": len(contents),
            "image_size": img.size,
            "image_mode": img.mode,
            "result": result
        }
    except Exception as e:
        logger.error(f"Test error: {e}")
        logger.exception("Full traceback:")
        return {
            "status": "error",
            "message": str(e)
        }


def _test_deepfake_inference() -> dict:
    """Test deepfake model with dummy tensor."""
    try:
        import torch as torch_module
        
        if deepfake_service.model is None:
            return {"status": "model_not_loaded"}
        
        dummy_input = torch_module.randn(1, 3, 300, 300).to(deepfake_service.device)
        with torch_module.no_grad():
            output = deepfake_service.model(dummy_input)
        
        return {
            "status": "success",
            "output_shape": list(output.shape),
            "output_sample": output[0].tolist()
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


def _test_document_inference() -> dict:
    """Test document model with dummy tensor."""
    try:
        import torch as torch_module
        
        if document_service.model is None:
            return {"status": "model_not_loaded"}
        
        dummy_input = torch_module.randn(1, 3, 300, 300).to(document_service.device)
        with torch_module.no_grad():
            output = document_service.model(dummy_input)
        
        return {
            "status": "success",
            "output_shape": list(output.shape),
            "output_sample": output[0].tolist()
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}
