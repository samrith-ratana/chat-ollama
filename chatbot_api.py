#!/usr/bin/env python3
"""
Flask Web API for Ollama Chatbot with RAG Support
Provides REST endpoints for chat interactions with Retrieval-Augmented Generation
"""

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import requests
from typing import Dict, List, Optional
import json
import os
from knowledge_base import KnowledgeBase, RAGContext

# Get absolute path for static files
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = Flask(__name__, static_folder=BASE_DIR, static_url_path='')
CORS(app)  # Enable CORS for all routes

# Configuration
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
DEFAULT_MODEL = os.getenv("DEFAULT_MODEL", "llama2")
ENABLE_RAG = os.getenv("ENABLE_RAG", "true").lower() == "true"

# In-memory storage for conversations (use database in production)
conversations = {}

# Initialize knowledge base and RAG
kb = KnowledgeBase("knowledge.db")
rag = RAGContext(kb)


class OllamaChatAPI:
    def __init__(self, base_url: str = OLLAMA_BASE_URL):
        self.base_url = base_url
    
    def get_models(self) -> List[str]:
        """Get list of available models"""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            response.raise_for_status()
            models = response.json().get("models", [])
            return [m["name"] for m in models]
        except:
            return []
    
    def chat(self, messages: List[Dict], model: str = DEFAULT_MODEL) -> Optional[str]:
        """Send messages and get response"""
        try:
            url = f"{self.base_url}/api/chat"
            payload = {
                "model": model,
                "messages": messages,
                "stream": False
            }
            
            response = requests.post(url, json=payload, timeout=120)
            response.raise_for_status()
            
            result = response.json()
            return result.get("message", {}).get("content", "")
        except requests.exceptions.ConnectionError:
            return None
        except Exception as e:
            return None


ollama = OllamaChatAPI()


@app.route("/api/health", methods=["GET"])
def health():
    """Health check endpoint"""
    try:
        response = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=2)
        response.raise_for_status()
        return jsonify({"status": "healthy", "message": "Ollama is running"}), 200
    except:
        return jsonify({"status": "unhealthy", "message": "Ollama is not running"}), 503


@app.route("/api/models", methods=["GET"])
def get_models():
    """Get available models"""
    models = ollama.get_models()
    return jsonify({"models": models}), 200


