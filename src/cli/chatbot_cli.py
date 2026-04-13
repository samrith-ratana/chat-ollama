import requests
import json
import sys
from typing import Optional

class ChatBotCLI:
    def __init__(self, api_url: str = "http://localhost:5000/api"):
        self.api_url = api_url
        self.conversation_id = "cli-session"
        self.model = "llama2"
        self.use_rag = True

    def chat(self, message: str) -> Optional[str]:
        try:
            payload = {
                "message": message,
                "model": self.model,
                "conversation_id": self.conversation_id,
                "use_rag": self.use_rag
            }
            response = requests.post(f"{self.api_url}/chat", json=payload, timeout=120)
            response.raise_for_status()
            result = response.json()
            return result.get("response", "")
        except Exception as e:
            return f"Error: {e}"

    def run(self):
        print("=" * 40)
        print("🤖 Ollama Chatbot CLI")
        print("=" * 40)
        print("Commands: /quit, /clear, /model <name>, /rag <on|off>")
        
        while True:
            try:
                user_input = input("\nYou: ").strip()
                if not user_input: continue
                if user_input.lower() in ["/quit", "/exit"]: break
                
                if user_input.startswith("/model"):
                    self.model = user_input.split(" ", 1)[1]
                    print(f"Model set to {self.model}")
                    continue
                
                if user_input.startswith("/rag"):
                    val = user_input.split(" ", 1)[1].lower()
                    self.use_rag = (val == "on")
                    print(f"RAG is now {'ON' if self.use_rag else 'OFF'}")
                    continue

                print("Bot: ", end="", flush=True)
                response = self.chat(user_input)
                print(response)
            except KeyboardInterrupt:
                break
        print("\nGoodbye!")

if __name__ == "__main__":
    cli = ChatBotCLI()
    cli.run()
