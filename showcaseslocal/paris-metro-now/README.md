# 🚇 Paris Metro Now

![Transit Status](https://img.shields.io/badge/PyMapGIS-Local%20Showcase-blue) ![Status](https://img.shields.io/badge/Status-Active-green) ![License](https://img.shields.io/badge/License-MIT-yellow) ![Paris](https://img.shields.io/badge/City-Paris-blue) ![France](https://img.shields.io/badge/Country-France-blue)

## 📺 **Demo Video**

🎬 **Watch Paris Metro Now in Action**: https://youtu.be/sBfiKZOTtS4

See the enhanced lighter map styling, real-time French Metro/RER/bus tracking, elegance and sophistication analytics, and interactive Parisian transit features in this comprehensive demo video.

## 🎯 Why This Showcase?

Paris Metro Now demonstrates real-time French public transport monitoring using RATP API integration. This showcase provides comprehensive visibility into Metro, RER, and bus operations across the world's most elegant transit system in the City of Light.

**Perfect for:**
- 🏢 **Commuters**: Navigate Paris's sophisticated transit network efficiently
- 🧳 **Visitors**: Experience French elegance and style in public transport
- 🎯 **Transit Planning**: Monitor system elegance and French precision
- 📊 **Urban Analysis**: Study French transport artistry and sophistication

## ⚡ Quick Start

### 🐳 Option 1: Docker (Recommended)
```bash
# Run the Paris Metro Now showcase
docker run -p 8000:8000 nicholaskarlson/paris-metro-now:latest

# Access the application
open http://localhost:8000
```

### 🔧 Option 2: Local Development
```bash
# Clone the repository
git clone https://github.com/pymapgis/core.git
cd core/showcaseslocal/paris-metro-now

# Install dependencies with Poetry
poetry install

# Run the French transit data processor
poetry run python transit_worker.py

# Start the web application
poetry run python app.py

# View at: http://localhost:8000
```

## 🌟 Features

### 🚇 **Complete French Transit Coverage**
- **Metro Network**: All major lines (1, 4, 6, 7, 8, 9, 11, 14) with iconic French design
- **RER System**: Regional express lines (A, B, C, D) connecting Paris and suburbs
- **Bus Network**: Major Parisian bus routes with RATP integration
- **Real-time Elegance**: French style tracking, sophistication analysis, punctuality monitoring

### 🎨 **Enhanced Lighter Styling**
- **Brightest Background**: Perfect contrast for French transit colors
- **Official French Branding**: Authentic RATP Metro, RER, and bus colors
- **Interactive Transit Map**: Click any route for detailed elegance metrics
- **French Design**: Sophisticated, artistic interface with 🇫🇷 branding

### 📊 **Smart French Elegance Analytics**
- **Elegance Scoring**: 0-10 scale based on French style standards
- **Service Categories**: Excellent, Good, Fair, Poor classifications
- **Real-time Metrics**: Delay tracking, punctuality percentages, frequency analysis
- **Route Filtering**: Toggle Metro, RER, and bus visibility

## 🗺️ Data Sources

### 🇫🇷 **French Public Transport APIs**
- **RATP (Régie Autonome des Transports Parisiens)**: Paris transport authority
- **Real-time Traffic**: Live service status and performance updates
- **High Reliability**: Production-grade French transit data
- **Update Frequency**: Every 3 minutes for dynamic French precision

### 📍 **Transit Network**
- **Metro Lines**: 14 lines covering central Paris with artistic stations
- **RER Network**: 5 lines connecting Paris, suburbs, and airports
- **Bus System**: 60+ routes across Paris metropolitan area
- **Integration**: Seamless multi-modal French elegance

## 🏗️ Technical Architecture

### 📁 **File Structure**
```
paris-metro-now/
├── transit_worker.py       # ~35 LOC French transit processor
├── app.py                  # FastAPI web application
├── static/index.html       # Enhanced lighter French interface
├── Dockerfile              # Optimized PyMapGIS base image
├── pyproject.toml          # Poetry dependencies
└── README.md               # This documentation
```

### ⚡ **Performance Metrics**
- **Build Time**: ~12 seconds (using PyMapGIS base optimization)
- **Container Size**: ~200MB optimized
- **API Response**: <200ms for all endpoints
- **Data Processing**: <5 seconds for all 8 routes
- **Update Frequency**: Every 3 minutes during peak hours

## 🔌 API Endpoints

### 📊 **Public Endpoints**
- `GET /` - Interactive Paris Metro map
- `GET /health` - Service health check
- `GET /transit/status` - Complete French transit status data
- `GET /transit/routes` - Transit routes with current elegance
- `GET /transit/summary` - System summary statistics
- `GET /public/latest` - Latest public data (for frontend)

### 🔄 **Management Endpoints**
- `GET /api/refresh` - Manually refresh French transit data
- `GET /docs` - API documentation (Swagger UI)
- `GET /redoc` - Alternative API documentation

## 🎨 Enhanced Lighter Styling

### 🌟 **Design Features**
- **Brightest Background**: Maximum contrast for French transit visibility
- **Official French Colors**: Authentic RATP Metro, RER, and bus branding
- **Elegance Color Coding**: Green (Excellent) → Red (Poor)
- **French Identity**: 🇫🇷 flag integration and artistic design principles
- **Mobile Optimized**: Responsive design for all devices

### 🚇 **French Transit Colors**
- **Metro Lines**: Yellow (1), Purple (4), Light Green (6), Pink (7), Light Purple (8), Olive (9), Brown (11), Dark Purple (14)
- **RER Lines**: Red (A), Blue (B), Orange (C), Green (D)
- **Bus Routes**: Red (#E2231A) - Standard RATP bus color
- **Elegance**: Green (Excellent), Yellow (Good), Orange (Fair), Red (Poor)

## 🚀 Use Cases

### 🏢 **Daily Commuting**
- **Elegance Planning**: Choose most sophisticated routes during peak times
- **Multi-modal Integration**: Combine Metro, RER, and bus seamlessly
- **Delay Avoidance**: Real-time alerts for service disruptions

### 🧳 **Tourism & Visitors**
- **System Understanding**: Learn French transit operations and elegance
- **Journey Planning**: Navigate Paris's artistic network
- **Cultural Experience**: Experience renowned French style and sophistication

### 📊 **Urban Planning**
- **Elegance Analysis**: Monitor system-wide transit sophistication
- **French Standards**: Benchmark against world-class artistic design
- **Service Quality**: Study French transport excellence

## 🇫🇷 **Paris Context**

### 🌟 **Why Paris Matters**
- **French Elegance**: World-renowned style and sophistication
- **Artistic Heritage**: Metro stations as underground art galleries
- **Cultural Significance**: Transit system reflecting Parisian lifestyle
- **Global Inspiration**: Model for elegant urban transport worldwide

### 🚇 **French Transit Significance**
- **Metro Network**: Artistic underground system with French flair
- **RER Integration**: Regional connections with suburban elegance
- **Design Excellence**: Beautiful, stylish, and well-maintained system
- **Cultural Leadership**: Pioneer in artistic urban transport solutions

## 🔧 Development

### 📚 **Setup Documentation**
- **[Poetry Setup Guide](../docs/poetry-setup.md)** - Complete installation and usage
- **[Docker Setup Guide](../docs/docker-setup.md)** - Optimization and WSL2 integration
- **[WSL2 Setup Guide](../docs/wsl2-setup.md)** - Windows development environment

### 🧪 **Testing**
```bash
# Test the French transit data processor
poetry run python transit_worker.py

# Test the web application
poetry run python app.py

# Test Docker build
docker build -t paris-metro-now .

# Test Docker run
docker run -p 8000:8000 paris-metro-now
```

## 🌍 Global Impact

### 🎯 **Strategic Value**
- **French Representation**: Showcases European transport elegance
- **Artistic Benchmark**: Demonstrates world-class style standards
- **Cultural Focus**: Highlights French sophistication and design
- **European Integration**: Template for other French and European cities

### 🚀 **Expansion Opportunities**
- **Regional Integration**: Add Île-de-France suburban connections
- **Cultural Context**: Include Paris art and cultural transit history
- **Sustainability Metrics**: Environmental impact tracking
- **Multi-language**: French-English bilingual interface

## 🤝 Contributing

Want to enhance Paris Metro Now? Here are some ideas:

- **🚲 Vélib' Integration**: Add Paris bike-share and cycling data
- **🎨 Cultural Context**: Include Metro art and architectural features
- **📱 Mobile App**: Create native iOS/Android application
- **🇫🇷 French Language**: Add French language support
- **♿ Accessibility**: Enhanced features for mobility-impaired users

## 📝 License

MIT License - see the LICENSE file for details.

---

**🚇 Experience the power of real-time French elegance and sophistication with PyMapGIS!** 🇫🇷
