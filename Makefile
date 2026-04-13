# Makefile for Ollama Chatbot Docker commands

.PHONY: help build up down logs restart clean pull-model list-models shell

help:
	@echo "🤖 Ollama Chatbot Docker Commands"
	@echo "=================================="
	@echo ""
	@echo "Usage: make [command]"
	@echo ""
	@echo "Commands:"
	@echo "  make up              - Start containers"
	@echo "  make down            - Stop containers"
	@echo "  make build           - Build Docker images"
	@echo "  make logs            - View logs"
	@echo "  make logs-api        - View API logs only"
	@echo "  make logs-ollama     - View Ollama logs only"
	@echo "  make restart         - Restart containers"
	@echo "  make clean           - Remove containers and volumes"
	@echo "  make shell-api       - Open shell in API container"
	@echo "  make shell-ollama    - Open shell in Ollama container"
	@echo "  make pull-model      - Pull a model (usage: make pull-model MODEL=mistral)"
	@echo "  make list-models     - List available models"
	@echo "  make ps              - Show running containers"
	@echo "  make test-api        - Test API health"
	@echo ""

up:
	@echo "🚀 Starting containers..."
	docker-compose up -d
	@echo "✅ Containers started!"
	@echo "📡 API: http://localhost:5000"
	@echo "⏳ Wait 30-40 seconds for Ollama to start..."

down:
	@echo "🛑 Stopping containers..."
	docker-compose down
	@echo "✅ Containers stopped!"

build:
	@echo "🔨 Building images..."
	docker-compose build
	@echo "✅ Build complete!"

logs:
	docker-compose logs -f

logs-api:
	docker-compose logs -f chatbot-api

logs-ollama:
	docker-compose logs -f ollama

restart:
	@echo "🔄 Restarting containers..."
	docker-compose restart
	@echo "✅ Restarted!"

clean:
	@echo "⚠️  Removing containers and volumes..."
	docker-compose down -v
	@echo "✅ Cleaned!"
	@echo "❌ Warning: Ollama models have been deleted!"

clean-containers:
	@echo "🧹 Removing containers only (keeping volumes)..."
	docker-compose down
	@echo "✅ Containers removed!"

ps:
	docker ps --filter "label=com.docker.compose.project=chat-oll" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

shell-api:
	docker exec -it chatbot-api /bin/bash

shell-ollama:
	docker exec -it ollama-chatbot /bin/bash

pull-model:
	@if [ -z "$(MODEL)" ]; then \
		echo "Error: MODEL not specified"; \
		echo "Usage: make pull-model MODEL=llama2"; \
		exit 1; \
	fi
	@echo "📥 Pulling model: $(MODEL)..."
	docker exec ollama-chatbot ollama pull $(MODEL)
	@echo "✅ Model downloaded!"

list-models:
	@echo "📦 Available models:"
	docker exec ollama-chatbot ollama list

test-api:
	@echo "🧪 Testing API health..."
	curl -s http://localhost:5000/api/health | python -m json.tool || echo "❌ API not responding"

test-models:
	@echo "🧪 Testing model availability..."
	curl -s http://localhost:5000/api/models | python -m json.tool || echo "❌ API not responding"

test-chat:
	@echo "💬 Testing chat endpoint..."
	curl -s -X POST http://localhost:5000/api/chat \
	  -H "Content-Type: application/json" \
	  -d '{"message": "Hello!", "model": "llama2"}' | python -m json.tool || echo "❌ API not responding"

# Aliases
start: up
stop: down
reset: clean up

.DEFAULT_GOAL := help
