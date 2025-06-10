# PyMapGIS Universal IO - Usage Examples

## Phase 1 - Part 4 Implementation Complete ✅

The PyMapGIS Universal IO system now fully satisfies all Phase 1 - Part 4 requirements with a single, unified `pmg.read()` interface for all geospatial data formats.

## 1. Vector Data Formats

### Shapefile
```python
import pymapgis as pmg

# Read Shapefile
counties = pmg.read("data/counties.shp")
print(type(counties))  # <class 'geopandas.geodataframe.GeoDataFrame'>
```

### GeoJSON
```python
# Read GeoJSON (local or remote)
boundaries = pmg.read("https://example.com/boundaries.geojson")
local_data = pmg.read("data/features.geojson")
```

### GeoPackage
```python
# Read GeoPackage
buildings = pmg.read("data/buildings.gpkg")

# Read specific layer from GeoPackage
roads = pmg.read("data/infrastructure.gpkg", layer="roads")
```

### Parquet/GeoParquet
```python
# Read GeoParquet
large_dataset = pmg.read("data/large_dataset.parquet")
```

### CSV with Coordinates
```python
# CSV with standard coordinate columns
points = pmg.read("data/locations.csv")  # longitude, latitude columns

# CSV with custom coordinate columns
custom_points = pmg.read("data/custom.csv", x="x_coord", y="y_coord")

# CSV with custom CRS
projected_points = pmg.read("data/utm.csv", crs="EPSG:32633")

# CSV without coordinates (returns DataFrame)
tabular_data = pmg.read("data/attributes.csv")
print(type(tabular_data))  # <class 'pandas.core.frame.DataFrame'>
```

## 2. Raster Data Formats

### GeoTIFF/Cloud Optimized GeoTIFF
```python
# Read GeoTIFF
elevation = pmg.read("data/elevation.tif")
print(type(elevation))  # <class 'xarray.core.dataarray.DataArray'>

# Read COG with chunking for large files
large_raster = pmg.read("data/large_image.cog", chunks={'x': 256, 'y': 256})

# Read specific bands
rgb = pmg.read("data/satellite.tif", band=[1, 2, 3])
```

### NetCDF
```python
# Read NetCDF
climate_data = pmg.read("data/climate.nc")
print(type(climate_data))  # <class 'xarray.core.dataset.Dataset'>

# Read specific variables
temperature = pmg.read("data/weather.nc", group="temperature")
```

## 3. Remote Data Sources

### HTTPS URLs
```python
# Read from web server (automatically cached)
remote_data = pmg.read("https://example.com/data/counties.geojson")

# Subsequent reads use cached version
cached_data = pmg.read("https://example.com/data/counties.geojson")  # Fast!
```

### Amazon S3
```python
# Read from S3 (automatically cached)
s3_data = pmg.read("s3://my-bucket/data/raster.tif")

# With S3 credentials (if needed)
import os
os.environ['AWS_ACCESS_KEY_ID'] = 'your_key'
os.environ['AWS_SECRET_ACCESS_KEY'] = 'your_secret'
s3_secure = pmg.read("s3://private-bucket/data.shp")
```

### Google Cloud Storage
```python
# Read from GCS (automatically cached)
gcs_data = pmg.read("gs://my-bucket/data/boundaries.gpkg")
```

## 4. Caching Configuration

### Configure Cache Directory
```python
import pymapgis as pmg

# Set custom cache directory
pmg.settings.cache_dir = "/path/to/custom/cache"

# Read remote file (cached in custom directory)
data = pmg.read("https://example.com/large_dataset.tif")
```

### Cache Behavior
```python
# First read: downloads and caches
data1 = pmg.read("https://example.com/data.geojson")  # Slow (download)

# Second read: uses cache
data2 = pmg.read("https://example.com/data.geojson")  # Fast (cached)

# Local files are never cached
local_data = pmg.read("local_file.shp")  # Direct access
```

## 5. Advanced Usage and Options

### CSV with Custom Parameters
```python
# CSV with custom encoding
international = pmg.read("data/international.csv", encoding='utf-8')

# CSV with custom separator
european = pmg.read("data/european.csv", sep=';')

# CSV with custom headers
no_header = pmg.read("data/no_header.csv", header=None, names=['lon', 'lat', 'value'])
```

### Raster with Advanced Options
```python
# Read with specific overview level
overview = pmg.read("data/pyramid.tif", overview_level=2)

# Read with custom nodata handling
masked_raster = pmg.read("data/with_nodata.tif", masked=False)

# Read subset of large raster
bbox_raster = pmg.read("data/large.tif", bbox=[xmin, ymin, xmax, ymax])
```

### Vector with Advanced Options
```python
# Read with bounding box filter
clipped = pmg.read("data/large_dataset.shp", bbox=[xmin, ymin, xmax, ymax])

# Read with specific engine
fast_read = pmg.read("data/data.gpkg", engine="pyogrio")

# Read specific columns
minimal = pmg.read("data/attributes.shp", columns=['geometry', 'name'])
```

## 6. Error Handling

### Robust Error Management
```python
try:
    data = pmg.read("nonexistent_file.shp")
except FileNotFoundError as e:
    print(f"File not found: {e}")

try:
    data = pmg.read("data.xyz")  # Unsupported format
except ValueError as e:
    print(f"Unsupported format: {e}")

try:
    data = pmg.read("corrupted_file.tif")
except IOError as e:
    print(f"Read error: {e}")
```

## 7. Integration with PyMapGIS Operations

### Seamless Workflow
```python
# Read data
counties = pmg.read("data/counties.shp")
elevation = pmg.read("data/elevation.tif")

# Use with vector operations
buffered = counties.pmg.buffer(1000)  # Buffer by 1km
clipped = pmg.vector.clip(counties, buffered.geometry.iloc[0])

# Use with raster operations
reprojected = elevation.pmg.reproject("EPSG:3857")
ndvi = elevation.pmg.normalized_difference('nir', 'red')

# Use with visualization
counties.pmg.explore()  # Interactive map
elevation.pmg.map(colormap='terrain')  # Raster visualization
```

## 8. Real-world Examples

### Multi-source Data Integration
```python
# Load data from multiple sources
local_boundaries = pmg.read("data/local_boundaries.shp")
remote_population = pmg.read("https://census.gov/data/population.csv")
satellite_imagery = pmg.read("s3://satellite-data/region.tif")

# Combine and analyze
analysis_ready = local_boundaries.merge(remote_population, on='GEOID')
clipped_imagery = pmg.raster.clip(satellite_imagery, local_boundaries.geometry.iloc[0])
```

### Batch Processing
```python
import glob

# Process multiple files
file_pattern = "data/daily_*.nc"
daily_files = glob.glob(file_pattern)

datasets = []
for file_path in daily_files:
    daily_data = pmg.read(file_path)
    datasets.append(daily_data)

# Combine into time series
import xarray as xr
time_series = xr.concat(datasets, dim='time')
```

## Key Features

✅ **Single Interface**: One function for all geospatial data formats
✅ **Format Detection**: Automatic format detection from file extensions
✅ **Remote Support**: HTTPS, S3, GCS with transparent caching
✅ **Flexible Returns**: Appropriate data types (GeoDataFrame, DataArray, Dataset, DataFrame)
✅ **Error Handling**: Comprehensive error management with helpful messages
✅ **Performance**: Caching for remote files, efficient local access
✅ **Integration**: Seamless integration with PyMapGIS operations and visualization

The Universal IO system makes PyMapGIS a complete solution for geospatial data ingestion, providing a consistent interface regardless of data format or source location.
