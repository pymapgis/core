# Tennessee Counties QGIS Project Example

This example demonstrates how to use PyMapGIS to:

1. Download Tennessee counties data from the US Census Bureau
2. Filter and process the data using PyMapGIS
3. Create a QGIS project programmatically using PyQGIS
4. Visualize the data with styling and labels

## Features Demonstrated

- **Data Download**: Automated download of TIGER/Line shapefiles
- **PyMapGIS Integration**: Using PyMapGIS for data processing
- **PyQGIS Automation**: Creating QGIS projects without the GUI
- **Geospatial Analysis**: County-level analysis and visualization
- **State Filtering**: Extracting specific state data from national datasets

## Requirements

```bash
# Core dependencies (should be installed with PyMapGIS)
pip install pymapgis geopandas requests

# For QGIS project creation (requires QGIS installation)
# QGIS must be installed separately
```

## Files

- `tennessee_counties_example.py` - Main example script
- `create_qgis_project.py` - PyQGIS project creation script
- `test_example.py` - Test suite for validation
- `data/` - Downloaded data directory (created automatically)

## Usage

### Step 1: Run the Main Example

```bash
python tennessee_counties_example.py
```

This will:
- Download Tennessee counties data
- Process it with PyMapGIS
- Create visualizations
- Prepare data for QGIS

### Step 2: Create QGIS Project (Optional)

If you have QGIS installed:

```bash
python create_qgis_project.py
```

This will create a complete QGIS project file that you can open in QGIS.

## What You'll Learn

1. **PyMapGIS Data Sources**: How to work with Census TIGER/Line data
2. **Geospatial Processing**: Filtering, styling, and analysis
3. **QGIS Integration**: Creating projects programmatically
4. **Best Practices**: Proper data handling and project structure

## Expected Output

- Tennessee counties shapefile
- Interactive map visualization
- QGIS project file (`.qgz`)
- Summary statistics and analysis

## Tennessee Counties Info

Tennessee has 95 counties, making it a great example for:
- State-level analysis
- County comparison studies
- Regional planning applications
- Educational demonstrations

### Notable Tennessee Counties
- **Davidson County**: Nashville metropolitan area
- **Shelby County**: Memphis metropolitan area
- **Knox County**: Knoxville metropolitan area
- **Hamilton County**: Chattanooga metropolitan area
- **Williamson County**: Affluent Nashville suburb
- **Rutherford County**: Fast-growing Middle Tennessee

## Geographic Regions

Tennessee is traditionally divided into three regions:
- **East Tennessee**: Appalachian Mountains, includes Knoxville
- **Middle Tennessee**: Nashville Basin, includes Nashville
- **West Tennessee**: Mississippi River plains, includes Memphis

## Next Steps

After running this example, try:
- Modifying for other states (change FIPS code)
- Adding demographic data from Census ACS
- Creating choropleth maps with county statistics
- Integrating with other PyMapGIS features
- Analyzing regional differences across the three Tennessee regions
