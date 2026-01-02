#!/bin/bash

echo "🚀 Setting up AI Detector - Frontend"
echo "===================================="

# Check Node.js
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js 18+ first."
    exit 1
fi

echo "✅ Node.js version: $(node --version)"

# Install dependencies
echo ""
echo "📦 Installing dependencies..."
cd frontend
npm install

# Copy environment file
if [ ! -f .env.local ]; then
    echo ""
    echo "📝 Creating environment file..."
    cp .env.example .env.local
    echo "✅ Created .env.local - please update with your settings"
fi

echo ""
echo "✅ Frontend setup complete!"
echo ""
echo "To start the development server:"
echo "  cd frontend"
echo "  npm run dev"
echo ""
