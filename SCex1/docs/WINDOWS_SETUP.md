# 🪟 Windows Setup Guide for SCex1 Supply Chain Example

Complete step-by-step guide for running the Supply Chain Optimization example on Windows using WSL2 and Docker Desktop.

## 📋 Prerequisites

- Windows 10 version 2004+ or Windows 11
- Administrator access to your Windows machine
- At least 8GB RAM (16GB recommended)
- 20GB free disk space
- Stable internet connection

## 🔧 Step-by-Step Setup

### Step 1: Check System Compatibility

Open PowerShell as Administrator and run these commands:

```powershell
# Check Windows version
winver

# Check if virtualization is enabled
systeminfo | findstr /i "hyper-v"

# Check available memory
wmic computersystem get TotalPhysicalMemory

# Check available disk space
wmic logicaldisk get size,freespace,caption
```

**Expected Results:**
- Windows version 2004 or higher
- Hyper-V requirements met
- At least 8GB RAM available
- At least 20GB free space

### Step 2: Enable Required Windows Features

In PowerShell as Administrator:

```powershell
# Enable Windows Subsystem for Linux
dism.exe /online /enable-feature /featurename:Microsoft-Windows-Subsystem-Linux /all /norestart

# Enable Virtual Machine Platform
dism.exe /online /enable-feature /featurename:VirtualMachinePlatform /all /norestart

# Restart your computer (required)
shutdown /r /t 0
```

### Step 3: Install WSL2 Kernel Update

1. **Download the WSL2 kernel update package:**
   - Visit: https://wslstorestorage.blob.core.windows.net/wslblob/wsl_update_x64.msi
   - Download and run the installer

2. **Set WSL2 as default version:**
   ```powershell
   wsl --set-default-version 2
   ```

3. **Verify WSL installation:**
   ```powershell
   wsl --status
   ```

### Step 4: Install Ubuntu Distribution

**Option A: Microsoft Store (Recommended)**
1. Open Microsoft Store
2. Search for "Ubuntu"
3. Install "Ubuntu" (latest LTS version)

**Option B: Command Line**
```powershell
wsl --install -d Ubuntu
```

**Initial Ubuntu Setup:**
1. Launch Ubuntu from Start Menu
2. Create a username (lowercase, no spaces)
3. Set a password
4. Update the system:
   ```bash
   sudo apt update && sudo apt upgrade -y
   ```

### Step 5: Install Docker Desktop

1. **Download Docker Desktop:**
   - Visit: https://www.docker.com/products/docker-desktop
   - Download Docker Desktop for Windows

2. **Install Docker Desktop:**
   - Run the installer
   - **Important**: Check "Use WSL 2 instead of Hyper-V" during installation
   - Restart your computer when prompted

3. **Configure Docker Desktop:**
   - Open Docker Desktop
   - Go to Settings → General
   - Ensure "Use the WSL 2 based engine" is checked
   - Go to Settings → Resources → WSL Integration
   - Enable integration with Ubuntu

4. **Verify Docker Installation:**
   ```bash
   # In Ubuntu terminal
   docker --version
   docker-compose --version
   docker run hello-world
   ```

### Step 6: Test the Complete Setup

In your Ubuntu terminal:

```bash
# Verify WSL2 is running
wsl --list --verbose

# Test Docker integration
docker info

# Check available resources
free -h
df -h
```

## 🚀 Running the Supply Chain Example

### Method 1: Using Pre-built Docker Image

```bash
# Pull and run the image
docker run -d -p 8000:8000 --name scex1-demo nicholaskarlson/scex1-supply-chain:latest

# Check if it's running
docker ps

# Access the application
# Open your Windows browser and go to: http://localhost:8000
```

### Method 2: Building from Source

```bash
# Clone the repository (if you have access)
git clone <repository-url>
cd PyMapGIS-private/core/SCex1

# Build the Docker image
./scripts/build_docker.sh

# Run the container
docker run -d -p 8000:8000 --name scex1-demo nicholaskarlson/scex1-supply-chain:latest
```

