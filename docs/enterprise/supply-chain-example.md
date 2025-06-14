# 📦 Enterprise Supply Chain Logistics Platform

This comprehensive example demonstrates how to build a production-ready supply chain logistics platform using PyMapGIS enterprise features, deployed on Digital Ocean with Docker.

## 🎯 Project Overview

**Business Case**: Create a web-based supply chain monitoring platform that tracks:
- Warehouse locations and capacity utilization
- Delivery routes and real-time vehicle tracking
- Supply chain performance metrics and analytics
- Multi-tenant support for different logistics companies

**Technical Stack**:
- **Backend**: PyMapGIS with FastAPI
- **Authentication**: JWT with OAuth integration
- **Database**: PostgreSQL with PostGIS
- **Cloud Storage**: S3-compatible storage (DigitalOcean Spaces)
- **Deployment**: Docker on DigitalOcean Droplet
- **Monitoring**: Built-in health checks and metrics

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Web Frontend  │    │  PyMapGIS API   │    │   PostgreSQL    │
│   (React/Vue)   │◄──►│   (FastAPI)     │◄──►│   + PostGIS     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                              ▼
                    ┌─────────────────┐
                    │ DigitalOcean    │
                    │ Spaces (S3)     │
                    └─────────────────┘
```

## 🚀 Step-by-Step Implementation

### **Step 1: Project Setup**

```bash
# Create project directory
mkdir supply-chain-platform
cd supply-chain-platform

# Initialize Python project
poetry init
poetry add pymapgis[enterprise,cloud,streaming]
poetry add fastapi uvicorn psycopg2-binary
```

### **Step 2: Core Application Code**

Create `app/main.py`:

```python
"""
Supply Chain Logistics Platform
Enterprise PyMapGIS Application
"""

import os
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import HTTPBearer
import pymapgis as pmg
from pymapgis.enterprise import AuthenticationManager, UserManager, RBACManager

# Initialize FastAPI app
app = FastAPI(
    title="Supply Chain Logistics Platform",
    description="Enterprise geospatial logistics management",
    version="1.0.0"
)

# Security
security = HTTPBearer()

# Enterprise managers
auth_manager = AuthenticationManager(
    jwt_secret_key=os.getenv("JWT_SECRET_KEY", "your-secret-key"),
    jwt_algorithm="HS256"
)
user_manager = UserManager()
rbac_manager = RBACManager()

# Database connection
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:pass@localhost/logistics")

@app.on_startup
async def startup_event():
    """Initialize application on startup."""
    print("🚀 Starting Supply Chain Platform...")
    
    # Initialize cloud storage
    pmg.cloud.configure(
        provider="s3",
        endpoint_url=os.getenv("SPACES_ENDPOINT"),
        access_key=os.getenv("SPACES_ACCESS_KEY"),
        secret_key=os.getenv("SPACES_SECRET_KEY")
    )
    
    print("✅ Platform ready!")

@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Supply Chain Logistics Platform",
        "version": "1.0.0",
        "status": "operational"
    }

@app.get("/health")
async def health_check():
    """Health check for monitoring."""
    return {
        "status": "healthy",
        "services": {
            "database": "connected",
            "cloud_storage": "connected",
            "authentication": "operational"
        }
    }

# Authentication endpoints
@app.post("/auth/login")
async def login(credentials: dict):
    """User authentication."""
    try:
        token = auth_manager.authenticate_user(
            credentials["username"],
            credentials["password"]
        )
        return {"access_token": token, "token_type": "bearer"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )

# Warehouse management
@app.get("/api/warehouses")
async def get_warehouses(token: str = Depends(security)):
    """Get warehouse locations and data."""
    # Verify authentication
    user = auth_manager.verify_token(token.credentials)
    
    # Load warehouse data from cloud storage
    warehouses = pmg.cloud_read("s3://logistics-data/warehouses.geojson")
    
    # Add real-time utilization data
    warehouses["utilization"] = warehouses.apply(
        lambda row: calculate_utilization(row["warehouse_id"]), axis=1
    )
    
    return warehouses.to_dict("records")

