#!/usr/bin/env python3
"""
Example Python client for Ollama Chatbot API
Shows how to integrate the API into your applications
"""

import requests
import json
from typing import Optional, List, Dict

class OllamaChatClient:
    """Simple client for Ollama Chatbot API"""
    
    def __init__(self, api_url: str = "http://localhost:5000/api", model: str = "llama2"):
        self.api_url = api_url
        self.model = model
        self.conversation_id = "python_client"
    
    def is_running(self) -> bool:
        """Check if API is running"""
        try:
            response = requests.get(f"{self.api_url}/health", timeout=2)
            return response.status_code == 200
        except:
            return False
    
    def get_models(self) -> List[str]:
        """Get available models"""
        try:
            response = requests.get(f"{self.api_url}/models")
            data = response.json()
            return data.get("models", [])
        except Exception as e:
            print(f"Error fetching models: {e}")
            return []
    
    def chat(self, message: str) -> Optional[str]:
        """Send message and get response"""
        try:
            response = requests.post(
                f"{self.api_url}/chat",
                json={
                    "message": message,
                    "model": self.model,
                    "conversation_id": self.conversation_id
                },
                timeout=120
            )
            
            if response.status_code == 200:
                data = response.json()
                return data.get("response")
            else:
                print(f"Error: {response.json().get('error', 'Unknown error')}")
                return None
                
        except requests.exceptions.Timeout:
            print("Request timed out - model is thinking...")
            return None
        except Exception as e:
            print(f"Error: {e}")
            return None
    
    def get_conversation(self) -> List[Dict]:
        """Get conversation history"""
        try:
            response = requests.get(f"{self.api_url}/conversation/{self.conversation_id}")
            data = response.json()
            return data.get("conversation", [])
        except Exception as e:
            print(f"Error fetching conversation: {e}")
            return []
    
    def clear_conversation(self) -> bool:
        """Clear conversation history"""
        try:
            response = requests.delete(f"{self.api_url}/conversation/{self.conversation_id}")
            return response.status_code == 200
        except Exception as e:
            print(f"Error clearing conversation: {e}")
            return False
    
    def set_model(self, model: str):
        """Change the model"""
        self.model = model
    
    def set_conversation(self, conversation_id: str):
        """Switch to different conversation"""
        self.conversation_id = conversation_id


# Example usage
def main():
    print("🤖 Ollama Chatbot Client Example\n")
    
    # Initialize client
    client = OllamaChatClient()
    
    # Check if API is running
    if not client.is_running():
        print("❌ API is not running. Start it with: python chatbot_api.py")
        return
    
    print("✓ Connected to API\n")
    
    # Get available models
    models = client.get_models()
    print(f"Available models: {', '.join(models)}\n")
    
    # Example 1: Simple chat
    print("📝 Example 1: Simple Chat")
    print("-" * 50)
    response = client.chat("What is Python?")
    if response:
        print(f"Bot: {response}\n")
    
    # Example 2: Follow-up question (maintains context)
    print("📝 Example 2: Follow-up (Context Maintained)")
    print("-" * 50)
    response = client.chat("Can you give me an example of how to use it?")
    if response:
        print(f"Bot: {response}\n")
    
    # Example 3: Change model
    print("📝 Example 3: Change Model")
    print("-" * 50)
    client.set_model("mistral")
    print(f"Model changed to: {client.model}")
    response = client.chat("What is machine learning?")
    if response:
        print(f"Bot: {response}\n")
    
    # Example 4: View conversation history
    print("📝 Example 4: Conversation History")
    print("-" * 50)
    history = client.get_conversation()
    print(f"Total messages: {len(history)}\n")
    for i, msg in enumerate(history, 1):
        role = "📤" if msg["role"] == "user" else "📥"
        content = msg["content"][:100] + "..." if len(msg["content"]) > 100 else msg["content"]
        print(f"{i}. {role} {msg['role'].upper()}: {content}")
    
    print()
    
    # Example 5: Multiple conversations
    print("📝 Example 5: Multiple Conversations")
    print("-" * 50)
    client.set_conversation("conversation_1")
    client.set_model("llama2")
    response1 = client.chat("Tell me about AI")
    
    client.set_conversation("conversation_2")
    response2 = client.chat("What is the weather?")
    
    print("✓ Created 2 separate conversations")
    print(f"  Conversation 1 has {len(client.get_conversation())} messages")
    
    client.set_conversation("conversation_1")
    print(f"  Conversation 1 has {len(client.get_conversation())} messages")
    
    print()
    
    # Example 6: Clear conversation
    print("📝 Example 6: Clear Conversation")
    print("-" * 50)
    client.clear_conversation()
    print(f"Cleared. Messages remaining: {len(client.get_conversation())}\n")


if __name__ == "__main__":
    main()
