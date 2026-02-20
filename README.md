# FraudGuard AI

Enterprise-grade fraud detection platform powered by advanced AI. Detect deepfakes, voice spoofing, and document tampering with a professional, modern interface.

## Features

- **Deepfake Detection**: Analyze images and videos for manipulation using neural networks
- **Voice Spoof Detection**: Identify synthetic and cloned voice recordings
- **Document Verification**: Verify document authenticity and detect tampering
- **Email Fraud Detection**: Detect C-suite impersonation and Business Email Compromise (BEC) using FinBERT
- **Webcam Capture**: Real-time image capture for instant analysis
- **Audio Recording**: Record and analyze voice in real-time
- **Dark Mode**: Full dark mode support across the entire application
- **Responsive Design**: Works seamlessly on desktop, tablet, and mobile devices

## Tech Stack

### Backend
- **Framework**: FastAPI (Python)
- **ML Libraries**: PyTorch, OpenCV, Librosa
- **Database**: SQLite
- **API**: RESTful API with automatic documentation

### Frontend
- **Framework**: React 18 with TypeScript
- **Build Tool**: Vite
- **Styling**: Tailwind CSS
- **Icons**: Lucide React
- **Routing**: React Router DOM

## Project Structure

```
fraud-guard/
├── backend/
│   ├── app/
│   │   ├── api/              # API endpoints
│   │   ├── core/             # Core configuration
│   │   ├── db/               # Database setup
│   │   ├── models/           # Data models
│   │   └── services/         # Business logic
│   ├── ml_models/            # Trained ML models
│   ├── tests/                # Backend tests
│   ├── requirements.txt      # Python dependencies
│   └── Dockerfile            # Backend container
├── frontend/
│   ├── src/
│   │   ├── components/       # React components
│   │   ├── pages/            # Page components
│   │   ├── services/         # API services
│   │   └── types/            # TypeScript types
│   ├── package.json          # Node dependencies
│   └── vite.config.ts        # Vite configuration
└── README.md                 # This file
```

## Quick Start

### Prerequisites
- Python 3.9+
- Node.js 18+
- npm or yarn

### Backend Setup

```bash
# Navigate to backend directory
cd fraud-guard/backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env

# Run the server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The backend API will be available at `http://localhost:8000`
API documentation: `http://localhost:8000/docs`

### Frontend Setup

```bash
# Navigate to frontend directory
cd fraud-guard/frontend

# Install dependencies
npm install

# Create .env file
cp .env.example .env

# Start development server
npm run dev
```

The frontend will be available at `http://localhost:3000`

## Environment Variables

### Backend (.env)
```env
DATABASE_URL=sqlite:///./fraudguard.db
MODEL_PATH=./ml_models
CORS_ORIGINS=http://localhost:3000
```

### Frontend (.env)
```env
VITE_API_URL=http://localhost:8000/api/v1
```

## API Endpoints

### Health Check
```
GET /api/v1/health
```

### Analysis Endpoints
```
POST /api/v1/analyze/image      # Deepfake detection (image)
POST /api/v1/analyze/video      # Deepfake detection (video)
POST /api/v1/analyze/audio      # Voice spoof detection
POST /api/v1/analyze/document   # Document verification
POST /api/v1/analyze/email      # Email fraud detection (C-suite impersonation & BEC)
```

### Response Format
```json
{
  "risk_score": 0.85,
  "prediction": "High",
  "confidence": 0.92,
  "explanation": "Analysis details..."
}
```

## Usage

### Deepfake Detection
1. Navigate to "Deepfake" page
2. Choose "Upload File" or "Use Webcam"
3. Select/capture an image or video
4. Click "Analyze for Deepfakes"
5. View results with risk score and confidence

### Voice Spoof Detection
1. Navigate to "Voice" page
2. Choose "Upload Audio" or "Record Audio"
3. Select/record an audio file
4. Click "Analyze Voice"
5. View results with risk assessment

### Document Verification
1. Navigate to "Document" page
2. Upload a document image or PDF
3. Click "Verify Document"
4. View authenticity results

