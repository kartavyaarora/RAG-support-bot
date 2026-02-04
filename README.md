# RAG Q&A Support Bot

A production-ready Retrieval Augmented Generation (RAG) system that crawls websites, indexes content, and answers questions based solely on the crawled data.

## 🌟 Features

- **Website Crawling**: Automatically crawl and extract content from any website
- **Smart Chunking**: Intelligent text chunking with token-aware splitting
- **Vector Search**: Semantic search using OpenAI embeddings and ChromaDB
- **Context-Aware Answers**: GPT-powered answers based only on indexed content
- **RESTful API**: Complete FastAPI implementation with multiple endpoints
- **Persistent Storage**: Local ChromaDB vector database with persistence
- **Comprehensive Logging**: Detailed logging for debugging and monitoring

## 📋 Table of Contents

- [Architecture](#architecture)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [API Endpoints](#api-endpoints)
- [Testing](#testing)
- [Project Structure](#project-structure)
- [Troubleshooting](#troubleshooting)

## 🏗️ Architecture

The system follows a modular RAG pipeline:

```
User Question → Query Endpoint
                    ↓
              Generate Embedding (OpenAI)
                    ↓
              Vector Search (ChromaDB)
                    ↓
              Retrieve Relevant Chunks
                    ↓
              Generate Answer (GPT)
                    ↓
              Return Answer + Sources
```

### Components

1. **Web Crawler**: Scrapes website content with domain-specific crawling
2. **Text Chunker**: Splits content into token-aware chunks with overlap
3. **Embedding Service**: Generates embeddings using OpenAI API
4. **Vector Database**: ChromaDB for semantic similarity search
5. **LLM Service**: GPT-4 for context-aware answer generation
6. **FastAPI Server**: RESTful API with comprehensive endpoints

## 🔧 Prerequisites

- Python 3.8 or higher
- OpenAI API key
- 2GB+ free disk space (for ChromaDB)

## 📦 Installation

### 1. Clone the Repository

```bash
git clone <your-repo-url>
cd rag-support-bot
```

### 2. Create Virtual Environment

```bash
python -m venv venv

# On Windows
venv\Scripts\activate

# On macOS/Linux
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Set Up Environment Variables

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env and add your OpenAI API key
# Required: OPENAI_API_KEY=your-api-key-here
```

## ⚙️ Configuration

Edit the `.env` file to configure the application:

```env
# Required
OPENAI_API_KEY=your-openai-api-key-here

# Optional (with defaults)
APP_HOST=0.0.0.0
APP_PORT=8000
CHROMA_PERSIST_DIRECTORY=./chroma_db
EMBEDDING_MODEL=text-embedding-3-small
CHAT_MODEL=gpt-4-turbo-preview
MAX_PAGES=100
CRAWL_DEPTH=3
```

### Configuration Options

| Variable | Description | Default |
|----------|-------------|---------|
| `OPENAI_API_KEY` | Your OpenAI API key (required) | - |
| `APP_HOST` | Host to bind the server | `0.0.0.0` |
| `APP_PORT` | Port to run the server | `8000` |
| `CHROMA_PERSIST_DIRECTORY` | ChromaDB storage location | `./chroma_db` |
| `EMBEDDING_MODEL` | OpenAI embedding model | `text-embedding-3-small` |
| `CHAT_MODEL` | OpenAI chat model | `gpt-4-turbo-preview` |
| `MAX_PAGES` | Maximum pages to crawl | `100` |
| `CRAWL_DEPTH` | Maximum crawl depth | `3` |

## 🚀 Usage

### Start the Server

```bash
# From the project root
python -m uvicorn app.main:app --reload

# Or using the main module
cd app
python main.py
```

The API will be available at `http://localhost:8000`

### Interactive API Documentation

Once the server is running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 📡 API Endpoints

### 1. Root Endpoint
```http
GET /
```
Returns API information and available endpoints.

### 2. Health Check
```http
GET /health
```
Check API health and service status.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00",
  "version": "1.0.0",
  "openai_configured": true,
  "chroma_initialized": true
}
```

### 3. Crawl Website
```http
POST /crawl
Content-Type: application/json

{
  "url": "https://docs.python.org/3/",
  "max_pages": 50
}
```

**Response:**
```json
{
  "status": "success",
  "message": "Successfully crawled and indexed 50 pages",
  "pages_crawled": 50,
  "pages_indexed": 342,
  "website_url": "https://docs.python.org/3/",
  "timestamp": "2024-01-15T10:35:00"
}
```

### 4. Query the System
```http
POST /query
Content-Type: application/json

{
  "question": "How do I install Python packages?",
  "top_k": 5
}
```

**Response:**
```json
{
  "answer": "To install Python packages, you can use pip...",
  "sources": [
    {
      "url": "https://docs.python.org/3/installing/",
      "title": "Installing Packages",
      "chunk_text": "The standard package installer for Python is pip...",
      "similarity_score": 0.8921
    }
  ],
  "question": "How do I install Python packages?",
  "model_used": "gpt-4-turbo-preview",
  "timestamp": "2024-01-15T10:36:00"
}
```

### 5. Get Statistics
```http
GET /stats
```

**Response:**
```json
{
  "total_documents": 342,
  "total_chunks": 342,
  "indexed_websites": ["https://docs.python.org"],
  "database_size_mb": 15.42,
  "last_indexed": "2024-01-15T10:35:00"
}
```

### 6. Reindex Database
```http
POST /reindex
Content-Type: application/json

{
  "clear_existing": false
}
```

### 7. Clear Database
```http
POST /clear
```

Removes all indexed data from the vector database.

## 🧪 Testing

### Using cURL

#### 1. Check Health
```bash
curl http://localhost:8000/health
```

#### 2. Crawl a Website
```bash
curl -X POST http://localhost:8000/crawl \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://docs.python.org/3/tutorial/",
    "max_pages": 20
  }'
```

#### 3. Query the System
```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What is a Python list?",
    "top_k": 3
  }'
```

#### 4. Get Statistics
```bash
curl http://localhost:8000/stats
```

#### 5. Clear Database
```bash
curl -X POST http://localhost:8000/clear
```

### Using Postman

1. Import the collection from the interactive docs at `/docs`
2. Set up environment variables if needed
3. Test each endpoint individually

### Example Test Flow

```bash
# 1. Check health
curl http://localhost:8000/health

# 2. Crawl a small documentation site
curl -X POST http://localhost:8000/crawl \
  -H "Content-Type: application/json" \
  -d '{"url": "https://fastapi.tiangolo.com/", "max_pages": 30}'

# 3. Wait for crawling to complete, then query
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"question": "How do I create a FastAPI application?"}'

