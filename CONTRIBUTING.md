# Contributing

Thanks for your interest in improving `huberman-lab-rag`.

## Development setup

1. Create a virtual environment and install dependencies:

   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

2. Create `.env` from template and add `OPENAI_API_KEY`:

   ```bash
   cp env.template .env
   ```

3. Ensure Redis is running and index the data:

   ```bash
   redis-server
   python app/setup_vector_db.py
   ```

4. Run the app:

   ```bash
   ./run_app.sh
   ```

## Pull request guidelines

- Keep PRs focused and small when possible
- Update docs if behavior/setup changes
- Avoid committing secrets (`.env` is ignored)
- Avoid committing large generated artifacts unless explicitly needed

## Suggested verification before opening a PR

- App UI loads at `http://localhost:8000`
- API responds at `POST /query`
- Redis index exists and returns results
- Docker path still works if your changes touch runtime/setup files
