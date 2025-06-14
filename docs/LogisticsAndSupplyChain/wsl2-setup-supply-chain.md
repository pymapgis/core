# 🐧 WSL2 Setup for Supply Chain

## Complete Windows Environment Configuration for PyMapGIS Logistics

This comprehensive guide provides step-by-step instructions for setting up WSL2 with Ubuntu specifically for PyMapGIS logistics and supply chain analysis, with focus on end-user success and troubleshooting.

### 1. Understanding WSL2 for Supply Chain Analytics

#### Why WSL2 for Logistics Applications
- **Performance advantages**: Better I/O performance for large transportation datasets
- **Container compatibility**: Native Docker support for logistics containers
- **Development environment**: Consistent Linux environment on Windows
- **Tool ecosystem**: Access to Linux-based geospatial and optimization tools
- **Cost effectiveness**: No need for separate Linux machines or VMs

#### Supply Chain Specific Benefits
- **Large dataset handling**: Efficient processing of transportation networks
- **Real-time capabilities**: Better performance for GPS and IoT data streams
- **Optimization algorithms**: Access to Linux-native mathematical solvers
- **Geospatial libraries**: Full GDAL/GEOS/PROJ support
- **Container deployment**: Seamless Docker integration for logistics examples

### 2. System Requirements and Compatibility

#### Minimum Requirements
```
Operating System: Windows 10 version 2004+ or Windows 11
Processor: x64 with virtualization support
Memory: 8GB RAM (16GB recommended for large logistics datasets)
Storage: 20GB free space (50GB+ for comprehensive examples)
Network: Broadband internet for data downloads
```

#### Hardware Compatibility Check
```powershell
# Check Windows version
winver

# Check virtualization support
systeminfo | findstr /i "hyper-v"

# Check available memory
wmic computersystem get TotalPhysicalMemory

# Check available disk space
wmic logicaldisk get size,freespace,caption
```

#### Corporate Environment Considerations
- **Group Policy**: Check for WSL restrictions
- **Antivirus**: Ensure compatibility with virtualization
- **Network**: Proxy and firewall configuration
- **Permissions**: Administrator access requirements
- **Compliance**: Security and audit considerations

### 3. Pre-Installation Preparation

#### System Updates and Preparation
```powershell
# Update Windows to latest version
# Settings > Update & Security > Windows Update

# Enable Windows features
dism.exe /online /enable-feature /featurename:Microsoft-Windows-Subsystem-Linux /all /norestart
dism.exe /online /enable-feature /featurename:VirtualMachinePlatform /all /norestart

# Restart computer
shutdown /r /t 0
```

#### Download Required Components
- **WSL2 Linux kernel update**: Download from Microsoft
- **Ubuntu distribution**: From Microsoft Store or manual download
- **Windows Terminal**: Enhanced terminal experience
- **Docker Desktop**: Container platform for logistics examples

#### Backup and Safety Measures
- **System backup**: Create restore point before installation
- **Data backup**: Backup important files and documents
- **Recovery plan**: Know how to rollback changes if needed
- **Documentation**: Keep installation notes and configurations

### 4. WSL2 Installation Process

#### Step 1: Install WSL2 Kernel Update
```powershell
# Download and install WSL2 kernel update
# https://wslstorestorage.blob.core.windows.net/wslblob/wsl_update_x64.msi

# Set WSL2 as default version
wsl --set-default-version 2

# Verify WSL installation
wsl --status
```

#### Step 2: Install Ubuntu Distribution
```powershell
# Install Ubuntu from Microsoft Store
# Or use command line
wsl --install -d Ubuntu

# List available distributions
wsl --list --online

# Check installed distributions
wsl --list --verbose
```

#### Step 3: Initial Ubuntu Configuration
```bash
# First-time setup creates user account
# Enter username (lowercase, no spaces)
# Enter password (will be hidden)
# Confirm password

# Update system packages
sudo apt update && sudo apt upgrade -y

# Install essential tools
sudo apt install -y curl wget git vim nano htop
```

### 5. Ubuntu Environment Setup for Logistics

#### Python and Data Science Environment
```bash
# Install Python development tools
sudo apt install -y python3-pip python3-venv python3-dev

# Install system dependencies for geospatial work
sudo apt install -y build-essential libgdal-dev libproj-dev libgeos-dev
sudo apt install -y libspatialindex-dev libffi-dev libssl-dev

# Install additional tools for logistics
sudo apt install -y postgresql-client redis-tools
```

#### Geospatial and Optimization Libraries
```bash
# Install GDAL and geospatial tools
sudo apt install -y gdal-bin python3-gdal

# Install optimization solvers
sudo apt install -y coinor-cbc coinor-clp

# Install database tools
sudo apt install -y sqlite3 spatialite-bin

# Verify installations
python3 -c "import gdal; print(f'GDAL version: {gdal.__version__}')"
```

