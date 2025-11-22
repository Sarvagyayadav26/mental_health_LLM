import json
import os
import src.utils.config as config
from datetime import datetime

class ChatHistory:
    def __init__(self, path: str = None):
        self.path = path or config.CHAT_HISTORY_PATH
        os.makedirs(os.path.dirname(self.path), exist_ok=True)
        self._messages = []
        self.load()

    def add_user(self, text: str):
        self._messages.append({"role": "user", "text": text, "time": datetime.utcnow().isoformat()})
        self.save()

    def add_assistant(self, text: str):
        self._messages.append({"role": "assistant", "text": text, "time": datetime.utcnow().isoformat()})
        self.save()

    def last_n(self, n=6):
        return self._messages[-n:]

    def save(self):
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(self._messages, f, ensure_ascii=False, indent=2)

    def load(self):
        if os.path.exists(self.path):
            try:
                with open(self.path, "r", encoding="utf-8") as f:
                    self._messages = json.load(f)
            except Exception:
                self._messages = []