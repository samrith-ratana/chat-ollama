import os
import unittest
import uuid

from src.services.chat_service import ChatService
from src.services.knowledge_service import KnowledgeService


class FakeOllamaService:
    def __init__(self, response_text="Here is the support answer."):
        self.response_text = response_text
        self.last_messages = None
        self.last_options = None

    def chat(self, messages, model, options=None):
        self.last_messages = messages
        self.last_options = options
        return self.response_text


class ChatServiceTests(unittest.TestCase):
    def setUp(self):
        test_tmp_root = os.path.join(os.getcwd(), "data", "test_tmp")
        os.makedirs(test_tmp_root, exist_ok=True)
        self.db_path = os.path.join(test_tmp_root, f"knowledge_{uuid.uuid4().hex}.db")
        self.knowledge = KnowledgeService(self.db_path)
        self.knowledge.add_document(
            title="Returns and Refunds",
            content="Refunds are available within 30 days with receipt.",
            category="policy",
            tags=["refund"],
        )

    def tearDown(self):
        if os.path.exists(self.db_path):
            os.remove(self.db_path)

    def test_process_message_with_rag(self):
        ollama = FakeOllamaService()
        service = ChatService(ollama=ollama, knowledge=self.knowledge, num_docs=2)

        result = service.process_message(
            message="Can I get a refund?",
            history=[{"role": "user", "content": "Hi"}],
            model="mistral",
            use_rag=True,
            options={"temperature": 0.3},
        )

        self.assertTrue(result["rag_applied"])
        self.assertIsNotNone(result["response"])
        self.assertGreaterEqual(result["confidence"], 0)
        self.assertEqual(ollama.last_messages[0]["role"], "system")
        self.assertIn("Retrieved Knowledge Base Context", ollama.last_messages[-1]["content"])
        self.assertEqual(ollama.last_options, {"temperature": 0.3})

    def test_process_message_handles_model_failure(self):
        ollama = FakeOllamaService(response_text=None)
        service = ChatService(ollama=ollama, knowledge=self.knowledge)
        result = service.process_message(
            message="Hello",
            history=[],
            model="mistral",
            use_rag=False,
        )
        self.assertIsNone(result["response"])


if __name__ == "__main__":
    unittest.main()
