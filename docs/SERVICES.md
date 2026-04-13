# 🏗️ Services Architecture & Guidelines

## 📋 Overview

The chatbot is built using a **layered architecture** with clear separation of concerns:

```
┌─────────────────────────────────────┐
│      Presentation Layer             │
│  (Web UI, CLI, API Controllers)     │
└─────────────────────────────────────┘
           ↓
┌─────────────────────────────────────┐
│      Application Layer              │
│  (API Routes, Request Handling)     │
└─────────────────────────────────────┘
           ↓
┌─────────────────────────────────────┐
│      Business Logic Layer           │
│  (Services: Chat, Ollama, Model)    │
└─────────────────────────────────────┘
           ↓
┌─────────────────────────────────────┐
│      Data & Integration Layer       │
│  (Ollama API, Database, Cache)      │
└─────────────────────────────────────┘
```

---

## 🔌 Service Modules

### 1. **API Service** (`src/api/`)

Handles HTTP requests and responses.

**Responsibilities:**
- Route incoming requests
- Validate input data
- Format responses
- Handle CORS
- Apply middleware

**Key Files:**
```
src/api/
├── __init__.py         # Initialize Flask app
├── app.py              # Flask application factory
├── config.py           # Configuration management
├── routes.py           # API endpoints
├── middleware.py       # Custom middleware
└── health.py           # Health check endpoints
```

**Example Implementation:**

```python
# src/api/routes.py
from flask import Blueprint, request, jsonify
from src.services.chat_service import ChatService
from src.utils.validators import validate_message

chat_bp = Blueprint('chat', __name__, url_prefix='/api')
chat_service = ChatService()

@chat_bp.route('/chat', methods=['POST'])
def send_message():
    """Send message endpoint."""
    try:
        # 1. Get request data
        data = request.get_json()
        
        # 2. Validate
        message = validate_message(data.get('message'))
        model = data.get('model', 'llama2')
        conversation_id = data.get('conversation_id', 'default')
        
        # 3. Call service
        response = chat_service.process_message(
            message=message,
            model=model,
            conversation_id=conversation_id
        )
        
        # 4. Return response
        return jsonify({
            'status': 'success',
            'data': response,
            'timestamp': datetime.utcnow().isoformat()
        }), 200
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"Error: {e}")
        return jsonify({'error': 'Internal server error'}), 500
```

**Guidelines:**
- ✅ Keep routes thin - delegate to services
- ✅ Always validate input
- ✅ Return consistent JSON responses
- ✅ Use appropriate HTTP status codes
- ❌ Don't put business logic in routes
- ❌ Don't query databases directly

---

### 2. **Chat Service** (`src/services/chat_service.py`)

Core business logic for chat operations.

**Responsibilities:**
- Process user messages
- Manage conversation history
- Delegate to Ollama service
- Handle context management

**Interface:**

```python
class ChatService:
    """Handle chat operations."""
    
    def process_message(self, message: str, model: str, 
                       conversation_id: str) -> dict:
        """Process message and return response."""
    
    def get_conversation(self, conversation_id: str) -> list:
        """Get conversation history."""
    
    def clear_conversation(self, conversation_id: str) -> bool:
        """Clear conversation history."""
    
    def save_conversation(self, conversation_id: str) -> bool:
        """Save conversation to persistence."""
```

**Example Implementation:**

```python
# src/services/chat_service.py
from typing import Dict, List
from src.services.ollama_service import OllamaService
from src.utils.logger import logger

class ChatService:
    def __init__(self):
        self.ollama = OllamaService()
        self.conversations = {}  # In-memory, replace with DB
    
    def process_message(self, message: str, model: str, 
                       conversation_id: str) -> Dict:
        """
        Process message and return response.
        
        Args:
            message: User message
            model: Model name
            conversation_id: Session ID
        
        Returns:
            Response dictionary with metadata
        """
        try:
            # 1. Initialize conversation if needed
            if conversation_id not in self.conversations:
                self.conversations[conversation_id] = []
            
            history = self.conversations[conversation_id]
            
            # 2. Add user message to history
            history.append({
                'role': 'user',
                'content': message,
                'timestamp': datetime.utcnow().isoformat()
            })
            
            # 3. Get response from Ollama
            response = self.ollama.chat(history, model)
            
            # 4. Add to history
            history.append({
                'role': 'assistant',
                'content': response,
                'model': model,
                'timestamp': datetime.utcnow().isoformat()
            })
            
            # 5. Return response with metadata
            return {
                'response': response,
                'conversation_id': conversation_id,
                'message_count': len(history),
                'model': model
            }
            
        except Exception as e:
            logger.error(f"Chat service error: {e}")
            raise
    
    def get_conversation(self, conversation_id: str) -> List[Dict]:
        """Get conversation history."""
        return self.conversations.get(conversation_id, [])
    
    def clear_conversation(self, conversation_id: str) -> bool:
        """Clear conversation history."""
        if conversation_id in self.conversations:
            del self.conversations[conversation_id]
            return True
        return False
```

