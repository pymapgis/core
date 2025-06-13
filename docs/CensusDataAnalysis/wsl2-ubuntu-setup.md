# 🐧 WSL2 and Ubuntu Setup

## Content Outline

Complete guide for Windows users to set up WSL2 with Ubuntu for PyMapGIS Census analysis:

### 1. WSL2 Concepts for Windows Users
- **What is WSL2**: Windows Subsystem for Linux explained simply
- **Why WSL2 for data analysis**: Benefits over native Windows
- **Ubuntu choice**: Why Ubuntu is recommended for PyMapGIS
- **Performance considerations**: Memory, CPU, and storage implications
- **Integration benefits**: Seamless Windows-Linux workflow

### 2. System Requirements and Compatibility
- **Windows version requirements**: Windows 10/11 compatibility
- **Hardware requirements**: CPU, memory, and storage needs
- **Virtualization support**: BIOS/UEFI configuration
- **Hyper-V compatibility**: Understanding conflicts and solutions
- **Performance expectations**: Realistic performance guidelines

### 3. Pre-Installation Checklist
- **System updates**: Ensuring Windows is current
- **Backup recommendations**: Protecting existing data
- **Antivirus considerations**: Compatibility and configuration
- **Disk space planning**: Storage requirements and allocation
- **Network configuration**: Firewall and proxy considerations

### 4. WSL2 Installation Process

#### Step-by-Step Installation
```
Enable WSL Feature → Install WSL2 Kernel → 
Set WSL2 as Default → Install Ubuntu → 
Initial Configuration → Verification
```

#### PowerShell Commands
```powershell
# Enable WSL and Virtual Machine Platform
dism.exe /online /enable-feature /featurename:Microsoft-Windows-Subsystem-Linux /all /norestart
dism.exe /online /enable-feature /featurename:VirtualMachinePlatform /all /norestart

# Set WSL2 as default
wsl --set-default-version 2

# Install Ubuntu
wsl --install -d Ubuntu
```

#### Troubleshooting Common Issues
- **Installation failures**: Error codes and solutions
- **Kernel update issues**: Manual kernel installation
- **Permission problems**: Administrator access requirements
- **Network connectivity**: DNS and proxy configuration
- **Performance issues**: Resource allocation optimization

### 5. Ubuntu Configuration

#### Initial Setup
```
User Account Creation → Password Configuration → 
System Updates → Package Manager Setup → 
Locale Configuration → Time Zone Setup
```

#### Essential Package Installation
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install essential tools
sudo apt install -y curl wget git vim nano

# Install Python development tools
sudo apt install -y python3-pip python3-venv python3-dev

# Install system dependencies for geospatial work
sudo apt install -y build-essential libgdal-dev libproj-dev
```

### 6. Development Environment Setup

#### Python Environment Configuration
```
Python Installation → Virtual Environment → 
Package Management → IDE Integration → 
Jupyter Setup → Testing Validation
```

#### Git Configuration
```bash
# Configure Git
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"

# SSH key generation for GitHub
ssh-keygen -t ed25519 -C "your.email@example.com"
```

### 7. File System Integration

#### Understanding WSL2 File System
- **Linux file system**: /home/username structure
- **Windows integration**: /mnt/c/ access to Windows drives
- **Performance considerations**: Where to store files for best performance
- **Backup strategies**: Protecting WSL2 data
- **File permissions**: Understanding Linux permissions in Windows context

#### Best Practices
```
Project Organization → File Location Strategy → 
Backup Planning → Permission Management → 
Performance Optimization → Cross-Platform Access
```

### 8. Network Configuration

#### Network Setup and Troubleshooting
- **IP address management**: WSL2 networking model
- **Port forwarding**: Accessing services from Windows
- **Firewall configuration**: Windows Defender and WSL2
- **Proxy settings**: Corporate network configuration
- **DNS resolution**: Troubleshooting connectivity issues

#### Docker Network Integration
```
WSL2 Network → Docker Bridge → 
Port Mapping → Service Discovery → 
Security Configuration → Performance Optimization
```

### 9. Performance Optimization

#### Resource Allocation
```
Memory Configuration → CPU Allocation → 
Disk Performance → Network Optimization → 
Monitoring Tools → Performance Tuning
```

#### .wslconfig Configuration
```ini
[wsl2]
memory=8GB
processors=4
swap=2GB
localhostForwarding=true
```

### 10. Integration with Windows Tools

#### VS Code Integration
```
VS Code Installation → WSL Extension → 
Remote Development → File Synchronization → 
Debugging Setup → Terminal Integration
```

#### Windows Terminal Configuration
```
Terminal Installation → Profile Configuration → 
Theme Customization → Keyboard Shortcuts → 
Tab Management → Productivity Features
```

### 11. Backup and Recovery

#### Data Protection Strategies
- **WSL2 distribution backup**: Export and import procedures
- **File-level backup**: Important data protection
- **Configuration backup**: Settings and customizations
- **Recovery procedures**: Disaster recovery planning
- **Migration strategies**: Moving to new systems

#### Backup Commands
```bash
# Export WSL2 distribution
wsl --export Ubuntu C:\backup\ubuntu-backup.tar

# Import WSL2 distribution
wsl --import Ubuntu C:\WSL\Ubuntu C:\backup\ubuntu-backup.tar
```

### 12. Troubleshooting and Support

#### Common Issues and Solutions
- **WSL2 won't start**: Service and configuration issues
- **Performance problems**: Resource allocation and optimization
- **Network connectivity**: DNS and firewall issues
- **File access problems**: Permission and path issues
- **Integration issues**: Windows-Linux interoperability

#### Diagnostic Tools and Commands
```bash
# System information
uname -a
lsb_release -a

# Resource usage
htop
df -h
free -h

# Network diagnostics
ip addr show
ping google.com
```

### 13. Security Considerations

#### Security Best Practices
- **User account security**: Strong passwords and sudo access
- **Network security**: Firewall configuration and port management
- **File permissions**: Proper access control
- **Update management**: Keeping system current
- **Antivirus integration**: Windows Defender and WSL2

#### Security Monitoring
```
Access Logging → Security Updates → 
Vulnerability Scanning → Incident Response → 
Compliance Monitoring → Security Reporting
```

### 14. Advanced Configuration

#### Custom Kernel Configuration
- **Custom kernel compilation**: Advanced users only
- **Module loading**: Additional hardware support
- **Performance tuning**: Kernel parameter optimization
- **Debugging support**: Development environment enhancement
- **Experimental features**: Beta functionality access

#### Enterprise Considerations
- **Group Policy integration**: Corporate environment management
- **Centralized management**: IT administration tools
- **Compliance requirements**: Regulatory considerations
- **Support procedures**: Help desk and user support
- **Deployment automation**: Large-scale rollout strategies

---

*This guide provides comprehensive WSL2 and Ubuntu setup instructions specifically tailored for PyMapGIS Census analysis workflows, with focus on user-friendly explanations and troubleshooting support.*
