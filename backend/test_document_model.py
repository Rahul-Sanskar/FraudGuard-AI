"""
Diagnostic script to test document model inference.
Run this to identify why all predictions are 50.5%.
"""
import torch
from pathlib import Path
from PIL import Image
import numpy as np
from torchvision import transforms

print("=" * 60)
print("DOCUMENT MODEL DIAGNOSTIC TEST")
print("=" * 60)

# Load model
model_path = Path("ml_models/document_model.pt")
device = torch.device("cpu")

print(f"\n1. Checking model file...")
print(f"   Path: {model_path}")
print(f"   Exists: {model_path.exists()}")

if not model_path.exists():
    print("   ❌ Model file not found!")
    exit(1)

print(f"   Size: {model_path.stat().st_size / 1024 / 1024:.2f} MB")

# Load checkpoint
print(f"\n2. Loading checkpoint...")
checkpoint = torch.load(model_path, map_location=device)
print(f"   Type: {type(checkpoint)}")

if isinstance(checkpoint, dict):
    print(f"   Keys: {list(checkpoint.keys())[:10]}")
    print(f"   Total keys: {len(checkpoint.keys())}")
    
    # Check if it's a state_dict
    if 'classifier.weight' in checkpoint or 'head.weight' in checkpoint:
        print("   Format: State dict (weights only)")
        
        # Try to load with architecture
        from app.models.architectures import EfficientNetDocumentModel
        
        print(f"\n3. Instantiating model architecture...")
        model = EfficientNetDocumentModel(num_classes=1)
        
        print(f"\n4. Loading state dict...")
        missing, unexpected = model.load_state_dict(checkpoint, strict=False)
        
        if missing:
            print(f"   ⚠️ Missing keys: {missing}")
        if unexpected:
            print(f"   ⚠️ Unexpected keys: {unexpected}")
        
        model.to(device)
        model.eval()
        
    else:
        print("   Format: Unknown dict structure")
        print(f"   First key: {list(checkpoint.keys())[0]}")
        exit(1)
else:
    print("   Format: Complete model object")
    model = checkpoint
    model.to(device)
    model.eval()

print(f"\n5. Checking model weights...")

# Find classifier layer
if hasattr(model, 'classifier'):
    classifier = model.classifier
    print(f"   Classifier type: {type(classifier)}")
    
    if hasattr(classifier, 'weight'):
        weight = classifier.weight
        print(f"   Weight shape: {weight.shape}")
        print(f"   Weight mean: {weight.mean().item():.6f}")
        print(f"   Weight std: {weight.std().item():.6f}")
        print(f"   Weight min: {weight.min().item():.6f}")
        print(f"   Weight max: {weight.max().item():.6f}")
        
        # Check if weights look random (untrained)
        if abs(weight.mean().item()) < 0.001 and weight.std().item() < 0.01:
            print("   ❌ WARNING: Weights look randomly initialized!")
            print("      Model may not be trained")
        else:
            print("   ✅ Weights look trained")
    
    if hasattr(classifier, 'bias') and classifier.bias is not None:
        bias = classifier.bias
        print(f"   Bias value: {bias.item():.6f}")
elif hasattr(model, 'head'):
    print("   Using 'head' instead of 'classifier'")
    head = model.head
    if hasattr(head, 'weight'):
        weight = head.weight
        print(f"   Weight mean: {weight.mean().item():.6f}")
        print(f"   Weight std: {weight.std().item():.6f}")

print(f"\n6. Testing inference with dummy input...")

# Create dummy input (224x224 RGB image)
dummy_input = torch.randn(1, 3, 224, 224).to(device)
print(f"   Input shape: {dummy_input.shape}")
print(f"   Input stats - min: {dummy_input.min():.3f}, max: {dummy_input.max():.3f}, mean: {dummy_input.mean():.3f}")

# Run inference
with torch.no_grad():
    output = model(dummy_input)
    
print(f"\n   Output shape: {output.shape}")
print(f"   Raw output (logit): {output.item():.6f}")

# Apply sigmoid
probability = torch.sigmoid(output).item()
print(f"   After sigmoid: {probability:.6f}")
print(f"   Risk percentage: {probability * 100:.2f}%")

# Check if output is suspicious
if 0.49 < probability < 0.51:
    print(f"\n   ⚠️ WARNING: Output is {probability:.4f} (very close to 0.5)")
    print(f"      This suggests:")
    print(f"      1. Model weights are randomly initialized (not trained)")
    print(f"      2. Model architecture doesn't match saved weights")
    print(f"      3. Logit is near zero: {output.item():.6f}")
else:
    print(f"\n   ✅ Output looks reasonable: {probability:.4f}")

print(f"\n7. Testing with real image preprocessing...")

# Create a simple test image
test_image = Image.new('RGB', (224, 224), color=(128, 128, 128))

# Apply same preprocessing as service
preprocess = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
])

image_tensor = preprocess(test_image).unsqueeze(0).to(device)
print(f"   Preprocessed tensor stats:")
print(f"   - min: {image_tensor.min():.3f}")
print(f"   - max: {image_tensor.max():.3f}")
print(f"   - mean: {image_tensor.mean():.3f}")
print(f"   - std: {image_tensor.std():.3f}")

# Run inference
with torch.no_grad():
    output = model(image_tensor)
    probability = torch.sigmoid(output).item()

print(f"\n   Result:")
print(f"   - Raw logit: {output.item():.6f}")
print(f"   - Probability: {probability:.6f}")
print(f"   - Risk: {probability * 100:.2f}%")

print("\n" + "=" * 60)
print("DIAGNOSIS COMPLETE")
print("=" * 60)

if 0.49 < probability < 0.51:
    print("\n❌ PROBLEM IDENTIFIED:")
    print("   Model is producing ~50% for all inputs")
    print("   Root cause: Logit near zero (untrained or mismatched weights)")
    print("\n   SOLUTIONS:")
    print("   1. Retrain the model with proper data")
    print("   2. Check if model architecture matches training")
    print("   3. Verify state_dict keys match model structure")
    print("   4. Use a different pre-trained model")
else:
    print("\n✅ Model appears to be working correctly")
    print("   Different inputs should produce different outputs")

print("\n" + "=" * 60)
