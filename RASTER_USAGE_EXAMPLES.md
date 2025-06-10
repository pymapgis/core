# PyMapGIS Raster Operations - Usage Examples

## Phase 1 - Part 2 Implementation Complete ✅

The PyMapGIS raster module now fully satisfies all Phase 1 - Part 2 requirements with both standalone functions and xarray accessor methods.

## 1. Reprojection

### Standalone Function
```python
import pymapgis as pmg

# Load a raster
raster = pmg.read("path/to/raster.tif")

# Reproject to Web Mercator
reprojected = pmg.raster.reproject(raster, "EPSG:3857")

# Reproject with custom resolution
reprojected = pmg.raster.reproject(raster, "EPSG:4326", resolution=0.01)
```

### Accessor Method (NEW)
```python
# Same operations using the .pmg accessor
reprojected = raster.pmg.reproject("EPSG:3857")
reprojected = raster.pmg.reproject("EPSG:4326", resolution=0.01)
```

## 2. Normalized Difference (NDVI)

### With Multi-band DataArray
```python
# Load multi-band satellite data
landsat = pmg.read("path/to/landsat.tif")  # Bands: [red, green, nir]

# Calculate NDVI using standalone function
ndvi = pmg.raster.normalized_difference(landsat, 'nir', 'red')

# Calculate NDVI using accessor (NEW)
ndvi = landsat.pmg.normalized_difference('nir', 'red')

# With numbered bands
ndvi = landsat.pmg.normalized_difference(2, 0)  # NIR=band2, Red=band0
```

### With Dataset (separate band variables)
```python
# Load dataset with separate band variables
dataset = pmg.read("path/to/multiband.nc")  # Variables: B4 (red), B5 (nir)

# Calculate NDVI using standalone function
ndvi = pmg.raster.normalized_difference(dataset, 'B5', 'B4')

# Calculate NDVI using accessor (NEW)
ndvi = dataset.pmg.normalized_difference('B5', 'B4')
```

## 3. Real-world Workflow

```python
import pymapgis as pmg

# Load Landsat data
landsat = pmg.read("s3://landsat-data/LC08_L1TP_123456.tif")

# Reproject to local coordinate system
landsat_utm = landsat.pmg.reproject("EPSG:32633")

# Calculate vegetation indices
ndvi = landsat_utm.pmg.normalized_difference('nir', 'red')
ndwi = landsat_utm.pmg.normalized_difference('green', 'nir')

# Results are ready for analysis
print(f"NDVI range: {ndvi.min().values:.3f} to {ndvi.max().values:.3f}")
print(f"Mean NDVI: {ndvi.mean().values:.3f}")
```

## 4. Integration with Existing PyMapGIS

```python
# Works seamlessly with pmg.read()
raster = pmg.read("census://tiger/county?year=2022&state=06")  # Vector
satellite = pmg.read("path/to/satellite.tif")  # Raster

# Reproject satellite to match vector CRS
satellite_aligned = satellite.pmg.reproject(raster.crs)

# Calculate NDVI
ndvi = satellite_aligned.pmg.normalized_difference('B5', 'B4')

# Use with vector operations
clipped_ndvi = pmg.vector.clip(ndvi, raster.geometry.iloc[0])
```

## Key Features

✅ **Dual Interface**: Both standalone functions and accessor methods
✅ **Flexible Input**: Supports DataArray and Dataset objects  
✅ **CRS Support**: EPSG codes, WKT strings, Proj strings
✅ **Error Handling**: Comprehensive validation and helpful error messages
✅ **Performance**: Leverages xarray/rioxarray for efficient operations
✅ **Integration**: Works with pmg.read() and other PyMapGIS functions
