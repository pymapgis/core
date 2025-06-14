# 🚀 Running Logistics Examples

## Step-by-Step Guide for End Users

This comprehensive guide provides detailed instructions for running PyMapGIS logistics and supply chain examples, designed for users with varying technical backgrounds.

### 1. Quick Start for Beginners

#### One-Command Launch
```bash
# Download and run the complete logistics suite
curl -sSL https://get.pymapgis.com/logistics | bash
```

#### What This Does
- Downloads the latest PyMapGIS logistics containers
- Sets up the complete environment automatically
- Launches all necessary services
- Opens your web browser to the main interface
- Provides sample data for immediate analysis

### 2. Prerequisites Check

#### System Requirements Verification
```bash
# Check Windows version (run in PowerShell)
Get-ComputerInfo | Select WindowsProductName, WindowsVersion

# Check WSL2 status
wsl --status

# Check Docker installation
docker --version
docker-compose --version

# Check available resources
wsl -l -v
```

#### Required Resources
- **Memory**: 8GB RAM minimum (16GB recommended)
- **Storage**: 10GB free space minimum (20GB recommended)
- **Network**: Broadband internet connection
- **Ports**: 8000, 8501, 8888 available

### 3. Step-by-Step Manual Setup

#### Step 1: Prepare Your Environment
```bash
# Open Windows Terminal and switch to Ubuntu
wsl

# Create workspace directory
mkdir -p ~/logistics-examples
cd ~/logistics-examples

# Verify Docker is running
docker ps
```

#### Step 2: Download Example Configurations
```bash
# Download example configurations
curl -O https://raw.githubusercontent.com/pymapgis/examples/main/logistics/docker-compose.yml
curl -O https://raw.githubusercontent.com/pymapgis/examples/main/logistics/.env.example

# Copy environment template
cp .env.example .env

# Edit configuration if needed
nano .env
```

#### Step 3: Launch the Logistics Suite
```bash
# Pull latest images
docker-compose pull

# Start all services
docker-compose up -d

# Check service status
docker-compose ps
```

#### Step 4: Verify Installation
```bash
# Wait for services to start (about 2-3 minutes)
sleep 180

# Check service health
curl http://localhost:8000/health
curl http://localhost:8501/health
curl http://localhost:8888/api/status
```

### 4. Accessing Your Logistics Environment

#### Web Interfaces Overview
```
Main Dashboard:     http://localhost:8501
Jupyter Notebooks: http://localhost:8888
API Documentation: http://localhost:8000/docs
Monitoring:        http://localhost:3000 (if enabled)
```

#### First-Time Access
1. **Open your web browser**
2. **Navigate to http://localhost:8501** (Main Dashboard)
3. **Wait for the interface to load** (may take 30-60 seconds)
4. **Click "Get Started" or "Load Sample Data"**
5. **Follow the guided tour**

### 5. Example Categories and Usage

#### Route Optimization Examples

**Basic Route Optimization**
```bash
# Access via dashboard or Jupyter
# Navigate to: Examples > Route Optimization > Basic Delivery Routes

# Or run directly:
docker exec logistics-core python -c "
import pymapgis as pmg
example = pmg.examples.load('route_optimization_basic')
example.run()
example.visualize()
"
```

**Advanced Multi-Vehicle Routing**
```bash
# Navigate to: Examples > Route Optimization > Multi-Vehicle Fleet

# Parameters you can adjust:
# - Number of vehicles: 2-10
# - Vehicle capacity: 1000-5000 kg
# - Time windows: Flexible or strict
# - Optimization objective: Cost, time, or distance
```

#### Facility Location Examples

**Warehouse Location Analysis**
```bash
# Navigate to: Examples > Facility Location > Warehouse Optimization

# This example demonstrates:
# - Market demand analysis
# - Transportation cost modeling
# - Site selection optimization
# - Service area analysis
```

