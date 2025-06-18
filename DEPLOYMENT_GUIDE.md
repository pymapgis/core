# 🚀 PyMapGIS Production Deployment Guide

![Deployment](https://img.shields.io/badge/PyMapGIS-Production%20Deployment-blue) ![Status](https://img.shields.io/badge/Status-Enterprise%20Ready-success) ![Security](https://img.shields.io/badge/Security-Hardened-gold)

## 🎯 **Production-Ready Deployment**

This guide provides comprehensive instructions for deploying PyMapGIS showcases in production environments with enterprise-grade security, monitoring, and scalability.

## 🏗️ **Deployment Architecture Options**

### **🐳 Single Container Deployment (Recommended for Demos)**
**Best for**: Proof of concepts, demos, small-scale deployments
**Resources**: 1 CPU, 512MB RAM, minimal storage
**Complexity**: Low
**Scalability**: Limited

### **☁️ Cloud Platform Deployment (Recommended for Production)**
**Best for**: Production workloads, high availability, global reach
**Resources**: Auto-scaling, load balancing, managed services
**Complexity**: Medium
**Scalability**: Unlimited

### **🏢 Enterprise Kubernetes Deployment**
**Best for**: Large organizations, multi-tenant, high security
**Resources**: Kubernetes cluster, enterprise features
**Complexity**: High
**Scalability**: Enterprise-grade

## 🚀 **Quick Production Deployment**

### **1. 🌊 DigitalOcean Droplet (5 minutes)**
```bash
# Create optimized droplet
doctl compute droplet create pymapgis-prod \
  --image docker-20-04 \
  --size s-2vcpu-4gb \
  --region nyc1 \
  --ssh-keys your-ssh-key-id

# SSH into droplet
doctl compute ssh pymapgis-prod

# Deploy showcase
docker run -d \
  --name quake-impact-prod \
  --restart unless-stopped \
  -p 80:8000 \
  --health-cmd="curl -f http://localhost:8000/health" \
  --health-interval=30s \
  --health-retries=3 \
  nicholaskarlson/quake-impact-now:latest

# Verify deployment
curl http://your-droplet-ip/health
```

### **2. ☁️ AWS ECS Deployment (10 minutes)**
```bash
# Create ECS cluster
aws ecs create-cluster --cluster-name pymapgis-cluster

# Create task definition
aws ecs register-task-definition \
  --cli-input-json file://ecs-task-definition.json

# Create service
aws ecs create-service \
  --cluster pymapgis-cluster \
  --service-name quake-impact-service \
  --task-definition quake-impact-task \
  --desired-count 2 \
  --load-balancers targetGroupArn=arn:aws:elasticloadbalancing:...,containerName=quake-impact,containerPort=8000
```

### **3. 🌐 Google Cloud Run (3 minutes)**
```bash
# Deploy to Cloud Run
gcloud run deploy quake-impact-now \
  --image nicholaskarlson/quake-impact-now:latest \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --port 8000 \
  --memory 512Mi \
  --cpu 1 \
  --max-instances 10

# Get service URL
gcloud run services describe quake-impact-now \
  --platform managed \
  --region us-central1 \
  --format 'value(status.url)'
```

## 🔒 **Security Hardening**

### **🛡️ Container Security**
```dockerfile
# Use non-root user
FROM nicholaskarlson/pymapgis-base:latest
USER 1000:1000

# Remove unnecessary packages
RUN apt-get remove -y curl wget && \
    apt-get autoremove -y && \
    rm -rf /var/lib/apt/lists/*

# Set security headers
ENV PYTHONPATH=/app
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
```

### **🔐 Environment Security**
```bash
# Use secrets management
export API_KEYS_SECRET_ARN="arn:aws:secretsmanager:..."
export TLS_CERT_SECRET_ARN="arn:aws:secretsmanager:..."

# Enable security scanning
docker run --rm -v /var/run/docker.sock:/var/run/docker.sock \
  aquasec/trivy image nicholaskarlson/quake-impact-now:latest

# Network security
iptables -A INPUT -p tcp --dport 8000 -j ACCEPT
iptables -A INPUT -p tcp --dport 22 -j ACCEPT
iptables -A INPUT -j DROP
```

### **🌐 HTTPS/TLS Configuration**
```nginx
# Nginx reverse proxy with SSL
server {
    listen 443 ssl http2;
    server_name your-domain.com;
    
    ssl_certificate /etc/ssl/certs/your-cert.pem;
    ssl_certificate_key /etc/ssl/private/your-key.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512;
    
    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## 📊 **Monitoring & Observability**

### **🔍 Health Monitoring**
```yaml
# Docker Compose with monitoring
version: '3.8'
services:
  quake-impact:
    image: nicholaskarlson/quake-impact-now:latest
    ports:
      - "8000:8000"
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
    restart: unless-stopped
    
  prometheus:
    image: prom/prometheus:latest
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
      
  grafana:
    image: grafana/grafana:latest
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=secure_password
```

### **📈 Application Metrics**
```python
# Add to app.py for metrics collection
from prometheus_client import Counter, Histogram, generate_latest
import time

REQUEST_COUNT = Counter('http_requests_total', 'Total HTTP requests', ['method', 'endpoint'])
REQUEST_LATENCY = Histogram('http_request_duration_seconds', 'HTTP request latency')

@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    
    REQUEST_COUNT.labels(method=request.method, endpoint=request.url.path).inc()
    REQUEST_LATENCY.observe(process_time)
    
    return response

@app.get("/metrics")
async def metrics():
    return Response(generate_latest(), media_type="text/plain")
```

### **📋 Logging Configuration**
```python
# Structured logging setup
import logging
import json
from datetime import datetime

class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'level': record.levelname,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno
        }
        return json.dumps(log_entry)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('/var/log/pymapgis.log')
    ]
)

