# AI Healthcare Chatbot - Deployment Guide

## Overview

This guide covers deploying the **MediVoice AI Healthcare Chatbot** system, which consists of:
- **Backend**: FastAPI application (Python)
- **Frontend**: React + Vite application (TypeScript)
- **Redis**: Cache layer for performance

## Prerequisites

### Option A: Docker Deployment (Recommended)
- Docker Desktop installed ([Download here](https://www.docker.com/products/docker-desktop/))
- Docker Compose (included with Docker Desktop)

### Option B: Manual Deployment
- Python 3.11+
- Node.js 18+
- Redis 7+

---

## Option A: Docker Deployment (Production-Ready)

### 1. Install Docker Desktop

1. Download from https://www.docker.com/products/docker-desktop/
2. Install and restart your computer
3. Verify installation:
   ```bash
   docker --version
   docker-compose --version
   ```

### 2. Configure Environment

The `.env` file is already configured. For production, update these values:

```env
# Change JWT secret to a new random value
JWT_SECRET=<generate-new-secret-with-openssl-rand-base64-32>

# Set debug to false for production
DEBUG=false

# Update frontend URL to your domain
FRONTEND_URL=http://your-domain.com
```

### 3. Deploy with Docker Compose

```bash
# Build and start all services
docker-compose up -d --build

# View logs
docker-compose logs -f

# Check service status
docker-compose ps
```

### 4. Access the Application

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/api/health

### 5. Docker Management Commands

```bash
# Stop services
docker-compose stop

# Start services
docker-compose start

# Restart services
docker-compose restart

# Stop and remove containers
docker-compose down

# View logs for specific service
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f redis

# Rebuild after code changes
docker-compose up -d --build
```

---

## Option B: Manual Deployment (Development)

### 1. Install Redis

**Windows:**
```bash
# Using Chocolatey
choco install redis-64

# Or download from: https://github.com/microsoftarchive/redis/releases
```

**macOS:**
```bash
brew install redis
brew services start redis
```

**Linux:**
```bash
sudo apt-get install redis-server
sudo systemctl start redis
```

### 2. Set Up Backend

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Train ML model
python -m backend.train_model

# Start backend server
uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload
```

Backend will be available at: http://localhost:8000

### 3. Set Up Frontend

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev

# Or build for production
npm run build
npm run preview
```

Frontend will be available at: http://localhost:5173 (dev) or http://localhost:4173 (preview)

---

## Production Deployment Options

### Option 1: Cloud Platform (AWS, GCP, Azure)

#### Using AWS Elastic Container Service (ECS)

1. **Push Docker images to ECR:**
   ```bash
   # Authenticate to ECR
   aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <account-id>.dkr.ecr.us-east-1.amazonaws.com
   
   # Tag and push images
   docker tag ai-healthcare-backend:latest <account-id>.dkr.ecr.us-east-1.amazonaws.com/ai-healthcare-backend:latest
   docker push <account-id>.dkr.ecr.us-east-1.amazonaws.com/ai-healthcare-backend:latest
   ```

2. **Create ECS task definitions** for backend, frontend, and Redis
3. **Set up Application Load Balancer**
4. **Configure auto-scaling**

#### Using Google Cloud Run

```bash
# Build and deploy backend
gcloud builds submit --tag gcr.io/PROJECT-ID/backend
gcloud run deploy backend --image gcr.io/PROJECT-ID/backend --platform managed

# Build and deploy frontend
gcloud builds submit --tag gcr.io/PROJECT-ID/frontend
gcloud run deploy frontend --image gcr.io/PROJECT-ID/frontend --platform managed
```

### Option 2: VPS Deployment (DigitalOcean, Linode, AWS EC2)

1. **Provision a VPS** (minimum 2GB RAM, 2 CPU cores)

2. **Install Docker on the server:**
   ```bash
   curl -fsSL https://get.docker.com -o get-docker.sh
   sudo sh get-docker.sh
   sudo usermod -aG docker $USER
   ```

3. **Clone your repository:**
   ```bash
   git clone <your-repo-url>
   cd ai-healthcare
   ```

4. **Configure environment variables:**
   ```bash
   cp .env.example .env
   nano .env  # Edit with production values
   ```

5. **Deploy with Docker Compose:**
   ```bash
   docker-compose up -d --build
   ```

6. **Set up reverse proxy (Nginx):**
   ```nginx
   server {
       listen 80;
       server_name yourdomain.com;
       
       location / {
           proxy_pass http://localhost:3000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }
       
       location /api {
           proxy_pass http://localhost:8000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }
   }
   ```

7. **Set up SSL with Let's Encrypt:**
   ```bash
   sudo apt install certbot python3-certbot-nginx
   sudo certbot --nginx -d yourdomain.com
   ```

### Option 3: Platform as a Service (Heroku, Render, Railway)

#### Render.com (Recommended for ease)

1. Create account at https://render.com
2. Create new **Web Service** for backend
   - Build Command: `pip install -r requirements.txt && python -m backend.train_model`
   - Start Command: `uvicorn backend.app.main:app --host 0.0.0.0 --port $PORT`
3. Create new **Static Site** for frontend
   - Build Command: `cd frontend && npm install && npm run build`
   - Publish Directory: `frontend/dist`
4. Create **Redis** instance
5. Connect services with environment variables

---

## Database Migration (SQLite to PostgreSQL for Production)

For production, migrate from SQLite to PostgreSQL:

### 1. Update requirements.txt
```txt
# Add PostgreSQL driver
psycopg2-binary==2.9.9
```

### 2. Update DATABASE_URL in .env
```env
DATABASE_URL=postgresql://user:password@host:5432/dbname
```

### 3. Update docker-compose.yml
```yaml
services:
  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: healthcare
      POSTGRES_USER: healthcare_user
      POSTGRES_PASSWORD: secure_password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  backend:
    depends_on:
      - postgres
      - redis
    environment:
      - DATABASE_URL=postgresql://healthcare_user:secure_password@postgres:5432/healthcare
```

---

## Monitoring and Maintenance

### Health Checks

```bash
# Backend health
curl http://localhost:8000/api/health

# Redis health
docker-compose exec redis redis-cli ping
```

### View Application Logs

```bash
# Docker logs
docker-compose logs -f

# Backend logs specifically
docker-compose logs -f backend

# Last 100 lines
docker-compose logs --tail=100
```

### Backup Database

```bash
# SQLite backup
docker-compose exec backend cp /app/healthcare.db /app/backups/healthcare_$(date +%Y%m%d).db

# PostgreSQL backup
docker-compose exec postgres pg_dump -U healthcare_user healthcare > backup_$(date +%Y%m%d).sql
```

### Update Application

```bash
# Pull latest code
git pull

# Rebuild and restart
docker-compose up -d --build

# Or for zero-downtime:
docker-compose up -d --no-deps --build backend
docker-compose up -d --no-deps --build frontend
```

---

## Troubleshooting

### Port Already in Use
```bash
# Find process using port 8000
netstat -ano | findstr :8000

# Kill process (Windows)
taskkill /PID <process-id> /F

# Or change port in docker-compose.yml
ports:
  - "8001:8000"  # Map to different host port
```

### Redis Connection Failed
```bash
# Check Redis is running
docker-compose ps redis

# Check Redis logs
docker-compose logs redis

# Restart Redis
docker-compose restart redis
```

### Backend Won't Start
```bash
# Check backend logs
docker-compose logs backend

# Common issues:
# 1. Missing .env file - copy .env.example to .env
# 2. Port conflict - change port in docker-compose.yml
# 3. Redis not ready - ensure depends_on with health check
```

### Frontend Build Fails
```bash
# Clear node_modules and rebuild
docker-compose down
docker-compose build --no-cache frontend
docker-compose up -d
```

---

## Security Checklist for Production

- [ ] Generate new JWT_SECRET with `openssl rand -base64 32`
- [ ] Set DEBUG=false
- [ ] Use PostgreSQL instead of SQLite
- [ ] Enable HTTPS with SSL certificate
- [ ] Set up firewall rules (only allow 80, 443, 22)
- [ ] Use environment variables for secrets (never commit .env)
- [ ] Enable Redis password protection
- [ ] Set up regular database backups
- [ ] Configure CORS to only allow your domain
- [ ] Implement rate limiting
- [ ] Set up monitoring and alerting
- [ ] Keep dependencies updated

---

## Performance Optimization

### Enable Redis Persistence
```yaml
# In docker-compose.yml
redis:
  command: redis-server --appendonly yes --maxmemory 2gb --maxmemory-policy allkeys-lru
```

### Scale Services
```bash
# Run multiple backend instances
docker-compose up -d --scale backend=3
```

### Add Nginx Load Balancer
```nginx
upstream backend {
    least_conn;
    server backend:8000;
}
```

---

## Support

For issues or questions:
- Check logs: `docker-compose logs -f`
- Review `.env` configuration
- Ensure all required API keys are set
- Verify Redis is running: `docker-compose ps redis`

## Quick Start Summary

**Docker Deployment (Fastest):**
```bash
# 1. Install Docker Desktop
# 2. Clone/navigate to project
cd "d:\Coding\AI healthcare"

# 3. Deploy
docker-compose up -d --build

# 4. Access
# Frontend: http://localhost:3000
# Backend: http://localhost:8000/docs
```

**Manual Deployment:**
```bash
# Terminal 1: Redis
redis-server

# Terminal 2: Backend
pip install -r requirements.txt
python -m backend.train_model
uvicorn backend.app.main:app --reload

# Terminal 3: Frontend
cd frontend
npm install
npm run dev
```
