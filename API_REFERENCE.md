# 📡 API Reference

## Overview

REST API for Ollama Chatbot. All endpoints return JSON responses.

**Base URL:** `http://localhost:5000/api`

**Response Format:**
```json
{
  "status": "success|error",
  "data": {},
  "error": null,
  "timestamp": "2026-04-12T10:30:00Z"
}
```

---

## 🔑 Authentication

Currently no authentication. In production, add:
```bash
Authorization: Bearer YOUR_TOKEN
```

---

## 📋 Endpoints

### 1. Health Check

**Endpoint:** `GET /health`

**Description:** Check API and Ollama health status

**Request:**
```bash
curl http://localhost:5000/api/health
```

**Response (200 OK):**
```json
{
  "status": "healthy",
  "api": "running",
  "ollama": "running",
  "timestamp": "2026-04-12T10:30:00Z"
}
```

**Response (503 Service Unavailable):**
```json
{
  "status": "unhealthy",
  "api": "running",
  "ollama": "offline",
  "error": "Cannot connect to Ollama"
}
```

---

### 2. List Models

**Endpoint:** `GET /models`

**Description:** Get list of available models

**Request:**
```bash
curl http://localhost:5000/api/models
```

**Response (200 OK):**
```json
{
  "models": [
    "llama2",
    "mistral",
    "neural-chat",
    "falcon"
  ],
  "count": 4,
  "timestamp": "2026-04-12T10:30:00Z"
}
```

---

### 3. Send Message

**Endpoint:** `POST /chat`

**Description:** Send message and get response

**Request:**
```bash
curl -X POST http://localhost:5000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What is artificial intelligence?",
    "model": "llama2",
    "conversation_id": "user123"
  }'
```

**Request Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| message | string | Yes | User message |
| model | string | No | Model name (default: "llama2") |
| conversation_id | string | No | Conversation ID for history |
| options | object | No | Model options (see below) |

**Model Options (optional):**
```json
{
  "temperature": 0.7,    // 0.0-1.0, higher = more creative
  "top_p": 0.9,         // Nucleus sampling
  "top_k": 40,          // Top-K sampling
  "num_predict": 128    // Max tokens to generate
}
```

**Response (200 OK):**
```json
{
  "status": "success",
  "data": {
    "conversation_id": "user123",
    "model": "llama2",
    "response": "Artificial intelligence (AI) is...",
    "message_count": 2,
    "response_time": 2.345,
    "tokens": 156
  },
  "timestamp": "2026-04-12T10:30:00Z"
}
```

**Errors:**

400 Bad Request:
```json
{
  "status": "error",
  "error": "Message cannot be empty",
  "code": "VALIDATION_ERROR"
}
```

503 Service Unavailable:
```json
{
  "status": "error",
  "error": "Failed to connect to Ollama",
  "code": "OLLAMA_ERROR"
}
```

---

### 4. Get Conversation

**Endpoint:** `GET /conversation/<conversation_id>`

**Description:** Get full conversation history

**Request:**
```bash
curl http://localhost:5000/api/conversation/user123
```

**Response (200 OK):**
```json
{
  "status": "success",
  "data": {
    "conversation_id": "user123",
    "created_at": "2026-04-12T10:00:00Z",
    "messages": [
      {
        "id": "msg1",
        "role": "user",
        "content": "What is AI?",
        "timestamp": "2026-04-12T10:00:01Z"
      },
      {
        "id": "msg2",
        "role": "assistant",
        "content": "AI stands for...",
        "timestamp": "2026-04-12T10:00:03Z",
        "model": "llama2"
      }
    ],
    "message_count": 2
  },
  "timestamp": "2026-04-12T10:30:00Z"
}
```

**Query Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| limit | integer | Maximum messages to return (default: 50) |
| offset | integer | Skip N messages (default: 0) |

---

### 5. Clear Conversation

**Endpoint:** `DELETE /conversation/<conversation_id>`

**Description:** Clear conversation history

**Request:**
```bash
curl -X DELETE http://localhost:5000/api/conversation/user123
```

**Response (200 OK):**
```json
{
  "status": "success",
  "data": {
    "message": "Conversation cleared",
    "conversation_id": "user123"
  },
  "timestamp": "2026-04-12T10:30:00Z"
}
```

---

### 6. Update Conversation

**Endpoint:** `PATCH /conversation/<conversation_id>`

**Description:** Update conversation metadata

**Request:**
```bash
curl -X PATCH http://localhost:5000/api/conversation/user123 \
  -H "Content-Type: application/json" \
  -d '{
    "title": "My Chat Session",
    "tags": ["work", "ai"]
  }'
```

**Response (200 OK):**
```json
{
  "status": "success",
  "data": {
    "conversation_id": "user123",
    "title": "My Chat Session",
    "tags": ["work", "ai"]
  },
  "timestamp": "2026-04-12T10:30:00Z"
}
```

---

### 7. Download Model

**Endpoint:** `POST /models/download`

**Description:** Download/pull a model (background task)

**Request:**
```bash
curl -X POST http://localhost:5000/api/models/download \
  -H "Content-Type: application/json" \
  -d '{"model": "mistral"}'
```

**Response (202 Accepted):**
```json
{
  "status": "processing",
  "data": {
    "model": "mistral",
    "task_id": "task-uuid-1234",
    "status": "downloading"
  },
  "timestamp": "2026-04-12T10:30:00Z"
}
```

