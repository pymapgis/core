# 🐧 Ubuntu Setup Guide - Quake Impact Now

## Complete Ubuntu Installation and Setup Guide

This guide covers running the Quake Impact Now showcase on Ubuntu systems, from fresh installation to local development.

## 📋 Prerequisites

### System Requirements
- **Ubuntu 20.04 LTS** or newer (22.04 LTS recommended)
- **4GB RAM** minimum (8GB recommended)
- **2GB free disk space**
- **Internet connection** for data fetching

### Supported Ubuntu Versions
- ✅ Ubuntu 22.04 LTS (Jammy Jellyfish) - **Recommended**
- ✅ Ubuntu 20.04 LTS (Focal Fossa)
- ✅ Ubuntu 24.04 LTS (Noble Numbat)
- ✅ Ubuntu derivatives (Linux Mint, Pop!_OS, Elementary OS)

## 🚀 Quick Start (Docker Method)

### Option 1: Docker Hub Image (Fastest)

```bash
# Install Docker if not already installed
sudo apt update
sudo apt install -y docker.io
sudo systemctl start docker
sudo systemctl enable docker

# Add your user to docker group (logout/login required)
sudo usermod -aG docker $USER
newgrp docker

# Run the showcase
docker run -p 8000:8000 nicholaskarlson/quake-impact-now:latest

# Open browser to http://localhost:8000
```

### Option 2: Build from Source

```bash
# Clone the repository
git clone https://github.com/pymapgis/core.git
cd core/showcases/quake-impact-now

# Build and run
docker build -t quake-impact-now .
docker run -p 8000:8000 quake-impact-now

# Open browser to http://localhost:8000
```

## 🛠️ Local Development Setup

### Step 1: Install System Dependencies

```bash
# Update package list
sudo apt update && sudo apt upgrade -y

# Install Python and development tools
sudo apt install -y \
    python3 \
    python3-pip \
    python3-venv \
    python3-dev \
    build-essential \
    git \
    curl \
    wget

# Install geospatial libraries (optional, for full PyMapGIS features)
sudo apt install -y \
    gdal-bin \
    libgdal-dev \
    libproj-dev \
    libgeos-dev \
    libspatialindex-dev

# Verify installations
python3 --version
pip3 --version
git --version
```

### Step 2: Clone and Setup Repository

```bash
# Clone the PyMapGIS repository
git clone https://github.com/pymapgis/core.git
cd core

# Switch to the showcase branch
git checkout quake-impact-showcase-dev

# Navigate to the showcase directory
cd showcases/quake-impact-now
```

### Step 3: Python Environment Setup

#### Option A: Virtual Environment (Recommended)

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt

# Verify installation
python --version
pip list
```

#### Option B: Poetry (Advanced)

```bash
# Install Poetry
curl -sSL https://install.python-poetry.org | python3 -

# Add Poetry to PATH (add to ~/.bashrc for persistence)
export PATH="$HOME/.local/bin:$PATH"

# Navigate to project root
cd ../../

# Install dependencies
poetry install

# Activate Poetry shell
poetry shell

# Navigate back to showcase
cd showcases/quake-impact-now
```

### Step 4: Run the Application

```bash
# Process earthquake data
python quake_impact.py

# Start the web server
python app.py

# Open browser to http://localhost:8000
```

## 🔧 Ubuntu-Specific Configuration

### Firewall Configuration

```bash
# Check firewall status
sudo ufw status

# Allow port 8000 (if firewall is enabled)
sudo ufw allow 8000/tcp

# Reload firewall
sudo ufw reload
```

### Service Management (Optional)

Create a systemd service for automatic startup:

```bash
# Create service file
sudo nano /etc/systemd/system/quake-impact.service
```

Add the following content:

```ini
[Unit]
Description=Quake Impact Now Service
After=network.target

[Service]
Type=simple
User=your-username
WorkingDirectory=/path/to/core/showcases/quake-impact-now
Environment=PATH=/path/to/venv/bin
ExecStart=/path/to/venv/bin/python app.py
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start the service:

```bash
# Reload systemd
sudo systemctl daemon-reload

# Enable service
sudo systemctl enable quake-impact.service

# Start service
sudo systemctl start quake-impact.service

# Check status
sudo systemctl status quake-impact.service
```

## 🐛 Troubleshooting Ubuntu Issues

### Common Problems and Solutions

#### Port Already in Use
```bash
# Find process using port 8000
sudo netstat -tlnp | grep :8000

# Kill the process (replace PID)
sudo kill -9 <PID>

# Or use a different port
python app.py --port 8080
```

#### Permission Denied Errors
```bash
# Fix Python permissions
sudo chown -R $USER:$USER ~/.local

# Fix project permissions
sudo chown -R $USER:$USER ~/core
```

#### Missing Dependencies
```bash
# Install missing Python headers
sudo apt install python3-dev

# Install missing build tools
sudo apt install build-essential

# Install missing geospatial libraries
sudo apt install libgdal-dev libproj-dev libgeos-dev
```

#### Virtual Environment Issues
```bash
# Remove and recreate virtual environment
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

### Performance Optimization

#### System Tuning
```bash
# Increase file descriptor limits
echo "* soft nofile 65536" | sudo tee -a /etc/security/limits.conf
echo "* hard nofile 65536" | sudo tee -a /etc/security/limits.conf

# Optimize network settings
echo "net.core.somaxconn = 65536" | sudo tee -a /etc/sysctl.conf
sudo sysctl -p
```

#### Memory Management
```bash
# Check memory usage
free -h

# Monitor process memory
top -p $(pgrep -f "python app.py")

# Clear cache if needed
sudo sync && sudo sysctl vm.drop_caches=3
```

## 📊 Monitoring and Logging

### Application Logs
```bash
# View application logs
tail -f /var/log/quake-impact.log

# Monitor with journalctl (if using systemd)
sudo journalctl -u quake-impact.service -f
```

### System Monitoring
```bash
# Install monitoring tools
sudo apt install htop iotop nethogs

# Monitor system resources
htop

# Monitor network usage
sudo nethogs

# Monitor disk I/O
sudo iotop
```

## 🔄 Development Workflow

### Code Changes
```bash
# Make changes to code
nano app.py

# Restart application
# If running manually: Ctrl+C and restart
# If using systemd:
sudo systemctl restart quake-impact.service
```

### Testing
```bash
# Run health check
curl http://localhost:8000/health

# Test API endpoints
curl http://localhost:8000/public/latest

# Load test (install apache2-utils first)
sudo apt install apache2-utils
ab -n 100 -c 10 http://localhost:8000/health
```

### Git Workflow
```bash
# Check status
git status

# Add changes
git add .

# Commit changes
git commit -m "feat: your changes"

# Push to remote
git push origin quake-impact-showcase-dev
```

## 🚀 Production Deployment

### Using Nginx (Reverse Proxy)
```bash
# Install Nginx
sudo apt install nginx

# Create configuration
sudo nano /etc/nginx/sites-available/quake-impact
```

Add configuration:
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

Enable and restart:
```bash
sudo ln -s /etc/nginx/sites-available/quake-impact /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

This guide provides everything needed to run Quake Impact Now on Ubuntu systems, from quick Docker deployment to full development setup.
