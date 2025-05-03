import numpy as np
import os
import pickle
import openai
import redis
from typing import List
from collections import defaultdict
from redis.commands.search.query import Query

EMBEDDING_MODEL = "text-embedding-3-small"

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
    vector_field: str = "title_vector",
    return_fields: list = ["title", "text", "chunk_id", "vector_score"],
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
    chunk_ids: list,
    file_name: str,
    title_dict: dict,
    chunk_dict: dict,
):
    with open(f'data/prompt.txt', 'r', encoding='utf-8') as f:
        prompt = f.read()

    for i, chunk_id in enumerate(chunk_ids):
        video_id = chunk_id.split('_videoid:')[1].split('_chunk:')[0]
        prompt = f"{prompt}### Context Document {i}\nTitle: \t{title_dict[video_id]}\nContext: \t{chunk_dict[chunk_id]}\n"

    os.makedirs('data/prompts', exist_ok=True)
    with open(f"data/prompts/{file_name}.txt", "w") as f:
        f.write(prompt)

def ingest_query(
    openai_client: openai.OpenAI,
    redis_client: redis.Redis,
    user_query: str,
    k: int = 5,
    # vector_field: str = "content_vector",
):
    results = search_redis(
        openai_client, 
        redis_client, 
        user_query, 
        k, 
        # vector_field
    )

    chunk_ids = [x.chunk_id for x in results]

    with open('data/title_dict.pkl', 'rb') as f:
        title_dict = pickle.load(f)
    with open('data/chunk_dict.pkl', 'rb') as f:
        chunk_dict = pickle.load(f)

    add_context(
        chunk_ids,
        'prompt_0.txt',
        title_dict,
        chunk_dict
    )

