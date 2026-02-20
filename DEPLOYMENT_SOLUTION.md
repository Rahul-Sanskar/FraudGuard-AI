# 🎯 Complete Railway Deployment Solution

## Problem Analysis

**Your Error:**
```
Script start.sh not found
Railpack could not determine how to build the app.
```

**Root Cause:**
1. Railway tried to build from root directory (contains both backend and frontend)
2. No clear entry point detected
3. Monorepo structure confused Railpack

**Solution:**
Deploy backend and frontend as **separate services** with proper configuration files.

---

## ✅ Solution Implemented

### Files Created

#### Backend Deployment Files

**1. `backend/Procfile`**
```
web: uvicorn app.main:app --host 0.0.0.0 --port $PORT
```
- Tells Railway how to start your app
- Uses $PORT environment variable (Railway requirement)

**2. `backend/runtime.txt`**
```
python-3.11
```
- Specifies Python version
- Ensures consistent runtime

**3. `backend/railway.json`**
```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "uvicorn app.main:app --host 0.0.0.0 --port $PORT --workers 4",
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
```
- Railway service configuration
- 4 workers for production performance
- Auto-restart on failure

**4. `backend/nixpacks.toml`**
```toml
[phases.setup]
nixPkgs = ["python311", "ffmpeg", "poppler_utils"]
aptPkgs = ["libsndfile1"]

[phases.install]
cmds = ["pip install --upgrade pip", "pip install -r requirements.txt"]

[phases.build]
cmds = ["mkdir -p ml_models"]

[start]
cmd = "uvicorn app.main:app --host 0.0.0.0 --port $PORT --workers 4"
```
- Build configuration
- Installs system dependencies (FFmpeg for audio, Poppler for PDFs)
- Installs Python packages
- Creates ml_models directory

#### Frontend Deployment Files

**Already Configured:**
- `frontend/netlify.toml` - Netlify deployment
- `frontend/vercel.json` - Vercel alternative

---

## 📁 Final Project Structure

```
fraud-guard/
├── .gitignore                          ✅ Configured
├── README.md                           ✅ Complete guide
├── RAILWAY_DEPLOYMENT_GUIDE.md         ✅ Detailed instructions
├── DEPLOY_QUICK_START.txt              ✅ Quick reference
│
├── backend/                            ← DEPLOY THIS TO RAILWAY
│   ├── Procfile                        ✅ NEW - Railway process
│   ├── runtime.txt                     ✅ NEW - Python version
│   ├── railway.json                    ✅ UPDATED - 4 workers
│   ├── nixpacks.toml                   ✅ UPDATED - System deps
│   ├── Dockerfile                      ✅ Alternative method
│   ├── requirements.txt                ✅ Python dependencies
│   ├── .env.example                    ✅ Environment template
│   ├── .gitignore                      ✅ Excludes venv, .env, *.db
│   ├── app/                            ✅ FastAPI application
│   └── ml_models/                      ✅ Pre-trained models
│
└── frontend/                           ← DEPLOY THIS TO NETLIFY
    ├── netlify.toml                    ✅ Netlify config
    ├── vercel.json                     ✅ Vercel alternative
    ├── package.json                    ✅ Node dependencies
    ├── .env.example                    ✅ Environment template
    ├── .gitignore                      ✅ Excludes node_modules, dist
    └── src/                            ✅ React application
```

---

## 🚀 Deployment Steps (Exact Commands)

### Step 1: Push to GitHub

```bash
# Navigate to project
cd fraud-guard

# Initialize Git (if not done)
git init

# Add all files
git add .

# Commit
git commit -m "feat: Add Railway deployment configuration"

# Add remote (replace with your URL)
git remote add origin https://github.com/YOUR_USERNAME/fraudguard-ai.git

# Push
git branch -M main
git push -u origin main
```

### Step 2: Deploy Backend to Railway

**2.1 Create Project**
1. Open https://railway.app
2. Click "New Project"
3. Select "Deploy from GitHub repo"
4. Choose `fraudguard-ai` repository
5. Click "Deploy Now"