@app.route("/api/chat", methods=["POST"])
def chat():
    """Chat endpoint - send message and get response with optional RAG"""
    try:
        data = request.get_json()
        
        if not data or "message" not in data:
            return jsonify({"error": "Missing 'message' field"}), 400
        
        message = data.get("message", "").strip()
        model = data.get("model", DEFAULT_MODEL)
        conversation_id = data.get("conversation_id", "default")
        use_rag = data.get("use_rag", ENABLE_RAG)
        
        if not message:
            return jsonify({"error": "Message cannot be empty"}), 400
        
        # Initialize conversation if needed
        if conversation_id not in conversations:
            conversations[conversation_id] = []
        
        # Prepare message with RAG if enabled
        final_message = message
        retrieved_docs = []
        
        if use_rag:
            final_message, retrieved_docs = rag.enrich_message(message)
        
        # Add user message to conversation
        conversations[conversation_id].append({
            "role": "user",
            "content": message
        })
        
        # Get response from Ollama
        response_text = ollama.chat(conversations[conversation_id], model)
        
        if response_text is None:
            return jsonify({
                "error": "Failed to get response from Ollama",
                "hint": f"Make sure Ollama is running on {OLLAMA_BASE_URL}"
            }), 503
        
        # Add assistant message
        conversations[conversation_id].append({
            "role": "assistant",
            "content": response_text
        })
        
        return jsonify({
            "conversation_id": conversation_id,
            "model": model,
            "response": response_text,
            "message_count": len(conversations[conversation_id]),
            "rag_enabled": use_rag,
            "retrieved_documents": [
                {
                    "title": doc["title"],
                    "category": doc["category"],
                    "relevance": doc["relevance"]
                } for doc in retrieved_docs
            ] if retrieved_docs else []
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/conversation/<conversation_id>", methods=["GET"])
def get_conversation(conversation_id):
    """Get full conversation history"""
    if conversation_id not in conversations:
        return jsonify({"conversation": []}), 200
    
    return jsonify({"conversation": conversations[conversation_id]}), 200


@app.route("/api/conversation/<conversation_id>", methods=["DELETE"])
def clear_conversation(conversation_id):
    """Clear conversation history"""
    if conversation_id in conversations:
        del conversations[conversation_id]
        return jsonify({"message": "Conversation cleared"}), 200
    
    return jsonify({"message": "Conversation not found"}), 404


# ============================================================================
# Knowledge Base Management Endpoints
# ============================================================================

@app.route("/api/knowledge/stats", methods=["GET"])
def knowledge_stats():
    """Get knowledge base statistics"""
    stats = kb.get_stats()
    return jsonify(stats), 200


@app.route("/api/knowledge/documents", methods=["GET"])
def list_knowledge_documents():
    """List all documents in knowledge base"""
    category = request.args.get("category")
    limit = request.args.get("limit", 100, type=int)
    
    documents = kb.list_documents(category=category, limit=limit)
    
    return jsonify({
        "documents": documents,
        "count": len(documents)
    }), 200


@app.route("/api/knowledge/documents", methods=["POST"])
def add_knowledge_document():
    """Add a new document to knowledge base"""
    try:
        data = request.get_json()
        
        title = data.get("title", "").strip()
        content = data.get("content", "").strip()
        category = data.get("category", "general")
        tags = data.get("tags", [])
        
        if not title or not content:
            return jsonify({"error": "Missing 'title' or 'content'"}), 400
        
        doc_id = kb.add_document(title, content, category, tags)
        
        return jsonify({
            "message": "Document added successfully",
            "document_id": doc_id,
            "title": title
        }), 201
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/knowledge/documents/<doc_id>", methods=["GET"])
def get_knowledge_document(doc_id):
    """Get a specific document by ID"""
    document = kb.get_document(doc_id)
    
    if not document:
        return jsonify({"error": "Document not found"}), 404
    
    return jsonify(document), 200


@app.route("/api/knowledge/documents/<doc_id>", methods=["DELETE"])
def delete_knowledge_document(doc_id):
    """Delete a document from knowledge base"""
    success = kb.delete_document(doc_id)
    
    if not success:
        return jsonify({"error": "Document not found"}), 404
    
    return jsonify({"message": "Document deleted successfully"}), 200


@app.route("/api/knowledge/search", methods=["GET"])
def search_knowledge():
    """Search the knowledge base"""
    query = request.args.get("q", "").strip()
    limit = request.args.get("limit", 5, type=int)
    
    if not query:
        return jsonify({"error": "Missing 'q' parameter"}), 400
    
    results = kb.search(query, limit=limit)
    
    return jsonify({
        "query": query,
        "results": results,
        "count": len(results)
    }), 200


@app.route("/api/knowledge/upload-file", methods=["POST"])
def upload_knowledge_file():
    """Upload a file and add its content to knowledge base"""
    try:
        if 'file' not in request.files:
            return jsonify({"error": "No file provided"}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({"error": "No file selected"}), 400
        
        # Read file content
        content = file.read()
        
        # Try to decode as text
        try:
            text_content = content.decode('utf-8')
        except UnicodeDecodeError:
            return jsonify({"error": "File must be a text file"}), 400
        
        # Get metadata
        title = request.form.get("title") or file.filename
        category = request.form.get("category", "general")
        tags = request.form.getlist("tags")
        
        # Add to knowledge base
        doc_id = kb.add_document(title, text_content, category, tags)
        
        return jsonify({
            "message": "File uploaded successfully",
            "document_id": doc_id,
            "title": title,
            "size": len(text_content)
        }), 201
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/knowledge/rag-test", methods=["POST"])
def test_rag():
    """Test RAG retrieval for a query without calling Ollama"""
    try:
        data = request.get_json()
        query = data.get("query", "").strip()
        
        if not query:
            return jsonify({"error": "Missing 'query' field"}), 400
        
        enriched_message, documents = rag.enrich_message(query)
        
        return jsonify({
            "query": query,
            "enriched_message": enriched_message,
            "retrieved_documents": [
                {
                    "id": doc["id"],
                    "title": doc["title"],
                    "category": doc["category"],
                    "relevance": doc["relevance"],
                    "preview": doc["content"][:200] + "..." if len(doc["content"]) > 200 else doc["content"]
                } for doc in documents
            ]
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500



def not_found(error):
    return jsonify({"error": "Endpoint not found"}), 404


@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Internal server error"}), 500


# Serve web UI
@app.route('/')
def index():
    """Serve the web UI"""
    return send_from_directory(BASE_DIR, 'index.html')


@app.route('/<path:filename>')
def serve_static(filename):
    """Serve static files"""
    # Don't serve /api/* through this route
    if filename.startswith('api/'):
        return jsonify({"error": "Not found"}), 404
    
    # Try to serve the file
    try:
        return send_from_directory(BASE_DIR, filename)
    except:
        # If file not found, serve index.html (for single-page app)
        return send_from_directory(BASE_DIR, 'index.html')


if __name__ == "__main__":
    print("🚀 Starting Ollama Chatbot API with RAG Support...")
    print(f"📡 Ollama URL: {OLLAMA_BASE_URL}")
    print(f"🧠 RAG Enabled: {ENABLE_RAG}")
    print("📖 API Documentation at: http://localhost:5000/api/health")
    print("\n📝 Chat Endpoints:")
    print("  GET  /api/health                    - Health check")
    print("  GET  /api/models                    - List available models")
    print("  POST /api/chat                      - Send message with optional RAG")
    print("  GET  /api/conversation/<conv_id>   - Get conversation history")
    print("  DELETE /api/conversation/<conv_id> - Clear conversation")
    print("\n🧠 Knowledge Base & RAG Endpoints:")
    print("  GET    /api/knowledge/stats              - KB statistics")
    print("  GET    /api/knowledge/documents         - List all documents")
    print("  POST   /api/knowledge/documents         - Add new document")
    print("  GET    /api/knowledge/documents/<id>    - Get specific document")
    print("  DELETE /api/knowledge/documents/<id>    - Delete document")
    print("  GET    /api/knowledge/search            - Search knowledge base")
    print("  POST   /api/knowledge/upload-file       - Upload file to KB")
    print("  POST   /api/knowledge/rag-test          - Test RAG retrieval")
    print("\n")
    app.run(debug=True, host="0.0.0.0", port=5000)
