import numpy as np
import os
import pickle
import openai
from dotenv import load_dotenv
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
from typing import List
from collections import defaultdict

EMBEDDING_MODEL = "text-embedding-3-small"

load_dotenv()
open_api_key = os.getenv("OPENAI_API_KEY")
openai_client = openai.OpenAI(api_key=open_api_key)

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

# Save the defaultdict to a file
def save_defaultdict(data, filename):
    with open(filename, 'wb') as file:
        pickle.dump(dict(data), file)

# Load the defaultdict from the file
def load_defaultdict(filename):
    with open(filename, 'rb') as file:
        loaded_dict = pickle.load(file)
        restored_dict = defaultdict(lambda: defaultdict(list), loaded_dict)
    return restored_dict

def load_dict(filename: str) -> dict:
    with open(filename, 'rb') as f:
        return pickle.load(f)

def save_dict(data: dict, filename: str):
    with open(filename, 'wb') as f:
        pickle.dump(data, f)

# Helper function to get the video key from the chunk key
def get_video_key(chunk_key: str) -> str:
    return chunk_key.split('_chunk_')[0]

# Helper function to get the chunk index from the chunk key
def get_chunk_index(chunk_key: str) -> int:
    return int(chunk_key.split('_chunk_')[1])

# --- Query Tools ---
# Helper function to search on multiple fields
def create_hybrid_field(field_name: str, value: str) -> str:
    return f'@{field_name}:"{value}"'

# Search top K results from Redis using Embeddings
def search_redis(
    openai_client: openai.OpenAI,
    redis_client: redis.Redis,
    user_query: str,
    index_name: str = "embeddings-index",
    vector_field: str = "content_vector",
    return_fields: list = ["title", "text", "chunk_key", "vector_score"],
    hybrid_fields = "*",
    k: int = 5,
) -> List[dict]:
    # Creates embedding vector from user query
    embedded_query = openai_client.embeddings.create(input=user_query,
                                            model=EMBEDDING_MODEL,
                                            ).data[0].embedding
    # Prepare the Query
    base_query = f'{hybrid_fields}=>[KNN {k} @{vector_field} $vector AS vector_score]'
    query = (
        Query(base_query)
         .return_fields(*return_fields)
         .sort_by("vector_score")
         .paging(0, k)
         .dialect(2)
    )
    params_dict = {"vector": np.array(embedded_query).astype(dtype=np.float32).tobytes()}

    # Perform vector search
    results = redis_client.ft(index_name).search(query, params_dict)
    for i, article in enumerate(results.docs):
        score = 1 - float(article.vector_score)
        # print(f"{i}. {article.title}\n(Score: {round(score ,3) })")
    return results.docs

def add_context(
    chunk_keys: list,
    file_name: str,
    title_dict: dict,
    chunk_dict: dict,
):
    with open(f'data/prompt.txt', 'r', encoding='utf-8') as f:
        prompt = f.read()

    for i, chunk_key in enumerate(chunk_keys):
        video_key = get_video_key(chunk_key)
        prompt = f"{prompt}### Context Document {i}\nTitle: \t{title_dict[video_key]}\nContent: \t{chunk_dict[chunk_key]}\n\n\n"

    os.makedirs('chat_history/prompts', exist_ok=True)
    with open(f"chat_history/prompts/{file_name}.txt", "w") as f:
        f.write(prompt)

def process_query(user_query: str) -> str:
    results = search_redis(
        openai_client, 
        redis_client, 
        user_query, 
        vector_field='content_vector', 
        k=10
    )

    chunk_keys = [x.chunk_key for x in results]

    with open('data/title_dict.pkl', 'rb') as f:
        title_dict = pickle.load(f)
    with open('data/chunk_dict.pkl', 'rb') as f:
        chunk_dict = pickle.load(f)

    add_context(
        chunk_keys,
        'prompt_5',
        title_dict,
        chunk_dict
    )

    with open("chat_history/prompts/prompt_5.txt", "r", encoding="utf-8") as f:
        instructions = f.read()

    response = openai_client.responses.create(
        model="o4-mini",
        instructions=instructions,
        input=user_query,
    )

    os.makedirs('chat_history', exist_ok=True)
    with open(f"chat_history/response_5.txt", "w", encoding='utf-8') as f:
        f.write(response.output_text)

    return response.output_text

