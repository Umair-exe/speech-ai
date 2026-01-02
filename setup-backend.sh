#!/bin/bash

echo "🚀 Setting up AI Detector - Backend"
echo "==================================="

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.9+ first."
    exit 1
fi

echo "✅ Python version: $(python3 --version)"

# Create virtual environment
echo ""
echo "🐍 Creating virtual environment..."
cd backend
python3 -m venv venv

# Activate virtual environment
echo ""
echo "📦 Installing dependencies..."
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Copy environment file
if [ ! -f .env ]; then
    echo ""
    echo "📝 Creating environment file..."
    cp .env.example .env
    echo "✅ Created .env - please update with your settings"
fi

# Create directories
echo ""
echo "📁 Creating required directories..."
mkdir -p uploads temp models

echo ""
echo "✅ Backend setup complete!"
echo ""
echo "To start the development server:"
echo "  cd backend"
echo "  source venv/bin/activate"
echo "  uvicorn main:app --reload"
echo ""
echo "⚠️  Don't forget to:"
echo "  1. Start MongoDB (docker run -d -p 27017:27017 mongo)"
echo "  2. Update .env with your configuration"
echo ""
