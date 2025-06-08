# Local File Interaction Example

This example demonstrates how to load a local GeoJSON file, combine it with Census data (TIGER/Line county boundaries), and visualize the result using PyMapGIS.

## Description

The script `local_file_interaction.py` performs the following steps:

1.  **Imports PyMapGIS:** Imports the `pymapgis` library.
2.  **Loads Local Data:** Reads points of interest from a local GeoJSON file (`sample_data.geojson`) using `pmg.read()` with a `file://` URL.
3.  **Loads Census Data:** Fetches county boundaries for California from the TIGER/Line dataset.
4.  **Filters Data:** Selects Los Angeles County from the loaded counties.
5.  **Spatial Join:** Performs a spatial join to associate the points of interest with Los Angeles County. This step confirms which points are within the county boundary.
6.  **Visualizes Data:**
    *   Creates a base map showing the boundary of Los Angeles County.
    *   Overlays the points of interest on this map, styling them by their "amenity" type.
    *   Adds a title and legend to the map.
    *   Displays the combined map.

The `sample_data.geojson` file contains a few sample point features located within Los Angeles County.

## How to Run

1.  Ensure PyMapGIS and its dependencies (like GeoPandas, Matplotlib) are installed:
    ```bash
    pip install pymapgis
    ```
2.  Navigate to this directory:
    ```bash
    cd examples/local_file_interaction
    ```
3.  Run the script:
    ```bash
    python local_file_interaction.py
    ```

This will display a map showing the sample points of interest within the boundary of Los Angeles County.
