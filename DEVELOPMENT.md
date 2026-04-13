# 🛠️ Development Guidelines

## 📋 Table of Contents
1. [Code Standards](#code-standards)
2. [Git Workflow](#git-workflow)
3. [Testing](#testing)
4. [Documentation](#documentation)
5. [API Development](#api-development)
6. [Performance](#performance)
7. [Security](#security)
8. [Troubleshooting](#troubleshooting)

---

## 📝 Code Standards

### Python Code Style

**Follow PEP 8:**
```python
# ✅ Good
def send_message(message: str, model: str = "llama2") -> str:
    """Send message to model and get response."""
    if not message.strip():
        raise ValueError("Message cannot be empty")
    
    response = ollama_service.chat(message, model)
    return response

# ❌ Bad
def sendMessage(msg,m="llama2"):
    if msg=="":return None
    return OllamaService().chat(msg,m)
```

**Naming Conventions:**
- **Functions/Variables:** `snake_case`
- **Classes:** `PascalCase`
- **Constants:** `UPPER_SNAKE_CASE`
- **Private:** prefix with `_` (e.g., `_internal_method`)

**Type Hints:**
```python
from typing import List, Dict, Optional

def get_conversation(conversation_id: str) -> List[Dict[str, str]]:
    """Get full conversation by ID."""
    ...
```

### Docstrings

Use Google-style docstrings:
```python
def chat(message: str, model: str = "llama2") -> str:
    """
    Send a message and get response from Ollama.
    
    Args:
        message: The user message
        model: Model name (default: "llama2")
    
    Returns:
        Response from the model
    
    Raises:
        ValueError: If message is empty
        ConnectionError: If Ollama is not available
    
    Example:
        >>> response = chat("What is Python?")
        >>> print(response)
    """
```

### Line Length
- **Maximum:** 100 characters
- **Goal:** Readability

---

## 🔄 Git Workflow

### Branch Naming Convention

```
feature/description      - New feature
bugfix/description      - Bug fix
hotfix/description      - Urgent production fix
docs/description        - Documentation
refactor/description    - Code refactoring
test/description        - Test improvements
```

**Examples:**
```
feature/add-conversation-history
bugfix/fix-ollama-timeout
hotfix/fix-api-crash
docs/api-documentation
```

### Commit Message Format

```
<type>(<scope>): <description>

<body>

<footer>
```

**Types:**
- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation
- `test:` - Tests
- `refactor:` - Code refactoring
- `perf:` - Performance improvement
- `style:` - Code style (formatting)
- `chore:` - Maintenance

**Examples:**
```
feat(chat): add conversation persistence
fix(ollama): handle connection timeout
docs(api): add endpoint documentation
test(services): add ollama service tests
refactor(models): improve conversation schema
perf(cache): add redis caching
```

### Pull Request Process

1. Create feature branch
2. Make changes and commit
3. Write tests (minimum 80% coverage)
4. Update documentation
5. Submit PR with description
6. Get 2 approvals minimum
7. Merge to main

**PR Template:**
```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation

## Testing
- [ ] Unit tests added
- [ ] Integration tests added
- [ ] Manual testing completed

## Checklist
- [ ] Code follows style guidelines
- [ ] Documentation updated
- [ ] No new warnings generated
```

---

## 🧪 Testing

### Test Structure

```
tests/
├── test_api.py           # API endpoint tests
├── test_services.py      # Service layer tests
├── test_ollama.py        # Ollama integration tests
├── conftest.py           # Fixtures and setup
└── fixtures/
    ├── mock_responses.py
    └── test_data.py
```

### Writing Tests

**Unit Tests:**
```python
import pytest
from src.services.chat_service import ChatService

@pytest.fixture
def chat_service(mocker):
    """Provide mock chat service."""
    mocker.patch('src.services.ollama_service.OllamaService')
    return ChatService()

def test_send_message_success(chat_service):
    """Test successful message sending."""
    response = chat_service.send_message("Hello")
    assert response is not None
    assert isinstance(response, str)

def test_send_message_empty_raises_error(chat_service):
    """Test empty message raises ValueError."""
    with pytest.raises(ValueError):
        chat_service.send_message("")
```

**Integration Tests:**
```python
def test_api_chat_endpoint(client):
    """Test /api/chat endpoint."""
    response = client.post('/api/chat', json={
        'message': 'Test message',
        'model': 'llama2'
    })
    assert response.status_code == 200
    assert 'response' in response.json
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src

# Run specific test file
pytest tests/test_api.py

# Run specific test
pytest tests/test_api.py::test_health_check

# Run with verbose output
pytest -v

# Run in parallel
pytest -n auto
```

### Coverage Requirements

- **Line Coverage:** ≥80%
- **Branch Coverage:** ≥75%
- **Exclude:** migrations, __pycache__, venv

---

## 📚 Documentation

### Code Comments

**DO:**
```python
# Set timeout to 120 seconds for large models
response = requests.post(url, timeout=120)
```

**DON'T:**
```python
# increment counter
counter += 1
```

### README Standards

Each module should have:
- Purpose and description
- Usage examples
- Configuration options
- Common issues

### API Documentation

Use OpenAPI/Swagger format:
```python
from flask import Flask
from flasgger import Swagger

app = Flask(__name__)
swagger = Swagger(app)

@app.route('/api/chat', methods=['POST'])
def chat():
    """
    Send a message and get response
    ---
    parameters:
      - name: message
        in: body
        required: true
        schema:
          type: object
          properties:
            message:
              type: string
            model:
              type: string
    responses:
      200:
        description: Success
        schema:
          type: object
          properties:
            response:
              type: string
    """
    ...
```

---

## 🔌 API Development

### Adding New Endpoints

1. **Create route in `src/api/routes.py`:**
```python
@app.route('/api/new-endpoint', methods=['POST'])
def new_endpoint():
    """Handle new endpoint."""
    data = request.get_json()
    
    # Validate
    if not data:
        return jsonify({'error': 'Invalid request'}), 400
    
    # Process
    result = some_service.process(data)
    
    # Return
    return jsonify({'result': result}), 200
```

2. **Add service method in `src/services/`:**
```python
class SomeService:
    def process(self, data: Dict) -> str:
        """Process data and return result."""
        ...
```

3. **Write tests in `tests/test_api.py`:**
```python
def test_new_endpoint(client):
    """Test new endpoint."""
    response = client.post('/api/new-endpoint', json={'key': 'value'})
    assert response.status_code == 200
```

4. **Document in `docs/API.md`**

### Error Handling

```python
from src.utils.exceptions import OllamaError, ValidationError

try:
    result = ollama_service.chat(message)
except ConnectionError:
    return jsonify({'error': 'Ollama unavailable'}), 503
except ValidationError as e:
    return jsonify({'error': str(e)}), 400
except Exception as e:
    logger.error(f"Unexpected error: {e}")
    return jsonify({'error': 'Internal server error'}), 500
```

---

## ⚡ Performance

### Best Practices

1. **Use Connection Pooling:**
```python
session = requests.Session()
adapter = HTTPAdapter(pool_connections=10, pool_maxsize=10)
session.mount('http://', adapter)
```

2. **Cache Responses:**
```python
from functools import lru_cache

@lru_cache(maxsize=128)
def get_model_info(model_name: str) -> Dict:
    """Get model info with caching."""
    ...
```

3. **Async Operations (for long-running tasks):**
```python
from flask import request
from celery import Celery

celery = Celery(__name__)

@celery.task
def process_large_request(data):
    """Process long-running task asynchronously."""
    ...
```

4. **Database Indexing:**
```sql
CREATE INDEX idx_conversation_user_id ON conversations(user_id);
CREATE INDEX idx_message_timestamp ON messages(created_at);
```

### Monitoring

```python
import time

def log_performance(func):
    """Decorator to log function performance."""
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        duration = time.time() - start
        logger.debug(f"{func.__name__} took {duration:.2f}s")
        return result
    return wrapper

@log_performance
def slow_function():
    ...
```

---

## 🔒 Security

### Input Validation

```python
from src.utils.validators import validate_message, validate_model

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.get_json()
    
    message = validate_message(data.get('message'))  # Validate
    model = validate_model(data.get('model'))
    
    # Process validated data
    ...
```

### Environment Variables (Never commit secrets!)

```python
import os
from dotenv import load_dotenv

load_dotenv()

OLLAMA_URL = os.getenv('OLLAMA_BASE_URL')
SECRET_KEY = os.getenv('SECRET_KEY')
DATABASE_URL = os.getenv('DATABASE_URL')
```

### SQL Injection Prevention

```python
# ✅ Good - Use parameterized queries
db.execute("SELECT * FROM users WHERE id = ?", (user_id,))

# ❌ Bad - String concatenation
db.execute(f"SELECT * FROM users WHERE id = {user_id}")
```

### Rate Limiting

```python
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)

@app.route('/api/chat', methods=['POST'])
@limiter.limit("30 per minute")
def chat():
    ...
```

---

## 🐛 Troubleshooting

### Common Development Issues

**Issue: "ModuleNotFoundError"**
```bash
# Solution: Ensure PYTHONPATH is set
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
python -m pytest
```

**Issue: "Port already in use"**
```bash
# Solution: Use different port
python -m flask run --port 5001
```

**Issue: "Ollama connection refused"**
```bash
# Solution: Ensure Ollama is running
ollama serve

# Test connection
curl http://localhost:11434/api/tags
```

**Issue: "Test failures**
```bash
# Solution: Clear cache and reinstall
rm -rf .pytest_cache __pycache__
pip install -r requirements-dev.txt
pytest -v
```

---

## 🚀 Development Workflow Example

```bash
# 1. Create feature branch
git checkout -b feature/add-conversation-history

# 2. Make changes
vim src/services/chat_service.py

# 3. Run tests
pytest --cov=src tests/

# 4. Commit changes
git commit -m "feat(chat): add conversation history persistence"

# 5. Push and create PR
git push origin feature/add-conversation-history
# Open PR on GitHub

# 6. After review and approval, merge
git checkout main
git pull origin main
git merge feature/add-conversation-history
git push origin main
```

---

See [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md) for directory organization.
