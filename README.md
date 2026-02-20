# 🛡️ FraudGuard AI - Multimodal Fraud Detection Platform

A production-ready AI platform for detecting fraud across multiple modalities: deepfake images/videos, voice spoofing, document tampering, and email impersonation (BEC).

## 🚀 Quick Start (< 5 Minutes)

### Prerequisites
- Python 3.9+
- Node.js 16+
- FFmpeg (for voice analysis)

### Installation

```bash
# 1. Clone repository
git clone <your-repo-url>
cd fraud-guard

# 2. Backend setup
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac
pip install -r requirements.txt

# 3. Frontend setup
cd ../frontend
npm install

# 4. Start backend (new terminal)
cd backend
venv\Scripts\activate
python -m uvicorn app.main:app --reload

# 5. Start frontend (new terminal)
cd frontend
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
│   ├── requirements.txt
│   └── .env
├── frontend/
│   ├── src/
│   │   ├── components/               # React components
│   │   ├── pages/                    # Page components
│   │   ├── services/api.ts           # API client
│   │   └── types/                    # TypeScript types
│   ├── package.json
│   └── .env
└── README.md
```

## 🔧 Technical Details

### ML Models

**Deepfake Detection**
- Architecture: EfficientNet-B3
- Input: 224x224 RGB images
- Preprocessing: ImageNet normalization
- Anti-spoofing: Screen pattern detection, glare analysis, flatness detection
- Live mode: Detects phone screen replay attacks
- Static mode: Model-only inference (no anti-spoofing)

**Voice Spoofing Detection**
- Architecture: Wav2Vec2-based
- Input: 16kHz mono audio, up to 30 seconds
- Auto-optimization: Converts to mono, resamples, trims silence
- Supports: WAV, MP3, WEBM, large files (up to 100MB)

**Document Tampering**
- Architecture: EfficientNet-B3
- Input: 224x224 RGB images
- PDF Support: Multi-page analysis (first 3 pages)
- Returns highest risk score across pages

**Email Fraud Detection (BEC)**
- Model: FinBERT (financial sentiment)
- Hybrid: 70% rules + 30% model
- Detects: Payment requests, authority impersonation, urgency tactics
- Hard gating: Auto-flags high-risk BEC patterns

### Risk Thresholds
- **Low Risk**: < 30%
- **Medium Risk**: 30-70%
- **High Risk**: > 70%

### File Limits
- Images: 100MB
- Videos: 500MB
- Audio: 100MB (auto-optimized)
- Documents: 100MB

## 💾 Database

### SQLite (Default)
- ✅ Zero configuration
- ✅ Auto-created on first run
- ✅ Located at `backend/fraudguard.db`
- ✅ Perfect for development

### PostgreSQL (Production)
```bash
# Install driver
pip install psycopg2-binary

# Update .env
DATABASE_URL=postgresql://user:password@host:5432/fraudguard
```

Tables are created automatically on startup.

## 🧪 Testing

### Quick Test
```bash
# Health check
curl http://localhost:8000/api/v1/health

# Model status
curl http://localhost:8000/api/v1/health/models
```

### Test Each Module

**1. Deepfake Detection**
- Upload image/video at http://localhost:5173/static
- Try live webcam at http://localhost:5173/live
- Live mode detects screen replay attacks

**2. Document Verification**
- Upload PDF or image
- Multi-page PDFs analyzed automatically

**3. Voice Analysis**
- Upload audio file (any format)
- Large files auto-optimized

**4. Email Fraud**
- Paste email with keywords:
  - Payment: "wire transfer", "payment", "bank account"
  - Authority: "CEO", "CFO", "urgent"
  - Pressure: "immediately", "confidential"

## 🐛 Troubleshooting

### Voice Returns Mock Predictions

**Solution**: Install FFmpeg
```bash
# Windows: Download from https://ffmpeg.org/download.html
# Add to PATH, restart terminal

# Verify
ffmpeg -version
```

### Webcam Black Screen

