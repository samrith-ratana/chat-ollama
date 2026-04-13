# 🚀 Deployment Guide

## 📋 Table of Contents
1. [Pre-Deployment](#pre-deployment)
2. [Local Deployment](#local-deployment)
3. [Docker Deployment](#docker-deployment)
4. [Cloud Deployment](#cloud-deployment)
5. [Production Checklist](#production-checklist)
6. [Monitoring](#monitoring)
7. [Scaling](#scaling)

---

## 🔍 Pre-Deployment

### Requirements Verification

**System Requirements:**
```bash
# Python version
python --version  # Should be 3.8+

# Docker version
docker --version

# Docker Compose version
docker-compose --version

# Disk space
df -h  # Minimum 50GB for models

# Memory
free -h  # Minimum 16GB RAM
```

### Configuration Check

```bash
# Test Ollama availability
curl http://localhost:11434/api/tags

# Test Python dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Run tests
pytest tests/ -v --cov=src

# Check code quality
flake8 src/
pylint src/
```

### Environment Setup

```bash
# Copy and customize environment file
cp .env.example .env

# Edit for your environment
nano .env

# Example .env file:
OLLAMA_BASE_URL=http://ollama:11434
DEFAULT_MODEL=mistral
FLASK_ENV=production
SECRET_KEY=your-secret-key-change-this
DATABASE_URL=postgresql://user:pass@db:5432/chatbot
REDIS_URL=redis://redis:6379/0
```

---

## 🖥️ Local Deployment

### Option 1: CLI Only

```bash
# Install dependencies
pip install -r requirements.txt

# Run CLI
python -m src.cli.chatbot_cli
```

### Option 2: API Server

```bash
# Install dependencies
pip install -r requirements.txt

# Start Ollama (separate terminal)
ollama serve

# Start API server
python src/api/app.py
```

Access at: `http://localhost:5000`

### Option 3: Development Mode

```bash
# Install dev dependencies
pip install -r requirements-dev.txt

# Run with hot-reload
export FLASK_ENV=development
export FLASK_APP=src/api/app.py
python -m flask run --reload

# In another terminal
python src/cli/chatbot_cli
```

---

## 🐳 Docker Deployment

### Quick Deploy

```bash
# Build and start
docker-compose up -d

# Download model
docker exec ollama-chatbot ollama pull llama2

# Check status
docker-compose ps

# View logs
docker-compose logs -f
```

### Custom Configuration

```bash
# Create .env file
cat > .env << EOF
OLLAMA_BASE_URL=http://ollama:11434
DEFAULT_MODEL=mistral
FLASK_ENV=production
EOF

# Deploy with env
docker-compose --env-file .env up -d
```

### Multi-Node Deployment

For scaling across multiple machines:

```yaml
# docker-compose.distributed.yml
version: '3.8'

services:
  ollama:
    image: ollama/ollama:latest
    environment:
      OLLAMA_HOST=0.0.0.0:11434
    volumes:
      - /large-storage/ollama:/root/.ollama
    networks:
      - distributed-net

  api-node-1:
    build: .
    environment:
      OLLAMA_BASE_URL=http://ollama:11434
    networks:
      - distributed-net
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 4G

  api-node-2:
    build: .
    environment:
      OLLAMA_BASE_URL=http://ollama:11434
    networks:
      - distributed-net
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 4G

networks:
  distributed-net:
    driver: overlay
```

---

## ☁️ Cloud Deployment

### AWS

**Using EC2 + RDS + ElastiCache:**

```bash
# 1. Launch EC2 instance
aws ec2 run-instances \
  --image-id ami-0c55b159cbfafe1f0 \
  --instance-type t3.xlarge \
  --key-name my-key

# 2. SSH into instance
ssh -i my-key.pem ec2-user@instance-ip

# 3. Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# 4. Clone and deploy
git clone https://github.com/your-repo/chat-oll.git
cd chat-oll
docker-compose -f docker-compose.prod.yml up -d

# 5. Configure RDS
# Update .env with RDS endpoint

# 6. Set up load balancer
# Create ALB pointing to EC2 on port 80/443
```

### Google Cloud (Cloud Run)

```bash
# 1. Create project
gcloud projects create chat-oll

# 2. Build and push image
gcloud builds submit --tag gcr.io/chat-oll/api

# 3. Deploy to Cloud Run
gcloud run deploy chat-oll-api \
  --image gcr.io/chat-oll/api \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars OLLAMA_BASE_URL=http://ollama:11434

# 4. Get endpoint URL
gcloud run services describe chat-oll-api
```

### Azure

```bash
# 1. Create resource group
az group create -n chat-oll-rg -l eastus

# 2. Create container registry
az acr create -g chat-oll-rg -n chatoll --sku Basic

# 3. Build and push
az acr build -r chatoll -t chat-oll:latest .

# 4. Deploy to Container Instances
az container create \
  -g chat-oll-rg \
  -n chat-oll \
  --image chatoll.azurecr.io/chat-oll:latest \
  --cpu 2 --memory 4 \
  --port 5000 \
  --environment-variables OLLAMA_BASE_URL=http://ollama:11434
```

---

## ✅ Production Checklist

### Pre-Launch

- [ ] All tests passing (100% coverage for critical paths)
- [ ] No hardcoded secrets or credentials
- [ ] Environment variables configured
- [ ] Database migrations completed
- [ ] Backups enabled
- [ ] Monitoring configured
- [ ] Alerting set up
- [ ] Rate limiting enabled
- [ ] CORS properly configured
- [ ] HTTPS/TLS configured
- [ ] Security headers added
- [ ] Logging configured
- [ ] Error tracking (Sentry) configured

### Infrastructure

- [ ] Database backups scheduled daily
- [ ] Log aggregation set up (ELK, CloudWatch)
- [ ] Metrics collection enabled (Prometheus)
- [ ] Health checks configured
- [ ] Auto-scaling policies set
- [ ] CDN configured for static assets
- [ ] Firewall rules configured
- [ ] VPC/Security groups restricted

### Performance

- [ ] Database indexes created
- [ ] Query optimization completed
- [ ] Caching configured (Redis)
- [ ] CDN enabled
- [ ] Compression enabled
- [ ] Load testing completed
- [ ] Capacity planning done

### Security

- [ ] TLS 1.2+ enforced
- [ ] SQL injection prevention verified
- [ ] XSS protection enabled
- [ ] CSRF tokens configured
- [ ] Rate limiting enabled
- [ ] Input validation on all endpoints
- [ ] Authentication/Authorization tested
- [ ] Secrets management configured

### Operations

- [ ] Run books documented
- [ ] On-call rotation established
- [ ] Incident response plan documented
- [ ] Disaster recovery plan tested
- [ ] Business continuity plan ready

---

## 📊 Monitoring

### Health Checks

```bash
# Check API health
curl http://localhost:5000/api/health -v

# Check Ollama availability
curl http://ollama:11434/api/tags

# Check database
curl http://localhost:5000/api/health/db

# Check Redis
redis-cli ping
```

### Metrics Collection (Prometheus)

```python
# src/api/metrics.py
from prometheus_client import Counter, Histogram, Gauge
import time

request_count = Counter(
    'api_requests_total',
    'Total API requests',
    ['method', 'endpoint', 'status']
)

request_duration = Histogram(
    'api_request_duration_seconds',
    'API request duration',
    ['method', 'endpoint']
)

active_conversations = Gauge(
    'active_conversations',
    'Number of active conversations'
)

@app.before_request
def before_request():
    request.start_time = time.time()

@app.after_request
def after_request(response):
    duration = time.time() - request.start_time
    request_duration.labels(
        method=request.method,
        endpoint=request.endpoint
    ).observe(duration)
    
    request_count.labels(
        method=request.method,
        endpoint=request.endpoint,
        status=response.status_code
    ).inc()
    
    return response
```

### Logging

```python
# src/utils/logger.py
import logging
from pythonjsonlogger import jsonlogger

handler = logging.StreamHandler()
formatter = jsonlogger.JsonFormatter()
handler.setFormatter(formatter)

logger = logging.getLogger()
logger.addHandler(handler)
logger.setLevel(logging.INFO)

# Usage
logger.info("Chat request", extra={
    "user_id": "123",
    "model": "llama2",
    "message_length": 45
})
```

### Alerting

Set up alerts for:
- API response time > 5 seconds
- Error rate > 5%
- Ollama unavailable
- Database connection errors
- Low disk space
- High memory usage
- High CPU usage

---

## 🔄 Scaling

### Horizontal Scaling

Add more API instances:

```yaml
version: '3.8'
services:
  api-1:
    build: .
    environment:
      OLLAMA_BASE_URL=http://ollama:11434
    ports:
      - "5001:5000"

  api-2:
    build: .
    environment:
      OLLAMA_BASE_URL=http://ollama:11434
    ports:
      - "5002:5000"

  nginx:
    image: nginx:latest
    volumes:
      - ./nginx-lb.conf:/etc/nginx/nginx.conf
    ports:
      - "5000:5000"
    depends_on:
      - api-1
      - api-2
```

### Vertical Scaling

Increase container resources:

```yaml
deploy:
  resources:
    limits:
      cpus: '4'
      memory: 8G
    reservations:
      cpus: '2'
      memory: 4G
```

### Database Scaling

```sql
-- Add read replicas
-- Setup master-slave replication
-- Use connection pooling (pgBouncer)

CREATE EXTENSION pg_trgm;
CREATE INDEX idx_message_content ON messages USING gin(content gin_trgm_ops);
```

### Caching Strategy

```python
# Cache model responses
from functools import lru_cache
import redis

redis_client = redis.Redis(host='localhost', port=6379)

def get_cached_response(message_hash, model):
    key = f"response:{model}:{message_hash}"
    cached = redis_client.get(key)
    if cached:
        return json.loads(cached)
    return None

def cache_response(message_hash, model, response):
    key = f"response:{model}:{message_hash}"
    redis_client.setex(key, 3600, json.dumps(response))
```

---

## 📈 Load Testing

```bash
# Install locust
pip install locust

# Create locustfile.py
from locust import HttpUser, task, between

class ChatbotUser(HttpUser):
    wait_time = between(1, 5)
    
    @task
    def chat(self):
        self.client.post("/api/chat", json={
            "message": "Hello",
            "model": "llama2"
        })

# Run load test
locust -f locustfile.py --host http://localhost:5000
```

---

## 📋 Maintenance

### Regular Tasks

**Daily:**
- Monitor error rates
- Check logs for issues
- Verify backups completed

**Weekly:**
- Review performance metrics
- Update dependencies
- Check security advisories

**Monthly:**
- Full backup test
- Disaster recovery drill
- Capacity planning review

**Quarterly:**
- Security audit
- Performance optimization
- Infrastructure upgrade planning

### Updating

```bash
# Update Docker images
docker-compose pull
docker-compose up -d

# Update Python dependencies
pip install --upgrade -r requirements.txt

# Update Ollama models
docker exec ollama-chatbot ollama list
docker exec ollama-chatbot ollama pull mistral
```

---

See [DOCKER.md](DOCKER.md) for Docker-specific deployment details.
