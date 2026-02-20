#!/bin/bash
set -e

echo "=========================================="
echo "FraudGuard AI - Starting Application"
echo "=========================================="

# Check if models exist, download if needed
echo "Checking ML models..."
if [ ! -f "ml_models/deepfake_model_enhanced.pt" ] || \
   [ ! -f "ml_models/document_model.pt" ] || \
   [ ! -f "ml_models/voice_spoof_model.pt" ]; then
    echo "⚠️  Models not found, attempting download..."
    python download_models.py || echo "⚠️  Model download failed, continuing anyway..."
else
    echo "✅ All models present"
fi

# Start the application
echo "Starting uvicorn server..."
exec uvicorn app.main:app \
    --host 0.0.0.0 \
    --port ${PORT:-8000} \
    --workers ${WORKERS:-4} \
    --log-level info