logger = logging.getLogger(__name__)
logger.handlers[0].setFormatter(JSONFormatter())
```

## ⚡ **Performance Optimization**

### **🚀 Container Optimization**
```dockerfile
# Multi-stage build for minimal size
FROM python:3.11-slim as builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

FROM python:3.11-slim
WORKDIR /app
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY . .
EXPOSE 8000
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
```

### **📊 Load Balancing**
```yaml
# HAProxy configuration
global
    daemon
    maxconn 4096

defaults
    mode http
    timeout connect 5000ms
    timeout client 50000ms
    timeout server 50000ms

frontend pymapgis_frontend
    bind *:80
    default_backend pymapgis_backend

backend pymapgis_backend
    balance roundrobin
    option httpchk GET /health
    server app1 10.0.1.10:8000 check
    server app2 10.0.1.11:8000 check
    server app3 10.0.1.12:8000 check
```

### **💾 Caching Strategy**
```python
# Redis caching for API responses
import redis
import json
from functools import wraps

redis_client = redis.Redis(host='localhost', port=6379, db=0)

def cache_response(expiration=300):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            cache_key = f"{func.__name__}:{hash(str(args) + str(kwargs))}"
            
            # Try to get from cache
            cached_result = redis_client.get(cache_key)
            if cached_result:
                return json.loads(cached_result)
            
            # Execute function and cache result
            result = await func(*args, **kwargs)
            redis_client.setex(cache_key, expiration, json.dumps(result))
            
            return result
        return wrapper
    return decorator

@cache_response(expiration=180)  # 3 minutes
async def get_transit_data():
    # Expensive API call
    pass
```

## 🌍 **Multi-Region Deployment**

### **🌐 Global CDN Setup**
```bash
# CloudFlare CDN configuration
curl -X POST "https://api.cloudflare.com/client/v4/zones" \
  -H "Authorization: Bearer your-api-token" \
  -H "Content-Type: application/json" \
  --data '{
    "name": "your-domain.com",
    "type": "full"
  }'

