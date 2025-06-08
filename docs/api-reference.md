# 🔧 PyMapGIS API Reference

Complete API documentation for PyMapGIS functions, classes, and modules.

## Table of Contents

1. [📖 Core Functions](#-core-functions)
2. [🗺️ Plotting API](#️-plotting-api)
3. [⚡ Cache API](#-cache-api)
4. [⚙️ Settings API](#️-settings-api)
5. [📊 Data Sources](#-data-sources)

## 📖 Core Functions

### `pymapgis.read()`

Universal data reader function that supports multiple data sources through URL-based syntax.

```python
def read(
    url: str,
    cache_ttl: Optional[str] = None,
    **kwargs
) -> gpd.GeoDataFrame
```

**Parameters:**
- `url` (str): Data source URL with protocol-specific syntax
- `cache_ttl` (str, optional): Override default cache TTL for this request
- `**kwargs`: Additional parameters passed to underlying readers

**Returns:**
- `GeoDataFrame`: GeoPandas GeoDataFrame with spatial data

**Supported URL Patterns:**

#### Census ACS Data
```python
# Pattern: census://acs/{product}?{parameters}
pmg.read("census://acs/acs5?year=2022&geography=county&variables=B01003_001E")
```

**Parameters:**
- `product`: ACS product (`acs1`, `acs3`, `acs5`)
- `year`: Data year (2009-2022 for ACS5)
- `geography`: Geographic level (`county`, `state`, `tract`, `block group`)
- `variables`: Comma-separated ACS variable codes
- `state`: Optional state filter (FIPS code or name)

#### TIGER/Line Boundaries
```python
# Pattern: tiger://{geography}?{parameters}
pmg.read("tiger://county?year=2022&state=06")
```

**Parameters:**
- `geography`: Boundary type (`county`, `state`, `tract`, `block`, `place`, `zcta`)
- `year`: Vintage year (2010-2022)
- `state`: Optional state filter (FIPS code or name)

#### Local Files
```python
# Pattern: file://{path}
pmg.read("file://path/to/data.geojson")
```

**Supported formats:** GeoJSON, Shapefile, GeoPackage, KML, and other GeoPandas-supported formats.

**Examples:**
```python
import pymapgis as pmg

# Load Census data with automatic geometry
housing = pmg.read("census://acs/acs5?year=2022&geography=county&variables=B25070_010E,B25070_001E")

# Load geographic boundaries only
counties = pmg.read("tiger://county?year=2022")

# Load local file
local_data = pmg.read("file://./data/my_boundaries.geojson")

# Override cache TTL
fresh_data = pmg.read("census://acs/acs5?year=2022&geography=state&variables=B01003_001E", cache_ttl="1h")
```

## 🗺️ Plotting API

PyMapGIS extends GeoPandas with enhanced plotting capabilities through the `.plot` accessor.

### `.plot.interactive()`

Create a basic interactive map with default styling.

```python
def interactive(
    tiles: str = "OpenStreetMap",
    zoom_start: int = 4,
    **kwargs
) -> leafmap.Map
```

**Parameters:**
- `tiles` (str): Base map tiles (`"OpenStreetMap"`, `"CartoDB positron"`, `"Stamen Terrain"`)
- `zoom_start` (int): Initial zoom level
- `**kwargs`: Additional parameters passed to leafmap

**Returns:**
- `leafmap.Map`: Interactive Leaflet map object

**Example:**
```python
data = pmg.read("tiger://state?year=2022")
data.plot.interactive(tiles="CartoDB positron", zoom_start=3).show()
```

### `.plot.choropleth()`

Create a choropleth (color-coded) map based on data values.

```python
def choropleth(
    column: str,
    title: Optional[str] = None,
    cmap: str = "viridis",
    legend: bool = True,
    tooltip: Optional[List[str]] = None,
    popup: Optional[List[str]] = None,
    style_kwds: Optional[Dict] = None,
    legend_kwds: Optional[Dict] = None,
    tooltip_kwds: Optional[Dict] = None,
    popup_kwds: Optional[Dict] = None,
    **kwargs
) -> leafmap.Map
```

**Parameters:**
- `column` (str): Column name to use for color coding
- `title` (str, optional): Map title
- `cmap` (str): Matplotlib colormap name (default: "viridis")
- `legend` (bool): Whether to show color legend (default: True)
- `tooltip` (List[str], optional): Columns to show in hover tooltip
- `popup` (List[str], optional): Columns to show in click popup
- `style_kwds` (dict, optional): Styling parameters for map features
- `legend_kwds` (dict, optional): Legend customization parameters
- `tooltip_kwds` (dict, optional): Tooltip customization parameters
- `popup_kwds` (dict, optional): Popup customization parameters

**Style Parameters (`style_kwds`):**
- `fillOpacity` (float): Fill transparency (0-1)
- `weight` (float): Border line width
- `color` (str): Border color
- `fillColor` (str): Fill color (overridden by choropleth)

**Legend Parameters (`legend_kwds`):**
- `caption` (str): Legend title
- `max_labels` (int): Maximum number of legend labels
- `orientation` (str): Legend orientation ("vertical" or "horizontal")

**Returns:**
- `leafmap.Map`: Interactive choropleth map

**Examples:**
```python
# Basic choropleth
data.plot.choropleth(column="population", title="Population by County").show()

# Advanced styling
data.plot.choropleth(
    column="median_income",
    title="Median Household Income",
    cmap="RdYlBu_r",
    legend=True,
    tooltip=["NAME", "median_income"],
    popup=["NAME", "median_income", "total_households"],
    style_kwds={
        "fillOpacity": 0.7,
        "weight": 0.5,
        "color": "black"
    },
    legend_kwds={
        "caption": "Median Income ($)",
        "max_labels": 5
    }
).show()
```

## ⚡ Cache API

PyMapGIS provides a caching system for improved performance.

### `pymapgis.cache`

Global cache instance for manual cache operations.

#### `.get(key: str) -> Optional[Any]`

Retrieve a value from cache.

```python
value = pmg.cache.get("my_key")
```

#### `.put(key: str, value: Any, ttl: Optional[str] = None) -> None`

Store a value in cache with optional TTL.

```python
pmg.cache.put("my_key", "my_value", ttl="1h")
```

#### `.clear() -> None`

Clear all cached data.

```python
pmg.cache.clear()
```

#### Properties

- `.size` (int): Number of items in cache
- `.location` (str): Cache database file path

**Example:**
```python
# Check cache status
print(f"Cache has {pmg.cache.size} items")
print(f"Cache location: {pmg.cache.location}")

# Manual cache operations
pmg.cache.put("user_data", {"name": "John"}, ttl="24h")
user_data = pmg.cache.get("user_data")

# Clear cache
pmg.cache.clear()
```

## ⚙️ Settings API

Configuration management through `pymapgis.settings`.

### `pymapgis.settings`

Global settings object with the following attributes:

#### Cache Settings
- `cache_ttl` (str): Default cache time-to-live (default: "24h")
- `disable_cache` (bool): Disable caching entirely (default: False)
- `cache_dir` (str): Cache directory path (default: "./cache")

#### Request Settings
- `request_timeout` (int): HTTP request timeout in seconds (default: 30)
- `user_agent` (str): User agent string for HTTP requests
- `max_retries` (int): Maximum number of request retries (default: 3)

#### Data Source Settings
- `census_year` (int): Default Census data year (default: 2022)
- `census_api_key` (str, optional): Census API key for higher rate limits

**Example:**
```python
import pymapgis as pmg

# View current settings
print(pmg.settings)

# Modify settings
pmg.settings.cache_ttl = "12h"
pmg.settings.request_timeout = 60
pmg.settings.census_year = 2021

# Disable caching
pmg.settings.disable_cache = True
```

### Environment Variables

Settings can be configured via environment variables with `PYMAPGIS_` prefix:

```bash
export PYMAPGIS_CACHE_TTL="24h"
export PYMAPGIS_DISABLE_CACHE="false"
export PYMAPGIS_REQUEST_TIMEOUT="30"
export PYMAPGIS_CENSUS_YEAR="2022"
export PYMAPGIS_CENSUS_API_KEY="your_api_key"
```

## 📊 Data Sources

### Census ACS Variables

Common American Community Survey variable codes:

#### Population & Demographics
- `B01003_001E`: Total population
- `B25001_001E`: Total housing units
- `B08303_001E`: Total commuters

#### Housing
- `B25070_001E`: Total households (for cost burden calculation)
- `B25070_010E`: Households spending 30%+ of income on housing
- `B25077_001E`: Median home value
- `B25064_001E`: Median gross rent

#### Income & Employment
- `B19013_001E`: Median household income
- `B19301_001E`: Per capita income
- `B23025_003E`: Labor force
- `B23025_004E`: Employed population
- `B23025_005E`: Unemployed population

#### Education
- `B15003_022E`: Bachelor's degree
- `B15003_023E`: Master's degree
- `B15003_024E`: Professional degree
- `B15003_025E`: Doctorate degree

### Geographic Codes

#### State FIPS Codes (Common)
- `01`: Alabama
- `06`: California  
- `12`: Florida
- `17`: Illinois
- `36`: New York
- `48`: Texas

#### Geography Levels
- `state`: State boundaries (~50 features)
- `county`: County boundaries (~3,000 features)
- `tract`: Census tract boundaries (~80,000 features)
- `block group`: Block group boundaries (~240,000 features)

## 🔗 Type Hints

PyMapGIS uses comprehensive type hints for better IDE support:

```python
from typing import Optional, List, Dict, Any
import geopandas as gpd
import leafmap

def read(url: str, cache_ttl: Optional[str] = None) -> gpd.GeoDataFrame: ...
def choropleth(column: str, title: Optional[str] = None) -> leafmap.Map: ...
```

## 🚨 Error Handling

Common exceptions and how to handle them:

```python
try:
    data = pmg.read("census://acs/acs5?year=2022&geography=county&variables=INVALID")
except ValueError as e:
    print(f"Invalid parameter: {e}")
except ConnectionError as e:
    print(f"Network error: {e}")
except TimeoutError as e:
    print(f"Request timeout: {e}")
```

---

For more examples and tutorials, see the [User Guide](user-guide.md) and [Examples](examples.md).
