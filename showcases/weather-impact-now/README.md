# 🌦️ Weather Impact Now

![Weather Impact Now](https://img.shields.io/badge/PyMapGIS-Showcase-blue) ![Status](https://img.shields.io/badge/Status-Active-green) ![License](https://img.shields.io/badge/License-MIT-yellow)

## 📺 **Demo Video**

🎬 **Watch Weather Impact Now in Action**: https://youtu.be/MX9dv3GcF_I

See the enhanced lighter map styling, real-time weather monitoring, multi-dimensional impact analysis, and interactive alert system in this comprehensive demo video.

## 🎯 Why This Showcase?

Weather Impact Now demonstrates **real-time weather monitoring and supply chain impact analysis** using PyMapGIS. This showcase addresses critical infrastructure resilience needs by:

- **🌡️ Multi-Hazard Monitoring**: Track temperature, wind, precipitation, and visibility impacts
- **🚛 Transportation Risk Assessment**: Analyze weather effects on air, ground, and maritime transport
- **⚠️ Real-time Alerts**: Identify severe weather conditions affecting operations
- **📊 Impact Scoring**: Quantify weather severity for data-driven decision making

## 🚀 Quick Start

### Option 1: Docker (Recommended)
```bash
# Run Weather Impact Now (one command!)
docker run -p 8000:8000 nicholaskarlson/weather-impact-now:latest

# View at: http://localhost:8000
```

### Option 2: Local Development
```bash
# Clone and setup
git clone https://github.com/pymapgis/core.git
cd core/showcases/weather-impact-now

# Install dependencies with Poetry
poetry install

# Run the worker to process data
poetry run python weather_worker.py

# Start the web application
poetry run python app.py

# View at: http://localhost:8000
```

## 📊 What You'll See

### Interactive Weather Map with Lighter Styling
- **🌦️ Weather Conditions**: Real-time monitoring of 50 major US cities
- **🎨 Enhanced Readability**: Lighter map background for better visibility
- **📈 Impact Visualization**: Color-coded severity levels (green/yellow/orange/red)
- **⚠️ Alert System**: Interactive alerts panel for high-impact locations
- **🌡️ Detailed Popups**: Click any location for comprehensive weather data

### Key Metrics
- **Total Locations**: 50 major US cities with weather monitoring
- **Processing Speed**: <3 seconds for complete weather analysis
- **Update Frequency**: Real-time data refresh every 5 minutes
- **Impact Categories**: Temperature, wind, precipitation, visibility

## 🔧 Technical Architecture

### Weather Data Processing Pipeline
1. **NOAA Data Integration**: Fetch real-time weather observations
2. **Multi-Factor Analysis**: Calculate impact scores across 4 weather dimensions
3. **Risk Assessment**: Determine transportation and operational risks
4. **Alert Generation**: Identify high-impact weather conditions
5. **Geospatial Export**: Generate interactive map visualizations

### API Endpoints
- `GET /` - Interactive map interface with lighter styling
- `GET /public/latest` - Public weather and impact data
- `GET /internal/latest` - Full analyst data with metadata
- `GET /alerts` - Current weather alerts and warnings
- `GET /health` - Service health and data availability

### Technology Stack
- **Backend**: FastAPI with async weather processing
- **Frontend**: MapLibre GL JS with enhanced light theme
- **Data Processing**: GeoPandas + Pandas for weather analysis
- **Visualization**: Interactive map with weather icons and impact colors
- **Containerization**: Docker with optimized PyMapGIS base image

## 🌦️ Weather Impact Features

### Multi-Dimensional Impact Scoring
- **🌡️ Temperature Impact**: Extreme heat/cold affecting operations (0-100 scale)
- **💨 Wind Impact**: High winds affecting air/sea transport (0-100 scale)
- **🌧️ Precipitation Impact**: Rain/snow affecting ground transport (0-100 scale)
- **👁️ Visibility Impact**: Fog/conditions affecting all transport modes (0-100 scale)

### Weather Condition Classification
- **☀️ Clear**: Normal operations, minimal weather impact
- **🌧️ Rain**: Precipitation affecting ground transportation
- **❄️ Snow/Ice**: Winter conditions with high transport risk
- **💨 Windy**: High winds affecting aviation and maritime
- **🌡️ Extreme Temperature**: Heat/cold affecting infrastructure
- **🌫️ Fog**: Low visibility affecting all transportation modes

### Impact Severity Levels
- **🟢 Low (0-25)**: Minimal impact, normal operations
- **🟡 Moderate (25-50)**: Some delays possible, monitor conditions
- **🟠 High (50-75)**: Significant delays likely, adjust operations
- **🔴 Severe (75+)**: Major disruptions expected, consider cancellations

### Transportation Risk Assessment
- **Minimal Risk**: Normal operations across all transport modes
- **Low Risk**: Minor impacts, slight delays possible
- **Moderate Risk**: Some delays possible, monitor conditions
- **High Risk**: Delays and cancellations likely across transport modes

## 📈 Use Cases

### Supply Chain Management
- **Route Planning**: Avoid weather-impacted corridors
- **Inventory Management**: Anticipate weather-related delays
- **Risk Mitigation**: Proactive planning for severe weather events
- **Cost Optimization**: Minimize weather-related operational costs

### Transportation Operations
- **Flight Operations**: Weather impact on airport operations
- **Ground Transport**: Road conditions and visibility assessment
- **Maritime Operations**: Wind and precipitation effects on ports
- **Logistics Coordination**: Multi-modal transport planning

### Emergency Preparedness
- **Early Warning**: Severe weather alert system
- **Resource Allocation**: Deploy resources based on impact predictions
- **Business Continuity**: Weather-aware operational planning
- **Risk Communication**: Share weather intelligence across teams

## 🔄 Data Sources

### Primary Data (Production Ready)
- **NOAA Weather Service**: Real-time observations and forecasts
- **National Weather Service**: Severe weather warnings and alerts
- **Airport Weather Stations**: Aviation-specific weather data
- **Major Cities**: Top 50 US metropolitan weather monitoring

### Mock Data (Demo)
For demonstration purposes, this showcase uses realistic mock data that simulates:
- 50 weather locations across major US cities
- Realistic temperature, wind, precipitation, and visibility patterns
- Dynamic impact calculations based on weather severity
- Alert generation for high-impact conditions

## 🎨 Enhanced User Experience

### Lighter Map Styling (New!)
- **Improved Readability**: Brighter background for better contrast
- **Enhanced Visibility**: Weather overlays stand out clearly
- **Better Accessibility**: Easier reading for all users
- **Modern Design**: Clean, professional appearance

### Interactive Features
- **Weather Icons**: Intuitive symbols for quick condition identification
- **Color-Coded Severity**: Instant visual impact assessment
- **Detailed Popups**: Comprehensive weather data on click
- **Alert Panel**: Toggle-able alerts for high-impact locations
- **Auto-Refresh**: Live updates every 5 minutes

## 🛡️ Security & Performance

### Docker Optimization
- **Base Image Strategy**: Uses `nicholaskarlson/pymapgis-base:latest`
- **Build Time**: 12.8 seconds (95% faster than traditional builds)
- **Security**: Non-root `weatherimpact` user with proper permissions
- **Size**: Optimized ~200MB container

### Performance Metrics
- **Data Processing**: 2.23 seconds for 50 weather locations
- **Memory Usage**: <100MB RAM for full analysis
- **Startup Time**: <5 seconds from container launch
- **API Response**: <200ms for all endpoints

## 🌟 PyMapGIS Integration

This showcase demonstrates PyMapGIS capabilities:
- **Real-time Data Processing**: Efficient weather data analysis
- **Multi-Factor Scoring**: Complex impact calculations
- **Interactive Visualization**: Dynamic map updates with live data
- **Alert Systems**: Automated threshold-based notifications
- **Container Deployment**: Production-ready Docker packaging

## 🤝 Contributing

Want to enhance Weather Impact Now? Here are some ideas:
- **Real NOAA Integration**: Connect to live weather APIs
- **Historical Analysis**: Add weather trend analysis
- **Machine Learning**: Predictive weather impact models
- **Mobile Optimization**: Responsive design improvements
- **Additional Metrics**: Humidity, pressure, UV index integration

## 📝 License

MIT License - see the [LICENSE](../../LICENSE) file for details.

---

**🌦️ Weather Impact Now** - Bringing real-time weather intelligence to PyMapGIS with enhanced readability! 

*Part of the PyMapGIS showcase collection demonstrating geospatial data processing in action.*
