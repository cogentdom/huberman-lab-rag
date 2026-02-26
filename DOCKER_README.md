# Huberman Lab RAG - Docker Guide

This guide covers running the full RAG stack with Docker: Flask app + Redis Stack.

## Prerequisites

- Docker Desktop (or Docker Engine + Compose)
- OpenAI API key

## Quick start

1. Create environment file:

   ```bash
   cp env.template .env
   ```

2. Set your API key in `.env`:

   ```bash
   OPENAI_API_KEY=your_actual_api_key_here
   ```

3. Start services:

   ```bash
   ./docker-start.sh
   ```

4. Initialize vector data (first run, or after a full reset):

   ```bash
   ./docker-init-data.sh
   ```

5. Open:
   - App: `http://localhost:8000`
   - RedisInsight: `http://localhost:8001`

## Services

### `huberman-app` (Flask)

- Port `8000`
- Serves the web UI and `/query` API
- Runs an auto-restore check at startup (`auto-restore.py`)

### `huberman-redis` (Redis Stack)

- Ports `6379` (Redis) and `8001` (RedisInsight)
- Stores vector index + documents
- Uses persistent volume-backed storage

## Persistence and restore behavior

- Redis data persists in Docker volume `redis_data`
- App chat prompts/responses persist in `app_chat_history`
- `app/data` is mounted read-only into container
- On startup:
  - Redis loads `dump.rdb` from volume (or initial backup if needed)
  - App checks whether `embeddings-index` exists
  - Missing index is automatically rebuilt when possible

## Common commands

Start:

```bash
docker-compose up
```

Start detached:

```bash
docker-compose up -d
```

Logs:

```bash
docker-compose logs -f app
docker-compose logs -f redis
```

Stop:

```bash
docker-compose down
```

Stop + remove volumes:

```bash
docker-compose down -v
```

Rebuild:

```bash
docker-compose down
docker-compose up --build
```

Diagnostics:

```bash
./docker-diagnose.sh
```

Backup:

```bash
./docker-backup.sh
```

## Troubleshooting

### API returns request-processing errors

Most common causes:

- Missing/invalid `OPENAI_API_KEY` in `.env`
- Redis index not initialized

Fix:

```bash
./docker-init-data.sh
docker-compose restart app
```

### Redis connectivity or startup issues

- Check service status: `docker-compose ps`
- Check Redis logs: `docker-compose logs redis`
- If network/resources are stale, run:

  ```bash
  ./docker-clean.sh
  ./docker-start.sh
  ```

### Data/index issues

Ensure required data files exist in `app/data/`:

- `embeddings.csv`
- `title_dict.pkl`
- `chunk_dict.pkl`

## Environment variables

| Variable | Description | Default |
| --- | --- | --- |
| `OPENAI_API_KEY` | OpenAI API key used for query embeddings/chat | Required |
| `REDIS_HOST` | Redis hostname inside Docker network | `redis` |
| `REDIS_PORT` | Redis port | `6379` |
| `REDIS_PASSWORD` | Redis password | Empty |
| `FLASK_ENV` | Flask environment mode | `production` |
