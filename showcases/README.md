# 🎯 PyMapGIS Showcase Demos

**Welcome to the PyMapGIS Showcase!** 🌟

This directory contains **live, interactive demos** that demonstrate the power and versatility of PyMapGIS. Each showcase is a complete, deployable application that solves real-world geospatial problems.

## 🚀 **Live Demos**

### 🌍 **Quake Impact Now** - Real-time Earthquake Assessment
**📁 Directory:** `quake-impact/`  
**🔗 Live Demo:** [pymapgis-quake.herokuapp.com](https://pymapgis-quake.herokuapp.com)  
**📊 Description:** Real-time earthquake impact assessment using USGS earthquake data and WorldPop population rasters. Built with FastAPI, MapLibre GL JS, and Streamlit.

**Key Features:**
- 🔴 Real-time USGS earthquake data
- 👥 Population impact analysis with WorldPop data
- 🗺️ Interactive MapLibre GL JS visualization
- ⚡ 50-line microservice architecture
- 🐳 Docker deployment ready

### 📦 **Border Flow Analytics** - Cross-Border Trade Visualization
**📁 Directory:** `border-flow/`  
**🔗 Live Demo:** [pymapgis-border.herokuapp.com](https://pymapgis-border.herokuapp.com)  
**📊 Description:** Interactive visualization of cross-border trade flows and economic relationships.

**Key Features:**
- 🌐 International trade flow analysis
- 📈 Economic indicator visualization
- 🎯 Interactive filtering and exploration
- 📊 Real-time data processing

### 🏠 **Housing Cost Burden** - Affordability Analysis
**📁 Directory:** `housing-cost-burden/`  
**🔗 Live Demo:** [pymapgis-housing.herokuapp.com](https://pymapgis-housing.herokuapp.com)  
**📊 Description:** Interactive analysis of housing affordability using Census ACS data.

**Key Features:**
- 🏘️ Census ACS housing data integration
- 💰 Cost burden analysis (30%+ income on housing)
- 🗺️ County-level choropleth visualization
- 📊 Interactive data exploration

### 🚛 **Supply Chain Dashboard** - Logistics Optimization
**📁 Directory:** `supply-chain/`  
**🔗 Live Demo:** [pymapgis-logistics.herokuapp.com](https://pymapgis-logistics.herokuapp.com)  
**📊 Description:** Enterprise-grade supply chain optimization and monitoring dashboard.

**Key Features:**
- 🏭 Warehouse optimization analysis
- 🚚 Last-mile delivery routing
- 📊 Real-time logistics monitoring
- ⚡ High-performance processing

## 🤝 **Contributor Funnel**

### 🎮 **Step 1: Try the Demos**
Start by exploring our live demos to see PyMapGIS in action:
1. Click any demo link above
2. Interact with the visualizations
3. Explore the features and capabilities

### 🐛 **Step 2: Report Issues**
Found something that could be improved? We want to hear about it!
- **Quake Impact:** [Report Issue](https://github.com/pymapgis/core/issues/new?labels=quake-impact,good-first-issue)
- **Border Flow:** [Report Issue](https://github.com/pymapgis/core/issues/new?labels=border-flow,good-first-issue)
- **Housing:** [Report Issue](https://github.com/pymapgis/core/issues/new?labels=housing,good-first-issue)
- **Supply Chain:** [Report Issue](https://github.com/pymapgis/core/issues/new?labels=logistics,good-first-issue)

### 💡 **Step 3: Suggest Features**
Have ideas for new features or improvements?
- [💡 Feature Request](https://github.com/pymapgis/core/issues/new?labels=enhancement,showcase)

### 🔧 **Step 4: Contribute Code**
Ready to contribute? Here's how:

#### **🌟 Good First Issues**
Perfect for new contributors:
- [📝 Documentation improvements](https://github.com/pymapgis/core/labels/documentation)
- [🐛 Bug fixes](https://github.com/pymapgis/core/labels/good-first-issue)
- [✨ UI/UX enhancements](https://github.com/pymapgis/core/labels/ui-ux)

#### **🚀 Stretch Goals**
For experienced contributors:
- [⚡ Performance optimizations](https://github.com/pymapgis/core/labels/performance)
- [🌐 New data source integrations](https://github.com/pymapgis/core/labels/data-sources)
- [🔧 Advanced features](https://github.com/pymapgis/core/labels/stretch)

## 🛠️ **Development Setup**

### **Quick Start**
```bash
# Clone the repository
git clone https://github.com/pymapgis/core.git
cd core

# Install dependencies
poetry install --with dev,test

# Run a showcase demo locally
cd showcases/quake-impact
poetry run python app.py
```

### **Docker Development**
```bash
# Build and run any showcase
cd showcases/quake-impact
docker build -t pymapgis-quake .
docker run -p 8000:8000 pymapgis-quake
```

### **Testing**
```bash
# Run showcase tests
cd showcases/quake-impact
poetry run pytest test_demo.py

# Run all tests
poetry run pytest
```

## 📚 **Documentation**

- **[🚀 Quick Start Guide](../docs/quickstart.md)** - Get started with PyMapGIS
- **[🤝 Contributing Guide](../CONTRIBUTING.md)** - How to contribute
- **[🔧 API Reference](../docs/api-reference.md)** - Technical documentation
- **[💡 Examples Gallery](../docs/examples.md)** - More usage examples

## 🏆 **Recognition**

Contributors to our showcase demos get special recognition:
- 🌟 **Showcase Contributor** badge
- 📝 **Featured in release notes**
- 🎯 **Direct impact** on PyMapGIS adoption
- 🤝 **Community leadership** opportunities

## 🙏 **Get Help**

Need help getting started?
- 💬 **[GitHub Discussions](https://github.com/pymapgis/core/discussions)** - Ask questions
- 📧 **[Email Support](mailto:support@pymapgis.org)** - Direct assistance
- 📖 **[Documentation](../docs/)** - Comprehensive guides

---

**🚀 Ready to showcase the power of PyMapGIS? Pick a demo and start contributing!**
