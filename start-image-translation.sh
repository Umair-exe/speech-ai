#!/bin/bash

# Image Translation Feature - Quick Start Guide
echo "🚀 Starting AI Detector with Image Translation Feature..."
echo ""

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker Desktop and try again."
    exit 1
fi

echo "✅ Docker is running"
echo ""

# Stop any running containers
echo "🛑 Stopping existing containers..."
docker-compose down

# Build and start services
echo "🔨 Building and starting services..."
docker-compose up --build -d

# Wait for services to be ready
echo "⏳ Waiting for services to start..."
sleep 10

# Check if services are running
if docker-compose ps | grep -q "Up"; then
    echo "✅ Services are running!"
    echo ""
    echo "🌐 Access the application:"
    echo "   Frontend: http://localhost:3000"
    echo "   Backend API: http://localhost:8000"
    echo "   API Documentation: http://localhost:8000/docs"
    echo ""
    echo "📸 Image Translation Feature:"
    echo "   1. Go to http://localhost:3000/translate"
    echo "   2. Upload an image with text"
    echo "   3. Select source and target languages"
    echo "   4. Click 'Translate Image'"
    echo "   5. Download your translated image!"
    echo ""
    echo "📋 View logs:"
    echo "   docker-compose logs -f"
    echo ""
    echo "🛑 Stop services:"
    echo "   docker-compose down"
else
    echo "❌ Services failed to start. Check logs with: docker-compose logs"
    exit 1
fi
