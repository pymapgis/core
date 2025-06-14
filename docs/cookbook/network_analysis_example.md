# Network Analysis with PyMapGIS

This cookbook example demonstrates how to use the network analysis capabilities in `pymapgis.network`. You can create a network graph from road segments (LineStrings), find shortest paths, and generate isochrones (reachability polygons).

## 1. Setup

Ensure you have PyMapGIS installed with the necessary dependencies (`networkx`). If you installed PyMapGIS core, `networkx` should be included.

```python
import geopandas as gpd
from shapely.geometry import LineString, Point
import pymapgis.network as pmg_net
import matplotlib.pyplot as plt # For basic plotting of results
```

## 2. Creating a Network Graph

First, you need a `GeoDataFrame` containing LineString geometries representing the network segments (e.g., roads, pathways).

```python
# Sample GeoDataFrame representing a simple street network
data = {
    'id': [1, 2, 3, 4, 5, 6],
    'street_name': ['Main St', 'Oak Ave', 'Pine Ln', 'Elm Rd', 'Maple Dr', 'Cedar Byp'],
    'max_speed_kmh': [40, 40, 30, 50, 40, 60], # Used for calculating travel time weight
    'geometry': [
        LineString([(0, 0), (1, 0)]),      # Main St
        LineString([(1, 0), (2, 0)]),      # Oak Ave
        LineString([(0, 0), (0, 1)]),      # Pine Ln
        LineString([(0, 1), (1, 1)]),      # Elm Rd
        LineString([(1, 1), (2, 1)]),      # Maple Dr
        LineString([(2, 0), (2, 1)])       # Cedar Byp (connects Oak Ave and Maple Dr)
    ]
}
streets_gdf = gpd.GeoDataFrame(data, crs="EPSG:4326")

# Calculate a 'travel_time' weight for edges (time = length / speed)
# Assuming length is in meters (default for geographic CRS) and speed in km/h
# For consistency, let's assume CRS units are meters, or lengths are pre-calculated.
# Here, coordinates are simple, so length of segment (0,0)-(1,0) is 1 unit.
# If these units are meters, then length/ (speed_kmh * 1000/3600) gives seconds.
# For simplicity, let's use a nominal 'cost' = geometric_length / max_speed_kmh
streets_gdf['travel_time_cost'] = streets_gdf.geometry.length / streets_gdf['max_speed_kmh']

# Create the network graph
# Nodes will be (x,y) tuples. Edges store attributes like length and weight.
graph = pmg_net.create_network_from_geodataframe(streets_gdf, weight_col='travel_time_cost')

print(f"Created graph with {graph.number_of_nodes()} nodes and {graph.number_of_edges()} edges.")
# Example: print nodes and edges
# print("Nodes:", list(graph.nodes()))
# print("Edges with data:", list(graph.edges(data=True))[:2]) # Print first two edges
```

## 3. Finding the Nearest Network Node

If your point of interest doesn't exactly match a network node (intersection or dead-end), you can find the closest one.

```python
# Define an arbitrary point
my_location = (0.1, 0.1)

# Find the nearest node in the graph to this point
nearest_node = pmg_net.find_nearest_node(graph, my_location)
print(f"My location: {my_location}")
print(f"Nearest network node: {nearest_node}") # Expected: (0.0, 0.0)
```

## 4. Calculating the Shortest Path

Calculate the shortest path between two nodes in the network, using a specified weight (e.g., 'travel_time_cost' or default 'length').

```python
# Define source and target nodes (must be actual nodes from the graph)
source_node = (0,0) # e.g., start_point_on_network (use find_nearest_node if needed)
target_node = (2,1) # e.g., end_point_on_network

# Calculate shortest path using 'travel_time_cost'
try:
    path_nodes, total_cost = pmg_net.shortest_path(graph, source_node, target_node, weight='travel_time_cost')
    print(f"\nShortest path from {source_node} to {target_node}:")
    print("Path nodes:", path_nodes)
    print("Total travel time cost:", total_cost)

    # Visualize the path (optional)
    path_lines = [LineString([path_nodes[i], path_nodes[i+1]]) for i in range(len(path_nodes)-1)]
    path_gdf = gpd.GeoDataFrame({'geometry': path_lines}, crs=streets_gdf.crs)

    # Plotting (basic example)
    # fig, ax = plt.subplots()
    # streets_gdf.plot(ax=ax, color='gray', linewidth=1, label='Network')
    # path_gdf.plot(ax=ax, color='blue', linewidth=2, label='Shortest Path')
    # plt.scatter([source_node[0], target_node[0]], [source_node[1], target_node[1]], color='red', zorder=5, label='Source/Target')
    # plt.legend()
    # plt.title("Shortest Path Analysis")
    # plt.show()

except nx.NetworkXNoPath:
    print(f"No path found between {source_node} and {target_node}.")
except Exception as e:
    print(f"An error occurred: {e}")
```

## 5. Generating an Isochrone

Generate an isochrone to visualize the reachable area from a source node within a given maximum travel cost.

```python
# Isochrone from 'source_node' with a max 'travel_time_cost'
# Example: Max travel_time_cost of 0.025
# (0,0) -> (1,0) : length 1 / speed 40 = 0.025. Node (1,0) is reachable.
# (0,0) -> (0,1) : length 1 / speed 30 = ~0.033. Node (0,1) is NOT reachable with cost 0.025.
max_travel_cost = 0.025

isochrone_gdf = pmg_net.generate_isochrone(graph, source_node, max_cost=max_travel_cost, weight='travel_time_cost')

if not isochrone_gdf.empty:
    print(f"\nIsochrone for max cost {max_travel_cost} from {source_node}:")
    # print(isochrone_gdf.geometry.iloc[0])

    # Visualize the isochrone (optional)
    # fig, ax = plt.subplots()
    # streets_gdf.plot(ax=ax, color='gray', linewidth=1, label='Network', alpha=0.5)
    # isochrone_gdf.plot(ax=ax, alpha=0.5, color='green', edgecolor='black', label='Isochrone')
    # plt.scatter(source_node[0], source_node[1], color='red', s=50, zorder=5, label='Source Node')
    # plt.legend()
    # plt.title(f"Isochrone (Max Cost: {max_travel_cost})")
    # plt.show()
else:
    print(f"No area reachable from {source_node} within max cost {max_travel_cost}.")

```

## Important Considerations

- **CRS:** Ensure your input GeoDataFrame has a projected Coordinate Reference System (CRS) if you are using geometric length for weights, so that `gdf.geometry.length` provides meaningful distance units (e.g., meters).
- **Network Connectivity:** The quality of network analysis results depends heavily on how well connected your network graph is (e.g., overpasses/underpasses need careful handling if represented as simple intersections).
- **Performance:** For very large networks (millions of edges), the standard NetworkX algorithms used here (like Dijkstra's) can be slow. Future versions of PyMapGIS might explore integration with specialized libraries offering more performant algorithms (e.g., using Contraction Hierarchies).
- **Isochrone Generation:** The current isochrone generation uses a convex hull of reachable nodes. For more detailed or concave shapes, especially in complex street networks, more advanced techniques like alpha shapes or service area polygons based on buffered network segments might be necessary.

This example provides a starting point for leveraging network analysis tools within PyMapGIS.
```
