# 🚀 Deployment Guide for SCex1 Supply Chain Example

This guide covers various deployment scenarios for the Supply Chain Optimization example, from local development to cloud production environments.

## 📋 Deployment Options

### 1. Local Development
- **Use Case**: Development and testing
- **Requirements**: Docker Desktop
- **Complexity**: Low
- **Scalability**: Single instance

### 2. Docker Hub Deployment
- **Use Case**: Sharing and distribution
- **Requirements**: Docker Hub account
- **Complexity**: Low
- **Scalability**: Pull and run anywhere

### 3. Cloud Platform Deployment
- **Use Case**: Production workloads
- **Requirements**: Cloud account (AWS, Azure, GCP, DigitalOcean)
- **Complexity**: Medium to High
- **Scalability**: High

## 🐳 Docker Hub Deployment

### Prerequisites
- Docker Hub account
- Docker Desktop installed and running
- Built Docker image

### Step 1: Prepare the Image

```bash
# Build the image with proper tagging
cd SCex1
docker build -t nicholaskarlson/scex1-supply-chain:latest -f docker/Dockerfile .

# Tag with version
docker tag nicholaskarlson/scex1-supply-chain:latest nicholaskarlson/scex1-supply-chain:v0.1.0
```

### Step 2: Login to Docker Hub

```bash
# Login to Docker Hub
docker login

# Verify login
docker info | grep Username
```

### Step 3: Push to Docker Hub

```bash
# Push latest tag
docker push nicholaskarlson/scex1-supply-chain:latest

# Push version tag
docker push nicholaskarlson/scex1-supply-chain:v0.1.0
```

### Step 4: Verify Deployment

```bash
# Pull and test the image
docker pull nicholaskarlson/scex1-supply-chain:latest
docker run -d -p 8000:8000 --name test-scex1 nicholaskarlson/scex1-supply-chain:latest

# Test the application
curl http://localhost:8000/health

# Cleanup
docker stop test-scex1 && docker rm test-scex1
```

## ☁️ DigitalOcean Deployment

### Prerequisites
- DigitalOcean account
- `doctl` CLI tool installed
- SSH key configured

### Step 1: Create a Droplet

```bash
# Create a Docker-enabled droplet
doctl compute droplet create scex1-supply-chain \
  --image docker-20-04 \
  --size s-2vcpu-2gb \
  --region nyc1 \
  --ssh-keys YOUR_SSH_KEY_ID

# Get droplet IP
doctl compute droplet list
```

### Step 2: Deploy the Application

```bash
# SSH into the droplet
ssh root@YOUR_DROPLET_IP

# Pull and run the container
docker pull nicholaskarlson/scex1-supply-chain:latest
docker run -d \
  --name scex1-app \
  --restart unless-stopped \
  -p 80:8000 \
  -v /opt/scex1/data:/app/output \
  nicholaskarlson/scex1-supply-chain:latest

# Verify deployment
curl http://localhost/health
```

### Step 3: Configure Firewall

```bash
# Configure UFW firewall
ufw allow ssh
ufw allow http
ufw allow https
ufw --force enable
```

### Step 4: Setup SSL (Optional)

```bash
# Install Certbot
apt update && apt install certbot

# Get SSL certificate (replace with your domain)
certbot certonly --standalone -d your-domain.com

# Configure reverse proxy with SSL
# (See nginx configuration in docker/nginx.conf)
```

## 🌊 AWS ECS Deployment

### Prerequisites
- AWS CLI configured
- ECS CLI installed
- AWS account with appropriate permissions

### Step 1: Create ECS Task Definition

Create `ecs-task-definition.json`:

```json
{
  "family": "scex1-supply-chain",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "512",
  "memory": "1024",
  "executionRoleArn": "arn:aws:iam::YOUR_ACCOUNT:role/ecsTaskExecutionRole",
  "containerDefinitions": [
    {
      "name": "scex1-app",
      "image": "nicholaskarlson/scex1-supply-chain:latest",
      "portMappings": [
        {
          "containerPort": 8000,
          "protocol": "tcp"
        }
      ],
      "essential": true,
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/scex1-supply-chain",
          "awslogs-region": "us-east-1",
          "awslogs-stream-prefix": "ecs"
        }
      },
      "healthCheck": {
        "command": ["CMD-SHELL", "curl -f http://localhost:8000/health || exit 1"],
        "interval": 30,
        "timeout": 5,
        "retries": 3,
        "startPeriod": 60
      }
    }
  ]
}
```

### Step 2: Deploy to ECS

```bash
# Register task definition
aws ecs register-task-definition --cli-input-json file://ecs-task-definition.json

# Create ECS cluster
aws ecs create-cluster --cluster-name scex1-cluster

# Create service
aws ecs create-service \
  --cluster scex1-cluster \
  --service-name scex1-service \
  --task-definition scex1-supply-chain:1 \
  --desired-count 1 \
  --launch-type FARGATE \
  --network-configuration "awsvpcConfiguration={subnets=[subnet-12345],securityGroups=[sg-12345],assignPublicIp=ENABLED}"
```

