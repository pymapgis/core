# 📦 Poetry Setup Guide for PyMapGIS Local Showcases

![Poetry](https://img.shields.io/badge/Poetry-Dependency%20Management-blue) ![Python](https://img.shields.io/badge/Python-3.8%2B-green)

## 🎯 What is Poetry?

Poetry is a modern dependency management and packaging tool for Python that PyMapGIS uses for all local showcases. It provides:

- **🔒 Dependency Resolution**: Automatic conflict resolution and lock files
- **📦 Virtual Environments**: Isolated Python environments per project
- **🚀 Easy Installation**: One-command setup for all dependencies
- **🔄 Reproducible Builds**: Exact same dependencies across all environments

## 🛠️ Installing Poetry

### Windows (WSL2 Recommended)
```bash
# Install Poetry using the official installer
curl -sSL https://install.python-poetry.org | python3 -

# Add Poetry to PATH (add to ~/.bashrc for persistence)
export PATH="$HOME/.local/bin:$PATH"

# Verify installation
poetry --version
```

### macOS
```bash
# Install Poetry using the official installer
curl -sSL https://install.python-poetry.org | python3 -

# Add Poetry to PATH (add to ~/.zshrc for persistence)
export PATH="$HOME/.local/bin:$PATH"

# Verify installation
poetry --version
```

### Linux
```bash
# Install Poetry using the official installer
curl -sSL https://install.python-poetry.org | python3 -

# Add Poetry to PATH (add to ~/.bashrc for persistence)
export PATH="$HOME/.local/bin:$PATH"

# Verify installation
poetry --version
```

## 🚀 Using Poetry with PyMapGIS Local Showcases

### Quick Start
```bash
# Clone the PyMapGIS repository
git clone https://github.com/pymapgis/core.git
cd core/showcaseslocal/[showcase-name]

# Install all dependencies (creates virtual environment automatically)
poetry install

# Run the data worker
poetry run python [worker-name].py

# Start the web application
poetry run python app.py

# View at: http://localhost:8000
```

### Common Poetry Commands
```bash
# Install dependencies from pyproject.toml
poetry install

# Add a new dependency
poetry add requests

# Add a development dependency
poetry add --group dev pytest

# Run a command in the virtual environment
poetry run python script.py

# Activate the virtual environment shell
poetry shell

# Show dependency tree
poetry show --tree

# Update dependencies
poetry update

# Export requirements.txt (if needed)
poetry export -f requirements.txt --output requirements.txt
```

## 🔧 Poetry Configuration for PyMapGIS

### Recommended Settings
```bash
# Configure Poetry to create virtual environments in project directory
poetry config virtualenvs.in-project true

# Configure Poetry to use Python 3.8+ (required for PyMapGIS)
poetry config virtualenvs.prefer-active-python true

# Show current configuration
poetry config --list
```

### Project Structure
```
showcaseslocal/[showcase-name]/
├── pyproject.toml          # Poetry configuration and dependencies
├── poetry.lock            # Locked dependency versions
├── [worker].py            # Data processing worker
├── app.py                 # FastAPI web application
├── static/                # Web interface files
└── data/                  # Data storage directory
```

## 📋 PyMapGIS Dependencies

All PyMapGIS local showcases use these core dependencies:

### Core Dependencies
- **fastapi**: Modern web framework for APIs
- **uvicorn**: ASGI server for FastAPI
- **pandas**: Data manipulation and analysis
- **geopandas**: Geospatial data processing
- **requests**: HTTP library for API calls
- **matplotlib**: Visualization and plotting

### Geospatial Dependencies
- **fiona**: File I/O for geospatial data
- **shapely**: Geometric operations
- **pyproj**: Cartographic projections

## 🐛 Troubleshooting

### Common Issues and Solutions

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
# Remove existing virtual environment
poetry env remove python

# Recreate virtual environment
poetry install

# Check virtual environment location
poetry env info --path
```

#### Dependency Conflicts
```bash
# Clear Poetry cache
poetry cache clear pypi --all

# Update lock file
poetry lock --no-update

# Reinstall dependencies
poetry install
```

#### Python Version Issues
```bash
# Check Python version
python3 --version

# Use specific Python version
poetry env use python3.8

# Install with specific Python
poetry install --python python3.8
```

## 🔗 Integration with Docker

Poetry works seamlessly with Docker for PyMapGIS showcases:

```dockerfile
# Copy Poetry files
COPY pyproject.toml poetry.lock ./

# Install dependencies
RUN poetry config virtualenvs.create false \
    && poetry install --no-dev --no-interaction --no-ansi

# Copy application code
COPY . .
```

## 📚 Additional Resources

- **Poetry Documentation**: https://python-poetry.org/docs/
- **PyMapGIS GitHub**: https://github.com/pymapgis/core
- **Python Virtual Environments**: https://docs.python.org/3/tutorial/venv.html
- **FastAPI Documentation**: https://fastapi.tiangolo.com/

## 🎯 Next Steps

1. **Install Poetry** using the commands above
2. **Clone PyMapGIS** repository
3. **Navigate** to any local showcase directory
4. **Run `poetry install`** to set up dependencies
5. **Start developing** with `poetry run python app.py`

Poetry makes dependency management effortless for PyMapGIS local showcases! 🚀
