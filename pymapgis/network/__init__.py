"""
Network analysis capabilities for PyMapGIS.

This module provides functions to create network graphs from geospatial data
and perform common network analyses like shortest path and isochrone generation.
It currently uses NetworkX as the underlying graph library.

For very large networks, the performance of these standard algorithms might be
a concern. Future enhancements could explore specialized libraries or algorithms
like Contraction Hierarchies for improved performance in such scenarios.
"""

import geopandas as gpd
import networkx as nx
import numpy as np
from shapely.geometry import Point, LineString
from shapely.ops import nearest_points
from typing import Tuple, List, Any, Optional

__all__ = [
    "create_network_from_geodataframe",
    "find_nearest_node",
    "shortest_path",
    "generate_isochrone",
]


def create_network_from_geodataframe(
    gdf: gpd.GeoDataFrame, weight_col: Optional[str] = None, simplify_graph: bool = True
) -> nx.Graph:
    """
    Creates a NetworkX graph from a GeoDataFrame of LineStrings.

    Nodes in the graph are unique coordinates (start/end points of lines).
    Edges represent the LineString segments. Edge weights can be derived
    from segment length or a specified attribute column.

    Args:
        gdf (gpd.GeoDataFrame): Input GeoDataFrame with LineString geometries.
            Must have a valid geometry column.
        weight_col (Optional[str]): Name of the column to use for edge weights.
            If None, the geometric length of the LineString is used.
            The values in this column should be numeric.
        simplify_graph (bool): If True (default), simplifies the graph by removing
            degree-two nodes (nodes that merely connect two edges in a straight line)
            unless they are true intersections or endpoints. This can make some
            network algorithms more efficient but might alter path details slightly.
            Currently, simplification is basic and might be enhanced later.
            For now, it primarily ensures no duplicate edges between same nodes if simplify is False.
            A more robust simplification (contracting paths) is not yet implemented.

    Returns:
        nx.Graph: A NetworkX graph representing the network. Nodes are coordinate
                  tuples (x, y). Edges have a 'length' attribute (geometric length)
                  and potentially a 'weight' attribute (if `weight_col` is specified
                  or defaults to length).

    Raises:
        ValueError: If the GeoDataFrame does not contain LineString geometries
                    or if the specified `weight_col` contains non-numeric data.
        TypeError: If input is not a GeoDataFrame.
    """
    if not isinstance(gdf, gpd.GeoDataFrame):
        raise TypeError("Input must be a GeoDataFrame.")
    if gdf.empty:
        return nx.Graph()

    # Ensure geometries are LineStrings
    if not all(
        geom.geom_type == "LineString" for geom in gdf.geometry if geom is not None
    ):
        raise ValueError("All geometries in the GeoDataFrame must be LineStrings.")

    graph = nx.Graph()

    for idx, row in gdf.iterrows():
        geom = row.geometry
        if geom is None or geom.is_empty:
            continue

        start_node = (geom.coords[0][0], geom.coords[0][1])
        end_node = (geom.coords[-1][0], geom.coords[-1][1])

        # Add nodes (NetworkX handles duplicates automatically)
        graph.add_node(start_node, x=start_node[0], y=start_node[1])
        graph.add_node(end_node, x=end_node[0], y=end_node[1])

        length = geom.length
        weight = length  # Default weight is length

        if weight_col:
            if weight_col not in gdf.columns:
                raise ValueError(
                    f"Weight column '{weight_col}' not found in GeoDataFrame."
                )
            custom_weight = row[weight_col]
            if not isinstance(custom_weight, (int, float)):
                raise ValueError(
                    f"Weight column '{weight_col}' must contain numeric data. Found {type(custom_weight)}."
                )
            weight = custom_weight

        # Add edge with attributes
        # If an edge already exists, NetworkX updates attributes if new ones are provided.
        # We might want to handle parallel edges differently, but for now, one edge per node pair.
        if graph.has_edge(start_node, end_node):
            # If edge exists, update weight if current path is shorter (common in some graph constructions)
            # For now, let's assume we take the first encountered or overwrite.
            # Or, if multiple edges are allowed, use MultiGraph. For now, Graph (unique edges).
            # Let's prioritize shorter weight if duplicate.
            if weight < graph[start_node][end_node].get("weight", float("inf")):
                graph.add_edge(
                    start_node,
                    end_node,
                    length=length,
                    weight=weight,
                    id=idx,
                    geometry=geom,
                )
        else:
            graph.add_edge(
                start_node,
                end_node,
                length=length,
                weight=weight,
                id=idx,
                geometry=geom,
            )

    # Basic simplification: remove self-loops if any (should not occur from LineStrings)
    graph.remove_edges_from(nx.selfloop_edges(graph))

    # Note: True graph simplification (contracting paths of degree-two nodes) is more complex.
    # The `simplify_graph` flag is a placeholder for future more robust simplification.
    # For now, the main effect is how duplicate edges are handled (or not, with simple Graph).
    # If `simplify_graph` were to be fully implemented, it might involve:
    # G_simplified = G.copy()
    # for node, degree in list(G_simplified.degree()):
    #     if degree == 2:
    #         # logic to contract edge if it's not a terminal node of the original network
    #         pass # This is non-trivial
    # This is a placeholder for future complexity.

    return graph


