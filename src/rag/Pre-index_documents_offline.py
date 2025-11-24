from src.rag.embeddings import Embedder
from src.storage.vector_store import InMemoryVectorStore
from src.rag.indexer import Indexer
from src.rag.doc_loader import load_text_documents

embedder = Embedder()
store = InMemoryVectorStore()
indexer = Indexer(embedder, store)

docs = load_text_documents("./data/docs")
indexer.index_documents(docs)


