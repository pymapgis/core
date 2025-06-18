# 🚇 London Tube Status Now

![Tube Status](https://img.shields.io/badge/PyMapGIS-Local%20Showcase-blue) ![Status](https://img.shields.io/badge/Status-Active-green) ![License](https://img.shields.io/badge/License-MIT-yellow) ![London](https://img.shields.io/badge/City-London-red)

## 📺 **Demo Video**

🎬 **Watch London Tube Status Now in Action**: https://youtu.be/HL-xlLP8Jko

See the enhanced lighter map styling, real-time TfL API integration, authentic London Underground branding, and interactive tube line status features in this comprehensive demo video.

## 🎯 Why This Showcase?

London Tube Status Now demonstrates real-time London Underground service monitoring using Transport for London (TfL) APIs. This showcase provides instant visibility into tube line status, disruptions, and travel recommendations for the world's most iconic metro system.

**Perfect for:**
- 🧳 **Tourists**: Check tube status before traveling around London
- 🏢 **Commuters**: Find the best routes during rush hour
- 🎯 **Travel Planning**: Avoid disrupted lines and delays
- 📊 **Transport Analysis**: Monitor London's transport network performance

## ⚡ Quick Start

### 🐳 Option 1: Docker (Recommended)
```bash
# Run the London Tube Status Now showcase
docker run -p 8000:8000 nicholaskarlson/london-tube-status-now:latest

# Access the application
open http://localhost:8000
```

### 🔧 Option 2: Local Development
```bash
# Clone the repository
git clone https://github.com/pymapgis/core.git
cd core/showcaseslocal/london-tube-status-now

# Install dependencies with Poetry
poetry install

# Run the TfL data processor
poetry run python tube_worker.py

# Start the web application
poetry run python app.py

# View at: http://localhost:8000
```

## 🌟 Features

### 🚇 **Real-time Tube Status**
- **Live TfL API Integration**: Direct connection to Transport for London APIs
- **All 11 Tube Lines**: Complete coverage of London Underground network
- **Service Status Tracking**: Good Service, Minor Delays, Severe Delays, Suspended
- **Disruption Monitoring**: Real-time alerts and engineering works

### 🎨 **Enhanced Lighter Styling**
- **Brightest Background**: Perfect contrast for tube line colors
- **Official TfL Colors**: Authentic London Underground line colors
- **Interactive Tube Map**: Click any line for detailed status information
- **Tourist-Friendly Design**: Clear, accessible interface for visitors

### 📊 **Smart Travel Recommendations**
- **Best Route Suggestions**: Identify lines with good service
- **Disruption Warnings**: Avoid lines with delays or suspensions
- **Status Scoring**: 0-10 scale for easy comparison
- **Real-time Updates**: Refreshes every 30 seconds

## 🗺️ Data Sources

### 🇬🇧 **Transport for London (TfL) APIs**
- **Line Status API**: `https://api.tfl.gov.uk/Line/Mode/tube/Status`
- **Disruptions API**: `https://api.tfl.gov.uk/Line/Mode/tube/Disruption`
- **No API Key Required**: Free access to real-time data
- **High Reliability**: 10+ years of stable API availability

### 📍 **Coverage**
- **All 11 Tube Lines**: Bakerloo, Central, Circle, District, Hammersmith & City, Jubilee, Metropolitan, Northern, Piccadilly, Victoria, Waterloo & City
- **Central London Focus**: Optimized for tourist and business districts
- **Real-time Updates**: Live status from TfL control center

## 🏗️ Technical Architecture

### 📁 **File Structure**
```
london-tube-status-now/
├── tube_worker.py          # ~35 LOC TfL API processor
├── app.py                  # FastAPI web application
├── static/index.html       # Enhanced lighter tube map interface
├── Dockerfile              # Optimized PyMapGIS base image
├── pyproject.toml          # Poetry dependencies
└── README.md               # This documentation
```

### ⚡ **Performance Metrics**
- **Build Time**: ~10 seconds (using PyMapGIS base optimization)
- **Container Size**: ~200MB optimized
- **API Response**: <200ms for all endpoints
- **Data Processing**: <1 second for all 11 tube lines
- **Update Frequency**: Every 30 seconds during peak hours

## 🔌 API Endpoints

### 📊 **Public Endpoints**
- `GET /` - Interactive tube status map
- `GET /health` - Service health check
- `GET /tube/status` - Complete tube status data
- `GET /tube/lines` - Tube lines with current status
- `GET /tube/summary` - System summary statistics
- `GET /public/latest` - Latest public data (for frontend)

### 🔄 **Management Endpoints**
- `GET /api/refresh` - Manually refresh tube status data
- `GET /docs` - API documentation (Swagger UI)
- `GET /redoc` - Alternative API documentation

## 🎨 Enhanced Lighter Styling

### 🌟 **Design Features**
- **Brightest Background**: Maximum contrast for tube line visibility
- **Official TfL Colors**: Authentic London Underground branding
- **Status Color Coding**: Green (Good) → Red (Suspended)
- **Interactive Elements**: Hover effects and click interactions
- **Mobile Optimized**: Responsive design for all devices

### 🚇 **Tube Line Colors**
- **Bakerloo**: #B36305 (Brown)
- **Central**: #E32017 (Red)
- **Circle**: #FFD300 (Yellow)
- **District**: #00782A (Green)
- **Hammersmith & City**: #F3A9BB (Pink)
- **Jubilee**: #A0A5A9 (Grey)
- **Metropolitan**: #9B0056 (Magenta)
- **Northern**: #000000 (Black)
- **Piccadilly**: #003688 (Dark Blue)
- **Victoria**: #0098D4 (Light Blue)
- **Waterloo & City**: #95CDBA (Turquoise)

## 🚀 Use Cases

### 🧳 **Tourism**
- **Pre-visit Planning**: Check tube status before traveling to attractions
- **Real-time Navigation**: Find working routes to destinations
- **Disruption Avoidance**: Avoid suspended or delayed lines

### 🏢 **Commuting**
- **Rush Hour Planning**: Identify best routes during peak times
- **Alternative Routes**: Find backup options when primary routes disrupted
- **Time Management**: Plan journey times based on current status

### 📊 **Transport Analysis**
- **Network Performance**: Monitor overall system reliability
- **Pattern Recognition**: Identify frequently disrupted lines
- **Service Quality**: Track improvements and issues over time

## 🔧 Development

### 📚 **Setup Documentation**
- **[Poetry Setup Guide](../docs/poetry-setup.md)** - Complete installation and usage
- **[Docker Setup Guide](../docs/docker-setup.md)** - Optimization and WSL2 integration
- **[WSL2 Setup Guide](../docs/wsl2-setup.md)** - Windows development environment

### 🧪 **Testing**
```bash
# Test the TfL API connection
poetry run python tube_worker.py

# Test the web application
poetry run python app.py

# Test Docker build
docker build -t london-tube-status-now .

# Test Docker run
docker run -p 8000:8000 london-tube-status-now
```

## 🌍 Global Impact

### 🎯 **Why London Matters**
- **Global Recognition**: Everyone knows the London Underground
- **Tourist Destination**: Millions of visitors use the tube annually
- **Transport Innovation**: London leads in urban transport technology
- **Data Quality**: TfL provides world-class open data

### 🚀 **Expansion Opportunities**
- **London Buses**: Add bus status and real-time arrivals
- **London Overground**: Include Overground and DLR services
- **Accessibility**: Add step-free access information
- **Journey Planning**: Integrate with TfL Journey Planner API

## 🤝 Contributing

Want to enhance London Tube Status Now? Here are some ideas:

- **🚌 Bus Integration**: Add London bus real-time arrivals
- **♿ Accessibility**: Include step-free access information
- **🚶 Walking Routes**: Add walking alternatives during disruptions
- **📱 Mobile App**: Create native mobile application
- **🔔 Notifications**: Add push notifications for favorite lines

## 📝 License

MIT License - see the LICENSE file for details.

---

**🚇 Experience the power of real-time London transport intelligence with PyMapGIS!**