def find_nearest_node(graph: nx.Graph, point: Tuple[float, float]) -> Any:
    """
    Finds the closest graph node to an arbitrary coordinate tuple.

    Args:
        graph (nx.Graph): The NetworkX graph. Nodes are expected to be coordinate tuples.
        point (Tuple[float, float]): The (x, y) coordinate tuple for which to find the nearest node.

    Returns:
        Any: The identifier of the nearest node in the graph. Returns None if graph is empty.

    Raises:
        ValueError: If graph nodes are not coordinate tuples or graph is empty.
    """
    if not graph.nodes:
        return None

    nodes_array = np.array(list(graph.nodes))  # Assumes nodes are (x,y) tuples
    if nodes_array.ndim != 2 or nodes_array.shape[1] != 2:
        raise ValueError("Graph nodes must be structured as (x,y) coordinate tuples.")

    point_np = np.array(point)
    distances = np.sum((nodes_array - point_np) ** 2, axis=1)
    nearest_idx = np.argmin(distances)

    # Return the actual node from the graph's node list (maintaining original type)
    return list(graph.nodes)[nearest_idx]


def shortest_path(
    graph: nx.Graph,
    source_node: Tuple[float, float],
    target_node: Tuple[float, float],
    weight: str = "length",
) -> Tuple[List[Tuple[float, float]], float]:
    """
    Calculates the shortest path between two nodes in the graph.

    Uses NetworkX's `shortest_path` and `shortest_path_length` (Dijkstra's algorithm
    by default for weighted graphs).

    Args:
        graph (nx.Graph): The NetworkX graph.
        source_node (Tuple[float, float]): The (x, y) coordinate of the source node.
                                           Must be an existing node in the graph.
        target_node (Tuple[float, float]): The (x, y) coordinate of the target node.
                                           Must be an existing node in the graph.
        weight (str): The edge attribute to use as weight (e.g., 'length', 'time').
                      Defaults to 'length'. If None, uses unweighted path.

    Returns:
        Tuple[List[Tuple[float, float]], float]: A tuple containing:
            - A list of nodes (coordinate tuples) representing the path.
            - The total path cost (e.g., length or time).

    Raises:
        nx.NodeNotFound: If source or target node is not in the graph.
        nx.NetworkXNoPath: If no path exists between source and target.
        KeyError: If the specified `weight` attribute does not exist on edges.
    """
    if source_node not in graph:
        raise nx.NodeNotFound(f"Source node {source_node} not found in graph.")
    if target_node not in graph:
        raise nx.NodeNotFound(f"Target node {target_node} not found in graph.")

    try:
        path_nodes = nx.shortest_path(
            graph, source=source_node, target=target_node, weight=weight
        )
        path_cost = nx.shortest_path_length(
            graph, source=source_node, target=target_node, weight=weight
        )
    except nx.NetworkXNoPath:
        # Re-raise to be explicit or handle as per desired API (e.g. return [], float('inf'))
        raise
    except KeyError as e:
        raise KeyError(
            f"Weight attribute '{weight}' not found on graph edges. Original error: {e}"
        )

    return path_nodes, path_cost


