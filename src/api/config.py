import os
from typing import List, Optional

class Config:
    """Configuration management for the chatbot API"""
    
    # API Settings
    API_HOST = os.getenv("API_HOST", "0.0.0.0")
    API_PORT = int(os.getenv("API_PORT", 5000))
    DEBUG = os.getenv("DEBUG", "true").lower() == "true"
    
    # Ollama Settings
    OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    DEFAULT_MODEL = os.getenv("DEFAULT_MODEL", "llama2")
    OLLAMA_REQUEST_TIMEOUT = int(os.getenv("OLLAMA_REQUEST_TIMEOUT", 120))
    
    # RAG Settings
    ENABLE_RAG = os.getenv("ENABLE_RAG", "true").lower() == "true"
    KNOWLEDGE_DB_PATH = os.getenv("KNOWLEDGE_DB_PATH", "knowledge.db")
    MAX_CONTEXT_LENGTH = int(os.getenv("MAX_CONTEXT_LENGTH", 2000))
    NUM_RETRIEVED_DOCS = int(os.getenv("NUM_RETRIEVED_DOCS", 3))
    MIN_RAG_RELEVANCE = float(os.getenv("MIN_RAG_RELEVANCE", 2.0))
    MAX_HISTORY_MESSAGES = int(os.getenv("MAX_HISTORY_MESSAGES", 12))
    MAX_MESSAGE_LENGTH = int(os.getenv("MAX_MESSAGE_LENGTH", 4000))
    
    # Storage Settings
    CONVERSATIONS_DIR = os.getenv("CONVERSATIONS_DIR", "data/conversations")
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

    @staticmethod
    def init_app(app):
        """Perform app-specific initialization"""
        if not os.path.exists(Config.CONVERSATIONS_DIR):
            os.makedirs(Config.CONVERSATIONS_DIR, exist_ok=True)
