# ⚡ 5-Minute QuickStart

**Get PyMapGIS running with live earthquake data in under 5 minutes!**

## 🎯 What You'll Build

A live web map showing earthquake impact assessment that:
- Fetches real-time USGS earthquake data
- Calculates population exposure within 50km of each quake
- Displays interactive impact visualization
- Runs completely in Docker (no Python setup needed!)

## 🚀 Option 1: Docker Compose (Easiest)

### Prerequisites
- Docker Desktop installed ([Get it here](https://www.docker.com/products/docker-desktop/))
- 5 minutes of your time ⏰

### Steps
```bash
# 1. Clone the repository
git clone https://github.com/pymapgis/core.git
cd core/showcase-starter

# 2. Start the demo (builds and runs automatically)
docker compose up quake-demo

# 3. Open your browser
# Go to: http://localhost:8000
```

**That's it!** 🎉 You should see a live earthquake impact map.

### What You'll See
- 🌍 **Interactive world map** with earthquake markers
- 🔴 **Color-coded impact** (blue = low, red = extreme)
- 📊 **Click earthquakes** for detailed popup info
- 📈 **Real-time data** from USGS (updates every 15 minutes)

## 🚀 Option 2: Manual Docker Build

If you want to understand the build process:

```bash
# 1. Clone and navigate
git clone https://github.com/pymapgis/core.git
cd core/showcase-starter/showcases/quake-impact

# 2. Build the Docker image
docker build -t quake-demo .

# 3. Run the container
docker run -p 8000:8000 quake-demo

# 4. Open browser to http://localhost:8000
```

## 🚀 Option 3: Local Development

For contributors who want to modify the code:

```bash
# 1. Clone and setup Python environment
git clone https://github.com/pymapgis/core.git
cd core
poetry install

# 2. Run the data processing
cd showcase-starter/showcases/quake-impact
poetry run python worker.py

# 3. Start the web server
poetry run uvicorn app:app --host 0.0.0.0 --port 8000

# 4. Open browser to http://localhost:8000
```

## 🔍 What Happens Under the Hood

### Step 1: Data Processing (worker.py)
```python
# Fetch live earthquake data
quakes = pmg.read("https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_day.geojson")

# Buffer each earthquake to 50km
buffers = quakes.geometry.buffer(50_000)

# Calculate population within each buffer
async with pmg.AsyncGeoProcessor() as gp:
    pop_stats = await gp.zonal_stats(WORLDPOP_COG, buffers)

# Compute impact score: log10(population) × magnitude
quakes['Impact'] = quakes.apply(lambda r: math.log10(r.pop50k) * r.mag, axis=1)

# Export to web-ready formats
quakes.to_mvt("tiles/impact/{z}/{x}/{y}.mvt")  # Vector tiles
quakes.to_file("impact.geojson")               # Full data
quakes.plot.save_png("impact.png")             # Static map
```

### Step 2: Web Serving (app.py)
```python
# FastAPI server with multiple endpoints
@app.get("/")                              # Interactive map viewer
@app.get("/health")                        # Health check
@app.get("/public/tiles/{z}/{x}/{y}.mvt")  # Vector tiles (public)
@app.get("/internal/latest")               # Full data (JWT protected)
```

### Step 3: Frontend (static/index.html + app.js)
- **MapLibre GL JS** for interactive mapping
- **Tailwind CSS** for responsive styling
- **Color-coded visualization** based on impact scores
- **Click interactions** for detailed earthquake info

## 🧪 Testing Your Setup

### Health Check
```bash
curl http://localhost:8000/health
# Should return: {"status": "healthy", "features_count": N}
```

### API Endpoints
```bash
# Get latest earthquake data (requires demo token)
curl -H "Authorization: Bearer demo-token" \
     http://localhost:8000/internal/latest

# Test vector tiles
curl http://localhost:8000/public/tiles/0/0/0.mvt
```

### Generated Files
After running, check for these files:
```bash
ls -la
# impact.geojson  - Full earthquake data
# impact.png      - Static overview map  
# tiles/          - Vector tile directory
```

## 🎨 Customization Ideas

Once you have it running, try modifying:

### Change the Impact Formula
```python
# In worker.py, replace the impact calculation:
quakes['Impact'] = quakes['mag'] * np.sqrt(quakes['pop50k'])  # Square root scaling
quakes['Impact'] = quakes['mag'] ** 2 * quakes['pop50k']      # Exponential impact
```

### Adjust the Buffer Distance
```python
# Change from 50km to 100km
buffers = quakes.geometry.buffer(100_000)  # 100km in meters
```

### Modify Map Colors
```javascript
// In static/app.js, change the color ramp:
'circle-color': [
    'interpolate', ['linear'], ['get', 'Impact'],
    0, '#00ff00',    // Green for low impact
    4, '#ffff00',    // Yellow for medium
    6, '#ff8000',    // Orange for high  
    8, '#ff0000'     // Red for extreme
]
```

## 🐛 Troubleshooting

### Container Won't Start
```bash
# Check Docker is running
docker --version

# View container logs
docker logs quake-demo

# Rebuild if needed
docker build --no-cache -t quake-demo .
```

### No Earthquake Data
The demo includes fallback test data if the USGS feed is unavailable. You'll see:
```
⚠️ Could not fetch USGS data, creating test data for demo
✅ Created 5 test earthquakes for demo
```

### Port Already in Use
```bash
# Use a different port
docker run -p 8080:8000 quake-demo
# Then open http://localhost:8080
```

### Performance Issues
- **Slow processing**: Reduce the number of earthquakes processed
- **Memory usage**: The demo uses <100MB RAM for typical earthquake counts
- **Network timeouts**: Check your internet connection for USGS data access

## ✅ Success Criteria

You'll know it's working when you see:

1. ✅ **Docker container starts** without errors
2. ✅ **Health endpoint responds** at `/health`
3. ✅ **Interactive map loads** at `http://localhost:8000`
4. ✅ **Earthquake markers appear** on the map
5. ✅ **Clicking markers shows** popup with impact data
6. ✅ **Console shows** processing completion logs

## 🚀 Next Steps

Now that you have PyMapGIS running:

1. **📖 Explore the code** - Check out `worker.py` and `app.py`
2. **🎨 Try customizations** - Modify colors, formulas, or buffer distances
3. **💡 Pick a new demo** - Browse [ideas/](ideas/) for your next project
4. **🤝 Contribute** - Follow [CONTRIBUTING.md](CONTRIBUTING.md) to submit your own showcase

## 🆘 Need Help?

- 💬 **Ask questions** in [GitHub Discussions](https://github.com/pymapgis/core/discussions)
- 🐛 **Report issues** with the [bug report template](https://github.com/pymapgis/core/issues/new?template=bug_report.md)
- 📖 **Read the docs** at [pymapgis.readthedocs.io](https://pymapgis.readthedocs.io)

---

**🎉 Congratulations!** You've successfully run your first PyMapGIS showcase demo. 

Ready to build your own? **[Check out the ideas folder →](ideas/)**
