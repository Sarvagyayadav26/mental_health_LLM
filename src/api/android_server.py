from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.concurrency import run_in_threadpool
from pydantic import BaseModel, Field, field_validator
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import uvicorn
import time
import logging
import os
from typing import Optional
from src.android_main import run_rag_pipeline

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Rate limiting
limiter = Limiter(key_func=get_remote_address)

app = FastAPI(
    title="Mental Health RAG API",
    description="RAG-based mental health assistant API for Android",
    version="1.0.0"
)

# Apply rate limiter
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS middleware for Android app
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your Android app's domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Query(BaseModel):
    message: str = Field(..., min_length=1, max_length=1000, description="User's question or message")
    
    @field_validator('message')
    @classmethod
    def validate_message(cls, v):
        if not v or not v.strip():
            raise ValueError("Message cannot be empty")
        # Basic sanitization
        v = v.strip()
        if len(v) > 1000:
            raise ValueError("Message too long (max 1000 characters)")
        return v

class HealthResponse(BaseModel):
    status: str
    timestamp: float
    vector_store_size: int

class TopicInfo(BaseModel):
    id: str
    source: str
    topics: list[str]
    preview: str

class TopicsResponse(BaseModel):
    total_sections: int
    topics: list[TopicInfo]

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint for monitoring."""
    from src.android_main import VECTOR_STORE
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "vector_store_size": len(VECTOR_STORE.ids) if VECTOR_STORE.ids else 0
    }

@app.get("/topics", response_model=TopicsResponse)
async def get_indexed_topics():
    """
    Get all indexed topics/sections.
    Useful for displaying available topics in the Android app.
    """
    from src.android_main import VECTOR_STORE
    
    topics_list = []
    
    if VECTOR_STORE.ids and VECTOR_STORE.metadatas and VECTOR_STORE.texts:
        for i, (doc_id, metadata, text) in enumerate(zip(
            VECTOR_STORE.ids, 
            VECTOR_STORE.metadatas, 
            VECTOR_STORE.texts
        )):
            topics = metadata.get("topics", [])
            source = metadata.get("source", "unknown")
            preview = text[:100].replace("\n", " ") if text else ""
            
            topics_list.append({
                "id": doc_id,
                "source": source,
                "topics": topics,
                "preview": preview + "..." if len(text) > 100 else preview
            })
    
    return {
        "total_sections": len(topics_list),
        "topics": topics_list
    }

@app.post("/chat")
@limiter.limit("10/minute")  # Rate limit: 10 requests per minute per IP
async def chat(request: Request, query: Query):
    """
    Main chat endpoint for Android app.
    Returns AI-generated response based on RAG pipeline.
    """
    start_time = time.time()
    
    try:
        # Input validation is handled by Pydantic
        user_message = query.message
        
        logger.info(f"Received query: {user_message[:50]}...")
        
        # Run RAG pipeline
        response = await run_in_threadpool(run_rag_pipeline, user_message)
        
        processing_time = time.time() - start_time
        
        logger.info(f"Query processed in {processing_time:.2f}s")
        
        return {
            "reply": response,
            "processing_time": round(processing_time, 2),
            "status": "success"
        }
        
    except ValueError as e:
        logger.warning(f"Validation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error processing query: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="An error occurred while processing your request. Please try again."
        )

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler."""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error", "status": "error"}
    )

if __name__ == "__main__":
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=5001,
        log_level="info"
    )
