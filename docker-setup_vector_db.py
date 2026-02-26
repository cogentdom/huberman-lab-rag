import openai
import os
from typing import List, Iterator
import pandas as pd
import numpy as np
import pickle
from ast import literal_eval
from loguru import logger

# Redis client library for Python
import redis
from redis.commands.search.indexDefinition import (
    IndexDefinition,
    IndexType
)
from redis.commands.search.query import Query
from redis.commands.search.field import (
    TextField,
    VectorField
)

# I've set this to our new embeddings model, this can be changed to the embedding model of your choice
EMBEDDING_MODEL = "text-embedding-3-small"

# Ignore unclosed SSL socket warnings - optional in case you get these errors
import warnings

warnings.filterwarnings(action="ignore", message="unclosed", category=ResourceWarning)
warnings.filterwarnings("ignore", category=DeprecationWarning) 

print("🔄 Loading data files...")

# Load Data - using absolute paths for container
data_dir = "/app/app/data"
transcript_df = pd.read_csv(f'{data_dir}/embeddings.csv')

# Load title dictionary from pickle file
with open(f'{data_dir}/title_dict.pkl', 'rb') as f:
    title_dict = pickle.load(f)

title_df = pd.DataFrame(title_dict.items(), columns=['video_key', 'title'])

# Load chunk dictionary from pickle file
with open(f'{data_dir}/chunk_dict.pkl', 'rb') as f:
    chunk_dict = pickle.load(f)

chunk_df = pd.DataFrame(chunk_dict.items(), columns=['chunk_key', 'text'])

print(f"📊 Loaded {len(transcript_df)} transcript records")
print(f"📊 Loaded {len(title_dict)} titles")
print(f"📊 Loaded {len(chunk_dict)} chunks")

# Join transcript_df with title_df on video_id to add titles
transcript_df = transcript_df.merge(title_df, on='video_key', how='left')
transcript_df = transcript_df.merge(chunk_df, on='chunk_key', how='left')

# Read vectors from strings back into a list
transcript_df['title_vector'] = transcript_df.title_vector.apply(literal_eval)
transcript_df['content_vector'] = transcript_df.content_vector.apply(literal_eval)

# Set vector_id to be a string
transcript_df['video_key'] = transcript_df['video_key'].apply(str)

print(f"📊 Final dataset shape: {transcript_df.shape}")

# --- Redis Setup ---
REDIS_HOST = os.getenv("REDIS_HOST", "redis")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", "")

print(f"🔗 Connecting to Redis at {REDIS_HOST}:{REDIS_PORT}")

# Connect to Redis with improved settings for large data loading
redis_client = redis.Redis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    password=REDIS_PASSWORD if REDIS_PASSWORD else None,
    socket_timeout=30,  # Increase timeout for large operations
    socket_connect_timeout=10,
    socket_keepalive=True,
    socket_keepalive_options={},
    health_check_interval=30,
    retry_on_timeout=True,
    decode_responses=False  # Keep binary mode for vector data
)

try:
    redis_client.ping()
    print("✅ Redis connection successful")
except Exception as e:
    print(f"❌ Redis connection failed: {e}")
    exit(1)

# Create search index
# Constants
VECTOR_DIM = len(transcript_df['title_vector'][0]) # length of the vectors
VECTOR_NUMBER = len(transcript_df)                 # initial number of vectors
INDEX_NAME = "embeddings-index"                    # name of the search index
PREFIX = "doc"                                     # prefix for the document keys
DISTANCE_METRIC = "COSINE"                         # distance metric for the vectors (ex. COSINE, IP, L2)

print(f"🔍 Setting up search index '{INDEX_NAME}' with {VECTOR_NUMBER} vectors of dimension {VECTOR_DIM}")

# Define RediSearch fields for each of the columns in the dataset
title = TextField(name="title")
text = TextField(name="text")
video_key = TextField(name="video_key")
chunk_key = TextField(name="chunk_key")

title_embedding = VectorField("title_vector",
    "FLAT", {
        "TYPE": "FLOAT32",
        "DIM": VECTOR_DIM,
        "DISTANCE_METRIC": DISTANCE_METRIC,
        "INITIAL_CAP": VECTOR_NUMBER,
    }
)
content_embedding = VectorField("content_vector",
    "FLAT", {
        "TYPE": "FLOAT32",
        "DIM": VECTOR_DIM,
        "DISTANCE_METRIC": DISTANCE_METRIC,
        "INITIAL_CAP": VECTOR_NUMBER,
    }
)
fields = [title, text, video_key, chunk_key, title_embedding, content_embedding]

# Check if index exists
try:
    info = redis_client.ft(INDEX_NAME).info()
    print(f"⚠️ Index '{INDEX_NAME}' already exists, dropping it first...")
    redis_client.ft(INDEX_NAME).dropindex()
except:
    print(f"🆕 Creating new index '{INDEX_NAME}'...")

# Create RediSearch Index
redis_client.ft(INDEX_NAME).create_index(
    fields = fields,
    definition = IndexDefinition(prefix=[PREFIX], index_type=IndexType.HASH)
)

print("✅ Search index created successfully")

# Load Documents into Index with batch processing and error handling
def index_documents(client: redis.Redis, prefix: str, documents: pd.DataFrame):
    records = documents.to_dict("records")
    total = len(records)
    batch_size = 50  # Process in smaller batches
    
    for i in range(0, total, batch_size):
        batch_end = min(i + batch_size, total)
        batch_records = records[i:batch_end]
        
        print(f"📝 Indexing documents {i+1}-{batch_end}/{total}")
        
        # Use pipeline for batch operations
        pipe = client.pipeline()
        
        for doc in batch_records:
            try:
                key = f"{prefix}:{str(doc['id'])}"

                # create byte vectors for title and content
                title_embedding = np.array(doc["title_vector"], dtype=np.float32).tobytes()
                content_embedding = np.array(doc["content_vector"], dtype=np.float32).tobytes()

                # replace list of floats with byte vectors
                doc["title_vector"] = title_embedding
                doc["content_vector"] = content_embedding

                pipe.hset(key, mapping = doc)
            except Exception as e:
                print(f"⚠️ Error processing document {doc.get('id', 'unknown')}: {e}")
                continue
        
        try:
            pipe.execute()
        except Exception as e:
            print(f"⚠️ Error executing batch {i+1}-{batch_end}: {e}")
            # Try individual inserts for this batch
            for doc in batch_records:
                try:
                    key = f"{prefix}:{str(doc['id'])}"
                    title_embedding = np.array(doc["title_vector"], dtype=np.float32).tobytes()
                    content_embedding = np.array(doc["content_vector"], dtype=np.float32).tobytes()
                    doc["title_vector"] = title_embedding
                    doc["content_vector"] = content_embedding
                    client.hset(key, mapping = doc)
                except Exception as doc_e:
                    print(f"⚠️ Failed to index document {doc.get('id', 'unknown')}: {doc_e}")
                    continue

print("📤 Loading documents into search index...")
index_documents(redis_client, PREFIX, transcript_df)

# Verify the setup
db_info = redis_client.info()
num_keys = db_info.get('db0', {}).get('keys', 0)
print(f"✅ Successfully loaded {num_keys} documents in Redis search index '{INDEX_NAME}'")

# Test the search functionality
print("🧪 Testing search functionality...")
try:
    query = redis_client.ft(INDEX_NAME).search("sleep")
    print(f"✅ Search test successful - found {len(query.docs)} results for 'sleep'")
except Exception as e:
    print(f"⚠️ Search test failed: {e}")

print("🎉 Setup completed successfully!") 