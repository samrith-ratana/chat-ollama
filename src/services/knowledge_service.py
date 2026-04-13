import sqlite3
import hashlib
from datetime import datetime
from typing import List, Dict, Optional, Tuple

class KnowledgeService:
    """Service to manage knowledge base storage and retrieval"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self._init_db()
        
    def _init_db(self):
        """Initialize database schema"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Documents table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS documents (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                content TEXT NOT NULL,
                category TEXT,
                created_at TEXT,
                updated_at TEXT
            )
        ''')
        
        # Tags table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tags (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                document_id TEXT NOT NULL,
                tag TEXT NOT NULL,
                FOREIGN KEY (document_id) REFERENCES documents(id),
                UNIQUE(document_id, tag)
            )
        ''')
        
        # Search index
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS search_index (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                document_id TEXT NOT NULL,
                word TEXT NOT NULL,
                frequency INTEGER DEFAULT 1,
                FOREIGN KEY (document_id) REFERENCES documents(id),
                UNIQUE(document_id, word)
            )
        ''')
        
        conn.commit()
        conn.close()
        
    def add_document(self, title: str, content: str, category: str = "general", 
                    tags: Optional[List[str]] = None) -> str:
        """Add document to KB"""
        doc_id = hashlib.md5(f"{title}{datetime.now().isoformat()}".encode()).hexdigest()
        now = datetime.now().isoformat()
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            cursor.execute('''
                INSERT INTO documents (id, title, content, category, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (doc_id, title, content, category, now, now))
            
            if tags:
                for tag in tags:
                    cursor.execute('INSERT OR IGNORE INTO tags (document_id, tag) VALUES (?, ?)', (doc_id, tag))
            
            self._index_document(cursor, doc_id, content)
            conn.commit()
            return doc_id
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
            
    def _index_document(self, cursor, doc_id: str, content: str):
        """Build simple inverted index"""
        words = content.lower().split()
        word_freq = {}
        for word in words:
            word = ''.join(c for c in word if c.isalnum() or c in '-_')
            if len(word) > 2:
                word_freq[word] = word_freq.get(word, 0) + 1
                
        for word, freq in word_freq.items():
            cursor.execute('''
                INSERT OR REPLACE INTO search_index (document_id, word, frequency)
                VALUES (?, ?, ?)
            ''', (doc_id, word, freq))
            
    def search(self, query: str, limit: int = 5) -> List[Dict]:
        """Keyword-based search"""
        query_words = [w.lower() for w in query.split() if len(w) > 2]
        if not query_words:
            return []
            
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        placeholders = ','.join('?' * len(query_words))
        sql = f'''
            SELECT d.id, d.title, d.content, d.category, SUM(si.frequency) as score
            FROM documents d
            JOIN search_index si ON d.id = si.document_id
            WHERE si.word IN ({placeholders})
            GROUP BY d.id
            ORDER BY score DESC
            LIMIT ?
        '''
        
        cursor.execute(sql, (*query_words, limit))
        results = cursor.fetchall()
        conn.close()
        
        return [{
            'id': r[0], 'title': r[1], 'content': r[2], 
            'category': r[3], 'relevance': r[4]
        } for r in results]
        
    def get_stats(self) -> Dict:
        """KB stats"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM documents')
        doc_count = cursor.fetchone()[0]
        conn.close()
        return {'total_documents': doc_count}

    def list_documents(self, category: Optional[str] = None, limit: int = 100) -> List[Dict]:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        if category:
            cursor.execute('SELECT id, title, content, category FROM documents WHERE category = ? LIMIT ?', (category, limit))
        else:
            cursor.execute('SELECT id, title, content, category FROM documents LIMIT ?', (limit,))
        results = cursor.fetchall()
        conn.close()
        return [{'id': r[0], 'title': r[1], 'content': r[2], 'category': r[3]} for r in results]

    def delete_document(self, doc_id: str) -> bool:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('DELETE FROM documents WHERE id = ?', (doc_id,))
        success = cursor.rowcount > 0
        conn.commit()
        conn.close()
        return success