**Distribution Network Design**
```bash
# Navigate to: Examples > Facility Location > Distribution Network

# Features:
# - Multi-tier network design
# - Hub-and-spoke optimization
# - Cross-docking analysis
# - Cost-benefit evaluation
```

#### Supply Chain Analytics Examples

**Demand Forecasting**
```bash
# Navigate to: Examples > Analytics > Demand Forecasting

# Includes:
# - Historical data analysis
# - Seasonal pattern detection
# - Machine learning forecasts
# - Accuracy assessment
```

**Inventory Optimization**
```bash
# Navigate to: Examples > Analytics > Inventory Management

# Covers:
# - ABC analysis
# - Safety stock calculation
# - Reorder point optimization
# - Cost minimization
```

### 6. Working with Your Own Data

#### Data Upload Process
1. **Navigate to the Data Upload section** in the dashboard
2. **Choose your data format**: CSV, Excel, or GeoJSON
3. **Map your columns** to the required fields
4. **Preview and validate** your data
5. **Upload and process** the data

#### Supported Data Formats

**Customer/Delivery Locations**
```csv
# customers.csv
customer_id,name,address,latitude,longitude,demand
CUST001,ABC Company,123 Main St,40.7128,-74.0060,500
CUST002,XYZ Corp,456 Oak Ave,40.7589,-73.9851,750
```

**Vehicle Information**
```csv
# vehicles.csv
vehicle_id,type,capacity_kg,capacity_m3,fuel_type
VEH001,truck,5000,25,diesel
VEH002,van,2000,12,electric
```

**Facility Data**
```csv
# facilities.csv
facility_id,name,type,address,latitude,longitude,capacity
FAC001,Main Warehouse,warehouse,789 Industrial Blvd,40.6892,-74.0445,10000
FAC002,Distribution Center,distribution,321 Commerce St,40.7484,-73.9857,5000
```

### 7. Customizing Examples

#### Parameter Adjustment
Most examples allow you to customize:

**Route Optimization Parameters**
- **Vehicle capacity**: Adjust based on your fleet
- **Time windows**: Set delivery time constraints
- **Service time**: Time spent at each location
- **Maximum route duration**: Daily driving limits
- **Cost factors**: Fuel, labor, vehicle costs

**Facility Location Parameters**
- **Demand weights**: Importance of different customers
- **Distance limits**: Maximum service radius
- **Capacity constraints**: Facility size limitations
- **Cost factors**: Land, construction, operational costs

#### Advanced Customization
```python
# Example: Custom route optimization
import pymapgis as pmg

# Load your data
customers = pmg.read_csv('my_customers.csv')
vehicles = pmg.read_csv('my_vehicles.csv')

# Customize optimization parameters
optimizer = pmg.RouteOptimizer(
    max_route_duration=8*60,  # 8 hours in minutes
    service_time=15,          # 15 minutes per stop
    vehicle_speed=50,         # 50 km/h average speed
    cost_per_km=0.50,        # $0.50 per kilometer
    cost_per_hour=25.00      # $25 per hour labor
)

# Run optimization
routes = optimizer.optimize(customers, vehicles)

# Visualize results
routes.explore(
    column='total_cost',
    scheme='quantiles',
    legend=True
)
```

### 8. Understanding Results

#### Route Optimization Results
- **Route maps**: Visual representation of optimized routes
- **Performance metrics**: Distance, time, cost savings
- **Delivery schedules**: Optimized sequence and timing
- **Vehicle utilization**: Capacity and time usage
- **Cost breakdown**: Detailed cost analysis

#### Facility Location Results
- **Recommended locations**: Top-ranked sites with scores
- **Service areas**: Geographic coverage analysis
- **Cost analysis**: Total cost of ownership comparison
- **Accessibility metrics**: Transportation connectivity
- **Market coverage**: Customer demand satisfaction

