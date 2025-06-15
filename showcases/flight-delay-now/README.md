# ✈️ Flight Delay Now

**Live departure delay monitoring at the 35 busiest U.S. airports**

A real-time flight delay visualization showcasing PyMapGIS capabilities for logistics and supply chain applications. Perfect for air-cargo planners, logistics teams, and anyone needing to track airport congestion.

## 🎯 **What You'll See**

- **Dark MapLibre map** with colored circles over major airport hubs
- **Green circles** → On-time departures (<15 min delay)
- **Yellow circles** → Moderate delays (15-30 min)
- **Red circles** → Severe delays (>30 min)
- **Hover tooltips** showing "ATL • Avg dep delay 42 min (16 flights)"
- **Auto-refresh** every 2 minutes with live FAA data

## 🚛 **Supply Chain Relevance**

- **Air-cargo planners** can identify which hubs are stacking departures
- **Logistics teams** can pre-route high-value or time-critical loads
- **Supply chain managers** get real-time visibility into air freight delays
- **Operations analysts** can access detailed delay data via JWT-protected API

## 📊 **Data Sources (100% Public & Key-Free)**

1. **FAA OIS Current Delay Feed** - ~60 kB JSON, refreshes every 1-2 minutes
   - URL: `https://www.fly.faa.gov/ois/OIS_current.json`
   
2. **Individual Airport Status API** - Fallback for missing airports
   - URL: `https://services.faa.gov/airport/status/{IATA}?format=JSON`
   
3. **Top 35 Airports GeoJSON** - Hand-curated with lat/lon, IATA codes, names, runway counts

## ⚡ **PyMapGIS Magic**

- **`pmg.read()`** pulls FAA JSON and static GeoJSON in one line each
- **Async HTTP loops** fetch missing airports with `aiohttp`
- **`vector.weighted_score()`** builds DelayScore = log₁₊(avg_delay) × √(flights_affected)
- **Real-time processing** with FastAPI background tasks
- **Vector tiles** for smooth web map performance

## 🚀 **Quick Start**

### **Option 1: Docker (Recommended)**
```bash
# Clone and run
git clone https://github.com/pymapgis/core.git
cd core/showcases/flight-delay-now

# Build and run
docker build -t flight-delay-now .
docker run -p 8000:8000 flight-delay-now

# Open browser to http://localhost:8000
```

### **Option 2: Windows PowerShell**
```powershell
# Auto-build and open browser
.\entry.ps1
```

### **Option 3: Local Development**
```bash
# Install dependencies
pip install -r requirements.txt

# Run data worker
python flight_worker.py

# Start web server
uvicorn app:app --host 0.0.0.0 --port 8000
```

## 🏗️ **Architecture**

```
flight-delay-now/
├── flight_worker.py     # 35 LOC: fetch → join → score → export
├── app.py              # 15 LOC: FastAPI routes + MapLibre viewer  
├── Dockerfile          # Compact container ≤ 170 MB
├── entry.ps1           # Windows auto-launcher
├── requirements.txt    # Python dependencies
├── data/
│   └── top_airports.geojson  # 35 major airports with IATA codes
└── README.md
```

## 🔧 **API Endpoints**

### **Public Access (Anonymous)**
- `GET /` - Interactive web viewer
- `GET /public/tiles/{z}/{x}/{y}.pbf` - Vector tiles for map
- `GET /health` - Health check and status
- `GET /refresh` - Manual data refresh trigger

### **Internal Access (JWT Protected)**
- `GET /internal/latest` - Full GeoJSON with detailed delay data
  - Includes cancelled flights, ground holds, and operational details
  - Requires `Authorization: Bearer demo-token` header

## 📈 **Performance**

- **Processing time:** <4 seconds on laptop
- **Container size:** ≤170 MB
- **Memory usage:** ~50 MB runtime
- **Data refresh:** Every 2 minutes automatically
- **Response time:** <200ms for map tiles

## 🤝 **Contributing**

This showcase is perfect for new PyMapGIS contributors! Here are some ways to help:

### **🌟 Good First Issues**
- [ ] Add more airports (expand beyond top 35)
- [ ] Improve error handling for API failures
- [ ] Add historical delay trends
- [ ] Enhance mobile responsiveness
- [ ] Add airport weather integration

### **🚀 Advanced Features**
- [ ] Real-time WebSocket updates
- [ ] Predictive delay modeling
- [ ] Integration with flight tracking APIs
- [ ] Custom alert thresholds
- [ ] Export delay reports

### **🐛 Bug Reports**
Found an issue? [Report it here](https://github.com/pymapgis/core/issues/new?labels=flight-delay,good-first-issue)

## 🧪 **Testing**

```bash
# Run tests
pytest test_flight_delay.py

# Test with sample data
python flight_worker.py --test-mode

# Check API endpoints
curl http://localhost:8000/health
curl http://localhost:8000/public/tiles/0/0/0.pbf
```

## 🌟 **Why This Demo Matters**

1. **Real-world logistics problem** - Flight delays cost billions annually
2. **Live data integration** - Shows PyMapGIS handling real-time APIs
3. **Supply chain relevance** - Directly applicable to air cargo operations
4. **Beginner-friendly** - Simple architecture, clear code structure
5. **Scalable pattern** - Template for other real-time monitoring apps

## 📚 **Learn More**

- **[PyMapGIS Documentation](../../docs/quickstart.md)** - Get started with PyMapGIS
- **[FAA System Operations Center](https://www.fly.faa.gov/)** - Data source information
- **[MapLibre GL JS](https://maplibre.org/)** - Web mapping library used
- **[FastAPI](https://fastapi.tiangolo.com/)** - Web framework documentation

## 🏆 **Recognition**

Contributors to Flight Delay Now get:
- 🌟 **Showcase Contributor** badge
- 📝 **Featured in PyMapGIS release notes**
- 🎯 **Direct impact** on logistics community
- 🤝 **Mentorship** from PyMapGIS team

---

**🛫 Ready to track flight delays in real-time? Start the demo and explore the code!**

*Built with PyMapGIS • Powered by FAA data • Designed for logistics professionals*
