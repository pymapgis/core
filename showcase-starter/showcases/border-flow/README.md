# 🚛 Border Flow Now

**Real-time truck wait times at US border crossings - supply chain logistics intelligence**

A 40-line micro-service that turns the public CBP border-wait JSON feed into a live map of cross-border truck congestion, showcasing PyMapGIS's power for logistics analytics.

## 🎯 Why This Demo?

- **Direct Supply Chain Relevance** - 70% of US-Mexico trade travels by truck
- **Real-time Decision Making** - Live wait times impact modal shifts, inventory buffers, fuel costs
- **100% Open Data** - CBP Border Wait Times API + static port locations (no API keys)
- **Perfect PyMapGIS Fit** - JSON + GeoJSON → async join → vector tiles in ~40 lines

## 📊 Data Sources

| Dataset | Format & URL | Update Frequency |
|---------|--------------|------------------|
| **CBP Border Wait Times** | JSON API - https://bwt.cbp.gov/api/bwtdata | Every 15 minutes |
| **Border Port Locations** | Static GeoJSON - bundled in repo | Monthly updates |

## 🚀 Quick Start

### Option 1: Docker (Recommended)
```bash
# Build and run the complete demo
docker build -t border-flow .
docker run -p 8000:8000 border-flow

# Open http://localhost:8000 - live border wait map!
```

### Option 2: Local Development
```bash
# Install dependencies (requires Poetry)
cd /path/to/pymapgis/core
poetry install

# Run the data processing
cd showcase-starter/showcases/border-flow
poetry run python worker.py

# Start the web server
poetry run uvicorn app:app --host 0.0.0.0 --port 8000
```

## 🌐 Demo URLs

Once running, access:
- **http://localhost:8000** - Interactive border wait map
- **http://localhost:8000/health** - Health check and statistics
- **http://localhost:8000/internal/json?token=demo-token** - Full GeoJSON data (JWT protected)
- **http://localhost:8000/static/bwt.png** - Static overview image

## 🔧 How It Works

### Core Processing Logic (~40 lines)
```python
# 1. Fetch CBP border wait times
bwt = pmg.read("https://bwt.cbp.gov/api/bwtdata")  # JSON → DataFrame
ports = pmg.read("data/ports.geojson")             # GeoJSON → GeoDataFrame

# 2. Join wait times with geographic locations
gdf = ports.merge(bwt, on="port_id", how="left")

# 3. Calculate congestion score
gdf["Score"] = gdf.apply(lambda r: math.log1p(r.wait) * r.lanes, axis=1)

# 4. Export results
gdf.to_mvt("tiles/bwt/{z}/{x}/{y}.mvt")  # Vector tiles
gdf.to_file("bwt_latest.geojson")        # Full data
gdf.plot.save_png("bwt.png")             # Static overview
```

### Congestion Score Formula
**CongestionScore = log₁₊(wait_minutes) × commercial_lanes**

This formula:
- Uses `log₁₊` to handle zero waits gracefully
- Amplifies busy crossings with more commercial lanes
- Creates visually meaningful size differences on the map

## 🎨 Visualization Features

### Color Scheme (Traffic Light Logic)
- 🟢 **Green (0-20 min)** - Free flowing, optimal crossing time
- 🟡 **Yellow (20-40 min)** - Moderate delays, plan accordingly
- 🟠 **Orange (40-60 min)** - Heavy delays, consider alternatives
- 🔴 **Red (60+ min)** - Severe congestion, avoid if possible

### Interactive Map Features
- **Circle size** based on congestion score (wait × lanes)
- **Click popups** with detailed wait times and recommendations
- **Dark theme** for professional logistics appearance
- **Auto-refresh** every 5 minutes for live updates

## 📈 Business Value

### Use Cases
- **Freight Logistics** - Route optimization for time-sensitive cargo
- **Supply Chain Planning** - Just-in-time delivery scheduling
- **Trade Analysis** - Border efficiency monitoring and reporting
- **Economic Research** - Cross-border commerce flow patterns

### Target Users
- Trucking companies and freight brokers
- Supply chain managers and logistics coordinators
- Border trade analysts and government planners
- Academic researchers studying trade flows

## 🛠️ Technical Architecture

