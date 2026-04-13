# RAG System & Knowledge Base Guide

## Overview

The Ollama Chatbot now includes a complete **Retrieval-Augmented Generation (RAG)** system that allows the chatbot to reference custom knowledge bases when answering questions. This enables the chatbot to provide accurate, context-aware responses based on your specific documents.

## Features

### 1. **Knowledge Base Management**
- Add documents via web form
- Upload text and markdown files
- Organize documents by category
- Tag documents for easy organization
- Full-text search

### 2. **Semantic Search**
- Keyword-based retrieval
- Relevance scoring
- Quick document lookup

### 3. **RAG Integration**
- Automatic context injection into prompts
- Background document retrieval
- Conversation memory
- Multi-model support

### 4. **Admin Dashboard**
- Beautiful web-based management interface
- Document browser with categories
- File upload functionality
- Search and discovery tools
- Statistics and analytics

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                       Chat Interface                         │
│                       (index.html)                           │
└────────────────────────────┬────────────────────────────────┘
                             │
                    ┌────────▼────────┐
                    │  Flask API      │
                    │ (chatbot_api.py)│
                    └────────┬────────┘
                             │
                ┌────────────┼────────────┐
                │                        │
        ┌───────▼──────┐        ┌──────▼────────┐
        │   Ollama     │        │ Knowledge Base│
        │   LLM Model  │        │  (SQLite DB)  │
        └──────────────┘        │  (search idx) │
                                └───────────────┘
```

## API Endpoints

### Chat Endpoints

**POST /api/chat**
Send a message with optional RAG
```json
{
  "message": "What is Python?",
  "model": "llama2",
  "conversation_id": "default",
  "use_rag": true
}
```

Response:
```json
{
  "conversation_id": "default",
  "model": "llama2",
  "response": "Python is a programming language...",
  "rag_enabled": true,
  "retrieved_documents": [
    {
      "title": "Python Basics",
      "category": "tutorials",
      "relevance": 45
    }
  ]
}
```

### Knowledge Base Endpoints

**GET /api/knowledge/stats**
Get KB statistics
```json
{
  "total_documents": 15,
  "total_indexed_words": 1250,
  "categories": {
    "FAQ": 5,
    "Documentation": 7,
    "Tutorials": 3
  }
}
```

**GET /api/knowledge/documents**
List all documents
```json
{
  "documents": [
    {
      "id": "doc_123",
      "title": "Getting Started",
      "content": "...",
      "category": "Tutorials",
      "created_at": "2024-01-15T10:30:00",
      "updated_at": "2024-01-15T10:30:00"
    }
  ],
  "count": 5
}
```

**POST /api/knowledge/documents**
Add a new document
```json
{
  "title": "API Documentation",
  "content": "This is the content...",
  "category": "Documentation",
  "tags": ["api", "reference"]
}
```

**DELETE /api/knowledge/documents/{doc_id}**
Delete a document

**GET /api/knowledge/search?q=python&limit=5**
Search KB
```json
{
  "query": "python",
  "results": [
    {
      "id": "doc_123",
      "title": "Python Tutorial",
      "content": "...",
      "category": "Tutorials",
      "relevance": 85
    }
  ],
  "count": 1
}
```

**POST /api/knowledge/upload-file**
Upload a file
- Multipart form data
- Supports: .txt, .md, .pdf
- Optional: title, category

**POST /api/knowledge/rag-test**
Test RAG retrieval without calling Ollama
```json
{
  "query": "What is Python?"
}
```

## Usage Guide

### 1. Access Admin Dashboard

Navigate to:
```
http://localhost:5000/admin.html
```

### 2. Add Documents

#### Method A: Web Form
1. Click "➕ Add Document" tab
2. Enter title and content
3. Set category (e.g., "FAQ", "Documentation")
4. Add tags (optional)
5. Click "Add Document"

#### Method B: Upload File
1. Click "📤 Upload File" tab
2. Select a .txt or .md file
3. Set title (optional) and category
4. Click "Upload File"

#### Method C: API Call
```bash
curl -X POST http://localhost:5000/api/knowledge/documents \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Python Basics",
    "content": "Python is a programming language...",
    "category": "Tutorials",
    "tags": ["python", "programming"]
  }'
```

### 3. Search Knowledge Base

**Via Admin Dashboard:**
1. Click "🔍 Search" tab
2. Enter your search query
3. Click "Search"
4. View relevance scores and previews

**Via API:**
```bash
curl "http://localhost:5000/api/knowledge/search?q=python&limit=5"
```

### 4. Chat with RAG

1. Open http://localhost:5000
2. Ensure "RAG" checkbox is checked
3. Type your question
4. Bot will automatically search KB and use relevant documents
5. Retrieved documents appear below the response

### 5. View Statistics

1. Click "📊 Overview" tab
2. See total documents, indexed words, categories
3. Click "Refresh Stats" to update

### 6. Manage Documents

**Browse Documents:**
1. Click "📖 Browse" tab
2. Filter by category
3. View document cards
4. Click "View" for full content or "Delete" to remove

## Configuration

### Environment Variables

```bash
# API Configuration
OLLAMA_BASE_URL=http://localhost:11434
DEFAULT_MODEL=llama2

# RAG Configuration
ENABLE_RAG=true
KNOWLEDGE_DB_PATH=knowledge.db
```

### Flask Configuration

To run with specific settings:

```bash
# Development mode
FLASK_ENV=development python chatbot_api.py

# Production mode
FLASK_ENV=production python chatbot_api.py

