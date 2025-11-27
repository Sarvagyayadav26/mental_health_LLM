from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.concurrency import run_in_threadpool
from pydantic import BaseModel
import time
import logging
from flask import request
import bcrypt
from fastapi import HTTPException

# User DB imports
from src.storage.user_db import init_db, create_user, get_user, increment_usage

# RAG pipeline imports
from src.android_main import initialize_all, run_rag_pipeline

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Mental Health RAG API")

# Initialize DB immediately
init_db()

# Run RAG initialization AFTER server starts
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

# Incoming chat body format
class ChatQuery(BaseModel):
    email: str
    message: str


# ⛔ OLD ENDPOINT — DO NOT USE
# class Query(BaseModel):
#     message: str


# --------------------------------------------------------
# ✅ AUTH REGISTRATION ENDPOINT
# --------------------------------------------------------
@app.post("/auth/register")
async def register_user(data: dict):
    email = data.get("email")
    age = data.get("age")
    sex = data.get("sex")
    password = data.get("password")

    # Check missing fields
    missing_fields = []
    if not email: missing_fields.append("email")
    if not age: missing_fields.append("age")
    if not sex: missing_fields.append("sex")
    if not password: missing_fields.append("password")

    if missing_fields:
        raise HTTPException(
            status_code=400,
            detail=f"Missing required field(s): {', '.join(missing_fields)}"
        )

    # Check if user exists
    user = get_user(email)
    if user:
        return {
            "status": "existing",
            "message": "Welcome back!",
            "usage_count": user[3],
        }

    # Create new user
    create_user(email, age, sex, password)

    return {
        "status": "new",
        "message": "User created successfully",
        "usage_count": 0,
    }



# --------------------------------------------------------
# ✅ CHAT ENDPOINT WITH USAGE LIMIT
# --------------------------------------------------------
@app.post("/chat")
async def chat(query: ChatQuery):
    email = query.email
    message = query.message

    user = get_user(email)
    if not user:
        raise HTTPException(status_code=400, detail="User not registered")

    usage = user[3]
    FREE_LIMIT = 5  # ← modify this if needed

    # ----- FREE RESPONSE LIMIT -------
    if usage >= FREE_LIMIT:
        return {
            "allowed": False,
            "error": "Free limit reached. Please subscribe to continue.",
            "used": usage,
            "limit": FREE_LIMIT,
        }

    # Run RAG pipeline
    start = time.time()
    reply = await run_in_threadpool(run_rag_pipeline, message)

    # Increment usage count
    increment_usage(email)

    return {
        "allowed": True,
        "reply": reply,
        "usage_now": usage + 1,
        "limit": FREE_LIMIT,
        "processing_time": round(time.time() - start, 2),
    }


# --------------------------------------------------------
# HEALTH CHECK
# --------------------------------------------------------
@app.get("/health")
def health():
    return {"status": "ok", "message": "server running"}

