# 🎭 Poetry Setup Guide - Quake Impact Now

## Complete Poetry Development Environment Setup

This guide covers setting up the Quake Impact Now showcase using Poetry, PyMapGIS's preferred dependency management tool, with a locally cloned repository.

## 🎭 What is Poetry and Why Use It?

### Poetry Overview
**Poetry** is a modern dependency management and packaging tool for Python that simplifies project setup, dependency resolution, and virtual environment management. It's designed to replace the traditional combination of pip, virtualenv, and setup.py with a single, unified tool.

### Why PyMapGIS Uses Poetry

1. **Dependency Resolution**: Poetry automatically resolves complex dependency conflicts that are common in geospatial projects
2. **Lock Files**: Ensures reproducible builds across different environments with poetry.lock
3. **Virtual Environment Management**: Automatically creates and manages isolated environments
4. **Build System**: Modern PEP 518-compliant build system for packaging
5. **Development Dependencies**: Separates development tools from production dependencies

### Benefits for Geospatial Development

- **Complex Dependencies**: Geospatial libraries like GDAL, Fiona, and Rasterio have complex system dependencies
- **Version Conflicts**: Poetry resolves conflicts between packages like Shapely, GeoPandas, and Rasterio
- **Reproducible Environments**: Ensures the same versions work across development, testing, and production
- **Easy Collaboration**: Other developers get identical environments with `poetry install`

## 📋 Prerequisites

### System Requirements
- **Python 3.8+** (3.10+ recommended)
- **Git** for repository cloning
- **4GB RAM** minimum (8GB recommended)
- **2GB free disk space**
- **Internet connection** for dependency installation

### Supported Operating Systems
- ✅ **Ubuntu 20.04+ / Debian 11+**
- ✅ **macOS 10.15+ (Catalina)**
- ✅ **Windows 10+ with WSL2**
- ✅ **Fedora 34+ / CentOS 8+**
- ✅ **Arch Linux / Manjaro**

## 🚀 Quick Start with Poetry

### Step 1: Install Poetry

#### Option A: Official Installer (Recommended)
```bash
# Install Poetry using the official installer
curl -sSL https://install.python-poetry.org | python3 -

# Add Poetry to PATH (add to ~/.bashrc or ~/.zshrc for persistence)
export PATH="$HOME/.local/bin:$PATH"

# Verify installation
poetry --version
```

#### Option B: Package Manager Installation

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install python3-poetry
```

**macOS (Homebrew):**
```bash
brew install poetry
```

**Fedora:**
```bash
sudo dnf install poetry
```

### Step 2: Clone PyMapGIS Repository

```bash
# Clone the main PyMapGIS repository
git clone https://github.com/pymapgis/core.git
cd core

# Switch to the showcase development branch
git checkout quake-impact-showcase-dev

# Verify you're on the correct branch
git branch --show-current
```

### Step 3: Poetry Environment Setup

```bash
# Navigate to the project root (where pyproject.toml is located)
cd /path/to/core  # Adjust path as needed

# Configure Poetry to create virtual environments in project directory (optional)
poetry config virtualenvs.in-project true

# Install all dependencies including PyMapGIS
poetry install

# Verify installation
poetry show pymapgis
```

### Step 4: Run the Quake Impact Now Showcase

#### Method A: Using Poetry Run (Recommended)

```bash
# From the project root directory (/path/to/core)
# Process earthquake data
poetry run python showcases/quake-impact-now/quake_impact.py

# Start the web application
poetry run python showcases/quake-impact-now/app.py

# Open browser to http://localhost:8000
```

#### Method B: Using Poetry Environment

```bash
# Activate Poetry environment (Poetry 2.0+)
source $(poetry env info --path)/bin/activate

# Navigate to showcase directory
cd showcases/quake-impact-now

# Process earthquake data
python quake_impact.py

# Start the web application
python app.py

# Open browser to http://localhost:8000
```

#### Method C: Direct Execution

```bash
# Navigate to showcase directory first
cd showcases/quake-impact-now

# Use Poetry to run from project root
cd ../../
poetry run python showcases/quake-impact-now/quake_impact.py
poetry run python showcases/quake-impact-now/app.py
```

## 🔧 Poetry Configuration

### Project Structure with Poetry
```
core/
├── pyproject.toml          # Main Poetry configuration
├── poetry.lock            # Locked dependency versions
├── pymapgis/              # PyMapGIS source code
├── showcases/
│   └── quake-impact-now/
│       ├── app.py         # Web application
│       ├── quake_impact.py # Data processing
│       └── requirements.txt # Fallback dependencies
└── tests/                 # Test suite
```

### Poetry Commands Reference

#### Environment Management
```bash
# Create/activate virtual environment
poetry shell

# Run commands in Poetry environment
poetry run python script.py

# Install new dependencies
poetry add package-name

# Install development dependencies
poetry add --group dev package-name

# Update dependencies
poetry update

# Show installed packages
poetry show

# Show dependency tree
poetry show --tree
```

#### Development Workflow
```bash
# Install project in development mode
poetry install

# Run tests
poetry run pytest

# Run linting
poetry run flake8

# Run type checking
poetry run mypy

# Build package
poetry build

# Publish package (for maintainers)
poetry publish
```

## 🛠️ PyMapGIS Development with Poetry

### Installing PyMapGIS from Source

```bash
# From the core directory
poetry install

# This installs PyMapGIS in development mode, so changes to the source
# code are immediately available without reinstalling
```

### Adding Showcase Dependencies

```bash
# Add showcase-specific dependencies
poetry add fastapi uvicorn requests pandas

# Add optional geospatial dependencies
poetry add geopandas rasterio fiona

