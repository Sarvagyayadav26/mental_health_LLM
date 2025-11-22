import os
import datetime
import hashlib

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


# ----------------------------------------------
# 🔥 INITIALIZE EVERYTHING ONCE (FAST)
# ----------------------------------------------

def get_docs_hash(doc_dir):
    """Calculate hash of all document files to detect changes."""
    doc_files = [f for f in os.listdir(doc_dir) if f.endswith(".txt")]
    if not doc_files:
        return None
    
    hasher = hashlib.md5()
    for filename in sorted(doc_files):
        filepath = os.path.join(doc_dir, filename)
        if os.path.exists(filepath):
            mtime = os.path.getmtime(filepath)
            hasher.update(f"{filename}:{mtime}".encode())
    return hasher.hexdigest()


def get_saved_docs_hash():
    """Get saved hash from file."""
    hash_file = os.path.join(config.DATA_DIR, ".docs_hash")
    if os.path.exists(hash_file):
        with open(hash_file, "r") as f:
            return f.read().strip()
    return None


def save_docs_hash(hash_value):
    """Save hash to file."""
    hash_file = os.path.join(config.DATA_DIR, ".docs_hash")
    with open(hash_file, "w") as f:
        f.write(hash_value)


print("🔄 Initializing RAG pipeline for Android API...")

EMBEDDER = Embedder()
VECTOR_STORE = InMemoryVectorStore()
VECTOR_STORE.load()

INDEXER = Indexer(EMBEDDER, VECTOR_STORE)

# Smart re-indexing: only re-index if documents changed
doc_dir = os.path.join(config.DATA_DIR, "docs")
current_hash = get_docs_hash(doc_dir)
saved_hash = get_saved_docs_hash()

if VECTOR_STORE.embeddings is None or current_hash != saved_hash:
    print("📚 Loading and indexing documents...")
    docs = load_text_documents(doc_dir)
    # Clear existing data and re-index
    VECTOR_STORE.ids = []
    VECTOR_STORE.texts = []
    VECTOR_STORE.metadatas = []
    VECTOR_STORE.embeddings = None
    INDEXER.index_documents(docs)
    if current_hash:
        save_docs_hash(current_hash)
    print(f"✅ Indexed {len(docs)} document sections")
else:
    print(f"✅ Using cached vector store ({len(VECTOR_STORE.ids)} sections)")

RETRIEVER = Retriever(EMBEDDER, VECTOR_STORE)
LLM = LLMClient()

print("✅ Android RAG pipeline ready!")


# ----------------------------------------------
# 🔥 FUNCTION USED BY FastAPI → SUPER FAST
# ----------------------------------------------

def run_rag_pipeline(user_q: str):
    """Fast RAG pipeline for Android API calls."""

    chat_history = ChatHistory()
    chat_history.add_user(user_q)

    retrieved = RETRIEVER.retrieve(user_q, top_k=3)

    # Fallback
    if len(retrieved) == 0:
        simple_explain_msg = [{
            "role": "user",
            "content": f"Explain this in very simple words: '{user_q}'"
        }]
        simple_explanation = LLM.generate(simple_explain_msg)
        final_answer = (
            "\n\nI don't have a solution yet. Try consulting a doctor until we find one."
            + simple_explanation.strip()
        )
        return final_answer

    # Normal RAG
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

    return answer