#### Git Configuration for Development
```bash
# Configure Git for logistics projects
git config --global user.name "Your Name"
git config --global user.email "your.email@company.com"

# Generate SSH key for GitHub
ssh-keygen -t ed25519 -C "your.email@company.com"

# Display public key for GitHub
cat ~/.ssh/id_ed25519.pub
```

### 6. Docker Desktop Integration

#### Docker Desktop Installation
```powershell
# Download Docker Desktop for Windows
# Enable WSL2 backend during installation
# Restart computer after installation
```

#### Docker Configuration for Logistics
```bash
# Verify Docker integration
docker --version
docker-compose --version

# Test Docker with simple container
docker run hello-world

# Pull PyMapGIS logistics base image
docker pull pymapgis/logistics-base:latest
```

#### Resource Allocation for Logistics Workloads
```ini
# Create or edit ~/.wslconfig
[wsl2]
memory=12GB          # Allocate sufficient memory for large datasets
processors=6         # Use multiple cores for optimization
swap=4GB            # Swap space for memory-intensive operations
localhostForwarding=true  # Enable port forwarding for web interfaces
```

### 7. Network Configuration and Connectivity

#### Network Setup for Supply Chain Applications
```bash
# Test network connectivity
ping google.com
ping api.openstreetmap.org

# Configure DNS if needed
sudo nano /etc/resolv.conf
# Add: nameserver 8.8.8.8
```

#### Firewall and Security Configuration
```powershell
# Windows Firewall rules for WSL2
# Allow Docker Desktop through firewall
# Configure port forwarding for logistics applications
netsh interface portproxy add v4tov4 listenport=8888 listenaddress=0.0.0.0 connectport=8888 connectaddress=localhost
```

#### Corporate Network Configuration
```bash
# Configure proxy if required
export http_proxy=http://proxy.company.com:8080
export https_proxy=http://proxy.company.com:8080

# Add to ~/.bashrc for persistence
echo 'export http_proxy=http://proxy.company.com:8080' >> ~/.bashrc
echo 'export https_proxy=http://proxy.company.com:8080' >> ~/.bashrc
```

### 8. Performance Optimization for Logistics

#### File System Performance
```bash
# Use WSL2 file system for better performance
# Store logistics projects in /home/username/
mkdir -p ~/logistics-projects
cd ~/logistics-projects

# Avoid Windows file system for large datasets
# Use /mnt/c/ only for final results export
```

#### Memory and CPU Optimization
```bash
# Monitor resource usage
htop
free -h
df -h

# Optimize for large transportation datasets
# Increase virtual memory if needed
sudo sysctl vm.max_map_count=262144
```

#### Database Performance Tuning
```bash
# Configure PostgreSQL for spatial data
sudo apt install -y postgresql postgresql-contrib postgis

# Optimize for logistics workloads
sudo nano /etc/postgresql/*/main/postgresql.conf
# shared_buffers = 256MB
# effective_cache_size = 1GB
# work_mem = 64MB
```

### 9. Development Environment Setup

#### VS Code Integration
```bash
# Install VS Code extensions for logistics development
# Remote - WSL
# Python
# Jupyter
# Docker
# GitLens
```

#### Jupyter Lab Configuration
```bash
# Install Jupyter Lab with extensions
pip3 install jupyterlab ipywidgets

# Configure for logistics analysis
jupyter lab --generate-config

# Enable extensions
jupyter labextension install @jupyter-widgets/jupyterlab-manager
```

#### Environment Variables for Logistics
```bash
# Add to ~/.bashrc
export LOGISTICS_DATA_DIR=~/logistics-projects/data
export PYMAPGIS_CACHE_DIR=~/.pymapgis/cache
export OMP_NUM_THREADS=4  # Optimize for multi-core processing

# Source the configuration
source ~/.bashrc
```

### 10. Testing and Validation

#### System Validation Tests
```bash
# Test Python geospatial stack
python3 -c "
import geopandas as gpd
import pandas as pd
import numpy as np
print('✓ GeoPandas working')

import shapely
print('✓ Shapely working')

import fiona
print('✓ Fiona working')
"

# Test optimization libraries
python3 -c "
import scipy.optimize
print('✓ SciPy optimization working')

try:
    import pulp
    print('✓ PuLP optimization working')
except ImportError:
    print('⚠ PuLP not installed')
"
```

#### Docker Integration Test
```bash
# Test logistics container deployment
docker run -p 8888:8888 -v ~/logistics-projects:/workspace \
  pymapgis/logistics-demo:latest

# Verify port forwarding
curl http://localhost:8888/api/status
```

