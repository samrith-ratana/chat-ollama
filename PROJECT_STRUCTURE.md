# 📁 Project Structure

```
chat-oll/
│
├── 📄 README.md                    # Main project documentation
├── 📄 QUICK_START.md              # Quick start guide
├── 📄 DOCKER.md                   # Docker setup guide
├── 📄 DOCKER-QUICKSTART.md        # Docker quick start
├── 📄 PROJECT_STRUCTURE.md        # This file
├── 📄 DEVELOPMENT.md              # Development guidelines
├── 📄 API_REFERENCE.md            # API documentation
├── 📄 DEPLOYMENT.md               # Production deployment guide
│
├── 📁 src/                        # Source code
│   ├── 📁 api/                    # API server
│   │   ├── __init__.py
│   │   ├── app.py                 # Flask application factory
│   │   ├── config.py              # Configuration management
│   │   ├── routes.py              # API endpoints
│   │   └── health.py              # Health checks
│   │
│   ├── 📁 services/               # Business logic
│   │   ├── __init__.py
│   │   ├── ollama_service.py      # Ollama integration
│   │   ├── chat_service.py        # Chat operations
│   │   └── model_service.py       # Model management
│   │
│   ├── 📁 models/                 # Data models
│   │   ├── __init__.py
│   │   ├── conversation.py        # Conversation schema
│   │   └── message.py             # Message schema
│   │
│   ├── 📁 utils/                  # Utility functions
│   │   ├── __init__.py
│   │   ├── logger.py              # Logging setup
│   │   ├── exceptions.py          # Custom exceptions
│   │   └── validators.py          # Input validation
│   │
│   ├── 📁 cli/                    # CLI interface
│   │   ├── __init__.py
│   │   └── chatbot_cli.py         # CLI implementation
│   │
│   └── 📁 web/                    # Web UI
│       ├── index.html             # Main UI
│       └── assets/
│           ├── css/
│           │   └── style.css      # Stylesheets
│           └── js/
│               └── app.js         # Frontend logic
│
├── 📁 docker/                     # Docker files
│   ├── Dockerfile                 # API container
│   ├── Dockerfile.ollama          # Ollama container (optional)
│   └── .dockerignore
│
├── 📁 config/                     # Configuration files
│   ├── docker-compose.yml         # Development
│   ├── docker-compose.host-ollama.yml
│   ├── docker-compose.prod.yml    # Production
│   ├── nginx.conf                 # Nginx configuration
│   └── .env.example               # Environment template
│
├── 📁 tests/                      # Test suite
│   ├── __init__.py
│   ├── test_api.py                # API tests
│   ├── test_services.py           # Service tests
│   ├── test_ollama.py             # Ollama integration tests
│   └── conftest.py                # Pytest configuration
│
├── 📁 scripts/                    # Utility scripts
│   ├── init_db.py                 # Database initialization
│   ├── download_models.py         # Model download script
│   ├── setup_env.sh               # Environment setup
│   └── generate_docs.py           # API docs generation
│
├── 📁 docs/                       # Additional documentation
│   ├── ARCHITECTURE.md            # System architecture
│   ├── API.md                     # API full reference
│   ├── MODELS.md                  # Available models
│   ├── DEPLOYMENT.md              # Deployment guide
│   ├── TROUBLESHOOTING.md         # Common issues
│   └── examples/                  # Code examples
│       ├── python_client.py
│       ├── curl_examples.sh
│       └── javascript_client.js
│
├── 📁 logs/                       # Application logs
│   └── .gitkeep
│
├── 📁 data/                       # Data files
│   ├── conversations/             # Saved conversations
│   └── models/                    # Model configurations
│
├── .gitignore                     # Git ignore rules
├── .gitattributes                 # Git attributes
├── Makefile                       # Make commands
├── requirements.txt               # Python dependencies
├── requirements-dev.txt           # Development dependencies
├── setup.py                       # Package setup
├── setup.cfg                      # Setup configuration
└── pyproject.toml                 # Modern Python packaging
```

## 📂 Directory Descriptions

### `src/` - Source Code
Main application code organized by functionality:
- **api/** - Flask application and routes
- **services/** - Business logic layer (Ollama, Chat operations)
- **models/** - Data schemas and models
- **utils/** - Shared utilities and helpers
- **cli/** - Command-line interface
- **web/** - Frontend UI files

### `docker/` - Docker Configuration
Docker-related files:
- Dockerfiles for different components
- Build scripts
- Ignore rules

### `config/` - Configuration
Configuration files for different environments:
- docker-compose files (dev, prod)
- Nginx configuration
- Environment templates

### `tests/` - Test Suite
Testing files:
- Unit tests
- Integration tests
- Fixtures and mocks

### `scripts/` - Utility Scripts
Automation and setup scripts:
- Database initialization
- Model downloading
- Environment setup

### `docs/` - Documentation
Additional documentation:
- Architecture diagrams
- API reference
- Deployment guides
- Code examples

### `logs/` - Application Logs
Runtime logs directory

### `data/` - Data Files
Application data:
- Conversation history
- Model configurations

---

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────┐
│              User Interface Layer               │
├──────────────┬──────────────┬────────────────────┤
│  Web UI      │  CLI         │  REST API Clients  │
│  (index.html)│  (Python)    │  (Python, JS, etc) │
└──────────────┴──────────────┴────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────┐
│            API Server Layer (Flask)             │
├─────────────────────────────────────────────────┤
│  • Routes & Controllers (api/routes.py)         │
│  • Request/Response Handling                    │
│  • CORS & Middleware                           │
└─────────────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────┐
│         Business Logic Layer (Services)         │
├──────────────┬──────────────┬────────────────────┤
│ Chat Service │ Ollama       │ Model Service      │
│              │ Service      │                    │
└──────────────┴──────────────┴────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────┐
│           Data & External Services              │
├──────────────┬──────────────┬────────────────────┤
│ Ollama API   │ Database     │ Cache (Redis)      │
│              │ (PostgreSQL) │                    │
└──────────────┴──────────────┴────────────────────┘
```

---

## 🔄 Data Flow

```
Client Request
     │
     ▼
┌─────────────────┐
│  API Routes     │  Parse & validate request
└─────────────────┘
     │
     ▼
┌─────────────────┐
│  Services       │  Business logic
└─────────────────┘
     │
     ▼
┌─────────────────┐
│  Ollama API     │  AI model processing
└─────────────────┘
     │
     ▼
┌─────────────────┐
│  Response       │  Return to client
└─────────────────┘
```

---

## 📊 Development Workflow

1. **Development** → Local files with hot-reload
2. **Testing** → Run test suite
3. **Docker Build** → Create container image
4. **Staging** → Deploy to staging environment
5. **Production** → Deploy to production

---

## 🎯 Key Points

✅ **Separation of Concerns** - Each layer has a specific responsibility
✅ **Scalability** - Easy to add new services or features
✅ **Testability** - Clear structure for unit and integration tests
✅ **Maintainability** - Organized code is easier to maintain
✅ **Documentation** - Comprehensive docs in `docs/` folder
✅ **Flexibility** - Support for multiple deployment options

---

See [DEVELOPMENT.md](DEVELOPMENT.md) for development guidelines.
