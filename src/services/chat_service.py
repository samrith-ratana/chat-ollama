from typing import List, Dict, Tuple, Optional
from .ollama_service import OllamaService
from .knowledge_service import KnowledgeService

class ChatService:
    """Service to handle chat operations and RAG integration"""
    
    def __init__(self, ollama: OllamaService, knowledge: KnowledgeService, 
                 max_context_length: int = 2000, num_docs: int = 3):
        self.ollama = ollama
        self.knowledge = knowledge
        self.max_context_length = max_context_length
        self.num_docs = num_docs
        
    def get_rag_context(self, query: str) -> Tuple[str, List[Dict]]:
        """Retrieve context from KB for a query"""
        docs = self.knowledge.search(query, limit=self.num_docs)
        if not docs:
            return "", []
            
        context_parts = ["# Relevant Information:\n"]
        current_length = 0
        for doc in docs:
            if doc.get('relevance', 0) == 0:
                continue
            doc_text = f"\n## {doc['title']}\n{doc['content']}\n"
            if current_length + len(doc_text) > self.max_context_length:
                break
            context_parts.append(doc_text)
            current_length += len(doc_text)
            
        return "".join(context_parts), docs

    def process_message(self, message: str, history: List[Dict[str, str]], 
                        model: str, use_rag: bool = True) -> Dict:
        """Process user message, apply RAG if needed, and get response"""
        retrieved_docs = []
        final_prompt_message = message
        
        if use_rag:
            context, retrieved_docs = self.get_rag_context(message)
            if context:
                final_prompt_message = f"{context}\n\nUser Question: {message}"
        
        # Prepare messages for Ollama (history + current enriched message)
        api_messages = history + [{"role": "user", "content": final_prompt_message}]
        
        response_text = self.ollama.chat(api_messages, model)
        
        return {
            "response": response_text,
            "retrieved_documents": retrieved_docs,
            "rag_applied": use_rag and len(retrieved_docs) > 0
        }