#### Performance Benchmark
```bash
# Create performance test script
cat > ~/test_performance.py << 'EOF'
import time
import numpy as np
import pandas as pd

# Test data processing performance
start_time = time.time()
data = np.random.rand(1000000, 10)
df = pd.DataFrame(data)
result = df.groupby(df.columns[0] // 0.1).mean()
end_time = time.time()

print(f"Data processing test: {end_time - start_time:.2f} seconds")
print("✓ Performance test completed")
EOF

python3 ~/test_performance.py
```

### 11. Troubleshooting Common Issues

#### WSL2 Installation Problems
```bash
# Check WSL status
wsl --status

# Reset WSL if needed
wsl --shutdown
wsl --unregister Ubuntu
wsl --install -d Ubuntu

# Check virtualization
dism.exe /online /get-featureinfo /featurename:VirtualMachinePlatform
```

#### Docker Integration Issues
```bash
# Restart Docker service
sudo service docker restart

# Check Docker daemon
docker info

# Reset Docker if needed
docker system prune -a
```

#### Network Connectivity Problems
```bash
# Reset network configuration
sudo service networking restart

# Check DNS resolution
nslookup google.com

# Test with different DNS
sudo nano /etc/resolv.conf
# Try: nameserver 1.1.1.1
```

### 12. Maintenance and Updates

#### Regular Maintenance Tasks
```bash
# Update Ubuntu packages
sudo apt update && sudo apt upgrade -y

# Clean package cache
sudo apt autoremove -y
sudo apt autoclean

# Update Python packages
pip3 list --outdated
pip3 install --upgrade pip
```

#### Docker Maintenance
```bash
# Clean Docker resources
docker system prune -f

# Update Docker images
docker pull pymapgis/logistics-base:latest

# Check disk usage
docker system df
```

#### Performance Monitoring
```bash
# Monitor system resources
htop
iotop
nethogs

# Check WSL2 resource usage
wsl --list --verbose
```

### 13. Security Best Practices

#### Access Control and Permissions
```bash
# Set proper file permissions
chmod 700 ~/.ssh
chmod 600 ~/.ssh/id_ed25519

# Configure sudo timeout
sudo visudo
# Add: Defaults timestamp_timeout=15
```

#### Data Protection
```bash
# Encrypt sensitive logistics data
sudo apt install -y gnupg

# Create encrypted backup
tar -czf - ~/logistics-projects | gpg -c > logistics-backup.tar.gz.gpg
```

#### Network Security
```bash
# Configure firewall
sudo ufw enable
sudo ufw allow 22/tcp
sudo ufw allow 8888/tcp  # Jupyter
sudo ufw allow 8501/tcp  # Streamlit
```

### 14. Advanced Configuration

#### Custom Kernel Parameters
```bash
# Optimize for large datasets
echo 'vm.max_map_count=262144' | sudo tee -a /etc/sysctl.conf
echo 'fs.file-max=2097152' | sudo tee -a /etc/sysctl.conf

# Apply changes
sudo sysctl -p
```

#### Environment Automation
```bash
# Create setup script for new environments
cat > ~/setup-logistics-env.sh << 'EOF'
#!/bin/bash
# Automated logistics environment setup

# Update system
sudo apt update && sudo apt upgrade -y

# Install logistics dependencies
sudo apt install -y python3-pip python3-venv python3-dev
sudo apt install -y libgdal-dev libproj-dev libgeos-dev
sudo apt install -y postgresql-client redis-tools

# Create virtual environment
python3 -m venv ~/logistics-env
source ~/logistics-env/bin/activate

# Install Python packages
pip install pymapgis[logistics] jupyter pandas geopandas

echo "✓ Logistics environment setup complete"
EOF

chmod +x ~/setup-logistics-env.sh
```

### 15. Success Validation Checklist

#### ✅ Installation Verification
- [ ] WSL2 installed and running
- [ ] Ubuntu distribution configured
- [ ] Docker Desktop integrated
- [ ] Python geospatial stack working
- [ ] Network connectivity established

#### ✅ Performance Validation
- [ ] Memory allocation optimized
- [ ] File system performance acceptable
- [ ] Docker containers running smoothly
- [ ] Port forwarding working
- [ ] Resource monitoring configured

#### ✅ Development Environment
- [ ] VS Code WSL integration working
- [ ] Git configured and SSH keys set up
- [ ] Jupyter Lab accessible
- [ ] Environment variables configured
- [ ] Logistics examples deployable

---

*This comprehensive WSL2 setup guide ensures optimal Windows environment configuration for PyMapGIS logistics and supply chain analysis with focus on performance, reliability, and user success.*
