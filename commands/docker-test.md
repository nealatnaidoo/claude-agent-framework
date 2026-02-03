---
description: Build and run project in Docker for local testing
allowed-tools: Bash(docker:*), Bash(ls:*), Bash(cat:*), Bash(curl:*)
---

<docker-test>

## Context Discovery

Project structure:
!`ls -la Dockerfile docker-compose.yml fly.toml 2>/dev/null || echo "Checking subdirectories..."`

Frontend check:
!`ls -la frontend/Dockerfile 2>/dev/null || echo "No frontend Dockerfile"`

Backend check:
!`ls -la Dockerfile 2>/dev/null || ls -la backend/Dockerfile 2>/dev/null || echo "No backend Dockerfile"`

Running containers:
!`docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" 2>/dev/null || echo "Docker not available"`

## Your Task

You are invoking a **Docker Test Deployment** via the DevOps Governor.

### Step 1: Detect Project Type

Identify what can be containerized:
- **Frontend only**: `frontend/Dockerfile` exists
- **Backend only**: Root `Dockerfile` or `backend/Dockerfile` exists
- **Full stack**: Both frontend and backend Dockerfiles exist
- **Compose**: `docker-compose.yml` exists

### Step 2: Check Docker Status

Verify Docker is running:
```bash
docker info > /dev/null 2>&1 || (open -a Docker && sleep 15)
```

### Step 3: Build and Run

**For Frontend:**
```bash
cd frontend
docker build -t {project}-frontend-test --build-arg NEXT_PUBLIC_API_URL=http://host.docker.internal:8000 .
docker rm -f {project}-frontend-test 2>/dev/null || true
docker run -d --name {project}-frontend-test -p 3001:3000 --restart unless-stopped {project}-frontend-test
```

**For Backend:**
```bash
docker build -t {project}-backend-test .
docker rm -f {project}-backend-test 2>/dev/null || true
docker run -d --name {project}-backend-test -p 8001:8000 -e LAB_DATA_DIR=/data -v $(pwd)/data:/data --restart unless-stopped {project}-backend-test
```

**For Full Stack (docker-compose):**
```bash
docker-compose -f docker-compose.yml up -d --build
```

### Step 4: Health Check

Wait for containers and verify health:
```bash
sleep 5
# Frontend
curl -s -o /dev/null -w "%{http_code}" http://localhost:3001/ || echo "Frontend not responding"
# Backend
curl -s -o /dev/null -w "%{http_code}" http://localhost:8001/health || echo "Backend not responding"
```

### Step 5: Report Status

Display deployment summary:

```
## Docker Test Deployment

**Status:** Running ✅

### Access URLs
| Service | URL | Status |
|---------|-----|--------|
| Frontend | http://localhost:3001 | {status} |
| Backend | http://localhost:8001 | {status} |

### Containers
{docker ps output for project containers}

### Commands
- View logs: `docker logs {container-name}`
- Stop all: `docker stop {containers} && docker rm {containers}`
- Rebuild: `/docker-test`

### Notes
- Frontend API calls go to host.docker.internal:8000 (your local backend)
- If localhost doesn't work, try your machine's IP address
- Data persists in ./data volume
```

### Step 6: Cleanup Command

Provide cleanup instructions:
```bash
# Stop and remove test containers
docker stop {project}-frontend-test {project}-backend-test 2>/dev/null
docker rm {project}-frontend-test {project}-backend-test 2>/dev/null
```

## Arguments

Optional arguments:
- `frontend` - Only build/run frontend
- `backend` - Only build/run backend
- `stop` - Stop and remove test containers
- `logs` - Show container logs
- `rebuild` - Force rebuild (no cache)

Example: `/docker-test frontend` or `/docker-test stop`

</docker-test>