**2.2 Set Root Directory (CRITICAL)**
```
Settings → Service → Root Directory = "backend"
```
This tells Railway to build from the backend folder, not the root.

**2.3 Add Environment Variables**
```bash
DATABASE_URL=sqlite:///./fraudguard.db
SECRET_KEY=<generate-with-command-below>
MODEL_PATH=ml_models
MAX_FILE_SIZE=104857600
LOG_LEVEL=INFO
```

**Generate SECRET_KEY:**
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

**2.4 Verify Deployment**
```bash
# Replace with your Railway URL
curl https://your-app.railway.app/api/v1/health

# Expected response:
# {"status":"healthy","version":"1.0.0","timestamp":"..."}
```

### Step 3: Deploy Frontend to Netlify

**3.1 Create Site**
1. Open https://app.netlify.com
2. Click "Add new site" → "Import an existing project"
3. Select "Deploy with GitHub"
4. Choose `fraudguard-ai` repository

**3.2 Configure Build**
```
Base directory: frontend
Build command: npm run build
Publish directory: frontend/dist
```

**3.3 Add Environment Variable**
```bash
VITE_API_URL=https://your-backend-url.railway.app
```
⚠️ No trailing slash!

**3.4 Deploy**
Click "Deploy site" and wait for completion.

---

## 🔍 Verification Commands

### Backend Health Check
```bash
# Set your Railway URL
BACKEND_URL="https://your-app.railway.app"

# Health check
curl $BACKEND_URL/api/v1/health

# Models loaded
curl $BACKEND_URL/api/v1/health/models

# API documentation
open $BACKEND_URL/docs
```

### Frontend Check
```bash
# Open in browser
open https://your-app.netlify.app

# Check browser console (F12) for errors
# Check Network tab for API calls
```

---

## 🐛 Troubleshooting Guide

### Error: "Railpack could not determine how to build"

**Cause:** Root directory not set to `backend`

**Fix:**
1. Railway Dashboard → Your Service
2. Settings → Service
3. Root Directory = `backend`
4. Save (auto-redeploys)

### Error: "Module not found: app.main"

**Cause:** Wrong directory structure or missing files

**Fix:**
1. Verify `backend/app/main.py` exists
2. Check Railway logs for specific error
3. Ensure root directory is set to `backend`

### Error: "Port already in use"

**Cause:** Not using $PORT variable

**Fix:** Already handled in Procfile and nixpacks.toml

### Error: "Models not loading"

**Cause:** ML model files missing or too large

**Fix:**
1. Check `backend/ml_models/*.pt` files exist
2. Verify they're committed to Git (not in .gitignore)
3. Check Railway logs for loading errors

### Error: "Database connection failed"

**Cause:** DATABASE_URL not set or invalid

**Fix:**
1. Check environment variable is set
2. For SQLite: `sqlite:///./fraudguard.db`
3. For PostgreSQL: Use Railway-provided URL

### Error: "CORS policy blocked"

**Cause:** Backend not allowing frontend domain

**Fix:** Already configured in backend to allow all origins

### Error: "Frontend build failed"

**Cause:** Missing dependencies or wrong Node version

**Fix:**
1. Check Netlify build logs
2. Verify Node version is 18
3. Check all dependencies in package.json

---

## ✅ Final Verification Checklist

