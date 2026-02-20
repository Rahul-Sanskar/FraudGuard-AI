"""
Quick test to verify FFmpeg is accessible from Python.
Run this from the backend directory with venv activated.
"""
import shutil
import subprocess
import sys

print("=" * 60)
print("FFMPEG AVAILABILITY TEST")
print("=" * 60)

# Test 1: Check if ffmpeg is in PATH
ffmpeg_path = shutil.which("ffmpeg")
print(f"\n1. FFmpeg in PATH: {ffmpeg_path is not None}")
if ffmpeg_path:
    print(f"   Location: {ffmpeg_path}")
else:
    print("   ❌ FFmpeg NOT found in PATH")
    print("\n   SOLUTION:")
    print("   1. Close this terminal completely")
    print("   2. Open a NEW terminal")
    print("   3. Verify: ffmpeg -version")
    print("   4. Then activate venv and start backend")
    sys.exit(1)

# Test 2: Try to run ffmpeg
print("\n2. Testing FFmpeg execution...")
try:
    result = subprocess.run(
        ["ffmpeg", "-version"],
        capture_output=True,
        text=True,
        timeout=5
    )
    print(f"   ✅ FFmpeg runs successfully")
    version_line = result.stdout.split('\n')[0]
    print(f"   Version: {version_line}")
except Exception as e:
    print(f"   ❌ FFmpeg execution failed: {e}")
    sys.exit(1)

# Test 3: Check librosa and soundfile
print("\n3. Checking audio libraries...")
try:
    import librosa
    import soundfile as sf
    print("   ✅ librosa installed")
    print("   ✅ soundfile installed")
except ImportError as e:
    print(f"   ❌ Missing library: {e}")
    print("   Install with: pip install librosa soundfile")
    sys.exit(1)

print("\n" + "=" * 60)
print("✅ ALL CHECKS PASSED - Voice analysis should work!")
print("=" * 60)
print("\nNow restart your backend server and test voice recording.")
