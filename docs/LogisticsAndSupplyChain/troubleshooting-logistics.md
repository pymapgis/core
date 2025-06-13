# 🔧 Troubleshooting Logistics

## Comprehensive Problem-Solving Guide for PyMapGIS Logistics

This guide provides systematic troubleshooting for common issues encountered when running PyMapGIS logistics and supply chain applications.

### 1. Quick Diagnostic Commands

#### System Health Check
```bash
#!/bin/bash
# quick-health-check.sh - Run this first for any issues

echo "🔍 PyMapGIS Logistics Health Check"
echo "=================================="

# Check WSL2 status
echo "📋 WSL2 Status:"
wsl --status
echo ""

# Check Docker status
echo "🐳 Docker Status:"
docker --version
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
echo ""

# Check service endpoints
echo "🌐 Service Endpoints:"
services=("http://localhost:8000/health" "http://localhost:8501/health" "http://localhost:8888/api/status")
for service in "${services[@]}"; do
    if curl -f -s "$service" > /dev/null 2>&1; then
        echo "✅ $service - OK"
    else
        echo "❌ $service - FAILED"
    fi
done
echo ""

# Check resource usage
echo "💾 Resource Usage:"
echo "Memory: $(free -h | grep '^Mem:' | awk '{print $3 "/" $2}')"
echo "Disk: $(df -h / | tail -1 | awk '{print $3 "/" $2 " (" $5 " used)"}')"
echo ""

# Check network connectivity
echo "🌍 Network Connectivity:"
if ping -c 1 google.com > /dev/null 2>&1; then
    echo "✅ Internet connection - OK"
else
    echo "❌ Internet connection - FAILED"
fi
```

### 2. Installation and Setup Issues

#### WSL2 Installation Problems

**Issue: "WSL2 kernel not found"**
```bash
# Solution: Download and install WSL2 kernel update
curl -L -o wsl_update_x64.msi https://wslstorestorage.blob.core.windows.net/wslblob/wsl_update_x64.msi
# Run the downloaded installer as administrator
```

**Issue: "Virtualization not enabled"**
```powershell
# Check virtualization support
systeminfo | findstr /i "hyper-v"

# Enable in BIOS/UEFI:
# 1. Restart computer
# 2. Enter BIOS/UEFI setup (usually F2, F12, or Delete)
# 3. Find "Virtualization Technology" or "Intel VT-x/AMD-V"
# 4. Enable the setting
# 5. Save and exit
```

**Issue: "Ubuntu installation fails"**
```bash
# Reset WSL if installation is corrupted
wsl --shutdown
wsl --unregister Ubuntu
wsl --install -d Ubuntu

# Alternative: Manual installation
curl -L -o ubuntu.appx https://aka.ms/wslubuntu2004
Add-AppxPackage ubuntu.appx
```

#### Docker Desktop Issues

**Issue: "Docker Desktop won't start"**
```powershell
# Check Windows features
dism.exe /online /get-featureinfo /featurename:Microsoft-Windows-Subsystem-Linux
dism.exe /online /get-featureinfo /featurename:VirtualMachinePlatform

# Restart Docker Desktop service
Stop-Service -Name "Docker Desktop Service"
Start-Service -Name "Docker Desktop Service"

# Reset Docker Desktop
# Docker Desktop > Troubleshoot > Reset to factory defaults
```

**Issue: "Cannot connect to Docker daemon"**
```bash
# Check Docker service status
sudo service docker status

# Start Docker service
sudo service docker start

# Add user to docker group
sudo usermod -aG docker $USER
newgrp docker

# Test Docker access
docker run hello-world
```

### 3. Container Deployment Issues

#### Image Pull Problems

**Issue: "Failed to pull image"**
```bash
# Check Docker Hub connectivity
docker pull hello-world

# Check specific image availability
docker search pymapgis

# Use alternative registry if needed
docker pull ghcr.io/pymapgis/logistics-core:latest

# Clear Docker cache if corrupted
docker system prune -a
```

**Issue: "No space left on device"**
```bash
# Check disk usage
df -h
docker system df

# Clean Docker resources
docker system prune -f
docker volume prune -f
docker image prune -a -f

# Move Docker data directory if needed
# Edit ~/.wslconfig:
[wsl2]
memory=8GB
processors=4
```

#### Container Startup Failures

**Issue: "Container exits immediately"**
```bash
# Check container logs
docker logs logistics-core
docker logs logistics-dashboard

# Run container interactively for debugging
docker run -it --rm pymapgis/logistics-core:latest /bin/bash

# Check container health
docker inspect logistics-core | grep -A 10 "Health"
```

**Issue: "Port already in use"**
```bash
# Find process using port
netstat -tulpn | grep :8888
lsof -i :8888

# Kill process using port
sudo kill -9 $(lsof -t -i:8888)

# Use different ports
docker run -p 8889:8888 pymapgis/logistics-core:latest
```

### 4. Application Access Issues

#### Web Interface Problems

