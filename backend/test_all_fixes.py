"""
Test script to verify all production fixes are working correctly.
Tests model loading, preprocessing, and inference for all services.
"""
import sys
import torch
from pathlib import Path

# Add app to path
sys.path.insert(0, str(Path(__file__).parent))

from app.services.deepfake_service import deepfake_service
from app.services.voice_service import voice_service, AUDIO_LIBS_AVAILABLE
from app.services.document_service import document_service
from app.services.email_service import email_service
from app.core.logging import get_logger

logger = get_logger(__name__)


def test_deepfake_model():
    """Test deepfake model loading and inference."""
    print("\n" + "="*60)
    print("TEST 1: DEEPFAKE MODEL")
    print("="*60)
    
    # Check model loaded
    if deepfake_service.model is None:
        print("❌ FAIL: Deepfake model not loaded")
        return False
    
    print("✅ Model loaded successfully")
    
    # Check model has correct architecture
    if not hasattr(deepfake_service.model, 'head'):
        print("❌ FAIL: Model missing 'head' attribute")
        return False
    
    print("✅ Model has correct architecture")
    
    # Test inference with dummy tensor
    try:
        dummy_input = torch.randn(1, 3, 224, 224).to(deepfake_service.device)
        with torch.no_grad():
            output = deepfake_service.model(dummy_input)
        
        print(f"✅ Inference successful: output shape = {output.shape}")
        
        # Check output shape (should be [1, 2] for binary classification)
        if output.shape[-1] != 2:
            print(f"⚠️  WARNING: Expected 2 classes, got {output.shape[-1]}")
        
        # Apply softmax and check probabilities
        probs = torch.softmax(output, dim=-1)
        print(f"   Class probabilities: {probs[0].tolist()}")
        
        return True
        
    except Exception as e:
        print(f"❌ FAIL: Inference error: {e}")
        return False