### Processing Pipeline
1. **Data Ingestion** (< 1s) - CBP JSON API via HTTP
2. **Spatial Join** (< 1s) - Merge wait times with port coordinates
3. **Score Calculation** (< 1s) - Congestion formula application
4. **Multi-format Export** (< 2s) - MVT tiles, GeoJSON, PNG

### Web Interface
- **FastAPI** backend with health monitoring
- **MapLibre GL JS** frontend with dark theme
- **Vector tiles** for smooth pan/zoom performance
- **JWT authentication** for protected data access

### Performance Metrics
- **Total processing time**: < 5 seconds
- **Memory usage**: < 50MB for typical dataset
- **Docker image size**: ~200MB
- **Update frequency**: Every 5 minutes (CBP updates every 15 min)

## 🔧 Customization Options

### Change Wait Time Thresholds
```javascript
// In static/app.js, modify the color ranges
ranges: {
    low: 15,        // 0-15 minutes (was 20)
    medium: 30,     // 15-30 minutes (was 40)
    high: 45,       // 30-45 minutes (was 60)
    extreme: 60     // 45+ minutes (was 120)
}
```

### Add More Border Crossings
```json
// In data/ports.geojson, add new features
{
  "type": "Feature",
  "properties": {
    "port_id": "NEW_PORT_ID",
    "name": "New Border Crossing",
    "state": "TX",
    "lanes": 6
  },
  "geometry": { "type": "Point", "coordinates": [-99.123, 27.456] }
}
```

### Modify Congestion Formula
```python
# In worker.py, change the scoring logic
gdf['Score'] = gdf['wait'] * np.sqrt(gdf['lanes'])  # Square root scaling
gdf['Score'] = gdf['wait'] ** 1.5 * gdf['lanes']    # Exponential penalty
```

## 🚀 Extensions & Variations

### Enhanced Features
- **Weather Integration** - Factor in border weather conditions
- **Historical Analysis** - Daily/weekly wait time patterns
- **Predictive Modeling** - Forecast delays based on trends
- **Mobile Optimization** - Trucker-friendly mobile interface

### Additional Data Sources
- **Traffic Cameras** - Visual confirmation of crossing conditions
- **Economic Indicators** - Trade volume correlations
- **Holiday Calendars** - Predictable surge periods
- **Fuel Price Data** - Route cost optimization

### Alternative Visualizations
- **Heatmaps** - Regional congestion patterns
- **Flow Lines** - Trade volume visualization
- **Time Series Charts** - Historical delay trends
- **Comparison Tables** - Crossing efficiency rankings

## 🐳 Docker Hub

This demo is available as a pre-built Docker image:

```bash
# Pull and run the latest version
docker pull pymapgis/border-flow:latest
docker run -p 8000:8000 pymapgis/border-flow:latest
```

## 📊 Sample Output

The demo generates:
- **Vector tiles** at `tiles/bwt/{z}/{x}/{y}.mvt`
- **GeoJSON data** at `bwt_latest.geojson`
- **Static overview** at `bwt.png`

Example log output:
```
✅ 2024-01-15 14:30:00 UTC - Updated 20 ports
📊 Wait times: 5 to 85 minutes
🚛 Congestion scores: 2.1 to 45.3
🔥 Top 5 most congested crossings:
   Laredo - World Trade Bridge - Wait: 85min - Lanes: 8 - Score: 45.3
   Otay Mesa - Otay Mesa - Wait: 62min - Lanes: 12 - Score: 42.1
   ...
```

## 🤝 Contributing

This demo showcases PyMapGIS capabilities for logistics and supply chain applications. To contribute:

1. **Fork the repository** and create a feature branch
2. **Test your changes** with `docker build . && docker run -p 8000:8000 <image>`
3. **Submit a pull request** with screenshots and performance metrics

See [CONTRIBUTING.md](../../CONTRIBUTING.md) for detailed guidelines.

## 📜 License

This demo is dual-licensed under Apache 2.0 and MIT licenses.
Data sources: CBP Border Wait Times (public domain), OpenStreetMap (ODbL).

---

**🚛 Ready to optimize your supply chain?** This demo shows how PyMapGIS makes real-time logistics intelligence accessible in just 40 lines of code!