**Issue: "Cannot access dashboard at localhost:8501"**
```bash
# Check if service is running
docker ps | grep logistics-dashboard

# Check port forwarding
curl -I http://localhost:8501

# Test from WSL2
curl -I http://$(hostname -I | awk '{print $1}'):8501

# Configure Windows firewall
# Windows Security > Firewall & network protection
# Allow Docker Desktop and WSL2
```

**Issue: "Dashboard loads but shows errors"**
```bash
# Check dashboard logs
docker logs logistics-dashboard

# Restart dashboard service
docker restart logistics-dashboard

# Check API connectivity from dashboard
docker exec logistics-dashboard curl http://logistics-core:8000/health
```

**Issue: "Jupyter notebook token required"**
```bash
# Get Jupyter token
docker logs logistics-core | grep "token="

# Or disable token requirement
docker run -e JUPYTER_TOKEN="" pymapgis/logistics-core:latest

# Access with token
# http://localhost:8888/?token=YOUR_TOKEN_HERE
```

#### Authentication and Security Issues

**Issue: "Access denied or authentication failed"**
```bash
# Check environment variables
docker exec logistics-core env | grep -E "(USER|PASSWORD|TOKEN)"

# Reset authentication
docker exec logistics-core python -c "
from pymapgis.auth import reset_credentials
reset_credentials()
"

# Use default credentials
# Username: admin
# Password: admin (change after first login)
```

### 5. Data and Performance Issues

#### Data Loading Problems

**Issue: "Sample data not loading"**
```bash
# Check database connectivity
docker exec logistics-postgres pg_isready -U logistics_user

# Manually load sample data
docker exec logistics-core python -c "
import pymapgis as pmg
pmg.logistics.load_sample_data(force=True)
"

# Check data tables
docker exec logistics-postgres psql -U logistics_user -d logistics -c "\dt logistics.*"
```

**Issue: "Custom data upload fails"**
```bash
# Check file format and encoding
file your_data.csv
head -5 your_data.csv

# Validate CSV structure
python3 -c "
import pandas as pd
df = pd.read_csv('your_data.csv')
print(df.info())
print(df.head())
"

# Check file permissions
ls -la your_data.csv
chmod 644 your_data.csv
```

#### Performance Problems

**Issue: "Analysis is very slow"**
```bash
# Check resource allocation
docker stats

# Increase container resources
docker run --memory=4g --cpus=2 pymapgis/logistics-core:latest

# Optimize WSL2 resources
# Edit ~/.wslconfig:
[wsl2]
memory=12GB
processors=6
swap=4GB
```

**Issue: "Out of memory errors"**
```bash
# Check memory usage
free -h
docker stats --no-stream

# Reduce dataset size for testing
python3 -c "
import pandas as pd
df = pd.read_csv('large_dataset.csv')
sample = df.sample(n=1000)
sample.to_csv('sample_dataset.csv', index=False)
"

# Use data chunking for large datasets
python3 -c "
import pandas as pd
for chunk in pd.read_csv('large_dataset.csv', chunksize=1000):
    # Process chunk
    pass
"
```

### 6. Network and Connectivity Issues

#### API Connection Problems

**Issue: "API requests timeout"**
```bash
# Check API service status
curl -v http://localhost:8000/health

# Check network latency
ping localhost
traceroute localhost

# Increase timeout settings
export REQUESTS_TIMEOUT=300
export API_TIMEOUT=300
```

**Issue: "External API calls fail"**
```bash
# Check internet connectivity
ping google.com
curl -I https://api.openstreetmap.org

# Check proxy settings
echo $http_proxy
echo $https_proxy

# Configure proxy if needed
export http_proxy=http://proxy.company.com:8080
export https_proxy=http://proxy.company.com:8080
```

#### Database Connection Issues

**Issue: "Database connection refused"**
```bash
# Check PostgreSQL service
docker exec logistics-postgres pg_isready

# Check connection string
docker exec logistics-core python -c "
import os
print('DATABASE_URL:', os.getenv('DATABASE_URL'))
"

# Test direct connection
docker exec logistics-postgres psql -U logistics_user -d logistics -c "SELECT version();"
```

### 7. Optimization and Algorithm Issues

#### Route Optimization Problems

**Issue: "Route optimization fails or produces poor results"**
```python
# Debug optimization parameters
import pymapgis as pmg

# Check input data quality
customers = pmg.read_csv('customers.csv')
print("Data quality check:")
print(f"Missing coordinates: {customers[['latitude', 'longitude']].isnull().sum()}")
print(f"Invalid coordinates: {((customers.latitude < -90) | (customers.latitude > 90)).sum()}")

# Use simpler optimization for debugging
optimizer = pmg.RouteOptimizer(
    algorithm='nearest_neighbor',  # Simpler algorithm
    max_iterations=100,            # Fewer iterations
    time_limit=60                  # 1 minute limit
)
```

**Issue: "Optimization takes too long"**
```python
# Reduce problem size
customers_sample = customers.sample(n=50)  # Smaller dataset

# Use heuristic algorithms
optimizer = pmg.RouteOptimizer(
    algorithm='genetic_algorithm',
    population_size=50,
    max_generations=100
)

# Set time limits
optimizer.set_time_limit(300)  # 5 minutes maximum
```

