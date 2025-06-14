# 🚚 SCex1: Simple Supply Chain Optimization Example

A containerized supply chain optimization demonstration using PyMapGIS, designed for easy deployment on Windows with WSL2 and Docker Desktop.

## 📋 Overview

This example demonstrates:
- **Warehouse Location Optimization**: Using K-means clustering to find optimal warehouse locations
- **Distribution Network Analysis**: Analyzing customer-warehouse assignments and costs
- **Interactive Visualization**: Web-based maps and dashboards
- **REST API**: HTTP endpoints for integration with other systems
- **Docker Deployment**: Containerized solution for easy deployment

## 🏗️ Architecture

```
SCex1/
├── src/                          # Source code
│   ├── supply_chain_optimizer.py # Core optimization logic
│   ├── api.py                    # FastAPI web service
│   └── main.py                   # CLI and main entry point
├── docker/                       # Docker configuration
│   ├── Dockerfile               # Container definition
│   ├── docker-compose.yml       # Multi-service setup
│   └── nginx.conf               # Reverse proxy config
├── data/                        # Sample data
├── scripts/                     # Build and deployment scripts
└── docs/                        # Documentation
```

## 🚀 Quick Start

### Prerequisites

- **Windows 10/11** with WSL2 enabled
- **Docker Desktop** with WSL2 backend
- **Git** for cloning the repository

### Option 1: Using Pre-built Docker Image

```bash
# Pull and run the pre-built image
docker run -p 8000:8000 nicholaskarlson/scex1-supply-chain:latest

# Access the application
# Web UI: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

### Option 2: Building from Source

```bash
# Clone the repository (if not already done)
git clone <repository-url>
cd PyMapGIS-private/core/SCex1

# Build the Docker image
./scripts/build_docker.sh

# Run the container
docker run -p 8000:8000 nicholaskarlson/scex1-supply-chain:latest
```

### Option 3: Using Docker Compose

```bash
# Start all services
cd SCex1
docker-compose -f docker/docker-compose.yml up -d

# View logs
docker-compose -f docker/docker-compose.yml logs -f

# Stop services
docker-compose -f docker/docker-compose.yml down
```

## 🖥️ Windows WSL2 Setup Guide

### Step 1: Enable WSL2

Open PowerShell as Administrator and run:

```powershell
# Enable WSL and Virtual Machine Platform
dism.exe /online /enable-feature /featurename:Microsoft-Windows-Subsystem-Linux /all /norestart
dism.exe /online /enable-feature /featurename:VirtualMachinePlatform /all /norestart

# Restart your computer
shutdown /r /t 0
```

### Step 2: Install WSL2 Kernel Update

1. Download the WSL2 kernel update from Microsoft
2. Install the downloaded package
3. Set WSL2 as default:

```powershell
wsl --set-default-version 2
```

### Step 3: Install Ubuntu

```powershell
# Install Ubuntu from Microsoft Store or command line
wsl --install -d Ubuntu

# Verify installation
wsl --list --verbose
```

### Step 4: Install Docker Desktop

1. Download Docker Desktop for Windows
2. During installation, ensure "Use WSL 2 instead of Hyper-V" is selected
3. Restart your computer
4. Open Docker Desktop and verify WSL2 integration is enabled

### Step 5: Test the Setup

```bash
# In WSL2 Ubuntu terminal
docker --version
docker run hello-world

# If successful, you're ready to run the supply chain example!
```

## 🔧 Usage Examples

### Command Line Interface

```bash
# Run basic demo
python -m src.main demo

# Custom parameters
python -m src.main demo --customers 50 --warehouses 4 --output results

# Start web server
python -m src.main server --port 8000
```

### REST API Examples

```bash
# Health check
curl http://localhost:8000/health

# Run optimization
curl -X POST "http://localhost:8000/optimize" \
  -H "Content-Type: application/json" \
  -d '{
    "num_customers": 30,
    "num_warehouses": 3,
    "random_seed": 42
  }'

# Get results
curl http://localhost:8000/results/{optimization_id}

# Download interactive map
curl http://localhost:8000/map/{optimization_id} -o map.html
```

### Python API Examples

```python
from src.supply_chain_optimizer import SimpleSupplyChainOptimizer

# Initialize optimizer
optimizer = SimpleSupplyChainOptimizer(random_seed=42)

# Generate sample data
optimizer.generate_sample_data(
    num_customers=30,
    num_potential_warehouses=10
)

