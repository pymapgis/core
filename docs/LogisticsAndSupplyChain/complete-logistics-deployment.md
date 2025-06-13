# 🚀 Complete Logistics Deployment

## End-to-End Deployment Guide for PyMapGIS Logistics Solutions

This comprehensive guide provides complete deployment workflows for PyMapGIS logistics and supply chain applications, from development to production-ready containerized solutions.

### 1. Deployment Architecture Overview

#### Multi-Tier Logistics Deployment
```
Development Environment → Testing Environment → 
Staging Environment → Production Environment → 
Monitoring and Maintenance
```

#### Container Ecosystem Design
```
Base Infrastructure:
├── PyMapGIS Core Container
├── Logistics Analytics Container
├── Real-time Processing Container
├── Web Interface Container
└── Data Management Container

Supporting Services:
├── Database Container (PostgreSQL + PostGIS)
├── Cache Container (Redis)
├── Message Queue Container (RabbitMQ)
├── Monitoring Container (Prometheus + Grafana)
└── Reverse Proxy Container (Nginx)
```

### 2. Complete Deployment Workflow

#### Automated Deployment Script
```bash
#!/bin/bash
# complete-logistics-deploy.sh - One-command deployment

set -e

echo "🚛 Deploying PyMapGIS Logistics Suite..."

# Configuration
DEPLOYMENT_NAME="pymapgis-logistics"
NETWORK_NAME="logistics-network"
DATA_DIR="./logistics-data"
CONFIG_DIR="./logistics-config"

# Create directories
mkdir -p ${DATA_DIR}/{postgres,redis,uploads,exports}
mkdir -p ${CONFIG_DIR}/{nginx,prometheus,grafana}

# Create Docker network
docker network create ${NETWORK_NAME} 2>/dev/null || true

# Deploy database
echo "📊 Deploying database services..."
docker run -d \
  --name ${DEPLOYMENT_NAME}-postgres \
  --network ${NETWORK_NAME} \
  -e POSTGRES_DB=logistics \
  -e POSTGRES_USER=logistics_user \
  -e POSTGRES_PASSWORD=secure_password \
  -v ${DATA_DIR}/postgres:/var/lib/postgresql/data \
  -p 5432:5432 \
  postgis/postgis:14-3.2

# Deploy cache
echo "⚡ Deploying cache services..."
docker run -d \
  --name ${DEPLOYMENT_NAME}-redis \
  --network ${NETWORK_NAME} \
  -v ${DATA_DIR}/redis:/data \
  -p 6379:6379 \
  redis:7-alpine redis-server --appendonly yes

# Deploy core logistics application
echo "🏗️ Deploying core logistics application..."
docker run -d \
  --name ${DEPLOYMENT_NAME}-core \
  --network ${NETWORK_NAME} \
  -e DATABASE_URL=postgresql://logistics_user:secure_password@${DEPLOYMENT_NAME}-postgres:5432/logistics \
  -e REDIS_URL=redis://${DEPLOYMENT_NAME}-redis:6379 \
  -v ${DATA_DIR}/uploads:/app/uploads \
  -v ${DATA_DIR}/exports:/app/exports \
  -p 8888:8888 \
  pymapgis/logistics-core:latest

# Deploy analytics dashboard
echo "📈 Deploying analytics dashboard..."
docker run -d \
  --name ${DEPLOYMENT_NAME}-dashboard \
  --network ${NETWORK_NAME} \
  -e CORE_API_URL=http://${DEPLOYMENT_NAME}-core:8000 \
  -p 8501:8501 \
  pymapgis/logistics-dashboard:latest

# Deploy real-time processor
echo "⚡ Deploying real-time processor..."
docker run -d \
  --name ${DEPLOYMENT_NAME}-realtime \
  --network ${NETWORK_NAME} \
  -e DATABASE_URL=postgresql://logistics_user:secure_password@${DEPLOYMENT_NAME}-postgres:5432/logistics \
  -e REDIS_URL=redis://${DEPLOYMENT_NAME}-redis:6379 \
  pymapgis/logistics-realtime:latest

# Deploy API gateway
echo "🌐 Deploying API gateway..."
docker run -d \
  --name ${DEPLOYMENT_NAME}-api \
  --network ${NETWORK_NAME} \
  -e DATABASE_URL=postgresql://logistics_user:secure_password@${DEPLOYMENT_NAME}-postgres:5432/logistics \
  -p 8000:8000 \
  pymapgis/logistics-api:latest

# Wait for services to be ready
echo "⏳ Waiting for services to start..."
sleep 30

# Health checks
echo "🔍 Performing health checks..."
check_service() {
  local service_name=$1
  local url=$2
  local max_attempts=10
  local attempt=1
  
  while [ $attempt -le $max_attempts ]; do
    if curl -f -s $url > /dev/null 2>&1; then
      echo "✅ $service_name is healthy"
      return 0
    fi
    echo "⏳ Waiting for $service_name (attempt $attempt/$max_attempts)..."
    sleep 5
    ((attempt++))
  done
  
  echo "❌ $service_name failed to start"
  return 1
}

check_service "Core Application" "http://localhost:8888/health"
check_service "Analytics Dashboard" "http://localhost:8501/health"
check_service "API Gateway" "http://localhost:8000/health"

# Initialize database
echo "🗄️ Initializing database..."
docker exec ${DEPLOYMENT_NAME}-postgres psql -U logistics_user -d logistics -c "
CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS postgis_topology;
"

# Load sample data
echo "📊 Loading sample data..."
docker exec ${DEPLOYMENT_NAME}-core python -c "
import pymapgis as pmg
pmg.logistics.initialize_sample_data()
print('✅ Sample data loaded successfully')
"

echo "🎉 Deployment complete!"
echo ""
echo "📊 Access URLs:"
echo "  Jupyter Notebooks: http://localhost:8888"
echo "  Analytics Dashboard: http://localhost:8501"
echo "  API Documentation: http://localhost:8000/docs"
echo ""
echo "🔧 Management Commands:"
echo "  View logs: docker logs ${DEPLOYMENT_NAME}-core"
echo "  Stop all: docker stop \$(docker ps -q --filter name=${DEPLOYMENT_NAME})"
echo "  Remove all: docker rm \$(docker ps -aq --filter name=${DEPLOYMENT_NAME})"
```

