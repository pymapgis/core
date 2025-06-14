# TIGER/Line Data Visualization Example

This example demonstrates how to load and visualize TIGER/Line data, specifically roads, for a selected county using PyMapGIS.

## Description

The script `tiger_line_visualization.py` performs the following steps:

1.  **Imports PyMapGIS:** Imports the `pymapgis` library.
2.  **Loads Road Data:** Uses `pmg.read()` to fetch road data for Los Angeles County, California, from the TIGER/Line dataset. The `year`, `state` FIPS code, and `county` FIPS code are specified in the URL.
3.  **Visualizes Data:** Generates a plot of the roads, colored by road type (`RTTYP`), using the built-in plotting capabilities of PyMapGIS. The map includes a title and a legend.

## How to Run

1.  Ensure PyMapGIS is installed:
    ```bash
    pip install pymapgis
    ```
2.  Navigate to this directory:
    ```bash
    cd examples/tiger_line_visualization
    ```
3.  Run the script:
    ```bash
    python tiger_line_visualization.py
    ```

This will display an interactive map showing the roads in the specified county.
