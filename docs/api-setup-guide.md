# 🔑 API Setup Guide for PyMapGIS Showcases

![API Guide](https://img.shields.io/badge/PyMapGIS-API%20Setup-blue) ![Status](https://img.shields.io/badge/Status-Complete-success) ![Difficulty](https://img.shields.io/badge/Difficulty-Beginner-green)

## 🎯 Overview

This guide provides step-by-step instructions for setting up real-time API access for PyMapGIS showcases. While all showcases work with high-quality mock data by default, connecting to real APIs provides live, up-to-the-minute data.

## 🌍 **National Showcases (No API Keys Required)**

### ✅ **Ready to Use Out of the Box**
These showcases use public APIs or data sources that don't require authentication:

- **🌍 Quake Impact Now**: USGS Earthquake API (public)
- **🛂 Border Flow Now**: CBP Border Wait Times (public)
- **✈️ Flight Delay Now**: FAA System Operations Center (public)
- **🚢 Ship Traffic Now**: AIS data feeds (public)
- **🌦️ Weather Impact Now**: National Weather Service (public)
- **⚡ Energy Grid Now**: EIA electricity data (public)
- **🚛 Supply Chain Flow Now**: Public logistics data

**No setup required** - these showcases connect to real-time data automatically when APIs are available.

## 🏙️ **Local Showcases**

### 🚚 **Open Food Trucks Now (San Francisco)**
**Data Source**: San Francisco Open Data Portal
**Setup**: No API key required
```bash
# Test connectivity
curl "https://data.sfgov.org/resource/rqzj-sfat.json"
```

### 🕳️ **Open311 Pothole Now (San Francisco)**
**Data Source**: SF Open311 API
**Setup**: No API key required
```bash
# Test connectivity
curl "https://mobile311.sfgov.org/open311/v2/requests.json?service_code=001"
```

### 🚇 **Transit Crowding Now (NYC)**
**Data Source**: MTA GTFS-RT Feeds
**Setup**: API key recommended for production use

#### Optional MTA API Key Setup:
1. **Register**: Visit https://api.mta.info/
2. **Create Account**: Sign up for free developer account
3. **Get API Key**: Generate API key in dashboard
4. **Set Environment Variable**:
```bash
export MTA_API_KEY="your_api_key_here"
```

## 🌍 **Global Transit Showcases**

### 🇬🇧 **London Tube Status Now**
**Data Source**: Transport for London (TfL) API
**Setup**: Free API key required for production use

#### TfL API Key Setup:
1. **Register**: Visit https://api.tfl.gov.uk/
2. **Create Account**: Sign up for free developer account
3. **Generate Key**: Create API key in your account dashboard
4. **Set Environment Variable**:
```bash
export TFL_API_KEY="your_api_key_here"
```
5. **Test Connection**:
```bash
curl "https://api.tfl.gov.uk/line/mode/tube/status?app_key=your_api_key_here"
```

#### Usage in Code:
```python
import os
TFL_API_KEY = os.getenv('TFL_API_KEY')
if TFL_API_KEY:
    api_url = f"https://api.tfl.gov.uk/line/mode/tube/status?app_key={TFL_API_KEY}"
else:
    print("Using mock data - set TFL_API_KEY for real-time data")
```

### 🇨🇦 **Toronto Transit Now**
**Data Source**: TTC GTFS and real-time feeds
**Setup**: No API key required (public feeds)
```bash
# Test GTFS-RT feed
curl "https://gtfs.ttc.ca/gtfs-realtime/TripUpdates.pb"
```

### 🇩🇰 **Copenhagen Transit Now**
**Data Source**: Rejseplanen API
**Setup**: No API key required for basic usage
```bash
# Test connectivity
curl "https://xmlopen.rejseplanen.dk/bin/rest.exe/departureBoard?id=8600626&format=json"
```

### 🇩🇪 **Berlin U-Bahn Now**
**Data Source**: VBB (Verkehrsverbund Berlin-Brandenburg)
**Setup**: No API key required for basic endpoints
```bash
# Test connectivity
curl "https://v6.vbb.transport.rest/stops/900000100000/departures"
```

### 🇫🇷 **Paris Metro Now**
**Data Source**: RATP API
**Setup**: No API key required for basic traffic data
```bash
# Test connectivity
curl "https://api-ratp.pierre-grimaud.fr/v4/traffic"
```

## 🔧 **Environment Configuration**

### **1. Create .env File**
Create a `.env` file in your project root:
```bash
# Optional API Keys (showcases work without these)
TFL_API_KEY=your_london_api_key_here
MTA_API_KEY=your_nyc_api_key_here

# API Configuration
API_TIMEOUT=30
RETRY_ATTEMPTS=3
FALLBACK_TO_MOCK=true

# Logging
LOG_LEVEL=INFO
```

### **2. Load Environment Variables**
```python
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Access API keys
TFL_API_KEY = os.getenv('TFL_API_KEY')
MTA_API_KEY = os.getenv('MTA_API_KEY')
```

### **3. Docker Environment Setup**
```bash
# Run with environment variables
docker run -e TFL_API_KEY=your_key -p 8000:8000 showcase-name:latest

# Or use .env file
docker run --env-file .env -p 8000:8000 showcase-name:latest
```

## 🚨 **Troubleshooting Common Issues**

### **1. API Key Not Working**
```bash
# Verify API key format
echo $TFL_API_KEY

# Test with curl
curl "https://api.tfl.gov.uk/line/mode/tube/status?app_key=$TFL_API_KEY"
```

### **2. Network Connectivity Issues**
```python
# Test basic connectivity
import requests

def test_api_connection(url):
    try:
        response = requests.get(url, timeout=10)
        print(f"Status: {response.status_code}")
        print(f"Response time: {response.elapsed.total_seconds()}s")
        return True
    except requests.RequestException as e:
        print(f"Connection failed: {e}")
        return False

# Test TfL API
test_api_connection("https://api.tfl.gov.uk/line/mode/tube/status")
```

### **3. Rate Limiting**
Most APIs have rate limits. PyMapGIS showcases handle this gracefully:
- **TfL API**: 500 requests per minute
- **MTA API**: 300 requests per minute
- **Public APIs**: Usually 60-100 requests per minute

### **4. CORS Issues (Browser)**
If running in browser, some APIs may have CORS restrictions. Use the Docker containers or local Python execution instead.

## 📊 **API Status Monitoring**

### **Built-in Health Checks**
All showcases include health check endpoints:
```bash
# Check showcase health
curl http://localhost:8000/health

# Example response
{
  "status": "healthy",
  "service": "London Tube Status Now",
  "data_available": true,
  "api_connected": true,
  "last_updated": "2024-01-15T10:30:00Z"
}
```

### **Monitor API Connectivity**
```python
def monitor_api_health():
    """Monitor all API endpoints"""
    apis = {
        'TfL': 'https://api.tfl.gov.uk/line/mode/tube/status',
        'MTA': 'https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs',
        'VBB': 'https://v6.vbb.transport.rest/stops/900000100000/departures'
    }
    
    for name, url in apis.items():
        try:
            response = requests.get(url, timeout=5)
            status = "✅ UP" if response.status_code == 200 else f"⚠️ {response.status_code}"
        except:
            status = "❌ DOWN"
        
        print(f"{name}: {status}")
```

## 🎯 **Best Practices**

### **1. Always Use Fallback Data**
```python
def get_transit_data():
    """Get transit data with fallback"""
    try:
        # Try real API first
        return fetch_real_time_data()
    except Exception as e:
        print(f"API unavailable: {e}")
        # Fall back to high-quality mock data
        return create_mock_data()
```

### **2. Implement Caching**
```python
import time
from functools import lru_cache

@lru_cache(maxsize=1)
def cached_api_call(cache_key):
    """Cache API responses for 5 minutes"""
    return fetch_api_data()

def get_cached_data():
    # Create cache key with 5-minute intervals
    cache_key = int(time.time() // 300)
    return cached_api_call(cache_key)
```

### **3. Handle Errors Gracefully**
```python
def robust_api_call(url, retries=3):
    """Make API call with retries and error handling"""
    for attempt in range(retries):
        try:
            response = requests.get(url, timeout=15)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            if attempt == retries - 1:
                print(f"API failed after {retries} attempts: {e}")
                return None
            time.sleep(2 ** attempt)  # Exponential backoff
```

## 📝 **Summary**

**Key Points:**
- ✅ **All showcases work without API keys** using high-quality mock data
- ✅ **API keys are optional** but provide real-time data when available
- ✅ **Free registration** required for TfL and MTA APIs
- ✅ **Most APIs are public** and don't require authentication
- ✅ **Fallback system** ensures showcases always work
- ✅ **Health monitoring** built into all showcases

**Getting Started:**
1. **Try without API keys first** - all showcases work with mock data
2. **Register for TfL API key** if you want real London tube data
3. **Set environment variables** for any API keys you obtain
4. **Test connectivity** using the provided curl commands
5. **Monitor health endpoints** to verify API connections

For specific showcase setup, see the individual README.md files in each showcase directory.
