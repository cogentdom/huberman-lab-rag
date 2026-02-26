#!/bin/bash

echo "🚀 Starting Huberman Lab RAG with Docker..."

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Error: Docker is not running. Please start Docker first."
    exit 1
fi

# Check if docker-compose is available
if ! command -v docker-compose > /dev/null 2>&1; then
    echo "❌ Error: docker-compose is not installed."
    exit 1
fi

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    cp env.template .env
    echo "⚠️  Please edit .env file and add your OPENAI_API_KEY before running docker-compose up"
    echo "   You can do this by running: nano .env"
    echo ""
    echo "   Then run: docker-compose up --build"
    exit 0
fi

# Check if OPENAI_API_KEY is set
if ! grep -q "OPENAI_API_KEY=sk-" .env 2>/dev/null; then
    echo "⚠️  Warning: OPENAI_API_KEY not found or not properly set in .env file"
    echo "   Please edit .env file and add your OpenAI API key"
    echo "   Example: OPENAI_API_KEY=sk-your-key-here"
fi

# Set project name to avoid directory name issues
export COMPOSE_PROJECT_NAME=huberman-lab-rag

# Clean up any existing containers and networks
echo "🧹 Cleaning up existing containers..."
docker-compose down 2>/dev/null || true

# Start the services
echo "🔧 Building and starting services..."
if docker-compose up --build; then
    echo "✅ Services started successfully!"
    echo "📱 Application: http://localhost:8000"
    echo "🔍 RedisInsight: http://localhost:8001"
else
    echo "❌ Failed to start services. Check the logs above for details."
    echo "💡 Try running: docker-compose down && docker-compose up --build"
    exit 1
fi 