# Simulated Data Example

This example demonstrates how to create and use simulated geospatial data with PyMapGIS. It shows how to generate a GeoDataFrame with random point data and then visualize it.

## Description

The script `simulated_data_example.py` performs the following steps:

1.  **Imports Libraries:** Imports `pymapgis`, `geopandas`, `numpy`, `pandas`, and `shapely.geometry`.
2.  **Generates Simulated Data:**
    *   Defines the number of points to create.
    *   Generates random latitude and longitude coordinates within a bounding box (approximating part of Los Angeles).
    *   Generates random attribute data (e.g., temperature and humidity).
    *   Creates Shapely `Point` objects from the coordinates.
    *   Constructs a GeoPandas GeoDataFrame from the points and attributes, assigning a CRS (Coordinate Reference System).
3.  **Displays Data Information:** Prints the head of the GeoDataFrame and its CRS.
4.  **Visualizes Data:** Creates a scatter plot of the simulated points, where the color of the points represents the 'temperature' attribute. The map includes a title, legend, and tooltips.

## How to Run

1.  Ensure PyMapGIS and its dependencies (GeoPandas, NumPy, Pandas, Shapely, Matplotlib) are installed:
    ```bash
    pip install pymapgis geopandas numpy pandas shapely matplotlib
    ```
2.  Navigate to this directory:
    ```bash
    cd examples/simulated_data_example
    ```
3.  Run the script:
    ```bash
    python simulated_data_example.py
    ```

This will print information about the generated data and then display a map visualizing the simulated temperature points.
