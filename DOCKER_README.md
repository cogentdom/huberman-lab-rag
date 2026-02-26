# Huberman Lab RAG - Docker Setup

This document provides instructions for running the Huberman Lab RAG application using Docker containers.

## Prerequisites

- Docker and Docker Compose installed on your system
- OpenAI API key

## Quick Start

1. **Clone the repository and navigate to the project directory**

2. **Set up environment variables**
   ```bash
   cp env.template .env
   ```
   Edit the `.env` file and add your OpenAI API key:
   ```
   OPENAI_API_KEY=your_actual_api_key_here
   ```

3. **Build and start the services**
   ```bash
   ./docker-start.sh
   ```
   
   Or manually:
   ```bash
   docker-compose up --build
   ```

4. **Initialize the database (FIRST RUN ONLY)**
   ```bash
   ./docker-init-data.sh
   ```
   This step loads the embeddings and creates the search index in Redis. 
   **Note**: After first initialization, data persists automatically across container restarts.

5. **Access the application**
   - Main application: http://localhost:8000
   - RedisInsight (Redis web UI): http://localhost:8001

## Services

### Flask Application (huberman-app)
- **Port**: 8000
- **Container**: huberman-app
- **Features**: 
  - RAG-powered chat interface
  - Query processing with vector embeddings
  - Context-aware responses using Huberman Lab content
  - Auto-restore mechanism for search index
  - Persistent data across container restarts

### Redis Stack (huberman-redis)
- **Ports**: 
  - 6379 (Redis server)
  - 8001 (RedisInsight web UI)
- **Container**: huberman-redis
- **Features**:
  - Vector search capabilities
  - Enhanced persistent data storage with multiple save points
  - Initialized with existing backup data
  - Automatic protected mode disabled for container communication

## Data Persistence

- **Redis Data**: Automatically persisted in Docker volume `redis_data` with enhanced save settings
- **Application Data**: Mounted read-only from `./app/data`
- **Chat History**: Persisted in Docker volume `app_chat_history`
- **Redis Backup**: The existing `redis_backup_20250619_064236.rdb` is automatically loaded on first startup
- **Auto-Restore**: Search index is automatically checked and restored on container startup
- **Data Backup**: Use `./docker-backup.sh` to create timestamped backups

## Development Commands

### Start services
```bash
docker-compose up
```

### Start services in background
```bash
docker-compose up -d
```

### View logs
```bash
docker-compose logs -f app
docker-compose logs -f redis
```

### Stop services
```bash
docker-compose down
```

### Rebuild and restart
```bash
docker-compose down
docker-compose up --build
```

### Clean up (removes volumes)
```bash
docker-compose down -v
```

### Full cleanup and restart
```bash
./docker-clean.sh
./docker-start.sh
```

### Diagnose issues
```bash
./docker-diagnose.sh
```

### Initialize database
```bash
./docker-init-data.sh
```

### Create backup
```bash
./docker-backup.sh
```

## Troubleshooting

### Quick Diagnosis
Run the diagnostic script to identify issues:
```bash
./docker-diagnose.sh
```

### "Sorry, there was an error processing your request"
This error usually indicates one of two issues:

1. **Invalid OpenAI API Key**:
   ```bash
   # Edit .env file and add your real API key
   nano .env
   # Then restart the app container
   docker-compose restart app
   ```

2. **Empty Redis Database**:
   ```bash
   # Initialize the database with embeddings
   ./docker-init-data.sh
   ```
   **Note**: With the new auto-restore feature, this should happen automatically on startup.

### Network Issues
If you see "network not found" errors:
```bash
./docker-clean.sh  # Clean up
./docker-start.sh  # Start fresh
```

### Redis Connection Issues
- Check if Redis service is healthy: `docker-compose ps`
- View Redis logs: `docker-compose logs redis`

### Application Issues
- Check app logs: `docker-compose logs app`
- Verify environment variables are set correctly
- Ensure `.env` file exists with valid `OPENAI_API_KEY`

### Data Issues
- Ensure the `app/data` directory contains the required `.pkl` files
- Check that the Redis backup file exists: `app/redis_backup_20250619_064236.rdb`

### Module Loading Issues
If Redis fails to start with module errors, the docker-compose.yml has been configured to use only the essential modules (RedisSearch, RedisJSON, RedisBloom, RedisTimeSeries) and excludes problematic ones.

## Health Checks

Both services include health checks:
- **Redis**: Responds to `redis-cli ping`
- **App**: HTTP GET to `http://localhost:8000/`

Check service health:
```bash
docker-compose ps
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `OPENAI_API_KEY` | OpenAI API key for embeddings and chat | Required |
| `REDIS_HOST` | Redis hostname | `redis` (in Docker) |
| `REDIS_PORT` | Redis port | `6379` |
| `REDIS_PASSWORD` | Redis password | Empty |
| `FLASK_ENV` | Flask environment | `production` |

## File Structure

```
.
├── docker-compose.yml      # Docker services configuration
├── Dockerfile             # Flask app container definition
├── .dockerignore          # Files to exclude from Docker build
├── .env.example           # Environment template
├── app/                   # Application code
│   ├── app.py            # Flask application
│   ├── utils.py          # Redis and OpenAI utilities
│   ├── data/             # Application data (mounted read-only)
│   ├── templates/        # Flask templates
│   └── redis_backup_*.rdb # Redis backup file
└── requirements.txt       # Python dependencies
``` 