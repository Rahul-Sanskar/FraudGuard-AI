# 🐳 Docker Image Optimization Guide

## Problem Analysis

**Original Image Size**: ~6.8 GB
**Railway Limit**: 4 GB
**Target Size**: < 3 GB

### Size Breakdown (Original)
- CUDA PyTorch: ~3.5 GB
- ML Models: ~420 MB (deepfake: 18MB, document: 41MB, voice: 361MB)
- System dependencies: ~500 MB
- Application code: ~50 MB
- Other dependencies: ~2.3 GB

---

## ✅ Optimization Strategy

### 1. **Use CPU-Only PyTorch** (Saves ~2.5 GB)
- Replace CUDA PyTorch with CPU version
- CUDA: `torch==2.1.2` (~3.5 GB)
- CPU: `torch==2.1.2+cpu` (~800 MB)
- **Savings: ~2.7 GB**

### 2. **Exclude ML Models from Image** (Saves ~420 MB)
- Models NOT bundled in Docker image
- Downloaded at runtime or loaded from persistent storage
- **Savings: ~420 MB**

### 3. **Multi-Stage Build** (Saves ~300 MB)
- Build dependencies in separate stage
- Only copy runtime artifacts to final image
- Remove gcc, g++, build tools from final image
- **Savings: ~300 MB**

### 4. **Optimize Dependencies** (Saves ~200 MB)
- Use `opencv-python-headless` instead of `opencv-python`
- Remove test dependencies (pytest)
- Use `--no-cache-dir` for pip
- Clean apt cache properly
- **Savings: ~200 MB**

### 5. **Proper .dockerignore** (Saves ~100 MB)
- Exclude venv, __pycache__, .git
- Exclude test files, notebooks
- Exclude datasets, logs
- **Savings: ~100 MB**

---

## 📦 Files Created

### 1. `.dockerignore`
Excludes unnecessary files from Docker context:
- ML models (*.pt, *.pth, *.bin)
- Python cache (__pycache__)
- Virtual environments (venv/)
- Test files and datasets
- Documentation and config files

### 2. `Dockerfile.optimized`
Optimized multi-stage Dockerfile:
- Stage 1: Build dependencies
- Stage 2: Minimal runtime image
- CPU-only PyTorch
- No build tools in final image
- Non-root user for security

### 3. `requirements-cpu.txt`
Updated requirements without CUDA PyTorch:
- Uses `opencv-python-headless`
- Removes test dependencies
- Comments out PyTorch (installed separately)

### 4. `download_models.py`
Runtime model downloader:
- Downloads models from URLs
- Supports HuggingFace Hub
- Checks if models exist
- Progress bars for downloads

### 5. `start.sh`
Startup script:
- Checks for models
- Downloads if missing
- Starts uvicorn server

---

## 🚀 Deployment Options

### Option 1: Railway Persistent Volume (Recommended)

**Setup:**
1. Add Railway volume to your service
2. Mount at `/app/ml_models`
3. Upload models once to volume
4. Models persist across deployments

**Advantages:**
- Models loaded instantly
- No download time on startup
- No external dependencies
- Free on Railway

**Steps:**
```bash
# 1. Deploy with optimized Dockerfile
# 2. In Railway dashboard:
#    - Go to your service
#    - Click "Variables" → "Add Volume"
#    - Mount path: /app/ml_models
# 3. Upload models to volume (one-time):
railway run bash
# Inside container:
# Upload your .pt files to ml_models/
```

### Option 2: Download from Cloud Storage

**Setup:**
1. Upload models to cloud storage (S3, GCS, Cloudflare R2)
2. Generate public URLs or signed URLs
3. Set environment variables with URLs
4. Models download on first startup

**Environment Variables:**
```bash
DEEPFAKE_MODEL_URL=https://your-storage.com/deepfake_model_enhanced.pt
DOCUMENT_MODEL_URL=https://your-storage.com/document_model.pt
VOICE_MODEL_URL=https://your-storage.com/voice_spoof_model.pt
```

**Advantages:**
- Easy to update models
- Can use CDN for fast downloads
- Works with any cloud provider

**Disadvantages:**
- Slower first startup (~2-3 minutes)
- Requires internet access
- Download on every cold start

### Option 3: HuggingFace Hub

**Setup:**
1. Upload models to HuggingFace Hub
2. Use `huggingface_hub` library
3. Models cached locally after first download

**Code:**
```python
from huggingface_hub import hf_hub_download

model_path = hf_hub_download(
    repo_id="your-username/fraudguard-models",
    filename="deepfake_model_enhanced.pt"
)
```

**Advantages:**
- Free hosting
- Version control
- Easy sharing
- Built-in caching

---

## 📋 Deployment Steps

### Step 1: Update Dockerfile

Replace your current `Dockerfile` with `Dockerfile.optimized`:

```bash
cd fraud-guard/backend
mv Dockerfile Dockerfile.old
mv Dockerfile.optimized Dockerfile
```

### Step 2: Update Requirements

Replace `requirements.txt` with `requirements-cpu.txt`:

```bash
mv requirements.txt requirements-cuda.txt
mv requirements-cpu.txt requirements.txt
```

### Step 3: Build and Test Locally