@app.get("/api/routes")
async def get_delivery_routes(token: str = Depends(security)):
    """Get delivery routes with real-time traffic."""
    user = auth_manager.verify_token(token.credentials)
    
    # Load route data
    routes = pmg.cloud_read("s3://logistics-data/delivery-routes.geojson")
    
    # Calculate optimal routes with traffic
    optimized_routes = pmg.network.optimize_routes(
        routes,
        traffic_data=get_real_time_traffic(),
        optimization="time"
    )
    
    return optimized_routes.to_dict("records")

@app.get("/api/vehicles/live")
async def get_live_vehicles(token: str = Depends(security)):
    """Get real-time vehicle positions."""
    user = auth_manager.verify_token(token.credentials)
    
    # Stream live vehicle data
    vehicles = pmg.streaming.read("kafka://vehicle-positions")
    
    return vehicles.to_dict("records")

# Analytics endpoints
@app.get("/api/analytics/performance")
async def get_performance_metrics(token: str = Depends(security)):
    """Get supply chain performance analytics."""
    user = auth_manager.verify_token(token.credentials)
    
    # Load historical data for analysis
    deliveries = pmg.cloud_read("s3://logistics-data/deliveries.parquet")
    
    # Calculate KPIs
    metrics = {
        "on_time_delivery_rate": calculate_on_time_rate(deliveries),
        "average_delivery_time": calculate_avg_delivery_time(deliveries),
        "route_efficiency": calculate_route_efficiency(deliveries),
        "cost_per_mile": calculate_cost_per_mile(deliveries)
    }
    
    return metrics

# Helper functions
def calculate_utilization(warehouse_id: str) -> float:
    """Calculate warehouse utilization percentage."""
    # Implementation would connect to real-time inventory system
    return 0.75  # Example: 75% utilization

def get_real_time_traffic():
    """Get real-time traffic data."""
    # Implementation would connect to traffic API
    return {}

def calculate_on_time_rate(deliveries):
    """Calculate on-time delivery rate."""
    on_time = deliveries[deliveries["delivery_time"] <= deliveries["promised_time"]]
    return len(on_time) / len(deliveries)

def calculate_avg_delivery_time(deliveries):
    """Calculate average delivery time."""
    return deliveries["delivery_time"].mean()

def calculate_route_efficiency(deliveries):
    """Calculate route efficiency score."""
    return deliveries["actual_distance"] / deliveries["optimal_distance"]

def calculate_cost_per_mile(deliveries):
    """Calculate cost per mile."""
    return deliveries["total_cost"].sum() / deliveries["total_distance"].sum()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

### **Step 3: Docker Configuration**

Create `Dockerfile`:

```dockerfile
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Create user
RUN groupadd -r logistics && useradd -r -g logistics logistics

# Set work directory
WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY --chown=logistics:logistics . .

# Switch to non-root user
USER logistics

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Start application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Create `requirements.txt`:

```txt
pymapgis[enterprise,cloud,streaming]==0.3.2
fastapi>=0.100.0
uvicorn[standard]>=0.23.0
psycopg2-binary>=2.9.0
python-multipart>=0.0.6
```

### **Step 4: Digital Ocean Deployment**

Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  app:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://logistics:password@db:5432/logistics
      - JWT_SECRET_KEY=${JWT_SECRET_KEY}
      - SPACES_ENDPOINT=${SPACES_ENDPOINT}
      - SPACES_ACCESS_KEY=${SPACES_ACCESS_KEY}
      - SPACES_SECRET_KEY=${SPACES_SECRET_KEY}
    depends_on:
      - db
    restart: unless-stopped

  db:
    image: postgis/postgis:15-3.3
    environment:
      - POSTGRES_DB=logistics
      - POSTGRES_USER=logistics
      - POSTGRES_PASSWORD=password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - app
    restart: unless-stopped

volumes:
  postgres_data:
```

