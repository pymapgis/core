import osmnx as ox
import networkx as nx
import matplotlib
matplotlib.use('Agg') # Use Agg backend for non-interactive plotting
import matplotlib.pyplot as plt
import geopandas as gpd
from shapely.geometry import Point

def perform_network_analysis():
    """
    Demonstrates shortest path and isochrone analysis using osmnx.
    """
    # Define a place and download street network
    # Using a small, well-defined place for efficiency
    place_name = "Piedmont, California, USA"
    print(f"Fetching street network for '{place_name}'...")
    try:
        # 'drive' network is suitable for car travel
        graph = ox.graph_from_place(place_name, network_type="drive", retain_all=False)
        graph_proj = ox.project_graph(graph) # Project to UTM for accurate distances/areas
        print("Street network graph downloaded and projected.")
    except Exception as e:
        print(f"Error downloading or projecting graph for {place_name}: {e}")
        print("Please ensure you have an internet connection and osmnx is correctly installed.")
        print("Sometimes, specific locations might have issues with OSM data availability.")
        return

    # --- Shortest Path Analysis ---
    print("\\n--- Shortest Path Analysis ---")
    # Define origin and destination points (latitude, longitude)
    # These should be within the downloaded map area.
    # For Piedmont, CA:
    origin_coords = (37.827, -122.231)  # Example: Near city hall
    destination_coords = (37.820, -122.218) # Example: Near a park

    try:
        # Get the nearest network nodes to the specified coordinates
        origin_node = ox.nearest_nodes(graph, X=origin_coords[1], Y=origin_coords[0])
        destination_node = ox.nearest_nodes(graph, X=destination_coords[1], Y=destination_coords[0])
        print(f"Origin node: {origin_node}, Destination node: {destination_node}")

        # Calculate shortest path (length in meters)
        shortest_path_route = nx.shortest_path(graph, source=origin_node, target=destination_node, weight="length")
        shortest_path_length = nx.shortest_path_length(graph, source=origin_node, target=destination_node, weight="length")

        print(f"Shortest path (node IDs): {shortest_path_route}")
        print(f"Shortest path length: {shortest_path_length:.2f} meters")

        # Plot the shortest path
        print("Plotting shortest path (see pop-up window)...")
        fig, ax = ox.plot_graph_route(
            graph, shortest_path_route, route_color="r", route_linewidth=6,
            node_size=0, bgcolor="k", show=False, close=False
        )
        # Add markers for origin and destination
        ax.scatter(graph.nodes[origin_node]['x'], graph.nodes[origin_node]['y'], c='lime', s=100, zorder=5, label='Origin')
        ax.scatter(graph.nodes[destination_node]['x'], graph.nodes[destination_node]['y'], c='blue', s=100, zorder=5, label='Destination')
        ax.legend()
        plt.suptitle(f"Shortest Path in {place_name}", y=0.95)
        plt.savefig("shortest_path_plot.png") # Save plot instead of showing
        print("Shortest path plot saved to shortest_path_plot.png.")

    except nx.NetworkXNoPath:
        print(f"No path found between origin {origin_coords} and destination {destination_coords}.")
    except Exception as e:
        print(f"Error during shortest path analysis: {e}")

    # --- Isochrone Analysis ---
    print("\\n--- Isochrone Analysis ---")
    # Define a central point for isochrones
    isochrone_center_coords = origin_coords # Use the same origin as before for this example

    try:
        center_node_proj = ox.nearest_nodes(graph_proj, X=isochrone_center_coords[1], Y=isochrone_center_coords[0])
        print(f"Isochrone center node (projected graph): {center_node_proj}")

        # Travel times for isochrones (in minutes)
        # Assuming an average travel speed, e.g., 30 km/h = 500 meters/minute
        # travel_speed_kmh = 30
        # meters_per_minute = (travel_speed_kmh * 1000) / 60
        # trip_times_minutes = [2, 5, 10] # In minutes
        # trip_distances_meters = [t * meters_per_minute for t in trip_times_minutes]

        # OSMnx direct isochrone generation uses travel time and speed
        # Or, we can use 'length' attribute if speed data is not imputed.
        # For this example, let's use distances directly if speed imputation is complex.
        # The 'length' attribute is in meters.
        trip_lengths_meters = [500, 1000, 2000] # 500m, 1km, 2km travel distances

        isochrone_polygons = []
        for trip_length in sorted(trip_lengths_meters, reverse=True):
            subgraph = nx.ego_graph(graph_proj, center_node_proj, radius=trip_length, distance="length")
            # Create a GeoDataFrame from the nodes in the subgraph
            node_points = [Point(data["x"], data["y"]) for node, data in subgraph.nodes(data=True)]
            if not node_points:
                print(f"No nodes found within {trip_length}m for isochrone generation.")
                continue

            # Create convex hull of these nodes
            # For more accurate isochrones, alpha shapes (concave hulls) or buffer analysis on network edges are better.
            # OSMnx has a dedicated function for this:
            # isochrone_poly = ox.isochrones.isochrones_from_node(graph_proj, center_node_proj, [trip_length], travel_speed=travel_speed_kmh)
            # However, that requires travel_speed and might be more involved.
            # For simplicity, we'll use convex hull of nodes within the ego_graph.
            # This is a simplification. Real isochrones are more complex.

            # Using ox.features_from_polygon with convex_hull
            nodes_gdf = ox.graph_to_gdfs(subgraph, edges=False)
            if nodes_gdf.empty:
                 print(f"No nodes in subgraph for trip_length {trip_length}m to form a polygon.")
                 continue

            # Create a convex hull of the nodes
            convex_hull = nodes_gdf.unary_union.convex_hull
            isochrone_polygons.append(convex_hull)

        if isochrone_polygons:
            # Convert to GeoDataFrame for plotting
            iso_gdf = gpd.GeoDataFrame({'geometry': isochrone_polygons}, crs=graph_proj.graph["crs"])
            print(f"Generated {len(isochrone_polygons)} isochrone polygon(s).")

            # Plot the isochrones
            print("Plotting isochrones (see pop-up window)...")
            fig, ax = ox.plot_graph(
                graph_proj, show=False, close=False, bgcolor="k", node_size=0, edge_color="w", edge_linewidth=0.3
            )
            iso_gdf.plot(ax=ax, fc="blue", alpha=0.3, edgecolor="none") # Plot isochrones
            ax.scatter(graph_proj.nodes[center_node_proj]['x'], graph_proj.nodes[center_node_proj]['y'], c='red', s=100, zorder=5, label='Center Point')
            ax.legend()
            plt.suptitle(f"Isochrones from center point in {place_name} (based on distance)", y=0.95)
            plt.savefig("isochrone_plot.png") # Save plot instead of showing
            print("Isochrone plot saved to isochrone_plot.png.")
        else:
            print("No isochrone polygons were generated.")

    except Exception as e:
        print(f"Error during isochrone analysis: {e}")

if __name__ == "__main__":
    print("Starting Advanced Network Analysis Example (Shortest Path & Isochrones)...")
    # Check for dependencies
    try:
        import osmnx
        import networkx
        import matplotlib
        import geopandas
        from shapely.geometry import Point
    except ImportError as e:
        print(f"Import Error: {e}. Please ensure osmnx, networkx, matplotlib, geopandas, and shapely are installed.")
        print("You can typically install them using: pip install osmnx networkx matplotlib geopandas shapely")
    else:
        perform_network_analysis()
    print("\\nNetwork analysis example finished.")
