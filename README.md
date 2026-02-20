# 🛡️ FraudGuard AI - Multimodal Fraud Detection Platform

A production-ready AI platform for detecting fraud across multiple modalities: deepfake images/videos, voice spoofing, document tampering, and email impersonation (BEC).

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- FFmpeg (for voice analysis)

### Local Development

```bash
# Backend
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac
pip install torch==2.1.2 torchvision==0.16.2 torchaudio==2.1.2  # For local dev
pip install -r requirements.txt
python -m uvicorn app.main:app --reload

# Frontend (new terminal)
cd frontend
npm install
npm run dev
```

**Access**: http://localhost:5173

## 📋 Features

### Detection Modes

**Static Analysis**
- 🎭 Deepfake Detection - Images & videos
- 📄 Document Verification - PDFs & images  
- 🎤 Voice Analysis - Audio files
- 📧 Email Fraud Detection - BEC & phishing

**Live Detection**
- 📹 Live Webcam - Real-time deepfake detection with anti-spoofing
- 🎙️ Live Voice - Real-time voice spoofing detection

### Key Capabilities
- ✅ Multi-modal fraud detection
- ✅ Real-time analysis
- ✅ Anti-spoofing for screen replay attacks (live webcam only)
- ✅ Business Email Compromise (BEC) detection
- ✅ PDF document support
- ✅ Large audio file optimization
- ✅ SQLite database (zero configuration)
- ✅ Production-ready API

## 🏗️ Architecture

### Tech Stack
- **Backend**: FastAPI + PyTorch + SQLAlchemy
- **Frontend**: React + TypeScript + Vite + TailwindCSS
- **Database**: SQLite (local) or PostgreSQL (production)
- **ML Models**: EfficientNet-B3, Wav2Vec2, FinBERT

### Project Structure
```
fraud-guard/
├── backend/
│   ├── app/
│   │   ├── api/endpoints.py          # API routes
│   │   ├── core/                     # Config & logging
│   │   ├── db/session.py             # Database
│   │   ├── models/                   # ML architectures & schemas
│   │   └── services/                 # Detection services
│   ├── ml_models/                    # Pre-trained models
│   ├── Dockerfile                    # Optimized multi-stage build
│   ├── .dockerignore                 # Excludes models from image
│   └── requirements.txt              # Python dependencies
├── frontend/
│   ├── src/
│   │   ├── components/               # React components
│   │   ├── pages/                    # Page components
│   │   ├── services/api.ts           # API client
│   │   └── types/                    # TypeScript types
│   ├── netlify.toml                  # Netlify config
│   └── package.json                  # Node dependencies
└── README.md
```

## 🐳 Docker Image Optimization

The Docker image is optimized for Railway deployment:

- **Multi-stage build**: Separates build and runtime
- **CPU-only PyTorch**: Reduces size by 2.7 GB
- **Models excluded**: Loaded at runtime (saves 420 MB)
- **Optimized dependencies**: opencv-headless, no test deps
- **Final size**: ~2.4 GB (down from 6.8 GB)

### Dockerfile Features
- Python 3.11 slim base
- FFmpeg and Poppler for media processing
- Non-root user for security
- 4 Uvicorn workers for production
- Health checks enabled

## 🚀 Deployment

### Backend (Railway)

**1. Create Railway Project**
- Go to https://railway.app
- New Project → Deploy from GitHub repo
- Select your repository
- **IMPORTANT**: Settings → Service → Root Directory = `backend`

**2. Environment Variables**
```bash
DATABASE_URL=sqlite:///./fraudguard.db
SECRET_KEY=<generate-random-32-chars>
MODEL_PATH=ml_models
MAX_FILE_SIZE=104857600
LOG_LEVEL=INFO
```

Generate SECRET_KEY:
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

**3. Model Loading Options**

**Option A: Railway Volume (Recommended)**
- Add volume in Railway dashboard
- Mount at `/app/ml_models`
- Upload your .pt files once
- Fast startup, no downloads

