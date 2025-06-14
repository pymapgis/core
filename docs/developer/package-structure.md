# 📦 Package Structure

## Overview

This document provides a detailed breakdown of PyMapGIS's package structure, explaining the purpose and contents of each module, submodule, and key files.

## Root Package Structure

```
pymapgis/
├── __init__.py                 # Main API surface and lazy imports
├── settings.py                 # Global settings and configuration
├── cache.py                    # Legacy cache utilities
├── plotting.py                 # Legacy plotting functions
├── acs.py                      # American Community Survey utilities
├── tiger.py                    # TIGER/Line data utilities
├── cli.py                      # Legacy CLI entry point
├── serve.py                    # Legacy serve functionality
└── [modules]/                  # Core module directories
```

## Core Modules

### 1. IO Module (`pymapgis/io/`)
**Purpose**: Universal data reading and format handling

```
io/
├── __init__.py                 # Main read() function and registry
├── base.py                     # Base classes and interfaces
├── registry.py                 # Data source plugin registry
├── formats/                    # Format-specific handlers
│   ├── __init__.py
│   ├── geojson.py             # GeoJSON format handler
│   ├── shapefile.py           # Shapefile format handler
│   ├── geopackage.py          # GeoPackage format handler
│   └── raster.py              # Raster format handlers
├── sources/                    # Data source implementations
│   ├── __init__.py
│   ├── census.py              # Census API integration
│   ├── tiger.py               # TIGER/Line data source
│   ├── file.py                # Local file data source
│   ├── http.py                # HTTP/URL data source
│   └── cloud.py               # Cloud storage data sources
└── utils.py                    # IO utility functions
```

**Key Components**:
- `read()` - Main entry point for data reading
- `DataSourceRegistry` - Plugin management system
- `DataSourcePlugin` - Base class for custom sources
- Format detection and handling
- URL parsing and routing

### 2. Vector Module (`pymapgis/vector/`)
**Purpose**: Vector spatial operations and GeoPandas integration

```
vector/
├── __init__.py                 # Core vector operations
├── operations.py               # Spatial operation implementations
├── accessors.py                # GeoDataFrame accessor methods
├── geoarrow_utils.py          # GeoArrow integration utilities
├── spatial_index.py           # Spatial indexing optimizations
└── utils.py                    # Vector utility functions
```

**Key Components**:
- `clip()`, `buffer()`, `overlay()`, `spatial_join()` - Core operations
- `.pmg` accessor for GeoDataFrames
- GeoArrow integration for performance
- Spatial indexing for optimization

### 3. Raster Module (`pymapgis/raster/`)
**Purpose**: Raster processing and xarray integration

```
raster/
├── __init__.py                 # Core raster operations
├── operations.py               # Raster operation implementations
├── accessors.py                # DataArray accessor methods
├── cog.py                      # Cloud Optimized GeoTIFF utilities
├── zarr_utils.py              # Zarr format utilities
├── reprojection.py            # Coordinate system transformations
└── utils.py                    # Raster utility functions
```

**Key Components**:
- `reproject()`, `normalized_difference()` - Core operations
- `.pmg` accessor for DataArrays
- COG and Zarr format support
- Dask integration for large datasets

### 4. Visualization Module (`pymapgis/viz/`)
**Purpose**: Interactive mapping and visualization

```
viz/
├── __init__.py                 # Main visualization functions
├── accessors.py                # Accessor methods for mapping
├── leafmap_integration.py      # Leafmap backend integration
├── styling.py                  # Styling and symbology
├── exports.py                  # Export functionality
└── utils.py                    # Visualization utilities
```

**Key Components**:
- `.map()` and `.explore()` accessor methods
- Leafmap integration for interactive maps
- Styling engine for cartographic control
- Export capabilities (PNG, HTML, etc.)

### 5. Serve Module (`pymapgis/serve/`)
**Purpose**: Web services and tile serving

```
serve/
├── __init__.py                 # Main serve() function
├── app.py                      # FastAPI application factory
├── tiles/                      # Tile generation
│   ├── __init__.py
│   ├── xyz.py                 # XYZ tile service
│   ├── wms.py                 # WMS service
│   └── mvt.py                 # Vector tile (MVT) service
├── middleware.py              # Custom middleware
├── auth.py                    # Service authentication
└── utils.py                   # Service utilities
```

**Key Components**:
- `serve()` function as main entry point
- FastAPI-based web services
- XYZ, WMS, and MVT tile services
- Authentication and middleware support

### 6. CLI Module (`pymapgis/cli/`)
**Purpose**: Command-line interface

```
cli/
├── __init__.py                 # CLI app and imports
├── main.py                     # Main Typer application
├── commands/                   # Command implementations
│   ├── __init__.py
│   ├── info.py                # System information commands
│   ├── cache.py               # Cache management commands
│   ├── rio.py                 # Rasterio CLI passthrough
│   └── serve.py               # Service commands
└── utils.py                   # CLI utilities
```

**Key Components**:
- Typer-based CLI framework
- `pymapgis info`, `pymapgis cache`, `pymapgis rio` commands
- Extensible command structure
- Rich output formatting

## Advanced Modules

### 7. Authentication Module (`pymapgis/auth/`)
**Purpose**: Enterprise authentication and security

```
auth/
├── __init__.py                 # Main auth exports
├── api_keys.py                # API key management
├── oauth.py                   # OAuth providers
├── rbac.py                    # Role-based access control
├── sessions.py                # Session management
├── security.py               # Security utilities
├── middleware.py              # Authentication middleware
└── providers/                 # OAuth provider implementations
    ├── __init__.py
    ├── google.py              # Google OAuth
    ├── microsoft.py           # Microsoft OAuth
    └── github.py              # GitHub OAuth
```