### 3. Docker Compose Deployment

#### Production Docker Compose Configuration
```yaml
# docker-compose.logistics.yml
version: '3.8'

services:
  postgres:
    image: postgis/postgis:14-3.2
    container_name: logistics-postgres
    environment:
      POSTGRES_DB: logistics
      POSTGRES_USER: logistics_user
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./init-scripts:/docker-entrypoint-initdb.d
    ports:
      - "5432:5432"
    networks:
      - logistics-network
    restart: unless-stopped
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U logistics_user -d logistics"]
      interval: 30s
      timeout: 10s
      retries: 3

  redis:
    image: redis:7-alpine
    container_name: logistics-redis
    command: redis-server --appendonly yes --requirepass ${REDIS_PASSWORD}
    volumes:
      - redis_data:/data
    ports:
      - "6379:6379"
    networks:
      - logistics-network
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "redis-cli", "--raw", "incr", "ping"]
      interval: 30s
      timeout: 10s
      retries: 3

  logistics-core:
    image: pymapgis/logistics-core:${VERSION:-latest}
    container_name: logistics-core
    environment:
      - DATABASE_URL=postgresql://logistics_user:${POSTGRES_PASSWORD}@postgres:5432/logistics
      - REDIS_URL=redis://:${REDIS_PASSWORD}@redis:6379
      - SECRET_KEY=${SECRET_KEY}
      - ENVIRONMENT=production
    volumes:
      - uploads_data:/app/uploads
      - exports_data:/app/exports
      - ./config/logistics:/app/config
    ports:
      - "8888:8888"
      - "8000:8000"
    networks:
      - logistics-network
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  logistics-dashboard:
    image: pymapgis/logistics-dashboard:${VERSION:-latest}
    container_name: logistics-dashboard
    environment:
      - CORE_API_URL=http://logistics-core:8000
      - REDIS_URL=redis://:${REDIS_PASSWORD}@redis:6379
    ports:
      - "8501:8501"
    networks:
      - logistics-network
    depends_on:
      logistics-core:
        condition: service_healthy
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8501/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  logistics-realtime:
    image: pymapgis/logistics-realtime:${VERSION:-latest}
    container_name: logistics-realtime
    environment:
      - DATABASE_URL=postgresql://logistics_user:${POSTGRES_PASSWORD}@postgres:5432/logistics
      - REDIS_URL=redis://:${REDIS_PASSWORD}@redis:6379
      - KAFKA_BROKERS=${KAFKA_BROKERS:-localhost:9092}
    networks:
      - logistics-network
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    restart: unless-stopped

  nginx:
    image: nginx:alpine
    container_name: logistics-nginx
    volumes:
      - ./config/nginx/nginx.conf:/etc/nginx/nginx.conf
      - ./config/nginx/ssl:/etc/nginx/ssl
    ports:
      - "80:80"
      - "443:443"
    networks:
      - logistics-network
    depends_on:
      - logistics-core
      - logistics-dashboard
    restart: unless-stopped

  prometheus:
    image: prom/prometheus:latest
    container_name: logistics-prometheus
    volumes:
      - ./config/prometheus/prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus_data:/prometheus
    ports:
      - "9090:9090"
    networks:
      - logistics-network
    restart: unless-stopped

  grafana:
    image: grafana/grafana:latest
    container_name: logistics-grafana
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=${GRAFANA_PASSWORD}
    volumes:
      - grafana_data:/var/lib/grafana
      - ./config/grafana/dashboards:/etc/grafana/provisioning/dashboards
      - ./config/grafana/datasources:/etc/grafana/provisioning/datasources
    ports:
      - "3000:3000"
    networks:
      - logistics-network
    restart: unless-stopped

volumes:
  postgres_data:
  redis_data:
  uploads_data:
  exports_data:
  prometheus_data:
  grafana_data:

networks:
  logistics-network:
    driver: bridge
```

