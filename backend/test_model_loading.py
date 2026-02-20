"""
Quick test script to verify trained models load correctly.
"""
import sys
from pathlib import Path

# Add app to path
sys.path.insert(0, str(Path(__file__).parent))

from app.services.deepfake_service import deepfake_service
from app.services.document_service import document_service
from app.services.voice_service import voice_service

print("\n" + "="*60)
print("Testing Model Loading")
print("="*60 + "\n")

# Test deepfake model
print("1. Deepfake Model:")
if deepfake_service.model is not None:
    print("   ✅ LOADED - Using trained model")
    print(f"   Model type: {type(deepfake_service.model).__name__}")
else:
    print("   ❌ NOT LOADED - Using mock predictions")

# Test document model
print("\n2. Document Model:")
if document_service.model is not None:
    print("   ✅ LOADED - Using trained model")
    print(f"   Model type: {type(document_service.model).__name__}")
else:
    print("   ❌ NOT LOADED - Using mock predictions")

# Test voice model
print("\n3. Voice Model:")
if voice_service.model is not None:
    print("   ✅ LOADED - Using trained model")
    print(f"   Model type: {type(voice_service.model).__name__}")
else:
    print("   ❌ NOT LOADED - Using mock predictions")

print("\n" + "="*60)
print("Summary")
print("="*60)

loaded_count = sum([
    deepfake_service.model is not None,
    document_service.model is not None,
    voice_service.model is not None
])

print(f"\nModels loaded: {loaded_count}/3")

if loaded_count == 3:
    print("\n🎉 SUCCESS! All models loaded correctly!")
    print("Your trained models are now being used for inference.")
elif loaded_count > 0:
    print(f"\n⚠️  PARTIAL: {loaded_count} model(s) loaded, {3-loaded_count} using mocks")
    print("Check logs above for errors on failed models.")
else:
    print("\n❌ FAILED: No models loaded, all using mock predictions")
    print("Check that:")
    print("  1. timm is installed: pip install timm==0.9.12")
    print("  2. Model files exist in ml_models/ folder")
    print("  3. Check error messages above")

print("\n" + "="*60 + "\n")