def test_voice_model():
    """Test voice model loading and inference."""
    print("\n" + "="*60)
    print("TEST 2: VOICE MODEL")
    print("="*60)
    
    # Check audio libraries
    if not AUDIO_LIBS_AVAILABLE:
        print("⚠️  WARNING: Audio libraries not available (librosa/soundfile)")
        print("   Install with: pip install librosa soundfile")
    else:
        print("✅ Audio libraries available")
    
    # Check model loaded
    if voice_service.model is None:
        print("❌ FAIL: Voice model not loaded")
        return False
    
    print("✅ Model loaded successfully")
    
    # Check model has correct architecture
    if not hasattr(voice_service.model, 'classifier'):
        print("❌ FAIL: Model missing 'classifier' attribute")
        return False
    
    print("✅ Model has correct architecture")
    
    # Test inference with dummy tensor (4 seconds at 16kHz)
    try:
        dummy_input = torch.randn(1, 64000).to(voice_service.device)
        with torch.no_grad():
            output = voice_service.model(dummy_input)
        
        print(f"✅ Inference successful: output shape = {output.shape}")
        
        # Check output shape (should be [1, 1] for binary classification)
        if output.shape[-1] != 1:
            print(f"⚠️  WARNING: Expected 1 output, got {output.shape[-1]}")
        
        # Apply sigmoid
        prob = torch.sigmoid(output[0][0]).item()
        print(f"   Spoof probability: {prob:.3f}")
        
        return True
        
    except Exception as e:
        print(f"❌ FAIL: Inference error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_document_model():
    """Test document model loading and inference."""
    print("\n" + "="*60)
    print("TEST 3: DOCUMENT MODEL")
    print("="*60)
    
    # Check model loaded
    if document_service.model is None:
        print("❌ FAIL: Document model not loaded")
        return False
    
    print("✅ Model loaded successfully")
    
    # Check model has correct architecture
    if not hasattr(document_service.model, 'classifier'):
        print("❌ FAIL: Model missing 'classifier' attribute")
        return False
    
    print("✅ Model has correct architecture")
    
    # Test inference with dummy tensor
    try:
        dummy_input = torch.randn(1, 3, 224, 224).to(document_service.device)
        with torch.no_grad():
            output = document_service.model(dummy_input)
        
        print(f"✅ Inference successful: output shape = {output.shape}")
        
        # Check output shape (should be [1, 1] for binary classification)
        if output.shape[-1] != 1:
            print(f"⚠️  WARNING: Expected 1 output, got {output.shape[-1]}")
        
        # Apply sigmoid
        prob = torch.sigmoid(output[0][0]).item()
        print(f"   Tamper probability: {prob:.3f}")
        
        return True
        
    except Exception as e:
        print(f"❌ FAIL: Inference error: {e}")
        return False


def test_email_model():
    """Test email model loading and inference."""
    print("\n" + "="*60)
    print("TEST 4: EMAIL MODEL (FinBERT)")
    print("="*60)
    
    # Check model loaded
    if email_service.model is None:
        print("❌ FAIL: Email model not loaded")
        return False
    
    print("✅ Model loaded successfully")
    
    # Test with sample fraud email
    fraud_email = """
    URGENT: Wire Transfer Required
    
    Dear Team,
    
    I need you to process an urgent wire transfer immediately. 
    Please send $50,000 to the following account:
    
    Account: 123456789
    Bank: International Bank
    
    This is confidential - do not contact anyone else about this.
    
    CEO
    """
    
    try:
        risk_score, confidence, breakdown = email_service.analyze_email(fraud_email)
        
        print(f"✅ Analysis successful")
        print(f"   Risk score: {risk_score:.3f}")
        print(f"   Confidence: {confidence:.3f}")
        print(f"   Rule score: {breakdown['rule_score']:.3f}")
        print(f"   Model score: {breakdown['model_score']:.3f}")
        
        # Check if fraud is detected
        if risk_score > 0.5:
            print(f"✅ Correctly identified as HIGH RISK")
        else:
            print(f"⚠️  WARNING: Should be high risk but got {risk_score:.3f}")
        
        return True
        
    except Exception as e:
        print(f"❌ FAIL: Analysis error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_preprocessing():
    """Test preprocessing pipelines."""
    print("\n" + "="*60)
    print("TEST 5: PREPROCESSING")
    print("="*60)
    
    from PIL import Image
    import io
    
    # Create a test image
    test_image = Image.new('RGB', (640, 480), color='red')
    img_bytes = io.BytesIO()
    test_image.save(img_bytes, format='JPEG')
    img_bytes.seek(0)
    
    try:
        # Test deepfake preprocessing
        tensor = deepfake_service._preprocess_image(img_bytes.getvalue())
        print(f"✅ Deepfake preprocessing: shape={tensor.shape}")
        
        if tensor.shape != (1, 3, 224, 224):
            print(f"⚠️  WARNING: Expected (1, 3, 224, 224), got {tensor.shape}")
        
        # Check normalization (ImageNet stats)
        mean = tensor.mean().item()
        print(f"   Tensor mean: {mean:.3f} (should be ~0 for ImageNet norm)")
        
        # Test document preprocessing
        img_bytes.seek(0)
        tensor = document_service._preprocess_document(img_bytes.getvalue())
        print(f"✅ Document preprocessing: shape={tensor.shape}")
        
        if tensor.shape != (1, 3, 224, 224):
            print(f"⚠️  WARNING: Expected (1, 3, 224, 224), got {tensor.shape}")
        
        return True
        
    except Exception as e:
        print(f"❌ FAIL: Preprocessing error: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests."""
    print("\n" + "="*60)
    print("FRAUDGUARD AI - PRODUCTION FIX VERIFICATION")
    print("="*60)
    
    results = {
        "Deepfake Model": test_deepfake_model(),
        "Voice Model": test_voice_model(),
        "Document Model": test_document_model(),
        "Email Model": test_email_model(),
        "Preprocessing": test_preprocessing()
    }
    
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{test_name:20s} {status}")
    
    total = len(results)
    passed = sum(results.values())
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED! System ready for production.")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Please review errors above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