**Query Status:**
```bash
curl http://localhost:5000/api/models/download/task-uuid-1234
```

---

### 8. Delete Model

**Endpoint:** `DELETE /models/<model_name>`

**Description:** Delete a downloaded model

**Request:**
```bash
curl -X DELETE http://localhost:5000/api/models/mistral
```

**Response (200 OK):**
```json
{
  "status": "success",
  "data": {
    "message": "Model deleted",
    "model": "mistral"
  },
  "timestamp": "2026-04-12T10:30:00Z"
}
```

---

### 9. Get Statistics

**Endpoint:** `GET /stats`

**Description:** Get API statistics

**Request:**
```bash
curl http://localhost:5000/api/stats
```

**Response (200 OK):**
```json
{
  "status": "success",
  "data": {
    "total_conversations": 42,
    "total_messages": 356,
    "models_count": 3,
    "uptime_seconds": 86400,
    "requests_per_hour": 125,
    "average_response_time": 2.345
  },
  "timestamp": "2026-04-12T10:30:00Z"
}
```

---

## 📊 Status Codes

| Code | Meaning |
|------|---------|
| 200 | Success |
| 201 | Created |
| 202 | Accepted (async processing) |
| 400 | Bad Request (invalid input) |
| 401 | Unauthorized (auth required) |
| 403 | Forbidden (no permission) |
| 404 | Not Found |
| 409 | Conflict (duplicate, etc) |
| 429 | Too Many Requests (rate limited) |
| 500 | Internal Server Error |
| 503 | Service Unavailable (Ollama down) |

---

## 🔄 Pagination

For endpoints returning lists, use:

```bash
curl "http://localhost:5000/api/conversations?page=1&limit=10&sort=-created_at"
```

**Response:**
```json
{
  "status": "success",
  "data": {
    "items": [...],
    "pagination": {
      "page": 1,
      "limit": 10,
      "total": 42,
      "pages": 5
    }
  }
}
```

---

## 🔍 Filtering

Supported filters vary by endpoint:

```bash
# Filter by date range
curl "http://localhost:5000/api/conversations?from=2026-04-01&to=2026-04-12"

# Filter by tag
curl "http://localhost:5000/api/conversations?tags=work,personal"

# Search
curl "http://localhost:5000/api/conversations?search=python"
```

---

## 🔄 Streaming Responses (Future)

For long responses, use Server-Sent Events (SSE):

```bash
curl -N http://localhost:5000/api/chat/stream \
  -H "Content-Type: application/json" \
  -d '{"message": "Write a poem", "model": "llama2"}'
```

Response stream:
```
data: {"chunk": "Roses are red,"}
data: {"chunk": " violets are blue"}
data: {"status": "complete"}
```

---

## 📚 Code Examples

### Python Client
```python
import requests

API_URL = "http://localhost:5000/api"

# Send message
response = requests.post(f"{API_URL}/chat", json={
    "message": "What is machine learning?",
    "model": "mistral"
})

data = response.json()
print(data['data']['response'])

# Get conversation history
response = requests.get(f"{API_URL}/conversation/user123")
messages = response.json()['data']['messages']
for msg in messages:
    print(f"{msg['role']}: {msg['content']}")
```

### JavaScript Client
```javascript
const API_URL = "http://localhost:5000/api";

async function chat(message, model = "llama2") {
  const response = await fetch(`${API_URL}/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message, model })
  });
  
  const data = await response.json();
  return data.data.response;
}

// Usage
const response = await chat("Hello!");
console.log(response);
```

### cURL Examples
```bash
# Health check
curl http://localhost:5000/api/health | jq

# List models
curl http://localhost:5000/api/models | jq

# Send message
curl -X POST http://localhost:5000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Hello",
    "model": "llama2",
    "conversation_id": "test"
  }' | jq

# Get conversation
curl http://localhost:5000/api/conversation/test | jq
```

---

## ⚠️ Error Handling

Always handle errors in client code:

```python
try:
    response = requests.post(f"{API_URL}/chat", json={...})
    response.raise_for_status()  # Raise on 4xx/5xx
    data = response.json()
    
    if data['status'] == 'error':
        print(f"API Error: {data['error']}")
    else:
        print(f"Response: {data['data']['response']}")
        
except requests.exceptions.Timeout:
    print("Request timeout - model is thinking")
except requests.exceptions.ConnectionError:
    print("Cannot connect to API")
except Exception as e:
    print(f"Error: {e}")
```

---

## 🔐 Rate Limiting

API limits:
- **Global:** 200 requests/hour
- **Chat endpoint:** 30 requests/minute
- **Model download:** 5 concurrent downloads

Response headers:
```http
X-RateLimit-Limit: 30
X-RateLimit-Remaining: 28
X-RateLimit-Reset: 1681267200
```

When rate limited (429):
```json
{
  "status": "error",
  "error": "Too many requests",
  "retry_after": 60
}
```

---

## 📖 OpenAPI/Swagger

Interactive API docs available at:
```
http://localhost:5000/swagger
http://localhost:5000/redoc
```

Download OpenAPI spec:
```bash
curl http://localhost:5000/api/openapi.json
```

---

See [docs/examples/](docs/examples/) for more code samples.
