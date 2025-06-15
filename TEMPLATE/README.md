# 🎯 PyMapGIS Showcase Demo Template

**Welcome new contributor!** 🌟 This template helps you create a new PyMapGIS showcase demo.

## 📋 **Template Structure**

```
your-demo-name/
├── README.md              # Demo documentation
├── app.py                 # Main application
├── requirements.txt       # Python dependencies
├── Dockerfile            # Container deployment
├── test_demo.py          # Demo tests
├── static/               # Static assets (CSS, JS, images)
│   ├── style.css
│   └── script.js
└── data/                 # Sample data files
    └── sample.geojson
```

## 🚀 **Quick Start**

### **1. Copy Template**
```bash
cp -r TEMPLATE/ showcases/your-demo-name/
cd showcases/your-demo-name/
```

### **2. Customize Demo**
1. Update `README.md` with your demo description
2. Implement your logic in `app.py`
3. Add required dependencies to `requirements.txt`
4. Create tests in `test_demo.py`

### **3. Test Locally**
```bash
# Install dependencies
poetry install

# Run demo
poetry run python app.py

# Run tests
poetry run pytest test_demo.py
```

### **4. Deploy with Docker**
```bash
docker build -t pymapgis-your-demo .
docker run -p 8000:8000 pymapgis-your-demo
```

## 🎯 **Demo Requirements**

### **✅ Must Have**
- [ ] **Clear purpose** - Solves a real-world geospatial problem
- [ ] **PyMapGIS integration** - Uses PyMapGIS as primary library
- [ ] **Interactive visualization** - Maps, charts, or dashboards
- [ ] **Sample data** - Works without external API keys
- [ ] **Documentation** - Clear README with setup instructions
- [ ] **Tests** - Basic functionality tests
- [ ] **Docker support** - Containerized deployment

### **🌟 Nice to Have**
- [ ] **Real-time data** - Live data feeds or updates
- [ ] **Multiple data sources** - Combines different datasets
- [ ] **Advanced visualizations** - 3D maps, animations, etc.
- [ ] **User interaction** - Filters, controls, customization
- [ ] **Performance optimization** - Fast loading and processing
- [ ] **Mobile responsive** - Works on all devices

## 📊 **Demo Categories**

Choose a category that fits your demo:

### **🌍 Environmental & Climate**
- Climate change visualization
- Natural disaster impact assessment
- Environmental monitoring
- Biodiversity mapping

### **🏙️ Urban Planning & Smart Cities**
- Transportation analysis
- Urban growth modeling
- Infrastructure planning
- Public service optimization

### **📈 Economic & Business**
- Market analysis
- Supply chain optimization
- Real estate trends
- Economic indicators

### **👥 Social & Demographics**
- Population analysis
- Social equity mapping
- Health outcomes
- Education access

### **🚛 Logistics & Transportation**
- Route optimization
- Fleet management
- Traffic analysis
- Delivery planning

## 🛠️ **Technical Guidelines**

### **Python Code Style**
```python
import pymapgis as pmg
import streamlit as st
import plotly.express as px

def main():
    """Main demo application."""
    st.title("🎯 Your Demo Title")
    
    # Load data using PyMapGIS
    data = pmg.read("your-data-source")
    
    # Create visualization
    fig = data.plot.choropleth(
        column="your_column",
        title="Your Visualization Title"
    )
    
    # Display in Streamlit
    st.plotly_chart(fig)

if __name__ == "__main__":
    main()
```

### **FastAPI Alternative**
```python
from fastapi import FastAPI
import pymapgis as pmg

app = FastAPI(title="Your Demo API")

@app.get("/")
async def root():
    """Demo homepage."""
    return {"message": "Welcome to Your Demo"}

@app.get("/data")
async def get_data():
    """Get processed geospatial data."""
    data = pmg.read("your-data-source")
    return data.to_dict()
```

### **Testing Template**
```python
import pytest
import pymapgis as pmg
from app import main

def test_demo_loads():
    """Test that demo loads without errors."""
    # Your test logic here
    assert True

def test_data_processing():
    """Test data processing functions."""
    # Your test logic here
    assert True

def test_visualization():
    """Test visualization generation."""
    # Your test logic here
    assert True
```

## 📚 **Resources**

### **PyMapGIS Documentation**
- [🚀 Quick Start](../docs/quickstart.md)
- [🔧 API Reference](../docs/api-reference.md)
- [💡 Examples](../docs/examples.md)

### **Visualization Libraries**
- **[Streamlit](https://streamlit.io/)** - Quick web apps
- **[FastAPI](https://fastapi.tiangolo.com/)** - High-performance APIs
- **[Plotly](https://plotly.com/python/)** - Interactive charts
- **[MapLibre GL JS](https://maplibre.org/)** - Web maps
- **[Leafmap](https://leafmap.org/)** - Geospatial visualization

### **Data Sources**
- **Census ACS:** `pmg.read("census://acs/acs5?year=2022")`
- **TIGER/Line:** `pmg.read("tiger://county?year=2022")`
- **Local files:** `pmg.read("file://data/your-file.geojson")`
- **Cloud storage:** `pmg.read("s3://bucket/data.parquet")`

## 🤝 **Getting Help**

### **Stuck? We're here to help!**
- 💬 **[GitHub Discussions](https://github.com/pymapgis/core/discussions)** - Ask questions
- 📧 **[Email Support](mailto:support@pymapgis.org)** - Direct assistance
- 🎯 **[Showcase Issues](https://github.com/pymapgis/core/labels/showcase)** - Demo-specific help

### **Mentorship Available**
Look for issues with the `mentor-available` label - experienced contributors will help guide you through the development process.

## 🏆 **Recognition**

Your showcase demo will be:
- 🌟 **Featured** on the PyMapGIS homepage
- 📝 **Highlighted** in release notes
- 🎯 **Used** by potential PyMapGIS adopters
- 🤝 **Credited** to you as the creator

---

**🚀 Ready to build something amazing? Copy this template and start creating!**
