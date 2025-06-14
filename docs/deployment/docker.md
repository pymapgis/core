# 🐳 PyMapGIS Docker Deployment

This guide covers production-ready Docker deployment of PyMapGIS applications with enterprise features, health monitoring, and cloud integration.

## 🚀 Quick Start

### **Pull Official Image**
```bash
# Pull latest production image
docker pull pymapgis/core:latest

# Run with health monitoring
docker run -d \
  --name pymapgis-server \
  -p 8000:8000 \
  --health-cmd="curl -f http://localhost:8000/health" \
  --health-interval=30s \
  --health-timeout=10s \
  --health-retries=3 \
  pymapgis/core:latest
```

### **Verify Deployment**
```bash
# Check container status
docker ps

# Check health status
docker inspect pymapgis-server | grep Health -A 10

# Test API endpoint
curl http://localhost:8000/health
```

## 🏗️ Custom Application Dockerfile

### **Basic Application**
```dockerfile
# Use PyMapGIS base image
FROM pymapgis/core:latest

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install additional dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY --chown=pymapgis:pymapgis . .

# Expose application port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Start application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### **Enterprise Application with Authentication**
```dockerfile
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Create application user
RUN groupadd -r pymapgis && useradd -r -g pymapgis pymapgis

# Set work directory
WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY --chown=pymapgis:pymapgis . .

# Switch to non-root user
USER pymapgis

# Environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYMAPGIS_ENV=production

# Expose port
EXPOSE 8000

# Health check with authentication
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Start with Gunicorn for production
CMD ["gunicorn", "app.main:app", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000"]
```

## 🔧 Docker Compose for Full Stack

### **Production Stack**
```yaml
version: '3.8'

services:
  app:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://pymapgis:${DB_PASSWORD}@db:5432/pymapgis
      - REDIS_URL=redis://redis:6379/0
      - JWT_SECRET_KEY=${JWT_SECRET_KEY}
      - AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID}
      - AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY}
      - PYMAPGIS_ENV=production
    depends_on:
      - db
      - redis
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  db:
    image: postgis/postgis:15-3.3
    environment:
      - POSTGRES_DB=pymapgis
      - POSTGRES_USER=pymapgis
      - POSTGRES_PASSWORD=${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./init.sql:/docker-entrypoint-initdb.d/init.sql
    restart: unless-stopped
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U pymapgis"]
      interval: 30s
      timeout: 10s
      retries: 3

  redis:
    image: redis:7-alpine
    command: redis-server --appendonly yes
    volumes:
      - redis_data:/data
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 30s
      timeout: 10s
      retries: 3

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
      - static_files:/var/www/static
    depends_on:
      - app
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost/health"]
      interval: 30s
      timeout: 10s
      retries: 3

volumes:
  postgres_data:
  redis_data:
  static_files:

networks:
  default:
    driver: bridge
```

### **Environment Configuration**
```bash
# .env file
DB_PASSWORD=secure_database_password
JWT_SECRET_KEY=your_jwt_secret_key_here
AWS_ACCESS_KEY_ID=your_aws_access_key
AWS_SECRET_ACCESS_KEY=your_aws_secret_key
REDIS_PASSWORD=secure_redis_password
```

## 🌐 Production Deployment

### **Digital Ocean Droplet**
```bash
# Create droplet with Docker
doctl compute droplet create pymapgis-prod \
  --image docker-20-04 \
  --size s-4vcpu-8gb \
  --region nyc1 \
  --ssh-keys your-ssh-key-id \
  --user-data-file cloud-init.yml

# Get droplet IP
DROPLET_IP=$(doctl compute droplet get pymapgis-prod --format PublicIPv4 --no-header)

# Deploy application
ssh root@$DROPLET_IP
git clone https://github.com/your-org/pymapgis-app.git
cd pymapgis-app
docker-compose up -d
```

### **AWS ECS Deployment**
```json
{
  "family": "pymapgis-app",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "1024",
  "memory": "2048",
  "executionRoleArn": "arn:aws:iam::account:role/ecsTaskExecutionRole",
  "taskRoleArn": "arn:aws:iam::account:role/ecsTaskRole",
  "containerDefinitions": [
    {
      "name": "pymapgis-app",
      "image": "your-account.dkr.ecr.region.amazonaws.com/pymapgis-app:latest",
      "portMappings": [
        {
          "containerPort": 8000,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {
          "name": "PYMAPGIS_ENV",
          "value": "production"
        }
      ],
      "secrets": [
        {
          "name": "JWT_SECRET_KEY",
          "valueFrom": "arn:aws:secretsmanager:region:account:secret:pymapgis/jwt-secret"
        }
      ],
      "healthCheck": {
        "command": ["CMD-SHELL", "curl -f http://localhost:8000/health || exit 1"],
        "interval": 30,
        "timeout": 5,
        "retries": 3
      },
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/pymapgis-app",
          "awslogs-region": "us-east-1",
          "awslogs-stream-prefix": "ecs"
        }
      }
    }
  ]
}
```

### **Google Cloud Run**
```yaml
apiVersion: serving.knative.dev/v1
kind: Service
metadata:
  name: pymapgis-app
  annotations:
    run.googleapis.com/ingress: all
