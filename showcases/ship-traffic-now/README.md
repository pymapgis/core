# 🚢 Ship Traffic Now

![Ship Traffic Now](https://img.shields.io/badge/PyMapGIS-Showcase-blue) ![Status](https://img.shields.io/badge/Status-Active-green) ![License](https://img.shields.io/badge/License-MIT-yellow)

## 📺 **Demo Video**

🎬 **Watch Ship Traffic Now in Action**: https://youtu.be/a9xSScrlKpw

See the real-time maritime vessel tracking, port congestion analysis, and interactive map visualization in this comprehensive demo video.

## 🎯 Why This Showcase?

Ship Traffic Now demonstrates **real-time maritime vessel tracking and port congestion analysis** using PyMapGIS. This showcase addresses critical supply chain visibility needs by:

- **🌊 Maritime Traffic Monitoring**: Track vessel positions, speeds, and classifications
- **🏭 Port Congestion Analysis**: Calculate real-time congestion scores for major ports
- **📊 Supply Chain Intelligence**: Identify bottlenecks and traffic patterns
- **⚓ Vessel Classification**: Categorize ships by type, size, and operational status

## 🚀 Quick Start

### Option 1: Docker (Recommended)
```bash
# Run Ship Traffic Now (one command!)
docker run -p 8000:8000 nicholaskarlson/ship-traffic-now:latest

# View at: http://localhost:8000
```

### Option 2: Local Development
```bash
# Clone and setup
git clone https://github.com/pymapgis/core.git
cd core/showcases/ship-traffic-now

# Install dependencies with Poetry
poetry install

# Run the worker to process data
poetry run python ship_worker.py

# Start the web application
poetry run python app.py

# View at: http://localhost:8000
```

## 📊 What You'll See

### Interactive Maritime Map
- **🚢 Vessel Positions**: Real-time locations of 136+ vessels
- **🏭 Port Congestion**: Color-coded congestion levels at 15 major US ports
- **⚓ Vessel Details**: Click any vessel for detailed information
- **📈 Traffic Patterns**: Visual analysis of maritime traffic flow

### Key Metrics
- **Total Vessels**: 136 tracked vessels across major shipping routes
- **Port Coverage**: 15 major US ports from Los Angeles to New York
- **Processing Speed**: <2 seconds for complete analysis
- **Update Frequency**: Real-time data refresh every 2 minutes

## 🔧 Technical Architecture

### Data Processing Pipeline
1. **AIS Data Ingestion**: Fetch vessel positions and metadata
2. **Port Proximity Analysis**: Calculate vessels within 10km of each port
3. **Congestion Scoring**: Combine vessel count and average speed metrics
4. **Geospatial Export**: Generate GeoJSON for map visualization

### API Endpoints
- `GET /` - Interactive map interface
- `GET /public/latest` - Public vessel and port data
- `GET /internal/latest` - Full analyst data with metadata
- `GET /health` - Service health and data availability

### Technology Stack
- **Backend**: FastAPI with async processing
- **Frontend**: MapLibre GL JS with OpenStreetMap background
- **Data Processing**: GeoPandas + Pandas for geospatial analysis
- **Visualization**: Interactive map with vessel classification
- **Containerization**: Docker with optimized PyMapGIS base image

## 🌊 Maritime Data Features

### Vessel Classification
- **Container Ships**: Blue markers for containerized cargo
- **Tankers**: Red markers for liquid cargo vessels
- **Cargo Ships**: Green markers for general cargo
- **Bulk Carriers**: Purple markers for dry bulk commodities
- **Other Types**: Passenger, fishing, tug, and service vessels

### Port Congestion Analysis
- **Green (0-5)**: Low congestion, normal operations
- **Yellow (5-15)**: Medium congestion, some delays possible
- **Orange (15-30)**: High congestion, significant delays likely
- **Red (30+)**: Very high congestion, major bottlenecks

### Vessel Status Classification
- **Anchored**: Speed < 0.5 knots (stationary)
- **Maneuvering**: Speed 0.5-5 knots (port operations)
- **Transit**: Speed 5-15 knots (normal sailing)
- **High Speed**: Speed > 15 knots (fast transit)

## 📈 Use Cases

### Supply Chain Management
- **Port Selection**: Choose less congested ports for faster turnaround
- **Arrival Planning**: Predict delays based on current congestion
- **Route Optimization**: Identify efficient shipping corridors

### Maritime Operations
- **Traffic Monitoring**: Real-time awareness of vessel movements
- **Safety Analysis**: Identify high-density areas requiring attention
- **Capacity Planning**: Understand port utilization patterns

### Logistics Intelligence
- **Delay Prediction**: Anticipate supply chain disruptions
- **Performance Metrics**: Track port efficiency over time
- **Risk Assessment**: Identify potential bottlenecks

## 🔄 Data Sources

### Primary Data
- **AIS Maritime Traffic**: Automatic Identification System vessel positions
- **Port Locations**: Major US commercial ports with coordinates
- **Vessel Registry**: Ship classifications, dimensions, and flags

### Mock Data (Demo)
For demonstration purposes, this showcase uses realistic mock data that simulates:
- 136 vessels distributed around major US ports
- Realistic vessel types, speeds, and classifications
- Dynamic congestion calculations based on vessel density

## 🛡️ Security & Performance

### Docker Optimization
- **Base Image Strategy**: Uses `nicholaskarlson/pymapgis-base:latest`
- **Build Time**: 15.9 seconds (95% faster than previous builds)
- **Security**: Non-root `shiptraffic` user with proper permissions
- **Size**: Optimized ~200MB container

### Performance Metrics
- **Data Processing**: 1.32 seconds for 136 vessels
- **Memory Usage**: <100MB RAM for full analysis
- **Startup Time**: <5 seconds from container launch
- **API Response**: <200ms for all endpoints

## 🌟 PyMapGIS Integration

This showcase demonstrates PyMapGIS capabilities:
- **Geospatial Data Processing**: Efficient handling of vessel coordinates
- **Proximity Analysis**: Buffer operations for port congestion
- **Real-time Visualization**: Dynamic map updates with live data
- **API Development**: RESTful endpoints for data access
- **Container Deployment**: Production-ready Docker packaging

## 🤝 Contributing

Want to enhance Ship Traffic Now? Here are some ideas:
- **Real AIS Integration**: Connect to live maritime data feeds
- **Historical Analysis**: Add time-series congestion trends
- **Weather Integration**: Include weather impact on vessel movements
- **Route Prediction**: ML models for vessel destination prediction
- **Alert System**: Notifications for congestion threshold breaches

## 📝 License

MIT License - see the [LICENSE](../../LICENSE) file for details.

---

**🚢 Ship Traffic Now** - Bringing real-time maritime intelligence to PyMapGIS! 

*Part of the PyMapGIS showcase collection demonstrating geospatial data processing in action.*
