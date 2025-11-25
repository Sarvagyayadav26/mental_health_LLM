from flask import Flask, request, jsonify
from src.rag.retriever import Retriever
from src.llm.client import LLMClient
from src.storage.chat_history import ChatHistory
from src.rag.embeddings import Embedder
from src.storage.vector_store import InMemoryVectorStore as VectorStore
from src.storage.user_db import create_user, get_user, init_db
init_db()

app = Flask(__name__)

embedder = Embedder()
vector_store = VectorStore()
retriever = Retriever(embedder, vector_store)

llm_client = LLMClient()
chat_history = ChatHistory()

@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json(silent=True)

    if data is None:
        return jsonify({'error': 'Invalid JSON'}), 400

    user_input = data.get("input")
    if not user_input:
        return jsonify({'error': 'No input provided'}), 400

    try:
        # Retrieve relevant documents
        documents = retriever.retrieve_documents(user_input)

        # Generate LLM response — WARNING: this may take long
        response = llm_client.generate_response(user_input)

        # Save to history
        chat_history.add_entry(user_input, response)

        return jsonify({
            "response": response,
            "documents": documents,
            "error": None
        })

    except Exception as e:
        print("SERVER ERROR:", e)
        return jsonify({"error": "Server crashed"}), 500



@app.route('/history', methods=['GET'])
def history():
    return jsonify(chat_history.get_history())

@app.route("/auth/register", methods=["POST"])
def register():
    data = request.get_json()

    print("\n🔥 REGISTER ENDPOINT HIT")
    print("📨 Received JSON:", data)

    email = data.get("email") if data else None
    age = data.get("age") if data else None
    sex = data.get("sex") if data else None

    print("📌 Parsed email:", email)
    print("📌 Parsed age:", age)
    print("📌 Parsed sex:", sex)

    if not email or age is None or not sex:
        print("❌ ERROR: Missing fields\n")
        return jsonify({"error": "Missing fields"}), 400

    if get_user(email):
        print("❌ ERROR: User already exists\n")
        return jsonify({"error": "User already exists"}), 400

    create_user(email, int(age), sex)

    print("✅ SUCCESS: User registered\n")
    return jsonify({"success": "User registered"}), 200


@app.route("/auth/login", methods=["POST"])
def login():
    data = request.get_json()

    email = data.get("email")

    if not email:
        return jsonify({"error": "Email is required"}), 400

    user = get_user(email)
    if not user:
        return jsonify({"error": "User does not exist"}), 404

    return jsonify({
        "success": "Login successful",
        "email": user[0],
        "age": user[1],
        "sex": user[2],
        "usage_count": user[3]
    }), 200


if __name__ == '__main__':
    app.run(debug=True)