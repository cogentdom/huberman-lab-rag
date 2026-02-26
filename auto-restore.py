#!/usr/bin/env python3
"""
Auto-restore script for Huberman Lab RAG
Automatically restores the search index if it's missing after container restart
"""

import redis
import os
import time
import sys

def check_and_restore():
    """Check if search index exists and restore if needed"""
    
    REDIS_HOST = os.getenv("REDIS_HOST", "redis") 
    REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
    
    print("🔍 Auto-restore: Checking search index status...")
    
    # Wait for Redis to be ready
    max_retries = 30
    for i in range(max_retries):
        try:
            client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, socket_timeout=5, decode_responses=False)
            client.ping()
            print("✅ Redis connection established")
            break
        except Exception as e:
            if i < max_retries - 1:
                print(f"⏳ Waiting for Redis... ({i+1}/{max_retries})")
                time.sleep(2)
            else:
                print(f"❌ Failed to connect to Redis after {max_retries} attempts: {e}")
                return False
    
    # Check if search index exists
    try:
        # Try to get index info
        client.ft("embeddings-index").info()
        print("✅ Search index 'embeddings-index' exists")
        
        # Check if it has data
        db_size = client.dbsize()
        if db_size > 100:  # Should have thousands of documents
            print(f"✅ Database contains {db_size} keys - data looks good")
            return True
        else:
            print(f"⚠️ Database only contains {db_size} keys - may need restoration")
            
    except Exception as e:
        print(f"❌ Search index missing or invalid: {e}")
    
    # Index is missing or empty - trigger restoration
    print("🔄 Triggering search index restoration...")
    
    try:
        # Import and run the setup script
        import subprocess
        result = subprocess.run([
            sys.executable, "/app/docker-setup_vector_db.py"
        ], capture_output=True, text=True, timeout=600)  # 10 minute timeout
        
        if result.returncode == 0:
            print("✅ Search index restoration completed successfully!")
            
            # Verify restoration
            client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=False)
            db_size = client.dbsize()
            print(f"📊 Database now contains {db_size} keys")
            
            try:
                client.ft("embeddings-index").info()
                print("✅ Search index verified working")
                return True
            except Exception as e:
                print(f"❌ Search index verification failed: {e}")
                return False
                
        else:
            print(f"❌ Restoration failed with exit code {result.returncode}")
            print(f"STDOUT: {result.stdout}")
            print(f"STDERR: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ Restoration timed out after 10 minutes")
        return False
    except Exception as e:
        print(f"❌ Restoration failed: {e}")
        return False

if __name__ == "__main__":
    success = check_and_restore()
    sys.exit(0 if success else 1) 