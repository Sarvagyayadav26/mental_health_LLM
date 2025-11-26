from flask import Flask, request, jsonify
from src.rag.retriever import Retriever
from src.llm.client import LLMClient
from src.storage.chat_history import ChatHistory
from src.rag.embeddings import Embedder
from src.storage.vector_store import InMemoryVectorStore as VectorStore
from src.storage.user_db import create_user, get_user, init_db, save_message
import bcrypt


# Initialize DB
init_db()

app = Flask(__name__)

# RAG Components
embedder = Embedder()
vector_store = VectorStore()
retriever = Retriever(embedder, vector_store)

# LLM + History
llm_client = LLMClient()
chat_history = ChatHistory()


# ----------------------------------------------------------------------
# CHAT ENDPOINT
# ----------------------------------------------------------------------
@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json(silent=True)

    print("📨 Incoming JSON:", data)

    if data is None:
        return jsonify({'error': 'Invalid JSON'}), 400

    # Accept frontend keys
    email = data.get("email")
    user_input = (
        data.get("input") or
        data.get("message") or
        data.get("text") or
        data.get("query")
    )

    if not email:
        return jsonify({'error': 'Email missing'}), 400

    if not user_input:
        return jsonify({'error': 'No input provided'}), 400

    try:
        # Retrieve documents
        documents = retriever.retrieve(user_input)

        # LLM call
        reply = llm_client.generate_response([
            {"role": "user", "content": user_input}
        ])

        # Save history (local JSON)
        chat_history.add_user(user_input)
        chat_history.add_assistant(reply)

        # Save messages in DB
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

        return jsonify({
            "reply": reply,
            "documents": documents_clean,
            "error": None
        }), 200

    except Exception as e:
        print("🔥 SERVER ERROR:", e)
        return jsonify({"error": "Internal Server Error"}), 500
    #

# ----------------------------------------------------------------------
# CHAT HISTORY
# ----------------------------------------------------------------------
@app.route('/history', methods=['GET'])
def history():
    return jsonify(chat_history.get_history()), 200


# ----------------------------------------------------------------------
# AUTH: REGISTER
# ----------------------------------------------------------------------
@app.route("/auth/register", methods=["POST"])
def register():
    data = request.get_json()

    email = data.get("email")
    age = data.get("age")
    sex = data.get("sex")
    password = data.get("password")

    if not email or age is None or not sex or not password:
        return jsonify({"error": "Missing fields"}), 400

    if get_user(email):
        return jsonify({"error": "User already exists"}), 400

    create_user(email, age, sex, password)

    return jsonify({"success": "User registered"}), 200



# ----------------------------------------------------------------------
# AUTH: LOGIN
# ----------------------------------------------------------------------
@app.route("/auth/login", methods=["POST"])
def login():
    data = request.get_json()

    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"error": "Email and password required"}), 400

    user = get_user(email)

    if not user:
        return jsonify({"error": "User does not exist"}), 404

    stored_hash = user[3]  # email, age, sex, password_hash, usage_count

    if not bcrypt.checkpw(password.encode(), stored_hash.encode()):
        return jsonify({"error": "Incorrect password"}), 401

    return jsonify({
        "success": "Login successful",
        "email": user[0],
        "age": user[1],
        "sex": user[2],
        "usage_count": user[4]
    }), 200


# ----------------------------------------------------------------------
# RUN SERVER
# ----------------------------------------------------------------------
if __name__ == '__main__':
    app.run(debug=True)
