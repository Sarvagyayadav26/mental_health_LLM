from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.concurrency import run_in_threadpool
from pydantic import BaseModel
import time
import logging
from flask import request
import bcrypt
from fastapi import HTTPException
from src.storage.chat_history import ChatHistory


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

class RegisterRequest(BaseModel):
    email: str
    age: int
    sex: str
    password: str
# ⛔ OLD ENDPOINT — DO NOT USE
# class Query(BaseModel):
#     message: str
#hi

# --------------------------------------------------------
# ✅ AUTH REGISTRATION ENDPOINT
# --------------------------------------------------------
@app.post("/auth/register")
async def register_user(request: RegisterRequest):
    try:
        email = request.email
        age = request.age
        sex = request.sex
        password = request.password

        # Check if user exists
        user = get_user(email)
        if user:
            return {
                "success": "existing",
                "error": None
            }

        # Create new user
        create_user(email, age, sex, password)

        return {
            "success": "new",
            "error": None
        }

    except Exception as e:
        return {
            "success": None,
            "error": str(e)
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
        return {
            "allowed": False,
            "error": "User not registered",
            "reply": None
        }

    # Extract usage_count from database
    usage = user[3]
    try:
        usage = int(usage)
    except:
        usage = 0

    FREE_LIMIT = 50
    if usage >= FREE_LIMIT:
        return {
            "allowed": False,
            "error": "Free limit reached. Please subscribe to continue.",
            "used": usage,
            "limit": FREE_LIMIT,
            "reply": None
        }

    # 👉 NEW: per-user chat history
    chat_history = ChatHistory(email)

    start = time.time()
    try:
        # 👉 Pass ChatHistory to the RAG pipeline
        reply = await run_in_threadpool(run_rag_pipeline, message, chat_history)
    except Exception as e:
        return {
            "allowed": False,
            "error": f"Failed to generate reply: {str(e)}",
            "reply": None
        }

    increment_usage(email)

    return {
        "allowed": True,
        "reply": reply,
        "usage_now": usage + 1,
        "limit": FREE_LIMIT,
        "processing_time": round(time.time() - start, 2),
        "error": None
    }



# --------------------------------------------------------
# HEALTH CHECK
# --------------------------------------------------------
@app.get("/health")
def health():
    return {"status": "ok", "message": "server running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.api.android_server:app", host="0.0.0.0", port=8000, reload=True)

# --------------------------------------------------------
# ✅ AUTH LOGIN ENDPOINT
# --------------------------------------------------------
class LoginRequest(BaseModel):
    email: str
    password: str

@app.post("/auth/login")
async def login(req: LoginRequest):
    # Debug: see raw email
    print("LOGIN EMAIL RAW:", repr(req.email))

    email = req.email.strip().lower()
    password = req.password

    user = get_user(email)
    if not user:
        return {"error": "User does not exist"}

    stored_hash = user[3]

    if not bcrypt.checkpw(password.encode(), stored_hash.encode()):
        return {"error": "Incorrect password"}

    return {
        "success": "Login successful",
        "email": user[0],
        "age": user[1],
        "sex": user[2],
        "usage_count": user[4]
    }