# Custom port
python chatbot_api.py --port 8000
```

## Knowledge Base Schema

### Documents Table
```sql
CREATE TABLE documents (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    category TEXT,
    created_at TEXT,
    updated_at TEXT
);
```

### Search Index Table
```sql
CREATE TABLE search_index (
    id INTEGER PRIMARY KEY,
    document_id TEXT,
    word TEXT NOT NULL,
    frequency INTEGER,
    FOREIGN KEY (document_id) REFERENCES documents(id)
);
```

### Tags Table
```sql
CREATE TABLE tags (
    id INTEGER PRIMARY KEY,
    document_id TEXT,
    tag TEXT NOT NULL,
    FOREIGN KEY (document_id) REFERENCES documents(id)
);
```

## RAG Pipeline

### How RAG Works

1. **User Query Received**
   ```
   User: "What is machine learning?"
   ```

2. **Knowledge Base Search**
   - Query is split into keywords
   - Search index is queried for matching documents
   - Documents ranked by relevance

3. **Context Injection**
   ```
   # Relevant Information:
   
   ## Machine Learning Basics
   Machine learning is a subset of artificial intelligence...
   
   ## Applications of ML
   ML is used in recommendation systems...
   
   User Question: What is machine learning?
   ```

4. **Model Response**
   - Enriched prompt sent to Ollama
   - Model generates response with context
   - Retrieved documents metadata returned

5. **Response Display**
   - Bot response shown in chat
   - Source documents listed below
   - Relevance scores displayed

### Relevance Scoring

Documents are scored based on:
- **Word Frequency**: How often query words appear
- **Recency**: Recently added documents ranked higher
- **Exact Matches**: Exact phrase matches score highest

## Best Practices

### 1. Document Organization

✅ **Good:**
- Clear, descriptive titles
- Logical categories
- Relevant tags
- Well-structured content

❌ **Avoid:**
- Very long documents (split them)
- Missing categories
- Vague or generic titles

### 2. Knowledge Base Content

✅ **Recommended:**
- FAQs and common questions
- Documentation
- Tutorials and guides
- Company policies
- Product specifications

### 3. RAG Toggle

- **Enable for:** General knowledge, documentation queries
- **Disable for:** Creative writing, opinion-based questions
- **Default:** Enabled

### 4. Model Selection

- **llama2**: Good balance, fast
- **mistral**: Faster, good quality
- **neural-chat**: Chat-optimized
- **falcon**: High quality, slower

## Troubleshooting

### KB Not Retrieving Documents

**Issue:** RAG enabled but no documents found

**Solutions:**
1. Check if documents are in KB (Admin → Overview)
2. Search KB with simple keywords (Admin → Search)
3. Verify document content is indexed
4. Check relevance scores

### Search Returns No Results

**Issue:** Search query returns empty

**Solutions:**
1. Try simpler search terms
2. Check document categories (Admin → Browse)
3. Verify documents were added successfully
4. Use API endpoint: `/api/knowledge/search?q=term`

### API Connection Error

**Issue:** "Cannot connect to API"

**Solutions:**
1. Start Flask API: `python chatbot_api.py`
2. Check port 5000 is available
3. Verify CORS is enabled
4. Check browser console for errors

### Ollama Not Found

**Issue:** "Ollama is not running"

**Solutions:**
1. Start Ollama: `ollama serve`
2. Verify Ollama URL in config
3. Check `http://localhost:11434/api/tags`
4. Ensure model is installed: `ollama pull llama2`

## Advanced Usage

### Python Client with RAG

```python
from example_client import OllamaChatClient

client = OllamaChatClient()

# Search KB first
# (In production, implement this in client)
query = "Tell me about Python"
response = client.chat(query)

print(response)
```

### Bulk Upload Documents

```python
from knowledge_base import KnowledgeBase

kb = KnowledgeBase()

# Add multiple documents
documents = [
    ("Python Basics", "Python is...", "Tutorials"),
    ("API Reference", "The API ...", "Documentation"),
]

for title, content, category in documents:
    doc_id = kb.add_document(title, content, category)
    print(f"Added: {title} ({doc_id})")
```

### Custom RAG Pipeline

```python
from knowledge_base import KnowledgeBase, RAGContext

kb = KnowledgeBase()
rag = RAGContext(kb, max_context_length=3000)

# Get enriched message
query = "What is AI?"
enriched, docs = rag.enrich_message(query)

# Use enriched message with Ollama
# response = ollama.chat([{"role": "user", "content": enriched}])
```

## Database Backup

### Backup Knowledge Base

```bash
# Copy database file
cp knowledge.db knowledge.db.backup

# Export as JSON
sqlite3 knowledge.db ".mode json" ".output backup.json" "SELECT * FROM documents;"
```

### Restore Knowledge Base

```bash
# Restore from backup
cp knowledge.db.backup knowledge.db
```

## Performance Tips

1. **Indexing**: Documents are indexed automatically
2. **Search**: Limit results to top 5-10 documents
3. **Context Length**: Keep max context under 2000 tokens
4. **Batch Operations**: Upload multiple files at once
5. **Database**: Keep knowledge.db under 100MB for optimal performance

## Limitations

- **File Types**: Currently supports .txt, .md, .pdf (text extraction)
- **Context Window**: Max 2000 tokens per query (configurable)
- **Search**: Simple keyword-based (no semantic embeddings yet)
- **Storage**: SQLite DB (can migrate to PostgreSQL for scale)

## Future Enhancements

- [ ] Vector embeddings (OpenAI, Ollama embeddings)
- [ ] Semantic similarity search
- [ ] PDF text extraction
- [ ] Document versioning
- [ ] CRUD operations on documents
- [ ] User-based knowledge bases
- [ ] Document access controls
- [ ] Analytics dashboard
- [ ] Export to CSV/JSON
- [ ] Scheduled crawler for web content

## License & Attribution

This RAG system is part of the Ollama Chatbot project.
Feel free to extend and customize for your needs.
