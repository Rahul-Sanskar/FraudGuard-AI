"""
Script to inspect the format of saved PyTorch models.
This helps determine how to properly load them.
"""
import torch
from pathlib import Path


def inspect_model(model_path: Path):
    """Inspect a PyTorch model file and print its structure."""
    print(f"\n{'='*60}")
    print(f"Inspecting: {model_path.name}")
    print(f"{'='*60}")
    
    if not model_path.exists():
        print(f"❌ File not found: {model_path}")
        return
    
    try:
        # Load the checkpoint
        checkpoint = torch.load(model_path, map_location='cpu')
        
        # Check the type
        print(f"\nType: {type(checkpoint)}")
        
        if isinstance(checkpoint, dict):
            print(f"\n📦 Dictionary with {len(checkpoint)} keys:")
            for key in checkpoint.keys():
                value = checkpoint[key]
                if isinstance(value, torch.Tensor):
                    print(f"  - {key}: Tensor {value.shape}")
                elif isinstance(value, dict):
                    print(f"  - {key}: Dict with {len(value)} items")
                else:
                    print(f"  - {key}: {type(value).__name__}")
            
            # Check for common keys
            if 'model_state_dict' in checkpoint:
                print("\n✅ Contains 'model_state_dict' - saved with state dict")
                state_dict = checkpoint['model_state_dict']
                print(f"   State dict has {len(state_dict)} parameters")
                print("\n   First 5 parameter names:")
                for i, key in enumerate(list(state_dict.keys())[:5]):
                    print(f"     {i+1}. {key}: {state_dict[key].shape}")
            
            elif 'state_dict' in checkpoint:
                print("\n✅ Contains 'state_dict' - saved with state dict")
                state_dict = checkpoint['state_dict']
                print(f"   State dict has {len(state_dict)} parameters")
                print("\n   First 5 parameter names:")
                for i, key in enumerate(list(state_dict.keys())[:5]):
                    print(f"     {i+1}. {key}: {state_dict[key].shape}")
            
            else:
                print("\n⚠️  No standard state_dict key found")
                print("   This might be a custom format")
        
        elif hasattr(checkpoint, 'state_dict'):
            print("\n✅ Complete model object (nn.Module)")
            print(f"   Model type: {type(checkpoint).__name__}")
            print(f"   Model class: {checkpoint.__class__.__name__}")
            
            # Try to get state dict
            try:
                state_dict = checkpoint.state_dict()
                print(f"   State dict has {len(state_dict)} parameters")
                print("\n   First 5 parameter names:")
                for i, key in enumerate(list(state_dict.keys())[:5]):
                    print(f"     {i+1}. {key}: {state_dict[key].shape}")
            except:
                print("   Could not extract state_dict")
        
        else:
            print(f"\n⚠️  Unknown format: {type(checkpoint)}")
        
        # File size
        size_mb = model_path.stat().st_size / (1024 * 1024)
        print(f"\n📊 File size: {size_mb:.2f} MB")
        
        print(f"\n{'='*60}\n")
        
    except Exception as e:
        print(f"\n❌ Error loading model: {e}")
        print(f"   Error type: {type(e).__name__}")
        print(f"\n{'='*60}\n")


def main():
    """Inspect all models in ml_models directory."""
    print("\n🔍 PyTorch Model Inspector")
    print("="*60)
    
    ml_models_dir = Path("ml_models")
    
    if not ml_models_dir.exists():
        print(f"❌ Directory not found: {ml_models_dir}")
        return
    
    # Find all .pt files
    model_files = list(ml_models_dir.glob("*.pt"))
    
    if not model_files:
        print(f"❌ No .pt files found in {ml_models_dir}")
        return
    
    print(f"\nFound {len(model_files)} model file(s):\n")
    
    for model_path in model_files:
        inspect_model(model_path)
    
    print("\n" + "="*60)
    print("📝 Summary:")
    print("="*60)
    print("""
If models are saved as:
1. Complete nn.Module objects → ✅ Current code will work
2. State dicts only → ❌ Need model architecture definition
3. Custom format → ❌ Need custom loading code

To properly load state_dict models, you need to:
1. Define the model architecture (class definition)
2. Instantiate the model
3. Load the state_dict into it

Example:
    model = YourModelClass()
    checkpoint = torch.load('model.pt')
    model.load_state_dict(checkpoint['state_dict'])
    model.eval()
""")


if __name__ == "__main__":
    main()
