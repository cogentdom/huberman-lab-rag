import openai

from typing import List, Iterator
import pandas as pd
import numpy as np
import os
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

# Load Data
transcript_df = pd.read_csv('data/embeddings.csv')
# Load title dictionary from pickle file
with open('data/title_dict.pkl', 'rb') as f:
    title_dict = pickle.load(f)

title_df = pd.DataFrame(title_dict.items(), columns=['video_key', 'title'])

# Load title dictionary from pickle file
with open('data/chunk_dict.pkl', 'rb') as f:
    chunk_dict = pickle.load(f)

chunk_df = pd.DataFrame(chunk_dict.items(), columns=['chunk_key', 'text'])

# Join transcript_df with title_df on video_id to add titles
transcript_df = transcript_df.merge(title_df, on='video_key', how='left')
transcript_df = transcript_df.merge(chunk_df, on='chunk_key', how='left')

# Read vectors from strings back into a list
transcript_df['title_vector'] = transcript_df.title_vector.apply(literal_eval)
transcript_df['content_vector'] = transcript_df.content_vector.apply(literal_eval)

# Set vector_id to be a string
transcript_df['video_key'] = transcript_df['video_key'].apply(str)

# --- Redis Setup ---
REDIS_HOST =  "localhost"
REDIS_PORT = 6379
REDIS_PASSWORD = "" # default for passwordless Redis

# Connect to Redis
redis_client = redis.Redis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    password=REDIS_PASSWORD
)
redis_client.ping()

# Create search index
# Constants
VECTOR_DIM = len(transcript_df['title_vector'][0]) # length of the vectors
VECTOR_NUMBER = len(transcript_df)                 # initial number of vectors
INDEX_NAME = "embeddings-index"                    # name of the search index
PREFIX = "doc"                                     # prefix for the document keys
DISTANCE_METRIC = "COSINE"                         # distance metric for the vectors (ex. COSINE, IP, L2)

# Define RediSearch fields for each of the columns in the dataset
title = TextField(name="title")
text = TextField(name="text")
video_key = TextField(name="video_key")
chunk_key = TextField(name="chunk_key")
# url = TextField(name="url")

title_embedding = VectorField("title_vector",
    "FLAT", {
        "TYPE": "FLOAT32",
        "DIM": VECTOR_DIM,
        "DISTANCE_METRIC": DISTANCE_METRIC,
        "INITIAL_CAP": VECTOR_NUMBER,
    }
)
text_embedding = VectorField("content_vector",
    "FLAT", {
        "TYPE": "FLOAT32",
        "DIM": VECTOR_DIM,
        "DISTANCE_METRIC": DISTANCE_METRIC,
        "INITIAL_CAP": VECTOR_NUMBER,
    }
)
fields = [title, text, video_key, chunk_key, title_embedding, text_embedding]

# Check if index exists
try:
    redis_client.ft(INDEX_NAME).info()
    print("Index already exists")
except:
    # Create RediSearch Index
    redis_client.ft(INDEX_NAME).create_index(
        fields = fields,
        definition = IndexDefinition(prefix=[PREFIX], index_type=IndexType.HASH)
    )

 # Load Documents into Index
def index_documents(client: redis.Redis, prefix: str, documents: pd.DataFrame):
    records = documents.to_dict("records")
    for doc in records:
        key = f"{prefix}:{str(doc['id'])}"

        # create byte vectors for title and content
        title_embedding = np.array(doc["title_vector"], dtype=np.float32).tobytes()
        content_embedding = np.array(doc["content_vector"], dtype=np.float32).tobytes()

        # replace list of floats with byte vectors
        doc["title_vector"] = title_embedding
        doc["content_vector"] = content_embedding

        client.hset(key, mapping = doc)

index_documents(redis_client, PREFIX, transcript_df)
logger.info(f"Loaded {redis_client.info()['db0']['keys']} documents in Redis search index with name: {INDEX_NAME}")
