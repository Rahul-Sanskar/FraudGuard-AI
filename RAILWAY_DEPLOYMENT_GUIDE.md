# 🚂 Railway Deployment Guide - Complete Solution

## Architecture Decision

**✅ RECOMMENDED: Deploy Backend and Frontend Separately**

### Why Separate Deployments?

1. **Independent Scaling**: Scale backend and frontend independently
2. **Different Build Processes**: Python backend vs Node frontend
3. **Better Performance**: Frontend on CDN (Netlify/Vercel), Backend on Railway
4. **Easier Debugging**: Separate logs and monitoring
5. **Cost Effective**: Frontend is free on Netlify/Vercel

### Deployment Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    PRODUCTION SETUP                      │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  Frontend (Netlify/Vercel)                              │
│  ├── React + Vite Build                                 │
│  ├── Served from CDN                                    │
│  └── Calls Backend API                                  │
│                                                          │
│  Backend (Railway)                                      │
│  ├── FastAPI + Uvicorn                                  │
│  ├── 4 Workers for Production                           │
│  ├── SQLite or PostgreSQL                               │
│  └── ML Models Loaded                                   │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

---

## 📋 Pre-Deployment Checklist

### ✅ Files Created (Already Done)
- [x] `backend/Procfile` - Railway process file
- [x] `backend/runtime.txt` - Python version
- [x] `backend/railway.json` - Railway configuration
- [x] `backend/nixpacks.toml` - Build configuration
- [x] `backend/.env.example` - Environment template
- [x] `frontend/netlify.toml` - Netlify configuration
- [x] `frontend/vercel.json` - Vercel alternative

### ✅ Code Verification
- [x] No .env files in repository
- [x] No *.db files in repository
- [x] No venv/ or node_modules/ in repository
- [x] ML models present in backend/ml_models/
- [x] requirements.txt is complete
- [x] package.json is complete

---

## 🚀 STEP 1: Push to GitHub

```bash
# Navigate to project root
cd fraud-guard

# Initialize Git (if not already done)
git init

# Add all files
git add .

# Commit
git commit -m "Initial commit: FraudGuard AI Platform"

# Add remote (replace with your repo URL)
git remote add origin https://github.com/YOUR_USERNAME/fraudguard-ai.git

# Push to main branch
git branch -M main
git push -u origin main
```

---

## 🔧 STEP 2: Deploy Backend to Railway

### 2.1 Create Railway Project

1. Go to https://railway.app
2. Sign in with GitHub
3. Click **"New Project"**
4. Select **"Deploy from GitHub repo"**
5. Choose your `fraudguard-ai` repository
6. Click **"Deploy Now"**

### 2.2 Configure Service Settings

**⚠️ CRITICAL STEP - This fixes the "Railpack could not determine how to build" error**

1. After deployment starts, click on your service name
2. Go to **"Settings"** tab
3. Scroll to **"Service"** section
4. Find **"Root Directory"** field
5. Enter: `backend`
6. Click **"Update"** or press Enter
7. Railway will automatically redeploy

### 2.3 Add Environment Variables

Go to **"Variables"** tab and add:

```bash
# Database (SQLite for development, PostgreSQL for production)
DATABASE_URL=sqlite:///./fraudguard.db

# Security (GENERATE A RANDOM 32+ CHARACTER STRING)
SECRET_KEY=your-super-secret-key-min-32-characters-change-this

# ML Models
MODEL_PATH=ml_models

# File Upload Limit (100MB)
MAX_FILE_SIZE=104857600

# Logging
LOG_LEVEL=INFO
```

**Generate SECRET_KEY:**
```bash
# Python method
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Or use online generator
# https://randomkeygen.com/
```

### 2.4 Optional: Add PostgreSQL Database

For production, use PostgreSQL instead of SQLite:

1. In Railway dashboard, click **"New"** → **"Database"** → **"Add PostgreSQL"**
2. Railway will create a PostgreSQL instance
3. Copy the `DATABASE_URL` from PostgreSQL service
4. Update your backend's `DATABASE_URL` variable
5. Redeploy backend

### 2.5 Verify Backend Deployment

1. Wait for deployment to complete (green checkmark)
2. Click on your service to see the generated URL
3. Copy the URL (e.g., `https://fraudguard-backend-production.up.railway.app`)