#### Analytics Results
- **Forecasts**: Predicted demand with confidence intervals
- **Trends**: Historical patterns and seasonality
- **Optimization recommendations**: Actionable insights
- **Performance indicators**: Key metrics and benchmarks
- **What-if scenarios**: Alternative strategy comparisons

### 9. Exporting and Sharing Results

#### Export Options
```python
# Export route optimization results
routes.to_csv('optimized_routes.csv')
routes.to_excel('route_analysis.xlsx')
routes.to_geojson('routes.geojson')

# Export maps and visualizations
route_map.save('route_map.html')
route_map.save('route_map.png', width=1200, height=800)

# Generate PDF report
pmg.generate_report(
    results=routes,
    template='route_optimization',
    output='route_report.pdf'
)
```

#### Sharing with Stakeholders
1. **Interactive maps**: Share HTML files for web viewing
2. **PDF reports**: Professional summaries for executives
3. **Excel files**: Detailed data for further analysis
4. **PowerPoint slides**: Ready-to-present visualizations
5. **API endpoints**: Real-time data access for systems

### 10. Troubleshooting Common Issues

#### Services Won't Start
```bash
# Check Docker status
docker ps -a

# View service logs
docker-compose logs logistics-core
docker-compose logs logistics-dashboard

# Restart services
docker-compose restart

# Full reset if needed
docker-compose down
docker-compose up -d
```

#### Can't Access Web Interface
```bash
# Check port availability
netstat -an | grep 8501
netstat -an | grep 8888

# Check Windows firewall
# Windows Security > Firewall & network protection
# Allow Docker Desktop through firewall

# Try different browser or incognito mode
```

#### Data Upload Issues
- **File format**: Ensure CSV/Excel files are properly formatted
- **Column names**: Match required field names exactly
- **Data validation**: Check for missing or invalid values
- **File size**: Large files may take time to process
- **Encoding**: Use UTF-8 encoding for special characters

#### Performance Issues
```bash
# Check resource usage
docker stats

# Increase WSL2 memory allocation
# Edit ~/.wslconfig:
[wsl2]
memory=12GB
processors=6

# Restart WSL2
wsl --shutdown
```

### 11. Getting Help and Support

#### Built-in Help Resources
- **Interactive tutorials**: Step-by-step guided examples
- **Help tooltips**: Hover over interface elements
- **Documentation links**: Context-sensitive help
- **Video tutorials**: Visual learning resources
- **FAQ section**: Common questions and answers

#### Community Support
- **User forums**: https://community.pymapgis.com
- **GitHub discussions**: Technical questions and issues
- **Stack Overflow**: Tag questions with 'pymapgis'
- **LinkedIn group**: Professional networking and tips
- **YouTube channel**: Tutorial videos and webinars

#### Professional Support
- **Email support**: support@pymapgis.com
- **Live chat**: Available during business hours
- **Training sessions**: Scheduled group or individual training
- **Consulting services**: Custom implementation assistance
- **Enterprise support**: Dedicated support for organizations

### 12. Next Steps and Advanced Usage

#### Skill Development Path
```
Week 1: Basic examples and interface familiarization
Week 2: Data upload and customization
Week 3: Advanced parameters and optimization
Week 4: Custom analysis and reporting
Week 5: Integration with existing systems
```

#### Advanced Features
- **API integration**: Connect to existing business systems
- **Custom algorithms**: Implement specialized optimization
- **Real-time processing**: Live GPS and sensor data
- **Machine learning**: Advanced predictive analytics
- **Multi-user collaboration**: Team-based analysis

#### Business Integration
- **ERP connectivity**: SAP, Oracle, Microsoft Dynamics
- **BI tools**: Tableau, Power BI, QlikView
- **GIS systems**: ArcGIS, QGIS integration
- **Fleet management**: Telematics and GPS systems
- **E-commerce platforms**: Shopify, Magento, WooCommerce

---

*This comprehensive guide ensures successful execution of PyMapGIS logistics examples with clear instructions for users of all technical levels.*
