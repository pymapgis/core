# 🕳️ Open311 Pothole Now - SF

![Pothole Status](https://img.shields.io/badge/PyMapGIS-Local%20Showcase-blue) ![Status](https://img.shields.io/badge/Status-Active-green) ![License](https://img.shields.io/badge/License-MIT-yellow) ![SF](https://img.shields.io/badge/City-San%20Francisco-orange)

## 📺 **Demo Video**

🎬 **Watch Open311 Pothole Now in Action**: https://youtu.be/RK-uVn7FwOo

See the enhanced lighter map styling, real-time SF Open311 civic issue tracking, priority-based visualization, and interactive civic engagement features in this comprehensive demo video.

## 🎯 Why This Showcase?

Open311 Pothole Now demonstrates real-time civic issue tracking using San Francisco's Open311 API. This showcase provides instant visibility into street defects, sidewalk issues, and infrastructure problems across the city.

**Perfect for:**
- 🏛️ **Civic Engagement**: Track municipal service requests and responses
- 🚶 **Pedestrian Safety**: Identify sidewalk and street hazards
- 🎯 **Infrastructure Monitoring**: Monitor city maintenance priorities
- 📊 **Government Transparency**: Analyze municipal response times

## ⚡ Quick Start

### 🐳 Option 1: Docker (Recommended)
```bash
# Run the Open311 Pothole Now showcase
docker run -p 8000:8000 nicholaskarlson/open311-pothole-now:latest

# Access the application
open http://localhost:8000
```

### 🔧 Option 2: Local Development
```bash
# Clone the repository
git clone https://github.com/pymapgis/core.git
cd core/showcaseslocal/open311-pothole-now

# Install dependencies with Poetry
poetry install

# Run the Open311 data processor
poetry run python pothole_worker.py

# Start the web application
poetry run python app.py

# View at: http://localhost:8000
```

## 🌟 Features

### 🕳️ **Real-time Civic Issue Tracking**
- **Live SF Open311 API Integration**: Direct connection to city systems
- **All Issue Types**: Potholes, sidewalk defects, street damage, safety hazards
- **Priority Analysis**: High/Medium/Low priority classification
- **Age Tracking**: Fresh → Very Old progression analysis

### 🎨 **Enhanced Lighter Styling**
- **Brightest Background**: Perfect contrast for civic issue visibility
- **Priority Color Coding**: Red (High) → Green (Resolved)
- **Interactive Issue Map**: Click any issue for detailed information
- **Civic-Friendly Design**: Clear, accessible interface for public use

### 📊 **Smart Civic Intelligence**
- **Issue Scoring**: Priority-based classification system
- **Response Tracking**: Municipal response time analysis
- **Neighborhood Analysis**: Geographic distribution of issues
- **Transparency Tools**: Open government data visualization

## 🗺️ Data Sources

### 🏛️ **San Francisco Open311 API**
- **Street/Sidewalk Defects**: Real-time infrastructure issues
- **Service Requests**: Citizen-reported problems
- **Response Tracking**: Municipal action and resolution
- **Update Frequency**: Every 15 minutes for fresh civic data

## 🚀 Use Cases

### 🏛️ **Civic Engagement**
- **Issue Reporting**: Track citizen service requests
- **Government Accountability**: Monitor municipal response times
- **Community Awareness**: Understand neighborhood infrastructure needs

### 🚶 **Public Safety**
- **Hazard Identification**: Locate street and sidewalk dangers
- **Route Planning**: Avoid areas with infrastructure problems
- **Safety Awareness**: Stay informed about local hazards

### 📊 **Urban Planning**
- **Infrastructure Assessment**: Analyze city maintenance needs
- **Resource Allocation**: Understand priority areas for investment
- **Performance Monitoring**: Track municipal service quality

## 🔧 Development

### 📚 **Setup Documentation**
- **[Poetry Setup Guide](../docs/poetry-setup.md)** - Complete installation and usage
- **[Docker Setup Guide](../docs/docker-setup.md)** - Optimization and WSL2 integration
- **[WSL2 Setup Guide](../docs/wsl2-setup.md)** - Windows development environment

## 🤝 Contributing

Want to enhance Open311 Pothole Now? Here are some ideas:

- **🌍 Multi-City**: Expand to other cities with Open311 APIs
- **📱 Mobile App**: Create native mobile reporting application
- **🔔 Notifications**: Alert users to nearby infrastructure issues
- **📊 Analytics**: Advanced trend analysis and prediction
- **♿ Accessibility**: Include accessibility-related issue tracking

## 📝 License

MIT License - see the LICENSE file for details.

---

**🕳️ Experience the power of real-time civic infrastructure intelligence with PyMapGIS!**
