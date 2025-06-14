# 🔄 Universal IO System

## Overview

The Universal IO System is the cornerstone of PyMapGIS, providing a unified interface for reading geospatial data from any source through the `pmg.read()` function. This system abstracts away the complexity of different data formats, sources, and protocols behind a simple, consistent API.

## Architecture

### Core Components

```
Universal IO System
├── read() Function           # Main entry point
├── DataSourceRegistry       # Plugin management
├── DataSourcePlugin         # Base plugin class
├── FormatDetector          # Automatic format detection
├── CacheManager            # Intelligent caching
└── URLParser               # URL scheme handling
```

### Data Flow
```
User Request → URL Parsing → Plugin Selection → 
Cache Check → Data Retrieval → Format Processing → 
Validation → Caching → Return GeoDataFrame/DataArray
```

## URL Scheme Architecture

### Supported Schemes
- `census://` - US Census Bureau data (ACS, Decennial)
- `tiger://` - TIGER/Line geographic boundaries
- `file://` - Local file system
- `http://` / `https://` - Remote HTTP resources
- `s3://` - Amazon S3 storage
- `gs://` - Google Cloud Storage
- `azure://` - Azure Blob Storage
- `ftp://` - FTP servers

### URL Structure
```
scheme://[authority]/[path]?[query]#[fragment]

Examples:
census://acs/acs5?year=2022&geography=county&variables=B01003_001E
tiger://county?year=2022&state=06
file://./data/counties.shp
s3://bucket/path/to/data.geojson
```

## Data Source Plugin System

### Plugin Interface
```python
from abc import ABC, abstractmethod
from typing import Union, Dict, Any
import geopandas as gpd
import xarray as xr

class DataSourcePlugin(ABC):
    """Base class for data source plugins."""
    
    @property
    @abstractmethod
    def schemes(self) -> List[str]:
        """URL schemes handled by this plugin."""
        pass
    
    @abstractmethod
    def can_handle(self, url: str) -> bool:
        """Check if plugin can handle the given URL."""
        pass
    
    @abstractmethod
    def read(self, url: str, **kwargs) -> Union[gpd.GeoDataFrame, xr.DataArray]:
        """Read data from the given URL."""
        pass
    
    @abstractmethod
    def get_metadata(self, url: str) -> Dict[str, Any]:
        """Get metadata about the data source."""
        pass
```

### Built-in Plugins

#### 1. Census Plugin (`census://`)
**Purpose**: Access US Census Bureau data

**Features**:
- American Community Survey (ACS) data
- Decennial Census data
- Automatic geometry attachment
- Variable metadata lookup
- Geographic level support

**URL Format**:
```
census://dataset/table?parameters

Examples:
census://acs/acs5?year=2022&geography=county&variables=B01003_001E
census://decennial/pl?year=2020&geography=state&variables=P1_001N
```

**Implementation Details**:
- Uses Census API for data retrieval
- Automatic TIGER/Line geometry joining
- Caches both data and geometry
- Handles API rate limiting
- Provides variable search and metadata

#### 2. TIGER Plugin (`tiger://`)
**Purpose**: Access TIGER/Line geographic boundaries

**Features**:
- County, state, tract boundaries
- Multiple vintage years
- Automatic coordinate system handling
- Simplified and detailed geometries

**URL Format**:
```
tiger://geography?parameters

Examples:
tiger://county?year=2022&state=06
tiger://tract?year=2022&state=06&county=001
```

#### 3. File Plugin (`file://`)
**Purpose**: Read local geospatial files

**Features**:
- Automatic format detection
- Support for all GeoPandas formats
- Raster file support via rioxarray
- Relative and absolute paths

**URL Format**:
```
file://path/to/file

Examples:
file://./data/counties.shp
file:///absolute/path/to/data.geojson
```

#### 4. HTTP Plugin (`http://`, `https://`)
**Purpose**: Read remote geospatial data

**Features**:
- HTTP/HTTPS protocol support
- Automatic format detection
- Response caching
- Authentication support

**URL Format**:
```
https://example.com/path/to/data.format

Examples:
https://example.com/data/counties.geojson
https://api.example.com/data?format=geojson
```

#### 5. Cloud Storage Plugins
**Purpose**: Access cloud-stored geospatial data

**S3 Plugin (`s3://`)**:
```python
# Configuration
pmg.settings.aws_access_key_id = "your_key"
pmg.settings.aws_secret_access_key = "your_secret"

# Usage
data = pmg.read("s3://bucket/path/to/data.geojson")
```

**GCS Plugin (`gs://`)**:
```python
# Configuration
pmg.settings.google_credentials = "path/to/credentials.json"

# Usage
data = pmg.read("gs://bucket/path/to/data.geojson")
```

## Format Detection System

### Automatic Detection
The system automatically detects data formats based on:
1. File extension
2. MIME type (for HTTP sources)
3. Content inspection
4. URL patterns

### Supported Formats

#### Vector Formats
- **GeoJSON** (`.geojson`, `.json`)
- **Shapefile** (`.shp` + supporting files)
- **GeoPackage** (`.gpkg`)
- **KML/KMZ** (`.kml`, `.kmz`)
- **GML** (`.gml`)
- **CSV with coordinates** (`.csv`)

