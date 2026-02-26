#!/bin/bash

echo "🚀 Starting Huberman Lab RAG Application..."

# Run auto-restore check in background
echo "🔍 Running auto-restore check..."
python /app/auto-restore.py &
RESTORE_PID=$!

# Wait for auto-restore to complete (with timeout)
echo "⏳ Waiting for auto-restore to complete..."
timeout=300  # 5 minutes
counter=0

while kill -0 $RESTORE_PID 2>/dev/null; do
    if [ $counter -ge $timeout ]; then
        echo "⚠️ Auto-restore taking longer than expected, starting app anyway..."
        break
    fi
    sleep 2
    counter=$((counter + 2))
done

# Check if auto-restore completed successfully
if wait $RESTORE_PID; then
    echo "✅ Auto-restore completed successfully"
else
    echo "⚠️ Auto-restore completed with warnings, but continuing..."
fi

echo "🌐 Starting Flask application..."
exec python app/app.py 