### Pre-Deployment
- [ ] All code pushed to GitHub
- [ ] No .env files in repository
- [ ] No *.db files in repository
- [ ] ML models committed (backend/ml_models/*.pt)
- [ ] requirements.txt complete
- [ ] package.json complete

### Backend (Railway)
- [ ] Service created from GitHub
- [ ] Root directory set to `backend`
- [ ] All environment variables added
- [ ] Deployment successful (green checkmark)
- [ ] Health endpoint works: `/api/v1/health`
- [ ] Models endpoint works: `/api/v1/health/models`
- [ ] API docs accessible: `/docs`
- [ ] No errors in Railway logs
- [ ] 4 workers running (check logs)

### Frontend (Netlify)
- [ ] Site created from GitHub
- [ ] Base directory: `frontend`
- [ ] Build command: `npm run build`
- [ ] Publish directory: `frontend/dist`
- [ ] VITE_API_URL environment variable set
- [ ] Deployment successful
- [ ] Site loads without errors
- [ ] No errors in browser console (F12)
- [ ] API calls work (check Network tab)

### Integration Testing
- [ ] Upload image → Returns analysis
- [ ] Upload video → Returns analysis
- [ ] Upload audio → Returns analysis
- [ ] Upload PDF → Returns analysis
- [ ] Submit email → Returns analysis
- [ ] Live webcam works (if camera available)
- [ ] Live voice works (if microphone available)
- [ ] Response times < 5 seconds
- [ ] No CORS errors

---

## 📊 Production Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     PRODUCTION SETUP                         │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  User Browser                                                │
│       │                                                      │
│       ├──→ Frontend (Netlify CDN)                           │
│       │    ├── React + Vite                                 │
│       │    ├── Static files served from CDN                 │
│       │    └── Fast global delivery                         │
│       │                                                      │
│       └──→ Backend (Railway)                                │
│            ├── FastAPI + Uvicorn                            │
│            ├── 4 Workers (production)                       │
│            ├── SQLite or PostgreSQL                         │
│            ├── ML Models loaded in memory                   │
│            └── Auto-scaling enabled                         │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

**Benefits:**
- ✅ Frontend on CDN (fast, free)
- ✅ Backend on Railway (scalable, managed)
- ✅ Independent scaling
- ✅ Separate logs and monitoring
- ✅ Easy rollbacks
- ✅ Cost-effective

---

## 🎯 Why This Solution Works

### 1. Separate Deployments
- Backend and frontend have different requirements
- Python backend needs different runtime than Node frontend
- Easier to debug and scale independently

### 2. Proper Configuration Files
- `Procfile` - Railway knows how to start your app
- `runtime.txt` - Correct Python version
- `railway.json` - Production settings (4 workers)
- `nixpacks.toml` - System dependencies (FFmpeg, Poppler)

### 3. Root Directory Setting
- Tells Railway to build from `backend/` not root
- Fixes "Railpack could not determine how to build" error

### 4. Environment Variables
- Secure configuration
- Easy to change without code changes
- Different values for dev/prod

### 5. Production Optimizations
- 4 Uvicorn workers for concurrency
- Auto-restart on failure
- Health checks enabled
- Proper logging

---

## 📚 Additional Resources

### Railway
- Docs: https://docs.railway.app
- Discord: https://discord.gg/railway
- Status: https://status.railway.app

### Netlify
- Docs: https://docs.netlify.com
- Community: https://answers.netlify.com
- Status: https://www.netlifystatus.com

### FastAPI
- Docs: https://fastapi.tiangolo.com
- Deployment: https://fastapi.tiangolo.com/deployment/

### Uvicorn
- Docs: https://www.uvicorn.org
- Workers: https://www.uvicorn.org/deployment/

---

## 🎉 Success Criteria

Your deployment is successful when:

1. ✅ Backend health check returns 200 OK
2. ✅ All models show "loaded: true"
3. ✅ Frontend loads without errors
4. ✅ API calls work from frontend
5. ✅ All detection modules functional
6. ✅ No errors in logs
7. ✅ Response times < 5 seconds

---

## 🚀 You're Ready to Deploy!

**Total Time:** ~10-15 minutes

**Steps:**
1. Push to GitHub (2 min)
2. Deploy backend to Railway (5 min)
3. Deploy frontend to Netlify (3 min)
4. Verify integration (5 min)

**Key Point:** Set Railway Root Directory to `backend` and you're good to go!

---

**Questions?** Check `RAILWAY_DEPLOYMENT_GUIDE.md` for detailed instructions.
