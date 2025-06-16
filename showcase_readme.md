# 🌍 Quake Impact Now

**A 50-line microservice that turns the public USGS earthquake feed + open population rasters into a live 'likely-felt' map**

![Quake Impact Now](https://img.shields.io/badge/PyMapGIS-Showcase-blue) ![Status](https://img.shields.io/badge/Status-Active-green) ![License](https://img.shields.io/badge/License-MIT-yellow)

## 🎯 Why This Showcase?

- **100% Open Data**: Only two public datasets – nothing to download manually, no API keys
- **Lightning Fast**: Runs in < 1 minute on a free GitHub Actions runner – perfect demo
- **PyMapGIS Power**: Shows off the 3 marquee PyMapGIS tricks in minimal code:
  - Single-line multi-format ingest (`pmg.read`)
  - Async raster zonal statistics
  - Instant vector-tile export for browser maps

## 📊 Data Sources (100% Open)

| Feed | Format & URL | Notes |
|------|-------------|-------|
| USGS "all_day" earthquakes | GeoJSON – https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_day.geojson | max ~20 kB |
| WorldPop 2020 population | Cloud-Optimised GeoTIFF on AWS Open Data – s3://worldpop-data/ | ~200 MB per continent COG |

*WorldPop is CC-BY-4.0; no key required. Streamed + windowed reads mean no full download.*

## 🚀 Quick Start

### Option 1: Docker (Recommended)

```bash
# Build and run
docker build -t quake-impact-now .
docker run -p 8000:8000 quake-impact-now

# Open browser to http://localhost:8000
```

### Option 2: Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run data processing
python quake_impact.py

# Start web server
python app.py

# Open browser to http://localhost:8000
```

### Option 3: Poetry (PyMapGIS Development)

```bash
# From the PyMapGIS core directory
cd showcases/quake-impact-now
poetry install
poetry run python quake_impact.py
poetry run python app.py
```

## 🔧 What the Service Does

Every time you run it, the lightweight worker:

1. **Pulls latest USGS GeoJSON** (≤ 1 s)
2. **Buffers each quake epicenter** to 50 km (negligible)
3. **Uses PyMapGIS async zonal stats** to sum population inside each buffer from WorldPop COG
4. **Computes ImpactScore** = log₁₀(pop_within_50km) × magnitude
5. **Exports three artifacts**:
   - `impact.geojson` – full attribute table
   - `impact.png` – static overview PNG
   - Vector tiles via FastAPI endpoints

## 🌐 API Endpoints

| Endpoint | Access | Description |
|----------|--------|-------------|
| `GET /` | Public | Interactive map interface |
| `GET /public/latest` | Public | Latest earthquake data (JSON) |
| `GET /public/tiles/{z}/{x}/{y}.pbf` | Public | Vector tiles for maps |
| `GET /internal/latest` | Protected | Full analyst data with metadata |
| `GET /health` | Public | Service health check |

## 💡 Why PyMapGIS is Optimal

| Need | PyMapGIS Solution | Competing Stack Pain |
|------|------------------|---------------------|
| Read GeoJSON and remote COG | `pmg.read("https://earthquake...")`, `pmg.read("s3://worldpop...")` | Vanilla Python: requests + rasterio + boto3 GDAL VFS gymnastics |
| Buffer & population sum fast | `AsyncGeoProcessor.zonal_stats()` on list of geometries | Pure rasterstats or GDAL slower; need threading boilerplate |
| Instant web-map tiles | Built-in FastAPI integration with MVT export | Would otherwise call Tippecanoe or tegola |
| Secure vs. public routes | Built-in JWT helper + FastAPI examples | Flask/Shiny require extra plugins/middleware |
| Container distribution | Base on `pymapgis/core:latest` ⇒ 1-step docker build | Build GDAL + rasterio yourself; bigger image; longer CI |

## 🎨 Features

### Interactive Web Map
- **Dark theme** with Tailwind CSS styling
- **MapLibre GL JS** for smooth, modern mapping
- **Real-time data** with refresh capability
- **Impact visualization** with color-coded severity
- **Interactive popups** showing earthquake details

### Processing Pipeline
- **Async processing** for optimal performance
- **Memory efficient** chunked operations
- **Error handling** with graceful degradation
- **Progress tracking** with detailed logging

### Production Ready
- **Docker containerization** for easy deployment
- **Health checks** for monitoring
- **API documentation** with FastAPI
- **Static file serving** for frontend assets

## 📁 File Structure

```
showcases/quake-impact-now/
├── quake_impact.py      # Core processing script (~50 lines)
├── app.py              # FastAPI web application (~15 lines)
├── Dockerfile          # Container configuration
├── requirements.txt    # Python dependencies
├── static/
│   └── index.html     # Interactive map interface
├── README.md          # This file
├── impact.geojson     # Generated earthquake data
└── impact.png         # Generated overview map
```

## 🔄 Development Workflow

1. **Process Data**: `python quake_impact.py`
2. **Start Server**: `python app.py`
3. **View Results**: Open http://localhost:8000
4. **Iterate**: Modify code and refresh

## 🌟 Next Steps

- **Change buffer radius** or add ShakeMap PGA rasters to refine impact
- **Swap WorldPop** with GPW v4 or LandScan—just edit one line in `POP_COG`
- **Deploy to cloud** on Railway, Render, or Fly.io—it's a single container
- **Fork and customize** for your specific use case

## 📈 Performance

- **Processing Time**: < 1 minute for 24 hours of earthquakes
- **Memory Usage**: < 500MB peak
- **API Response**: < 100ms for most endpoints
- **Container Size**: ~800MB (includes GDAL + geospatial stack)

## 🤝 Contributing

This showcase is part of the PyMapGIS project. See the main [CONTRIBUTING.md](../../CONTRIBUTING.md) for guidelines.

## 📄 License

MIT License - see [LICENSE](../../LICENSE) for details.

---

**TL;DR**: PyMapGIS turns a blend of public GeoJSON + remote COG into a live, vector-tiled "quake impact" map in 50 lines and one Docker run. Try it, inspect the code, and you'll see exactly why PyMapGIS is the simplest path from raw open data to production-grade geospatial APIs.
