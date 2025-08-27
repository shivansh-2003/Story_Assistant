# Story Assistant Backend - Technical Setup Guide

This comprehensive guide will walk you through setting up the Story Assistant backend from scratch, including all dependencies, services, and configuration.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Environment Setup](#environment-setup)
3. [Database Setup](#database-setup)
4. [Vector Database Setup](#vector-database-setup)
5. [LLM Service Setup](#llm-service-setup)
6. [Image Generation Setup](#image-generation-setup)
7. [Application Setup](#application-setup)
8. [Testing & Verification](#testing--verification)
9. [Production Deployment](#production-deployment)
10. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### System Requirements

**Minimum Requirements:**
- **CPU**: 8 cores (16+ recommended)
- **RAM**: 32GB (64GB+ recommended)
- **Storage**: 500GB SSD (1TB+ recommended)
- **OS**: Ubuntu 20.04+ / macOS 12+ / Windows 11 (WSL2)

**Recommended for Production:**
- **CPU**: 32 cores
- **RAM**: 128GB
- **Storage**: 2TB NVMe SSD
- **GPU**: RTX 4090 or A6000 (for image generation)

### Software Dependencies

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install -y python3.11 python3.11-venv python3.11-dev
sudo apt install -y postgresql postgresql-contrib
sudo apt install -y redis-server
sudo apt install -y docker docker-compose
sudo apt install -y git curl wget

# macOS
brew install python@3.11
brew install postgresql
brew install redis
brew install docker docker-compose
brew install git curl wget

# Windows (WSL2)
# Install Ubuntu WSL2 and follow Ubuntu instructions
```

### Python Version
- **Required**: Python 3.11+
- **Recommended**: Python 3.11.8

---

## Environment Setup

### 1. Clone the Repository

```bash
git clone <repository-url>
cd Story_Assistant/src
```

### 2. Create Virtual Environment

```bash
# Create virtual environment
python3.11 -m venv venv

# Activate virtual environment
# Linux/macOS:
source venv/bin/activate
# Windows:
venv\Scripts\activate
```

### 3. Install Python Dependencies

```bash
# Upgrade pip
pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt
```

### 4. Environment Configuration

Create a `.env` file in the `src` directory:

```bash
# Copy template
cp env.template .env
```

Edit `.env` with your configuration:

```env
# Application Settings
APP_NAME=Story Assistant
DEBUG=false
HOST=0.0.0.0
PORT=8000
SECRET_KEY=your-super-secret-key-here

# Database Configuration
DATABASE_URL=postgresql://story_user:story_password@localhost:5432/story_assistant
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-supabase-anon-key
SUPABASE_SERVICE_ROLE_KEY=your-supabase-service-role-key

# LLM API Keys
GROQ_API_KEY=your-groq-api-key
OPENAI_API_KEY=your-openai-api-key
ANTHROPIC_API_KEY=your-anthropic-api-key

# Vector Database (Pinecone)
PINECONE_API_KEY=your-pinecone-api-key
PINECONE_ENVIRONMENT=us-west1-gcp
PINECONE_INDEX_NAME=story-assistant-index

# Image Generation
GEMINI_API_KEY=your-gemini-api-key

# Redis
REDIS_URL=redis://localhost:6379

# Generation Settings
DEFAULT_MAX_TOKENS=2000
DEFAULT_TEMPERATURE=0.7
MAX_CONCURRENT_GENERATIONS=10

# Vector DB Settings
EMBEDDING_MODEL=text-embedding-ada-002
VECTOR_DIMENSION=1536
SIMILARITY_THRESHOLD=0.8
```

---

## Database Setup

### Option 1: PostgreSQL (Recommended)

#### Install PostgreSQL

```bash
# Ubuntu/Debian
sudo apt install postgresql postgresql-contrib

# macOS
brew install postgresql
brew services start postgresql

# Windows
# Download from https://www.postgresql.org/download/windows/
```

#### Configure PostgreSQL

```bash
# Switch to postgres user
sudo -u postgres psql

# Create database and user
CREATE DATABASE story_assistant;
CREATE USER story_user WITH PASSWORD 'story_password';
GRANT ALL PRIVILEGES ON DATABASE story_assistant TO story_user;
ALTER USER story_user CREATEDB;

# Exit psql
\q
```

#### Initialize Database Schema

```bash
# Run database initialization
python -c "
from config.database_config import init_database
import asyncio
asyncio.run(init_database())
"
```

### Option 2: Supabase (Cloud)

1. Create account at [supabase.com](https://supabase.com)
2. Create new project
3. Get your project URL and API keys
4. Update `.env` with Supabase credentials

---

## Vector Database Setup

### Option 1: Pinecone (Recommended for Production)

1. Create account at [pinecone.io](https://pinecone.io)
2. Create new index:
   - **Name**: `story-assistant-index`
   - **Dimensions**: `1536`
   - **Metric**: `cosine`
   - **Environment**: Choose closest to your server

3. Get API key and environment from dashboard
4. Update `.env` with Pinecone credentials

### Option 2: ChromaDB (Self-hosted)

```bash
# Install ChromaDB
pip install chromadb

# Start ChromaDB server
chroma run --host 0.0.0.0 --port 8001
```

Update `.env`:
```env
CHROMA_HOST=localhost
CHROMA_PORT=8001
```

### Option 3: Local ChromaDB (Development)

```python
# The application will automatically use local ChromaDB
# No additional setup required for development
```

---

## LLM Service Setup

### Option 1: Groq API (Recommended)

1. Create account at [groq.com](https://groq.com)
2. Get API key from dashboard
3. Update `.env` with Groq API key

### Option 2: OpenAI API

1. Create account at [openai.com](https://openai.com)
2. Get API key from dashboard
3. Update `.env` with OpenAI API key

### Option 3: Anthropic API

1. Create account at [anthropic.com](https://anthropic.com)
2. Get API key from dashboard
3. Update `.env` with Anthropic API key

### Option 4: Local Ollama (Advanced)

```bash
# Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Pull models
ollama pull llama3.1:70b
ollama pull qwen2.5:72b

# Start Ollama service
ollama serve
```

---

## Image Generation Setup

### Option 1: Gemini Vision API (Recommended)

1. Create Google Cloud account
2. Enable Gemini API
3. Get API key from Google AI Studio
4. Update `.env` with Gemini API key

### Option 2: OpenAI DALL-E

1. Use existing OpenAI API key
2. Update image service configuration

### Option 3: Local Stable Diffusion (Advanced)

```bash
# Install ComfyUI
git clone https://github.com/comfyanonymous/ComfyUI
cd ComfyUI
pip install -r requirements.txt

# Download models
wget https://huggingface.co/stabilityai/stable-diffusion-xl-base-1.0/resolve/main/sd_xl_base_1.0.safetensors
mv sd_xl_base_1.0.safetensors models/checkpoints/

# Start ComfyUI
python main.py --listen 0.0.0.0 --port 8188
```

---

## Application Setup

### 1. Initialize Services

```bash
# Run setup script
python setup.py
```

This script will:
- Test database connections
- Initialize vector database
- Verify LLM service connectivity
- Test image generation service
- Create initial data structures

### 2. Start the Application

#### Development Mode

```bash
# Start with auto-reload
python main.py --reload --host 0.0.0.0 --port 8000
```

#### Production Mode

```bash
# Start with multiple workers
python main.py --host 0.0.0.0 --port 8000 --workers 4
```

### 3. Verify Installation

```bash
# Test health endpoint
curl http://localhost:8000/health

# Test API health
curl http://localhost:8000/api/v1/health
```

---

## Testing & Verification

### 1. Run Test Suite

```bash
# Install test dependencies
pip install pytest pytest-asyncio pytest-cov

# Run tests
pytest tests/ -v --cov=src
```

### 2. Manual Testing

#### Test Story Creation

```bash
# Create a test story
curl -X POST http://localhost:8000/api/v1/stories \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "title": "Test Story",
    "genre": "fantasy",
    "description": "A test story for verification"
  }'
```

#### Test Content Generation

```bash
# Generate story content
curl -X POST http://localhost:8000/api/v1/stories/STORY_ID/generate \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "user_input": "Start the story with a mysterious character",
    "target_word_count": 250
  }'
```

### 3. Performance Testing

```bash
# Install load testing tool
pip install locust

# Run load test
locust -f tests/load_test.py --host=http://localhost:8000
```

---

## Production Deployment

### 1. Docker Deployment

Create `docker-compose.yml`:

```yaml
version: '3.8'
services:
  story-assistant:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://story_user:story_password@postgres:5432/story_assistant
      - REDIS_URL=redis://redis:6379
    depends_on:
      - postgres
      - redis
    restart: unless-stopped

  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: story_assistant
      POSTGRES_USER: story_user
      POSTGRES_PASSWORD: story_password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data
    restart: unless-stopped

volumes:
  postgres_data:
  redis_data:
```

Create `Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 8000

# Start application
CMD ["python", "main.py", "--host", "0.0.0.0", "--port", "8000"]
```

### 2. Systemd Service (Linux)

Create `/etc/systemd/system/story-assistant.service`:

```ini
[Unit]
Description=Story Assistant Backend
After=network.target postgresql.service redis.service

[Service]
Type=simple
User=story-assistant
WorkingDirectory=/opt/story-assistant/src
Environment=PATH=/opt/story-assistant/src/venv/bin
ExecStart=/opt/story-assistant/src/venv/bin/python main.py --host 0.0.0.0 --port 8000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start service:

```bash
sudo systemctl enable story-assistant
sudo systemctl start story-assistant
sudo systemctl status story-assistant
```

### 3. Nginx Configuration

Create `/etc/nginx/sites-available/story-assistant`:

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Enable site:

```bash
sudo ln -s /etc/nginx/sites-available/story-assistant /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### 4. SSL Certificate (Let's Encrypt)

```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx

# Get SSL certificate
sudo certbot --nginx -d your-domain.com

# Auto-renewal
sudo crontab -e
# Add: 0 12 * * * /usr/bin/certbot renew --quiet
```

---

## Troubleshooting

### Common Issues

#### 1. Database Connection Failed

```bash
# Check PostgreSQL status
sudo systemctl status postgresql

# Check connection
psql -h localhost -U story_user -d story_assistant

# Check logs
sudo tail -f /var/log/postgresql/postgresql-*.log
```

#### 2. Vector Database Issues

```bash
# Test Pinecone connection
python -c "
import pinecone
pinecone.init(api_key='your-key', environment='your-env')
print(pinecone.list_indexes())
"

# Test ChromaDB
python -c "
import chromadb
client = chromadb.Client()
print(client.list_collections())
"
```

#### 3. LLM Service Issues

```bash
# Test Groq API
curl -X POST https://api.groq.com/openai/v1/chat/completions \
  -H "Authorization: Bearer YOUR_GROQ_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "llama3-70b-8192",
    "messages": [{"role": "user", "content": "Hello"}]
  }'
```

#### 4. Memory Issues

```bash
# Check memory usage
free -h

# Check process memory
ps aux | grep python

# Optimize memory settings
export PYTHONMALLOC=malloc
export PYTHONDEVMODE=1
```

#### 5. Port Conflicts

```bash
# Check what's using port 8000
sudo lsof -i :8000

# Kill process if needed
sudo kill -9 PID
```

### Debug Mode

Enable debug mode for troubleshooting:

```bash
# Set debug environment variable
export DEBUG=true

# Start with debug logging
python main.py --reload --log-level debug
```

### Log Analysis

```bash
# View application logs
tail -f /var/log/story-assistant/app.log

# Search for errors
grep -i error /var/log/story-assistant/app.log

# Monitor real-time requests
tail -f /var/log/story-assistant/app.log | grep "POST\|GET"
```

---

## Security Considerations

### 1. Environment Variables

```bash
# Never commit .env files
echo ".env" >> .gitignore
echo "*.env" >> .gitignore
```

### 2. API Key Security

```bash
# Rotate API keys regularly
# Use environment-specific keys
# Monitor API usage for anomalies
```

### 3. Database Security

```sql
-- Create read-only user for monitoring
CREATE USER story_monitor WITH PASSWORD 'monitor_password';
GRANT CONNECT ON DATABASE story_assistant TO story_monitor;
GRANT USAGE ON SCHEMA public TO story_monitor;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO story_monitor;
```

### 4. Network Security

```bash
# Configure firewall
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

---

## Conclusion

This setup guide provides a comprehensive path to deploying the Story Assistant backend. The system is designed to be scalable, maintainable, and production-ready.

For additional support:
- Check the troubleshooting section
- Review application logs
- Monitor system resources
- Keep dependencies updated

The Story Assistant backend is now ready to power your AI-driven storytelling platform!

