# Local Quickstart

Use this guide when running without Docker.

## Prerequisites

- Python 3.12+
- Redis Stack or Redis running on `localhost:6379`
- OpenAI API key
- Data assets present in `app/data/`:
  - `embeddings.csv`
  - `title_dict.pkl`
  - `chunk_dict.pkl`

## 1) Environment setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp env.template .env
```

Edit `.env` and set:

```bash
OPENAI_API_KEY=your_openai_api_key_here
```

## 2) Start Redis

```bash
redis-server
```

Verify:

```bash
redis-cli ping
```

## 3) Build the vector index

```bash
cd app
python setup_vector_db.py
cd ..
```

## 4) Run the app

```bash
./run_app.sh
```

## 5) Access endpoints

- Web UI: `http://localhost:8000`
- API: `POST http://localhost:8000/query`

Example request:

```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"query":"What are the benefits of cold exposure?"}'
```

## Troubleshooting

- `No module named ...`: activate `.venv` and run from project root
- Redis errors: ensure `redis-cli ping` returns `PONG`
- Empty / poor responses: rebuild the index with `python app/setup_vector_db.py`

## Stop the app

- Press `Ctrl+C` in the running terminal
- Optional force stop: `lsof -ti:8000 | xargs kill -9`
