# Data Sources and Acquisition Guide

This document explains why large geospatial datasets are not included in the repository and provides comprehensive guidance on acquiring the necessary data for the Oklahoma Economic Indicators example.

## 🚫 Why Data is Not Included in Repository

### Size Constraints
- **County shapefiles**: 50-200 MB per state
- **High-resolution boundaries**: 500 MB - 2 GB
- **Economic time series**: 100-500 MB per dataset
- **Repository size limits**: GitHub recommends <1 GB total

### Licensing Considerations
- **Public domain data**: Freely available but large
- **Commercial datasets**: Cannot redistribute
- **Attribution requirements**: Complex for bundled data
- **Version control**: Binary files don't diff well

### Dynamic Data
- **Census data updates**: Annual releases
- **Economic indicators**: Monthly/quarterly updates
- **Boundary changes**: Periodic redistricting
- **API access**: Real-time data preferred over static files

## 📊 Required Data Sources

### 1. County Boundaries (Required)

**Source**: U.S. Census Bureau TIGER/Line Shapefiles
```
URL: https://www.census.gov/geographies/mapping-files/time-series/geo/tiger-line-file.html
File: tl_2022_us_county.zip (National) or tl_2022_40_county.zip (Oklahoma only)
Size: ~180 MB (National), ~8 MB (Oklahoma)
Format: Shapefile (.shp, .shx, .dbf, .prj)
License: Public Domain
```

**Alternative**: Cartographic Boundary Files (Simplified)
```
URL: https://www.census.gov/geographies/mapping-files/time-series/geo/carto-boundary-file.html
File: cb_2022_us_county_500k.zip
Size: ~25 MB (National)
Format: Shapefile
Advantage: Smaller file size, faster rendering
```

### 2. Economic Data (Fetched via API)

**Source**: U.S. Census Bureau American Community Survey (ACS)
```
API Endpoint: https://api.census.gov/data/2022/acs/acs5
Variables: B19013_001E (Median household income)
Geographic Level: County
State Filter: 40 (Oklahoma FIPS code)
License: Public Domain
```

**API Key**: Required for production use
```
Registration: https://api.census.gov/data/key_signup.html
Rate Limits: 500 requests per IP per day (without key)
Rate Limits: 50,000 requests per day (with key)
```

## 🔄 Data Acquisition Workflow

### Step 1: Download County Boundaries
```bash
# Create data directory
mkdir -p data/counties

# Download Oklahoma counties (recommended)
wget https://www2.census.gov/geo/tiger/TIGER2022/COUNTY/tl_2022_40_county.zip
unzip tl_2022_40_county.zip -d data/counties/

# OR download national counties (if analyzing multiple states)
wget https://www2.census.gov/geo/tiger/TIGER2022/COUNTY/tl_2022_us_county.zip
unzip tl_2022_us_county.zip -d data/counties/
```

### Step 2: Verify Data Structure
```python
import geopandas as gpd

# Load and inspect county data
counties = gpd.read_file("data/counties/tl_2022_40_county.shp")
print(f"Columns: {counties.columns.tolist()}")
print(f"CRS: {counties.crs}")
print(f"Counties: {len(counties)}")

# Check for Oklahoma (should be 77 counties)
assert len(counties) == 77, "Oklahoma should have 77 counties"
```

### Step 3: Get Census API Key (Optional but Recommended)
```
1. Visit: https://api.census.gov/data/key_signup.html
2. Fill out registration form
3. Receive key via email
4. Set environment variable: export CENSUS_API_KEY="your_key_here"
```

### Step 4: Test Data Integration
```python
# Test the complete workflow
import pymapgis as pmg

# Fetch economic data
oklahoma_data = pmg.get_county_table(2022, ["B19013_001E"], state="40")

# Load boundaries
counties = gpd.read_file("data/counties/tl_2022_40_county.shp")

# Verify join compatibility
print(f"Data GEOID format: {oklahoma_data['geoid'].iloc[0]}")
print(f"Shapefile GEOID format: {counties['GEOID'].iloc[0]}")
```

## 🌐 Alternative Data Sources

### Oklahoma-Specific Sources

**Oklahoma Department of Commerce**
```
URL: https://www.okcommerce.gov/data-research/
Data: Economic development indicators
Format: Excel, CSV
Update: Annual
```

**Oklahoma Employment Security Commission**
```
URL: https://www.ok.gov/oesc/
Data: Labor force statistics, unemployment rates
Format: Excel, PDF reports
Update: Monthly
```

**Federal Reserve Bank of Kansas City**
```
URL: https://www.kansascityfed.org/research/regional-economy/
Data: Regional economic indicators
Format: Excel, interactive dashboards
Update: Quarterly
```

