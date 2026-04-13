# 🐳 Docker Setup Guide

Run the Ollama Chatbot using Docker!

## 📋 Prerequisites

- **Docker** installed (from https://docs.docker.com/get-docker/)
- **Docker Compose** installed (comes with Docker Desktop)
- At least **8GB RAM** available for Docker

---

## 🚀 Quick Start (Easiest Method)

### Option 1: Ollama + API in Docker (Recommended)

This runs both Ollama and the API in containers.

```bash
docker-compose up -d
```

That's it! Now:

1. **Wait 30-40 seconds** for Ollama to start
2. **Download a model:**
   ```bash
   docker exec ollama-chatbot ollama pull llama2
   ```
3. **Open Web UI:** http://localhost:5000
4. **Start chatting!**

View logs:
```bash
docker-compose logs -f chatbot-api
docker-compose logs -f ollama
```

Stop everything:
```bash
docker-compose down
```

---

### Option 2: API in Docker, Ollama on Host

If you prefer Ollama on your machine (not in Docker):

**Terminal 1 - Run Ollama on your machine:**
```bash
ollama serve
```

**Terminal 2 - Run API in Docker:**
```bash
docker-compose -f docker-compose.host-ollama.yml up
```

Then open http://localhost:5000

---

## 📡 Available Endpoints

All same endpoints as before, now running in Docker:

```bash
# Health check
curl http://localhost:5000/api/health

# Get models
curl http://localhost:5000/api/models

# Send message
curl -X POST http://localhost:5000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello", "model": "llama2"}'
```

---

## 🔧 Configuration

### Environment Variables

Add to `docker-compose.yml` under `chatbot-api` `environment`:

```yaml
environment:
  - OLLAMA_BASE_URL=http://ollama:11434
  - DEFAULT_MODEL=mistral
  - FLASK_ENV=production
```

### Change API Port

Edit `docker-compose.yml`:
```yaml
ports:
  - "5001:5000"  # Access on http://localhost:5001
```

### Change Ollama Port

Edit `docker-compose.yml`:
```yaml
ollama:
  ports:
    - "11435:11434"  # Use different port
```

---

## 🎮 Common Commands

### View running containers
```bash
docker ps
```

### View logs
```bash
# All logs
docker-compose logs

# Specific service
docker-compose logs chatbot-api
docker-compose logs ollama

# Follow logs in real-time
docker-compose logs -f
```

### Stop containers
```bash
docker-compose stop
```

### Restart containers
```bash
docker-compose restart
```

### Remove everything
```bash
# Stop and remove containers
docker-compose down

# Also remove volumes (deletes Ollama models!)
docker-compose down -v
```

### Pull a model
```bash
docker exec ollama-chatbot ollama pull mistral
```

### List models in container
```bash
docker exec ollama-chatbot ollama list
```

### Access Ollama directly
```bash
docker exec -it ollama-chatbot ollama run llama2
```

---

## 💾 Persistent Data

Models are stored in the `ollama_data` volume. This persists between container restarts.

View volumes:
```bash
docker volume ls
```

Remove volume (deletes models):
```bash
docker volume rm chat-oll_ollama_data
```

---

## 🖥️ GPU Support

To use GPU acceleration:

1. Install NVIDIA Docker runtime: https://github.com/NVIDIA/nvidia-docker
2. Uncomment GPU section in `docker-compose.yml`:

```yaml
deploy:
  resources:
    reservations:
      devices:
        - driver: nvidia
          count: 1
          capabilities: [gpu]
```

3. Run:
```bash
docker-compose up -d
```

Check GPU usage:
```bash
docker exec ollama-chatbot nvidia-smi
```

---

## 🔍 Troubleshooting

### "Connection refused"
```bash
# Check if containers are running
docker ps

# View logs for errors
docker-compose logs
```

### "Port 5000 already in use"
Change port in `docker-compose.yml`:
```yaml
ports:
  - "5001:5000"
```

### "Out of memory"
Models need RAM. Give Docker more memory:
- **Windows/Mac:** Docker Desktop → Settings → Resources → Increase Memory
- **Linux:** Edit `/etc/docker/daemon.json`

### "Ollama not responding"
```bash
# Restart Ollama
docker-compose restart ollama

# Check health
docker exec ollama-chatbot curl http://localhost:11434/api/tags
```

### "Download model hangs"
Models can be 3-7GB. Be patient or:
```bash
# Check download progress
docker-compose logs -f ollama
```

### To rebuild after changes
```bash
docker-compose up -d --build
```

---

## 📊 Performance Tips

| Model | VRAM | Speed | Quality |
|-------|------|-------|---------|
| mistral | 5GB | ⚡⚡⚡ | ⭐⭐⭐⭐ |
| llama2 | 4GB | ⚡⚡ | ⭐⭐⭐⭐ |
| neural-chat | 3GB | ⚡⚡⭐ | ⭐⭐⭐ |

**Tip:** Start with `mistral` for best speed/quality.

---

## 🏢 Production Deployment

For production, consider:

1. **Use a proper database** (PostgreSQL, MongoDB)
2. **Add authentication** (JWT tokens)
3. **Use reverse proxy** (Nginx)
4. **Set up monitoring** (Prometheus, Grafana)
5. **Use CI/CD** (GitHub Actions, GitLab CI)
6. **Environment .env file** for secrets

Example `.env`:
```
OLLAMA_BASE_URL=http://ollama:11434
DEFAULT_MODEL=mistral
FLASK_ENV=production
SECRET_KEY=your-secret-key
```

Example `docker-compose.prod.yml` with more security.

---

## 📚 Useful Docker Compose Docs

- https://docs.docker.com/compose/compose-file/
- https://docs.docker.com/compose/reference/
- https://docs.docker.com/get-started/

---

## 🎯 Architecture

```
┌─────────────────────────────────────────┐
│        Docker Network                   │
├─────────────────────────────────────────┤
│                                         │
│  ┌────────────────┐   ┌──────────────┐ │
│  │  Chatbot API   │   │   Ollama     │ │
│  │  (Flask)       │───┼──  (Models)  │ │
│  │  Port: 5000    │   │  Port: 11434 │ │
│  └────────────────┘   └──────────────┘ │
│         ↑                      ↑        │
│         │ HTTP                 │ API    │
│         │                      │        │
└─────────┼──────────────────────┼────────┘
          │                      │
          ↓                      ↓
    ┌──────────────┐     ┌──────────────┐
    │ Browser/Web  │     │ ollama       │
    │ UI           │     │ CLI (host)   │
    └──────────────┘     └──────────────┘
```

---

## ❓ FAQ

**Q: Can I use this with multiple users?**  
A: Yes! The API stores conversations by ID. Scale with a proper database.

**Q: Will Ollama models persist after container stops?**  
A: Yes, volumes are persistent. Models stay in `ollama_data`.

**Q: Can I add more services?**  
A: Absolutely! Add PostgreSQL, Redis, etc. to `docker-compose.yml`.

**Q: Is this production-ready?**  
A: It's a great start! Add auth, monitoring, and proper database for production.

---

Enjoy your Dockerized chatbot! 🐳🤖
