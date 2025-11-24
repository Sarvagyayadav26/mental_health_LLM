import os
import datetime
import hashlib

from fastapi import FastAPI
from pydantic import BaseModel

from src.rag.embeddings import Embedder
from src.storage.vector_store import InMemoryVectorStore
from src.rag.indexer import Indexer
from src.rag.retriever import Retriever
from src.storage.chat_history import ChatHistory
from src.llm.client import LLMClient
from src.llm.prompts import build_messages
from src.llm.instruction_templates import DEFAULT_INSTRUCTION
from src.rag.doc_loader import load_text_documents
import src.utils.config as config


# ================================================================
# 🧠 1. RAG INITIALIZATION (Optimized — loads existing index)
# ================================================================
def init_rag():
    """
    Initialize RAG:
    - Loads existing vector_store.index.npz (fast)
    - Only builds index if missing (slow)
    """
    print("🔄 Initializing RAG pipeline for Android API...")

    embedder = Embedder()
    store = InMemoryVectorStore()
    vs_path = config.VECTOR_STORE_PATH

    # 1️⃣ Load existing vector store
    if os.path.exists(vs_path):
        print(f"🔍 Found vector store at: {vs_path}")
        store.load(vs_path)
        print(f"✅ Loaded vector store with {len(store.ids)} documents.")

    else:
        # 2️⃣ Fallback — build only if missing
        print("📚 No vector store found — building index (slow)...")
        docs = load_text_documents(config.DOCS_DIR)
        indexer = Indexer(embedder, store)
        indexer.index_documents(docs)
        print(f"✅ Vector store built and saved to {vs_path}")

    retriever = Retriever(embedder, store)
    return embedder, store, retriever


# Initialize globally ONCE (Railway can reuse this)
EMBEDDER, VECTOR_STORE, RAG = init_rag()

LLM = LLMClient()
chat_history = ChatHistory()


# ================================================================
# 📱 FASTAPI APP (Android API)
# ================================================================
app = FastAPI()


class Query(BaseModel):
    text: str


@app.post("/android-rag")
def android_rag(query: Query):
    user_q = query.text.strip()
    if not user_q:
        return {"error": "Empty query"}

    chat_history.add_user(user_q)

    # 🔍 Retrieve top docs
    try:
        retrieved = RAG.retrieve(user_q, top_k=3)
    except Exception as e:
        return {"error": f"Retriever error: {e}"}

    # 🧠 Generate messages for LLM
    try:
        messages = build_messages(
            user_q,
            retrieved,
            chat_history.last_n(6),
            instruction=DEFAULT_INSTRUCTION
        )
        answer = LLM.generate(messages)

    except Exception as e:
        answer = "RAG failed internally. Error: " + str(e)

    chat_history.add_assistant(answer)

    return {
        "question": user_q,
        "answer": answer,
        "retrieved_docs": retrieved
    }


# ================================================================
# 🔎 HEALTH CHECK
# ================================================================
@app.get("/")
def root():
    return {"status": "ok", "message": "Android RAG API is running!"}

# ================================================================
# 🧠 Reusable RAG function for API server (used by android_server.py)
# ================================================================
def run_rag_pipeline(user_query: str):
    user_query = user_query.strip()
    if not user_query:
        return "Empty query"

    chat_history.add_user(user_query)

    # Retrieve documents
    retrieved = RAG.retrieve(user_query, top_k=3)

    # Build LLM messages
    messages = build_messages(
        user_query,
        retrieved,
        chat_history.last_n(6),
        instruction=DEFAULT_INSTRUCTION
    )

    # Generate answer
    answer = LLM.generate(messages)

    chat_history.add_assistant(answer)

    return answer