### National Economic Data

**Bureau of Economic Analysis (BEA)**
```
URL: https://www.bea.gov/data/gdp/gdp-county-metro-and-other-areas
Data: GDP by county, personal income
API: https://apps.bea.gov/api/
Format: JSON, CSV
Update: Annual
```

**Bureau of Labor Statistics (BLS)**
```
URL: https://www.bls.gov/data/
Data: Employment, wages, prices
API: https://www.bls.gov/developers/
Format: JSON, Excel
Update: Monthly/Quarterly
```

## 🛠️ Data Processing Scripts

### Automated Download Script
```python
#!/usr/bin/env python3
"""
download_oklahoma_data.py
Automated script to download required geospatial data
"""

import os
import requests
import zipfile
from pathlib import Path

def download_county_boundaries():
    """Download Oklahoma county boundaries from Census Bureau."""
    
    # Create data directory
    data_dir = Path("data/counties")
    data_dir.mkdir(parents=True, exist_ok=True)
    
    # Download URL
    url = "https://www2.census.gov/geo/tiger/TIGER2022/COUNTY/tl_2022_40_county.zip"
    zip_path = data_dir / "tl_2022_40_county.zip"
    
    print(f"Downloading Oklahoma county boundaries...")
    
    # Download file
    response = requests.get(url, stream=True)
    response.raise_for_status()
    
    with open(zip_path, 'wb') as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)
    
    # Extract files
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(data_dir)
    
    # Clean up zip file
    zip_path.unlink()
    
    print(f"✓ County boundaries saved to {data_dir}")

if __name__ == "__main__":
    download_county_boundaries()
```

### Data Validation Script
```python
#!/usr/bin/env python3
"""
validate_data.py
Validate downloaded data integrity and compatibility
"""

import geopandas as gpd
import pandas as pd
from pathlib import Path

def validate_county_data():
    """Validate Oklahoma county boundary data."""
    
    shapefile_path = Path("data/counties/tl_2022_40_county.shp")
    
    if not shapefile_path.exists():
        raise FileNotFoundError(f"County shapefile not found: {shapefile_path}")
    
    # Load and validate
    counties = gpd.read_file(shapefile_path)
    
    # Check county count
    assert len(counties) == 77, f"Expected 77 counties, found {len(counties)}"
    
    # Check required columns
    required_cols = ['GEOID', 'NAME', 'STATEFP', 'COUNTYFP']
    missing_cols = [col for col in required_cols if col not in counties.columns]
    assert not missing_cols, f"Missing columns: {missing_cols}"
    
    # Check state FIPS
    assert counties['STATEFP'].iloc[0] == '40', "Not Oklahoma data (STATEFP != 40)"
    
    # Check CRS
    assert counties.crs is not None, "No coordinate reference system defined"
    
    print("✓ County data validation passed")
    return counties

if __name__ == "__main__":
    validate_county_data()
```

## 📋 Data Management Best Practices

### Directory Structure
```
oklahoma_economic_indicators/
├── data/
│   ├── counties/           # County boundary shapefiles
│   ├── economic/          # Downloaded economic datasets
│   └── processed/         # Cleaned and processed data
├── outputs/
│   ├── maps/             # Generated map images
│   ├── tables/           # Summary statistics
│   └── exports/          # Data exports for QGIS
└── scripts/
    ├── download_data.py  # Data acquisition
    ├── process_data.py   # Data cleaning
    └── validate_data.py  # Quality checks
```

### Version Control
```
# Add to .gitignore
data/raw/
data/counties/*.shp
data/counties/*.dbf
data/counties/*.shx
data/counties/*.prj
outputs/maps/*.png
outputs/exports/*.geojson

# Track only
data/README.md
scripts/
*.py
*.md
requirements.txt
```

### Documentation
```
# Always document:
- Data source URLs and access dates
- Processing steps and transformations
- Known data quality issues
- Update schedules and procedures
- Contact information for data providers
```

## 🔍 Quality Assurance

### Data Validation Checklist
- [ ] Correct number of counties (77 for Oklahoma)
- [ ] Valid coordinate reference system
- [ ] No missing geometries
- [ ] Consistent GEOID format
- [ ] Economic data within reasonable ranges
- [ ] No duplicate records
- [ ] Proper null value handling

### Regular Updates
- [ ] Check for new ACS data releases (annual)
- [ ] Update county boundaries if redistricting occurs
- [ ] Validate API endpoints and parameters
- [ ] Test data processing pipeline
- [ ] Update documentation and examples

---

*This guide ensures reproducible data acquisition and processing workflows while explaining why large datasets are not included in the repository.*