```bash
# Build image
docker build -t fraudguard-backend:optimized .

# Check image size
docker images fraudguard-backend:optimized

# Expected: < 2.5 GB

# Test run
docker run -p 8000:8000 \
  -e DATABASE_URL=sqlite:///./fraudguard.db \
  -e SECRET_KEY=test-key \
  fraudguard-backend:optimized
```

### Step 4: Deploy to Railway

```bash
# Commit changes
git add .
git commit -m "feat: Optimize Docker image for Railway deployment"
git push origin main

# Railway will auto-deploy
```

### Step 5: Configure Railway Volume (Recommended)

1. Go to Railway dashboard
2. Select your service
3. Click "Variables" tab
4. Click "Add Volume"
5. Mount path: `/app/ml_models`
6. Save

### Step 6: Upload Models to Volume

**Option A: Using Railway CLI**
```bash
railway run bash
# Inside container:
# Upload your models to /app/ml_models/
```

**Option B: Using download script**
Set environment variables with model URLs and let the app download them.

---

## 🔍 Verification Checklist

### Before Deployment
- [ ] `.dockerignore` created
- [ ] `Dockerfile.optimized` renamed to `Dockerfile`
- [ ] `requirements-cpu.txt` renamed to `requirements.txt`
- [ ] PyTorch version uses `+cpu` suffix
- [ ] ML models excluded from Docker context
- [ ] Multi-stage build configured
- [ ] Non-root user configured

### After Build
- [ ] Docker image size < 3 GB
- [ ] Image builds successfully
- [ ] No CUDA dependencies in image
- [ ] FFmpeg and Poppler installed
- [ ] Application code copied correctly
- [ ] ml_models directory exists (empty)

### After Deployment
- [ ] Railway deployment successful
- [ ] Container starts without errors
- [ ] Health endpoint responds: `/api/v1/health`
- [ ] Models loaded (from volume or downloaded)
- [ ] API endpoints work correctly
- [ ] No memory issues
- [ ] Response times acceptable

---

## 📊 Expected Results

### Image Size Comparison

| Component | Original | Optimized | Savings |
|-----------|----------|-----------|---------|
| PyTorch | 3.5 GB | 0.8 GB | 2.7 GB |
| ML Models | 420 MB | 0 MB | 420 MB |
| Build Tools | 300 MB | 0 MB | 300 MB |
| Dependencies | 2.3 GB | 1.5 GB | 800 MB |
| Application | 50 MB | 50 MB | 0 MB |
| **Total** | **6.8 GB** | **2.4 GB** | **4.4 GB** |

### Build Time
- Original: ~15-20 minutes
- Optimized: ~8-12 minutes
- **Improvement: ~40% faster**

### Startup Time
- With volume: ~10 seconds
- With download: ~2-3 minutes (first time), ~10 seconds (cached)

---

## 🐛 Troubleshooting

### "Image size still > 4 GB"

**Check:**
1. Verify `.dockerignore` is working:
   ```bash
   docker build --no-cache -t test .
   docker history test
   ```
2. Ensure PyTorch is CPU version:
   ```bash
   docker run test pip list | grep torch
   # Should show: torch 2.1.2+cpu
   ```
3. Check no models in image:
   ```bash
   docker run test ls -lh ml_models/
   # Should be empty or only .gitkeep
   ```

### "Models not loading"

**Check:**
1. Railway volume mounted correctly
2. Model URLs set in environment variables
3. Download script has permissions
4. Check logs for download errors

### "Application crashes on startup"

**Check:**
1. All dependencies installed
2. FFmpeg and Poppler available
3. Database URL set correctly
4. Sufficient memory allocated

### "Import errors for torch"

**Check:**
1. PyTorch installed with CPU suffix
2. No CUDA dependencies in requirements
3. Rebuild image with `--no-cache`

---

## 💡 Additional Optimizations

### 1. Use Alpine Linux (Advanced)
- Even smaller base image (~5 MB vs ~50 MB)
- Requires more complex setup
- May have compatibility issues

### 2. Compress Models
- Use model quantization
- Convert to ONNX format
- Use model pruning
- Can reduce model size by 50-75%

### 3. Lazy Loading
- Load models only when needed
- Unload unused models
- Reduces memory usage

### 4. Model Caching
- Cache models in Railway volume
- Share volume across deployments
- Faster cold starts

---

## 📚 Resources

- [Docker Multi-Stage Builds](https://docs.docker.com/build/building/multi-stage/)
- [PyTorch CPU Installation](https://pytorch.org/get-started/locally/)
- [Railway Volumes](https://docs.railway.app/reference/volumes)
- [Docker Best Practices](https://docs.docker.com/develop/dev-best-practices/)

---

## ✅ Success Criteria

Your optimization is successful when:

1. ✅ Docker image size < 3 GB
2. ✅ Build completes in < 15 minutes
3. ✅ Railway deployment succeeds
4. ✅ Application starts in < 30 seconds
5. ✅ All API endpoints work
6. ✅ Models load correctly
7. ✅ No memory issues
8. ✅ Response times < 5 seconds

---

## 🎉 Expected Final Size

**Docker Image**: ~2.4 GB
**Railway Deployment**: ✅ Under 4 GB limit
**Free Plan**: ✅ Compatible

**You're ready to deploy!** 🚀
