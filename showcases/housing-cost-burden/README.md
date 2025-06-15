# Housing-Cost Burden Explorer

**before/** – classic GeoPandas + requests + matplotlib  
**after/**  – 10-line PyMapGIS script

## Description

This demo shows how to create a map of housing cost burden (percentage of households spending 30%+ of income on housing) by county using Census ACS data.

### Before (Traditional Approach)
- Manual API calls to Census Bureau
- Complex data aggregation and calculation
- Merging with shapefile using GeoPandas
- Static plotting with matplotlib

### After (PyMapGIS Approach)
- Single `pmg.read()` call with census:// URL
- Built-in formula calculation for complex aggregations
- Interactive map generation with tooltips
- Automatic data handling and visualization
