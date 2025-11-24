from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.concurrency import run_in_threadpool
from pydantic import BaseModel
import time
import logging

from src.android_main import initialize_all, run_rag_pipeline

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Mental Health RAG API")

# Run initialization AFTER server starts (important)
@app.on_event("startup")
def startup_event():
    logger.info("🚀 Starting system initialization...")
    initialize_all()
    logger.info("✅ RAG system ready!")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class Query(BaseModel):
    message: str

@app.post("/chat")
async def chat(query: Query):
    start = time.time()

    reply = await run_in_threadpool(run_rag_pipeline, query.message)

    return {
        "reply": reply,
        "processing_time": round(time.time() - start, 2),
    }

@app.get("/health")
def health():
    return {"status": "ok", "message": "server running"}
