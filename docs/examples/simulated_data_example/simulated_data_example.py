import pymapgis as pmg
import geopandas as gpd
import numpy as np
import pandas as pd
from shapely.geometry import Point

# Generate simulated data
num_points = 50

# Generate random latitudes (e.g., between 34.0 and 34.2) and longitudes (e.g., between -118.5 and -118.2) for Los Angeles area.
np.random.seed(42) # for reproducibility
latitudes = np.random.uniform(34.0, 34.2, num_points)
longitudes = np.random.uniform(-118.5, -118.2, num_points)

# Create random temperature values (e.g., between 15 and 30) and humidity values (e.g., between 40 and 80).
temp_values = np.random.uniform(15, 30, num_points)
humidity_values = np.random.uniform(40, 80, num_points)

# Create a list of Shapely Point objects from the latitudes and longitudes.
points = [Point(lon, lat) for lon, lat in zip(longitudes, latitudes)]

# Create a GeoDataFrame
simulated_gdf = gpd.GeoDataFrame(
    {'temperature': temp_values, 'humidity': humidity_values, 'geometry': points},
    crs="EPSG:4326"
)

# Demonstrate PyMapGIS functionality
print("Simulated GeoDataFrame:")
print(simulated_gdf.head())
print(f"\nCRS: {simulated_gdf.crs}")

# Create a scatter plot of temperature
# Using .plot.scatter() as choropleth is not ideal for points.
# The .show() method is chained if the plot object supports it,
# otherwise, we rely on pmg.plt.show() or direct figure showing.

plot_object = simulated_gdf.plot.scatter(
    column="temperature",
    cmap="viridis",
    legend=True,
    title="Simulated Temperature Data Points",
    tooltip=['temperature', 'humidity']
)

# Show the plot
if hasattr(plot_object, 'figure') and hasattr(plot_object.figure, 'show'):
    plot_object.figure.show()
elif hasattr(pmg, 'plt') and hasattr(pmg.plt, 'show'):
    pmg.plt.show()
else:
    # Fallback for environments where .show() might be implicitly called or handled differently
    # For example, in a Jupyter notebook, the plot might show automatically.
    # If running as a script, and the above don't work, matplotlib might need specific backend configuration.
    print("Plot generated. Ensure your environment is configured to display Matplotlib plots.")
    # Attempt a more direct matplotlib show if pmg.plt is indeed pyplot
    try:
        import matplotlib.pyplot as plt
        plt.show()
    except ImportError:
        print("Matplotlib.pyplot not found, cannot explicitly call show().")