### 4. Environment Configuration

#### Environment Variables Configuration
```bash
# .env file for deployment configuration
# Database Configuration
POSTGRES_PASSWORD=your_secure_postgres_password
REDIS_PASSWORD=your_secure_redis_password

# Application Configuration
SECRET_KEY=your_secret_key_here
VERSION=latest
ENVIRONMENT=production

# External Services
KAFKA_BROKERS=localhost:9092
GRAFANA_PASSWORD=your_grafana_password

# API Keys
OPENSTREETMAP_API_KEY=your_osm_api_key
WEATHER_API_KEY=your_weather_api_key
TRAFFIC_API_KEY=your_traffic_api_key

# Monitoring
SENTRY_DSN=your_sentry_dsn
LOG_LEVEL=INFO

# Resource Limits
MAX_WORKERS=4
MEMORY_LIMIT=2G
CPU_LIMIT=2.0
```

#### Nginx Configuration
```nginx
# config/nginx/nginx.conf
events {
    worker_connections 1024;
}

http {
    upstream logistics_core {
        server logistics-core:8000;
    }
    
    upstream logistics_dashboard {
        server logistics-dashboard:8501;
    }
    
    server {
        listen 80;
        server_name localhost;
        
        # Core API
        location /api/ {
            proxy_pass http://logistics_core/;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
        
        # Jupyter Notebooks
        location /notebooks/ {
            proxy_pass http://logistics_core:8888/;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            
            # WebSocket support
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection "upgrade";
        }
        
        # Analytics Dashboard
        location /dashboard/ {
            proxy_pass http://logistics_dashboard/;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            
            # WebSocket support for Streamlit
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection "upgrade";
        }
        
        # Static files
        location /static/ {
            alias /var/www/static/;
            expires 1y;
            add_header Cache-Control "public, immutable";
        }
    }
}
```

