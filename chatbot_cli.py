#!/usr/bin/env python3
"""
Simple CLI Chatbot with Ollama Backend
"""

import requests
import json
from typing import Optional

class OllamaChat:
    def __init__(self, base_url: str = "http://localhost:11434", model: str = "llama2"):
        """
        Initialize Ollama chat client
        
        Args:
            base_url: Ollama server URL
            model: Model name to use (e.g., 'llama2', 'mistral', 'neural-chat')
        """
        self.base_url = base_url
        self.model = model
        self.conversation_history = []
    
    def chat(self, message: str) -> Optional[str]:
        """
        Send a message and get a response from Ollama
        
        Args:
            message: User message
            
        Returns:
            Response from the model
        """
        self.conversation_history.append({"role": "user", "content": message})
        
        try:
            url = f"{self.base_url}/api/chat"
            payload = {
                "model": self.model,
                "messages": self.conversation_history,
                "stream": False
            }
            
            response = requests.post(url, json=payload, timeout=60)
            response.raise_for_status()
            
            result = response.json()
            assistant_message = result.get("message", {}).get("content", "")
            
            self.conversation_history.append({"role": "assistant", "content": assistant_message})
            return assistant_message
            
        except requests.exceptions.ConnectionError:
            return "❌ Error: Cannot connect to Ollama. Make sure Ollama is running on " + self.base_url
        except Exception as e:
            return f"❌ Error: {str(e)}"
    
    def clear_history(self):
        """Clear conversation history"""
        self.conversation_history = []
    
    def set_model(self, model: str):
        """Change the model"""
        self.model = model
        print(f"✓ Model changed to: {model}")


def main():
    """Main CLI interface"""
    print("=" * 60)
    print("🤖 Ollama Chatbot")
    print("=" * 60)
    print("Commands:")
    print("  /quit or /exit  - Exit the chatbot")
    print("  /clear          - Clear conversation history")
    print("  /model <name>   - Change model (e.g., /model mistral)")
    print("=" * 60)
    
    # Initialize chatbot
    chatbot = OllamaChat(model="llama2")
    
    print(f"\n📡 Using model: {chatbot.model}")
    print("Type your message and press Enter...\n")
    
    while True:
        try:
            user_input = input("You: ").strip()
            
            if not user_input:
                continue
            
            # Handle commands
            if user_input.lower() in ["/quit", "/exit"]:
                print("Goodbye! 👋")
                break
            
            if user_input.lower() == "/clear":
                chatbot.clear_history()
                print("✓ Conversation history cleared\n")
                continue
            
            if user_input.lower().startswith("/model"):
                parts = user_input.split(" ", 1)
                if len(parts) == 2:
                    chatbot.set_model(parts[1])
                else:
                    print("Usage: /model <model_name>\n")
                continue
            
            # Get response
            print("\nBot: ", end="", flush=True)
            response = chatbot.chat(user_input)
            print(response + "\n")
            
        except KeyboardInterrupt:
            print("\n\nGoodbye! 👋")
            break
        except Exception as e:
            print(f"Error: {e}\n")


if __name__ == "__main__":
    main()
