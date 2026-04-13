# 🤖 Ollama Chatbot

A complete chatbot solution powered by Ollama with multiple interfaces: CLI, REST API, Web UI, and **RAG (Retrieval-Augmented Generation)** for knowledgebase integration.

## 📋 Prerequisites

- **Python 3.8+** installed
- **Ollama** installed and running on `http://localhost:11434`
  - Download from: https://ollama.ai
  - Run: `ollama serve`

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Start Ollama (in a separate terminal)

```bash
ollama serve
```

Then pull a model:
```bash
ollama pull llama2
```

Available models:
- `llama2` - Meta's Llama 2 (default, 7B params)
- `mistral` - Mistral 7B (fast and capable)
- `neural-chat` - Intel's Neural Chat
- `falcon` - TII Falcon
- `dolphin-mixtral` - Larger model (slower but better)

### 3. Choose Your Interface

---

## 🖥️ Option 1: CLI Chatbot (Simplest)

Interactive terminal-based chat.

```bash
python chatbot_cli.py
```

**Features:**
- Conversation history in one session
- Commands:
  - `/quit` or `/exit` - Exit
  - `/clear` - Clear history
  - `/model <name>` - Change model

**Example:**
```
You: What is Python?
Bot: Python is a programming language...

You: /clear
✓ Conversation history cleared

You: /model mistral
✓ Model changed to: mistral
```

---

## 🌐 Option 2: Web API + Web UI (Recommended)

REST API for programmatic access + Beautiful web interface.

### Start the API Server:

```bash
python chatbot_api.py
```

Server runs on: `http://localhost:5000`

### Open Web UI:

Open [index.html](index.html) in your browser or run:

```bash
# On Windows
start index.html

# On Mac
open index.html

# On Linux
xdg-open index.html
```

**Features:**
- Beautiful gradient UI
- Model selection dropdown
- Real-time chat
- Multiple conversations
- Typing animation

---

## 📡 API Documentation

### Endpoints

#### 1. Health Check
```bash
GET /api/health
```
**Response:**
```json
{
  "status": "healthy",
  "message": "Ollama is running"
}
```

#### 2. Get Available Models
```bash
GET /api/models
```
**Response:**
```json
{
  "models": ["llama2", "mistral", "neural-chat"]
}
```

#### 3. Send Message & Get Reply
```bash
POST /api/chat
Content-Type: application/json

{
  "message": "What is AI?",
  "model": "llama2",
  "conversation_id": "user123"
}
```

**Response:**
```json
{
  "conversation_id": "user123",
  "model": "llama2",
  "response": "AI stands for Artificial Intelligence...",
  "message_count": 2
}
```

#### 4. Get Conversation History
```bash
GET /api/conversation/<conversation_id>
```

#### 5. Clear Conversation
```bash
DELETE /api/conversation/<conversation_id>
```

---

## 🔧 Usage Examples

### Using cURL

```bash
# Send a message
curl -X POST http://localhost:5000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello", "model": "llama2"}'

# Get available models
curl http://localhost:5000/api/models

# Check health
curl http://localhost:5000/api/health
```

### Using Python

```python
import requests
import json

API_URL = "http://localhost:5000/api"

# Send message
response = requests.post(
    f"{API_URL}/chat",
    json={
        "message": "What is machine learning?",
        "model": "mistral",
        "conversation_id": "session1"
    }
)

data = response.json()
print(data["response"])

# Get conversation history
response = requests.get(f"{API_URL}/conversation/session1")
history = response.json()["conversation"]
for msg in history:
    print(f"{msg['role']}: {msg['content']}")
```

### Using JavaScript/Fetch

```javascript
async function chat(message, model = "llama2") {
  const response = await fetch("http://localhost:5000/api/chat", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      message: message,
      model: model,
      conversation_id: "default"
    })
  });
  
  const data = await response.json();
  console.log(data.response);
}

chat("Hello there!");
```

---

## 📁 Project Structure

```
chat-oll/
├── chatbot_cli.py        # CLI interface
├── chatbot_api.py        # REST API server
├── index.html            # Web UI
├── requirements.txt      # Python dependencies
└── README.md            # This file
```

---

## 🎨 Customization

### Change Default Model

**CLI:**
```python
chatbot = OllamaChat(model="mistral")  # Change in line 47
```

**API:**
```python
DEFAULT_MODEL = "mistral"  # Change in line 11
```

### Change Ollama URL

```python
OLLAMA_BASE_URL = "http://192.168.1.100:11434"
```

### Adjust Timeout

