#!/bin/bash

echo "🚀 Starting AI Detector - Full Stack"
echo "====================================="

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check Docker
if ! command_exists docker; then
    echo "❌ Docker is not installed. Using manual startup..."
    
    # Start MongoDB manually if needed
    echo ""
    echo "Starting services manually..."
    
    # Start backend in background
    echo "🐍 Starting backend..."
    cd backend
    source venv/bin/activate 2>/dev/null || true
    uvicorn main:app --reload --host 0.0.0.0 --port 8000 &
    BACKEND_PID=$!
    cd ..
    
    # Start frontend
    echo "⚛️  Starting frontend..."
    cd frontend
    npm run dev &
    FRONTEND_PID=$!
    cd ..
    
    echo ""
    echo "✅ Services started!"
    echo "   Backend: http://localhost:8000"
    echo "   Frontend: http://localhost:3000"
    echo "   API Docs: http://localhost:8000/docs"
    echo ""
    echo "Press Ctrl+C to stop all services"
    
    # Wait for interrupt
    trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null" EXIT
    wait
else
    echo "🐳 Using Docker Compose..."
    docker-compose up
fi
