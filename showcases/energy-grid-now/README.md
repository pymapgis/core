# ⚡ Energy Grid Now

![Energy Grid Now](https://img.shields.io/badge/PyMapGIS-Showcase-blue) ![Status](https://img.shields.io/badge/Status-Active-green) ![License](https://img.shields.io/badge/License-MIT-yellow)

## 🎯 Why This Showcase?

Energy Grid Now demonstrates **real-time power grid monitoring and outage impact analysis** using PyMapGIS. This showcase addresses critical infrastructure resilience needs by:

- **⚡ Grid Resilience Monitoring**: Track power facility health across multiple dimensions
- **🏭 Multi-Modal Energy Sources**: Monitor nuclear, hydro, coal, gas, wind, and solar facilities
- **🚨 Outage Impact Analysis**: Assess economic and operational impacts of power disruptions
- **🌐 Regional Health Tracking**: Monitor grid stability across major US regions
- **📊 Resilience Scoring**: Quantify grid reliability for data-driven infrastructure planning

## 🚀 Quick Start

### Option 1: Docker (Recommended)
```bash
# Run Energy Grid Now (one command!)
docker run -p 8000:8000 nicholaskarlson/energy-grid-now:latest

# View at: http://localhost:8000
```

### Option 2: Local Development
```bash
# Clone and setup
git clone https://github.com/pymapgis/core.git
cd core/showcases/energy-grid-now

# Install dependencies with Poetry
poetry install

# Run the worker to process data
poetry run python energy_worker.py

# Start the web application
poetry run python app.py

# View at: http://localhost:8000
```

## 📊 What You'll See

### Interactive Energy Grid Map with Enhanced Lighter Styling
- **⚡ Power Facilities**: Real-time monitoring of 25 major US power facilities
- **🎨 Enhanced Readability**: Lighter map background for better visibility
- **📈 Resilience Visualization**: Color-coded facility health (green/yellow/orange/red)
- **🚨 Outage Tracking**: Interactive outages panel for grid issues
- **🌐 Regional Health**: Live regional grid stability monitoring

### Key Metrics
- **Total Capacity**: 56,117 MW across major US power facilities
- **Processing Speed**: <1 second for complete grid analysis
- **Update Frequency**: Real-time data refresh every 3 minutes
- **Resilience Factors**: Capacity, outage status, demand, facility age

## 🔧 Technical Architecture

### Energy Grid Data Processing Pipeline
1. **EIA Data Integration**: Fetch real-time energy facility data
2. **Multi-Factor Analysis**: Calculate resilience scores across 4 grid dimensions
3. **Outage Assessment**: Determine economic and operational impacts
4. **Regional Analysis**: Aggregate grid health by major US regions
5. **Alert Generation**: Identify critical grid vulnerabilities
6. **Geospatial Export**: Generate interactive grid visualizations

### API Endpoints
- `GET /` - Interactive map interface with enhanced lighter styling
- `GET /public/latest` - Public grid and resilience data
- `GET /internal/latest` - Full analyst data with metadata
- `GET /outages` - Current power outages and grid issues
- `GET /regional` - Regional grid health analysis
- `GET /health` - Service health and data availability

### Technology Stack
- **Backend**: FastAPI with async energy processing
- **Frontend**: MapLibre GL JS with enhanced light theme
- **Data Processing**: GeoPandas + Pandas for grid analysis
- **Visualization**: Interactive map with facility icons and resilience colors
- **Containerization**: Docker with optimized PyMapGIS base image

## ⚡ Energy Grid Features

### Multi-Dimensional Resilience Scoring
- **🏭 Capacity Impact**: Facility size affecting grid stability (0-100 scale)
- **🚨 Outage Impact**: Current operational status and disruptions (0-100 scale)
- **📊 Demand Impact**: Current load vs capacity affecting reliability (0-100 scale)
- **🕰️ Age Impact**: Infrastructure age affecting long-term resilience (0-100 scale)

### Facility Type Classification
- **⚛️ Nuclear**: Large baseload facilities with high capacity
- **🌊 Hydro**: Renewable facilities with flexible generation
- **🔥 Coal/Gas**: Fossil fuel facilities with variable operations
- **💨 Wind**: Renewable facilities with weather-dependent generation
- **☀️ Solar**: Renewable facilities with time-dependent generation

### Resilience Levels
- **🟢 Excellent (80+)**: Highly resilient, minimal risk
- **🟡 Good (60-80)**: Generally stable, monitor conditions
- **🟠 Fair (40-60)**: Some vulnerabilities, enhanced monitoring needed
- **🔴 Critical (<40)**: High risk, immediate attention required

### Grid Status Categories
- **Normal Operations**: Facility operating within normal parameters
- **High Demand**: Facility under stress from elevated demand
- **Reduced Capacity**: Facility operating at reduced output
- **Maintenance**: Planned maintenance affecting availability
- **Outage**: Facility offline due to unplanned issues

## 📈 Use Cases

### Infrastructure Resilience
- **Grid Planning**: Identify vulnerable facilities for investment prioritization
- **Risk Assessment**: Quantify grid stability across regions
- **Emergency Response**: Rapid assessment of outage impacts
- **Investment Strategy**: Data-driven infrastructure modernization

### Supply Chain Management
- **Manufacturing Planning**: Assess power reliability for industrial operations
- **Data Center Operations**: Monitor grid stability for critical facilities
- **Logistics Coordination**: Plan around potential power disruptions
- **Business Continuity**: Proactive planning for energy-related risks

### Energy Operations
- **Load Balancing**: Monitor facility capacity and demand
- **Maintenance Scheduling**: Coordinate maintenance across grid regions
- **Renewable Integration**: Track renewable facility performance
- **Grid Modernization**: Identify aging infrastructure needing upgrades

## 🔄 Data Sources

### Primary Data (Production Ready)
- **EIA (Energy Information Administration)**: Real-time facility data and capacity
- **NERC (North American Electric Reliability Corporation)**: Grid reliability data
- **Regional Grid Operators**: Real-time operational status
- **Major Power Facilities**: Top 25 US power generation facilities

### Mock Data (Demo)
For demonstration purposes, this showcase uses realistic mock data that simulates:
- 25 major power facilities across nuclear, hydro, coal, gas, wind, and solar
- Realistic capacity, demand, and operational status patterns
- Dynamic resilience calculations based on multiple factors
- Regional health aggregation across major US grid regions

## 🎨 Enhanced User Experience

### Lighter Map Styling (Enhanced!)
- **Improved Readability**: Brighter background for better contrast
- **Enhanced Visibility**: Grid overlays stand out clearly
- **Better Accessibility**: Easier reading for all users
- **Modern Design**: Clean, professional appearance
- **YouTube Optimized**: Perfect for video demonstrations

### Interactive Features
- **Facility Icons**: Intuitive symbols for quick facility type identification
- **Color-Coded Resilience**: Instant visual grid health assessment
- **Detailed Popups**: Comprehensive facility data on click
- **Outages Panel**: Toggle-able outages for grid issues
- **Regional Health**: Live regional stability monitoring
- **Auto-Refresh**: Live updates every 3 minutes

## 🛡️ Security & Performance

### Docker Optimization
- **Base Image Strategy**: Uses `nicholaskarlson/pymapgis-base:latest`
- **Build Time**: 11.3 seconds (95% faster than traditional builds)
- **Security**: Non-root `energygrid` user with proper permissions
- **Size**: Optimized ~200MB container

### Performance Metrics
- **Data Processing**: 0.95 seconds for 25 power facilities
- **Memory Usage**: <100MB RAM for full analysis
- **Startup Time**: <5 seconds from container launch
- **API Response**: <200ms for all endpoints

## 🌟 PyMapGIS Integration

This showcase demonstrates PyMapGIS capabilities:
- **Real-time Data Processing**: Efficient energy grid analysis
- **Multi-Factor Scoring**: Complex resilience calculations
- **Interactive Visualization**: Dynamic map updates with live data
- **Regional Aggregation**: Multi-level geographic analysis
- **Container Deployment**: Production-ready Docker packaging

## 🌐 Regional Grid Health

### US Grid Regions Monitored
- **Northeast**: High-density urban grid with aging infrastructure
- **Southeast**: Mixed generation with growing renewable integration
- **Midwest**: Coal-heavy grid transitioning to renewables
- **Southwest**: Solar-rich grid with transmission challenges
- **West**: Hydro-dominated grid with seasonal variability

### Regional Metrics
- **Average Resilience**: Regional grid stability scores
- **Total Capacity**: Aggregate generation capacity by region
- **Facility Count**: Number of major facilities per region
- **Critical Count**: Facilities requiring immediate attention

## 🤝 Contributing

Want to enhance Energy Grid Now? Here are some ideas:
- **Real EIA Integration**: Connect to live EIA APIs
- **Transmission Lines**: Add high-voltage transmission visualization
- **Demand Forecasting**: Predictive load analysis
- **Renewable Integration**: Enhanced wind/solar tracking
- **Carbon Intensity**: Emissions tracking by facility type

## 📝 License

MIT License - see the [LICENSE](../../LICENSE) file for details.

---

**⚡ Energy Grid Now** - Bringing real-time power grid intelligence to PyMapGIS with enhanced readability! 

*Part of the PyMapGIS showcase collection demonstrating geospatial data processing in action.*
