#!/usr/bin/env python3
"""
Knowledge Base Management for RAG System
Handles document storage, embeddings, and semantic search
"""

import os
import json
import sqlite3
from typing import List, Dict, Optional, Tuple
from datetime import datetime
import hashlib

class KnowledgeBase:
    """
    Simple knowledge base for storing and retrieving documents
    Uses SQLite for storage and simple keyword-based retrieval
    """
    
    def __init__(self, db_path: str = "knowledge.db"):
        """Initialize knowledge base with SQLite database"""
        self.db_path = db_path
        self.init_db()
    
    def init_db(self):
        """Initialize database tables"""
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
        
        # Tags table for documents
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tags (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                document_id TEXT NOT NULL,
                tag TEXT NOT NULL,
                FOREIGN KEY (document_id) REFERENCES documents(id),
                UNIQUE(document_id, tag)
            )
        ''')
        
        # Search index (simple inverted index)
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
        """
        Add a document to the knowledge base
        
        Args:
            title: Document title
            content: Document content
            category: Document category
            tags: List of tags for the document
            
        Returns:
            Document ID
        """
        doc_id = hashlib.md5(f"{title}{datetime.now().isoformat()}".encode()).hexdigest()
        now = datetime.now().isoformat()
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Insert document
            cursor.execute('''
                INSERT INTO documents (id, title, content, category, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (doc_id, title, content, category, now, now))
            
            # Add tags
            if tags:
                for tag in tags:
                    cursor.execute('''
                        INSERT OR IGNORE INTO tags (document_id, tag)
                        VALUES (?, ?)
                    ''', (doc_id, tag))
            
            # Index the content
            self._index_document(cursor, doc_id, content)
            
            conn.commit()
            return doc_id
            
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    
    def _index_document(self, cursor, doc_id: str, content: str):
        """Create search index for document content"""
        words = content.lower().split()
        word_freq = {}
        
        # Count word frequencies
        for word in words:
            # Simple cleanup
            word = ''.join(c for c in word if c.isalnum() or c in '-_')
            if len(word) > 2:  # Skip very short words
                word_freq[word] = word_freq.get(word, 0) + 1
        
        # Store in search index
        for word, freq in word_freq.items():
            cursor.execute('''
                INSERT OR REPLACE INTO search_index (document_id, word, frequency)
                VALUES (?, ?, ?)
            ''', (doc_id, word, freq))
    
    def search(self, query: str, limit: int = 5) -> List[Dict]:
        """
        Search for documents using keyword matching
        
        Args:
            query: Search query
            limit: Maximum number of results
            
        Returns:
            List of relevant documents with relevance scores
        """
        query_words = query.lower().split()
        query_words = [w for w in query_words if len(w) > 2]
        
        if not query_words:
            return []
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Find documents that match query words
        placeholders = ','.join('?' * len(query_words))
        sql = f'''
            SELECT DISTINCT d.id, d.title, d.content, d.category,
                   SUM(si.frequency) as relevance_score
            FROM documents d
            LEFT JOIN search_index si ON d.id = si.document_id
            WHERE si.word IN ({placeholders})
            GROUP BY d.id
            ORDER BY relevance_score DESC, d.created_at DESC
            LIMIT ?
        '''
        
        cursor.execute(sql, (*query_words, limit))
        results = cursor.fetchall()
        conn.close()
        
        return [
            {
                'id': r[0],
                'title': r[1],
                'content': r[2],
                'category': r[3],
                'relevance': r[4] or 0
            }
            for r in results
        ]
    
    def get_document(self, doc_id: str) -> Optional[Dict]:
        """Get a specific document by ID"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, title, content, category, created_at, updated_at
            FROM documents
            WHERE id = ?
        ''', (doc_id,))
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return {
                'id': result[0],
                'title': result[1],
                'content': result[2],
                'category': result[3],
                'created_at': result[4],
                'updated_at': result[5]
            }
        return None
    
    def list_documents(self, category: Optional[str] = None, limit: int = 100) -> List[Dict]:
        """List all documents, optionally filtered by category"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if category:
            cursor.execute('''
                SELECT id, title, content, category, created_at, updated_at
                FROM documents
                WHERE category = ?
                ORDER BY created_at DESC
                LIMIT ?
            ''', (category, limit))
        else:
            cursor.execute('''
                SELECT id, title, content, category, created_at, updated_at
                FROM documents
                ORDER BY created_at DESC
                LIMIT ?
            ''', (limit,))
        
        results = cursor.fetchall()
        conn.close()
        
        return [
            {
                'id': r[0],
                'title': r[1],
                'content': r[2],
                'category': r[3],
                'created_at': r[4],
                'updated_at': r[5]
            }
            for r in results
        ]
    
    def delete_document(self, doc_id: str) -> bool:
        """Delete a document from the knowledge base"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Delete related tags and search index entries
            cursor.execute('DELETE FROM tags WHERE document_id = ?', (doc_id,))
            cursor.execute('DELETE FROM search_index WHERE document_id = ?', (doc_id,))
            cursor.execute('DELETE FROM documents WHERE id = ?', (doc_id,))
            
            conn.commit()
            return cursor.rowcount > 0
        finally:
            conn.close()
    
    def get_stats(self) -> Dict:
        """Get knowledge base statistics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT COUNT(*) FROM documents')
        doc_count = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(DISTINCT word) FROM search_index')
        word_count = cursor.fetchone()[0]
        
        cursor.execute('''
            SELECT category, COUNT(*) as count
            FROM documents
            GROUP BY category
        ''')
        categories = {row[0]: row[1] for row in cursor.fetchall()}
        
        conn.close()
        
        return {
            'total_documents': doc_count,
            'total_indexed_words': word_count,
            'categories': categories
        }


class RAGContext:
    """
    Retrieval-Augmented Generation context manager
    Retrieves relevant documents and formats them for use in prompts
    """
    
    def __init__(self, knowledge_base: KnowledgeBase, max_context_length: int = 2000):
        """
        Initialize RAG context
        
        Args:
            knowledge_base: KnowledgeBase instance
            max_context_length: Maximum length of retrieved context
        """
        self.kb = knowledge_base
        self.max_context_length = max_context_length
    
    def get_context(self, query: str, num_docs: int = 3) -> str:
        """
        Get relevant context for a query
        
        Args:
            query: User query
            num_docs: Number of documents to retrieve
            
        Returns:
            Formatted context string to inject into prompt
        """
        documents = self.kb.search(query, limit=num_docs)
        
        if not documents:
            return ""
        
        context_parts = ["# Relevant Information:\n"]
        current_length = 0
        
        for doc in documents:
            if doc['relevance'] == 0:
                continue
                
            doc_text = f"\n## {doc['title']}\n{doc['content']}\n"
            
            if current_length + len(doc_text) > self.max_context_length:
                break
            
            context_parts.append(doc_text)
            current_length += len(doc_text)
        
        return "".join(context_parts) if len(context_parts) > 1 else ""
    
    def enrich_message(self, user_message: str) -> Tuple[str, List[Dict]]:
        """
        Enrich user message with context from knowledge base
        
        Args:
            user_message: Original user message
            
        Returns:
            Tuple of (enriched_message, retrieved_documents)
        """
        documents = self.kb.search(user_message, limit=3)
        context = self.get_context(user_message)
        
        if context:
            enriched = f"{context}\n\nUser Question: {user_message}"
            return enriched, documents
        
        return user_message, []