**Option B: Cloud Storage**
- Upload models to S3/GCS/Cloudflare R2
- Set environment variables with URLs
- Models download on first startup

**4. Deploy**
- Railway auto-deploys from GitHub
- Build time: 8-12 minutes
- Image size: ~2.4 GB
- Test: `https://your-app.railway.app/api/v1/health`

### Frontend (Netlify)

**1. Create Netlify Site**
- Go to https://app.netlify.com
- New site from Git → Select repository
- Base directory: `frontend`
- Build command: `npm run build`
- Publish directory: `frontend/dist`

**2. Environment Variables**
```bash
VITE_API_URL=https://your-backend.railway.app
```

**3. Deploy**
- Netlify auto-deploys from GitHub
- Build time: 2-3 minutes
- Test: Open your Netlify URL

## 🔧 Technical Details

### ML Models

**Deepfake Detection**
- Architecture: EfficientNet-B3
- Input: 224x224 RGB images
- Anti-spoofing: Screen pattern, glare, flatness detection
- Live mode: Detects phone screen replay attacks
- Static mode: Model-only inference

**Voice Spoofing Detection**
- Architecture: Wav2Vec2-based
- Input: 16kHz mono audio, up to 30 seconds
- Auto-optimization: Mono conversion, resampling, silence trimming
- Supports: WAV, MP3, WEBM, large files (up to 100MB)

**Document Tampering**
- Architecture: EfficientNet-B3
- Input: 224x224 RGB images
- PDF Support: Multi-page analysis (first 3 pages)
- Returns highest risk score across pages

**Email Fraud Detection (BEC)**
- Model: FinBERT (financial sentiment)
- Hybrid: 70% rules + 30% model
- Detects: Payment requests, authority impersonation, urgency
- Hard gating: Auto-flags high-risk BEC patterns

### Risk Thresholds
- **Low Risk**: < 30%
- **Medium Risk**: 30-70%
- **High Risk**: > 70%

## 💾 Database

### SQLite (Default)
- Zero configuration
- Auto-created on first run
- Located at `backend/fraudguard.db`
- Perfect for development

### PostgreSQL (Production)
```bash
# Add PostgreSQL service in Railway
# Update DATABASE_URL environment variable
# Tables created automatically
```

## 📊 API Endpoints

### Analysis Endpoints
```
POST /api/v1/analyze/image       # Deepfake detection
POST /api/v1/analyze/video       # Video analysis
POST /api/v1/analyze/audio       # Voice spoofing
POST /api/v1/analyze/document    # Document tampering
POST /api/v1/analyze/email       # Email fraud
```

### Utility Endpoints
```
GET  /api/v1/health              # Health check
GET  /api/v1/health/models       # Model status
GET  /api/v1/debug               # Debug info
GET  /docs                       # API documentation
```

## 🧪 Testing

### Quick Test
```bash
# Health check
curl https://your-backend-url.railway.app/api/v1/health

# Model status
curl https://your-backend-url.railway.app/api/v1/health/models
```

### Test Each Module
1. **Deepfake Detection**: Upload image/video
2. **Document Verification**: Upload PDF or image
3. **Voice Analysis**: Upload audio file
4. **Email Fraud**: Paste email with fraud keywords

## 🐛 Troubleshooting

### Voice Returns Mock Predictions
**Solution**: Install FFmpeg
```bash
# Windows: Download from https://ffmpeg.org/download.html
# Add to PATH, restart terminal
ffmpeg -version
```

### Webcam Black Screen
**Solutions**:
1. Grant camera permissions in browser
2. Close other apps using camera
3. Try Chrome/Edge browser

### PDF Upload Error
**Solution**: Install Poppler
```bash
# Windows: Download from https://github.com/oschwartz10612/poppler-windows/releases
# Extract and add bin/ to PATH
```

### Railway Build Fails
**Check**:
1. Root directory set to `backend`
2. All environment variables added
3. Railway logs for specific errors

## 🔒 Security

