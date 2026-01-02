# AI Media Detector - Backend

FastAPI backend for AI-generated media detection.

## Setup

### 1. Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment

```bash
cp .env.example .env
# Edit .env with your configuration
```

### 4. Start MongoDB

```bash
# Using Docker
docker run -d -p 27017:27017 --name mongodb mongo:latest

# Or install MongoDB locally
```

### 5. Run the Server

```bash
# Development
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Production
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

## API Documentation

Once running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Project Structure

```
backend/
├── app/
│   ├── db/              # Database models and connection
│   ├── models/          # AI/ML detection models
│   ├── routes/          # API endpoints
│   ├── services/        # Business logic
│   └── config.py        # Configuration
├── main.py              # FastAPI application entry
└── requirements.txt     # Python dependencies
```

## Key Features

- **Image Detection**: Uses EfficientNet/XceptionNet for deepfake detection
- **Video Detection**: Frame-by-frame analysis with temporal consistency checks
- **Artifact Analysis**: Detects visual anomalies in AI-generated content
- **Cloud Storage**: AWS S3 integration with local fallback
- **MongoDB**: Async database with Beanie ODM

## Model Information

The detection models analyze:
- Facial landmarks consistency
- Texture patterns and noise
- Color distribution anomalies
- Edge consistency
- Temporal patterns (videos)

## API Endpoints

### Detection
- `POST /api/detect` - Analyze single file
- `POST /api/detect/batch` - Analyze multiple files
- `GET /api/analysis/{id}` - Get analysis details
- `GET /api/history` - Get analysis history
- `GET /api/stats` - Get detection statistics

### Health
- `GET /api/health` - Health check
- `GET /` - API information

## Environment Variables

See `.env.example` for all configuration options.

## Testing

```bash
# Run tests
pytest

# With coverage
pytest --cov=app tests/
```

## Docker

```bash
# Build image
docker build -t ai-detector-backend .

# Run container
docker run -p 8000:8000 --env-file .env ai-detector-backend
```