**Solutions**:
1. Grant camera permissions in browser
2. Close other apps using camera (Zoom, Teams)
3. Try Chrome/Edge browser
4. Check Windows privacy settings

### PDF Upload Error

**Solution**: Install Poppler
```bash
# Windows: Download from https://github.com/oschwartz10612/poppler-windows/releases
# Extract and add bin/ to PATH
```

### Database Errors

**Solution**: Delete and recreate
```bash
cd backend
del fraudguard.db
python -m uvicorn app.main:app --reload
# Database recreated automatically
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

## 🚀 Deployment

### Backend (Railway)

1. **Create Railway Project**
   - Connect GitHub repository
   - Select `backend` as root directory

2. **Environment Variables**
   ```
   DATABASE_URL=sqlite:///./fraudguard.db
   SECRET_KEY=your-secret-key-min-32-chars
   MODEL_PATH=ml_models
   MAX_FILE_SIZE=104857600
   LOG_LEVEL=INFO
   ```

3. **Build Settings**
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

4. **Optional: Add PostgreSQL**
   - Add PostgreSQL service in Railway
   - Update `DATABASE_URL` to PostgreSQL connection string

### Frontend (Netlify)

1. **Create Netlify Site**
   - Connect GitHub repository
   - Base directory: `frontend`
   - Build command: `npm run build`
   - Publish directory: `dist`

2. **Environment Variables**
   ```
   VITE_API_URL=https://your-backend.railway.app
   ```

3. **Deploy**
   - Push to GitHub
   - Netlify auto-deploys

### Alternative: Vercel (Frontend)

```bash
cd frontend
npm install -g vercel
vercel --prod
```

Set environment variable:
```
VITE_API_URL=https://your-backend.railway.app
```

## 🔒 Security

- ✅ File type & size validation
- ✅ Input sanitization
- ✅ CORS configuration
- ✅ Environment variables for secrets
- ✅ Inference-only models (no training)
- ✅ Database logging
- ✅ Rate limiting ready

## 📦 Dependencies

### Backend Key Packages
```
fastapi==0.109.0
uvicorn==0.27.0
torch==2.1.2
torchvision==0.16.2
transformers==4.36.2
librosa==0.10.1
audioread==3.0.1
opencv-python==4.9.0.80
sqlalchemy==2.0.25
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
- Combo bonuses for multiple indicators
- Hard gating at 88% risk for BEC patterns

### Audio Optimization
- Auto-converts to mono
- Resamples to 16kHz
- Trims silence
- Limits to 30 seconds (keeps center)
- Normalizes amplitude
- Handles files up to 100MB

### PDF Support
- Multi-page analysis (first 3 pages)
- Returns highest risk score
- Fraud often hidden on later pages
- Requires Poppler for conversion

## 🔄 Recent Updates

### v1.0.0 (Latest)
- ✅ Anti-spoofing for live webcam only
- ✅ Enhanced BEC detection with hard gating
- ✅ Large audio file support with optimization
- ✅ PDF document analysis
- ✅ SQLite database (zero config)
- ✅ Production-ready deployment guides
- ✅ Comprehensive error handling

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
- Additional language support

## 📄 License

Proprietary - All rights reserved

## 🆘 Support

**Common Issues**:
1. Voice mock predictions → Install FFmpeg
2. Webcam black screen → Grant camera permissions
3. PDF errors → Install Poppler
4. Database errors → Delete and restart

**Debug Steps**:
1. Check `/api/v1/health/models` - all models loaded?
2. Check backend logs for errors
3. Check browser console (F12) for frontend errors
4. Verify environment variables set correctly

## ✅ Success Checklist

Your installation is successful when:
- [ ] Backend starts without errors
- [ ] Frontend loads at http://localhost:5173
- [ ] `/api/v1/health/models` shows all models loaded
- [ ] Voice analysis returns real predictions (not 20%)
- [ ] Webcam displays video feed
- [ ] All 4 static detection modules work
- [ ] Live detection modes work
- [ ] No errors in logs

**Ready to detect fraud!** 🚀

---

**Built with ❤️ using FastAPI, React, and PyTorch**
