# 🌐 Real-Time Data Integration Guide

![Data Status](https://img.shields.io/badge/PyMapGIS-Documentation-blue) ![Guide](https://img.shields.io/badge/Type-Developer%20Guide-green) ![Status](https://img.shields.io/badge/Status-Complete-success)

## 🎯 Overview

This guide helps developers understand and overcome real-time data connectivity challenges in PyMapGIS showcases. Many showcases fall back to high-quality mock data when real-time APIs are unavailable, rate-limited, or require authentication.

## 🚨 Common Real-Time Data Challenges

### 1. **API Authentication Requirements**
Many transit agencies require API keys or authentication:
- **London TfL**: Requires free API key registration
- **NYC MTA**: Requires API key for GTFS-RT feeds
- **Berlin VBB**: Some endpoints require authentication
- **Paris RATP**: Limited public access to real-time feeds

### 2. **Rate Limiting and Quotas**
Public APIs often have strict limits:
- **Requests per minute**: 60-300 typical limits
- **Daily quotas**: 1,000-10,000 requests per day
- **Concurrent connections**: Usually 1-5 simultaneous

### 3. **Network Connectivity Issues**
- **Firewall restrictions**: Corporate/institutional firewalls
- **Geographic blocking**: Some APIs block international requests
- **Temporary outages**: API maintenance or service disruptions
- **SSL/TLS issues**: Certificate validation problems

### 4. **Data Format Variations**
- **GTFS-RT complexity**: Protocol buffer parsing challenges
- **JSON schema differences**: Inconsistent field naming
- **Timezone handling**: UTC vs local time complications
- **Data quality**: Missing or malformed responses

## 🛠️ PyMapGIS Fallback Strategy

### **Intelligent Mock Data System**
All PyMapGIS showcases implement a robust fallback system:

```python
def fetch_real_time_data():
    """Attempt real-time data fetch with intelligent fallback"""
    try:
        # Try real-time API first
        response = requests.get(API_URL, timeout=15)
        response.raise_for_status()
        return process_real_data(response.json())
    except (requests.RequestException, ValueError, KeyError) as e:
        print(f"⚠️ Real-time API unavailable: {e}")
        print("🎭 Using high-quality mock data...")
        return create_realistic_mock_data()
```

### **High-Quality Mock Data Features**
- **Realistic patterns**: Based on actual transit operations
- **Time-aware**: Reflects rush hour vs off-peak patterns
- **Geographic accuracy**: Proper route coordinates and stops
- **Performance metrics**: Realistic delays, frequencies, and scores
- **Status variety**: Mix of excellent, good, and problematic services

## 🔧 Developer Solutions

### **1. API Key Setup (When Available)**

#### London TfL API
```bash
# Register at: https://api.tfl.gov.uk/
export TFL_API_KEY="your_api_key_here"
```

#### NYC MTA API
```bash
# Register at: https://api.mta.info/
export MTA_API_KEY="your_api_key_here"
```

#### Configuration in Code
```python
import os

# Use environment variables for API keys
TFL_API_KEY = os.getenv('TFL_API_KEY')
MTA_API_KEY = os.getenv('MTA_API_KEY')

# Graceful fallback when keys unavailable
if not TFL_API_KEY:
    print("ℹ️ TFL_API_KEY not found, using mock data")
    use_mock_data = True
```

### **2. Network Troubleshooting**

#### Test API Connectivity
```bash
# Test basic connectivity
curl -I https://api.tfl.gov.uk/line/mode/tube/status

# Test with timeout
curl --max-time 10 https://api.tfl.gov.uk/line/mode/tube/status

# Test through proxy (if needed)
curl --proxy http://proxy:8080 https://api.tfl.gov.uk/line/mode/tube/status
```

#### Python Network Debugging
```python
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

def create_robust_session():
    """Create HTTP session with retry logic"""
    session = requests.Session()
    
    # Retry strategy
    retry_strategy = Retry(
        total=3,
        backoff_factor=1,
        status_forcelist=[429, 500, 502, 503, 504],
    )
    
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    
    return session

# Usage
session = create_robust_session()
try:
    response = session.get(API_URL, timeout=15)
    response.raise_for_status()
except requests.RequestException as e:
    print(f"Network error: {e}")
    # Fall back to mock data
```

### **3. GTFS-RT Processing**

#### Install Required Dependencies
```bash
# For GTFS-RT protocol buffer support
pip install gtfs-realtime-bindings protobuf
```

#### GTFS-RT Parsing Example
```python
from google.transit import gtfs_realtime_pb2
import requests

def fetch_gtfs_rt_data(feed_url):
    """Fetch and parse GTFS-RT feed"""
    try:
        response = requests.get(feed_url, timeout=15)
        response.raise_for_status()
        
        # Parse protocol buffer
        feed = gtfs_realtime_pb2.FeedMessage()
        feed.ParseFromString(response.content)
        
        # Process entities
        vehicles = []
        for entity in feed.entity:
            if entity.HasField('vehicle'):
                vehicles.append({
                    'id': entity.vehicle.vehicle.id,
                    'route': entity.vehicle.trip.route_id,
                    'lat': entity.vehicle.position.latitude,
                    'lon': entity.vehicle.position.longitude,
                    'timestamp': entity.vehicle.timestamp
                })
        
        return vehicles
        
    except Exception as e:
        print(f"GTFS-RT parsing error: {e}")
        return create_mock_vehicle_data()
```

## 🎭 Mock Data Best Practices

### **1. Realistic Data Generation**
```python
import random
from datetime import datetime, timedelta

def create_realistic_transit_data():
    """Generate realistic transit performance data"""
    current_hour = datetime.now().hour
    
    # Rush hour patterns (7-9 AM, 5-7 PM)
    is_rush_hour = (7 <= current_hour <= 9) or (17 <= current_hour <= 19)
    
    # Adjust performance based on time
    base_delay = 2 if is_rush_hour else 1
    base_frequency = 3 if is_rush_hour else 5
    
    routes = []
    for route_id in ['line_1', 'line_2', 'line_3']:
        delay = max(0, random.gauss(base_delay, 1))
        frequency = max(2, random.gauss(base_frequency, 1))
        punctuality = max(75, min(99, random.gauss(90, 5)))
        
        routes.append({
            'route_id': route_id,
            'delay_minutes': round(delay, 1),
            'frequency_minutes': round(frequency, 1),
            'punctuality_percent': round(punctuality, 1),
            'last_updated': datetime.now().isoformat()
        })
    
    return routes
```

### **2. Geographic Accuracy**
```python
def create_realistic_route_coordinates(city_center_lat, city_center_lon):
    """Generate realistic route coordinates around city center"""
    routes = {}
    
    # Create routes radiating from city center
    for i, route_id in enumerate(['line_1', 'line_2', 'line_3']):
        angle = (i * 60) * (3.14159 / 180)  # 60 degrees apart
        
        coordinates = []
        for j in range(5):  # 5 stops per route
            # Distance from center (0.01 degrees ≈ 1km)
            distance = 0.005 + (j * 0.01)
            
            lat = city_center_lat + (distance * math.cos(angle))
            lon = city_center_lon + (distance * math.sin(angle))
            
            coordinates.append([lon, lat])  # GeoJSON format: [lon, lat]
        
        routes[route_id] = coordinates
    
    return routes
```

## 🔍 Debugging Real-Time Data Issues

### **1. Enable Verbose Logging**
```python
import logging

# Enable debug logging for requests
logging.basicConfig(level=logging.DEBUG)
logging.getLogger("requests.packages.urllib3").setLevel(logging.DEBUG)
logging.getLogger("urllib3.connectionpool").setLevel(logging.DEBUG)
```

### **2. API Response Validation**
```python
def validate_api_response(response_data, required_fields):
    """Validate API response has required fields"""
    if not isinstance(response_data, dict):
        raise ValueError("Response is not a dictionary")
    
    missing_fields = []
    for field in required_fields:
        if field not in response_data:
            missing_fields.append(field)
    
    if missing_fields:
        raise ValueError(f"Missing required fields: {missing_fields}")
    
    return True

# Usage
try:
    data = response.json()
    validate_api_response(data, ['routes', 'last_updated'])
    return process_real_data(data)
except ValueError as e:
    print(f"Invalid API response: {e}")
    return create_mock_data()
```

### **3. Connection Testing Utility**
```python
def test_api_connectivity(api_urls):
    """Test connectivity to multiple API endpoints"""
    results = {}
    
    for name, url in api_urls.items():
        try:
            start_time = time.time()
            response = requests.get(url, timeout=10)
            response_time = time.time() - start_time
            
            results[name] = {
                'status': 'success',
                'status_code': response.status_code,
                'response_time': round(response_time, 2),
                'content_length': len(response.content)
            }
        except requests.RequestException as e:
            results[name] = {
                'status': 'error',
                'error': str(e)
            }
    
    return results

# Test all showcase APIs
api_endpoints = {
    'London TfL': 'https://api.tfl.gov.uk/line/mode/tube/status',
    'NYC MTA': 'https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs',
    'Berlin VBB': 'https://v6.vbb.transport.rest/stops/900000100000/departures',
    'Paris RATP': 'https://api-ratp.pierre-grimaud.fr/v4/traffic',
    'Copenhagen': 'https://xmlopen.rejseplanen.dk/bin/rest.exe/departureBoard'
}

connectivity_results = test_api_connectivity(api_endpoints)
for api, result in connectivity_results.items():
    print(f"{api}: {result['status']}")
```

## 🚀 Production Deployment Tips

### **1. Environment Configuration**
```bash
# .env file for production
TFL_API_KEY=your_production_key
MTA_API_KEY=your_production_key
API_TIMEOUT=30
RETRY_ATTEMPTS=3
FALLBACK_TO_MOCK=true
LOG_LEVEL=INFO
```

### **2. Health Monitoring**
```python
def api_health_check():
    """Monitor API health for production deployment"""
    health_status = {
        'timestamp': datetime.now().isoformat(),
        'apis': {},
        'overall_status': 'healthy'
    }
    
    for api_name, api_url in API_ENDPOINTS.items():
        try:
            response = requests.get(api_url, timeout=10)
            health_status['apis'][api_name] = {
                'status': 'up',
                'response_time': response.elapsed.total_seconds(),
                'status_code': response.status_code
            }
        except Exception as e:
            health_status['apis'][api_name] = {
                'status': 'down',
                'error': str(e)
            }
            health_status['overall_status'] = 'degraded'
    
    return health_status
```

## 📝 Summary

PyMapGIS showcases are designed to work reliably whether real-time APIs are available or not. The intelligent fallback system ensures users always see realistic, high-quality data that demonstrates the full capabilities of each showcase.

**Key Takeaways:**
- ✅ **Always implement fallback**: Never rely solely on external APIs
- ✅ **Use realistic mock data**: Base on actual transit patterns
- ✅ **Handle errors gracefully**: Provide clear feedback to users
- ✅ **Test connectivity**: Validate API access during development
- ✅ **Monitor in production**: Track API health and performance

For specific API setup instructions, see the individual showcase documentation in each showcase's README.md file.
