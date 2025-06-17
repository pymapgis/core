# 🪟 WSL2 Setup Guide for PyMapGIS Local Showcases

![WSL2](https://img.shields.io/badge/WSL2-Windows%20Subsystem-blue) ![Ubuntu](https://img.shields.io/badge/Ubuntu-22.04%20LTS-orange)

## 🎯 What is WSL2?

Windows Subsystem for Linux 2 (WSL2) is a compatibility layer that allows you to run Linux environments directly on Windows. For PyMapGIS development, WSL2 provides:

- **🐧 Native Linux Environment**: Full Linux compatibility for geospatial tools
- **🚀 Better Performance**: Near-native Linux performance
- **🔧 Development Tools**: Access to Linux package managers and tools
- **🐳 Docker Integration**: Seamless Docker Desktop integration

## 🛠️ Installing WSL2

### Prerequisites
- **Windows 11** or **Windows 10 version 2004+** (Build 19041+)
- **Administrator privileges** on your Windows machine
- **Virtualization enabled** in BIOS/UEFI

### Step 1: Enable WSL2
```powershell
# Open PowerShell as Administrator and run:

# Enable WSL feature
dism.exe /online /enable-feature /featurename:Microsoft-Windows-Subsystem-Linux /all /norestart

# Enable Virtual Machine Platform
dism.exe /online /enable-feature /featurename:VirtualMachinePlatform /all /norestart

# Restart your computer
shutdown /r /t 0
```

### Step 2: Set WSL2 as Default
```powershell
# After restart, open PowerShell as Administrator:

# Set WSL2 as default version
wsl --set-default-version 2

# Verify WSL installation
wsl --status
```

### Step 3: Install Ubuntu
```powershell
# Install Ubuntu 22.04 LTS (recommended for PyMapGIS)
wsl --install -d Ubuntu-22.04

# Alternative: Install from Microsoft Store
# Search for "Ubuntu 22.04.3 LTS" in Microsoft Store
```

### Step 4: Initial Ubuntu Setup
```bash
# First time setup will prompt for:
# - Username (lowercase, no spaces)
# - Password (for sudo commands)

# Update package lists
sudo apt update && sudo apt upgrade -y

# Install essential development tools
sudo apt install -y curl wget git build-essential
```

## 🚀 Configuring WSL2 for PyMapGIS

### Install Python and Poetry
```bash
# Install Python 3.8+ (required for PyMapGIS)
sudo apt install -y python3 python3-pip python3-venv

# Install Poetry for dependency management
curl -sSL https://install.python-poetry.org | python3 -

# Add Poetry to PATH
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc

# Verify installations
python3 --version
poetry --version
```

### Install Geospatial Dependencies
```bash
# Install GDAL and other geospatial libraries
sudo apt install -y gdal-bin libgdal-dev libproj-dev libgeos-dev

# Install additional Python geospatial dependencies
sudo apt install -y python3-gdal python3-fiona python3-shapely

# Verify GDAL installation
gdalinfo --version
```

### Configure Git
```bash
# Set up Git for PyMapGIS development
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"

# Generate SSH key for GitHub (optional)
ssh-keygen -t ed25519 -C "your.email@example.com"
```

## 🐳 Docker Integration

### Install Docker in WSL2
```bash
# Add Docker's official GPG key
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

# Add Docker repository
echo "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Install Docker
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io

# Add user to docker group
sudo usermod -aG docker $USER

# Start Docker service
sudo service docker start
```

### Docker Desktop Integration (Recommended)
```bash
# 1. Install Docker Desktop for Windows
# Download from: https://www.docker.com/products/docker-desktop

# 2. Enable WSL2 integration in Docker Desktop
# Settings → Resources → WSL Integration → Enable Ubuntu-22.04

# 3. Verify integration
docker --version
docker run hello-world
```

## 📁 File System Integration

### Accessing Windows Files from WSL2
```bash
# Windows C: drive is mounted at /mnt/c
cd /mnt/c/Users/[YourUsername]

# Create a symbolic link for easy access
ln -s /mnt/c/Users/[YourUsername]/Documents ~/windows-docs

# Best practice: Keep projects in WSL2 file system for better performance
mkdir ~/projects
cd ~/projects
```

### Accessing WSL2 Files from Windows
```bash
# From Windows Explorer, navigate to:
\\wsl$\Ubuntu-22.04\home\[username]

# Or use the network path directly:
\\wsl$\Ubuntu-22.04\home\[username]\projects
```

## 🚀 PyMapGIS Development Workflow

### Clone and Setup PyMapGIS
```bash
# Navigate to your projects directory
cd ~/projects

# Clone PyMapGIS repository
git clone https://github.com/pymapgis/core.git
cd core

# Navigate to a local showcase
cd showcaseslocal/open-food-trucks-now

# Install dependencies with Poetry
poetry install

# Run the showcase
poetry run python truck_worker.py
poetry run python app.py
```

### Development Environment
```bash
# Install VS Code Server (automatic when using VS Code)
# Open WSL2 from VS Code: Ctrl+Shift+P → "WSL: Connect to WSL"

# Install useful development tools
sudo apt install -y htop tree jq

# Set up aliases for convenience
echo 'alias ll="ls -la"' >> ~/.bashrc
echo 'alias pymapgis="cd ~/projects/core"' >> ~/.bashrc
source ~/.bashrc
```

## 🔧 Performance Optimization

### WSL2 Configuration
```bash
# Create or edit ~/.wslconfig in Windows home directory
# From WSL2, access Windows home:
cd /mnt/c/Users/[YourUsername]

# Create .wslconfig with optimal settings:
cat > .wslconfig << EOF
[wsl2]
memory=8GB
processors=4
swap=2GB
localhostForwarding=true
EOF
```

### Resource Management
```bash
# Check WSL2 resource usage
wsl --list --verbose

# Restart WSL2 to apply .wslconfig changes
# From PowerShell:
wsl --shutdown
wsl
```

## 🐛 Troubleshooting

### Common WSL2 Issues

#### WSL2 Not Starting
```powershell
# Check WSL status
wsl --status

# Restart WSL
wsl --shutdown
wsl

# Update WSL
wsl --update
```

#### Docker Issues
```bash
# Restart Docker service
sudo service docker restart

# Check Docker status
sudo service docker status

# Test Docker
docker run hello-world
```

#### Network Issues
```bash
# Reset WSL2 network
# From PowerShell as Administrator:
wsl --shutdown
netsh winsock reset
netsh int ip reset all
netsh winhttp reset proxy
ipconfig /flushdns
```

#### Performance Issues
```bash
# Move projects to WSL2 file system
mv /mnt/c/Users/[username]/projects ~/projects

# Use WSL2 file system for better I/O performance
# Avoid cross-file-system operations
```

## 🔒 Security Considerations

### Best Practices
- **Keep WSL2 Updated**: Regular `sudo apt update && sudo apt upgrade`
- **Use SSH Keys**: For secure Git operations
- **Firewall Configuration**: Windows Defender handles WSL2 networking
- **User Permissions**: Don't run as root unnecessarily

### Backup and Recovery
```bash
# Export WSL2 distribution
wsl --export Ubuntu-22.04 ubuntu-backup.tar

# Import WSL2 distribution
wsl --import Ubuntu-22.04-Backup C:\WSL\Ubuntu-Backup ubuntu-backup.tar
```

## 📚 Additional Resources

- **WSL2 Documentation**: https://docs.microsoft.com/en-us/windows/wsl/
- **Ubuntu on WSL**: https://ubuntu.com/wsl
- **Docker Desktop WSL2**: https://docs.docker.com/desktop/windows/wsl/
- **VS Code WSL**: https://code.visualstudio.com/docs/remote/wsl

## 🎯 Next Steps

1. **Install WSL2** using the commands above
2. **Set up Ubuntu** with Python and Poetry
3. **Configure Docker** integration
4. **Clone PyMapGIS** repository
5. **Start developing** local showcases

WSL2 provides the perfect Linux environment for PyMapGIS development on Windows! 🚀