# 4. Check statistics
curl http://localhost:8000/stats
```

## 📁 Project Structure

```
rag-support-bot/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application entry point
│   ├── config.py               # Configuration management
│   ├── api/
│   │   ├── __init__.py
│   │   └── routes.py           # API endpoints
│   ├── models/
│   │   ├── __init__.py
│   │   └── schemas.py          # Pydantic models
│   ├── services/
│   │   ├── __init__.py
│   │   ├── crawler.py          # Web crawling logic
│   │   ├── embeddings.py       # OpenAI embeddings
│   │   ├── vector_db.py        # ChromaDB interface
│   │   ├── llm.py              # LLM service
│   │   └── rag_service.py      # Main RAG orchestration
│   └── utils/
│       ├── __init__.py
│       └── chunker.py          # Text chunking utilities
├── chroma_db/                  # Vector database (created at runtime)
├── .env.example                # Example environment variables
├── .gitignore                  # Git ignore file
├── requirements.txt            # Python dependencies
└── README.md                   # This file
```

## 🔍 How It Works

### 1. Crawling Phase

```python
# The crawler visits pages breadth-first
1. Start from seed URL
2. Extract all links on the same domain
3. Visit each link up to max_depth
4. Extract text content from each page
5. Clean and store content
```

### 2. Indexing Phase

```python
# Content is processed and stored
1. Split content into chunks (500 tokens, 50 overlap)
2. Generate embeddings for each chunk (OpenAI)
3. Store embeddings in ChromaDB with metadata
```

### 3. Query Phase

```python
# Questions are answered using retrieved context
1. Generate embedding for user question
2. Find top-k most similar chunks (cosine similarity)
3. Build context from retrieved chunks
4. Generate answer using GPT with context
5. Return answer with source citations
```

## 🐛 Troubleshooting

### Common Issues

#### 1. OpenAI API Key Error
```
Error: OpenAI API key not configured
```
**Solution**: Make sure you've set `OPENAI_API_KEY` in your `.env` file

#### 2. ChromaDB Permission Error
```
Error: Permission denied for chroma_db directory
```
**Solution**: Ensure the application has write permissions for the ChromaDB directory

#### 3. Crawling Timeout
```
Error: Request timeout while crawling
```
**Solution**: The website might be slow or blocking requests. Try:
- Reduce `max_pages`
- Increase timeout in `crawler.py`
- Check if the website allows crawling

#### 4. No Results Found
```
Answer: "I couldn't find any relevant information..."
```
**Solution**: 
- Ensure the website has been crawled
- Check if your question relates to crawled content
- Try rephrasing your question

### Debugging

Enable debug logging by setting in `.env`:
```env
LOG_LEVEL=debug
```

Check logs for detailed information about:
- Crawling progress
- Embedding generation
- Vector search results
- LLM prompts and responses

## 💡 Best Practices

1. **Start Small**: Test with a small website (10-20 pages) first
2. **Monitor Costs**: OpenAI API calls cost money - monitor your usage
3. **Rate Limiting**: Be respectful when crawling - the default has delays
4. **Question Quality**: Ask specific questions related to crawled content
5. **Regular Updates**: Re-crawl websites periodically to update content

## 🔒 Security Considerations

- Never commit `.env` file with API keys
- In production, use proper secret management
- Implement rate limiting for API endpoints
- Validate and sanitize all inputs
- Use environment-specific CORS settings

## 📈 Performance Tips

1. **Batch Processing**: Embeddings are generated in batches (100)
2. **Persistent Storage**: ChromaDB persists data across restarts
3. **Chunk Size**: Adjust chunk size based on your content type
4. **Top-K Selection**: Use appropriate top_k (3-5 for focused, 10+ for comprehensive)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🆘 Support

For issues and questions:
1. Check the troubleshooting section
2. Review the logs with debug mode enabled
3. Open an issue on GitHub

## 🙏 Acknowledgments

- OpenAI for embeddings and LLM APIs
- ChromaDB for vector database
- FastAPI for the web framework
- BeautifulSoup for HTML parsing

---

**Built with ❤️ using RAG technology**
