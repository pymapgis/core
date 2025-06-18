# 🔧 PyMapGIS Troubleshooting Guide

![Troubleshooting](https://img.shields.io/badge/PyMapGIS-Troubleshooting-orange) ![Status](https://img.shields.io/badge/Status-Complete-success) ![Help](https://img.shields.io/badge/Type-Support-blue)

## 🎯 Overview

This guide helps you diagnose and resolve common issues when running PyMapGIS showcases. Most issues are related to network connectivity, API access, or environment setup.

## 🚨 **Common Issues and Solutions**

### **1. "Loading data..." Never Completes**

#### **Symptoms:**
- Web interface shows "Loading [City] data..." indefinitely
- No data appears on the map
- Console shows network errors

#### **Diagnosis:**
```bash
# Check if the service is running
curl http://localhost:8000/health

# Check API connectivity
curl http://localhost:8000/public/latest
```

#### **Solutions:**

**A. API Connectivity Issues:**
```bash
# Test external API connectivity
curl -I https://api.tfl.gov.uk/line/mode/tube/status
curl -I https://api.mta.info/

# If external APIs fail, the showcase will use mock data
# This is normal and expected behavior
```

**B. Service Not Started:**
```bash
# Make sure the service is running
docker ps  # Should show your container running
# or
python app.py  # If running locally
```

**C. Port Conflicts:**
```bash
# Check if port 8000 is in use
netstat -an | grep 8000
# or
lsof -i :8000

# Use different port if needed
docker run -p 8001:8000 showcase-name:latest
```

### **2. Docker Container Won't Start**

#### **Symptoms:**
- `docker run` command fails
- Container exits immediately
- "Port already in use" errors

#### **Diagnosis:**
```bash
# Check Docker status
docker --version
docker info

# Check container logs
docker logs container_name

# Check available ports
docker run -p 8001:8000 showcase-name:latest
```

#### **Solutions:**

**A. Port Already in Use:**
```bash
# Find what's using the port
sudo lsof -i :8000

# Kill the process or use different port
docker run -p 8001:8000 showcase-name:latest
```

**B. Docker Not Running:**
```bash
# Start Docker service (Linux)
sudo systemctl start docker

# Start Docker Desktop (Windows/Mac)
# Open Docker Desktop application
```

**C. Image Not Found:**
```bash
# Pull the image explicitly
docker pull nicholaskarlson/london-tube-now:latest

# Or build locally
docker build -t london-tube-now .
```

### **3. "Mock Data" Messages in Console**

#### **Symptoms:**
- Console shows "Using mock data" messages
- Data appears but may not be real-time
- APIs return errors or timeouts

#### **This is Normal Behavior!**
PyMapGIS showcases are designed to fall back to high-quality mock data when:
- Real-time APIs are unavailable
- API keys are not configured
- Network connectivity issues occur
- Rate limits are exceeded

#### **To Enable Real-Time Data:**
```bash
# Set up API keys (optional)
export TFL_API_KEY="your_api_key"
export MTA_API_KEY="your_api_key"

# Restart the showcase
docker run -e TFL_API_KEY=$TFL_API_KEY -p 8000:8000 london-tube-now:latest
```

### **4. Poetry/Python Environment Issues**

#### **Symptoms:**
- `poetry install` fails
- Import errors when running Python
- Version conflicts

#### **Solutions:**

**A. Poetry Not Installed:**
```bash
# Install Poetry
curl -sSL https://install.python-poetry.org | python3 -

# Add to PATH
export PATH="$HOME/.local/bin:$PATH"
```

**B. Python Version Issues:**
```bash
# Check Python version (requires 3.9+)
python --version

# Use pyenv to manage Python versions
pyenv install 3.11
pyenv local 3.11
```

**C. Dependency Conflicts:**
```bash
# Clear Poetry cache
poetry cache clear pypi --all

# Reinstall dependencies
poetry install --no-cache
```

### **5. Map Not Loading or Blank**

#### **Symptoms:**
- Web page loads but map area is blank
- JavaScript console errors
- MapLibre GL JS errors

#### **Solutions:**

**A. JavaScript Errors:**
```javascript
// Open browser developer tools (F12)
// Check Console tab for errors
// Common issues:
// - Network connectivity to map tiles
// - CORS issues
// - JavaScript syntax errors
```

**B. Network Issues:**
```bash
# Test map tile connectivity
curl -I https://a.tile.openstreetmap.org/0/0/0.png

# If tiles don't load, check firewall/proxy settings
```

**C. Browser Compatibility:**
- Use modern browser (Chrome 79+, Firefox 70+, Safari 13+)
- Enable JavaScript
- Disable ad blockers that might block map tiles

### **6. API Rate Limiting**

#### **Symptoms:**
- Data loads initially but stops updating
- HTTP 429 "Too Many Requests" errors
- Intermittent data availability

#### **Solutions:**

**A. Reduce Update Frequency:**
```javascript
// In the showcase code, increase refresh interval
// From: setInterval(loadData, 60000)  // 1 minute
// To:   setInterval(loadData, 300000) // 5 minutes
```

**B. Use API Keys:**
```bash
# API keys often provide higher rate limits
export TFL_API_KEY="your_api_key"
export MTA_API_KEY="your_api_key"
```

**C. Implement Caching:**
```python
# Showcases include built-in caching
# Data is cached for 2-5 minutes to reduce API calls
```

### **7. Windows/WSL2 Issues**

#### **Symptoms:**
- Docker commands fail on Windows
- Network connectivity issues in WSL2
- File permission problems

#### **Solutions:**

**A. WSL2 Setup:**
```bash
# Install WSL2 and Ubuntu
wsl --install

# Update WSL2
wsl --update

# Set WSL2 as default
wsl --set-default-version 2
```

**B. Docker Desktop Integration:**
```bash
# Enable WSL2 integration in Docker Desktop
# Settings > Resources > WSL Integration
# Enable integration with Ubuntu
```

**C. Network Issues:**
```bash
# Reset WSL2 network
wsl --shutdown
# Restart WSL2 and Docker Desktop
```

## 🔍 **Diagnostic Commands**

### **System Health Check**
```bash
#!/bin/bash
echo "=== PyMapGIS System Health Check ==="

# Check Docker
echo "Docker version:"
docker --version

# Check Python
echo "Python version:"
python --version

# Check Poetry
echo "Poetry version:"
poetry --version

# Check network connectivity
echo "Network connectivity:"
curl -I https://api.tfl.gov.uk/line/mode/tube/status
curl -I https://data.sfgov.org/resource/rqzj-sfat.json

# Check ports
echo "Port availability:"
netstat -an | grep :8000
```

### **Showcase-Specific Diagnostics**
```python
#!/usr/bin/env python3
"""PyMapGIS Diagnostic Script"""

import requests
import json
from datetime import datetime

def test_showcase_health(port=8000):
    """Test showcase health and connectivity"""
    base_url = f"http://localhost:{port}"
    
    tests = {
        'Health Check': f"{base_url}/health",
        'Public Data': f"{base_url}/public/latest",
        'Transit Status': f"{base_url}/transit/status",
        'API Docs': f"{base_url}/docs"
    }
    
    results = {}
    for test_name, url in tests.items():
        try:
            response = requests.get(url, timeout=10)
            results[test_name] = {
                'status': response.status_code,
                'response_time': response.elapsed.total_seconds(),
                'success': response.status_code == 200
            }
        except Exception as e:
            results[test_name] = {
                'status': 'error',
                'error': str(e),
                'success': False
            }
    
    # Print results
    print(f"=== Showcase Diagnostic Results ===")
    print(f"Timestamp: {datetime.now()}")
    print(f"Port: {port}")
    print()
    
    for test_name, result in results.items():
        status = "✅ PASS" if result['success'] else "❌ FAIL"
        print(f"{test_name}: {status}")
        if 'response_time' in result:
            print(f"  Response time: {result['response_time']:.2f}s")
        if 'error' in result:
            print(f"  Error: {result['error']}")
        print()

if __name__ == "__main__":
    test_showcase_health()
```

## 🆘 **Getting Help**

### **1. Check Logs**
```bash
# Docker container logs
docker logs container_name

# Python application logs
python app.py  # Look for error messages

# System logs (Linux)
journalctl -u docker
```

### **2. Enable Debug Mode**
```bash
# Set debug environment variables
export DEBUG=true
export LOG_LEVEL=DEBUG

# Run with verbose output
python -v app.py
```

### **3. Community Support**
- **GitHub Issues**: Report bugs and request features
- **Documentation**: Check individual showcase README files
- **API Documentation**: Visit `/docs` endpoint for each showcase

### **4. Common Environment Variables**
```bash
# Debug and logging
export DEBUG=true
export LOG_LEVEL=DEBUG

# API configuration
export API_TIMEOUT=30
export RETRY_ATTEMPTS=3
export FALLBACK_TO_MOCK=true

# API keys (optional)
export TFL_API_KEY="your_key"
export MTA_API_KEY="your_key"
```

## ✅ **Quick Fixes Checklist**

When a showcase isn't working:

1. **✅ Check if Docker is running**
   ```bash
   docker --version && docker info
   ```

2. **✅ Verify port availability**
   ```bash
   curl http://localhost:8000/health
   ```

3. **✅ Test with different port**
   ```bash
   docker run -p 8001:8000 showcase-name:latest
   ```

4. **✅ Check network connectivity**
   ```bash
   curl -I https://api.tfl.gov.uk/line/mode/tube/status
   ```

5. **✅ Review container logs**
   ```bash
   docker logs container_name
   ```

6. **✅ Try fresh container**
   ```bash
   docker pull nicholaskarlson/showcase-name:latest
   docker run -p 8000:8000 nicholaskarlson/showcase-name:latest
   ```

## 📝 **Remember**

**PyMapGIS showcases are designed to be resilient:**
- ✅ **Mock data fallback** ensures showcases always work
- ✅ **No API keys required** for basic functionality
- ✅ **Graceful error handling** prevents crashes
- ✅ **Health monitoring** helps diagnose issues
- ✅ **Comprehensive logging** aids troubleshooting

**Most "issues" are actually normal behavior** - showcases falling back to mock data when real-time APIs are unavailable. This is by design to ensure reliability and demonstrate functionality even without external dependencies.