### Method 3: Using Docker Compose

```bash
cd SCex1
docker-compose -f docker/docker-compose.yml up -d

# View logs
docker-compose -f docker/docker-compose.yml logs -f scex1-app

# Stop when done
docker-compose -f docker/docker-compose.yml down
```

## 🌐 Accessing the Application

Once the container is running, you can access:

- **Main Application**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

## 🔍 Verification and Testing

### Test the API

```bash
# Health check
curl http://localhost:8000/health

# Run optimization (using PowerShell or Ubuntu terminal)
curl -X POST "http://localhost:8000/optimize" -H "Content-Type: application/json" -d '{"num_customers": 20, "num_warehouses": 3}'
```

### Test the Web Interface

1. Open your browser to http://localhost:8000
2. You should see the Supply Chain Optimization API welcome page
3. Click on "📚 View Interactive API Documentation"
4. Try the `/optimize` endpoint with default parameters

## 🛠️ Troubleshooting

### Common Issues and Solutions

**Issue 1: WSL2 installation fails**
```powershell
# Check if virtualization is enabled in BIOS
# Restart and enter BIOS setup
# Enable Intel VT-x or AMD-V
```

**Issue 2: Docker Desktop won't start**
```powershell
# Restart Docker Desktop service
net stop com.docker.service
net start com.docker.service

# Or restart Docker Desktop application
```

**Issue 3: Port 8000 already in use**
```bash
# Find what's using the port
netstat -ano | findstr :8000

# Use a different port
docker run -p 8080:8000 nicholaskarlson/scex1-supply-chain:latest
```

**Issue 4: Container fails to start**
```bash
# Check container logs
docker logs scex1-demo

# Check if image exists
docker images | grep scex1

# Remove and recreate container
docker rm -f scex1-demo
docker run -d -p 8000:8000 --name scex1-demo nicholaskarlson/scex1-supply-chain:latest
```

**Issue 5: Cannot access application from Windows browser**
```bash
# Check if container is running
docker ps

# Check port forwarding
docker port scex1-demo

# Try accessing from Ubuntu terminal first
curl http://localhost:8000/health
```

### Performance Optimization

**Allocate more resources to WSL2:**

Create or edit `%USERPROFILE%\.wslconfig`:
```ini
[wsl2]
memory=8GB
processors=4
swap=2GB
localhostForwarding=true
```

Restart WSL2:
```powershell
wsl --shutdown
wsl
```

## 📊 Monitoring and Maintenance

### Check Resource Usage

```bash
# WSL2 resource usage
wsl --list --verbose

# Docker resource usage
docker stats

# Container logs
docker logs scex1-demo --tail 50 -f
```

### Regular Maintenance

```bash
# Update Ubuntu packages
sudo apt update && sudo apt upgrade -y

# Clean Docker resources
docker system prune -f

# Update Docker images
docker pull nicholaskarlson/scex1-supply-chain:latest
```

## 🎯 Next Steps

After successful setup:

1. **Explore the API**: Use the interactive documentation at `/docs`
2. **Run Custom Optimizations**: Modify parameters in the API calls
3. **View Results**: Download and examine the generated maps and reports
4. **Integrate**: Use the REST API in your own applications
5. **Customize**: Modify the source code for your specific needs

## 📚 Additional Resources

- [Docker Desktop WSL2 Backend](https://docs.docker.com/desktop/windows/wsl/)
- [WSL2 Installation Guide](https://docs.microsoft.com/en-us/windows/wsl/install)
- [Ubuntu on WSL2](https://ubuntu.com/wsl)
- [PyMapGIS Documentation](../../docs/)

## 🆘 Getting Help

If you encounter issues:

1. Check the troubleshooting section above
2. Review Docker Desktop logs
3. Check WSL2 status and logs
4. Consult the main project documentation
5. Report issues with detailed error messages

---

*This guide ensures a smooth setup experience for Windows users wanting to run the Supply Chain Optimization example using modern containerization technologies.*
