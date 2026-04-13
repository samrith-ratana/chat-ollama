# 🐳 Docker Installation & Quick Start

## ⚡ 5-Minute Setup

### Step 1: Install Docker

**Windows/Mac:**
- Download [Docker Desktop](https://www.docker.com/products/docker-desktop)
- Install and launch

**Linux:**
```bash
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER
```

Verify installation:
```bash
docker --version
docker-compose --version
```

### Step 2: Start Everything

```bash
docker-compose up -d
```

That's it! Your chatbot is starting. Check status:
```bash
docker-compose ps
```

### Step 3: Download a Model

```bash
docker exec ollama-chatbot ollama pull llama2
```

This may take 5-10 minutes depending on your internet speed.

### Step 4: Open Web UI

Go to: **http://localhost:5000**

Start chatting! 🚀

---

## 📋 What's Running?

```
✅ Ollama                  - AI models running on http://localhost:11434
✅ Chatbot API             - REST API running on http://localhost:5000
✅ Web UI                  - Beautiful chat interface
```

---

## 🎯 Next Commands to Try

```bash
# View logs in real-time
docker-compose logs -f

# Check available models
docker exec ollama-chatbot ollama list

# Try another model
docker exec ollama-chatbot ollama pull mistral

# Restart containers
docker-compose restart

# Stop everything
docker-compose down

# Remove everything (including downloaded models)
docker-compose down -v
```

---

## 🛠️ Faster Commands with Make

If you have `make` installed (Linux/Mac):

```bash
make help        # Show all commands
make up          # Start containers
make logs        # View logs
make pull-model MODEL=mistral  # Download new model
make list-models # List downloaded models
make down        # Stop containers
```

---

## 🐛 Troubleshooting

**API showing "Cannot connect to Ollama"**
- Wait 30-40 seconds for Ollama to fully start
- Check logs: `docker-compose logs ollama`
- Restart: `docker-compose restart`

**Need more than 5GB RAM for models**
- Windows/Mac: Docker Desktop → Settings → Resources → Memory
- Linux: Check available RAM: `free -h`

**Models not downloading**
- Check internet connection
- View download progress: `docker-compose logs -f ollama`
- Models are 3-7GB each

**Port 5000 already in use**
Edit `docker-compose.yml` and change:
```yaml
ports:
  - "5001:5000"  # Use 5001 instead
```
Then run: `docker-compose up -d`

---

## 📊 Model Download Times

| Model | Size | Speed |
|-------|------|-------|
| neural-chat | 3GB | 2-3 min |
| mistral | 4GB | 3-4 min |
| llama2 | 3GB | 2-3 min |
| dolphin-mixtral | 26GB | 15-20 min |

*Times vary based on internet speed*

---

## 💻 System Requirements

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| RAM | 8GB | 16GB+ |
| Disk Space | 20GB | 50GB+ |
| Network | 10Mbps | 50Mbps+ |
| CPU | 2 cores | 4+ cores |
| GPU | No | NVIDIA (optional) |

---

## 🚀 Advanced Usage

### Option 2: Ollama on Host, API in Docker

If you want Ollama running on your PC (not in Docker):

**Terminal 1:**
```bash
ollama serve
```

**Terminal 2:**
```bash
docker-compose -f docker-compose.host-ollama.yml up -d
```

Then visit: http://localhost:5000

### Option 3: Custom Configuration

Create `.env` file:
```env
OLLAMA_BASE_URL=http://ollama:11434
DEFAULT_MODEL=mistral
FLASK_ENV=production
```

Run with env:
```bash
docker-compose --env-file .env up -d
```

---

## 📖 Common Docker Commands

```bash
# View all containers
docker ps -a

# View all images
docker images

# View container logs
docker logs container_name
docker logs -f container_name  # Follow logs

# Execute command in container
docker exec -it container_name bash
docker exec container_name ollama run llama2

# Stop specific container
docker stop container_name

# Remove container
docker rm container_name

# View disk usage
docker system df

# Clean up unused data
docker system prune
```

---

## 🔄 Updating

Update to latest images:
```bash
docker-compose pull
docker-compose up -d
```

---

## 🎓 Learning Resources

- [Docker Official Docs](https://docs.docker.com/)
- [Docker Compose Guide](https://docs.docker.com/compose/)
- [Ollama Documentation](https://ollama.ai)

---

## ✅ Checklist

- [ ] Docker installed (`docker --version`)
- [ ] Docker Compose installed (`docker-compose --version`)
- [ ] Ran `docker-compose up -d`
- [ ] Waited 30-40 seconds
- [ ] Downloaded model: `ollama pull llama2`
- [ ] Opened http://localhost:5000
- [ ] Chatting successfully!

---

You're all set! Enjoy your containerized chatbot! 🐳🤖