### 5. Database Initialization

#### Database Setup Script
```sql
-- init-scripts/01-init-logistics.sql
-- Initialize logistics database with PostGIS

-- Enable PostGIS extensions
CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS postgis_topology;
CREATE EXTENSION IF NOT EXISTS postgis_raster;
CREATE EXTENSION IF NOT EXISTS fuzzystrmatch;
CREATE EXTENSION IF NOT EXISTS postgis_tiger_geocoder;

-- Create logistics schema
CREATE SCHEMA IF NOT EXISTS logistics;

-- Create tables for logistics data
CREATE TABLE IF NOT EXISTS logistics.facilities (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    type VARCHAR(100) NOT NULL,
    address TEXT,
    geometry GEOMETRY(POINT, 4326),
    capacity INTEGER,
    operating_hours JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS logistics.vehicles (
    id SERIAL PRIMARY KEY,
    vehicle_id VARCHAR(100) UNIQUE NOT NULL,
    type VARCHAR(100) NOT NULL,
    capacity_weight DECIMAL(10,2),
    capacity_volume DECIMAL(10,2),
    fuel_type VARCHAR(50),
    status VARCHAR(50) DEFAULT 'available',
    current_location GEOMETRY(POINT, 4326),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS logistics.routes (
    id SERIAL PRIMARY KEY,
    route_name VARCHAR(255),
    vehicle_id INTEGER REFERENCES logistics.vehicles(id),
    start_facility_id INTEGER REFERENCES logistics.facilities(id),
    end_facility_id INTEGER REFERENCES logistics.facilities(id),
    route_geometry GEOMETRY(LINESTRING, 4326),
    distance_km DECIMAL(10,2),
    duration_minutes INTEGER,
    status VARCHAR(50) DEFAULT 'planned',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS logistics.deliveries (
    id SERIAL PRIMARY KEY,
    delivery_id VARCHAR(100) UNIQUE NOT NULL,
    route_id INTEGER REFERENCES logistics.routes(id),
    customer_name VARCHAR(255),
    delivery_address TEXT,
    delivery_location GEOMETRY(POINT, 4326),
    scheduled_time TIMESTAMP,
    actual_time TIMESTAMP,
    status VARCHAR(50) DEFAULT 'pending',
    weight_kg DECIMAL(10,2),
    volume_m3 DECIMAL(10,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create spatial indexes
CREATE INDEX IF NOT EXISTS idx_facilities_geometry ON logistics.facilities USING GIST (geometry);
CREATE INDEX IF NOT EXISTS idx_vehicles_location ON logistics.vehicles USING GIST (current_location);
CREATE INDEX IF NOT EXISTS idx_routes_geometry ON logistics.routes USING GIST (route_geometry);
CREATE INDEX IF NOT EXISTS idx_deliveries_location ON logistics.deliveries USING GIST (delivery_location);

-- Create performance indexes
CREATE INDEX IF NOT EXISTS idx_vehicles_status ON logistics.vehicles (status);
CREATE INDEX IF NOT EXISTS idx_routes_status ON logistics.routes (status);
CREATE INDEX IF NOT EXISTS idx_deliveries_status ON logistics.deliveries (status);
CREATE INDEX IF NOT EXISTS idx_deliveries_scheduled_time ON logistics.deliveries (scheduled_time);

-- Insert sample data
INSERT INTO logistics.facilities (name, type, address, geometry, capacity) VALUES
('Main Warehouse', 'warehouse', '123 Industrial Blvd, City, State', ST_SetSRID(ST_MakePoint(-74.0060, 40.7128), 4326), 10000),
('Distribution Center North', 'distribution', '456 Commerce St, North City, State', ST_SetSRID(ST_MakePoint(-73.9857, 40.7484), 4326), 5000),
('Distribution Center South', 'distribution', '789 Logistics Ave, South City, State', ST_SetSRID(ST_MakePoint(-74.0445, 40.6892), 4326), 5000);

INSERT INTO logistics.vehicles (vehicle_id, type, capacity_weight, capacity_volume, fuel_type) VALUES
('TRUCK-001', 'delivery_truck', 5000.00, 25.00, 'diesel'),
('TRUCK-002', 'delivery_truck', 5000.00, 25.00, 'diesel'),
('VAN-001', 'delivery_van', 2000.00, 12.00, 'gasoline'),
('VAN-002', 'delivery_van', 2000.00, 12.00, 'electric');

-- Grant permissions
GRANT ALL PRIVILEGES ON SCHEMA logistics TO logistics_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA logistics TO logistics_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA logistics TO logistics_user;
```

