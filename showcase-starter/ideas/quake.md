# 🌍 Quake Impact Now

**Status**: ✅ **Implemented** - See [showcases/quake-impact/](../showcases/quake-impact/)

## Overview
Live earthquake impact assessment that combines real-time USGS earthquake data with population exposure analysis to create an interactive "likely-felt" impact map.

## Why This Demo?
- **100% Open Data** - Only two public datasets, no API keys required
- **Fast Execution** - Complete pipeline in under 60 seconds
- **Visual Impact** - Immediate, intuitive earthquake impact visualization
- **PyMapGIS Showcase** - Demonstrates all three marquee features

## Data Sources

| Dataset | Format & URL | Notes |
|---------|--------------|-------|
| **USGS "all_day" earthquakes** | GeoJSON - https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_day.geojson | ~20 kB, hourly updates |
| **WorldPop 2020 population** | Cloud-Optimised GeoTIFF on AWS Open Data | ~200 MB per continent, streamed reads |

## Core Logic (~40 lines)

```python
# 1. Fetch earthquake data
quakes = pmg.read(QUAKE_FEED)[['id','mag','geometry']]

# 2. Buffer epicenters to 50 km  
buffers = quakes.geometry.buffer(50_000)

# 3. Async zonal statistics for population
async with pmg.AsyncGeoProcessor() as gp:
    pop_stats = await gp.zonal_stats(WORLDPOP_COG, buffers, stats=("sum",))

# 4. Calculate impact score
quakes['pop50k'] = pop_stats['sum']
quakes['Impact'] = quakes.apply(
    lambda r: (math.log10(max(r.pop50k,1)) * r.mag), axis=1
)

# 5. Export results
quakes.to_mvt("tiles/impact/{z}/{x}/{y}.mvt")
quakes.to_file("impact.geojson")
quakes.plot.save_png("impact.png")
```

## Impact Formula
**ImpactScore = log₁₀(population_within_50km) × magnitude**

This formula balances:
- **Magnitude** - Earthquake strength (logarithmic scale)
- **Population Exposure** - People within likely-felt radius
- **Logarithmic Scaling** - Prevents mega-cities from dominating

## Visualization

### Color Scheme
- 🔵 **Blue (0-4)** - Low impact (rural areas, small quakes)
- 🟡 **Yellow (4-6)** - Medium impact (moderate exposure)
- 🟠 **Orange (6-8)** - High impact (urban areas or strong quakes)
- 🔴 **Red (8+)** - Extreme impact (major cities + strong quakes)

### Map Features
- **Interactive markers** sized by impact score
- **Click popups** with magnitude, population, and impact details
- **Real-time updates** every 15 minutes
- **Global coverage** with automatic zoom to active regions

## Technical Implementation

### Processing Pipeline
1. **Data Fetch** (< 1s) - USGS GeoJSON via HTTP
2. **Buffering** (< 1s) - 50km circles around epicenters
3. **Zonal Stats** (~5s) - Population sum within buffers
4. **Impact Calc** (< 1s) - Logarithmic scoring formula
5. **Export** (< 2s) - MVT tiles, GeoJSON, PNG

### Web Interface
- **FastAPI** backend with health checks
- **MapLibre GL JS** frontend with Tailwind CSS
- **Vector tiles** for smooth pan/zoom
- **JWT protection** for full data access

### Fallback Mechanisms
- **Test data generation** when USGS feed unavailable
- **Population estimation** when WorldPop access fails
- **Graceful degradation** with informative error messages

## Performance Metrics

### Typical Run (24-hour period)
- **Earthquakes processed**: 50-200 events
- **Processing time**: 5-10 seconds total
- **Memory usage**: < 100MB
- **Output size**: < 5MB (tiles + data)

### Scalability
- **Global coverage** - handles worldwide earthquake activity
- **Real-time capable** - 15-minute update cycles
- **Resource efficient** - runs on free-tier cloud instances

## Educational Value

### Geospatial Concepts Demonstrated
- **Coordinate Reference Systems** - WGS84 to Web Mercator projection
- **Buffer Analysis** - Distance-based spatial operations
- **Zonal Statistics** - Raster-vector overlay analysis
- **Vector Tiles** - Efficient web mapping data format
- **Async Processing** - Parallel geospatial operations

### Domain Knowledge
- **Seismology** - Earthquake magnitude scales and felt intensity
- **Demographics** - Population density and exposure analysis
- **Risk Assessment** - Multi-factor impact scoring
- **Emergency Response** - Rapid situation assessment tools

## Deployment Options

### Local Development
```bash
poetry run python quake_impact.py
poetry run uvicorn app:app --host 0.0.0.0 --port 8000
```

### Docker Container
```bash
docker build -t quake-impact .
docker run -p 8000:8000 quake-impact
```

### Cloud Platforms
- **Railway** - One-click deploy from GitHub
- **Render** - Automatic builds from repository
- **Fly.io** - Global edge deployment
- **AWS/GCP/Azure** - Container services

## Extensions & Variations

### Data Enhancements
- **ShakeMap integration** - USGS intensity predictions
- **Historical analysis** - Multi-day earthquake patterns
- **Tsunami warnings** - Coastal impact assessment
- **Infrastructure overlay** - Critical facilities exposure

### Algorithm Variations
- **Distance decay** - Weighted impact by distance from epicenter
- **Vulnerability factors** - Building codes, soil conditions
- **Economic impact** - GDP-weighted exposure calculations
- **Social vulnerability** - Age, income, disability factors

### Visualization Options
- **Heatmaps** - Continuous impact surfaces
- **Isochrones** - Equal-impact contour lines
- **3D visualization** - Magnitude as height dimension
- **Time animation** - Earthquake sequence playback

## Community Contributions

This demo serves as the **reference implementation** for PyMapGIS showcases, demonstrating:
- ✅ Clean, readable code structure
- ✅ Comprehensive error handling
- ✅ Multiple output formats
- ✅ Interactive web interface
- ✅ Docker containerization
- ✅ Detailed documentation

**Want to contribute?** Use this as a template for your own showcase demo!

## Resources

### Data Sources
- [USGS Earthquake Feeds](https://earthquake.usgs.gov/earthquakes/feed/)
- [WorldPop Population Data](https://www.worldpop.org/)
- [AWS Open Data](https://registry.opendata.aws/worldpop/)

### Technical Documentation
- [PyMapGIS Documentation](https://pymapgis.readthedocs.io)
- [MapLibre GL JS](https://maplibre.org/maplibre-gl-js-docs/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)

### Seismology Background
- [USGS Earthquake Magnitude](https://www.usgs.gov/natural-hazards/earthquake-hazards/science/earthquake-magnitude-energy-release-and-shaking-intensity)
- [Modified Mercalli Intensity Scale](https://www.usgs.gov/natural-hazards/earthquake-hazards/science/modified-mercalli-intensity-scale)

---

**🎉 This demo is live and ready to use!**

👉 **[Try it now](../showcases/quake-impact/)** - See the implementation  
👉 **[Docker Hub](https://hub.docker.com/r/pymapgis/quake-impact)** - Pull the container  
👉 **[Live Demo](https://quake-impact.pymapgis.org)** - Interactive web version