# Optimize warehouse locations
solution = optimizer.optimize_warehouse_locations(num_warehouses=3)

# Create visualization
map_obj = optimizer.create_visualization(save_path="results.html")

# Generate report
report = optimizer.generate_report()
print(f"Total cost: ${report['optimization_summary']['total_cost']:,.2f}")
```

## 📊 Features

### Core Optimization
- **K-means Clustering**: Optimal warehouse placement based on customer locations
- **Cost Minimization**: Balances transportation costs and warehouse fixed costs
- **Capacity Planning**: Ensures warehouses can handle assigned demand
- **Utilization Analysis**: Monitors warehouse efficiency

### Visualization
- **Interactive Maps**: Folium-based maps with customer and warehouse locations
- **Color Coding**: Visual assignment of customers to warehouses
- **Popup Information**: Detailed data on hover/click
- **Export Options**: Save maps as HTML files

### Web Interface
- **REST API**: Full HTTP API for integration
- **Interactive Documentation**: Swagger/OpenAPI docs at `/docs`
- **Health Monitoring**: Built-in health checks
- **Background Processing**: Async map generation

### Docker Features
- **Multi-stage Build**: Optimized image size
- **Security**: Non-root user execution
- **Health Checks**: Container health monitoring
- **Volume Mounts**: Persistent data storage
- **Environment Configuration**: Flexible deployment options

## 🔍 Technical Details

### Optimization Algorithm

The example uses a simplified but effective approach:

1. **Data Generation**: Creates random customer and warehouse locations
2. **Clustering**: Uses K-means to group customers geographically
3. **Assignment**: Places warehouses at cluster centers
4. **Capacity Sizing**: Calculates required warehouse capacity
5. **Cost Calculation**: Computes total transportation and fixed costs

### Performance Characteristics

- **Scalability**: Handles 1-1000 customers efficiently
- **Memory Usage**: ~100MB for typical scenarios
- **Processing Time**: <5 seconds for 100 customers
- **API Response**: <2 seconds for optimization requests

### Dependencies

- **PyMapGIS**: Core geospatial functionality
- **Scikit-learn**: K-means clustering
- **Folium**: Interactive mapping
- **FastAPI**: Web API framework
- **Pandas/NumPy**: Data processing
- **Docker**: Containerization

## 🛠️ Development

### Local Development Setup

```bash
# Install Poetry (if not already installed)
curl -sSL https://install.python-poetry.org | python3 -

# Install dependencies
cd SCex1
poetry install

# Activate virtual environment
poetry shell

# Run tests
pytest

# Run the application
python -m src.main demo
```

### Building Custom Images

```bash
# Build with custom tag
docker build -t my-supply-chain:v1.0 -f docker/Dockerfile .

# Build with build arguments
docker build --build-arg PYTHON_VERSION=3.11 -t my-supply-chain .

# Multi-platform build
docker buildx build --platform linux/amd64,linux/arm64 -t my-supply-chain .
```

## 📈 Monitoring and Troubleshooting

### Health Checks

```bash
# Container health
docker ps --format "table {{.Names}}\t{{.Status}}"

# Application health
curl http://localhost:8000/health

# Detailed status
curl http://localhost:8000/list
```

### Common Issues

**Issue**: Container fails to start
```bash
# Check logs
docker logs scex1-supply-chain

# Check port conflicts
netstat -tulpn | grep 8000
```

**Issue**: WSL2 integration problems
```bash
# Restart Docker Desktop
# Verify WSL2 integration in Docker Desktop settings
# Check WSL2 status: wsl --status
```

**Issue**: Permission errors
```bash
# Ensure proper file permissions
chmod +x scripts/*.sh

# Check Docker daemon permissions
sudo usermod -aG docker $USER
```

## 📚 Additional Resources

- [PyMapGIS Documentation](../docs/)
- [Docker Desktop WSL2 Guide](https://docs.docker.com/desktop/windows/wsl/)
- [Supply Chain Optimization Theory](../docs/LogisticsAndSupplyChain/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

MIT License - see [LICENSE](../LICENSE) for details.

## 👥 Support

- **Issues**: Report bugs and feature requests
- **Discussions**: Community support and questions
- **Documentation**: Comprehensive guides and examples

---

*This example demonstrates the power of PyMapGIS for supply chain optimization in a containerized, production-ready format suitable for Windows environments with WSL2 and Docker Desktop.*
