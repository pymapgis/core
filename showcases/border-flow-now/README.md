# 🚛 Border Flow Now

**A 40-line microservice that turns the public CBP border-wait JSON feed into a live map of cross-border truck congestion**

![Border Flow Now](https://img.shields.io/badge/PyMapGIS-Showcase-blue) ![Status](https://img.shields.io/badge/Status-Active-green) ![License](https://img.shields.io/badge/License-MIT-yellow)

## 🎯 Why This Showcase?

- **100% Open Data**: Only CBP Border Wait Times API - no API keys required
- **Supply Chain Relevance**: 70% of U.S.–Mexico trade travels by truck; real-time delays impact logistics
- **PyMapGIS Power**: Demonstrates geospatial data processing and visualization in minimal code:
  - Single-line multi-format ingest (`pmg.read`)
  - Spatial joins and analysis
  - Real-time web mapping with vector tiles

## 📊 Data Sources (100% Open)

| Feed | Format & URL | Notes |
|------|-------------|-------|
| CBP Border Wait Times | JSON API – https://bwt.cbp.gov/api/bwt | Real-time wait times |
| Land Port Locations | GeoJSON – bundled in repo | 30 major border crossings |

*All data is public domain from U.S. Customs and Border Protection*

## 🚀 Quick Start

### Option 1: Docker Hub (Recommended - One Command!)

```bash
# Pull and run the pre-built image
docker run -p 8000:8000 nicholaskarlson/border-flow-now:latest

# Open browser to http://localhost:8000
```

### Option 2: Build from Source

```bash
# Clone and build locally
git clone https://github.com/pymapgis/core.git
cd core/showcases/border-flow-now
docker build -t border-flow-now .
docker run -p 8000:8000 border-flow-now
```

### Option 3: Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run data processing
python border_worker.py

# Start web server
python app.py

# Open browser to http://localhost:8000
```

### Option 4: Poetry (PyMapGIS Development - Recommended)

```bash
# From the PyMapGIS core directory
# Method A: Using poetry run (recommended)
poetry run python showcases/border-flow-now/border_worker.py
poetry run python showcases/border-flow-now/app.py

# Method B: Using Poetry environment
source $(poetry env info --path)/bin/activate
cd showcases/border-flow-now
python border_worker.py
python app.py

# Open browser to http://localhost:8000
```

## 🔧 What the Service Does

Every time you run it, the lightweight worker:

1. **Pulls latest CBP Border Wait Times JSON** (≤ 2 s)
2. **Joins wait times to port locations** using port codes/names
3. **Computes CongestionScore** = log₁₊(wait_minutes) × commercial_lanes
4. **Exports three artifacts**:
   - `border_impact.geojson` – full attribute table
   - `border_impact.png` – static overview visualization
   - JSON data via FastAPI endpoints

## 🌐 API Endpoints

| Endpoint | Access | Description |
|----------|--------|-------------|
| `GET /` | Public | Interactive map interface |
| `GET /public/latest` | Public | Latest border wait data (JSON) |
| `GET /internal/latest` | Protected | Full analyst data with metadata |
| `GET /health` | Public | Service health check |
| `GET /api/docs` | Public | API documentation |

## 💡 Why PyMapGIS is Optimal

| Need | PyMapGIS Solution | Competing Stack Pain |
|------|------------------|---------------------|
| Read JSON and GeoJSON | `pmg.read("https://bwt.cbp.gov/...")`, `pmg.read("ports.geojson")` | Vanilla Python: requests + pandas + geopandas setup |
| Fast spatial joins | Built-in merge operations on GeoDataFrames | Manual coordinate matching and CRS handling |
| Instant web-map tiles | Built-in FastAPI integration with vector export | Would need Tippecanoe or custom tile server |
| Secure vs. public routes | Built-in JWT helper + FastAPI examples | Flask/Django require extra auth middleware |
| Container distribution | Base on `pymapgis/core:latest` ⇒ 1-step docker build | Build GDAL + geospatial stack manually |

## 🎨 Features

### Interactive Web Map
- **Dark theme** with modern styling
- **MapLibre GL JS** for smooth border region mapping
- **Real-time data** with 5-minute auto-refresh
- **Congestion visualization** with color-coded wait times
- **Interactive popups** showing port details and wait times

### Processing Pipeline
- **Async processing** for optimal performance
- **Robust error handling** with fallback to mock data
- **Flexible data merging** supporting multiple API formats
- **Progress tracking** with detailed logging

### Production Ready
- **Docker containerization** for easy deployment
- **Health checks** for monitoring
- **API documentation** with FastAPI
- **Security hardening** with non-root user

## 📁 File Structure

```
showcases/border-flow-now/
├── border_worker.py     # Core processing script (~40 lines)
├── app.py              # FastAPI web application (~15 lines)
├── Dockerfile          # Container configuration
├── requirements.txt    # Python dependencies
├── data/
│   └── ports.geojson   # Border port locations
├── static/
│   └── index.html     # Interactive map interface
├── README.md          # This file
├── border_impact.geojson  # Generated border data
├── border_latest.json     # API data cache
└── border_impact.png      # Generated visualization
```

## 🔄 Development Workflow

1. **Process Data**: `python border_worker.py`
2. **Start Server**: `python app.py`
3. **View Results**: Open http://localhost:8000
4. **Iterate**: Modify code and refresh

## 🌟 Next Steps

- **Add historical analysis** - track wait time trends over time
- **Implement alerts** - notify when wait times exceed thresholds
- **Expand coverage** - include Canadian border crossings
- **Add predictive modeling** - forecast wait times based on patterns
- **Deploy to cloud** on Railway, Render, or Fly.io—it's a single container

## 🔒 Security Features

This Docker image has been built with security best practices:

### Container Security
- **Non-root user**: Runs as `borderflow` user (not root)
- **Minimal base image**: Uses Python slim image to reduce attack surface
- **Updated packages**: All system packages upgraded to latest versions
- **No unnecessary tools**: Only essential packages installed
- **Proper file permissions**: Secure file ownership and permissions

### Network Security
- **Single port exposure**: Only port 8000 exposed
- **Health checks**: Built-in health monitoring
- **No privileged access**: Container runs without elevated privileges

### Application Security
- **Input validation**: All API inputs validated
- **Error handling**: Graceful error handling without information leakage
- **Dependency management**: Minimal, well-maintained dependencies
- **No secrets in image**: No hardcoded credentials or API keys

## 📈 Performance

- **Processing Time**: < 3 seconds for all border ports
- **Memory Usage**: < 200MB peak
- **API Response**: < 50ms for most endpoints
- **Container Size**: ~300MB (optimized for security and performance)
- **Startup Time**: < 5 seconds from container start to ready

## 🤝 Contributing

This showcase is part of the PyMapGIS project. See the main [CONTRIBUTING.md](../../CONTRIBUTING.md) for guidelines.

## 📄 License

MIT License - see [LICENSE](../../LICENSE) for details.

---

**TL;DR**: PyMapGIS turns CBP border wait time JSON + port locations into a live, interactive "border congestion" map in 40 lines and one Docker run. Perfect for supply chain analytics, logistics optimization, and real-time border monitoring.