**Test Endpoints:**
```bash
# Health check
curl https://your-backend-url.railway.app/api/v1/health

# Model status
curl https://your-backend-url.railway.app/api/v1/health/models

# API docs
# Open in browser: https://your-backend-url.railway.app/docs
```

**Expected Response:**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "timestamp": "2024-..."
}
```

### 2.6 Check Logs

1. Go to **"Deployments"** tab
2. Click on latest deployment
3. View logs for any errors
4. Look for: `"Application startup complete"`

---

## 🌐 STEP 3: Deploy Frontend to Netlify

### 3.1 Create Netlify Site

1. Go to https://app.netlify.com
2. Sign in with GitHub
3. Click **"Add new site"** → **"Import an existing project"**
4. Choose **"Deploy with GitHub"**
5. Select your `fraudguard-ai` repository
6. Click **"Deploy"**

### 3.2 Configure Build Settings

**Site settings:**
- **Base directory**: `frontend`
- **Build command**: `npm run build`
- **Publish directory**: `frontend/dist`
- **Node version**: 18

### 3.3 Add Environment Variables

Go to **"Site settings"** → **"Environment variables"** → **"Add a variable"**

```bash
# Backend API URL (use your Railway URL from Step 2.5)
VITE_API_URL=https://your-backend-url.railway.app
```

**⚠️ Important**: Remove trailing slash from URL

### 3.4 Deploy

1. Click **"Deploy site"**
2. Wait for build to complete
3. Netlify will generate a URL (e.g., `https://fraudguard-ai.netlify.app`)

### 3.5 Verify Frontend Deployment

1. Open your Netlify URL in browser
2. Check browser console (F12) for errors
3. Test all pages:
   - Homepage
   - Static detection page
   - Live detection page
4. Test API calls (upload an image)

---

## 🔍 STEP 4: Verify Integration

### 4.1 Test Backend Endpoints

```bash
# Replace with your Railway URL
BACKEND_URL="https://your-backend-url.railway.app"

# Health check
curl $BACKEND_URL/api/v1/health

# Models loaded
curl $BACKEND_URL/api/v1/health/models

# Debug info
curl $BACKEND_URL/api/v1/debug
```

### 4.2 Test Frontend → Backend Communication

1. Open frontend in browser
2. Open browser console (F12) → Network tab
3. Upload a test image in Static Detection
4. Check Network tab for API call
5. Should see: `POST /api/v1/analyze/image` with 200 status

### 4.3 Test All Detection Modules

- [ ] Deepfake Detection (image upload)
- [ ] Deepfake Detection (video upload)
- [ ] Document Verification (PDF upload)
- [ ] Voice Analysis (audio upload)
- [ ] Email Fraud Detection (text input)
- [ ] Live Webcam (if camera available)
- [ ] Live Voice (if microphone available)

---

## 🐛 Troubleshooting

### Backend Issues

#### "Railpack could not determine how to build"
**Cause**: Root directory not set
**Fix**: Settings → Service → Root Directory = `backend`

#### "Module not found" errors
**Cause**: Dependencies not installed
**Fix**: 
1. Check `requirements.txt` is in backend directory
2. Check Railway logs for pip install errors
3. Redeploy

#### "Port already in use"
**Cause**: Not using $PORT variable
**Fix**: Already handled in Procfile and nixpacks.toml

#### Models not loading
**Cause**: ml_models directory missing
**Fix**: 
1. Ensure `backend/ml_models/*.pt` files exist
2. Check they're not in .gitignore
3. Verify file sizes (should be committed to Git)

#### Database errors
**Cause**: DATABASE_URL not set or invalid
**Fix**: 
1. Check environment variable is set
2. For SQLite: `sqlite:///./fraudguard.db`
3. For PostgreSQL: Use Railway-provided URL

#### Application won't start
**Cause**: Various
**Fix**:
1. Check Railway logs for specific error
2. Verify all environment variables set
3. Check Python version (should be 3.11)
4. Verify uvicorn is in requirements.txt

### Frontend Issues

#### "API calls fail" / CORS errors
**Cause**: Backend CORS not configured or wrong URL
**Fix**:
1. Backend already has CORS configured for all origins
2. Check `VITE_API_URL` is correct (no trailing slash)
3. Check backend is running (test health endpoint)

#### "Build failed"
**Cause**: Various
**Fix**:
1. Check Netlify build logs
2. Verify Node version is 18
3. Check `package.json` has all dependencies
4. Try building locally: `npm run build`

