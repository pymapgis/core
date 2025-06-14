# 🐳 Supply Chain Docker Examples

## Industry-Specific Containerized Solutions

This guide provides comprehensive Docker examples for PyMapGIS logistics applications, covering industry-specific containerized solutions, deployment patterns, and production-ready configurations for supply chain operations.

### 1. Docker Examples Framework

#### Comprehensive Containerization System
```python
import pymapgis as pmg
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import asyncio
from typing import Dict, List, Optional
import json
import docker
import yaml
import os

class SupplyChainDockerSystem:
    def __init__(self, config):
        self.config = config
        self.container_manager = ContainerManager(config.get('containers', {}))
        self.deployment_manager = DeploymentManager(config.get('deployment', {}))
        self.orchestration_manager = OrchestrationManager(config.get('orchestration', {}))
        self.monitoring_manager = MonitoringManager(config.get('monitoring', {}))
        self.security_manager = DockerSecurityManager(config.get('security', {}))
        self.scaling_manager = ScalingManager(config.get('scaling', {}))
    
    async def deploy_docker_examples(self, docker_requirements):
        """Deploy comprehensive Docker examples system."""
        
        # Container management and configuration
        container_management = await self.container_manager.deploy_container_management(
            docker_requirements.get('containers', {})
        )
        
        # Deployment patterns and strategies
        deployment_patterns = await self.deployment_manager.deploy_deployment_patterns(
            docker_requirements.get('deployment', {})
        )
        
        # Orchestration and coordination
        orchestration_coordination = await self.orchestration_manager.deploy_orchestration_coordination(
            docker_requirements.get('orchestration', {})
        )
        
        # Monitoring and observability
        monitoring_observability = await self.monitoring_manager.deploy_monitoring_observability(
            docker_requirements.get('monitoring', {})
        )
        
        # Security and compliance
        security_compliance = await self.security_manager.deploy_security_compliance(
            docker_requirements.get('security', {})
        )
        
        # Scaling and performance
        scaling_performance = await self.scaling_manager.deploy_scaling_performance(
            docker_requirements.get('scaling', {})
        )
        
        return {
            'container_management': container_management,
            'deployment_patterns': deployment_patterns,
            'orchestration_coordination': orchestration_coordination,
            'monitoring_observability': monitoring_observability,
            'security_compliance': security_compliance,
            'scaling_performance': scaling_performance,
            'docker_readiness_score': await self.calculate_docker_readiness()
        }
```

### 2. Industry-Specific Container Examples

#### Retail Supply Chain Container
```dockerfile
# Retail Supply Chain Analytics Container
FROM python:3.11-slim

LABEL maintainer="PyMapGIS Team"
LABEL description="Retail Supply Chain Analytics with PyMapGIS"
LABEL version="1.0.0"

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV RETAIL_ENV=production
ENV PYMAPGIS_CONFIG=/app/config/retail_config.yaml

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gdal-bin \
    libgdal-dev \
    libproj-dev \
    libgeos-dev \
    libspatialite7 \
    spatialite-bin \
    postgresql-client \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create application directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements/retail_requirements.txt .
RUN pip install --no-cache-dir -r retail_requirements.txt

# Copy application code
COPY src/ ./src/
COPY config/ ./config/
COPY data/retail/ ./data/
COPY scripts/retail/ ./scripts/

# Create necessary directories
RUN mkdir -p /app/logs /app/output /app/cache

# Set permissions
RUN chmod +x scripts/*.sh

# Expose ports
EXPOSE 8000 8080

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Default command
CMD ["python", "src/retail_analytics.py"]
```