spec:
  template:
    metadata:
      annotations:
        autoscaling.knative.dev/maxScale: "10"
        run.googleapis.com/cpu-throttling: "false"
    spec:
      containerConcurrency: 80
      containers:
      - image: gcr.io/your-project/pymapgis-app:latest
        ports:
        - containerPort: 8000
        env:
        - name: PYMAPGIS_ENV
          value: "production"
        - name: JWT_SECRET_KEY
          valueFrom:
            secretKeyRef:
              name: pymapgis-secrets
              key: jwt-secret
        resources:
          limits:
            cpu: "2"
            memory: "4Gi"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 30
```

## 📊 Monitoring & Logging

### **Health Check Configuration**
```python
# app/health.py
from fastapi import FastAPI
import pymapgis as pmg

app = FastAPI()

@app.get("/health")
async def health_check():
    """Comprehensive health check."""
    health_status = {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": pmg.__version__,
        "checks": {}
    }
    
    # Database connectivity
    try:
        # Test database connection
        health_status["checks"]["database"] = "healthy"
    except Exception as e:
        health_status["checks"]["database"] = f"unhealthy: {e}"
        health_status["status"] = "unhealthy"
    
    # Redis connectivity
    try:
        # Test Redis connection
        health_status["checks"]["redis"] = "healthy"
    except Exception as e:
        health_status["checks"]["redis"] = f"unhealthy: {e}"
        health_status["status"] = "degraded"
    
    # Cloud storage connectivity
    try:
        # Test cloud storage
        health_status["checks"]["cloud_storage"] = "healthy"
    except Exception as e:
        health_status["checks"]["cloud_storage"] = f"unhealthy: {e}"
        health_status["status"] = "degraded"
    
    return health_status

@app.get("/metrics")
async def metrics():
    """Prometheus-compatible metrics."""
    return {
        "pymapgis_requests_total": 1000,
        "pymapgis_request_duration_seconds": 0.1,
        "pymapgis_cache_hits_total": 800,
        "pymapgis_cache_misses_total": 200
    }
```

### **Logging Configuration**
```python
# app/logging_config.py
import logging
import sys
from pythonjsonlogger import jsonlogger

def setup_logging():
    """Configure structured logging for production."""
    
    # Create JSON formatter
    formatter = jsonlogger.JsonFormatter(
        '%(asctime)s %(name)s %(levelname)s %(message)s'
    )
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    # PyMapGIS specific logging
    pymapgis_logger = logging.getLogger("pymapgis")
    pymapgis_logger.setLevel(logging.INFO)
    
    return root_logger
```

## 🔒 Security Best Practices

### **Secure Dockerfile**
```dockerfile
# Use specific version tags
FROM python:3.11.7-slim

# Create non-root user
RUN groupadd -r pymapgis && useradd -r -g pymapgis pymapgis

# Install security updates
RUN apt-get update && apt-get upgrade -y && \
    apt-get install -y --no-install-recommends curl && \
    rm -rf /var/lib/apt/lists/*

# Set secure permissions
COPY --chown=pymapgis:pymapgis . /app
WORKDIR /app

# Switch to non-root user
USER pymapgis

# Remove unnecessary packages
RUN pip uninstall -y pip setuptools

# Use read-only filesystem
VOLUME ["/tmp"]
```

### **Environment Security**
```bash
# Use Docker secrets for sensitive data
echo "your-jwt-secret" | docker secret create jwt_secret -

# Run with security options
docker run -d \
  --name pymapgis-secure \
  --read-only \
  --tmpfs /tmp \
  --security-opt no-new-privileges \
  --cap-drop ALL \
  --cap-add NET_BIND_SERVICE \
  pymapgis/core:latest
```

## 🚀 Performance Optimization

### **Multi-stage Build**
```dockerfile
# Build stage
FROM python:3.11-slim as builder

WORKDIR /app
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# Production stage
FROM python:3.11-slim

# Copy Python packages from builder
COPY --from=builder /root/.local /root/.local

# Copy application
COPY . /app
WORKDIR /app

# Update PATH
ENV PATH=/root/.local/bin:$PATH

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### **Resource Limits**
```yaml
# docker-compose.yml
services:
  app:
    deploy:
      resources:
        limits:
          cpus: '2.0'
          memory: 4G
        reservations:
          cpus: '1.0'
          memory: 2G
```

## 🔧 Troubleshooting

### **Common Issues**
```bash
# Check container logs
docker logs pymapgis-server

# Debug container
docker exec -it pymapgis-server /bin/bash

# Check health status
docker inspect pymapgis-server | grep Health -A 10

# Monitor resource usage
docker stats pymapgis-server
```

### **Performance Monitoring**
```bash
# Install monitoring tools
docker run -d \
  --name prometheus \
  -p 9090:9090 \
  prom/prometheus

docker run -d \
  --name grafana \
  -p 3000:3000 \
  grafana/grafana
```

---

**Deploy PyMapGIS applications with confidence using Docker!** 🐳🚀
