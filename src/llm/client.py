import os

# 🔥 Debug print must come FIRST
import groq
print("🚩 runtime debug: groq package version =", getattr(groq, "__version__", "unknown"))

# 🔥 Must come AFTER the groq version print
from groq import Groq

import src.utils.config as config


class LLMClient:
    def __init__(self, model_name=None):
        self.api_key = config.GROQ_API_KEY
        if not self.api_key:
            raise ValueError("GROQ_API_KEY is missing in .env file")

        self.client = Groq(api_key=self.api_key)
        # self.client = Groq(
        #  api_key=self.api_key,
        #   http_client=None   # <--- IMPORTANT PATCH
        #     )

        self.model = model_name or config.GROQ_MODEL

    def generate(self, messages):
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7,
                max_tokens=500
            )
            
            content = response.choices[0].message.content
            
            if not content or content.strip() == "":
                print(f"⚠️  LLM returned empty content. Response object: {response}")
            
            return content or ""

        except Exception as e:
            print(f"❌ Error in LLM.generate: {e}")
            raise