#### Manufacturing Supply Chain Container
```dockerfile
# Manufacturing Supply Chain Optimization Container
FROM python:3.11-slim

LABEL maintainer="PyMapGIS Team"
LABEL description="Manufacturing Supply Chain Optimization with PyMapGIS"
LABEL version="1.0.0"

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV MANUFACTURING_ENV=production
ENV PYMAPGIS_CONFIG=/app/config/manufacturing_config.yaml

# Install system dependencies for manufacturing analytics
RUN apt-get update && apt-get install -y \
    gdal-bin \
    libgdal-dev \
    libproj-dev \
    libgeos-dev \
    libspatialite7 \
    spatialite-bin \
    postgresql-client \
    redis-tools \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create application directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements/manufacturing_requirements.txt .
RUN pip install --no-cache-dir -r manufacturing_requirements.txt

# Copy application code
COPY src/ ./src/
COPY config/ ./config/
COPY data/manufacturing/ ./data/
COPY scripts/manufacturing/ ./scripts/

# Create necessary directories
RUN mkdir -p /app/logs /app/output /app/cache /app/models

# Set permissions
RUN chmod +x scripts/*.sh

# Expose ports for manufacturing services
EXPOSE 8000 8080 8081

# Health check for manufacturing services
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Default command
CMD ["python", "src/manufacturing_optimizer.py"]
```

### 3. Docker Compose Examples

#### Complete Retail Analytics Stack
```yaml
# docker-compose.retail.yml
version: '3.8'

services:
  # Retail Analytics Application
  retail-analytics:
    build:
      context: .
      dockerfile: dockerfiles/Dockerfile.retail
    container_name: retail-analytics
    environment:
      - POSTGRES_HOST=retail-db
      - REDIS_HOST=retail-cache
      - PYMAPGIS_ENV=production
    ports:
      - "8000:8000"
      - "8080:8080"
    volumes:
      - ./data/retail:/app/data
      - ./logs:/app/logs
      - ./output:/app/output
    depends_on:
      - retail-db
      - retail-cache
    networks:
      - retail-network
    restart: unless-stopped

  # PostgreSQL Database with PostGIS
  retail-db:
    image: postgis/postgis:15-3.3
    container_name: retail-db
    environment:
      - POSTGRES_DB=retail_supply_chain
      - POSTGRES_USER=retail_user
      - POSTGRES_PASSWORD=secure_password
      - POSTGRES_INITDB_ARGS=--encoding=UTF-8
    ports:
      - "5432:5432"
    volumes:
      - retail_db_data:/var/lib/postgresql/data
      - ./sql/retail:/docker-entrypoint-initdb.d
    networks:
      - retail-network
    restart: unless-stopped

  # Redis Cache
  retail-cache:
    image: redis:7-alpine
    container_name: retail-cache
    ports:
      - "6379:6379"
    volumes:
      - retail_cache_data:/data
    networks:
      - retail-network
    restart: unless-stopped

  # Jupyter Notebook for Analysis
  retail-notebook:
    build:
      context: .
      dockerfile: dockerfiles/Dockerfile.notebook
    container_name: retail-notebook
    environment:
      - JUPYTER_ENABLE_LAB=yes
      - JUPYTER_TOKEN=retail_analytics_token
    ports:
      - "8888:8888"
    volumes:
      - ./notebooks/retail:/home/jovyan/work
      - ./data/retail:/home/jovyan/data
    depends_on:
      - retail-db
      - retail-cache
    networks:
      - retail-network
    restart: unless-stopped

  # Monitoring with Grafana
  retail-monitoring:
    image: grafana/grafana:latest
    container_name: retail-monitoring
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin_password
    ports:
      - "3000:3000"
    volumes:
      - retail_grafana_data:/var/lib/grafana
      - ./monitoring/retail/dashboards:/etc/grafana/provisioning/dashboards
      - ./monitoring/retail/datasources:/etc/grafana/provisioning/datasources
    networks:
      - retail-network
    restart: unless-stopped

volumes:
  retail_db_data:
  retail_cache_data:
  retail_grafana_data:

networks:
  retail-network:
    driver: bridge
```

