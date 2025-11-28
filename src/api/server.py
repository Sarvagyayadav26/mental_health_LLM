from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from src.rag.retriever import Retriever
from src.llm.client import LLMClient
from src.storage.chat_history import ChatHistory
from src.rag.embeddings import Embedder
from src.storage.vector_store import InMemoryVectorStore as VectorStore
from src.storage.user_db import create_user, get_user, init_db, save_message

import bcrypt
print("🔥 FASTAPI SERVER FILE LOADED!")


# ----------------------------------------------------------------------
# INITIALIZE APP + COMPONENTS
# ----------------------------------------------------------------------
app = FastAPI()
init_db()

embedder = Embedder()
vector_store = VectorStore()
retriever = Retriever(embedder, vector_store)

llm_client = LLMClient()
chat_history = ChatHistory()


# ----------------------------------------------------------------------
# REQUEST MODELS (Swagger uses these)
# ----------------------------------------------------------------------
class ChatRequest(BaseModel):
    email: str
    message: str


class RegisterRequest(BaseModel):
    email: str
    age: int
    sex: str
    password: str


class LoginRequest(BaseModel):
    email: str
    password: str


# ----------------------------------------------------------------------
# CHAT ENDPOINT
# ----------------------------------------------------------------------
@app.post("/chat")
async def chat(req: ChatRequest):
    email = req.email
    user_input = req.input

    try:
        # Retrieve RAG documents
        documents = retriever.retrieve(user_input)

        # LLM Response
        reply = llm_client.generate_response([
            {"role": "user", "content": user_input}
        ])

        # Save chat history
        chat_history.add_user(user_input)
        chat_history.add_assistant(reply)

        # Save to DB
        save_message(email, "user", user_input)
        save_message(email, "assistant", reply)

        # Clean docs
        documents_clean = [
            {
                "text": d["text"],
                "score": d["score"],
                "metadata": d["metadata"]
            }
            for d in documents
        ]

        return JSONResponse({
            "reply": reply,
            "documents": documents_clean,
            "error": None
        })

    except Exception as e:
        print("🔥 CHAT ERROR:", e)
        return JSONResponse({"error": "Internal Server Error"}, status_code=500)


# ----------------------------------------------------------------------
# CHAT HISTORY
# ----------------------------------------------------------------------
@app.get("/history")
def history():
    return JSONResponse(chat_history.get_history())


# ----------------------------------------------------------------------
# REGISTER USER
# ----------------------------------------------------------------------
@app.post("/auth/register")
async def register(req: RegisterRequest):

    if get_user(req.email):
        return JSONResponse({"error": "User already exists"}, status_code=400)

    create_user(req.email, req.age, req.sex, req.password)

    return JSONResponse({"success": "User registered"})


# ----------------------------------------------------------------------
# LOGIN USER
# ----------------------------------------------------------------------
@app.post("/auth/login")
async def login(req: LoginRequest):

    user = get_user(req.email)

    if not user:
        return JSONResponse({"error": "User does not exist"}, status_code=404)

    stored_hash = user[3]

    if not bcrypt.checkpw(req.password.encode(), stored_hash.encode()):
        return JSONResponse({"error": "Incorrect password"}, status_code=401)

    return JSONResponse({
        "success": "Login successful",
        "email": user[0],
        "age": user[1],
        "sex": user[2],
        "usage_count": user[4]
    })

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.api.server:app", host="0.0.0.0", port=8000, reload=True)
