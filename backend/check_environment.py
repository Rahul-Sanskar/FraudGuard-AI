"""
Check if Python environment is correctly configured.
Run from backend directory with venv activated.
"""
import sys
import os

print("=" * 60)
print("PYTHON ENVIRONMENT CHECK")
print("=" * 60)

print(f"\nPython executable: {sys.executable}")
print(f"Python version: {sys.version}")

# Check if running in venv
in_venv = hasattr(sys, 'real_prefix') or (
    hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix
)
print(f"\nRunning in virtual environment: {in_venv}")
if in_venv:
    print(f"   ✅ Virtual environment active")
    print(f"   Location: {sys.prefix}")
else:
    print(f"   ⚠️ NOT in virtual environment!")
    print(f"   Run: venv\\Scripts\\activate")

# Check PATH
print(f"\nPATH environment variable:")
path_dirs = os.environ.get('PATH', '').split(os.pathsep)
for i, p in enumerate(path_dirs[:5]):  # Show first 5
    print(f"   {i+1}. {p}")
print(f"   ... ({len(path_dirs)} total directories)")

# Check if FFmpeg directory is in PATH
ffmpeg_in_path = any('ffmpeg' in p.lower() for p in path_dirs)
print(f"\nFFmpeg directory in PATH: {ffmpeg_in_path}")

# Check installed packages
print("\nChecking required packages...")
packages = {
    'torch': 'PyTorch',
    'librosa': 'Librosa',
    'soundfile': 'SoundFile',
    'fastapi': 'FastAPI',
    'uvicorn': 'Uvicorn'
}

for pkg, name in packages.items():
    try:
        __import__(pkg)
        print(f"   ✅ {name} installed")
    except ImportError:
        print(f"   ❌ {name} NOT installed")

print("\n" + "=" * 60)
