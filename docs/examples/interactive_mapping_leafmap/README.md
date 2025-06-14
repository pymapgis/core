# Interactive Mapping with Leafmap Example

This example demonstrates how to use PyMapGIS to load geospatial data and create an interactive choropleth map using its Leafmap integration.

## Description

The Python script `interactive_map_example.py` performs the following steps:

1.  **Imports PyMapGIS**: `import pymapgis as pmg`.
2.  **Loads Data**: It fetches US state-level geometry and land area data from the TIGER/Line data provider for the year 2022.
3.  **Data Preparation**: Ensures the land area column (`ALAND`) is in a numeric format.
4.  **Creates Map**: It generates an interactive choropleth map where the color intensity of each state corresponds to its land area.
5.  **Saves Map**: The interactive map is saved as an HTML file (`us_states_land_area_map.html`) in the script's directory. Tooltips will show the state name and its land area.

## How to Run

1.  **Ensure PyMapGIS is installed**:
    If you haven't installed PyMapGIS and its optional dependencies for mapping, you might need to:
    \`\`\`bash
    pip install pymapgis[leafmap]
    \`\`\`
    or
    \`\`\`bash
    pip install pymapgis leafmap
    \`\`\`

2.  **Navigate to the example directory**:
    \`\`\`bash
    cd docs/examples/interactive_mapping_leafmap
    \`\`\`

3.  **Run the script**:
    \`\`\`bash
    python interactive_map_example.py
    \`\`\`

## Expected Output

-   The script will print messages to the console indicating its progress (loading data, creating map).
-   An HTML file named `us_states_land_area_map.html` will be created in the current directory (`docs/examples/interactive_mapping_leafmap/`).
-   Opening this HTML file in a web browser will display an interactive map of the United States, where states are colored based on their land area. You can pan, zoom, and hover over states to see tooltips with their name and land area.

## Note on Display

If you run this script in a Jupyter Notebook environment, the map might display directly within the notebook after the cell execution, depending on your Leafmap and Jupyter setup. The script explicitly saves to an HTML file for broader compatibility.
