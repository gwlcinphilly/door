#!/bin/bash

# Door FastAPI Application Startup Script

echo "🚀 Starting Door FastAPI Application..."

# Check if virtual environment exists
if [ ! -d "env" ]; then
    echo "📦 Creating virtual environment..."
    python -m venv env
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source env/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "⚠️  Warning: .env file not found!"
    echo "Please create a .env file with your database configuration."
    echo "See README.md for details."
fi

# Start the application
echo "🌟 Starting FastAPI application..."
echo "📱 Web interface: http://127.0.0.1:8000"
echo "📚 API docs: http://127.0.0.1:8000/docs"
echo "🔄 Press Ctrl+C to stop the application"
echo ""

python main.py
