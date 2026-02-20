"""
Test script to determine correct label order for deepfake model.
Run this with a real webcam photo to see which interpretation is correct.
"""
import torch
from pathlib import Path
from PIL import Image
from torchvision import transforms
from app.models.architectures import EfficientNetDeepfakeModel

print("=" * 60)
print("DEEPFAKE MODEL LABEL ORDER TEST")
print("=" * 60)

# Load model
model_path = Path("ml_models/deepfake_model_enhanced.pt")
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

print(f"\nLoading model from: {model_path}")
checkpoint = torch.load(model_path, map_location=device)

if isinstance(checkpoint, dict) and not hasattr(checkpoint, 'state_dict'):
    model = EfficientNetDeepfakeModel(num_classes=2)
    model.load_state_dict(checkpoint, strict=False)
else:
    model = checkpoint

model.to(device)
model.eval()
print("✅ Model loaded")

# Preprocessing (must match training)
preprocess = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
])

print("\n" + "=" * 60)
print("INSTRUCTIONS:")
print("=" * 60)
print("1. Take a photo of yourself with your webcam")
print("2. Save it as 'test_real_face.jpg' in the backend folder")
print("3. Run this script again")
print("\nThis will help determine if labels are reversed.")
print("=" * 60)

# Check if test image exists
test_image_path = Path("test_real_face.jpg")
if not test_image_path.exists():
    print("\n⚠️ test_real_face.jpg not found")
    print("Please capture a real webcam photo and save it as test_real_face.jpg")
    exit(0)

# Load and preprocess image
print(f"\nLoading test image: {test_image_path}")
image = Image.open(test_image_path).convert('RGB')
image_tensor = preprocess(image).unsqueeze(0).to(device)

# Check tensor stats
print(f"\nTensor statistics:")
print(f"  Min: {image_tensor.min():.3f}")
print(f"  Max: {image_tensor.max():.3f}")
print(f"  Mean: {image_tensor.mean():.3f}")
print(f"  Expected range: -2.1 to +2.3, mean ≈ 0")

if image_tensor.min() < -3 or image_tensor.max() > 3:
    print("  ⚠️ WARNING: Tensor values outside expected range!")
elif image_tensor.min() > 0:
    print("  ❌ ERROR: Tensor not normalized! Values should be negative/positive.")
else:
    print("  ✅ Tensor normalization looks correct")

# Run inference
print("\nRunning inference...")
with torch.no_grad():
    output = model(image_tensor)
    probabilities = torch.softmax(output, dim=-1)
    
    class_0_prob = probabilities[0][0].item()
    class_1_prob = probabilities[0][1].item()
    class_0_logit = output[0][0].item()
    class_1_logit = output[0][1].item()

print("\n" + "=" * 60)
print("RESULTS:")
print("=" * 60)
print(f"Raw logits:      [{class_0_logit:.3f}, {class_1_logit:.3f}]")
print(f"Probabilities:   [{class_0_prob:.3f}, {class_1_prob:.3f}]")

print("\n" + "=" * 60)
print("INTERPRETATION:")
print("=" * 60)

print("\nOption A: Standard labels (class_0=real, class_1=fake)")
print(f"  Real probability: {class_0_prob:.1%}")
print(f"  Fake probability: {class_1_prob:.1%}")
if class_0_prob > 0.7:
    print("  ✅ This makes sense for a real face")
else:
    print("  ❌ This doesn't make sense for a real face")

print("\nOption B: Reversed labels (class_0=fake, class_1=real)")
print(f"  Fake probability: {class_0_prob:.1%}")
print(f"  Real probability: {class_1_prob:.1%}")
if class_1_prob > 0.7:
    print("  ✅ This makes sense for a real face")
else:
    print("  ❌ This doesn't make sense for a real face")

print("\n" + "=" * 60)
print("RECOMMENDATION:")
print("=" * 60)

if class_0_prob > 0.7:
    print("✅ Use STANDARD labels: class_0=real, class_1=fake")
    print("   In deepfake_service.py, set:")
    print("   real_prob = class_0_prob")
    print("   fake_prob = class_1_prob")
elif class_1_prob > 0.7:
    print("✅ Use REVERSED labels: class_0=fake, class_1=real")
    print("   In deepfake_service.py, set:")
    print("   real_prob = class_1_prob")
    print("   fake_prob = class_0_prob")
    print("   (This is currently implemented)")
else:
    print("⚠️ Model is uncertain (both probabilities < 70%)")
    print("   This could mean:")
    print("   1. Image quality is poor")
    print("   2. Model needs retraining")
    print("   3. Preprocessing still doesn't match training")

print("\n" + "=" * 60)
