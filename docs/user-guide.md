# 📖 PyMapGIS User Guide

Welcome to the comprehensive PyMapGIS user guide! This guide covers everything you need to know to become productive with PyMapGIS.

## Table of Contents

1. [🎯 Core Concepts](#-core-concepts)
2. [📊 Data Sources](#-data-sources)
3. [🗺️ Visualization](#️-visualization)
4. [⚡ Caching System](#-caching-system)
5. [🔧 Configuration](#-configuration)
6. [🎨 Advanced Usage](#-advanced-usage)

## 🎯 Core Concepts

### The PyMapGIS Philosophy

PyMapGIS is built around three core principles:

1. **Simplicity**: Complex geospatial workflows should be simple
2. **Performance**: Smart caching and efficient data handling
3. **Interactivity**: Beautiful, interactive maps by default

### Key Components

- **`pmg.read()`**: Universal data reader with URL-based syntax
- **Smart Caching**: Automatic HTTP caching with TTL support
- **Interactive Plotting**: Built-in Leaflet-based visualizations
- **Pandas Integration**: Familiar DataFrame-like operations

## 📊 Data Sources

PyMapGIS supports multiple data sources through a unified URL-based interface.

### Census American Community Survey (ACS)

The ACS provides detailed demographic and economic data for US geographies.

#### Basic Syntax
```python
import pymapgis as pmg

# Basic ACS data request
data = pmg.read("census://acs/acs5?year=2022&geography=county&variables=B25070_001E")
```

#### Parameters
- **`year`**: Data year (2009-2022 for ACS 5-year estimates)
- **`geography`**: Geographic level (`county`, `state`, `tract`, `block group`)
- **`variables`**: Comma-separated list of ACS variable codes
- **`state`**: Optional state filter (FIPS code or abbreviation)

#### Common Variables
```python
# Housing variables
housing_vars = "B25070_001E,B25070_010E"  # Total households, cost burden 30%+

# Labor force variables  
labor_vars = "B23025_003E,B23025_004E"    # Labor force, employed

# Income variables
income_vars = "B19013_001E,B19301_001E"   # Median household income, per capita income

# Population variables
pop_vars = "B01003_001E,B25001_001E"      # Total population, housing units
```

#### Geographic Levels
```python
# County level (default)
counties = pmg.read("census://acs/acs5?year=2022&geography=county&variables=B01003_001E")

# State level
states = pmg.read("census://acs/acs5?year=2022&geography=state&variables=B01003_001E")

# Census tract level (requires state)
tracts = pmg.read("census://acs/acs5?year=2022&geography=tract&state=06&variables=B01003_001E")

# Block group level (requires state)
bg = pmg.read("census://acs/acs5?year=2022&geography=block group&state=06&variables=B01003_001E")
```

### TIGER/Line Geographic Boundaries

TIGER/Line provides geographic boundaries without demographic data.

#### Basic Syntax
```python
# County boundaries
counties = pmg.read("tiger://county?year=2022")

# State boundaries  
states = pmg.read("tiger://state?year=2022")

# Specific state's counties
ca_counties = pmg.read("tiger://county?year=2022&state=06")
```

#### Available Geographies
- `county`: County boundaries
- `state`: State boundaries
- `tract`: Census tract boundaries
- `block`: Census block boundaries
- `place`: Incorporated places
- `zcta`: ZIP Code Tabulation Areas

### Local Files

Load your own geospatial data files.

```python
# GeoJSON files
data = pmg.read("file://path/to/data.geojson")

# Shapefile
data = pmg.read("file://path/to/data.shp")

# Other formats supported by GeoPandas
data = pmg.read("file://path/to/data.gpkg")  # GeoPackage
data = pmg.read("file://path/to/data.kml")   # KML
```

## 🗺️ Visualization

PyMapGIS provides powerful, interactive visualization capabilities built on Leaflet.

### Basic Plotting

```python
import pymapgis as pmg

# Load data
data = pmg.read("census://acs/acs5?year=2022&geography=county&variables=B01003_001E")

# Simple interactive map
data.plot.interactive().show()

# Choropleth map
data.plot.choropleth(column="B01003_001E", title="Population by County").show()
```

### Choropleth Maps

Choropleth maps color-code geographic areas based on data values.

```python
# Basic choropleth
data.plot.choropleth(
    column="population_density",
    title="Population Density by County",
    cmap="viridis"
).show()

# Advanced styling
data.plot.choropleth(
    column="median_income",
    title="Median Household Income",
    cmap="RdYlBu_r",
    legend=True,
    legend_kwds={
        'caption': 'Median Income ($)',
        'max_labels': 5
    },
    style_kwds={
        'fillOpacity': 0.7,
        'weight': 0.5,
        'color': 'black'
    }
).show()
```

### Color Maps

PyMapGIS supports all matplotlib colormaps:

```python
# Sequential colormaps (for continuous data)
"viridis", "plasma", "Blues", "Reds", "YlOrRd"

# Diverging colormaps (for data with meaningful center)
"RdBu", "RdYlBu", "coolwarm", "seismic"

# Qualitative colormaps (for categorical data)
"Set1", "Set2", "tab10", "Pastel1"
```

### Interactive Features

```python
# Add tooltips and popups
data.plot.choropleth(
    column="cost_burden_rate",
    tooltip=['NAME', 'cost_burden_rate'],           # Show on hover
    popup=['NAME', 'total_households', 'burden_30plus'],  # Show on click
    title="Housing Cost Burden"
).show()

# Custom tooltip formatting
data.plot.choropleth(
    column="median_income",
    tooltip=['NAME', 'median_income'],
    tooltip_kwds={'labels': ['County', 'Median Income']},
    popup_kwds={'labels': ['County Name', 'Income ($)']}
).show()
```

## ⚡ Caching System

PyMapGIS includes an intelligent caching system to improve performance and reduce API calls.

### How Caching Works

1. **Automatic**: All HTTP requests are cached automatically
2. **TTL-based**: Cache entries expire after a configurable time
3. **Smart Keys**: Cache keys include all request parameters
4. **SQLite Backend**: Persistent cache stored in SQLite database

### Cache Configuration

```python
import pymapgis as pmg

# Set cache TTL (time-to-live)
pmg.settings.cache_ttl = "24h"   # 24 hours
pmg.settings.cache_ttl = "90m"   # 90 minutes  
pmg.settings.cache_ttl = "7d"    # 7 days
pmg.settings.cache_ttl = 3600    # 3600 seconds

# Disable caching (not recommended)
pmg.settings.disable_cache = True

# Custom cache directory
pmg.settings.cache_dir = "/path/to/custom/cache"
```

### Cache Management

```python
# Clear all cache
pmg.cache.clear()

# Check cache status
print(f"Cache size: {pmg.cache.size}")
print(f"Cache location: {pmg.cache.location}")

# Manual cache operations
pmg.cache.put("key", "value", ttl="1h")
value = pmg.cache.get("key")
```

### TTL Format

PyMapGIS supports flexible TTL formats:

```python
# Time units
"30s"    # 30 seconds
"5m"     # 5 minutes  
"2h"     # 2 hours
"1d"     # 1 day
"1w"     # 1 week

# Combinations
"1h30m"  # 1 hour 30 minutes
"2d12h"  # 2 days 12 hours
```

## 🔧 Configuration

### Settings Overview

PyMapGIS uses Pydantic for configuration management with environment variable support.

```python
import pymapgis as pmg

# View current settings
print(pmg.settings)

# Modify settings
pmg.settings.cache_ttl = "12h"
pmg.settings.request_timeout = 30
pmg.settings.census_year = 2021
```

### Environment Variables

Set configuration via environment variables:

```bash
# Cache settings
export PYMAPGIS_CACHE_TTL="24h"
export PYMAPGIS_DISABLE_CACHE="false"
export PYMAPGIS_CACHE_DIR="/custom/cache/path"

# Request settings  
export PYMAPGIS_REQUEST_TIMEOUT="30"
export PYMAPGIS_USER_AGENT="MyApp/1.0"

# Data source settings
export PYMAPGIS_CENSUS_YEAR="2022"
```

### Configuration File

Create a `pymapgis.toml` configuration file:

```toml
[cache]
ttl = "24h"
disable = false
directory = "./cache"

[requests]
timeout = 30
user_agent = "PyMapGIS/0.1.0"

[census]
default_year = 2022
api_key = "your_census_api_key"  # Optional but recommended
```

## 🎨 Advanced Usage

### Data Processing Workflows

```python
import pymapgis as pmg
import pandas as pd

# Load and process multiple datasets
housing = pmg.read("census://acs/acs5?year=2022&geography=county&variables=B25070_010E,B25070_001E")
income = pmg.read("census://acs/acs5?year=2022&geography=county&variables=B19013_001E")

# Calculate derived metrics
housing["cost_burden_rate"] = housing["B25070_010E"] / housing["B25070_001E"]

# Merge datasets
combined = housing.merge(income, on="GEOID")

# Create multi-variable visualization
combined.plot.choropleth(
    column="cost_burden_rate",
    title="Housing Cost Burden vs Median Income"
).show()
```

### Custom Data Processing

```python
# Filter data
high_burden = data[data["cost_burden_rate"] > 0.3]

# Aggregate by state
state_summary = data.groupby("STATE").agg({
    "B25070_010E": "sum",
    "B25070_001E": "sum"
}).reset_index()

# Calculate state-level rates
state_summary["state_burden_rate"] = state_summary["B25070_010E"] / state_summary["B25070_001E"]
```

### Performance Optimization

```python
# Use appropriate geographic levels
# County level: ~3,000 features (fast)
# Tract level: ~80,000 features (slower)
# Block group level: ~240,000 features (slowest)

# Filter by state for tract/block group level
ca_tracts = pmg.read("census://acs/acs5?year=2022&geography=tract&state=06&variables=B01003_001E")

# Use caching effectively
pmg.settings.cache_ttl = "7d"  # Cache for a week for stable data
```

### Error Handling

```python
try:
    data = pmg.read("census://acs/acs5?year=2022&geography=county&variables=INVALID_VAR")
except ValueError as e:
    print(f"Invalid variable: {e}")
except ConnectionError as e:
    print(f"Network error: {e}")
```

## 🔗 Next Steps

- **[🔧 API Reference](api-reference.md)** - Detailed function documentation
- **[💡 Examples](examples.md)** - Real-world use cases
- **[🤝 Contributing](../CONTRIBUTING.md)** - Help improve PyMapGIS

---

**Happy mapping with PyMapGIS!** 🗺️✨
