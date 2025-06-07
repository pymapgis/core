# Labor-Force Participation Gap

**before/** – classic GeoPandas + requests + matplotlib  
**after/**  – 10-line PyMapGIS script

## Description

This demo shows how to create a map of prime-age labor-force participation rates by county using Census ACS data.

### Before (Traditional Approach)
- Manual API calls to Census Bureau
- Data cleaning and transformation with pandas
- Merging with shapefile using GeoPandas
- Plotting with matplotlib

### After (PyMapGIS Approach)
- Single `pmg.read()` call with census:// URL
- Built-in formula calculation
- Interactive map generation with tooltips
- Automatic data handling and visualization