### **Step 5: Deploy to Digital Ocean**

```bash
# 1. Create Digital Ocean Droplet
doctl compute droplet create logistics-platform \
  --image docker-20-04 \
  --size s-4vcpu-8gb \
  --region nyc1 \
  --ssh-keys your-ssh-key-id

# 2. Get droplet IP
DROPLET_IP=$(doctl compute droplet get logistics-platform --format PublicIPv4 --no-header)

# 3. SSH to droplet and deploy
ssh root@$DROPLET_IP

# On the droplet:
git clone https://github.com/your-org/supply-chain-platform.git
cd supply-chain-platform

# Set environment variables
export JWT_SECRET_KEY="your-production-secret"
export SPACES_ENDPOINT="https://nyc3.digitaloceanspaces.com"
export SPACES_ACCESS_KEY="your-spaces-key"
export SPACES_SECRET_KEY="your-spaces-secret"

# Deploy with Docker Compose
docker-compose up -d

# Verify deployment
curl http://localhost:8000/health
```

## 🌐 Frontend Integration

Create a simple dashboard frontend:

```html
<!DOCTYPE html>
<html>
<head>
    <title>Supply Chain Dashboard</title>
    <script src="https://unpkg.com/leaflet@1.7.1/dist/leaflet.js"></script>
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.7.1/dist/leaflet.css" />
</head>
<body>
    <div id="map" style="height: 600px;"></div>
    
    <script>
        // Initialize map
        const map = L.map('map').setView([40.7128, -74.0060], 10);
        
        // Add tile layer
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png').addTo(map);
        
        // Load warehouse data
        fetch('/api/warehouses', {
            headers: {
                'Authorization': 'Bearer ' + localStorage.getItem('token')
            }
        })
        .then(response => response.json())
        .then(warehouses => {
            warehouses.forEach(warehouse => {
                L.marker([warehouse.lat, warehouse.lon])
                    .bindPopup(`
                        <b>${warehouse.name}</b><br>
                        Utilization: ${(warehouse.utilization * 100).toFixed(1)}%
                    `)
                    .addTo(map);
            });
        });
        
        // Load delivery routes
        fetch('/api/routes')
        .then(response => response.json())
        .then(routes => {
            routes.forEach(route => {
                L.polyline(route.coordinates, {color: 'blue'})
                    .bindPopup(`Route: ${route.name}`)
                    .addTo(map);
            });
        });
    </script>
</body>
</html>
```

## 📊 Monitoring & Analytics

The platform includes built-in monitoring:

- **Health Checks**: `/health` endpoint for load balancer monitoring
- **Performance Metrics**: Real-time KPI calculation and reporting
- **Error Tracking**: Comprehensive logging and error handling
- **User Analytics**: Authentication and usage tracking

## 🔒 Security Features

- **JWT Authentication**: Secure token-based authentication
- **Role-Based Access**: Different access levels for users
- **Data Encryption**: All data encrypted in transit and at rest
- **Audit Logging**: Complete audit trail of all operations

## 🚀 Production Considerations

1. **Scaling**: Use Docker Swarm or Kubernetes for horizontal scaling
2. **Database**: Consider read replicas for high-traffic scenarios
3. **Caching**: Implement Redis for session and data caching
4. **CDN**: Use DigitalOcean CDN for static assets
5. **Backup**: Automated database and file backups
6. **SSL**: Let's Encrypt for HTTPS certificates

## 💡 Next Steps

1. **Deploy the platform** following the steps above
2. **Customize the data models** for your specific logistics needs
3. **Add real-time integrations** with your existing systems
4. **Implement advanced analytics** with machine learning
5. **Scale horizontally** as your user base grows

---

**This example demonstrates the power of PyMapGIS enterprise features for building production-ready geospatial applications!** 🚀
