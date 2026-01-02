FROM python:3.11-slim

WORKDIR /app

# Install system dependencies for audio processing and OCR
RUN apt-get update && apt-get install -y \
    ffmpeg \
    libsndfile1 \
    tesseract-ocr \
    tesseract-ocr-eng \
    tesseract-ocr-spa \
    tesseract-ocr-fra \
    tesseract-ocr-deu \
    tesseract-ocr-ita \
    tesseract-ocr-por \
    tesseract-ocr-rus \
    tesseract-ocr-jpn \
    tesseract-ocr-chi-sim \
    tesseract-ocr-chi-tra \
    tesseract-ocr-ara \
    tesseract-ocr-hin \
    tesseract-ocr-kor \
    tesseract-ocr-urd \
    tesseract-ocr-hun \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p temp audio_outputs uploads compressed translated_images

# Expose port
EXPOSE 8000

# Run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
