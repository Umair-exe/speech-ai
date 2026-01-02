#!/bin/bash

# AI Detector - Docker Quick Start Script

echo "🚀 Starting AI Detector with Docker..."
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

echo "✅ Docker and Docker Compose are installed"
echo ""

# Stop any existing containers
echo "🛑 Stopping existing containers..."
docker-compose down

echo ""
echo "🔨 Building and starting containers..."
docker-compose up --build -d

echo ""
echo "⏳ Waiting for services to start..."
sleep 10

# Check if containers are running
if docker-compose ps | grep -q "Up"; then
    echo ""
    echo "✅ Services are running!"
    echo ""
    echo "📱 Application URLs:"
    echo "   Frontend:     http://localhost:3000"
    echo "   Backend API:  http://localhost:8000"
    echo "   API Docs:     http://localhost:8000/docs"
    echo ""
    echo "🔧 Useful commands:"
    echo "   View logs:       docker-compose logs -f"
    echo "   Stop services:   docker-compose down"
    echo "   Restart:         docker-compose restart"
    echo ""
    echo "✨ Features available:"
    echo "   • AI Detection:     http://localhost:3000"
    echo "   • Image Compression: http://localhost:3000/compress"
    echo "   • History:          http://localhost:3000/history"
    echo ""
else
    echo ""
    echo "❌ Failed to start services. Check logs with:"
    echo "   docker-compose logs"
    exit 1
fi