### Email Fraud Detection
1. Navigate to "Email" page
2. Paste the email content into the text area
3. Click "Analyze Email"
4. View results showing:
   - C-suite impersonation detection
   - Business Email Compromise (BEC) indicators
   - Payment request analysis
   - Urgency and pressure tactics
   - Risk assessment with confidence score

## Development

### Backend Commands
```bash
# Run tests
pytest

# Run with auto-reload
uvicorn app.main:app --reload

# Check code style
black app/
flake8 app/
```

### Frontend Commands
```bash
# Development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Type checking
npm run type-check

# Linting
npm run lint
```

## Building for Production

### Backend
```bash
# Using Docker
docker build -t fraudguard-backend ./backend
docker run -p 8000:8000 fraudguard-backend

# Or manually
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### Frontend
```bash
# Build
npm run build

# Output will be in dist/ folder
# Deploy dist/ to any static hosting service
```

## Deployment

### Backend Deployment Options
- Docker container
- AWS EC2 / Azure VM
- Heroku
- Google Cloud Run

### Frontend Deployment Options
- Vercel (recommended)
- Netlify
- AWS S3 + CloudFront
- Any static hosting service

### Quick Deploy to Vercel
```bash
cd frontend
npm install -g vercel
vercel
```

## Browser Support

- Chrome/Edge (latest 2 versions)
- Firefox (latest 2 versions)
- Safari (latest 2 versions)
- Mobile browsers (iOS Safari, Chrome Mobile)

## Features in Detail

### Webcam Capture
- Live video preview
- Multiple camera support
- Device selection
- Permission handling
- Error recovery

### Audio Recording
- Real-time recording
- Pause/Resume functionality
- Recording timer
- Permission handling
- WebM format output

### Email Fraud Detection (FinBERT)
- **C-suite Impersonation Detection**: Identifies emails claiming to be from executives (CEO, CFO, etc.)
- **Business Email Compromise (BEC)**: Detects payment fraud and wire transfer scams
- **Hybrid Analysis**: Combines FinBERT NLP model (30%) with rule-based detection (70%)
- **Pattern Recognition**: Identifies urgency tactics, payment requests, and authority claims
- **Hard BEC Override**: Automatically flags high-risk patterns (payment + authority combination)
- **Confidence Scoring**: Provides detailed risk assessment with explanation

**What it detects:**
- Urgent payment requests
- Wire transfer scams
- Executive impersonation
- Pressure tactics
- Confidentiality requests
- Suspicious authority claims
- Banking detail changes

### Dark Mode
- System preference detection
- Manual toggle
- Persistent preference
- Smooth transitions

### Error Handling
- User-friendly error messages
- Network error recovery
- Permission denied handling
- Timeout management

## Security

- CORS configuration
- Input validation
- File type restrictions
- Size limits
- Error boundaries
- Secure API communication

## Performance

- Code splitting
- Lazy loading
- Optimized bundle size (~272 KB)
- Fast initial load
- Efficient re-renders

## Accessibility

- Keyboard navigation
- ARIA labels
- Focus indicators
- Screen reader support
- Color contrast compliance

## Troubleshooting

### Backend Issues

**Port already in use:**
```bash
# Change port in command
uvicorn app.main:app --port 8001
```

**Module not found:**
```bash
# Reinstall dependencies
pip install -r requirements.txt
```

**Database errors:**
```bash
# Delete and recreate database
rm fraudguard.db
# Restart server to recreate
```

### Frontend Issues

**Build fails:**
```bash
# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install
npm run build
```

**API connection fails:**
- Check `VITE_API_URL` in `.env`
- Ensure backend is running
- Check CORS configuration

**Dark mode not working:**
- Clear browser cache
- Check localStorage
- Verify ThemeProvider is wrapping App

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests and linting
5. Submit a pull request

## License

Proprietary - FraudGuard AI

## Support

For issues or questions:
1. Check this README
2. Review API documentation at `/docs`
3. Check browser console for errors
4. Verify environment variables
5. Contact the development team

## Acknowledgments

Built with modern web technologies and best practices for enterprise-grade fraud detection.