# Enable caching rules
curl -X POST "https://api.cloudflare.com/client/v4/zones/zone-id/pagerules" \
  -H "Authorization: Bearer your-api-token" \
  -H "Content-Type: application/json" \
  --data '{
    "targets": [{"target": "url", "constraint": {"operator": "matches", "value": "*.your-domain.com/static/*"}}],
    "actions": [{"id": "cache_level", "value": "cache_everything"}]
  }'
```

### **🌎 Regional Deployment Strategy**
```yaml
# Kubernetes multi-region deployment
apiVersion: apps/v1
kind: Deployment
metadata:
  name: pymapgis-showcase
spec:
  replicas: 3
  selector:
    matchLabels:
      app: pymapgis-showcase
  template:
    metadata:
      labels:
        app: pymapgis-showcase
    spec:
      affinity:
        podAntiAffinity:
          preferredDuringSchedulingIgnoredDuringExecution:
          - weight: 100
            podAffinityTerm:
              labelSelector:
                matchExpressions:
                - key: app
                  operator: In
                  values:
                  - pymapgis-showcase
              topologyKey: kubernetes.io/zone
      containers:
      - name: showcase
        image: nicholaskarlson/quake-impact-now:latest
        ports:
        - containerPort: 8000
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
```

## 🔧 **Maintenance & Updates**

### **🔄 Zero-Downtime Deployment**
```bash
# Blue-green deployment script
#!/bin/bash

# Deploy new version (green)
docker run -d --name pymapgis-green \
  -p 8001:8000 \
  nicholaskarlson/quake-impact-now:latest

# Health check
sleep 30
if curl -f http://localhost:8001/health; then
  # Switch traffic (update load balancer)
  # Stop old version (blue)
  docker stop pymapgis-blue
  docker rm pymapgis-blue
  
  # Rename green to blue
  docker rename pymapgis-green pymapgis-blue
  
  echo "Deployment successful"
else
  # Rollback
  docker stop pymapgis-green
  docker rm pymapgis-green
  echo "Deployment failed, rolled back"
fi
```

### **📊 Backup & Recovery**
```bash
# Automated backup script
#!/bin/bash

BACKUP_DIR="/backups/$(date +%Y%m%d)"
mkdir -p $BACKUP_DIR

# Backup container volumes
docker run --rm -v pymapgis_data:/data -v $BACKUP_DIR:/backup \
  alpine tar czf /backup/data.tar.gz -C /data .

# Backup configuration
cp -r /etc/pymapgis/ $BACKUP_DIR/config/

# Upload to cloud storage
aws s3 sync $BACKUP_DIR s3://pymapgis-backups/$(date +%Y%m%d)/

echo "Backup completed: $BACKUP_DIR"
```

## 📋 **Production Checklist**

### **🔒 Security Checklist**
- [ ] Container runs as non-root user
- [ ] Secrets managed securely (not in environment variables)
- [ ] HTTPS/TLS enabled with valid certificates
- [ ] Security headers configured
- [ ] Container image scanned for vulnerabilities
- [ ] Network access restricted (firewall rules)
- [ ] Regular security updates scheduled

### **📊 Monitoring Checklist**
- [ ] Health checks configured and working
- [ ] Application metrics collected
- [ ] Log aggregation set up
- [ ] Alerting rules configured
- [ ] Performance monitoring enabled
- [ ] Uptime monitoring from external service
- [ ] Error tracking and notification

### **⚡ Performance Checklist**
- [ ] Load testing completed
- [ ] Caching strategy implemented
- [ ] CDN configured for static assets
- [ ] Database queries optimized
- [ ] Container resources properly sized
- [ ] Auto-scaling configured
- [ ] Performance baselines established

### **🔄 Operations Checklist**
- [ ] Automated deployment pipeline
- [ ] Backup and recovery procedures tested
- [ ] Rollback procedures documented
- [ ] Maintenance windows scheduled
- [ ] Documentation updated
- [ ] Team training completed
- [ ] Incident response plan ready

---

**🚀 This deployment guide ensures PyMapGIS showcases run reliably in production with enterprise-grade security and performance.**

*Ready to deploy PyMapGIS in production? Follow this guide for a robust, scalable, and secure deployment.*