### 8. Cloud Module (`pymapgis/cloud/`)
**Purpose**: Cloud storage and processing integration

```
cloud/
├── __init__.py                 # Main cloud functions
├── storage.py                 # Cloud storage abstraction
├── providers/                 # Cloud provider implementations
│   ├── __init__.py
│   ├── aws.py                 # AWS S3 integration
│   ├── gcp.py                 # Google Cloud Storage
│   └── azure.py               # Azure Blob Storage
├── processing.py              # Cloud processing utilities
└── utils.py                   # Cloud utilities
```

### 9. Streaming Module (`pymapgis/streaming/`)
**Purpose**: Real-time data processing

```
streaming/
├── __init__.py                 # Main streaming exports
├── kafka_integration.py       # Apache Kafka integration
├── mqtt_integration.py        # MQTT integration
├── processors.py              # Stream processing utilities
├── buffers.py                 # Data buffering strategies
└── utils.py                   # Streaming utilities
```

### 10. Machine Learning Module (`pymapgis/ml/`)
**Purpose**: Spatial ML and analytics

```
ml/
├── __init__.py                 # Main ML exports
├── features.py                # Spatial feature engineering
├── sklearn_integration.py     # Scikit-learn integration
├── spatial_algorithms.py      # Spatial ML algorithms
├── evaluation.py              # Model evaluation
├── preprocessing.py           # Data preprocessing
└── pipelines.py               # ML pipeline utilities
```

### 11. Network Module (`pymapgis/network/`)
**Purpose**: Network analysis and routing

```
network/
├── __init__.py                 # Main network exports
├── graph.py                   # Graph construction
├── routing.py                 # Routing algorithms
├── analysis.py                # Network analysis
├── osm_integration.py         # OpenStreetMap integration
└── utils.py                   # Network utilities
```

### 12. Point Cloud Module (`pymapgis/pointcloud/`)
**Purpose**: 3D point cloud processing

```
pointcloud/
├── __init__.py                 # Main point cloud exports
├── pdal_integration.py        # PDAL integration
├── processing.py              # Point cloud processing
├── visualization.py           # 3D visualization
├── formats.py                 # Format handling (LAS, LAZ, etc.)
└── utils.py                   # Point cloud utilities
```

## Infrastructure Modules

### 13. Cache Module (`pymapgis/cache/`)
**Purpose**: Intelligent caching system

```
cache/
├── __init__.py                 # Main cache functions
├── manager.py                 # Cache management
├── backends/                  # Cache backend implementations
│   ├── __init__.py
│   ├── memory.py              # In-memory caching
│   ├── disk.py                # Disk-based caching
│   └── redis.py               # Redis caching
├── strategies.py              # Caching strategies
└── utils.py                   # Cache utilities
```

### 14. Settings Module (`pymapgis/settings/`)
**Purpose**: Configuration management

```
settings/
├── __init__.py                 # Settings exports
├── config.py                  # Configuration classes
├── validation.py              # Settings validation
├── defaults.py                # Default configurations
└── utils.py                   # Settings utilities
```

### 15. Plugins Module (`pymapgis/plugins/`)
**Purpose**: Plugin system and extensions

```
plugins/
├── __init__.py                 # Plugin system exports
├── registry.py                # Plugin registry
├── base.py                    # Base plugin classes
├── loader.py                  # Plugin loading utilities
├── discovery.py               # Plugin discovery
└── examples/                  # Example plugins
    ├── __init__.py
    └── sample_plugin.py       # Sample plugin implementation
```

## Deployment and Testing Modules

### 16. Deployment Module (`pymapgis/deployment/`)
**Purpose**: Deployment utilities and configurations

```
deployment/
├── __init__.py                 # Deployment exports
├── docker.py                  # Docker utilities
├── kubernetes.py              # Kubernetes configurations
├── cloud_deploy.py            # Cloud deployment
├── monitoring.py              # Monitoring setup
└── utils.py                   # Deployment utilities
```

### 17. Testing Module (`pymapgis/testing/`)
**Purpose**: Testing utilities and fixtures

```
testing/
├── __init__.py                 # Testing exports
├── fixtures.py                # Common test fixtures
├── data.py                    # Test data generation
├── mocks.py                   # Mock objects
├── assertions.py              # Custom assertions
└── utils.py                   # Testing utilities
```

### 18. Performance Module (`pymapgis/performance/`)
**Purpose**: Performance optimization and profiling

```
performance/
├── __init__.py                 # Performance exports
├── profiling.py               # Profiling utilities
├── optimization.py            # Optimization strategies
├── benchmarks.py              # Benchmark utilities
├── monitoring.py              # Performance monitoring
└── utils.py                   # Performance utilities
```

## File Naming Conventions

### Module Files
- `__init__.py` - Module exports and main API
- `base.py` - Base classes and interfaces
- `utils.py` - Utility functions
- `exceptions.py` - Custom exceptions

### Implementation Files
- `{feature}.py` - Main feature implementation
- `{feature}_integration.py` - Third-party integrations
- `{feature}_utils.py` - Feature-specific utilities

### Test Files
- `test_{module}.py` - Module tests
- `test_{feature}.py` - Feature tests
- `conftest.py` - pytest configuration

## Import Strategy

### Lazy Imports
- Heavy dependencies loaded on first use
- Optional dependencies handled gracefully
- Fast startup times maintained

### Public API
- Main functions exported from `__init__.py`
- Consistent naming across modules
- Clear deprecation paths

### Internal APIs
- Private functions prefixed with `_`
- Internal modules not exported
- Clear separation of concerns

---

*Next: [Design Patterns](./design-patterns.md) for architectural patterns used throughout PyMapGIS*