#### Raster Formats
- **GeoTIFF** (`.tif`, `.tiff`)
- **NetCDF** (`.nc`)
- **Zarr** (`.zarr`)
- **HDF5** (`.h5`, `.hdf5`)
- **COG** (Cloud Optimized GeoTIFF)

### Format-Specific Handling
```python
# Vector data returns GeoDataFrame
counties = pmg.read("file://counties.shp")
assert isinstance(counties, gpd.GeoDataFrame)

# Raster data returns DataArray
elevation = pmg.read("file://elevation.tif")
assert isinstance(elevation, xr.DataArray)
```

## Caching System Integration

### Cache Levels
1. **Memory Cache**: Frequently accessed small datasets
2. **Disk Cache**: Downloaded files and processed data
3. **Metadata Cache**: Data source metadata and schemas

### Cache Keys
Cache keys are generated based on:
- URL and parameters
- Data source version/timestamp
- Processing options
- User settings

### Cache Management
```python
import pymapgis as pmg

# Check cache status
stats = pmg.cache.stats()

# Clear specific cache
pmg.cache.clear(pattern="census://*")

# Purge old cache entries
pmg.cache.purge(older_than="7d")
```

## Error Handling

### Exception Hierarchy
```python
class PyMapGISError(Exception):
    """Base exception for PyMapGIS."""
    pass

class DataSourceError(PyMapGISError):
    """Error in data source operations."""
    pass

class FormatError(PyMapGISError):
    """Error in format detection or processing."""
    pass

class CacheError(PyMapGISError):
    """Error in caching operations."""
    pass
```

### Error Recovery
- Automatic retry for transient network errors
- Fallback to alternative data sources
- Graceful degradation for optional features
- Detailed error messages with suggestions

## Performance Optimization

### Lazy Loading
- Plugins loaded only when needed
- Optional dependencies handled gracefully
- Minimal import overhead

### Parallel Processing
- Concurrent downloads for multiple files
- Parallel processing of large datasets
- Async support for I/O operations

### Memory Management
- Streaming for large files
- Chunked processing
- Memory-mapped file access
- Automatic garbage collection

## Extension Points

### Custom Data Source Plugin
```python
from pymapgis.io.base import DataSourcePlugin

class CustomPlugin(DataSourcePlugin):
    @property
    def schemes(self):
        return ["custom"]
    
    def can_handle(self, url):
        return url.startswith("custom://")
    
    def read(self, url, **kwargs):
        # Custom implementation
        return gdf
    
    def get_metadata(self, url):
        return {"source": "custom", "format": "geojson"}

# Register plugin
pmg.io.register_plugin(CustomPlugin())
```

### Custom Format Handler
```python
from pymapgis.io.formats.base import FormatHandler

class CustomFormatHandler(FormatHandler):
    @property
    def extensions(self):
        return [".custom"]
    
    def can_handle(self, path_or_url):
        return path_or_url.endswith(".custom")
    
    def read(self, path_or_url, **kwargs):
        # Custom format reading logic
        return gdf

# Register handler
pmg.io.register_format_handler(CustomFormatHandler())
```

## Configuration

### Settings
```python
import pymapgis as pmg

# Cache configuration
pmg.settings.cache_dir = "./custom_cache"
pmg.settings.cache_ttl = "1d"

# Network configuration
pmg.settings.request_timeout = 30
pmg.settings.max_retries = 3

# Data source configuration
pmg.settings.census_api_key = "your_key"
pmg.settings.default_crs = "EPSG:4326"
```

### Environment Variables
```bash
# Cache settings
export PYMAPGIS_CACHE_DIR="./cache"
export PYMAPGIS_CACHE_TTL="1d"

# API keys
export CENSUS_API_KEY="your_key"

# Network settings
export PYMAPGIS_REQUEST_TIMEOUT="30"
export PYMAPGIS_MAX_RETRIES="3"
```

## Testing

### Unit Tests
- Plugin functionality
- Format detection
- Error handling
- Cache behavior

### Integration Tests
- End-to-end data reading
- Multi-source workflows
- Performance benchmarks
- Error recovery

### Mock Data Sources
```python
from pymapgis.testing import MockDataSource

# Create mock for testing
mock_source = MockDataSource(
    scheme="test",
    data=test_geodataframe
)

with mock_source:
    data = pmg.read("test://sample")
    assert data.equals(test_geodataframe)
```

## Best Practices

### Plugin Development
1. Follow the plugin interface exactly
2. Handle errors gracefully
3. Provide meaningful metadata
4. Support caching when possible
5. Document URL format and parameters

### Performance
1. Use streaming for large datasets
2. Implement proper caching
3. Minimize memory usage
4. Support parallel processing
5. Profile and optimize bottlenecks

### Error Handling
1. Provide clear error messages
2. Include suggestions for fixes
3. Handle edge cases gracefully
4. Log appropriate information
5. Support error recovery

---

*Next: [Vector Operations](./vector-operations.md) for spatial vector processing details*