#### "Blank page" after deployment
**Cause**: JavaScript errors
**Fix**:
1. Open browser console (F12)
2. Check for errors
3. Verify `VITE_API_URL` is set correctly
4. Check Network tab for failed requests

#### "Environment variable not found"
**Cause**: VITE_API_URL not set
**Fix**:
1. Go to Netlify → Site settings → Environment variables
2. Add `VITE_API_URL` with your Railway URL
3. Redeploy site

---

## 📊 Production Optimization

### Backend (Railway)

#### Use PostgreSQL for Production
```bash
# In Railway, add PostgreSQL service
# Update DATABASE_URL to PostgreSQL connection string
# Benefits: Better performance, data persistence, scalability
```

#### Enable Workers
Already configured in `nixpacks.toml`:
```toml
cmd = "uvicorn app.main:app --host 0.0.0.0 --port $PORT --workers 4"
```

#### Add Health Checks
Railway automatically monitors `/` endpoint. Your app has `/api/v1/health`.

#### Monitor Logs
- Railway Dashboard → Deployments → View Logs
- Look for errors, warnings, slow requests

### Frontend (Netlify)

#### Enable CDN
Automatically enabled by Netlify

#### Add Custom Domain
1. Netlify → Domain settings
2. Add custom domain
3. Configure DNS records
4. Enable HTTPS (automatic)

#### Enable Caching
Already configured in `netlify.toml`

---

## 🔒 Security Checklist

- [ ] SECRET_KEY is random and secure (32+ characters)
- [ ] .env files not committed to Git
- [ ] Database credentials secure (if using PostgreSQL)
- [ ] CORS configured correctly (backend allows frontend domain)
- [ ] HTTPS enabled (automatic on Railway/Netlify)
- [ ] File upload limits enforced (100MB)
- [ ] Input validation on all endpoints
- [ ] No sensitive data in logs

---

## ✅ Final Verification Checklist

### Before Deployment
- [ ] Code pushed to GitHub
- [ ] No .env files in repository
- [ ] No *.db files in repository
- [ ] ML models committed to Git
- [ ] requirements.txt complete
- [ ] package.json complete

### Backend Deployment (Railway)
- [ ] Service created
- [ ] Root directory set to `backend`
- [ ] All environment variables added
- [ ] Deployment successful (green checkmark)
- [ ] `/api/v1/health` returns 200 OK
- [ ] `/api/v1/health/models` shows all models loaded
- [ ] `/docs` shows API documentation
- [ ] No errors in logs

### Frontend Deployment (Netlify)
- [ ] Site created
- [ ] Base directory set to `frontend`
- [ ] Build command: `npm run build`
- [ ] Publish directory: `frontend/dist`
- [ ] VITE_API_URL environment variable set
- [ ] Deployment successful
- [ ] Site loads without errors
- [ ] No errors in browser console
- [ ] API calls work (check Network tab)

### Integration Testing
- [ ] All 4 static detection modules work
- [ ] Live webcam works (if camera available)
- [ ] Live voice works (if microphone available)
- [ ] File uploads work (images, videos, audio, PDFs)
- [ ] Email fraud detection works
- [ ] Response times < 5 seconds
- [ ] No CORS errors

---

## 📝 Quick Command Reference

### Backend (Railway)
```bash
# View logs
railway logs

# Redeploy
railway up

# Add environment variable
railway variables set KEY=value

# Check status
railway status
```

### Frontend (Netlify)
```bash
# Install Netlify CLI
npm install -g netlify-cli

# Login
netlify login

# Deploy
netlify deploy --prod

# View logs
netlify logs
```

---

## 🆘 Getting Help

### Railway Support
- Docs: https://docs.railway.app
- Discord: https://discord.gg/railway
- Status: https://status.railway.app

### Netlify Support
- Docs: https://docs.netlify.com
- Community: https://answers.netlify.com
- Status: https://www.netlifystatus.com

### Project Documentation
- README.md - Complete guide
- API Docs: `https://your-backend-url.railway.app/docs`

---

## 🎉 Success!

Your FraudGuard AI platform is now deployed and production-ready!

**Backend**: https://your-backend-url.railway.app
**Frontend**: https://your-frontend-url.netlify.app

**Next Steps:**
1. Set up monitoring and alerts
2. Configure custom domains
3. Add analytics
4. Set up CI/CD pipeline
5. Plan for scaling

---

**Built with ❤️ using FastAPI, React, and PyTorch**