**Guidelines:**
- ✅ One responsibility per method
- ✅ Use dependency injection
- ✅ Handle errors gracefully
- ✅ Log important operations
- ✅ Use type hints
- ❌ Don't handle HTTP directly
- ❌ Don't hardcode configuration

---

### 3. **Ollama Service** (`src/services/ollama_service.py`)

Interface with Ollama API.

**Responsibilities:**
- Send requests to Ollama
- Format messages for model
- Handle model errors
- Manage model versions

**Interface:**

```python
class OllamaService:
    """Interface with Ollama API."""
    
    def chat(self, messages: List[Dict], model: str) -> str:
        """Send message to model."""
    
    def get_models(self) -> List[str]:
        """Get available models."""
    
    def health_check(self) -> bool:
        """Check if Ollama is running."""
    
    def pull_model(self, model: str) -> bool:
        """Download/pull a model."""
```

**Example Implementation:**

```python
# src/services/ollama_service.py
import requests
from typing import List, Dict
from src.utils.logger import logger
from src.utils.exceptions import OllamaError

class OllamaService:
    def __init__(self, base_url: str = "http://localhost:11434"):
        self.base_url = base_url
        self.session = self._create_session()
    
    def _create_session(self) -> requests.Session:
        """Create HTTP session with connection pooling."""
        session = requests.Session()
        adapter = requests.adapters.HTTPAdapter(
            pool_connections=10,
            pool_maxsize=10
        )
        session.mount('http://', adapter)
        return session
    
    def chat(self, messages: List[Dict], model: str) -> str:
        """
        Send messages to model and get response.
        
        Args:
            messages: Message history
            model: Model name
        
        Returns:
            Response text
        
        Raises:
            OllamaError: If request fails
        """
        try:
            url = f"{self.base_url}/api/chat"
            payload = {
                'model': model,
                'messages': messages,
                'stream': False
            }
            
            response = self.session.post(
                url,
                json=payload,
                timeout=120
            )
            response.raise_for_status()
            
            result = response.json()
            return result.get('message', {}).get('content', '')
            
        except requests.exceptions.Timeout:
            logger.error(f"Timeout calling model {model}")
            raise OllamaError("Model request timed out")
        except requests.exceptions.ConnectionError:
            logger.error("Cannot connect to Ollama")
            raise OllamaError("Ollama service unavailable")
        except Exception as e:
            logger.error(f"Ollama error: {e}")
            raise OllamaError(str(e))
    
    def health_check(self) -> bool:
        """Check if Ollama is healthy."""
        try:
            response = self.session.get(
                f"{self.base_url}/api/tags",
                timeout=5
            )
            return response.status_code == 200
        except:
            return False
    
    def get_models(self) -> List[str]:
        """Get available models."""
        try:
            response = self.session.get(
                f"{self.base_url}/api/tags",
                timeout=10
            )
            response.raise_for_status()
            models = response.json().get('models', [])
            return [m['name'] for m in models]
        except Exception as e:
            logger.error(f"Error fetching models: {e}")
            return []
    
    def pull_model(self, model: str) -> bool:
        """Download a model."""
        try:
            url = f"{self.base_url}/api/pull"
            payload = {'name': model, 'stream': False}
            
            response = self.session.post(url, json=payload)
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Error pulling model: {e}")
            return False
```

**Guidelines:**
- ✅ Handle timeout gracefully
- ✅ Implement connection pooling
- ✅ Validate model names
- ✅ Log errors with context
- ✅ Use exponential backoff for retries
- ❌ Don't expose Ollama errors directly
- ❌ Don't hardcode timeouts

---

### 4. **Model Service** (`src/services/model_service.py`)

Manage available models.

**Responsibilities:**
- List available models
- Download new models
- Delete models
- Validate model compatibility

**Example Implementation:**