# Add development tools
poetry add --group dev pytest black isort mypy
```

### Working with Multiple Python Versions

```bash
# Specify Python version for the project
poetry env use python3.10

# List available environments
poetry env list

# Remove environment
poetry env remove python3.10
```

## 🔍 Troubleshooting Poetry Issues

### Common Problems and Solutions

#### Poetry Not Found
```bash
# Ensure Poetry is in PATH
echo $PATH | grep -o "$HOME/.local/bin"

# If not found, add to shell profile
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

#### Virtual Environment Issues
```bash
# Clear Poetry cache
poetry cache clear pypi --all

# Remove and recreate environment
poetry env remove python
poetry install
```

#### Dependency Conflicts
```bash
# Update lock file
poetry lock --no-update

# Force update specific package
poetry update package-name

# Show dependency conflicts
poetry show --outdated
```

#### Permission Errors
```bash
# Fix Poetry directory permissions
sudo chown -R $USER:$USER ~/.cache/pypoetry
sudo chown -R $USER:$USER ~/.local/share/pypoetry
```

### Platform-Specific Issues

#### macOS Issues
```bash
# Install Xcode command line tools if needed
xcode-select --install

# Fix SSL certificate issues
/Applications/Python\ 3.x/Install\ Certificates.command
```

#### Windows WSL2 Issues
```bash
# Ensure WSL2 is using correct Python
which python3
poetry env use $(which python3)

# Fix line ending issues
git config --global core.autocrlf input
```

#### Linux Issues
```bash
# Install system dependencies for geospatial packages
sudo apt install libgdal-dev libproj-dev libgeos-dev

# Fix locale issues
export LC_ALL=C.UTF-8
export LANG=C.UTF-8
```

## 🚀 Advanced Poetry Usage

### Custom Poetry Configuration

```bash
# Configure Poetry settings
poetry config virtualenvs.create true
poetry config virtualenvs.in-project true
poetry config virtualenvs.prefer-active-python true

# View all configuration
poetry config --list
```

### Working with Private Repositories

```bash
# Add private repository
poetry source add --priority=primary private-repo https://private.repo.com/simple/

# Configure authentication
poetry config http-basic.private-repo username password
```

### Performance Optimization

```bash
# Use parallel installation
poetry config installer.parallel true

# Increase timeout for slow connections
poetry config installer.timeout 600

# Use system git for faster cloning
poetry config installer.use-system-git true
```

## 🔄 Development Workflow

### Daily Development Routine

```bash
# Start development session
cd /path/to/core
poetry shell

# Update dependencies (weekly)
poetry update

# Navigate to showcase
cd showcases/quake-impact-now

# Make code changes...

# Test changes
python quake_impact.py
python app.py

# Run tests
cd ../../
poetry run pytest tests/

# Commit changes
git add .
git commit -m "feat: your changes"
git push origin quake-impact-showcase-dev
```

### Contributing to PyMapGIS

```bash
# Create feature branch
git checkout -b feature/your-feature

# Make changes and test
poetry run pytest

# Format code
poetry run black .
poetry run isort .

# Type check
poetry run mypy pymapgis/

# Submit pull request
git push origin feature/your-feature
```

## 📊 Performance Monitoring

### Poetry Performance Tips

```bash
# Check dependency resolution time
time poetry install

# Profile package installation
poetry install --verbose

# Monitor virtual environment size
du -sh $(poetry env info --path)

# Check for unused dependencies
poetry show --outdated
```

### Memory Usage Optimization

```bash
# Limit Poetry memory usage
export POETRY_INSTALLER_MAX_WORKERS=2

# Use system packages when possible
poetry install --no-dev

# Clear unnecessary caches
poetry cache clear pypi --all
poetry cache clear _default_cache --all
```

## 🎯 Production Deployment with Poetry

### Building for Production

```bash
# Build wheel package
poetry build

# Export requirements.txt for Docker
poetry export -f requirements.txt --output requirements.txt --without-hashes

# Export with development dependencies
poetry export -f requirements.txt --output requirements-dev.txt --with dev --without-hashes
```

### Docker Integration

The Quake Impact Now showcase includes a production-ready Docker image built with Poetry:

#### Pre-built Docker Image (Recommended)

```bash
# Pull and run the Poetry-based Docker image
docker run -p 8000:8000 nicholaskarlson/quake-impact-now:latest

# The image includes:
# - Poetry dependency management
# - PyMapGIS development installation
# - Complete geospatial stack (GDAL, PROJ, GEOS)
# - Security hardening and health checks
```

#### Building Custom Docker Image

```dockerfile
# Use Poetry in Docker (example from the actual Dockerfile)
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential curl git \
    libgdal-dev libproj-dev libgeos-dev \
    libgdal32 libproj25 libgeos-c1v5

# Install Poetry
RUN pip install --no-cache-dir poetry==1.8.3

# Configure Poetry
ENV POETRY_NO_INTERACTION=1 \
    POETRY_VENV_IN_PROJECT=0 \
    POETRY_VIRTUALENVS_CREATE=false

# Copy Poetry files
COPY pyproject.toml poetry.lock ./
COPY pymapgis/ ./pymapgis/

# Install dependencies
RUN poetry install --only=main --no-root

# Copy application
COPY showcases/quake-impact-now/ ./

# Run application
CMD ["poetry", "run", "python", "app.py"]
```

#### Docker Hub Repository

The official Docker image is available at:
**https://hub.docker.com/repository/docker/nicholaskarlson/quake-impact-now**

This comprehensive guide ensures smooth Poetry-based development for the Quake Impact Now showcase and PyMapGIS contributions.
