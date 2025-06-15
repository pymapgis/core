# 🚀 PyMapGIS Showcase Starter

**Build your own geospatial micro-app in 40 lines of code!**

[![Open Issues](https://img.shields.io/github/issues/pymapgis/core/showcase)](https://github.com/pymapgis/core/issues?q=is%3Aissue+is%3Aopen+label%3Ashowcase)
[![Good First Issue](https://img.shields.io/github/issues/pymapgis/core/good%20first%20issue)](https://github.com/pymapgis/core/issues?q=is%3Aissue+is%3Aopen+label%3A%22good+first+issue%22)
[![Docker Pulls](https://img.shields.io/docker/pulls/pymapgis/core)](https://hub.docker.com/r/pymapgis/core)

## 🎯 What is this?

The **Showcase Starter** is your fast-track to contributing to PyMapGIS! Pick a public data feed, write ~40 lines of Python, and create a live web map that demonstrates PyMapGIS's power.

### 🌟 Examples of Showcase Apps:
- **🌍 Quake Impact Now** - Live earthquake impact assessment
- **🚛 Border Flow Now** - Real-time truck wait times at crossings  
- **✈️ Flight Delay Now** - Airport delay visualization
- **❄️ Snow Freight Now** - Winter road conditions for logistics
- **🔥 Wildfire Risk Now** - Fire danger + population exposure

Each showcase is a **complete, deployable micro-service** that:
- Fetches live public data (no API keys needed)
- Processes it with PyMapGIS in ~40 lines
- Serves interactive web maps via FastAPI
- Runs in Docker for instant deployment

## 🚀 Quick Start (5 minutes)

### Option 1: Try the Quake Demo
```bash
# Clone and test the earthquake impact demo
git clone https://github.com/pymapgis/core.git
cd core/showcase-starter
docker compose up quake-demo

# Open http://localhost:8000 - live earthquake impact map!
```

### Option 2: Create Your Own
```bash
# 1. Pick an idea from /ideas/ folder
# 2. Generate your scaffold
python scripts/new_demo.py your-demo-name

# 3. Edit the generated files
cd showcases/your-demo-name/
# Edit worker.py (add your data processing logic)
# Edit static/app.js (customize the map colors)

# 4. Test locally
docker build -t your-demo .
docker run -p 8000:8000 your-demo

# 5. Submit PR!
```

## 📁 Repository Structure

```
showcase-starter/
├── README.md              # This file
├── QUICKSTART.md           # 5-minute Docker test guide
├── CONTRIBUTING.md         # Contribution guidelines
├── TEMPLATE/               # Copy-paste scaffold for new demos
│   ├── Dockerfile          # Ready-to-use container config
│   ├── worker.py           # Data processing template (~40 LOC)
│   ├── app.py              # FastAPI web server
│   ├── static/
│   │   ├── index.html      # MapLibre + Tailwind frontend
│   │   └── app.js          # Map visualization logic
│   └── entry.ps1           # Windows auto-launch script
├── ideas/                  # Pre-designed demo concepts
│   ├── quake.md            # ✅ Implemented
│   ├── border-flow.md      # 🚛 Truck wait times
│   ├── flight-delay.md     # ✈️ Airport delays
│   ├── snow-freight.md     # ❄️ Winter road conditions
│   ├── wildfire-risk.md    # 🔥 Fire danger mapping
│   ├── drought-monitor.md  # 🌵 Drought conditions
│   └── ...                 # More ideas welcome!
├── scripts/
│   ├── new_demo.py         # Scaffold generator
│   └── validate_demo.py    # CI validation script
└── showcases/              # Completed demos (created by contributors)
    ├── quake-impact/       # ✅ Reference implementation
    ├── border-flow/        # 🚧 Your contribution here!
    └── ...
```

## 🎨 Available Demo Ideas

| Demo | Difficulty | Data Source | Status |
|------|------------|-------------|---------|
| [🌍 Quake Impact](ideas/quake.md) | ⭐ Easy | USGS GeoJSON | ✅ Complete |
| [🚛 Border Flow](ideas/border-flow.md) | ⭐ Easy | CBP Wait Times | 🚧 Open |
| [✈️ Flight Delay](ideas/flight-delay.md) | ⭐ Easy | FAA JSON | 🚧 Open |
| [❄️ Snow Freight](ideas/snow-freight.md) | ⭐⭐ Medium | DOT Road Conditions | 🚧 Open |
| [🔥 Wildfire Risk](ideas/wildfire-risk.md) | ⭐⭐ Medium | NIFC + Census | 🚧 Open |
| [🌵 Drought Monitor](ideas/drought-monitor.md) | ⭐⭐ Medium | USDM Shapefiles | 🚧 Open |
| [🌙 Night Lights](ideas/night-lights.md) | ⭐⭐⭐ Hard | VIIRS + OSM | 🚧 Open |
| [💨 Air Quality](ideas/air-quality.md) | ⭐⭐⭐ Hard | EPA + Weather | 🚧 Open |

**Want to suggest a new idea?** [Open an issue](https://github.com/pymapgis/core/issues/new?template=showcase-idea.md) with the `showcase` label!

## 🏆 Contributor Benefits

When your showcase gets merged, you get:

- 🐳 **Docker Hub Image** - `pymapgis/your-demo:latest` published automatically
- 📖 **Documentation Feature** - Your demo showcased on the official docs site
- 🏷️ **GitHub Release** - Tagged as `showcase/your-demo`
- 🎉 **Social Recognition** - Featured in our monthly community blog
- 💼 **Portfolio Piece** - Real geospatial project for your resume

## 🛠️ Development Workflow

### 1. Claim an Issue
- Browse [showcase issues](https://github.com/pymapgis/core/issues?q=is%3Aissue+is%3Aopen+label%3Ashowcase)
- Comment "🚀 starting" to claim it
- Issue moves to "In Progress" on our [project board](https://github.com/pymapgis/core/projects/1)

### 2. Build Your Demo
```bash
# Generate scaffold
python scripts/new_demo.py your-demo-name

# Implement core logic in worker.py (~40 lines)
# Customize map styling in static/app.js
# Test with: docker build . && docker run -p 8000:8000 your-demo
```

### 3. Submit PR
- Include 200×120 screenshot of your map
- Update the main docs table
- All CI checks must pass (build, lint, size < 200MB)

### 4. Get Merged & Published
- One maintainer review required
- Auto-deployment to Docker Hub
- Featured in next community update

## 📋 Quality Standards

All showcase demos must:

- ✅ **Build successfully** in Docker (< 200MB final image)
- ✅ **Process real data** from public feeds (no API keys)
- ✅ **Complete in < 60 seconds** on a standard laptop
- ✅ **Serve interactive map** at `http://localhost:8000`
- ✅ **Include health check** endpoint at `/health`
- ✅ **Pass all linting** (black, flake8, isort)
- ✅ **Have clear documentation** with data sources cited

## 🤝 Getting Help

- 💬 **GitHub Discussions** - [Ask questions](https://github.com/pymapgis/core/discussions)
- 📖 **Documentation** - [PyMapGIS Docs](https://pymapgis.readthedocs.io)
- 🐛 **Bug Reports** - [Open an issue](https://github.com/pymapgis/core/issues/new)
- 💡 **Feature Requests** - [Suggest improvements](https://github.com/pymapgis/core/discussions/categories/ideas)

## 📜 License

All showcase demos are dual-licensed under **Apache 2.0** and **MIT** to ensure maximum reusability. By contributing, you agree to license your code under these terms.

---

**Ready to build something awesome?** 🚀

👉 **[Start with QUICKSTART.md](QUICKSTART.md)** for a 5-minute test drive  
👉 **[Browse ideas/](ideas/)** to pick your first demo  
👉 **[Check CONTRIBUTING.md](CONTRIBUTING.md)** for detailed guidelines  

Let's show the world what PyMapGIS can do! 🌍✨