def generate_isochrone(
    graph: nx.Graph,
    source_node: Tuple[float, float],
    max_cost: float,
    weight: str = "length",
) -> gpd.GeoDataFrame:
    """
    Generates an isochrone polygon representing reachable areas from a source node
    within a maximum travel cost.

    Calculates all reachable nodes within `max_cost` from `source_node` using
    NetworkX's `single_source_dijkstra_path_length` (or `ego_graph` for unweighted).
    Returns a GeoDataFrame containing a polygon representing the isochrone,
    generated by a convex hull of the reachable nodes.

    Args:
        graph (nx.Graph): The NetworkX graph.
        source_node (Tuple[float, float]): The (x, y) coordinate of the source node.
                                           Must be an existing node in the graph.
        max_cost (float): The maximum travel cost (e.g., distance or time)
                          from the source node.
        weight (str): The edge attribute to use as cost (e.g., 'length', 'time').
                      Defaults to 'length'. If None, treats graph as unweighted
                      and `max_cost` would refer to number of hops.

    Returns:
        gpd.GeoDataFrame: A GeoDataFrame with a single row containing the
                          isochrone Polygon geometry. Returns an empty GeoDataFrame
                          with CRS EPSG:4326 (a common default) if no reachable
                          nodes are found or if source node is invalid.

    Raises:
        nx.NodeNotFound: If source_node is not in the graph.
        KeyError: If the specified `weight` attribute does not exist on edges (and is not None).
    """
    if source_node not in graph:
        raise nx.NodeNotFound(f"Source node {source_node} not found in graph.")

    reachable_nodes = []

    if weight is None:  # Unweighted graph, max_cost is number of hops
        # ego_graph gives all nodes reachable within a certain radius (number of hops)
        # It includes the source_node itself at radius 0.
        # If max_cost is 0, only source_node is included.
        subgraph = nx.ego_graph(
            graph, n=source_node, radius=int(max_cost), undirected=True
        )
        reachable_nodes.extend(list(subgraph.nodes()))
    else:
        # Weighted graph, use Dijkstra
        try:
            path_lengths = nx.single_source_dijkstra_path_length(
                graph, source=source_node, cutoff=max_cost, weight=weight
            )
            reachable_nodes.extend(path_lengths.keys())
        except KeyError as e:
            raise KeyError(
                f"Weight attribute '{weight}' not found on graph edges. Original error: {e}"
            )

    if not reachable_nodes or len(reachable_nodes) < 3:
        # Convex hull needs at least 3 points.
        # If fewer than 3 nodes, return an empty GDF or a Point/LineString representation.
        # For simplicity, returning an empty GDF.
        # A common default CRS like EPSG:4326 can be set.
        return gpd.GeoDataFrame({"geometry": []}, crs="EPSG:4326")

    # Create Point geometries from reachable nodes
    points = [Point(node) for node in reachable_nodes]

    # Generate convex hull
    # Note: For more accurate isochrones, especially on sparse networks or complex street layouts,
    # an alpha shape (concave hull) or buffer-based approach on the network segments might be better.
    # Convex hull is a simpler first implementation.
    isochrone_polygon = gpd.GeoSeries(points).unary_union.convex_hull

    # Create GeoDataFrame for the isochrone
    # Using a common default CRS. Ideally, the graph or input data would carry CRS.
    # For now, let's assume WGS84-like coordinates.
    isochrone_gdf = gpd.GeoDataFrame({"geometry": [isochrone_polygon]}, crs="EPSG:4326")

    return isochrone_gdf
