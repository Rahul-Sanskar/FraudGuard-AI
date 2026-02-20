"""
Test script to verify production-safe model loading.
This should NOT crash even if models are missing.
"""
import sys
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def test_model_manager():
    """Test model manager initialization."""
    logger.info("=" * 80)
    logger.info("TEST 1: Model Manager Initialization")
    logger.info("=" * 80)
    
    try:
        from app.core.model_manager import model_manager
        
        status = model_manager.get_status()
        logger.info(f"✅ Model manager initialized successfully")
        logger.info(f"   Model directory: {status['model_directory']}")
        logger.info(f"   Available models: {status['available_models']}/{status['total_models']}")
        logger.info(f"   Models: {status['models']}")
        
        return True
    except Exception as e:
        logger.error(f"❌ Model manager initialization failed: {e}")
        return False


def test_service_initialization():
    """Test that all services initialize without crashing."""
    logger.info("\n" + "=" * 80)
    logger.info("TEST 2: Service Initialization (Should NOT Crash)")
    logger.info("=" * 80)
    
    services_ok = True
    
    # Test document service
    try:
        from app.services.document_service import document_service
        logger.info(f"✅ Document service initialized")
        logger.info(f"   Model loaded: {document_service.model is not None}")
        logger.info(f"   Mock mode: {document_service.mock_mode}")
    except Exception as e:
        logger.error(f"❌ Document service failed: {e}")
        services_ok = False
    
    # Test deepfake service
    try:
        from app.services.deepfake_service import deepfake_service
        logger.info(f"✅ Deepfake service initialized")
        logger.info(f"   Model loaded: {deepfake_service.model is not None}")
        logger.info(f"   Mock mode: {deepfake_service.mock_mode}")
    except Exception as e:
        logger.error(f"❌ Deepfake service failed: {e}")
        services_ok = False
    
    # Test voice service
    try:
        from app.services.voice_service import voice_service
        logger.info(f"✅ Voice service initialized")
        logger.info(f"   Model loaded: {voice_service.model is not None}")
        logger.info(f"   Mock mode: {voice_service.mock_mode}")
    except Exception as e:
        logger.error(f"❌ Voice service failed: {e}")
        services_ok = False
    
    return services_ok


def test_mock_predictions():
    """Test that mock predictions work when models are missing."""
    logger.info("\n" + "=" * 80)
    logger.info("TEST 3: Mock Predictions (When Models Missing)")
    logger.info("=" * 80)
    
    from app.services.document_service import document_service
    from app.services.deepfake_service import deepfake_service
    from app.services.voice_service import voice_service
    
    # Only test if in mock mode
    if document_service.mock_mode:
        try:
            # Create a dummy image
            from PIL import Image
            from io import BytesIO
            
            img = Image.new('RGB', (224, 224), color='red')
            img_bytes = BytesIO()
            img.save(img_bytes, format='JPEG')
            img_bytes.seek(0)
            
            result = document_service.analyze_document(img_bytes.read(), filename="test.jpg")
            logger.info(f"✅ Document mock prediction: {result}")
            
            if result.get("mock") == True:
                logger.info("   ✅ Mock flag correctly set")
            else:
                logger.warning("   ⚠️  Mock flag not set")
                
        except Exception as e:
            logger.error(f"❌ Document mock prediction failed: {e}")
            return False
    else:
        logger.info("   Document service has real model - skipping mock test")
    
    if deepfake_service.mock_mode:
        try:
            from PIL import Image
            from io import BytesIO
            
            img = Image.new('RGB', (224, 224), color='blue')
            img_bytes = BytesIO()
            img.save(img_bytes, format='JPEG')
            img_bytes.seek(0)
            
            result = deepfake_service.analyze_image(img_bytes.read())
            logger.info(f"✅ Deepfake mock prediction: {result}")
            
            if result.get("mock") == True:
                logger.info("   ✅ Mock flag correctly set")
            else:
                logger.warning("   ⚠️  Mock flag not set")
                
        except Exception as e:
            logger.error(f"❌ Deepfake mock prediction failed: {e}")
            return False
    else:
        logger.info("   Deepfake service has real model - skipping mock test")
    
    return True


def main():
    """Run all tests."""
    logger.info("PRODUCTION-SAFE MODEL LOADING TEST")
    logger.info("This test verifies that the API never crashes due to missing models")
    logger.info("")
    
    results = []
    
    # Test 1: Model manager
    results.append(("Model Manager", test_model_manager()))
    
    # Test 2: Service initialization
    results.append(("Service Initialization", test_service_initialization()))
    
    # Test 3: Mock predictions
    results.append(("Mock Predictions", test_mock_predictions()))
    
    # Summary
    logger.info("\n" + "=" * 80)
    logger.info("TEST SUMMARY")
    logger.info("=" * 80)
    
    all_passed = True
    for test_name, passed in results:
        status = "✅ PASSED" if passed else "❌ FAILED"
        logger.info(f"{test_name}: {status}")
        if not passed:
            all_passed = False
    
    logger.info("=" * 80)
    
    if all_passed:
        logger.info("🎉 ALL TESTS PASSED - Production-safe loading works!")
        return 0
    else:
        logger.error("❌ SOME TESTS FAILED - Check logs above")
        return 1


if __name__ == "__main__":
    sys.exit(main())
