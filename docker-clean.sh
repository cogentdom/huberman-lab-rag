#!/bin/bash

echo "🧹 Cleaning up Docker containers and networks..."

# Set project name
export COMPOSE_PROJECT_NAME=huberman-lab-rag

# Stop and remove containers
echo "Stopping containers..."
docker-compose down

# Remove orphaned networks
echo "Cleaning up networks..."
docker network prune -f

# Optional: Remove volumes (uncomment if you want to reset all data)
# echo "Cleaning up volumes..."
# docker-compose down -v

echo "✅ Cleanup complete!"
echo "💡 You can now run ./docker-start.sh to start fresh" 