## 🔧 Production Configuration

### Environment Variables

```bash
# Production environment variables
export SC_ENV=production
export SC_LOG_LEVEL=INFO
export SC_MAX_WORKERS=4
export SC_CACHE_TTL=3600
export SC_CORS_ORIGINS="https://yourdomain.com"
```

### Docker Compose for Production

Create `docker-compose.prod.yml`:

```yaml
version: '3.8'

services:
  scex1-app:
    image: nicholaskarlson/scex1-supply-chain:latest
    restart: unless-stopped
    environment:
      - SC_ENV=production
      - SC_LOG_LEVEL=INFO
    ports:
      - "8000:8000"
    volumes:
      - ./data:/app/output
      - ./logs:/app/logs
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
    deploy:
      resources:
        limits:
          cpus: '1.0'
          memory: 1G
        reservations:
          cpus: '0.5'
          memory: 512M

  nginx:
    image: nginx:alpine
    restart: unless-stopped
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./ssl:/etc/nginx/ssl:ro
    depends_on:
      - scex1-app

  redis:
    image: redis:alpine
    restart: unless-stopped
    volumes:
      - redis_data:/data
    command: redis-server --appendonly yes

volumes:
  redis_data:
```

### Monitoring and Logging

```bash
# Setup log rotation
cat > /etc/logrotate.d/scex1 << EOF
/opt/scex1/logs/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 644 root root
    postrotate
        docker kill -s USR1 scex1-app
    endscript
}
EOF

# Setup monitoring with Prometheus
docker run -d \
  --name prometheus \
  -p 9090:9090 \
  -v ./prometheus.yml:/etc/prometheus/prometheus.yml \
  prom/prometheus
```

## 🔒 Security Considerations

### Container Security

```bash
# Run with non-root user (already configured in Dockerfile)
# Scan for vulnerabilities
docker scan nicholaskarlson/scex1-supply-chain:latest

# Use specific version tags in production
docker pull nicholaskarlson/scex1-supply-chain:v0.1.0
```

### Network Security

```bash
# Configure firewall rules
ufw allow from 10.0.0.0/8 to any port 8000
ufw deny 8000

# Use reverse proxy for SSL termination
# Configure rate limiting
# Implement API authentication if needed
```

### Data Security

```bash
# Encrypt data at rest
# Use secrets management for sensitive configuration
# Regular security updates
apt update && apt upgrade -y
docker pull nicholaskarlson/scex1-supply-chain:latest
```

## 📊 Monitoring and Maintenance

### Health Monitoring

```bash
# Setup health check monitoring
#!/bin/bash
# health-check.sh
HEALTH_URL="http://localhost:8000/health"
if ! curl -f $HEALTH_URL > /dev/null 2>&1; then
    echo "Health check failed, restarting container..."
    docker restart scex1-app
    # Send alert notification
fi
```

### Performance Monitoring

```bash
# Monitor container resources
docker stats scex1-app

# Monitor application metrics
curl http://localhost:8000/metrics

# Setup alerts for high resource usage
```

### Backup and Recovery

```bash
# Backup application data
tar -czf scex1-backup-$(date +%Y%m%d).tar.gz /opt/scex1/data

# Backup configuration
docker inspect scex1-app > scex1-config-backup.json

# Test recovery procedures regularly
```

## 🚀 Scaling Strategies

### Horizontal Scaling

```bash
# Run multiple instances with load balancer
docker run -d --name scex1-app-1 -p 8001:8000 nicholaskarlson/scex1-supply-chain:latest
docker run -d --name scex1-app-2 -p 8002:8000 nicholaskarlson/scex1-supply-chain:latest

# Configure load balancer (nginx, HAProxy, etc.)
```

### Vertical Scaling

```bash
# Increase container resources
docker run -d \
  --name scex1-app \
  --cpus="2.0" \
  --memory="2g" \
  -p 8000:8000 \
  nicholaskarlson/scex1-supply-chain:latest
```

## 📋 Deployment Checklist

### Pre-deployment
- [ ] Image built and tested locally
- [ ] Security scan completed
- [ ] Configuration reviewed
- [ ] Backup procedures in place
- [ ] Monitoring configured

### Deployment
- [ ] Infrastructure provisioned
- [ ] Application deployed
- [ ] Health checks passing
- [ ] SSL certificates configured
- [ ] Firewall rules applied

### Post-deployment
- [ ] Functionality testing completed
- [ ] Performance monitoring active
- [ ] Logs being collected
- [ ] Backup verified
- [ ] Documentation updated

---

*This deployment guide provides comprehensive instructions for deploying the Supply Chain Optimization example across various environments, from development to production.*
