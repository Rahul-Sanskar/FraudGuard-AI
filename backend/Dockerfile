FROM python:3.11-slim

WORKDIR /app

# Install system dependencies (including FFmpeg for audio processing)
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    ffmpeg \
    poppler-utils \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create ml_models directory if it doesn't exist
RUN mkdir -p ml_models

# Expose port (Railway will set PORT env variable)
EXPOSE 8000

# Run the application (use $PORT from Railway)
CMD uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}