In `chatbot_api.py`:
```python
response = requests.post(url, json=payload, timeout=120)  # In seconds
```

---

## 🐛 Troubleshooting

### "Cannot connect to Ollama"
- Make sure Ollama is running: `ollama serve`
- Check if it's on `http://localhost:11434`
- Try: `curl http://localhost:11434/api/tags`

### "Model not found"
- Pull the model: `ollama pull llama2`
- List models: `ollama list`

### API returns 503
- Ollama is not running
- Start it with: `ollama serve`

### Slow responses
- Using a large model (try `mistral` instead of `neural-chat`)
- Check GPU availability
- Increase timeout in the code

---

## 🧠 RAG System (Retrieval-Augmented Generation)

The chatbot now includes a complete **Knowledge Base** with RAG capabilities! Enable the chatbot to answer questions based on your custom documents.

### Quick Start with RAG

1. **Open Admin Dashboard**
   ```
   http://localhost:5000/admin.html
   ```

2. **Add Documents**
   - Click "➕ Add Document"
   - Enter title and content
   - Set category (e.g., "Documentation", "FAQ")
   - Click "Add Document"

3. **Chat with Context**
   - Open http://localhost:5000
   - Ensure "RAG" checkbox is checked
   - Ask questions - bot will use your documents!

### Knowledge Base Features

- 📚 **Add Documents**: Text, markdown, or upload files
- 🔍 **Search**: Full-text search with relevance scoring
- 📖 **Browse**: View all documents by category
- 🏷️ **Organize**: Categories and tags for organization
- 📊 **Analytics**: Statistics about your knowledge base

### RAG API Endpoints

```bash
# Add a document
curl -X POST http://localhost:5000/api/knowledge/documents \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Python Guide",
    "content": "Python is a programming language...",
    "category": "Tutorials"
  }'

# Search knowledge base
curl "http://localhost:5000/api/knowledge/search?q=python"

# Upload a file
curl -F "file=@document.txt" \
  -F "category=Documentation" \
  http://localhost:5000/api/knowledge/upload-file

# Get KB statistics
curl http://localhost:5000/api/knowledge/stats
```

### How RAG Works

```
User Question
     ↓
Search Knowledge Base
     ↓
Retrieve Relevant Documents
     ↓
Inject Context into Prompt
     ↓
Send to Ollama with Enhanced Context
     ↓
Get Accurate, Informed Response
```

### Example RAG Usage

**Without RAG:**
```
User: "What is our API rate limit?"
Bot: "I don't have information about your API..."
```

**With RAG:**
```
User: "What is our API rate limit?"
Bot: "According to our documentation, the API rate limit is 1000 requests per minute..."
Retrieved from: API Documentation [Relevance: 95]
```

### For Complete RAG Documentation

See [RAG_GUIDE.md](RAG_GUIDE.md) for:
- Detailed setup instructions
- All API endpoints
- Configuration options
- Best practices
- Troubleshooting
- Advanced usage

---

## 📊 Performance Tips

| Model | Speed | Quality | VRAM |
|-------|-------|---------|------|
| mistral | ⚡⚡⚡ | ⭐⭐⭐⭐ | 5GB |
| llama2 | ⚡⚡ | ⭐⭐⭐⭐ | 4GB |
| neural-chat | ⚡⚡⭐ | ⭐⭐⭐ | 3GB |
| falcon | ⚡ | ⭐⭐⭐⭐⭐ | 8GB |

**Recommendation:** Start with `mistral` for best speed/quality balance.

---

## 📝 Notes

- Conversations are stored in memory (cleared when server restarts)
- For production: use a real database
- CORS is enabled for all origins (change in `chatbot_api.py` if needed)
- All models run on your local machine - no data sent to external servers

---

## 📄 License

Free to use and modify.

---

## 💡 What's Included

✅ Complete CLI chatbot  
✅ REST API with documentation  
✅ Beautiful web interface  
✅ Multi-conversation support  
✅ Model selection  
✅ Error handling  
✅ Health checks  
✅ **RAG System** with knowledge base  
✅ **Admin Dashboard** for KB management  
✅ **Full-text search** with relevance scoring  
✅ **File upload** for documents  
✅ Multiple endpoints for integration  
✅ Ready for production  

---

## 🚢 Next Steps

1. Try the CLI: `python chatbot_cli.py`
2. Try the Web UI: Open `index.html`
3. Build custom integrations using the API
4. Deploy to production (add database, authentication, etc.)

Enjoy your local AI chatbot! 🤖
#   c h a t - o l l a m a  
 