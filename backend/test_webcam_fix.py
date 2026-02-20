"""
Test script to verify webcam image processing fix.
"""
import io
from PIL import Image
import numpy as np

# Create a test image
test_image = Image.new('RGB', (640, 480), color='red')

# Convert to bytes (simulating webcam capture)
img_byte_arr = io.BytesIO()
test_image.save(img_byte_arr, format='JPEG')
img_bytes = img_byte_arr.getvalue()

print(f"Created test image: {len(img_bytes)} bytes")

# Test 1: Direct bytes
print("\nTest 1: Direct bytes")
try:
    img = Image.open(io.BytesIO(img_bytes))
    print(f"✅ Success: {img.size}")
except Exception as e:
    print(f"❌ Error: {e}")

# Test 2: BytesIO object (without seek)
print("\nTest 2: BytesIO object (without seek)")
try:
    bio = io.BytesIO(img_bytes)
    img = Image.open(bio)
    print(f"✅ Success: {img.size}")
except Exception as e:
    print(f"❌ Error: {e}")

# Test 3: BytesIO object (with seek)
print("\nTest 3: BytesIO object (with seek)")
try:
    bio = io.BytesIO(img_bytes)
    bio.seek(0)
    img = Image.open(bio)
    print(f"✅ Success: {img.size}")
except Exception as e:
    print(f"❌ Error: {e}")

# Test 4: Simulate service preprocessing
print("\nTest 4: Simulate service preprocessing")
try:
    from app.services.deepfake_service import deepfake_service
    
    result = deepfake_service.analyze_image(img_bytes)
    print(f"✅ Success: risk_score={result['risk_score']:.3f}")
except Exception as e:
    print(f"❌ Error: {e}")

print("\n✅ All tests completed!")
