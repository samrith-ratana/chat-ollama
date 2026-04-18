from typing import Any, Dict, List, Optional, Tuple

from .knowledge_service import KnowledgeService
from .ollama_service import OllamaService


class ChatService:
    """Service to handle chat operations and customer-support optimized RAG."""

    def __init__(
        self,
        ollama: OllamaService,
        knowledge: KnowledgeService,
        max_context_length: int = 2000,
        num_docs: int = 3,
        max_history_messages: int = 12,
        min_relevance_score: float = 2.0,
    ):
        self.ollama = ollama
        self.knowledge = knowledge
        self.max_context_length = max_context_length
        self.num_docs = num_docs
        self.max_history_messages = max_history_messages
        self.min_relevance_score = min_relevance_score

    def _system_prompt(self, has_context: bool) -> str:
        kb_policy = (
            "Use the provided knowledge base context as the source of truth for company-specific details."
            if has_context
            else "No verified knowledge-base context is available for this turn."
        )
        return (
            "You are a customer support assistant. Respond clearly, politely, and actionably. "
            "Prioritize solving the customer's problem quickly.\n"
            "Rules:\n"
            "1. Do not invent company policies, pricing, timelines, or guarantees.\n"
            "2. If information is missing, say so plainly and ask one focused follow-up question.\n"
            "3. Prefer short steps and concrete next actions.\n"
            "4. If the issue requires an agent, suggest escalation with needed details.\n"
            f"5. {kb_policy}\n"
            "6. Keep responses concise and customer-friendly."
        )

    def _trim_history(self, history: List[Dict[str, str]]) -> List[Dict[str, str]]:
        if self.max_history_messages <= 0:
            return []
        return history[-self.max_history_messages :]

    def _calculate_confidence(self, docs: List[Dict]) -> float:
        if not docs:
            return 0.0
        top_score = float(docs[0].get("relevance", 0))
        avg_score = sum(float(doc.get("relevance", 0)) for doc in docs) / len(docs)
        confidence = min(1.0, (top_score * 0.08) + (avg_score * 0.03))
        return round(confidence, 3)

    def get_rag_context(self, query: str) -> Tuple[str, List[Dict], float]:
        """Retrieve and format relevant KB context for a query."""
        docs = self.knowledge.search(query, limit=self.num_docs)
        if not docs:
            return "", [], 0.0

        qualified_docs = [doc for doc in docs if float(doc.get("relevance", 0.0)) >= self.min_relevance_score]
        if not qualified_docs and docs:
            qualified_docs = docs[:1]

        context_parts = ["# Retrieved Knowledge Base Context\n"]
        current_length = len(context_parts[0])
        included_docs: List[Dict] = []

        for idx, doc in enumerate(qualified_docs, start=1):
            snippet = (doc.get("content", "") or "").strip()
            snippet = snippet[:1200]
            doc_text = (
                f"\n[Source {idx}] Title: {doc.get('title', 'Untitled')}\n"
                f"Category: {doc.get('category', 'general')}\n"
                f"Relevance: {doc.get('relevance', 0)}\n"
                f"Content:\n{snippet}\n"
            )
            if current_length + len(doc_text) > self.max_context_length:
                break
            context_parts.append(doc_text)
            current_length += len(doc_text)
            included_docs.append(doc)

        confidence = self._calculate_confidence(included_docs)
        return "".join(context_parts), included_docs, confidence

    def process_message(
        self,
        message: str,
        history: List[Dict[str, str]],
        model: str,
        use_rag: bool = True,
        options: Optional[Dict[str, Any]] = None,
    ) -> Dict:
        """Process a user message with optional RAG and support-style behavior."""
        retrieved_docs: List[Dict] = []
        confidence = 0.0
        rag_context = ""

        if use_rag:
            rag_context, retrieved_docs, confidence = self.get_rag_context(message)

        final_message = message
        if rag_context:
            final_message = (
                f"{rag_context}\n\nCustomer Message:\n{message}\n\n"
                "Use the context when relevant. If unclear, ask one clarifying question."
            )

        api_messages: List[Dict[str, str]] = [
            {"role": "system", "content": self._system_prompt(bool(rag_context))}
        ]
        api_messages.extend(self._trim_history(history))
        api_messages.append({"role": "user", "content": final_message})

        response_text = self.ollama.chat(api_messages, model, options=options)
        if not response_text:
            return {
                "response": None,
                "retrieved_documents": retrieved_docs,
                "rag_applied": use_rag and len(retrieved_docs) > 0,
                "confidence": confidence,
            }

        return {
            "response": response_text.strip(),
            "retrieved_documents": retrieved_docs,
            "rag_applied": use_rag and len(retrieved_docs) > 0,
            "confidence": confidence,
            "source_titles": [doc.get("title") for doc in retrieved_docs if doc.get("title")],
        }