### 6. Monitoring and Health Checks

#### Prometheus Configuration
```yaml
# config/prometheus/prometheus.yml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

rule_files:
  - "logistics_rules.yml"

scrape_configs:
  - job_name: 'logistics-core'
    static_configs:
      - targets: ['logistics-core:8000']
    metrics_path: '/metrics'
    scrape_interval: 30s

  - job_name: 'logistics-dashboard'
    static_configs:
      - targets: ['logistics-dashboard:8501']
    metrics_path: '/metrics'
    scrape_interval: 30s

  - job_name: 'postgres'
    static_configs:
      - targets: ['postgres:5432']
    scrape_interval: 30s

  - job_name: 'redis'
    static_configs:
      - targets: ['redis:6379']
    scrape_interval: 30s

alerting:
  alertmanagers:
    - static_configs:
        - targets:
          - alertmanager:9093
```

#### Health Check Script
```bash
#!/bin/bash
# health-check.sh - Comprehensive health monitoring

check_container_health() {
    local container_name=$1
    local health_status=$(docker inspect --format='{{.State.Health.Status}}' $container_name 2>/dev/null)
    
    if [ "$health_status" = "healthy" ]; then
        echo "✅ $container_name: healthy"
        return 0
    else
        echo "❌ $container_name: $health_status"
        return 1
    fi
}

check_service_endpoint() {
    local service_name=$1
    local url=$2
    local expected_status=${3:-200}
    
    local status_code=$(curl -s -o /dev/null -w "%{http_code}" $url)
    
    if [ "$status_code" = "$expected_status" ]; then
        echo "✅ $service_name endpoint: accessible"
        return 0
    else
        echo "❌ $service_name endpoint: HTTP $status_code"
        return 1
    fi
}

echo "🔍 Performing comprehensive health check..."

# Check container health
check_container_health "logistics-postgres"
check_container_health "logistics-redis"
check_container_health "logistics-core"
check_container_health "logistics-dashboard"

# Check service endpoints
check_service_endpoint "Core API" "http://localhost:8000/health"
check_service_endpoint "Dashboard" "http://localhost:8501/health"
check_service_endpoint "Jupyter" "http://localhost:8888/api/status"

# Check database connectivity
echo "🗄️ Checking database connectivity..."
if docker exec logistics-postgres pg_isready -U logistics_user -d logistics > /dev/null 2>&1; then
    echo "✅ Database: connected"
else
    echo "❌ Database: connection failed"
fi

# Check Redis connectivity
echo "⚡ Checking Redis connectivity..."
if docker exec logistics-redis redis-cli ping > /dev/null 2>&1; then
    echo "✅ Redis: connected"
else
    echo "❌ Redis: connection failed"
fi

echo "🔍 Health check complete"
```

### 7. Backup and Recovery

