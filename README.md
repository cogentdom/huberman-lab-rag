# Huberman Lab RAG

![Python](https://img.shields.io/badge/python-v3.12+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

![banner](https://cogentdom.wordpress.com/wp-content/uploads/2026/02/huberman-lab-rag-interface.png)

## Overview

The Huberman Lab RAG (Retrieval-Augmented Generation) system is an intelligent conversational AI platform that makes neuroscience knowledge from the Huberman Lab podcast freely accessible to everyone. This system serves as an ethereal persona of Dr. Andrew Huberman's teachings, providing expert insights into health, performance, and neuroscience topics based on the extensive content library from his podcast episodes.

## Purpose & Mission

Dr. Andrew Huberman, Ph.D., is a neuroscientist and tenured professor at Stanford School of Medicine who has made significant contributions to brain development, brain function, and neural plasticity research. The Huberman Lab podcast aims to make neuroscience tools freely accessible to everyone. This RAG system extends that mission by creating an intelligent assistant named "Costello" that can answer questions about health and performance using the vast knowledge contained within podcast transcripts.

## 📊 Data Sources & Content

### Primary Data Source
All content in this RAG system is derived from **publicly available Huberman Lab podcast episodes** hosted on YouTube. The system contains no private, personal, or confidential information.

### Content Details
- **Source**: [Huberman Lab YouTube Channel](https://www.youtube.com/@hubermanlab)
- **Content Type**: Auto-generated YouTube transcripts from podcast episodes
- **Episodes Covered**: 290+ episodes (as of data collection)
- **Topics Include**:
  - Sleep optimization and circadian rhythms
  - Nutrition and supplementation
  - Exercise and physical performance
  - Mental health and stress management
  - Learning and neuroplasticity
  - Vision and eye health
  - Hormones and endocrine function
  - And many more neuroscience-backed health topics

### Data Processing
1. **Collection**: YouTube URLs and metadata scraped using `youtube_get_data.ipynb`
2. **Transcription**: Transcripts obtained via YouTube Transcript API using `youtube_transcript_gen.ipynb`
3. **Storage**: Raw transcripts stored as text files in `data/documents/`
4. **Processing**: Content chunked and embedded using OpenAI's text-embedding-3-small model
5. **Indexing**: Vector embeddings stored in Redis for efficient semantic search

### Content Integrity
- **No Modification**: Transcript content is used as-is from YouTube's auto-generated transcripts
- **Attribution**: All responses cite the original Huberman Lab podcast content
- **Educational Purpose**: Content used under fair use for educational and research purposes
- **Public Domain**: All source material is freely accessible public content

### Data Transparency
- **Complete Episode List**: Available in `data/huberman_videos.csv`
- **Transparent Processing**: All data pipeline code is open source
- **Reproducible**: Users can regenerate the entire dataset using provided notebooks

## 🚀 Features

### Intelligent Query Processing
- Natural language understanding for health and neuroscience questions
- Context-aware answers using retrieved podcast content
- Structured responses comparing different approaches and effectiveness
- Synthesizes information from multiple sources efficiently

### Advanced Retrieval System
- **Vector Search**: Uses OpenAI's text-embedding-3-small for semantic similarity
- **Redis Storage**: High-performance vector database with RedisSearch
- **Chunked Content**: Smart document segmentation for precise retrieval
- **Ranking System**: Selects context based on relevance scores

### User Interfaces
- **Web Interface**: Flask-based chat application
- **API Endpoint**: RESTful API for programmatic access
- **RedisInsight**: Database visualization and monitoring

### Production-Ready Deployment
- **Docker**: Complete Docker Compose setup
- **Data Persistence**: Automatic backup and restore capabilities
- **Health Monitoring**: Built-in checks for all services
- **Auto-Recovery**: Intelligent recovery and index restoration

## 📋 Prerequisites

- Python 3.12+
- Docker and Docker Compose
- OpenAI API key
- At least 4GB RAM recommended

## 🛠 Installation & Setup

### 1. Clone the Repository
```bash
git clone <repository-url>
cd huberman-lab-rag
```

### 2. Environment Setup

**Important**: You must create a `.env` file to store your OpenAI API key securely.

#### Step-by-step .env file creation:

1. **Create the .env file** in the project root directory:
   ```bash
   touch .env
   ```
   Or on Windows:
   ```cmd
   type nul > .env
   ```

2. **Add your OpenAI API key** to the `.env` file:
   ```bash
   echo "OPENAI_API_KEY=your_actual_api_key_here" >> .env
   ```
   Or manually edit the `.env` file and add:
   ```
   OPENAI_API_KEY=your_actual_api_key_here
   ```

3. **Get your OpenAI API key**:
   - Visit [OpenAI Platform](https://platform.openai.com/api-keys)
   - Create an account or sign in
   - Generate a new API key
   - Replace `your_actual_api_key_here` with your actual key

**⚠️ Security Note**: The `.env` file is automatically excluded from git via `.gitignore` to keep your API key secure. Never commit API keys to version control.

### 3. Create Data Directory
```bash
mkdir -p data/documents
```

### 4. Install Dependencies

#### Using Virtual Environment (Recommended)
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

#### Using Docker
```bash
docker-compose up -d
```

### 5. Database Setup

**MongoDB**: Default port 27017
- Username: `root`
- Password: `example`

**Redis Stack**: Ports 6379 (Redis) and 8001 (RedisInsight)
- Access RedisInsight at: `http://localhost:8001`

## 📊 Data Pipeline Workflow

### Step 1: Data Collection
1. **Scrape podcast URLs**:
   ```bash
   jupyter notebook youtube_get_data.ipynb
   ```
   - Saves scraped data to `huberman_videos.csv`

2. **Generate transcripts**:
   ```bash
   jupyter notebook youtube_transcript_gen.ipynb
   ```
   - Saves transcripts to `data/documents/` directory as `.txt` files

### Step 2: Document Storage
1. **Initialize MongoDB**:
   ```bash
   python pymongo_get_database.py
   ```

2. **Insert documents**:
   ```bash
   python pymongo_test_insert_file.py
   ```

### Step 3: Preprocessing
1. **Chunk and embed documents**:
   ```bash
   jupyter notebook document_embedding.ipynb
   ```
   - Creates `embedding.csv` with document embeddings

### Step 4: Vector Indexing
1. **Create Redis vector index**:
   ```bash
   jupyter notebook redis_index_embeddings.ipynb
   ```

### Step 5: Query Interface
1. **Test query functionality**:
   ```bash
   jupyter notebook query_database.ipynb
   ```

2. **Run the web application**:
   ```bash
   python app.py
   ```
   - Access the web interface at: `http://localhost:5000`

## 🔌 API Usage

### Query Endpoint
```bash
curl -X POST http://localhost:5000/query \
  -H "Content-Type: application/json" \
  -d '{"query": "What are the best supplements for sleep?"}'
```

### Response Format
```json
{
  "response": "Based on the Huberman Lab content, here are the most effective supplements for sleep..."
}
```

## 🏗 Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Flask Web UI  │    │   API Endpoint  │    │  Query Processor│
└─────────┬───────┘    └─────────┬───────┘    └─────────┬───────┘
          │                      │                      │
          └──────────────────────┼──────────────────────┘
                                 │
                    ┌─────────────┴───────────┐
                    │      Vector Search      │
                    │    (Redis + OpenAI)     │
                    └─────────────┬───────────┘
                                 │
                    ┌─────────────┴───────────┐
                    │    Document Storage     │
                    │      (MongoDB)          │
                    └─────────────────────────┘
```

## 🔧 Configuration

Key configuration files:
- `requirements.txt`: Python dependencies
- `docker-compose.yml`: Container orchestration
- `utils.py`: Core functionality and database connections
- `.env`: Environment variables (create this file)

## 🐛 Troubleshooting

### Common Issues

1. **Redis Connection Error**
   ```bash
   # Check if Redis is running
   docker ps | grep redis
   # Restart Redis container
   docker-compose restart redis-stack
   ```

2. **MongoDB Authentication Issues**
   - Verify credentials in `docker-compose.yml`
   - Check connection string in Python scripts

3. **OpenAI API Rate Limits**
   - Implement exponential backoff
   - Consider using a higher-tier API plan

4. **Memory Issues**
   - Reduce batch sizes in embedding generation
   - Use smaller chunk sizes for documents

## 📚 Additional Resources

- [Huberman Lab Podcast](https://hubermanlab.com/)
- [OpenAI API Documentation](https://platform.openai.com/docs)
- [Redis Vector Similarity](https://redis.io/docs/stack/search/reference/vectors/)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## ⚠️ Disclaimer

This project is for educational and research purposes. Always consult with healthcare professionals for medical advice. The AI responses are based on podcast content and should not replace professional medical consultation. 

