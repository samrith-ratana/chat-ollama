from flask import Blueprint, request, jsonify, current_app, send_from_directory
from ..services.ollama_service import OllamaService
from ..services.knowledge_service import KnowledgeService
from ..services.chat_service import ChatService
import os

api_bp = Blueprint('api', __name__)

# Global storage (in-memory for simple implementation, move to DB later)
conversations = {}

def get_services():
    """Helper to get initialized services from app config"""
    ollama = current_app.config['OLLAMA_SERVICE']
    knowledge = current_app.config['KNOWLEDGE_SERVICE']
    chat = current_app.config['CHAT_SERVICE']
    return ollama, knowledge, chat

@api_bp.route("/health", methods=["GET"])
def health():
    ollama, _, _ = get_services()
    models = ollama.get_models()
    if models is not None:
        return jsonify({"status": "healthy", "ollama": "connected"}), 200
    return jsonify({"status": "unhealthy", "ollama": "disconnected"}), 503

@api_bp.route("/models", methods=["GET"])
def get_models():
    ollama, _, _ = get_services()
    models = ollama.get_models()
    return jsonify({"models": models}), 200

@api_bp.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    if not data or "message" not in data:
        return jsonify({"error": "Missing message field"}), 400
        
    message = data.get("message", "").strip()
    model = data.get("model", current_app.config['DEFAULT_MODEL'])
    conv_id = data.get("conversation_id", "default")
    use_rag = data.get("use_rag", current_app.config['ENABLE_RAG'])
    
    if conv_id not in conversations:
        conversations[conv_id] = []
        
    _, _, chat_service = get_services()
    
    # Process message with history
    result = chat_service.process_message(
        message, 
        conversations[conv_id], 
        model, 
        use_rag=use_rag
    )
    
    if result["response"] is None:
        return jsonify({"error": "Ollama service unavailable"}), 503
        
    # Update local history
    conversations[conv_id].append({"role": "user", "content": message})
    conversations[conv_id].append({"role": "assistant", "content": result["response"]})
    
    return jsonify({
        "conversation_id": conv_id,
        "response": result["response"],
        "retrieved_documents": [
            {"title": doc["title"], "relevance": doc["relevance"]} 
            for doc in result["retrieved_documents"]
        ],
        "rag_applied": result["rag_applied"]
    }), 200

@api_bp.route("/knowledge/documents", methods=["POST"])
def add_doc():
    data = request.get_json()
    if not data or "title" not in data or "content" not in data:
        return jsonify({"error": "Missing title or content"}), 400
        
    _, knowledge, _ = get_services()
    doc_id = knowledge.add_document(
        data["title"], 
        data["content"], 
        data.get("category", "general"),
        data.get("tags", [])
    )
    return jsonify({"message": "Document added", "id": doc_id}), 201

@api_bp.route("/knowledge/stats", methods=["GET"])
def knowledge_stats():
    _, knowledge, _ = get_services()
    return jsonify(knowledge.get_stats()), 200
