# Speech AI - Voice to Text & Text to Voice

A web application that converts speech to text and text to speech using advanced AI models.

## 🚀 Quick Start

```bash
# 1. Setup backend
cd backend
pip install -r requirements.txt

# 2. Start services with Docker
docker-compose up -d

# 3. Access the application
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

---

## Features

### 🎤 Voice to Text (Speech Recognition)
- **High Accuracy**: Powered by OpenAI Whisper for accurate transcription
- **Multi-Format Support**: MP3, WAV, M4A, WebM, OGG
- **Language Detection**: Automatic language detection
- **Timestamped Segments**: View transcription with timestamps
- **Copy & Export**: Easy copy and export of transcribed text

### 🔊 Text to Voice (Speech Synthesis)
- **Natural Voices**: High-quality speech synthesis using Google TTS
- **20+ Languages**: Support for English, Spanish, French, German, and more
- **Speed Control**: Choose normal or slow speech
- **Audio Download**: Download generated audio files (MP3)
- **Real-time Preview**: Play audio directly in the browser

### ⚡ Additional Features
- **User-Friendly Interface**: Clean, intuitive design
- **Fast Processing**: Quick transcription and synthesis
- **Cross-Platform**: Works on desktop and mobile
- **API Access**: RESTful API for integration

## Technology Stack

### Frontend
- **Next.js 14** - React framework with server-side rendering
- **TypeScript** - Type-safe development
- **Tailwind CSS** - Modern, responsive styling
- **Lucide Icons** - Beautiful icons

### Backend
- **FastAPI** - Modern Python web framework
- **OpenAI Whisper** - State-of-the-art speech recognition
- **gTTS** - Google Text-to-Speech
- **Pydub** - Audio processing
- **MongoDB** - Database for storing history

### Backend
- **FastAPI** - High-performance Python web framework
- **PyTorch** - Deep learning framework
- **OpenCV** - Video processing
- **MongoDB** - Database for user data and history
- **AWS S3** - Cloud storage for media files

### AI/ML Models
- **XceptionNet** - Image deepfake detection
- **EfficientNet** - Feature extraction
- **FaceForensics++** - Facial manipulation detection
- **Custom temporal models** - Video consistency analysis

## Project Structure

```
ai-detector/
├── frontend/               # Next.js application
│   ├── src/
│   │   ├── app/           # App router pages
│   │   ├── components/    # React components
│   │   ├── lib/           # Utilities and helpers
│   │   └── types/         # TypeScript types
│   ├── public/            # Static assets
│   └── package.json
├── backend/               # FastAPI application
│   ├── app/
│   │   ├── models/        # AI/ML models
│   │   ├── routes/        # API endpoints
│   │   ├── services/      # Business logic
│   │   ├── db/            # Database models
│   │   └── utils/         # Helper functions
│   ├── requirements.txt
│   └── main.py
└── README.md
```

## Setup Instructions

### Prerequisites
- Node.js 18+ and npm/yarn
- Python 3.9+
- MongoDB (local or Atlas)
- AWS account (for S3 storage)

### Frontend Setup

```bash
cd frontend
npm install
cp .env.example .env.local
# Configure your environment variables
npm run dev
```

The frontend will run on `http://localhost:3000`

### Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Configure your environment variables
uvicorn main:app --reload
```

The backend API will run on `http://localhost:8000`

## Environment Variables

### Frontend (.env.local)
```
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_MAX_FILE_SIZE=100
```

### Backend (.env)
```
MONGODB_URI=mongodb://localhost:27017/ai_detector
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_S3_BUCKET=your_bucket_name
JWT_SECRET=your_secret_key
MODEL_PATH=./models
```

## API Documentation

Once the backend is running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Usage

1. **Upload Media**: Drag and drop or click to upload images/videos
2. **Analysis**: Wait for AI model to process the media
3. **Results**: View confidence scores and detection details
4. **History**: Access your previous analyses from your profile

## Monetization

- **Free Tier**: 5 uploads per month
- **Premium**: Unlimited uploads, batch processing, API access
- **Enterprise**: Custom solutions with dedicated support

## Development

### Run Tests
```bash
# Frontend
cd frontend && npm test

# Backend
cd backend && pytest
```

### Build for Production
```bash
# Frontend
cd frontend && npm run build

# Backend
cd backend && docker build -t ai-detector-api .
```

## License

MIT

## Contributing

Contributions are welcome! Please read our contributing guidelines before submitting PRs.
