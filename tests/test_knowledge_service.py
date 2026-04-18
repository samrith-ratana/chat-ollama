import os
import unittest
import uuid

from src.services.knowledge_service import KnowledgeService


class KnowledgeServiceTests(unittest.TestCase):
    def setUp(self):
        test_tmp_root = os.path.join(os.getcwd(), "data", "test_tmp")
        os.makedirs(test_tmp_root, exist_ok=True)
        self.db_path = os.path.join(test_tmp_root, f"knowledge_{uuid.uuid4().hex}.db")
        self.service = KnowledgeService(self.db_path)

    def tearDown(self):
        if os.path.exists(self.db_path):
            os.remove(self.db_path)

    def test_add_search_and_stats(self):
        self.service.add_document(
            title="Refund Policy",
            content="Customers can request a refund within 30 days of purchase.",
            category="policy",
            tags=["refund", "billing"],
        )
        self.service.add_document(
            title="Shipping Times",
            content="Standard shipping takes 3 to 5 business days.",
            category="logistics",
            tags=["shipping"],
        )

        results = self.service.search("refund within 30 days", limit=5)
        self.assertGreaterEqual(len(results), 1)
        self.assertEqual(results[0]["title"], "Refund Policy")
        self.assertGreater(results[0]["relevance"], 0)

        stats = self.service.get_stats()
        self.assertEqual(stats["total_documents"], 2)
        self.assertGreater(stats["total_indexed_words"], 0)
        self.assertEqual(stats["categories"]["policy"], 1)

    def test_delete_document_removes_it(self):
        doc_id = self.service.add_document(
            title="Temporary Doc",
            content="This document should be deleted.",
            category="temp",
        )
        self.assertIsNotNone(self.service.get_document(doc_id))
        self.assertTrue(self.service.delete_document(doc_id))
        self.assertIsNone(self.service.get_document(doc_id))


if __name__ == "__main__":
    unittest.main()
