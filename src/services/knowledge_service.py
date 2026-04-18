import hashlib
import re
import sqlite3
from collections import Counter, defaultdict
from datetime import datetime, timezone
from typing import Dict, List, Optional


class KnowledgeService:
    """Service to manage knowledge base storage and retrieval."""

    STOP_WORDS = {
        "the",
        "and",
        "for",
        "that",
        "with",
        "this",
        "you",
        "your",
        "are",
        "was",
        "were",
        "have",
        "has",
        "had",
        "from",
        "into",
        "about",
        "what",
        "when",
        "where",
        "which",
        "will",
        "would",
        "can",
        "could",
        "our",
        "their",
        "them",
        "they",
    }

    def __init__(self, db_path: str):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        """Initialize database schema."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS documents (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                content TEXT NOT NULL,
                category TEXT,
                created_at TEXT,
                updated_at TEXT
            )
            """
        )

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS tags (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                document_id TEXT NOT NULL,
                tag TEXT NOT NULL,
                FOREIGN KEY (document_id) REFERENCES documents(id),
                UNIQUE(document_id, tag)
            )
            """
        )

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS search_index (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                document_id TEXT NOT NULL,
                word TEXT NOT NULL,
                frequency INTEGER DEFAULT 1,
                FOREIGN KEY (document_id) REFERENCES documents(id),
                UNIQUE(document_id, word)
            )
            """
        )
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_search_word ON search_index(word)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_docs_category ON documents(category)")

        conn.commit()
        conn.close()

    def _tokenize(self, text: str) -> List[str]:
        tokens = re.findall(r"[a-z0-9][a-z0-9_-]{1,}", (text or "").lower())
        return [token for token in tokens if len(token) >= 3 and token not in self.STOP_WORDS]

    def add_document(
        self,
        title: str,
        content: str,
        category: str = "general",
        tags: Optional[List[str]] = None,
    ) -> str:
        """Add a new document to the knowledge base and index it."""
        clean_title = (title or "").strip()
        clean_content = (content or "").strip()
        clean_category = (category or "general").strip() or "general"
        clean_tags = sorted({t.strip().lower() for t in (tags or []) if isinstance(t, str) and t.strip()})
        if not clean_title or not clean_content:
            raise ValueError("title and content are required")

        now = datetime.now(timezone.utc).isoformat()
        doc_id = hashlib.md5(f"{clean_title}{now}".encode("utf-8")).hexdigest()

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            cursor.execute(
                """
                INSERT INTO documents (id, title, content, category, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (doc_id, clean_title, clean_content, clean_category, now, now),
            )

            for tag in clean_tags:
                cursor.execute(
                    "INSERT OR IGNORE INTO tags (document_id, tag) VALUES (?, ?)",
                    (doc_id, tag),
                )

            self._index_document(cursor, doc_id, clean_title, clean_content, clean_category, clean_tags)
            conn.commit()
            return doc_id
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def _index_document(
        self,
        cursor: sqlite3.Cursor,
        doc_id: str,
        title: str,
        content: str,
        category: str,
        tags: List[str],
    ):
        """Build a weighted inverted index for search."""
        weighted = Counter()

        for token in self._tokenize(content):
            weighted[token] += 1
        for token in self._tokenize(title):
            weighted[token] += 3
        for token in self._tokenize(category):
            weighted[token] += 2
        for tag in tags:
            for token in self._tokenize(tag):
                weighted[token] += 2

        for word, freq in weighted.items():
            cursor.execute(
                """
                INSERT OR REPLACE INTO search_index (document_id, word, frequency)
                VALUES (?, ?, ?)
                """,
                (doc_id, word, freq),
            )

    def search(self, query: str, limit: int = 5, category: Optional[str] = None) -> List[Dict]:
        """Search documents by weighted keyword relevance."""
        query_terms = self._tokenize(query)
        if not query_terms:
            return []

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        placeholders = ",".join("?" * len(query_terms))
        sql = f"""
            SELECT
                d.id,
                d.title,
                d.content,
                d.category,
                d.created_at,
                d.updated_at,
                COALESCE(SUM(si.frequency), 0) as term_score,
                COUNT(DISTINCT si.word) as matched_terms
            FROM documents d
            JOIN search_index si ON d.id = si.document_id
            WHERE si.word IN ({placeholders})
        """
        params: List[object] = list(query_terms)
        if category:
            sql += " AND d.category = ?"
            params.append(category)
        sql += " GROUP BY d.id"

        cursor.execute(sql, params)
        rows = cursor.fetchall()
        conn.close()

        unique_terms = set(query_terms)
        results: List[Dict] = []
        lowered_query = query.strip().lower()

        for row in rows:
            title_lower = (row[1] or "").lower()
            content_lower = (row[2] or "").lower()
            title_hits = sum(1 for term in unique_terms if term in title_lower)
            phrase_boost = 6 if lowered_query and lowered_query in content_lower else 0
            coverage = float(row[7]) / max(len(unique_terms), 1)
            score = float(row[6]) + (title_hits * 2) + phrase_boost + (coverage * 4)

            results.append(
                {
                    "id": row[0],
                    "title": row[1],
                    "content": row[2],
                    "category": row[3],
                    "created_at": row[4],
                    "updated_at": row[5],
                    "relevance": round(score, 3),
                }
            )

        results.sort(key=lambda d: d["relevance"], reverse=True)
        return results[: max(1, limit)]

    def get_stats(self) -> Dict:
        """Knowledge base statistics."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM documents")
        total_documents = cursor.fetchone()[0]

        cursor.execute("SELECT COALESCE(SUM(frequency), 0) FROM search_index")
        total_indexed_words = cursor.fetchone()[0]

        cursor.execute(
            "SELECT category, COUNT(*) FROM documents GROUP BY category ORDER BY COUNT(*) DESC"
        )
        categories = {row[0] or "general": row[1] for row in cursor.fetchall()}

        conn.close()
        return {
            "total_documents": total_documents,
            "total_indexed_words": total_indexed_words,
            "categories": categories,
        }

    def list_documents(self, category: Optional[str] = None, limit: int = 100) -> List[Dict]:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        if category:
            cursor.execute(
                """
                SELECT id, title, content, category, created_at, updated_at
                FROM documents
                WHERE category = ?
                ORDER BY updated_at DESC
                LIMIT ?
                """,
                (category, limit),
            )
        else:
            cursor.execute(
                """
                SELECT id, title, content, category, created_at, updated_at
                FROM documents
                ORDER BY updated_at DESC
                LIMIT ?
                """,
                (limit,),
            )
        rows = cursor.fetchall()

        doc_ids = [row[0] for row in rows]
        tags_by_doc: Dict[str, List[str]] = defaultdict(list)
        if doc_ids:
            placeholders = ",".join("?" * len(doc_ids))
            cursor.execute(
                f"SELECT document_id, tag FROM tags WHERE document_id IN ({placeholders})",
                doc_ids,
            )
            for document_id, tag in cursor.fetchall():
                tags_by_doc[document_id].append(tag)

        conn.close()

        return [
            {
                "id": row[0],
                "title": row[1],
                "content": row[2],
                "category": row[3],
                "created_at": row[4],
                "updated_at": row[5],
                "tags": tags_by_doc.get(row[0], []),
            }
            for row in rows
        ]

    def get_document(self, doc_id: str) -> Optional[Dict]:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT id, title, content, category, created_at, updated_at
            FROM documents
            WHERE id = ?
            """,
            (doc_id,),
        )
        row = cursor.fetchone()
        if not row:
            conn.close()
            return None

        cursor.execute("SELECT tag FROM tags WHERE document_id = ? ORDER BY tag ASC", (doc_id,))
        tags = [tag_row[0] for tag_row in cursor.fetchall()]
        conn.close()

        return {
            "id": row[0],
            "title": row[1],
            "content": row[2],
            "category": row[3],
            "created_at": row[4],
            "updated_at": row[5],
            "tags": tags,
        }

    def delete_document(self, doc_id: str) -> bool:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("DELETE FROM tags WHERE document_id = ?", (doc_id,))
        cursor.execute("DELETE FROM search_index WHERE document_id = ?", (doc_id,))
        cursor.execute("DELETE FROM documents WHERE id = ?", (doc_id,))
        success = cursor.rowcount > 0

        conn.commit()
        conn.close()
        return success
