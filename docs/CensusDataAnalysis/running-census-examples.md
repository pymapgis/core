# 🚀 Running Census Examples

## Content Outline

Step-by-step guide for end users to run PyMapGIS Census analysis examples:

### 1. Before You Begin
- **System requirements**: Windows 10/11 with WSL2 support
- **Prerequisites checklist**: What you need before starting
- **Time expectations**: How long each step typically takes
- **Backup recommendations**: Protecting your existing work
- **Support resources**: Where to get help if needed

### 2. Quick Start Guide

#### One-Command Launch (Advanced Users)
```bash
# Pull and run the Census analysis example
docker run -p 8888:8888 -p 8501:8501 \
  -v $(pwd)/census-results:/app/results \
  pymapgis/census-analysis:latest
```

#### Beginner-Friendly Approach
```
Step 1: Open Windows Terminal
Step 2: Switch to Ubuntu
Step 3: Navigate to your workspace
Step 4: Run the example
Step 5: Open your web browser
Step 6: Start analyzing!
```

### 3. Detailed Step-by-Step Instructions

#### Step 1: Opening Your Terminal
- **Finding Windows Terminal**: Start menu → "Terminal"
- **Alternative methods**: PowerShell, Command Prompt, or Ubuntu app
- **First-time setup**: What to expect on first launch
- **Troubleshooting**: Common startup issues
- **Keyboard shortcuts**: Useful commands for efficiency

#### Step 2: Switching to Ubuntu
```bash
# In Windows Terminal, switch to Ubuntu
wsl

# Verify you're in Ubuntu
whoami
pwd
```

#### Step 3: Setting Up Your Workspace
```bash
# Create a workspace for your Census analysis
mkdir -p ~/census-analysis
cd ~/census-analysis

# Create directories for results
mkdir -p results data notebooks
```

### 4. Running Different Example Types

#### Basic Demographic Analysis Example
```bash
# Pull the basic example
docker pull pymapgis/census-demographics:latest

# Run with Jupyter notebook interface
docker run -p 8888:8888 \
  -v ~/census-analysis/results:/app/results \
  pymapgis/census-demographics:latest
```

#### Interactive Dashboard Example
```bash
# Pull the dashboard example
docker pull pymapgis/census-dashboard:latest

# Run with Streamlit interface
docker run -p 8501:8501 \
  -v ~/census-analysis/results:/app/results \
  pymapgis/census-dashboard:latest
```

#### Complete Analysis Suite
```bash
# Pull the comprehensive example
docker pull pymapgis/census-complete:latest

# Run with multiple interfaces
docker run -p 8888:8888 -p 8501:8501 \
  -v ~/census-analysis:/app/workspace \
  pymapgis/census-complete:latest
```

### 5. Accessing Your Analysis Environment

#### Jupyter Notebook Access
```
1. Wait for "Server is ready" message
2. Open web browser
3. Go to: http://localhost:8888
4. Enter token if prompted (shown in terminal)
5. Navigate to notebooks folder
6. Open desired analysis notebook
```

#### Streamlit Dashboard Access
```
1. Wait for "You can now view your Streamlit app" message
2. Open web browser
3. Go to: http://localhost:8501
4. Interactive dashboard loads automatically
5. Use sidebar controls to customize analysis
```

### 6. Understanding the Interface

#### Jupyter Notebook Interface
- **File browser**: Navigate between notebooks and data
- **Code cells**: Executable Python code blocks
- **Markdown cells**: Documentation and explanations
- **Output cells**: Results, charts, and maps
- **Kernel controls**: Running, stopping, and restarting

#### Streamlit Dashboard Interface
- **Sidebar controls**: Parameter selection and configuration
- **Main display**: Maps, charts, and analysis results
- **Download buttons**: Export results and visualizations
- **Help sections**: Contextual assistance and documentation
- **Progress indicators**: Analysis status and completion

### 7. Customizing Your Analysis

#### Parameter Modification
```python
# In Jupyter notebooks, modify these parameters:
GEOGRAPHY = "county"        # county, tract, block group
STATE = "06"               # California (FIPS code)
YEAR = 2022               # Analysis year
VARIABLES = [              # Census variables to analyze
    "B01003_001E",        # Total population
    "B19013_001E",        # Median household income
    "B25077_001E"         # Median home value
]
```

