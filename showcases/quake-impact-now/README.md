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

## 📚 Documentation

| Document | Description |
|----------|-------------|
| **[Architecture Overview](ARCHITECTURE.md)** | System design, data flow, and PyMapGIS integration |
| **[Ubuntu Setup Guide](UBUNTU_SETUP.md)** | Complete Ubuntu installation and local development |
| **[PyMapGIS Integration](PYMAPGIS_INTEGRATION.md)** | How PyMapGIS powers the application |
| **[Windows 11 Setup](#-windows-11--wsl2--docker-desktop-setup)** | Windows + WSL2 + Docker Desktop guide |

## 🚀 Quick Start

### Option 1: Docker Hub (Recommended - One Command!)

```bash
# Pull and run the pre-built image
docker run -p 8000:8000 nicholaskarlson/quake-impact-now:latest

# Open browser to http://localhost:8000
```

### Option 2: Build from Source

```bash
# Clone and build locally
git clone https://github.com/pymapgis/core.git
cd core/showcases/quake-impact-now
docker build -t quake-impact-now .
docker run -p 8000:8000 quake-impact-now
```

### Option 3: Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run data processing
python quake_impact.py

# Start web server
python app.py

# Open browser to http://localhost:8000
```

### Option 4: Ubuntu Local Development

```bash
# Install system dependencies
sudo apt update && sudo apt install -y python3 python3-pip python3-venv git

# Clone repository
git clone https://github.com/pymapgis/core.git
cd core/showcases/quake-impact-now

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the application
python quake_impact.py
python app.py

# Open browser to http://localhost:8000
```

**📖 For detailed Ubuntu setup instructions, see [Ubuntu Setup Guide](UBUNTU_SETUP.md)**

### Option 5: Poetry (PyMapGIS Development)

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

## 🪟 Windows 11 + WSL2 + Docker Desktop Setup

### Prerequisites for Windows Users

1. **Windows 11** (Home, Pro, or Enterprise)
2. **WSL2** (Windows Subsystem for Linux 2)
3. **Docker Desktop for Windows**
4. **Web browser** (Chrome, Edge, Firefox)

### Step-by-Step Windows Setup

#### 1. Install WSL2 (if not already installed)

Open **PowerShell as Administrator** and run:

```powershell
# Enable WSL and Virtual Machine Platform
dism.exe /online /enable-feature /featurename:Microsoft-Windows-Subsystem-Linux /all /norestart
dism.exe /online /enable-feature /featurename:VirtualMachinePlatform /all /norestart

# Restart your computer, then set WSL2 as default
wsl --set-default-version 2

# Install Ubuntu (recommended)
wsl --install -d Ubuntu
```

#### 2. Install Docker Desktop

1. **Download**: Go to [Docker Desktop for Windows](https://www.docker.com/products/docker-desktop/)
2. **Install**: Run the installer with default settings
3. **Configure**: Ensure "Use WSL 2 based engine" is enabled
4. **Verify**: Open Docker Desktop and check it's running

#### 3. Run Quake Impact Now

Open **Windows Terminal** or **PowerShell** and run:

```powershell
# Pull and run the showcase
docker run -p 8000:8000 nicholaskarlson/quake-impact-now:latest
```

#### 4. Access the Application

- **Automatic**: The app should open automatically in your default browser
- **Manual**: Navigate to http://localhost:8000
- **Alternative**: Try http://127.0.0.1:8000 if localhost doesn't work

### Windows-Specific Tips

#### Docker Desktop Configuration
- **Memory**: Allocate at least 4GB RAM to Docker (Settings → Resources → Advanced)
- **WSL Integration**: Enable integration with your Ubuntu distribution
- **File Sharing**: Ensure C: drive is shared if building from source

#### Troubleshooting Windows Issues

**Port Already in Use:**
```powershell
# Find what's using port 8000
netstat -ano | findstr :8000

# Kill the process (replace PID with actual process ID)
taskkill /PID <PID> /F

# Or use a different port
docker run -p 8080:8000 nicholaskarlson/quake-impact-now:latest
```

**Docker Not Starting:**
```powershell
# Restart Docker Desktop
# Or restart the Docker service
net stop com.docker.service
net start com.docker.service
```

**WSL2 Issues:**
```powershell
# Restart WSL
wsl --shutdown
wsl

# Update WSL
wsl --update
```

#### Performance Optimization for Windows

1. **Close unnecessary applications** to free up memory
2. **Use SSD storage** for better Docker performance
3. **Enable Hyper-V** for optimal virtualization
4. **Update Windows** to the latest version

### Windows Security Considerations

- **Windows Defender**: May scan Docker images (can slow down builds)
- **Firewall**: Ensure Docker Desktop is allowed through Windows Firewall
- **Antivirus**: Add Docker directories to exclusion list if using third-party antivirus

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

## 🔒 Security Features

This Docker image has been built with security best practices:

### Container Security
- **Non-root user**: Runs as `pymapgis` user (not root)
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

### Docker Hub Image
- **Verified publisher**: Published by verified Docker Hub account
- **Regular updates**: Image updated with security patches
- **Scan results**: Regularly scanned for vulnerabilities
- **Minimal layers**: Optimized layer structure for security

## 📈 Performance

- **Processing Time**: < 1 minute for 24 hours of earthquakes
- **Memory Usage**: < 500MB peak
- **API Response**: < 100ms for most endpoints
- **Container Size**: ~425MB (optimized for security and performance)
- **Startup Time**: < 5 seconds from container start to ready

## 🤝 Contributing

This showcase is part of the PyMapGIS project. See the main [CONTRIBUTING.md](../../CONTRIBUTING.md) for guidelines.

## 📄 License

MIT License - see [LICENSE](../../LICENSE) for details.

---

**TL;DR**: PyMapGIS turns a blend of public GeoJSON + remote COG into a live, vector-tiled "quake impact" map in 50 lines and one Docker run. Try it, inspect the code, and you'll see exactly why PyMapGIS is the simplest path from raw open data to production-grade geospatial APIs.
