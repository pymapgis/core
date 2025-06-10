# PyMapGIS Interactive Maps - Usage Examples

## Phase 1 - Part 3 Implementation Complete ✅

The PyMapGIS visualization module now fully satisfies all Phase 1 - Part 3 requirements with both standalone functions and accessor methods for interactive mapping using Leafmap.

## 1. GeoDataFrame Visualization

### Quick Exploration with .explore()
```python
import pymapgis as pmg

# Load vector data
counties = pmg.read("census://acs/acs5?year=2022&geography=county&variables=B01003_001E")

# Quick exploration with defaults
counties.pmg.explore()

# With custom styling
counties.pmg.explore(
    style={'color': 'blue', 'fillOpacity': 0.3},
    popup=['NAME', 'B01003_001E'],
    layer_name="US Counties"
)
```

### Building Complex Maps with .map()
```python
# Create a map for further customization
m = counties.pmg.map(layer_name="Counties")

# Add basemap and additional layers
m.add_basemap("Satellite")

# Add more data
states = pmg.read("tiger://state?year=2022")
m = states.pmg.map(m=m, layer_name="State Boundaries", style={'color': 'red', 'weight': 2})

# Display the final map
m
```

## 2. Raster Visualization

### DataArray Quick Exploration
```python
# Load raster data
elevation = pmg.read("path/to/elevation.tif")

# Quick exploration
elevation.pmg.explore()

# With custom colormap
elevation.pmg.explore(
    colormap='terrain',
    opacity=0.7,
    layer_name="Elevation"
)
```

### Multi-layer Raster Maps
```python
# Load multiple rasters
temperature = pmg.read("path/to/temperature.tif")
precipitation = pmg.read("path/to/precipitation.tif")

# Build layered map
m = temperature.pmg.map(layer_name="Temperature", colormap="RdYlBu_r")
m = precipitation.pmg.map(m=m, layer_name="Precipitation", colormap="Blues", opacity=0.6)

# Add basemap
m.add_basemap("OpenStreetMap")
m
```

## 3. Dataset Visualization

### Multi-variable Climate Data
```python
# Load climate dataset
climate = pmg.read("path/to/climate_data.nc")

# Explore the dataset
climate.pmg.explore(layer_name="Climate Data")

# Build detailed map
m = climate.pmg.map(layer_name="Climate Variables")
m.add_basemap("Terrain")
m
```

## 4. Combined Vector and Raster Workflows

### Overlay Analysis Visualization
```python
# Load vector boundaries
watersheds = pmg.read("path/to/watersheds.shp")

# Load raster data
landcover = pmg.read("path/to/landcover.tif")

# Create combined visualization
m = landcover.pmg.map(layer_name="Land Cover", colormap="Set3")
m = watersheds.pmg.map(
    m=m, 
    layer_name="Watersheds",
    style={'color': 'black', 'weight': 2, 'fillOpacity': 0}
)

# Add interactive controls
m.add_basemap("Satellite")
m
```

## 5. Real-world Example: Housing Analysis

```python
import pymapgis as pmg

# Load housing cost data
housing = pmg.read("census://acs/acs5?year=2022&geography=county&variables=B25070_010E,B25070_001E")

# Calculate cost burden rate
housing["cost_burden_rate"] = housing["B25070_010E"] / housing["B25070_001E"]

# Create interactive choropleth
m = housing.pmg.explore(
    # Use a column for choropleth coloring (if supported by leafmap)
    popup=["NAME", "cost_burden_rate"],
    tooltip=["NAME", "cost_burden_rate"],
    layer_name="Housing Cost Burden",
    style={'weight': 0.5}
)

# Add context
m.add_basemap("CartoDB.Positron")
m
```

## 6. Integration with Raster Operations

```python
# Load satellite data
landsat = pmg.read("path/to/landsat.tif")

# Calculate NDVI using raster operations
ndvi = landsat.pmg.normalized_difference('nir', 'red')

# Reproject for better visualization
ndvi_web = ndvi.pmg.reproject("EPSG:3857")

# Visualize the result
m = ndvi_web.pmg.explore(
    colormap='RdYlGn',
    layer_name="NDVI",
    opacity=0.8
)

# Add satellite basemap for context
m.add_basemap("Satellite")
m
```

## 7. Standalone Functions (Alternative Interface)

```python
from pymapgis.viz import explore, plot_interactive

# Using standalone functions
counties = pmg.read("tiger://county?year=2022&state=06")

# Quick exploration
explore(counties, layer_name="CA Counties")

# Building maps
m = plot_interactive(counties, layer_name="Counties")
m.add_basemap("OpenStreetMap")
m
```

## Key Features

✅ **Dual Interface**: Both accessor methods (`.pmg.explore()`, `.pmg.map()`) and standalone functions
✅ **Leafmap Integration**: Full integration with leafmap for interactive mapping
✅ **Multi-format Support**: Works with GeoDataFrame, DataArray, and Dataset objects
✅ **Customizable**: Extensive styling and configuration options via kwargs
✅ **Jupyter Ready**: Optimized for Jupyter Notebook/Lab environments
✅ **Layered Maps**: Support for building complex multi-layer visualizations
✅ **Basemap Integration**: Easy addition of various basemap styles

## Method Comparison

| Method | Purpose | Returns | Auto-Display |
|--------|---------|---------|--------------|
| `.pmg.explore()` | Quick exploration | leafmap.Map | Yes (in Jupyter) |
| `.pmg.map()` | Building complex maps | leafmap.Map | No (manual display) |
| `pmg.viz.explore()` | Standalone exploration | leafmap.Map | Yes (in Jupyter) |
| `pmg.viz.plot_interactive()` | Standalone map building | leafmap.Map | No (manual display) |

The PyMapGIS visualization system provides a complete solution for interactive geospatial visualization, making it easy to explore data quickly or build sophisticated multi-layer maps for analysis and presentation.
