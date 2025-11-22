# Deployment Guide

## Quick Start with Docker

1. **Create `.env` file:**
```bash
GROQ_API_KEY=your_groq_api_key_here
GROQ_MODEL=openai/gpt-oss-20b
EMBEDDING_MODEL=all-MiniLM-L6-v2
```

2. **Build and run:**
```bash
docker-compose up -d
```

3. **Check health:**
```bash
curl http://localhost:5001/health
```

## Cloud Deployment Options

### Option 1: Railway
1. Connect your GitHub repo to Railway
2. Add environment variables in Railway dashboard
3. Railway will auto-detect Dockerfile and deploy

### Option 2: Render
1. Create new Web Service
2. Connect GitHub repo
3. Set build command: `docker build -t rag-api .`
4. Set start command: `docker run -p 5001:5001 rag-api`
5. Add environment variables

### Option 3: AWS/GCP/Azure
- Use container services (ECS, Cloud Run, Container Instances)
- Upload Docker image to container registry
- Deploy with environment variables

## Environment Variables

Required:
- `GROQ_API_KEY`: Your Groq API key

Optional:
- `GROQ_MODEL`: Model to use (default: openai/gpt-oss-20b)
- `EMBEDDING_MODEL`: Embedding model (default: all-MiniLM-L6-v2)
- `DATA_DIR`: Path to data directory (default: ./data)

## API Endpoints

### POST /chat
Main chat endpoint for Android app.

**Request:**
```json
{
  "message": "I'm feeling anxious about my career"
}
```

**Response:**
```json
{
  "reply": "AI-generated response...",
  "processing_time": 1.23,
  "status": "success"
}
```

### GET /health
Health check endpoint for monitoring.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": 1234567890.123,
  "vector_store_size": 100
}
```

## Performance Tips

1. **Vector Store Caching**: The system automatically caches the vector store and only re-indexes when documents change.

2. **Scaling**: For high traffic, consider:
   - Using a load balancer
   - Running multiple instances
   - Using a shared vector store (Redis/PostgreSQL)

3. **Monitoring**: Set up monitoring for:
   - `/health` endpoint
   - Response times
   - Error rates

## Security Considerations

1. **CORS**: Update `allow_origins` in `android_server.py` to your Android app's domain
2. **Rate Limiting**: Consider adding rate limiting middleware
3. **API Keys**: Never commit `.env` file to git
4. **Input Validation**: Already implemented with Pydantic

## Troubleshooting

- **Port already in use**: Change port in docker-compose.yml
- **Vector store not loading**: Check data directory permissions
- **API key errors**: Verify GROQ_API_KEY in environment variables

