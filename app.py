from flask import Flask, render_template, request, jsonify
import os
from dotenv import load_dotenv
import openai
import redis
import numpy as np
from typing import List
import pickle

app = Flask(__name__)

# Load environment variables
load_dotenv()
open_api_key = os.getenv("OPENAI_API_KEY")
openai_client = openai.OpenAI(api_key=open_api_key)

# Redis configuration
REDIS_HOST = "localhost"
REDIS_PORT = 6379
REDIS_PASSWORD = ""

# Connect to Redis
redis_client = redis.Redis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    password=REDIS_PASSWORD
)

EMBEDDING_MODEL = "text-embedding-3-small"

def search_redis(
    openai_client: openai.OpenAI,
    redis_client: redis.Redis,
    user_query: str,
    index_name: str = "embeddings-index",
    vector_field: str = "content_vector",
    return_fields: list = ["title", "text", "chunk_id", "vector_score"],
    hybrid_fields = "*",
    k: int = 5,
) -> List[dict]:
    embedded_query = openai_client.embeddings.create(
        input=user_query,
        model=EMBEDDING_MODEL,
    ).data[0].embedding
    
    base_query = f'{hybrid_fields}=>[KNN {k} @{vector_field} $vector AS vector_score]'
    query = (
        Query(base_query)
         .return_fields(*return_fields)
         .sort_by("vector_score")
         .paging(0, k)
         .dialect(2)
    )
    params_dict = {"vector": np.array(embedded_query).astype(dtype=np.float32).tobytes()}
    
    results = redis_client.ft(index_name).search(query, params_dict)
    return results.docs

def add_context(
    chunk_ids: list,
    file_name: str,
    title_dict: dict,
    chunk_dict: dict,
):
    with open('data/prompt.txt', 'r', encoding='utf-8') as f:
        prompt = f.read()

    for i, chunk_id in enumerate(chunk_ids):
        video_id = chunk_id.split('_videoid:')[1].split('_chunk:')[0]
        prompt = f"{prompt}### Context Document {i}\nTitle: \t{title_dict[video_id]}\nContext: \t{chunk_dict[chunk_id]}\n\n\n"

    os.makedirs('data/prompts', exist_ok=True)
    with open(f"data/prompts/{file_name}.txt", "w") as f:
        f.write(prompt)

def process_query(user_query: str) -> str:
    results = search_redis(
        openai_client, 
        redis_client, 
        user_query, 
        vector_field='content_vector', 
        k=10
    )

    chunk_ids = [x.chunk_id for x in results]

    with open('data/title_dict.pkl', 'rb') as f:
        title_dict = pickle.load(f)
    with open('data/chunk_dict.pkl', 'rb') as f:
        chunk_dict = pickle.load(f)

    add_context(
        chunk_ids,
        'prompt_0',
        title_dict,
        chunk_dict
    )

    with open("data/prompts/prompt_0.txt", "r", encoding="utf-8") as f:
        instructions = f.read()

    response = openai_client.responses.create(
        model="o4-mini",
        instructions=instructions,
        input=user_query,
    )

    # Save response to chat history
    os.makedirs('chat_history', exist_ok=True)
    with open(f"chat_history/response.txt", "w") as f:
        f.write(response.output_text)

    return response.output_text

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/query', methods=['POST'])
def query():
    data = request.get_json()
    user_query = data.get('query', '')
    if not user_query:
        return jsonify({'error': 'No query provided'}), 400
    
    try:
        response = process_query(user_query)
        return jsonify({'response': response})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True) 