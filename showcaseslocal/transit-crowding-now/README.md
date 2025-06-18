# 🚇 Transit Crowding Now - NYC

![Transit Crowding](https://img.shields.io/badge/PyMapGIS-Local%20Showcase-blue) ![Status](https://img.shields.io/badge/Status-Active-green) ![License](https://img.shields.io/badge/License-MIT-yellow) ![NYC](https://img.shields.io/badge/City-NYC-blue)

## 📺 **Demo Video**

🎬 **Watch NYC Transit Crowding Now in Action**: https://youtu.be/bwT--KYjjiE

See the enhanced lighter map styling, real-time NYC subway crowding analysis, commuter recommendations, and interactive transit planning features in this comprehensive demo video.

## 🎯 Why This Showcase?

NYC Transit Crowding Now demonstrates real-time subway crowding analysis using MTA GTFS-RT data. This showcase provides instant visibility into subway line crowding, delays, and commuter recommendations for the world's largest subway system.

**Perfect for:**
- 🏢 **Commuters**: Choose less crowded subway lines for better journeys
- 🧳 **Tourists**: Navigate NYC subway system efficiently
- 🎯 **Transit Planning**: Avoid overcrowded routes during rush hour
- 📊 **Urban Analysis**: Monitor NYC's massive transit network performance

## ⚡ Quick Start

### 🐳 Option 1: Docker (Recommended)
```bash
# Run the NYC Transit Crowding Now showcase
docker run -p 8000:8000 nicholaskarlson/transit-crowding-now:latest

# Access the application
open http://localhost:8000
```

### 🔧 Option 2: Local Development
```bash
# Clone the repository
git clone https://github.com/pymapgis/core.git
cd core/showcaseslocal/transit-crowding-now

# Install dependencies with Poetry
poetry install

# Run the MTA data processor
poetry run python transit_worker.py

# Start the web application
poetry run python app.py

# View at: http://localhost:8000
```

## 🌟 Features

### 🚇 **Real-time Subway Crowding**
- **Live MTA GTFS-RT Integration**: Direct connection to MTA APIs
- **All Major Lines**: Complete coverage of NYC subway network
- **Crowding Analysis**: Real-time passenger density tracking
- **Commuter Recommendations**: Best/worst route suggestions

### 🎨 **Enhanced Lighter Styling**
- **Brightest Background**: Perfect contrast for subway line colors
- **NYC Subway Colors**: Authentic MTA line branding
- **Interactive Crowding Map**: Click any line for detailed crowding info
- **Commuter-Friendly Design**: Clear, accessible interface for daily use

### 📊 **Smart Commuter Intelligence**
- **Crowding Scores**: 0-10 scale for easy comparison
- **Route Recommendations**: Identify less crowded alternatives
- **Real-time Alerts**: Service disruptions and delays
- **Rush Hour Analysis**: Peak time crowding patterns

## 🗺️ Data Sources

### 🚇 **Metropolitan Transportation Authority (MTA)**
- **GTFS-Realtime**: Live subway positions and crowding data
- **Service Alerts**: Real-time disruptions and delays
- **High Reliability**: Production-grade transit data
- **Update Frequency**: Every 5 minutes during rush hours

## 🚀 Use Cases

### 🏢 **Daily Commuting**
- **Rush Hour Planning**: Avoid overcrowded lines during peak times
- **Route Optimization**: Find less crowded alternatives
- **Time Management**: Plan journeys based on current crowding

### 🧳 **Tourism & Visitors**
- **System Navigation**: Understand NYC subway operations
- **Crowd Avoidance**: Travel comfortably during busy periods
- **Journey Planning**: Efficient routes across Manhattan and boroughs

### 📊 **Urban Planning**
- **Capacity Analysis**: Monitor subway system utilization
- **Peak Hour Patterns**: Track crowding trends over time
- **Service Quality**: Benchmark MTA performance

## 🔧 Development

### 📚 **Setup Documentation**
- **[Poetry Setup Guide](../docs/poetry-setup.md)** - Complete installation and usage
- **[Docker Setup Guide](../docs/docker-setup.md)** - Optimization and WSL2 integration
- **[WSL2 Setup Guide](../docs/wsl2-setup.md)** - Windows development environment

## 🤝 Contributing

Want to enhance NYC Transit Crowding Now? Here are some ideas:

- **🚌 Bus Integration**: Add NYC bus crowding data
- **🚶 Walking Routes**: Alternative walking paths during crowding
- **📱 Mobile App**: Create native mobile application
- **🔔 Notifications**: Push alerts for favorite lines
- **♿ Accessibility**: Include elevator status and accessible routes

## 📝 License

MIT License - see the LICENSE file for details.

---

**🚇 Experience the power of real-time NYC subway crowding intelligence with PyMapGIS!**