#### Automated Backup Script
```bash
#!/bin/bash
# backup-logistics.sh - Automated backup solution

BACKUP_DIR="/backup/logistics"
DATE=$(date +%Y%m%d_%H%M%S)
RETENTION_DAYS=30

mkdir -p $BACKUP_DIR

echo "📦 Starting logistics backup..."

# Database backup
echo "🗄️ Backing up database..."
docker exec logistics-postgres pg_dump -U logistics_user -d logistics | gzip > $BACKUP_DIR/postgres_$DATE.sql.gz

# Redis backup
echo "⚡ Backing up Redis..."
docker exec logistics-redis redis-cli BGSAVE
docker cp logistics-redis:/data/dump.rdb $BACKUP_DIR/redis_$DATE.rdb

# Application data backup
echo "📊 Backing up application data..."
docker run --rm -v logistics_uploads_data:/data -v $BACKUP_DIR:/backup alpine tar czf /backup/uploads_$DATE.tar.gz -C /data .
docker run --rm -v logistics_exports_data:/data -v $BACKUP_DIR:/backup alpine tar czf /backup/exports_$DATE.tar.gz -C /data .

# Configuration backup
echo "⚙️ Backing up configuration..."
tar czf $BACKUP_DIR/config_$DATE.tar.gz ./config

# Clean old backups
echo "🧹 Cleaning old backups..."
find $BACKUP_DIR -name "*.gz" -mtime +$RETENTION_DAYS -delete
find $BACKUP_DIR -name "*.rdb" -mtime +$RETENTION_DAYS -delete

echo "✅ Backup complete: $BACKUP_DIR"
```

### 8. Deployment Validation

#### Comprehensive Deployment Test
```python
#!/usr/bin/env python3
# test-deployment.py - Validate complete deployment

import requests
import time
import sys
import json

def test_endpoint(name, url, expected_status=200, timeout=30):
    """Test service endpoint availability."""
    try:
        response = requests.get(url, timeout=timeout)
        if response.status_code == expected_status:
            print(f"✅ {name}: OK ({response.status_code})")
            return True
        else:
            print(f"❌ {name}: HTTP {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ {name}: {str(e)}")
        return False

def test_api_functionality():
    """Test core API functionality."""
    base_url = "http://localhost:8000"
    
    # Test health endpoint
    if not test_endpoint("API Health", f"{base_url}/health"):
        return False
    
    # Test facilities endpoint
    if not test_endpoint("Facilities API", f"{base_url}/api/facilities"):
        return False
    
    # Test vehicles endpoint
    if not test_endpoint("Vehicles API", f"{base_url}/api/vehicles"):
        return False
    
    return True

def test_dashboard_functionality():
    """Test dashboard functionality."""
    if not test_endpoint("Dashboard Health", "http://localhost:8501/health"):
        return False
    
    return True

def test_database_connectivity():
    """Test database operations."""
    try:
        response = requests.get("http://localhost:8000/api/facilities")
        if response.status_code == 200:
            data = response.json()
            if len(data) > 0:
                print("✅ Database: Connected and populated")
                return True
            else:
                print("⚠️ Database: Connected but empty")
                return False
    except Exception as e:
        print(f"❌ Database: {str(e)}")
        return False

def main():
    """Run comprehensive deployment tests."""
    print("🧪 Running deployment validation tests...")
    
    tests = [
        ("API Functionality", test_api_functionality),
        ("Dashboard Functionality", test_dashboard_functionality),
        ("Database Connectivity", test_database_connectivity),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🔍 Testing {test_name}...")
        if test_func():
            passed += 1
        else:
            print(f"❌ {test_name} failed")
    
    print(f"\n📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Deployment is successful.")
        sys.exit(0)
    else:
        print("❌ Some tests failed. Please check the deployment.")
        sys.exit(1)

if __name__ == "__main__":
    main()
```

---

*This complete deployment guide provides comprehensive workflows for deploying PyMapGIS logistics solutions from development to production with monitoring, backup, and validation capabilities.*
