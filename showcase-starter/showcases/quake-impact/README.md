# 🌍 Quake Impact Now - PyMapGIS Showcase Demo

A **50-line micro-service** that turns the public USGS earthquake feed + open population rasters into a live 'likely-felt' map, showcasing PyMapGIS's three marquee features:

1. **Single-line multi-format ingest** (`pmg.read`)
2. **Async raster zonal statistics** 
3. **Instant vector-tile export** for browser maps

## 🎯 Why This Demo?

- **100% Open Data**: Only two public datasets, no API keys required
- **Fast Execution**: Runs in < 1 minute on a free GitHub Actions runner
- **Visual Impact**: Immediate, intuitive earthquake impact visualization
- **Minimal Code**: Core functionality in ~50 lines of Python

## 📊 Data Sources

| Dataset | Format & URL | Notes |
|---------|--------------|-------|
| **USGS "all_day" earthquakes** | GeoJSON - https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_day.geojson | ~20 kB, hourly updates |
| **WorldPop 2020 population** | Cloud-Optimised GeoTIFF on AWS Open Data | ~200 MB per continent, streamed reads |

*WorldPop is CC-BY-4.0 licensed, no API key required.*

## 🚀 Quick Start

### Option 1: Docker (Recommended)

```bash
# Pull and run the demo
docker run -p 8000:8000 ghcr.io/pymapgis/quake-impact:latest

# Or build locally
git clone https://github.com/pymapgis/core.git
cd core/examples/quake-impact-demo
docker build -t quake-impact .
docker run -p 8000:8000 quake-impact
```

### Option 2: Local Development

```bash
# Clone and setup
git clone https://github.com/pymapgis/core.git
cd core/examples/quake-impact-demo

# Install dependencies
pip install -r requirements.txt

# Run the data processing
python quake_impact.py

# Start the web server
uvicorn app:app --host 0.0.0.0 --port 8000
```

## 🌐 Access the Demo

Once running, open your browser to:

- **http://localhost:8000** - Interactive earthquake impact map
- **http://localhost:8000/health** - Health check endpoint
- **http://localhost:8000/internal/latest** - Full GeoJSON data (requires JWT token)

### JWT Authentication

For the protected endpoint, use:
```bash
curl -H "Authorization: Bearer demo-token" \
     http://localhost:8000/internal/latest | jq .
```

## 🔧 How It Works

### Core Processing (`quake_impact.py`)

```python
import pymapgis as pmg, pandas as pd, asyncio, math, datetime as dt

POP_COG  = "https://data.worldpop.org/GIS/Population/Global_2000_2020/2020/0_Mosaicked/ppp_2020_1km_Aggregated.tif"
QUAKE_FEED = "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_day.geojson"

async def main():
    # 1. Read earthquake data
    quakes = pmg.read(QUAKE_FEED)[['id','mag','geometry']]
    
    # 2. Buffer epicenters to 50 km
    buffers = quakes.geometry.buffer(50_000)
    
    # 3. Async zonal statistics for population
    async with pmg.AsyncGeoProcessor(workers=4) as gp:
        pop = await gp.zonal_stats(POP_COG, buffers, stats=("sum",), nodata=0)
    
    # 4. Calculate impact score
    quakes['pop50k'] = pop['sum']
    quakes['Impact'] = quakes.apply(
        lambda r: (math.log10(max(r.pop50k,1))*r.mag), axis=1)
    
    # 5. Export results
    quakes.pmg.to_mvt("tiles/impact/{z}/{x}/{y}.mvt", layer="quake")
    quakes.to_file("impact.geojson", driver="GeoJSON")
    quakes.plot.save_png("impact.png", column="Impact", dpi=150)
```

### Web Interface (`app.py`)

- **FastAPI** backend with vector tile serving
- **MapLibre GL JS** frontend with interactive visualization
- **JWT authentication** for protected endpoints
- **CORS enabled** for cross-origin requests

## 📈 Performance

| Step | Action | Time |
|------|--------|------|
| 1 | Fetch USGS GeoJSON | < 1 s |
| 2 | Buffer epicenters | negligible |
| 3 | Async zonal stats | ~5 s |
| 4 | Calculate impact scores | instant |
| 5 | Export vector tiles | < 1 s |
| 6 | Save GeoJSON & PNG | < 1 s |

**Total: ~7 seconds** for complete processing pipeline

## 🎨 Visualization Features

- **Color-coded impact scale**: Blue (low) → Red (extreme)
- **Interactive popups**: Click earthquakes for details
- **Responsive design**: Works on desktop and mobile
- **Real-time updates**: Refresh data every 15 minutes
- **Multiple formats**: Vector tiles, GeoJSON, static PNG

## 🔧 Customization

### Change Buffer Distance
```python
buffers = quakes.geometry.buffer(100_000)  # 100 km instead of 50 km
```

### Different Population Dataset
```python
POP_COG = "s3://your-bucket/custom-population.tif"
```

### Custom Impact Formula
```python
quakes['Impact'] = quakes['mag'] * np.sqrt(quakes['pop50k'])
```

### Additional Statistics
```python
pop = await gp.zonal_stats(POP_COG, buffers, stats=("sum", "mean", "max"))
```

## 🐳 Docker Configuration

The included Dockerfile:
- Uses Python 3.11 slim base image
- Installs GDAL and geospatial libraries
- Runs data processing on startup
- Serves web interface on port 8000
- Includes health checks for monitoring

## 🚀 Deployment Options

### Local Development
```bash
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

### Production (Docker)
```bash
docker run -d -p 8000:8000 --name quake-impact quake-impact:latest
```

### Cloud Platforms
- **Railway**: `railway deploy`
- **Render**: Connect GitHub repo
- **Fly.io**: `fly deploy`
- **AWS/GCP/Azure**: Use container services

## 📊 API Endpoints

| Endpoint | Method | Description | Auth |
|----------|--------|-------------|------|
| `/` | GET | Interactive map viewer | None |
| `/health` | GET | Health check | None |
| `/public/tiles/{z}/{x}/{y}.pbf` | GET | Vector tiles | None |
| `/internal/latest` | GET | Full GeoJSON data | JWT |
| `/static/{filename}` | GET | Static files | None |

## 🔍 Monitoring

Health check endpoint provides:
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00Z",
  "version": "1.0.0",
  "service": "quake-impact-now",
  "checks": {
    "data_file": "ok",
    "tiles": "ok", 
    "features_count": 42
  }
}
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test with `python quake_impact.py`
5. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details.

## 🙏 Acknowledgments

- **USGS** for real-time earthquake data
- **WorldPop** for open population datasets
- **PyMapGIS** team for the geospatial toolkit
- **MapLibre** for the web mapping library
