# Oklahoma Economic Indicators Explorer

**before/** – classic GeoPandas + requests + matplotlib  
**after/**  – 10-line PyMapGIS script

## Description

This demo shows how to create a map of median household income by county in Oklahoma using Census ACS data. Oklahoma's economy is diverse, spanning energy, agriculture, aerospace, and technology sectors, making income distribution analysis valuable for economic development planning.

### Before (Traditional Approach)
- Manual API calls to Census Bureau
- Complex data filtering for Oklahoma counties
- Merging with shapefile using GeoPandas
- Static plotting with matplotlib
- Manual handling of missing data and formatting

### After (PyMapGIS Approach)
- Single `pmg.read()` call with census:// URL
- Built-in state filtering and data processing
- Interactive map generation with tooltips
- Automatic data handling and visualization
- Built-in statistical analysis and formatting

## Oklahoma Context

Oklahoma has 77 counties with significant economic diversity:
- **Energy Hub**: Major oil and natural gas production
- **Agricultural Base**: Cattle, wheat, and cotton farming
- **Urban Centers**: Oklahoma City and Tulsa metropolitan areas
- **Rural Communities**: Smaller counties with different economic profiles

This analysis helps identify:
- Economic disparities across counties
- Urban vs rural income patterns
- Areas needing economic development focus
- Regional economic strengths and challenges

## Data Source

Uses American Community Survey (ACS) 5-Year Estimates for median household income (Table B19013) from the U.S. Census Bureau.

## 🚀 Running the Examples

### Prerequisites
```bash
# Install PyMapGIS and dependencies
pip install pymapgis matplotlib geopandas pandas
```

### Execute the Analysis
```bash
# Traditional approach (requires manual data download)
cd before
python app.py <your-census-api-key>

# PyMapGIS approach (automatic data fetching)
cd after
python app.py
```

### Expected Output
- **Console analysis**: Detailed county statistics and rankings
- **Visualization**: `oklahoma_income_map.png` with choropleth map
- **Data insights**: Top/bottom performing counties by median income

## 📊 Example Results

**Oklahoma Economic Summary (2022 ACS)**:
- **77 counties analyzed** with complete income data
- **Income range**: $42,274 - $82,364 median household income
- **State average**: $56,460 median household income
- **Top performer**: Canadian County ($82,364)
- **Economic diversity**: Urban centers vs rural agricultural areas

## QGIS Integration

See `QGIS_GUIDE.md` for detailed instructions on:
- Loading PyMapGIS outputs in QGIS
- Creating custom symbology and layouts
- Performing additional spatial analysis
- Exporting publication-ready maps

See `DATA_SOURCES.md` for information on:
- Why large datasets are not included in the repository
- How to acquire necessary geospatial data
- Data validation and processing workflows

**Note**: Large geospatial datasets are not included in this repository due to size constraints. The examples demonstrate data fetching and processing workflows that can be applied to your own datasets.
