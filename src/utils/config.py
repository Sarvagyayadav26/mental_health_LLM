import os
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")  
GROQ_API_KEY= os.getenv("GROQ_API_KEY")
GROQ_MODEL=os.getenv("GROQ_MODEL", "openai/gpt-oss-20b")

# Sentence Transformers model name
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")

# Base data directory
DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "data")

CHAT_HISTORY_PATH = os.getenv(
    "CHAT_HISTORY_PATH",
    os.path.join(DATA_DIR, "chat_history.json")
)

VECTOR_STORE_PATH = os.getenv(
    "VECTOR_STORE_PATH",
    os.path.join(DATA_DIR, "vector_store.index")  # change depending on storage type
)