```python
# src/services/model_service.py
from typing import List, Dict
from src.services.ollama_service import OllamaService

class ModelService:
    """Manage AI models."""
    
    # Supported models with metadata
    MODELS_INFO = {
        'llama2': {
            'size': '3.8GB',
            'speed': 'Medium',
            'quality': 'Good',
            'url': 'https://ollama.ai/library/llama2'
        },
        'mistral': {
            'size': '4.1GB',
            'speed': 'Fast',
            'quality': 'Excellent',
            'url': 'https://ollama.ai/library/mistral'
        },
        'neural-chat': {
            'size': '2.9GB',
            'speed': 'Very Fast',
            'quality': 'Good',
            'url': 'https://ollama.ai/library/neural-chat'
        }
    }
    
    def __init__(self):
        self.ollama = OllamaService()
    
    def get_available_models(self) -> List[str]:
        """Get list of available models."""
        return self.ollama.get_models()
    
    def get_model_info(self, model: str) -> Dict:
        """Get model metadata."""
        return self.MODELS_INFO.get(model, {})
    
    def download_model(self, model: str) -> bool:
        """Download a model."""
        if model not in self.MODELS_INFO:
            return False
        return self.ollama.pull_model(model)
    
    def validate_model(self, model: str) -> bool:
        """Check if model is available."""
        return model in self.get_available_models()
```

**Guidelines:**
- ✅ Maintain model metadata
- ✅ Validate before using
- ✅ Support async downloads
- ✅ Track model versions
- ❌ Don't assume models exist

---

## 🔗 Service Communication

### Dependency Injection

```python
# ✅ Good - Injected dependency
class ChatService:
    def __init__(self, ollama_service: OllamaService):
        self.ollama = ollama_service

# ❌ Bad - Hardcoded dependency
class ChatService:
    def __init__(self):
        self.ollama = OllamaService()
```

### Service Factory

```python
# src/api/app.py
from src.services.chat_service import ChatService
from src.services.ollama_service import OllamaService

def create_app():
    """Application factory."""
    app = Flask(__name__)
    app.config.from_object('src.api.config.Config')
    
    # Initialize services
    ollama_service = OllamaService(
        base_url=app.config['OLLAMA_BASE_URL']
    )
    chat_service = ChatService(ollama_service)
    
    # Make available globally
    app.ollama_service = ollama_service
    app.chat_service = chat_service
    
    return app
```

---

## 🧪 Service Testing

**Unit Test Example:**

```python
# tests/test_services.py
import pytest
from unittest.mock import Mock, patch
from src.services.chat_service import ChatService
from src.services.ollama_service import OllamaService

@pytest.fixture
def mock_ollama():
    """Mock Ollama service."""
    mock = Mock(spec=OllamaService)
    mock.chat.return_value = "Test response"
    return mock

@pytest.fixture
def chat_service(mock_ollama):
    """Provide chat service with mock."""
    return ChatService(mock_ollama)

def test_process_message_success(chat_service, mock_ollama):
    """Test successful message processing."""
    response = chat_service.process_message(
        message="Hello",
        model="llama2",
        conversation_id="test1"
    )
    
    assert response['response'] == "Test response"
    assert response['conversation_id'] == "test1"
    assert mock_ollama.chat.called

def test_process_message_empty_fails(chat_service):
    """Test empty message is rejected."""
    with pytest.raises(ValueError):
        chat_service.process_message(
            message="",
            model="llama2",
            conversation_id="test1"
        )
```

---

## 📋 Service Checklist

When creating a new service:

- [ ] Single responsibility principle
- [ ] Clear interface/contract
- [ ] Type hints on all methods
- [ ] Comprehensive docstrings
- [ ] Error handling
- [ ] Logging
- [ ] Unit tests (>80% coverage)
- [ ] Integration tests
- [ ] Configuration externalized
- [ ] Dependency injection
- [ ] No hardcoded values
- [ ] Database independence (if applicable)

---

## 🔄 Best Practices

### Error Handling

```python
# Custom exceptions
class ChatError(Exception):
    """Base chat exception."""

class OllamaError(ChatError):
    """Ollama-related error."""

# Usage in service
try:
    response = ollama.chat(messages, model)
except OllamaError as e:
    logger.error(f"Ollama failed: {e}")
    raise ChatError("Failed to get response") from e
```

### Logging

```python
import logging

logger = logging.getLogger(__name__)

class ChatService:
    def process_message(self, message, model, conv_id):
        logger.info(
            "Processing message",
            extra={
                'conversation_id': conv_id,
                'model': model,
                'message_length': len(message)
            }
        )
```

### Configuration

```python
import os

class Config:
    """Configuration management."""
    OLLAMA_BASE_URL = os.getenv(
        'OLLAMA_BASE_URL',
        'http://localhost:11434'
    )
    DEFAULT_MODEL = os.getenv('DEFAULT_MODEL', 'llama2')
    REQUEST_TIMEOUT = int(os.getenv('REQUEST_TIMEOUT', 120))
```

---

See [DEVELOPMENT.md](DEVELOPMENT.md) for coding guidelines and [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md) for organization.
