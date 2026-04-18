import io
from datetime import datetime, timezone
from typing import Dict, List

from flask import Blueprint, current_app, jsonify, request

api_bp = Blueprint("api", __name__)

# In-memory conversation storage; replace with persistent storage for production.
conversations: Dict[str, List[Dict[str, str]]] = {}

ALLOWED_UPLOAD_EXTENSIONS = {".txt", ".md", ".markdown", ".pdf"}


def get_services():
    """Helper to get initialized services from app config."""
    ollama = current_app.config["OLLAMA_SERVICE"]
    knowledge = current_app.config["KNOWLEDGE_SERVICE"]
    chat = current_app.config["CHAT_SERVICE"]
    return ollama, knowledge, chat


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _parse_bool(value, default: bool) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.strip().lower() in {"1", "true", "yes", "on"}
    return default


def _trim_conversation(conv_id: str):
    max_messages = max(2, int(current_app.config.get("MAX_HISTORY_MESSAGES", 12)) * 2)
    if conv_id in conversations and len(conversations[conv_id]) > max_messages:
        conversations[conv_id] = conversations[conv_id][-max_messages:]


def _parse_int_arg(value, default: int, min_value: int, max_value: int) -> int:
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        return default
    return max(min_value, min(max_value, parsed))


def _extract_text_from_upload(filename: str, file_bytes: bytes) -> str:
    lower_name = filename.lower()
    if lower_name.endswith((".txt", ".md", ".markdown")):
        return file_bytes.decode("utf-8", errors="ignore").strip()

    if lower_name.endswith(".pdf"):
        try:
            from pypdf import PdfReader  # type: ignore
        except Exception as exc:
            raise ValueError(
                "PDF upload requires optional dependency 'pypdf'. Install it or upload .txt/.md files."
            ) from exc

        reader = PdfReader(io.BytesIO(file_bytes))
        text = "\n".join((page.extract_text() or "").strip() for page in reader.pages).strip()
        if not text:
            raise ValueError("Could not extract text from this PDF.")
        return text

    raise ValueError("Unsupported file type. Use .txt, .md, .markdown, or .pdf.")


@api_bp.route("/health", methods=["GET"])
def health():
    ollama, _, _ = get_services()
    if ollama.health_check():
        return jsonify(
            {
                "status": "healthy",
                "api": "running",
                "ollama": "connected",
                "timestamp": _now_iso(),
            }
        ), 200
    return jsonify(
        {
            "status": "unhealthy",
            "api": "running",
            "ollama": "disconnected",
            "timestamp": _now_iso(),
        }
    ), 503


@api_bp.route("/models", methods=["GET"])
def get_models():
    ollama, _, _ = get_services()
    models = ollama.get_models()
    return jsonify({"models": models, "count": len(models), "timestamp": _now_iso()}), 200


@api_bp.route("/chat", methods=["POST"])
def chat():
    data = request.get_json(silent=True) or {}
    message = str(data.get("message", "")).strip()
    if not message:
        return jsonify({"error": "Missing or empty message field"}), 400

    max_message_length = int(current_app.config.get("MAX_MESSAGE_LENGTH", 4000))
    if len(message) > max_message_length:
        return jsonify({"error": f"Message too long (max {max_message_length} characters)"}), 400

    model = str(data.get("model", current_app.config["DEFAULT_MODEL"])).strip()
    if not model:
        model = current_app.config["DEFAULT_MODEL"]

    conv_id = str(data.get("conversation_id", "default")).strip()[:120] or "default"
    use_rag = _parse_bool(data.get("use_rag"), current_app.config["ENABLE_RAG"])
    options = data.get("options") if isinstance(data.get("options"), dict) else None

    if conv_id not in conversations:
        conversations[conv_id] = []

    _, _, chat_service = get_services()
    result = chat_service.process_message(
        message,
        conversations[conv_id],
        model,
        use_rag=use_rag,
        options=options,
    )

    if result["response"] is None:
        return jsonify({"error": "Ollama service unavailable"}), 503

    conversations[conv_id].append({"role": "user", "content": message})
    conversations[conv_id].append({"role": "assistant", "content": result["response"]})
    _trim_conversation(conv_id)

    retrieved_documents = [
        {
            "id": doc.get("id"),
            "title": doc.get("title"),
            "category": doc.get("category"),
            "relevance": doc.get("relevance"),
        }
        for doc in result["retrieved_documents"]
    ]

    return jsonify(
        {
            "conversation_id": conv_id,
            "response": result["response"],
            "model": model,
            "confidence": result.get("confidence", 0.0),
            "retrieved_documents": retrieved_documents,
            "rag_applied": result["rag_applied"],
            "rag_enabled": result["rag_applied"],  # backwards compatibility
            "source_titles": result.get("source_titles", []),
            "timestamp": _now_iso(),
        }
    ), 200


