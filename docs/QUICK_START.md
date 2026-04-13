# 🚀 Quick Start Guide

Get your Ollama chatbot running in **5 minutes**!

## Step 1: Install Ollama (If Not Already Done)

1. Go to https://ollama.ai
2. Download and install for your OS
3. Open a terminal and run:
   ```bash
   ollama serve
   ```
4. In another terminal, download a model:
   ```bash
   ollama pull llama2
   ```
   
✅ Ollama is ready!

---

## Step 2: Install Python Dependencies

In the `chat-oll` folder:

```bash
pip install -r requirements.txt
```

✅ Dependencies installed!

---

## Step 3: Choose Your Interface

### 🖥️ Option A: CLI Chatbot (Simplest)

**Start with this for quick testing:**

```bash
python chatbot_cli.py
```

Type your messages and chat instantly!

Commands:
- `/clear` - Clear history
- `/model mistral` - Change model
- `/quit` - Exit

---

### 🌐 Option B: Web Interface with RAG (Recommended)

**Beautiful UI + Knowledge Base + Admin Dashboard**

1. **Start the API server:**
   ```bash
   python chatbot_api.py
   ```

2. **Open in your browser:**
   - Chat: http://localhost:5000
   - Admin: http://localhost:5000/admin.html

3. **Add some knowledge:**
   - Go to Admin Dashboard
   - Click "➕ Add Document"
   - Enter title, content, category
   - Click "Add Document"

4. **Chat with your knowledge:**
   - Go to Chat (http://localhost:5000)
   - Ensure "RAG" checkbox is checked
   - Ask questions about your documents
   - Bot will use your knowledge base!

---

## 🧠 RAG System Quick Tips

**What is RAG?** Retrieval-Augmented Generation allows your chatbot to reference custom documents.

### Admin Dashboard Features
- 📊 **Overview** - See knowledge base statistics
- ➕ **Add Document** - Create documents via web form
- 📖 **Browse** - View all documents, filter by category
- 🔍 **Search** - Full-text search with relevance
- 📤 **Upload File** - Upload .txt or .md files

### Quick Example
1. Add a document: "Python is a programming language..."
2. Chat: "Tell me about Python"
3. Bot uses your document to answer!

---

## 🔌 Python API Example

**Start API Server:**
```bash
python chatbot_api.py
```

**Use Python client:**
```bash
python example_client.py
```

**Or curl:**
```bash
curl -X POST http://localhost:5000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello!", "model": "llama2"}'
```

---

## ✅ Checklist

- [ ] Ollama installed and running (`ollama serve`)
- [ ] Model downloaded (`ollama pull llama2`)
- [ ] Python dependencies installed (`pip install -r requirements.txt`)
- [ ] Choose interface and run it
- [ ] Start chatting!

---

## 🆘 Common Issues

**"Cannot connect to Ollama"**
→ Make sure `ollama serve` is running in a terminal

**"Port 5000 already in use"**
→ Change port in `chatbot_api.py` line 78: `port=5001`

**"Model not found"**
→ Run: `ollama pull llama2`

**"API not responding"**
→ Make sure you started `chatbot_api.py`

---

## 📊 Recommended Models

Start with these (fastest):
1. **mistral** - Best overall (4-5 sec/response)
2. **neural-chat** - Fast and good (3-4 sec/response)
3. **llama2** - Default (5-10 sec/response)

---

## 🎯 Next Steps

1. Play with different models
2. Try longer conversations
3. Use the API in your own projects
4. Read full [README.md](README.md) for more details

---

Enjoy! 🤖
