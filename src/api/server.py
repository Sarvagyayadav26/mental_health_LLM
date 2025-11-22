from flask import Flask, request, jsonify
from src.rag.retriever import Retriever
from src.llm.client import LLMClient
from src.storage.chat_history import ChatHistory

app = Flask(__name__)

retriever = Retriever()
llm_client = LLMClient()
chat_history = ChatHistory()

@app.route('/chat', methods=['POST'])
def chat():
    user_input = request.json.get('input')
    if not user_input:
        return jsonify({'error': 'No input provided'}), 400

    # Retrieve relevant documents
    documents = retriever.retrieve_documents(user_input)

    # Generate a response from the LLM
    response = llm_client.generate_response(user_input)

    # Store the chat entry
    chat_history.add_entry(user_input, response)

    return jsonify({'response': response, 'documents': documents})

@app.route('/history', methods=['GET'])
def history():
    return jsonify(chat_history.get_history())

if __name__ == '__main__':
    app.run(debug=True)