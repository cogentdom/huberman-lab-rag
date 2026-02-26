#!/bin/bash

echo "🔄 Initializing Redis data for Huberman Lab RAG..."

# Set project name
export COMPOSE_PROJECT_NAME=huberman-lab-rag

# Check if containers are running
if ! docker-compose ps | grep -q "Up"; then
    echo "❌ Containers are not running. Please start them first with: docker-compose up -d"
    exit 1
fi

# Check if .env file exists and has a valid OpenAI API key
if [ ! -f .env ]; then
    echo "❌ .env file not found. Please create it from env.template and add your OpenAI API key."
    exit 1
fi

if ! grep -q "OPENAI_API_KEY=sk-" .env; then
    echo "❌ Valid OpenAI API key not found in .env file."
    echo "   Please edit .env and set OPENAI_API_KEY=sk-your-actual-key"
    exit 1
fi

# Copy setup script into container and run it
echo "📊 Setting up Redis search index and loading embeddings..."
docker cp docker-setup_vector_db.py huberman-app:/app/

# Run the setup script inside the container
if docker exec huberman-app python docker-setup_vector_db.py; then
    echo "✅ Redis data initialization completed successfully!"
    echo "🔍 You can now query the application at http://localhost:8000"
else
    echo "❌ Failed to initialize Redis data. Check the logs above for details."
    exit 1
fi 