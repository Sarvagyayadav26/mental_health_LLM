from .instruction_templates import DEFAULT_INSTRUCTION

def build_messages(user_query: str, retrieved_docs: list, chat_history: list, instruction: str = None):
    instruction = instruction or DEFAULT_INSTRUCTION

    system_msg = {
        "role": "system",
        "content": instruction
    }

    if not retrieved_docs:
        # No relevant documents → simple explanation mode
        user_content = f"""
You are a helpful assistant.

The user said:
"{user_query}"

1. First, explain the user’s issue in very simple words.
2. Then say: "I don’t have a solution yet. Try consulting a doctor until we find one."

Do NOT hallucinate any extra advice or treatments.
        """

        return [system_msg, {"role": "user", "content": user_content}]

    # retrieved docs exist
    docs_text = []
    for d in retrieved_docs:
        docs_text.append(f"[{d['id']}] {d['text']}")

    docs_block = "\n\n".join(docs_text)

    user_content = f"""Based on the following retrieved document, answer the user's question about "{user_query}".

Retrieved document:
{docs_block}

Instructions:
- Use the content from the retrieved document above to answer the question
- If the content is brief, expand on it naturally and provide helpful context
- Be empathetic and supportive
- The text in brackets is actual content, not a placeholder

Now provide a helpful answer to: {user_query}"""

    return [
        system_msg,
        {"role": "user", "content": user_content}
    ]