#### Geographic Customization
- **State selection**: Choose your state of interest
- **Geography level**: County, tract, or block group
- **Custom boundaries**: Upload your own geographic boundaries
- **Multi-state analysis**: Combine multiple states
- **Metropolitan areas**: Focus on specific urban regions

### 8. Working with Results

#### Understanding Output Files
```
results/
├── data/                 # Processed Census data
├── maps/                 # Generated map visualizations
├── charts/               # Statistical charts and graphs
├── reports/              # Analysis reports and summaries
└── exports/              # Data exports in various formats
```

#### Accessing Results from Windows
```bash
# Your results are automatically saved to:
# Windows path: \\wsl$\Ubuntu\home\username\census-analysis\results
# Or navigate through File Explorer to WSL locations
```

### 9. Common Workflows

#### Basic Demographic Analysis
```
1. Select your geography (state, county, etc.)
2. Choose demographic variables
3. Run the analysis
4. Review population pyramids and maps
5. Export results for presentation
```

#### Housing Affordability Study
```
1. Load housing cost and income data
2. Calculate affordability ratios
3. Create choropleth maps
4. Identify areas of concern
5. Generate policy recommendations
```

#### Economic Development Analysis
```
1. Gather employment and income data
2. Analyze industry composition
3. Identify economic clusters
4. Assess development opportunities
5. Create investment priority maps
```

### 10. Saving and Sharing Your Work

#### Saving Analysis Results
```bash
# Results are automatically saved to your workspace
# To backup to Windows:
cp -r ~/census-analysis/results /mnt/c/Users/YourName/Documents/
```

#### Sharing Your Analysis
- **Export options**: PDF reports, Excel files, image maps
- **Presentation formats**: PowerPoint-ready visualizations
- **Web sharing**: Interactive maps and dashboards
- **Data sharing**: CSV and GeoJSON formats
- **Reproducibility**: Sharing analysis parameters and code

### 11. Troubleshooting Common Issues

#### "Container won't start"
```bash
# Check if Docker is running
docker --version

# Check for port conflicts
netstat -an | grep 8888

# Restart Docker if needed
sudo service docker restart
```

#### "Can't access the web interface"
- **Check the URL**: Ensure correct localhost address
- **Firewall issues**: Windows Defender or antivirus blocking
- **Port conflicts**: Another application using the same port
- **Browser issues**: Try different browser or incognito mode
- **Network problems**: Corporate firewall or proxy issues

#### "Analysis is very slow"
- **Resource allocation**: Increase Docker memory limits
- **Data size**: Start with smaller geographic areas
- **Network speed**: Large data downloads may take time
- **Computer performance**: Close other applications
- **Optimization**: Use pre-processed data when available

### 12. Getting Help and Support

#### Built-in Help Resources
- **Notebook documentation**: Detailed explanations in each notebook
- **Interactive help**: Hover tooltips and help buttons
- **Example data**: Sample datasets for learning
- **Video tutorials**: Step-by-step video guides
- **FAQ sections**: Common questions and answers

#### Community Support
- **GitHub discussions**: Community Q&A and troubleshooting
- **User forums**: Peer support and knowledge sharing
- **Documentation**: Comprehensive online documentation
- **Video tutorials**: YouTube channel with examples
- **Office hours**: Regular community support sessions

### 13. Next Steps and Advanced Usage

#### Expanding Your Analysis
- **Custom data**: Adding your own datasets
- **Advanced statistics**: Spatial regression and modeling
- **Time series**: Multi-year trend analysis
- **Integration**: Connecting with other tools (QGIS, R, etc.)
- **Automation**: Scripting repetitive analyses

#### Learning Path
```
Week 1: Basic demographic analysis
Week 2: Housing and economic analysis
Week 3: Spatial statistics and mapping
Week 4: Custom analysis development
Week 5: Integration with other tools
```

### 14. Best Practices

#### Workflow Organization
- **Project structure**: Consistent folder organization
- **File naming**: Clear and descriptive names
- **Documentation**: Notes about analysis decisions
- **Version control**: Tracking changes and iterations
- **Backup strategy**: Regular backup of important work

#### Analysis Quality
- **Data validation**: Checking data quality and completeness
- **Statistical significance**: Understanding margins of error
- **Visualization quality**: Clear and accurate maps and charts
- **Interpretation**: Proper understanding of results
- **Peer review**: Having others check your work

---

*This guide provides comprehensive, user-friendly instructions for running PyMapGIS Census analysis examples, with focus on supporting non-technical users through the entire process.*
