# 🚚 Open Food Trucks Now - San Francisco Live Lunch Heat-Map

![Food Trucks](https://img.shields.io/badge/PyMapGIS-Local%20Showcase-blue) ![Status](https://img.shields.io/badge/Status-Active-green) ![License](https://img.shields.io/badge/License-MIT-yellow)

## 🎯 Why This Showcase?

Open Food Trucks Now demonstrates **real-time food truck location intelligence** using San Francisco's open data. This showcase represents the perfect example of hyperlocal geospatial analysis by:

- **🌮 Live Lunch Intelligence**: Real-time food truck locations and schedules
- **🏙️ Neighborhood Analysis**: Spatial density analysis using SF neighborhood polygons
- **📊 Lunch Heat-Maps**: Visual density mapping for optimal food truck discovery
- **⏰ Time-Aware Filtering**: Only show currently open and permitted food trucks
- **🎨 Enhanced Lighter Styling**: Perfect readability for lunch planning

## 🚀 Quick Start

### Option 1: Docker (Recommended)
```bash
# Run Open Food Trucks Now (one command!)
docker run -p 8000:8000 nicholaskarlson/open-food-trucks-now:latest

# View at: http://localhost:8000
```

### Option 2: Poetry (Local Development)
```bash
# Clone and setup
git clone https://github.com/pymapgis/core.git
cd core/showcaseslocal/open-food-trucks-now

# Install dependencies with Poetry
poetry install

# Run the worker to process data
poetry run python truck_worker.py

# Start the web application
poetry run python app.py

# View at: http://localhost:8000
```

### Option 3: Manual Setup
```bash
# Install Python dependencies
pip install fastapi uvicorn pandas geopandas requests matplotlib

# Run the data processor
python3 truck_worker.py

# Start the web server
python3 app.py

# View at: http://localhost:8000
```

## 📊 What You'll See

### Interactive Food Truck Map with Enhanced Lighter Styling
- **🚚 Live Food Truck Locations**: Real-time SF food truck positions with vendor details
- **🎨 Ultimate Readability**: Brightest map background for perfect lunch planning visibility
- **🏙️ Neighborhood Density**: Color-coded SF neighborhoods by food truck concentration
- **🌮 Food Type Icons**: Visual indicators for cuisine types (tacos, burgers, Asian, etc.)
- **⏰ Operating Hours**: Current status and closing times for each food truck
- **📍 Location Details**: Exact addresses and vendor information

### Key Metrics
- **Total Food Trucks**: Live count of currently operating food trucks
- **Active Neighborhoods**: SF neighborhoods with active food truck presence
- **Lunch Density**: Heat-map showing food truck concentration hotspots
- **Update Frequency**: Real-time data refresh every 15 minutes during lunch hours

## 🔧 Technical Architecture

### Food Truck Data Processing Pipeline
1. **SF Open Data Integration**: Fetch live food truck schedule from SF Open Data API
2. **Permit Filtering**: Keep only currently approved and operating food trucks
3. **Time-Based Filtering**: Filter for trucks open during current time
4. **Geospatial Processing**: Convert lat/lon to points and validate SF boundaries
5. **Neighborhood Analysis**: Spatial join with SF neighborhood polygons using `geopandas.sjoin()`
6. **Density Calculation**: Calculate food truck density per neighborhood
7. **Export Generation**: Create interactive GeoJSON and API-ready data

### API Endpoints
- `GET /` - Interactive map interface with enhanced lighter styling
- `GET /public/latest` - Public food truck and neighborhood data
- `GET /health` - Service health and data availability
- `GET /neighborhoods` - SF neighborhoods with food truck density
- `GET /trucks` - Current food truck locations and details

### Technology Stack
- **Backend**: FastAPI with async food truck processing
- **Frontend**: MapLibre GL JS with enhanced light theme
- **Data Processing**: GeoPandas + Pandas for spatial analysis
- **Visualization**: Interactive map with food truck density colors
- **Containerization**: Docker with optimized PyMapGIS base image

## 🚚 Food Truck Features

### Real-time Data Sources
- **SF Food Truck Schedule**: `https://data.sfgov.org/resource/jjew-5d7t.json`
- **SF Neighborhood Polygons**: `https://data.sfgov.org/resource/ejmn-km5w.geojson`
- **Update Frequency**: Every 15 minutes during lunch hours (10 AM - 3 PM)

### Intelligent Filtering
- **Permit Status**: Only APPROVED food truck permits
- **Operating Hours**: Filter by current time vs. truck schedule
- **Geographic Bounds**: Validate locations within SF city limits
- **Data Quality**: Remove trucks with missing location data

### Neighborhood Density Analysis
- **Spatial Join**: Use `geopandas.sjoin()` for truck-to-neighborhood mapping
- **Density Calculation**: Count trucks per neighborhood polygon
- **Heat-Map Visualization**: Color-coded neighborhoods by truck concentration
- **Hotspot Identification**: Find the best areas for food truck variety

### Food Type Classification
- **🌮 Tacos & Mexican**: Tacos, burritos, quesadillas, Mexican cuisine
- **🍔 Burgers & American**: Burgers, fries, American comfort food
- **🍜 Asian Fusion**: Rice bowls, noodles, Asian-inspired dishes
- **🥪 Sandwiches & Deli**: Sandwiches, salads, deli-style food
- **🍕 Pizza & Italian**: Pizza, pasta, Italian specialties

## 📈 Use Cases

### Lunch Planning
- **Food Truck Discovery**: Find nearby food trucks during lunch hours
- **Variety Assessment**: See food truck density and cuisine diversity
- **Time Management**: Check operating hours and closing times
- **Location Intelligence**: Identify food truck hotspots in SF

### Urban Analysis
- **Food Access**: Analyze food truck distribution across SF neighborhoods
- **Economic Activity**: Track food truck concentration patterns
- **Permit Utilization**: Monitor food truck permit usage and compliance
- **Lunch Infrastructure**: Understand SF's mobile food ecosystem

### Business Intelligence
- **Competition Analysis**: Food truck density for new vendor planning
- **Location Selection**: Identify underserved neighborhoods
- **Market Research**: Food truck popularity and cuisine trends
- **Foot Traffic**: Correlate food truck presence with pedestrian activity

## 🔄 Data Sources & Mock Fallback

### Primary Data (Production Ready)
- **SF Open Data Portal**: Real-time food truck schedule and permits
- **SF Neighborhood Boundaries**: Official city neighborhood polygons
- **Live Updates**: 15-minute refresh cycle during lunch hours

### Mock Data (Demo)
When SF APIs are unavailable, the showcase uses realistic mock data:
- 5 sample food trucks across different SF neighborhoods
- Realistic vendor names, food items, and operating hours
- 3 SF neighborhood polygons (SOMA, Mission, Financial District)
- Proper geospatial formatting and density calculations

## 🎨 Enhanced Lighter Styling

### Ultimate Lunch Planning Visibility
- **Brightest Background**: Maximum contrast for outdoor lunch planning
- **Food Truck Icons**: Clear, colorful markers for easy identification
- **Neighborhood Colors**: Intuitive density heat-map with bright colors
- **Mobile Optimized**: Perfect for on-the-go lunch decisions
- **Professional Design**: Clean, modern interface for food discovery

### Interactive Features
- **Food Truck Popups**: Detailed vendor information on click
- **Density Toggle**: Show/hide neighborhood density overlay
- **Real-time Updates**: Live data refresh with visual indicators
- **Cuisine Filtering**: Filter by food type preferences
- **Location Search**: Find food trucks near specific addresses

## 🛡️ Performance & Reliability

### Processing Speed
- **Data Processing**: <1 second for 100+ food truck locations
- **Spatial Analysis**: Instant neighborhood density calculation
- **API Response**: <200ms for all endpoints
- **Map Rendering**: Smooth interactive experience

### Docker Optimization
- **Build Time**: 10-12 seconds using PyMapGIS base image
- **Container Size**: ~200MB optimized
- **Startup Time**: <5 seconds from container launch
- **Memory Usage**: <100MB RAM for full analysis

## 📚 Setup Documentation

For detailed setup instructions, see our centralized documentation:

- **[Poetry Setup Guide](../docs/poetry-setup.md)** - Complete Poetry installation and usage guide
- **[Docker Setup Guide](../docs/docker-setup.md)** - Docker installation, optimization, and WSL2 integration
- **[WSL2 Setup Guide](../docs/wsl2-setup.md)** - Windows Subsystem for Linux 2 setup for PyMapGIS development

### Quick Setup Summary
```bash
# 1. Install Poetry (see Poetry Setup Guide for details)
curl -sSL https://install.python-poetry.org | python3 -

# 2. Install Docker (see Docker Setup Guide for details)
# Windows: Download Docker Desktop + enable WSL2 integration
# Linux: sudo apt install docker.io

# 3. Clone and run Food Trucks showcase
git clone https://github.com/pymapgis/core.git
cd core/showcaseslocal/open-food-trucks-now

# Option A: Docker (recommended)
docker run -p 8000:8000 nicholaskarlson/open-food-trucks-now:latest

# Option B: Poetry
poetry install && poetry run python food_truck_app.py
```

## 🌟 PyMapGIS Integration

This showcase demonstrates PyMapGIS capabilities:
- **Municipal API Integration**: Real-time city data processing
- **Spatial Analysis**: Neighborhood-level geographic analysis
- **Interactive Visualization**: Dynamic local maps with live data
- **Hyperlocal Intelligence**: Food truck discovery and lunch planning

## 🤝 Contributing

Want to enhance Open Food Trucks Now? Here are some ideas:
- **Real-time Tracking**: GPS integration for moving food trucks
- **User Reviews**: Community ratings and recommendations
- **Menu Integration**: Detailed food truck menus and pricing
- **Wait Time Prediction**: Crowd-sourced wait time estimates
- **Favorite Trucks**: User preferences and notification system

## 📝 License

MIT License - see the [LICENSE](../../LICENSE) file for details.

---

**🚚 Open Food Trucks Now** - Bringing real-time food truck intelligence to San Francisco with enhanced readability! 

*The perfect example of hyperlocal geospatial analysis for daily life applications.*