#### Manufacturing Optimization Stack
```yaml
# docker-compose.manufacturing.yml
version: '3.8'

services:
  # Manufacturing Optimization Application
  manufacturing-optimizer:
    build:
      context: .
      dockerfile: dockerfiles/Dockerfile.manufacturing
    container_name: manufacturing-optimizer
    environment:
      - POSTGRES_HOST=manufacturing-db
      - REDIS_HOST=manufacturing-cache
      - RABBITMQ_HOST=manufacturing-queue
      - PYMAPGIS_ENV=production
    ports:
      - "8000:8000"
      - "8080:8080"
      - "8081:8081"
    volumes:
      - ./data/manufacturing:/app/data
      - ./logs:/app/logs
      - ./output:/app/output
      - ./models:/app/models
    depends_on:
      - manufacturing-db
      - manufacturing-cache
      - manufacturing-queue
    networks:
      - manufacturing-network
    restart: unless-stopped

  # PostgreSQL Database with PostGIS
  manufacturing-db:
    image: postgis/postgis:15-3.3
    container_name: manufacturing-db
    environment:
      - POSTGRES_DB=manufacturing_supply_chain
      - POSTGRES_USER=manufacturing_user
      - POSTGRES_PASSWORD=secure_password
    ports:
      - "5433:5432"
    volumes:
      - manufacturing_db_data:/var/lib/postgresql/data
      - ./sql/manufacturing:/docker-entrypoint-initdb.d
    networks:
      - manufacturing-network
    restart: unless-stopped

  # Redis Cache
  manufacturing-cache:
    image: redis:7-alpine
    container_name: manufacturing-cache
    ports:
      - "6380:6379"
    volumes:
      - manufacturing_cache_data:/data
    networks:
      - manufacturing-network
    restart: unless-stopped

  # RabbitMQ Message Queue
  manufacturing-queue:
    image: rabbitmq:3-management-alpine
    container_name: manufacturing-queue
    environment:
      - RABBITMQ_DEFAULT_USER=manufacturing_user
      - RABBITMQ_DEFAULT_PASS=queue_password
    ports:
      - "5672:5672"
      - "15672:15672"
    volumes:
      - manufacturing_queue_data:/var/lib/rabbitmq
    networks:
      - manufacturing-network
    restart: unless-stopped

  # Machine Learning Model Server
  manufacturing-ml:
    build:
      context: .
      dockerfile: dockerfiles/Dockerfile.ml
    container_name: manufacturing-ml
    environment:
      - MODEL_PATH=/app/models
      - REDIS_HOST=manufacturing-cache
    ports:
      - "8082:8082"
    volumes:
      - ./models:/app/models
      - ./data/manufacturing:/app/data
    depends_on:
      - manufacturing-cache
    networks:
      - manufacturing-network
    restart: unless-stopped

  # Real-time Data Processor
  manufacturing-processor:
    build:
      context: .
      dockerfile: dockerfiles/Dockerfile.processor
    container_name: manufacturing-processor
    environment:
      - POSTGRES_HOST=manufacturing-db
      - REDIS_HOST=manufacturing-cache
      - RABBITMQ_HOST=manufacturing-queue
    volumes:
      - ./data/manufacturing:/app/data
      - ./logs:/app/logs
    depends_on:
      - manufacturing-db
      - manufacturing-cache
      - manufacturing-queue
    networks:
      - manufacturing-network
    restart: unless-stopped

volumes:
  manufacturing_db_data:
  manufacturing_cache_data:
  manufacturing_queue_data:

networks:
  manufacturing-network:
    driver: bridge
```

### 4. Kubernetes Deployment Examples

