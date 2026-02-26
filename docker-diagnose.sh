#!/bin/bash

echo "🔍 Huberman Lab RAG - Diagnostic Check"
echo "======================================"

# Set project name
export COMPOSE_PROJECT_NAME=huberman-lab-rag

echo ""
echo "1. 🐳 Docker Services Status:"
echo "------------------------------"
docker-compose ps

echo ""
echo "2. 📁 Environment File:"
echo "----------------------"
if [ -f .env ]; then
    echo "✅ .env file exists"
    if grep -q "OPENAI_API_KEY=sk-" .env; then
        echo "✅ OpenAI API key appears to be set"
    else
        echo "❌ OpenAI API key not properly set in .env"
        echo "   Current value: $(grep OPENAI_API_KEY .env)"
    fi
else
    echo "❌ .env file not found"
fi

echo ""
echo "3. 📊 Data Files:"
echo "-----------------"
for file in "app/data/title_dict.pkl" "app/data/chunk_dict.pkl" "app/data/embeddings.csv"; do
    if [ -f "$file" ]; then
        size=$(du -h "$file" | cut -f1)
        echo "✅ $file ($size)"
    else
        echo "❌ $file missing"
    fi
done

echo ""
echo "4. 🔗 Redis Connection:"
echo "----------------------"
if docker exec huberman-redis redis-cli ping > /dev/null 2>&1; then
    echo "✅ Redis is responding"
    
    # Check database size
    db_size=$(docker exec huberman-redis redis-cli DBSIZE)
    echo "📊 Redis database contains $db_size keys"
    
    # Check if search index exists
    if docker exec huberman-redis redis-cli FT._LIST | grep -q "embeddings-index"; then
        echo "✅ Search index 'embeddings-index' exists"
    else
        echo "❌ Search index 'embeddings-index' not found"
        echo "   💡 Run ./docker-init-data.sh to initialize the database"
    fi
else
    echo "❌ Redis connection failed"
fi

echo ""
echo "5. 🌐 Application Health:"
echo "-------------------------"
if curl -f http://localhost:8000/ > /dev/null 2>&1; then
    echo "✅ Flask app is responding on port 8000"
    
    # Test a query if everything looks good
    if [ "$db_size" -gt 0 ] && grep -q "OPENAI_API_KEY=sk-" .env 2>/dev/null; then
        echo "🧪 Testing query functionality..."
        response=$(curl -s -X POST http://localhost:8000/query \
            -H "Content-Type: application/json" \
            -d '{"query": "test"}' | head -c 100)
        
        if echo "$response" | grep -q "error"; then
            echo "❌ Query test failed: $response"
        else
            echo "✅ Query test successful"
        fi
    fi
else
    echo "❌ Flask app not responding on port 8000"
fi

echo ""
echo "📋 Summary & Next Steps:"
echo "========================"

# Provide recommendations based on findings
if [ ! -f .env ] || ! grep -q "OPENAI_API_KEY=sk-" .env 2>/dev/null; then
    echo "🔧 1. Set up your OpenAI API key:"
    echo "   cp env.template .env"
    echo "   # Edit .env and add your OpenAI API key"
fi

if [ "$db_size" -eq 0 ] 2>/dev/null || ! docker exec huberman-redis redis-cli FT._LIST | grep -q "embeddings-index" 2>/dev/null; then
    echo "🔧 2. Initialize the Redis database:"
    echo "   ./docker-init-data.sh"
fi

if ! docker-compose ps | grep -q "Up.*healthy"; then
    echo "🔧 3. Start/restart the services:"
    echo "   ./docker-start.sh"
fi

echo ""
echo "For more help, see DOCKER_README.md" 