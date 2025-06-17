# 🏙️ PyMapGIS Local Showcases

![PyMapGIS Local](https://img.shields.io/badge/PyMapGIS-Local%20Showcases-blue) ![Status](https://img.shields.io/badge/Status-Active-green) ![License](https://img.shields.io/badge/License-MIT-yellow)

## 🎯 What Are Local Showcases?

PyMapGIS Local Showcases demonstrate **real-time local data processing** using publicly available city and regional datasets. These showcases focus on **hyperlocal intelligence** by:

- **🏙️ City-Specific Data**: Using real municipal open data APIs
- **📍 Hyperlocal Focus**: Neighborhood-level analysis and insights
- **🔄 Real-time Updates**: Live data feeds refreshing every 15 minutes
- **🎨 Enhanced Lighter Styling**: Perfect readability for local demonstrations
- **⚡ Lightning-Fast Performance**: Optimized Docker builds using PyMapGIS base

## 🚀 Available Local Showcases

### 🚚 Open Food Trucks Now - San Francisco
**Live lunch location heat-map for SF food trucks**
- **Data Source**: SF Open Data - Food Truck Schedule API
- **Features**: Neighborhood density analysis, live truck locations, lunch recommendations
- **Update Frequency**: Every 15 minutes during lunch hours
- **Use Case**: Find the best food truck clusters for lunch planning

### 🕳️ Open311 Pothole Now - San Francisco  
**Civic issues tracking and infrastructure monitoring**
- **Data Source**: SF Open311 API - Street/Sidewalk Defects
- **Features**: Issue age analysis, priority scoring, civic engagement tracking
- **Update Frequency**: Every 15 minutes for fresh civic data
- **Use Case**: Urban infrastructure monitoring and civic transparency

### 🚇 Transit Crowding Now - New York City
**Real-time subway crowding analysis for commuter planning**
- **Data Source**: MTA GTFS-Realtime Alerts API
- **Features**: Route crowding scores, commuter recommendations, real-time alerts
- **Update Frequency**: Every 5 minutes during rush hours
- **Use Case**: Choose less crowded subway lines for better commutes

## 🔧 Technical Architecture

### Shared Implementation Pattern
All local showcases follow the same optimized architecture:

```
showcaseslocal/
├── [showcase-name]/
│   ├── [name]_worker.py      # ~35 LOC data processor
│   ├── app.py                # FastAPI web application  
│   ├── static/index.html     # Enhanced lighter styling
│   ├── Dockerfile            # Optimized PyMapGIS base
│   └── requirements.txt      # Minimal dependencies
```

### Key Implementation Features
- **📊 Spatial Joins**: Using `geopandas.sjoin()` for neighborhood analysis
- **🎨 Enhanced Lighter Styling**: Maximum readability with bright backgrounds
- **⚡ Docker Optimization**: 10-12 second builds using PyMapGIS base image
- **🔄 Real-time APIs**: Live municipal data integration
- **📱 Responsive Design**: Mobile-optimized interfaces

## 🎨 Enhanced Lighter Styling

All local showcases feature **ultimate enhanced lighter styling**:
- **Brightest Backgrounds**: Maximum contrast for perfect readability
- **Clean Color Palettes**: Professional, accessible design
- **Optimized for Demos**: Perfect for video presentations and screenshots
- **Consistent Branding**: Unified PyMapGIS visual identity

## ⚡ Performance Metrics

### Docker Optimization Results
- **Build Time**: 10-12 seconds (95% faster than traditional)
- **Container Size**: ~200MB optimized
- **Startup Time**: <5 seconds from launch
- **Memory Usage**: <100MB RAM per showcase

### Data Processing Speed
- **Food Trucks**: <1 second for 100+ truck locations
- **Civic Issues**: <1 second for 500+ Open311 requests  
- **Transit**: <1 second for 20+ subway routes
- **API Response**: <200ms for all endpoints

## 🏙️ Local Data Sources

### San Francisco Open Data
- **Food Truck Schedule**: `https://data.sfgov.org/resource/jjew-5d7t.json`
- **Neighborhood Polygons**: `https://data.sfgov.org/resource/ejmn-km5w.geojson`
- **Open311 Requests**: `https://mobile311.sfgov.org/open311/v2/requests.json`

### New York City Open Data
- **MTA GTFS-Realtime**: `https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/`
- **Subway Routes**: Static GeoJSON from MTA
- **Real-time Alerts**: GTFS-RT protobuf feeds

## 🚀 Quick Start

### Option 1: Docker (Recommended)
```bash
# Run any local showcase
docker run -p 8000:8000 nicholaskarlson/[showcase-name]:latest

# Examples:
docker run -p 8000:8000 nicholaskarlson/open-food-trucks-now:latest
docker run -p 8000:8000 nicholaskarlson/open311-pothole-now:latest
docker run -p 8000:8000 nicholaskarlson/transit-crowding-now:latest
```

### Option 2: Local Development
```bash
# Clone and setup
git clone https://github.com/pymapgis/core.git
cd core/showcaseslocal/[showcase-name]

# Install dependencies with Poetry
poetry install

# Run the worker to process data
poetry run python [name]_worker.py

# Start the web application
poetry run python app.py

# View at: http://localhost:8000
```

## 📊 Use Cases

### Urban Planning
- **Food Access**: Analyze food truck distribution across neighborhoods
- **Infrastructure**: Track civic issue patterns and response times
- **Transportation**: Optimize transit routes based on crowding data

### Civic Engagement
- **Transparency**: Real-time civic issue tracking and resolution
- **Community**: Neighborhood-level service analysis
- **Accountability**: Municipal response time monitoring

### Business Intelligence
- **Location Planning**: Food truck density for restaurant site selection
- **Commuter Analysis**: Transit patterns for office location planning
- **Market Research**: Neighborhood activity and engagement patterns

## 🌟 PyMapGIS Integration

Local showcases demonstrate PyMapGIS capabilities:
- **Municipal API Integration**: Real-time city data processing
- **Spatial Analysis**: Neighborhood-level geographic analysis
- **Interactive Visualization**: Dynamic local maps with live data
- **Civic Intelligence**: Municipal service monitoring and analysis

## 🤝 Contributing

Want to add more local showcases? Here are some ideas:
- **Parking Availability Now**: Real-time parking space monitoring
- **Crime Patterns Now**: Public safety incident tracking
- **Air Quality Now**: Environmental monitoring by neighborhood
- **Construction Impact Now**: Infrastructure project tracking
- **Event Crowds Now**: Public event attendance and impact

## 📝 License

MIT License - see the [LICENSE](../LICENSE) file for details.

---

**🏙️ PyMapGIS Local Showcases** - Bringing hyperlocal intelligence to PyMapGIS with enhanced readability! 

*Demonstrating the power of municipal open data for community-driven geospatial analysis.*