- ✅ File type & size validation
- ✅ Input sanitization
- ✅ CORS configuration
- ✅ Environment variables for secrets
- ✅ Inference-only models (no training)
- ✅ Database logging
- ✅ Non-root Docker user

## 📦 Dependencies

### Backend Key Packages
```
fastapi==0.109.0
uvicorn==0.27.0
torch==2.1.2+cpu (CPU-only for production)
transformers==4.36.2
librosa==0.10.1
opencv-python-headless==4.9.0.80
pdf2image==1.17.0
```

### Frontend Key Packages
```
react==18.2.0
typescript==5.2.2
vite==5.0.8
tailwindcss==3.4.1
axios
lucide-react
```

## 🎯 Key Features

### Anti-Spoofing (Live Webcam Only)
- Screen pattern detection (moire patterns)
- Display glare analysis
- Flatness detection (2D vs 3D)
- Hard gating at 92% risk when screen detected
- Static uploads skip anti-spoofing for faster processing

### BEC Detection (Email)
- Payment action detection (18 keywords)
- Authority impersonation (12 terms)
- Pressure indicators (12 urgency terms)
- Executive signature detection
- Hard gating at 88% risk for BEC patterns

### Audio Optimization
- Auto-converts to mono
- Resamples to 16kHz
- Trims silence
- Limits to 30 seconds
- Handles files up to 100MB

### PDF Support
- Multi-page analysis (first 3 pages)
- Returns highest risk score
- Requires Poppler for conversion

## ✅ Deployment Checklist

### Before Deployment
- [ ] Code pushed to GitHub
- [ ] No .env files in repository
- [ ] No *.db files in repository
- [ ] ML models present (for local dev) or configured for download
- [ ] Dockerfile optimized
- [ ] .dockerignore configured

### Backend (Railway)
- [ ] Service created from GitHub
- [ ] Root directory set to `backend`
- [ ] All environment variables added
- [ ] Deployment successful
- [ ] `/api/v1/health` returns 200 OK
- [ ] `/api/v1/health/models` shows models loaded
- [ ] No errors in logs

### Frontend (Netlify)
- [ ] Site created from GitHub
- [ ] Base directory: `frontend`
- [ ] VITE_API_URL environment variable set
- [ ] Deployment successful
- [ ] Site loads without errors
- [ ] API calls work

### Integration Testing
- [ ] All detection modules work
- [ ] File uploads work
- [ ] No CORS errors
- [ ] Response times < 5 seconds

## 📝 Environment Variables

### Backend (.env)
```bash
# Database
DATABASE_URL=sqlite:///./fraudguard.db

# Security
SECRET_KEY=your-secret-key-change-in-production-min-32-characters

# ML Models
MODEL_PATH=./ml_models
MAX_FILE_SIZE=104857600

# Logging
LOG_LEVEL=INFO
```

### Frontend (.env)
```bash
VITE_API_URL=http://localhost:8000
```

## 🤝 Contributing

Contributions welcome! Areas for improvement:
- Additional fraud detection modalities
- Model fine-tuning on domain-specific data
- Performance optimizations
- UI/UX enhancements

## 📄 License

Proprietary - All rights reserved

## 🆘 Support

**Common Issues**:
1. Voice mock predictions → Install FFmpeg
2. Webcam black screen → Grant camera permissions
3. PDF errors → Install Poppler
4. Railway build fails → Check root directory setting

**Debug Steps**:
1. Check `/api/v1/health/models` - all models loaded?
2. Check backend logs for errors
3. Check browser console (F12) for frontend errors
4. Verify environment variables set correctly

## 🎉 Success Criteria

Your deployment is successful when:
- [ ] Backend health check returns 200 OK
- [ ] All models show "loaded: true"
- [ ] Frontend loads without errors
- [ ] All detection modules work
- [ ] No errors in logs
- [ ] Response times < 5 seconds

---

**Built with ❤️ using FastAPI, React, and PyTorch**

**Repository**: https://github.com/Rahul-Sanskar/FraudGuard-AI