@api_bp.route("/conversation/<conversation_id>", methods=["GET"])
def get_conversation(conversation_id: str):
    history = conversations.get(conversation_id, [])
    return jsonify(
        {
            "conversation_id": conversation_id,
            "messages": history,
            "message_count": len(history),
        }
    ), 200


@api_bp.route("/conversation/<conversation_id>", methods=["DELETE"])
def clear_conversation(conversation_id: str):
    existed = conversation_id in conversations
    conversations.pop(conversation_id, None)
    return jsonify({"conversation_id": conversation_id, "cleared": existed}), 200


@api_bp.route("/knowledge/documents", methods=["POST"])
def add_doc():
    data = request.get_json(silent=True) or {}
    title = str(data.get("title", "")).strip()
    content = str(data.get("content", "")).strip()
    if not title or not content:
        return jsonify({"error": "Missing title or content"}), 400

    _, knowledge, _ = get_services()
    doc_id = knowledge.add_document(
        title,
        content,
        str(data.get("category", "general")).strip() or "general",
        data.get("tags", []),
    )
    return jsonify({"message": "Document added", "id": doc_id}), 201


@api_bp.route("/knowledge/documents", methods=["GET"])
def list_docs():
    _, knowledge, _ = get_services()
    category = request.args.get("category")
    limit = _parse_int_arg(request.args.get("limit", 100), default=100, min_value=1, max_value=500)
    documents = knowledge.list_documents(category=category, limit=limit)
    return jsonify({"documents": documents, "count": len(documents)}), 200


@api_bp.route("/knowledge/documents/<doc_id>", methods=["GET"])
def get_doc(doc_id: str):
    _, knowledge, _ = get_services()
    doc = knowledge.get_document(doc_id)
    if not doc:
        return jsonify({"error": "Document not found"}), 404
    return jsonify(doc), 200


@api_bp.route("/knowledge/documents/<doc_id>", methods=["DELETE"])
def delete_doc(doc_id: str):
    _, knowledge, _ = get_services()
    deleted = knowledge.delete_document(doc_id)
    if not deleted:
        return jsonify({"error": "Document not found"}), 404
    return jsonify({"message": "Document deleted", "id": doc_id}), 200


@api_bp.route("/knowledge/search", methods=["GET"])
def search_knowledge():
    _, knowledge, _ = get_services()
    query = request.args.get("q", "").strip()
    if not query:
        return jsonify({"error": "Missing query parameter 'q'"}), 400

    limit = _parse_int_arg(request.args.get("limit", 5), default=5, min_value=1, max_value=20)
    category = request.args.get("category")
    results = knowledge.search(query, limit=limit, category=category)
    return jsonify({"query": query, "results": results, "count": len(results)}), 200


@api_bp.route("/knowledge/upload-file", methods=["POST"])
def upload_knowledge_file():
    if "file" not in request.files:
        return jsonify({"error": "Missing file upload"}), 400

    file = request.files["file"]
    filename = (file.filename or "").strip()
    if not filename:
        return jsonify({"error": "Invalid file"}), 400

    extension = "." + filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    if extension not in ALLOWED_UPLOAD_EXTENSIONS:
        return jsonify({"error": "Unsupported file type"}), 400

    raw_bytes = file.read()
    if not raw_bytes:
        return jsonify({"error": "Uploaded file is empty"}), 400

    try:
        content = _extract_text_from_upload(filename, raw_bytes)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400

    if not content:
        return jsonify({"error": "No readable content found in file"}), 400

    title = (request.form.get("title") or filename).strip()
    category = (request.form.get("category") or "general").strip() or "general"
    tags_raw = (request.form.get("tags") or "").strip()
    tags = [tag.strip() for tag in tags_raw.split(",") if tag.strip()]

    _, knowledge, _ = get_services()
    doc_id = knowledge.add_document(title=title, content=content, category=category, tags=tags)
    return jsonify({"message": "File uploaded and indexed", "id": doc_id, "title": title}), 201


@api_bp.route("/knowledge/rag-test", methods=["POST"])
def rag_test():
    data = request.get_json(silent=True) or {}
    query = str(data.get("query", "")).strip()
    if not query:
        return jsonify({"error": "Missing query field"}), 400

    _, _, chat_service = get_services()
    context, docs, confidence = chat_service.get_rag_context(query)
    return jsonify(
        {
            "query": query,
            "retrieved_documents": docs,
            "count": len(docs),
            "confidence": confidence,
            "context_preview": context[:800],
        }
    ), 200


@api_bp.route("/knowledge/stats", methods=["GET"])
def knowledge_stats():
    _, knowledge, _ = get_services()
    return jsonify(knowledge.get_stats()), 200