#### Retail Analytics Kubernetes Deployment
```yaml
# k8s/retail/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: retail-analytics
  namespace: supply-chain
  labels:
    app: retail-analytics
    tier: application
spec:
  replicas: 3
  selector:
    matchLabels:
      app: retail-analytics
  template:
    metadata:
      labels:
        app: retail-analytics
    spec:
      containers:
      - name: retail-analytics
        image: pymapgis/retail-analytics:latest
        ports:
        - containerPort: 8000
        - containerPort: 8080
        env:
        - name: POSTGRES_HOST
          value: "retail-db-service"
        - name: REDIS_HOST
          value: "retail-cache-service"
        - name: PYMAPGIS_ENV
          value: "production"
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "1Gi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
        volumeMounts:
        - name: data-volume
          mountPath: /app/data
        - name: logs-volume
          mountPath: /app/logs
      volumes:
      - name: data-volume
        persistentVolumeClaim:
          claimName: retail-data-pvc
      - name: logs-volume
        persistentVolumeClaim:
          claimName: retail-logs-pvc

---
apiVersion: v1
kind: Service
metadata:
  name: retail-analytics-service
  namespace: supply-chain
spec:
  selector:
    app: retail-analytics
  ports:
  - name: http
    port: 80
    targetPort: 8000
  - name: api
    port: 8080
    targetPort: 8080
  type: LoadBalancer
```

### 5. Production Configuration Examples

#### Environment Configuration
```yaml
# config/production.yaml
environment: production

database:
  host: ${POSTGRES_HOST}
  port: 5432
  name: ${POSTGRES_DB}
  user: ${POSTGRES_USER}
  password: ${POSTGRES_PASSWORD}
  pool_size: 20
  max_overflow: 30

cache:
  host: ${REDIS_HOST}
  port: 6379
  db: 0
  password: ${REDIS_PASSWORD}
  max_connections: 50

logging:
  level: INFO
  format: json
  handlers:
    - console
    - file
  file_path: /app/logs/application.log
  max_size: 100MB
  backup_count: 5

monitoring:
  enabled: true
  metrics_port: 9090
  health_check_port: 8000
  prometheus_enabled: true

security:
  ssl_enabled: true
  cors_enabled: true
  allowed_origins:
    - "https://analytics.company.com"
    - "https://dashboard.company.com"

performance:
  worker_processes: 4
  worker_connections: 1000
  keepalive_timeout: 65
  client_max_body_size: 10M

pymapgis:
  cache_dir: /app/cache
  default_crs: EPSG:4326
  max_memory_usage: 2GB
  parallel_processing: true
  optimization_level: high
```

### 6. Monitoring and Observability

#### Prometheus Configuration
```yaml
# monitoring/prometheus.yml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

rule_files:
  - "rules/*.yml"

scrape_configs:
  - job_name: 'retail-analytics'
    static_configs:
      - targets: ['retail-analytics:9090']
    metrics_path: /metrics
    scrape_interval: 10s

  - job_name: 'manufacturing-optimizer'
    static_configs:
      - targets: ['manufacturing-optimizer:9090']
    metrics_path: /metrics
    scrape_interval: 10s

  - job_name: 'postgres-exporter'
    static_configs:
      - targets: ['postgres-exporter:9187']

  - job_name: 'redis-exporter'
    static_configs:
      - targets: ['redis-exporter:9121']

alerting:
  alertmanagers:
    - static_configs:
        - targets:
          - alertmanager:9093
```

#### Grafana Dashboard Configuration
```json
{
  "dashboard": {
    "title": "Supply Chain Analytics Dashboard",
    "tags": ["pymapgis", "supply-chain", "analytics"],
    "timezone": "UTC",
    "panels": [
      {
        "title": "Application Performance",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(http_requests_total[5m])",
            "legendFormat": "Request Rate"
          },
          {
            "expr": "histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))",
            "legendFormat": "95th Percentile Latency"
          }
        ]
      },
      {
        "title": "Database Performance",
        "type": "graph",
        "targets": [
          {
            "expr": "pg_stat_database_tup_fetched",
            "legendFormat": "Tuples Fetched"
          },
          {
            "expr": "pg_stat_database_tup_inserted",
            "legendFormat": "Tuples Inserted"
          }
        ]
      }
    ]
  }
}
```

---

*This comprehensive Docker examples guide provides industry-specific containerized solutions, deployment patterns, and production-ready configurations for PyMapGIS logistics applications.*
