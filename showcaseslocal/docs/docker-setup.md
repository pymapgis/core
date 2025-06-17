# 🐳 Docker Setup Guide for PyMapGIS Local Showcases

![Docker](https://img.shields.io/badge/Docker-Containerization-blue) ![Optimization](https://img.shields.io/badge/Build%20Time-10s-green)

## 🎯 What is Docker?

Docker is a containerization platform that PyMapGIS uses to package local showcases into portable, lightweight containers. Benefits include:

- **🚀 Instant Deployment**: One command to run any showcase
- **⚡ Lightning-Fast Builds**: 10-12 second builds using PyMapGIS base image
- **🔒 Consistent Environment**: Same runtime across all systems
- **📦 Easy Distribution**: Share showcases as Docker images

## 🛠️ Installing Docker

### Windows 11 with WSL2 (Recommended)
```bash
# 1. Install Docker Desktop for Windows
# Download from: https://www.docker.com/products/docker-desktop

# 2. Enable WSL2 integration in Docker Desktop settings
# Settings → Resources → WSL Integration → Enable integration

# 3. Verify installation in WSL2
docker --version
docker-compose --version

# 4. Test Docker
docker run hello-world
```

### macOS
```bash
# 1. Install Docker Desktop for Mac
# Download from: https://www.docker.com/products/docker-desktop

# 2. Verify installation
docker --version
docker-compose --version

# 3. Test Docker
docker run hello-world
```

### Linux (Ubuntu/Debian)
```bash
# 1. Update package index
sudo apt-get update

# 2. Install Docker
sudo apt-get install docker.io docker-compose

# 3. Add user to docker group
sudo usermod -aG docker $USER

# 4. Restart session or run
newgrp docker

# 5. Verify installation
docker --version
docker run hello-world
```

## 🚀 PyMapGIS Docker Optimization Strategy

### Lightning-Fast Builds with Base Image
PyMapGIS local showcases use an optimized base image strategy:

```dockerfile
# Uses pre-built PyMapGIS base with all dependencies
FROM nicholaskarlson/pymapgis-base:latest

# Only copy application-specific files
COPY [showcase-files] ./

# Result: 10-12 second builds instead of 5+ minutes!
```

### Build Performance Metrics
- **Traditional Build**: 5-8 minutes
- **PyMapGIS Optimized**: 10-12 seconds
- **Performance Gain**: 95% faster builds
- **Container Size**: ~200MB optimized

## 🏗️ Building PyMapGIS Local Showcases

### Quick Build Commands
```bash
# Navigate to showcase directory
cd showcaseslocal/[showcase-name]

# Build Docker image
docker build -f Dockerfile -t [showcase-name]:latest ../../

# Example for Food Trucks
cd showcaseslocal/open-food-trucks-now
docker build -f Dockerfile -t open-food-trucks-now:latest ../../
```

### Running Showcases
```bash
# Run any local showcase
docker run -p 8000:8000 [showcase-name]:latest

# Examples:
docker run -p 8000:8000 open-food-trucks-now:latest
docker run -p 8000:8000 open311-pothole-now:latest
docker run -p 8000:8000 transit-crowding-now:latest

# View at: http://localhost:8000
```

### Production Deployment
```bash
# Tag for production
docker tag [showcase-name]:latest nicholaskarlson/[showcase-name]:latest

# Push to Docker Hub
docker push nicholaskarlson/[showcase-name]:latest

# Pull and run from anywhere
docker run -p 8000:8000 nicholaskarlson/[showcase-name]:latest
```

## 🔧 Docker Configuration for PyMapGIS

### Dockerfile Structure
```dockerfile
# Optimized Dockerfile template for PyMapGIS local showcases
FROM nicholaskarlson/pymapgis-base:latest

# Set working directory (inherited from base)
WORKDIR /app

# Copy application files only
COPY showcaseslocal/[showcase-name]/[worker].py ./
COPY showcaseslocal/[showcase-name]/app.py ./
COPY showcaseslocal/[showcase-name]/static/ ./static/
COPY showcaseslocal/[showcase-name]/data/ ./data/

# Create showcase-specific user
USER root
RUN useradd --create-home --shell /bin/bash [username] && \
    chown -R [username]:[username] /app

# Switch to showcase user
USER [username]

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run application
CMD ["python", "-c", "import subprocess; import sys; subprocess.run([sys.executable, '[worker].py']); import app; import uvicorn; uvicorn.run(app.app, host='0.0.0.0', port=8000)"]
```

### Docker Compose (Optional)
```yaml
# docker-compose.yml for local development
version: '3.8'
services:
  showcase:
    build:
      context: ../../
      dockerfile: showcaseslocal/[showcase-name]/Dockerfile
    ports:
      - "8000:8000"
    environment:
      - PYTHONUNBUFFERED=1
    volumes:
      - ./data:/app/data  # For development data persistence
```

## 📊 Performance Optimization

### Base Image Strategy Benefits
- **Layer Caching**: Reuse common dependencies across showcases
- **Reduced Build Time**: Only rebuild application layers
- **Smaller Images**: Shared base layers reduce total size
- **Faster Deployment**: Quick pulls with layer reuse

### Build Optimization Tips
```bash
# Use .dockerignore to exclude unnecessary files
echo "__pycache__" >> .dockerignore
echo "*.pyc" >> .dockerignore
echo ".git" >> .dockerignore

# Multi-stage builds for even smaller images
FROM nicholaskarlson/pymapgis-base:latest as base
# ... build steps ...
FROM base as production
# ... production-only steps ...
```

## 🐛 Troubleshooting

### Common Docker Issues

#### Docker Not Starting
```bash
# Check Docker service status
sudo systemctl status docker

# Start Docker service
sudo systemctl start docker

# Enable Docker on boot
sudo systemctl enable docker
```

#### Permission Denied
```bash
# Add user to docker group
sudo usermod -aG docker $USER

# Restart session or run
newgrp docker

# Test permissions
docker run hello-world
```

#### Build Failures
```bash
# Clear Docker cache
docker system prune -a

# Rebuild without cache
docker build --no-cache -t [image-name] .

# Check disk space
docker system df
```

#### Container Won't Start
```bash
# Check container logs
docker logs [container-id]

# Run container interactively
docker run -it [image-name] /bin/bash

# Check port conflicts
netstat -tulpn | grep 8000
```

## 🔒 Security Best Practices

### Container Security
- **Non-root User**: All PyMapGIS showcases run as non-root users
- **Minimal Base**: Only essential dependencies in base image
- **Health Checks**: Built-in health monitoring
- **Resource Limits**: CPU and memory constraints

### Production Deployment
```bash
# Run with resource limits
docker run -p 8000:8000 \
  --memory=512m \
  --cpus=1.0 \
  --restart=unless-stopped \
  [showcase-name]:latest

# Use Docker secrets for sensitive data
docker secret create api_key api_key.txt
```

## 🌐 Integration with WSL2

### WSL2 + Docker Desktop Setup
```bash
# 1. Ensure WSL2 is default
wsl --set-default-version 2

# 2. Install Ubuntu in WSL2
wsl --install -d Ubuntu

# 3. Enable Docker Desktop WSL2 integration
# Docker Desktop → Settings → Resources → WSL Integration

# 4. Access from WSL2
cd /mnt/c/Users/[username]/pymapgis
docker run -p 8000:8000 open-food-trucks-now:latest
```

## 📚 Additional Resources

- **Docker Documentation**: https://docs.docker.com/
- **Docker Desktop**: https://www.docker.com/products/docker-desktop
- **WSL2 Setup**: https://docs.microsoft.com/en-us/windows/wsl/install
- **PyMapGIS Docker Hub**: https://hub.docker.com/u/nicholaskarlson

## 🎯 Next Steps

1. **Install Docker** using the commands above
2. **Clone PyMapGIS** repository
3. **Build a showcase** with `docker build`
4. **Run the container** with `docker run`
5. **Access the app** at http://localhost:8000

Docker makes PyMapGIS local showcases instantly deployable! 🚀
