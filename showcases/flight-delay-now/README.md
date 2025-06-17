# ✈️ Flight Delay Now

**A 35-line microservice that turns the public FAA OIS delay feed into a live map of airport congestion across major US hubs**

![Flight Delay Now](https://img.shields.io/badge/PyMapGIS-Showcase-blue) ![Status](https://img.shields.io/badge/Status-Active-green) ![License](https://img.shields.io/badge/License-MIT-yellow)

## 🎯 Why This Showcase?

- **100% Open Data**: Only FAA OIS current delay feed - no API keys required
- **Supply Chain Relevance**: Air-cargo and belly-cargo planners need real-time hub congestion data
- **PyMapGIS Power**: Demonstrates geospatial data processing and visualization in minimal code:
  - Single-line multi-format ingest (`pmg.read`)
  - Async HTTP processing for missing airports
  - Real-time web mapping with vector tiles

## 📊 Data Sources (100% Open)

| Feed | Format & URL | Notes |
|------|-------------|-------|
| FAA OIS Current Delays | JSON API – https://www.fly.faa.gov/ois/OIS_current.json | Real-time departure delays |
| Top 35 US Airports | GeoJSON – bundled in repo | Major hub locations with IATA codes |

*All data is public domain from Federal Aviation Administration*

## 🚀 Quick Start

### Option 1: Docker Hub (Recommended - One Command!)

```bash
# Pull and run the pre-built image
docker run -p 8000:8000 nicholaskarlson/flight-delay-now:latest

# Open browser to http://localhost:8000
```

### Option 2: Build from Source

```bash
# Clone and build locally
git clone https://github.com/pymapgis/core.git
cd core/showcases/flight-delay-now
docker build -t flight-delay-now .
docker run -p 8000:8000 flight-delay-now
```

### Option 3: Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run data processing
python flight_worker.py

# Start web server
python app.py

# Open browser to http://localhost:8000
```

### Option 4: Poetry (PyMapGIS Development - Recommended)

```bash
# From the PyMapGIS core directory
# Method A: Using poetry run (recommended)
poetry run python showcases/flight-delay-now/flight_worker.py
poetry run python showcases/flight-delay-now/app.py

# Method B: Using Poetry environment
source $(poetry env info --path)/bin/activate
cd showcases/flight-delay-now
python flight_worker.py
python app.py

# Open browser to http://localhost:8000
```

## 🔧 What the Service Does

Every time you run it, the lightweight worker:

1. **Pulls latest FAA OIS delay JSON** (≤ 2 s)
2. **Joins delay data to airport locations** using IATA codes
3. **Computes DelayScore** = log₁₊(avg_delay) × flights_affected
4. **Exports three artifacts**:
   - `flight_impact.geojson` – full attribute table
   - `flight_impact.png` – static overview visualization
   - JSON data via FastAPI endpoints

## 🌐 API Endpoints

| Endpoint | Access | Description |
|----------|--------|-------------|
| `GET /` | Public | Interactive map interface |
| `GET /public/latest` | Public | Latest flight delay data (JSON) |
| `GET /internal/latest` | Protected | Full analyst data with metadata |
| `GET /health` | Public | Service health check |
| `GET /api/docs` | Public | API documentation |

## 💡 Why PyMapGIS is Optimal

| Need | PyMapGIS Solution | Competing Stack Pain |
|------|------------------|---------------------|
| Read JSON and GeoJSON | `pmg.read("https://www.fly.faa.gov/ois/...")`, `pmg.read("airports.geojson")` | Vanilla Python: requests + pandas + geopandas setup |
| Fast spatial joins | Built-in merge operations on GeoDataFrames | Manual coordinate matching and CRS handling |
| Instant web-map tiles | Built-in FastAPI integration with vector export | Would need Tippecanoe or custom tile server |
| Secure vs. public routes | Built-in JWT helper + FastAPI examples | Flask/Django require extra auth middleware |
| Container distribution | Base on `pymapgis/core:latest` ⇒ 1-step docker build | Build GDAL + geospatial stack manually |

## 🎨 Features

### Interactive Web Map
- **Dark theme** with modern styling
- **MapLibre GL JS** for smooth continental US mapping
- **Real-time data** with 5-minute auto-refresh
- **Delay visualization** with color-coded wait times
- **Interactive popups** showing airport details and delay metrics

### Processing Pipeline
- **Async processing** for optimal performance
- **Robust error handling** with fallback to mock data
- **Flexible data merging** supporting multiple FAA formats
- **Progress tracking** with detailed logging

### Production Ready
- **Docker containerization** for easy deployment
- **Health checks** for monitoring
- **API documentation** with FastAPI
- **Security hardening** with non-root user

## 📁 File Structure

```
showcases/flight-delay-now/
├── flight_worker.py     # Core processing script (~35 lines)
├── app.py              # FastAPI web application (~15 lines)
├── Dockerfile          # Container configuration
├── requirements.txt    # Python dependencies
├── data/
│   └── top_airports.geojson   # Top 35 US airport locations
├── static/
│   └── index.html     # Interactive map interface
├── README.md          # This file
├── flight_impact.geojson  # Generated flight data
├── flight_latest.json     # API data cache
└── flight_impact.png      # Generated visualization
```

## 🔄 Development Workflow

1. **Process Data**: `python flight_worker.py`
2. **Start Server**: `python app.py`
3. **View Results**: Open http://localhost:8000
4. **Iterate**: Modify code and refresh

## 🌟 Next Steps

- **Add historical analysis** - track delay trends over time
- **Implement alerts** - notify when delays exceed thresholds
- **Expand coverage** - include international airports
- **Add predictive modeling** - forecast delays based on weather/traffic
- **Deploy to cloud** on Railway, Render, or Fly.io—it's a single container

## 🔒 Security Features

This Docker image has been built with security best practices:

### Container Security
- **Non-root user**: Runs as `flightdelay` user (not root)
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

- **Processing Time**: < 4 seconds for all airports
- **Memory Usage**: < 170MB peak
- **API Response**: < 50ms for most endpoints
- **Container Size**: ~300MB (optimized for security and performance)
- **Startup Time**: < 5 seconds from container start to ready

## 🤝 Contributing

This showcase is part of the PyMapGIS project. See the main [CONTRIBUTING.md](../../CONTRIBUTING.md) for guidelines.

## 📄 License

MIT License - see [LICENSE](../../LICENSE) for details.

---

**TL;DR**: PyMapGIS turns FAA OIS delay JSON + airport locations into a live, interactive "flight delay" map in 35 lines and one Docker run. Perfect for logistics optimization, air cargo planning, and real-time airport monitoring.
