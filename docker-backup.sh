#!/bin/bash

echo "💾 Creating backup of Redis data..."

# Set project name
export COMPOSE_PROJECT_NAME=huberman-lab-rag

# Check if containers are running
if ! docker-compose ps | grep -q "Up"; then
    echo "❌ Containers are not running. Please start them first."
    exit 1
fi

# Create backup directory
backup_dir="backups/$(date +%Y%m%d_%H%M%S)"
mkdir -p "$backup_dir"

echo "📁 Backup directory: $backup_dir"

# Force Redis to save current state
echo "💾 Forcing Redis save..."
docker exec huberman-redis redis-cli BGSAVE

# Wait for background save to complete
echo "⏳ Waiting for background save to complete..."
while [ "$(docker exec huberman-redis redis-cli LASTSAVE)" = "$(docker exec huberman-redis redis-cli LASTSAVE)" ]; do
    sleep 1
done

echo "✅ Background save completed"

# Copy Redis dump file
echo "📋 Copying Redis dump file..."
docker cp huberman-redis:/data/dump.rdb "$backup_dir/redis_dump.rdb"

# Get Redis info
echo "📊 Saving Redis information..."
docker exec huberman-redis redis-cli INFO > "$backup_dir/redis_info.txt"
docker exec huberman-redis redis-cli FT._LIST > "$backup_dir/redis_indices.txt"
docker exec huberman-redis redis-cli DBSIZE > "$backup_dir/redis_dbsize.txt"

# Create backup metadata
echo "📝 Creating backup metadata..."
cat > "$backup_dir/backup_info.txt" << EOF
Backup created: $(date)
Redis version: $(docker exec huberman-redis redis-cli INFO server | grep redis_version)
Database size: $(docker exec huberman-redis redis-cli DBSIZE) keys
Search indices: $(docker exec huberman-redis redis-cli FT._LIST | tr '\n' ' ')
Container status: $(docker-compose ps --quiet | wc -l) containers
EOF

echo "✅ Backup completed successfully!"
echo "📂 Backup location: $backup_dir"
echo "📊 Backup size: $(du -sh "$backup_dir" | cut -f1)"

# List recent backups
echo ""
echo "📚 Recent backups:"
ls -la backups/ 2>/dev/null | tail -5 || echo "No previous backups found" 