#### Facility Location Issues

**Issue: "Facility location analysis produces unrealistic results"**
```python
# Validate input parameters
location_analyzer = pmg.FacilityLocationAnalyzer()

# Check demand data
print("Demand statistics:")
print(customers['demand'].describe())

# Validate cost parameters
print("Cost parameters:")
print(f"Land cost: {location_analyzer.land_cost_per_sqm}")
print(f"Construction cost: {location_analyzer.construction_cost_per_sqm}")
print(f"Transportation cost: {location_analyzer.transport_cost_per_km}")
```

### 8. Integration and API Issues

#### External System Integration

**Issue: "ERP system integration fails"**
```python
# Test API connectivity
import requests

try:
    response = requests.get('http://your-erp-system/api/health', timeout=30)
    print(f"ERP API Status: {response.status_code}")
except Exception as e:
    print(f"ERP API Error: {e}")

# Check authentication
headers = {'Authorization': 'Bearer YOUR_TOKEN'}
response = requests.get('http://your-erp-system/api/test', headers=headers)
```

**Issue: "GPS/IoT data integration problems"**
```python
# Test GPS data feed
import json
import websocket

def on_message(ws, message):
    data = json.loads(message)
    print(f"GPS Update: {data}")

def on_error(ws, error):
    print(f"GPS Error: {error}")

# Test WebSocket connection
ws = websocket.WebSocketApp("ws://your-gps-provider/feed",
                          on_message=on_message,
                          on_error=on_error)
```

### 9. Advanced Troubleshooting

#### Container Debugging

**Issue: "Need to debug inside container"**
```bash
# Access container shell
docker exec -it logistics-core /bin/bash

# Check container environment
env | sort

# Check installed packages
pip list
apt list --installed

# Check file system
ls -la /app
df -h
```

**Issue: "Container networking problems"**
```bash
# Check Docker networks
docker network ls
docker network inspect logistics_default

# Test inter-container connectivity
docker exec logistics-core ping logistics-postgres
docker exec logistics-core nslookup logistics-postgres

# Check port bindings
docker port logistics-core
```

#### Log Analysis

**Issue: "Need detailed logging for diagnosis"**
```bash
# Enable debug logging
docker run -e LOG_LEVEL=DEBUG pymapgis/logistics-core:latest

# Collect all logs
docker-compose logs > logistics-debug.log

# Monitor logs in real-time
docker-compose logs -f

# Filter specific service logs
docker logs logistics-core 2>&1 | grep ERROR
```

### 10. Recovery Procedures

#### Complete System Reset

**Issue: "Everything is broken, need fresh start"**
```bash
# Stop all containers
docker-compose down

# Remove all containers and volumes
docker system prune -a --volumes

# Remove WSL2 distribution (nuclear option)
wsl --shutdown
wsl --unregister Ubuntu

# Reinstall from scratch
wsl --install -d Ubuntu
```

#### Data Recovery

**Issue: "Lost data or corrupted database"**
```bash
# Check for backups
ls -la /backup/logistics/

# Restore from backup
docker exec logistics-postgres psql -U logistics_user -d logistics < backup.sql

# Recreate sample data
docker exec logistics-core python -c "
import pymapgis as pmg
pmg.logistics.initialize_sample_data(force=True)
"
```

### 11. Prevention and Monitoring

#### Proactive Monitoring

```bash
# Set up health monitoring
cat > monitor-logistics.sh << 'EOF'
#!/bin/bash
while true; do
    if ! curl -f http://localhost:8000/health > /dev/null 2>&1; then
        echo "$(date): API health check failed" >> logistics-monitor.log
        docker restart logistics-core
    fi
    sleep 60
done
EOF

chmod +x monitor-logistics.sh
nohup ./monitor-logistics.sh &
```

#### Regular Maintenance

```bash
# Weekly maintenance script
cat > weekly-maintenance.sh << 'EOF'
#!/bin/bash
echo "$(date): Starting weekly maintenance"

# Update containers
docker-compose pull
docker-compose up -d

# Clean up resources
docker system prune -f

# Backup data
./backup-logistics.sh

echo "$(date): Weekly maintenance complete"
EOF
```

### 12. Getting Additional Help

#### Information to Collect Before Seeking Help

```bash
# System information
uname -a > debug-info.txt
lsb_release -a >> debug-info.txt
docker --version >> debug-info.txt
docker-compose --version >> debug-info.txt

# Container status
docker ps -a >> debug-info.txt
docker-compose ps >> debug-info.txt

# Recent logs
docker-compose logs --tail=100 >> debug-info.txt

# Resource usage
free -h >> debug-info.txt
df -h >> debug-info.txt
```

#### Support Channels
- **GitHub Issues**: https://github.com/pymapgis/logistics/issues
- **Community Forum**: https://community.pymapgis.com
- **Email Support**: support@pymapgis.com
- **Live Chat**: Available on website during business hours
- **Emergency Support**: For critical production issues

---

*This comprehensive troubleshooting guide provides systematic solutions for common PyMapGIS logistics deployment and usage issues with focus on quick resolution and prevention.*
