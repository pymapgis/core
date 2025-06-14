# 🔧 PyMapGIS API Reference

Complete API documentation for PyMapGIS functions, classes, and modules.

## Table of Contents

1. [📖 Core Functions](#-core-functions)
2. [🗺️ Plotting API](#️-plotting-api)
3. [💾 Vector Data Utilities](#-vector-data-utilities)
4. [🎞️ Raster Data (`pymapgis.raster`)](#️-raster-data-pymapgisraster)
5. [🌐 Network Analysis (`pymapgis.network`)](#-network-analysis-pymapgisnetwork)
6. [☁️ Point Cloud (`pymapgis.pointcloud`)](#️-point-cloud-pymapgispointcloud)
7. [🌊 Streaming Data (`pymapgis.streaming`)](#-streaming-data-pymapgisstreaming)
8. [⚡ Cache API](#-cache-api)
9. [⚙️ Settings API](#️-settings-api)
10. [📊 Data Sources](#-data-sources)

## 📖 Core Functions

### `pymapgis.read()`

Universal data reader function that supports multiple data sources through URL-based syntax.

```python
def read(
    url: str,
    cache_ttl: Optional[str] = None,
    **kwargs
) -> gpd.GeoDataFrame
```

**Parameters:**
- `url` (str): Data source URL with protocol-specific syntax
- `cache_ttl` (str, optional): Override default cache TTL for this request
- `**kwargs`: Additional parameters passed to underlying readers

**Returns:**
- `GeoDataFrame`: GeoPandas GeoDataFrame with spatial data

**Supported URL Patterns:**

#### Census ACS Data
```python
# Pattern: census://acs/{product}?{parameters}
pmg.read("census://acs/acs5?year=2022&geography=county&variables=B01003_001E")
```

**Parameters:**
- `product`: ACS product (`acs1`, `acs3`, `acs5`)
- `year`: Data year (2009-2022 for ACS5)
- `geography`: Geographic level (`county`, `state`, `tract`, `block group`)
- `variables`: Comma-separated ACS variable codes
- `state`: Optional state filter (FIPS code or name)

#### TIGER/Line Boundaries
```python
# Pattern: tiger://{geography}?{parameters}
pmg.read("tiger://county?year=2022&state=06")
```

**Parameters:**
- `geography`: Boundary type (`county`, `state`, `tract`, `block`, `place`, `zcta`)
- `year`: Vintage year (2010-2022)
- `state`: Optional state filter (FIPS code or name)

#### Local Files
```python
# Pattern: file://{path}
pmg.read("file://path/to/data.geojson")
```

**Supported formats:** GeoJSON, Shapefile, GeoPackage, KML, and other GeoPandas-supported formats.

**Examples:**
```python
import pymapgis as pmg

# Load Census data with automatic geometry
housing = pmg.read("census://acs/acs5?year=2022&geography=county&variables=B25070_010E,B25070_001E")

# Load geographic boundaries only
counties = pmg.read("tiger://county?year=2022")

# Load local file
local_data = pmg.read("file://./data/my_boundaries.geojson")

# Override cache TTL
fresh_data = pmg.read("census://acs/acs5?year=2022&geography=state&variables=B01003_001E", cache_ttl="1h")
```

## 🗺️ Plotting API

PyMapGIS extends GeoPandas with enhanced plotting capabilities through the `.plot` accessor.

### `.plot.interactive()`

Create a basic interactive map with default styling.

```python
def interactive(
    tiles: str = "OpenStreetMap",
    zoom_start: int = 4,
    **kwargs
) -> leafmap.Map
```

**Parameters:**
- `tiles` (str): Base map tiles (`"OpenStreetMap"`, `"CartoDB positron"`, `"Stamen Terrain"`)
- `zoom_start` (int): Initial zoom level
- `**kwargs`: Additional parameters passed to leafmap

**Returns:**
- `leafmap.Map`: Interactive Leaflet map object

**Example:**
```python
data = pmg.read("tiger://state?year=2022")
data.plot.interactive(tiles="CartoDB positron", zoom_start=3).show()
```

### `.plot.choropleth()`

Create a choropleth (color-coded) map based on data values.

```python
def choropleth(
    column: str,
    title: Optional[str] = None,
    cmap: str = "viridis",
    legend: bool = True,
    tooltip: Optional[List[str]] = None,
    popup: Optional[List[str]] = None,
    style_kwds: Optional[Dict] = None,
    legend_kwds: Optional[Dict] = None,
    tooltip_kwds: Optional[Dict] = None,
    popup_kwds: Optional[Dict] = None,
    **kwargs
) -> leafmap.Map
```

**Parameters:**
- `column` (str): Column name to use for color coding
- `title` (str, optional): Map title
- `cmap` (str): Matplotlib colormap name (default: "viridis")
- `legend` (bool): Whether to show color legend (default: True)
- `tooltip` (List[str], optional): Columns to show in hover tooltip
- `popup` (List[str], optional): Columns to show in click popup
- `style_kwds` (dict, optional): Styling parameters for map features
- `legend_kwds` (dict, optional): Legend customization parameters
- `tooltip_kwds` (dict, optional): Tooltip customization parameters
- `popup_kwds` (dict, optional): Popup customization parameters

**Style Parameters (`style_kwds`):**
- `fillOpacity` (float): Fill transparency (0-1)
- `weight` (float): Border line width
- `color` (str): Border color
- `fillColor` (str): Fill color (overridden by choropleth)

**Legend Parameters (`legend_kwds`):**
- `caption` (str): Legend title
- `max_labels` (int): Maximum number of legend labels
- `orientation` (str): Legend orientation ("vertical" or "horizontal")

**Returns:**
- `leafmap.Map`: Interactive choropleth map

**Examples:**
```python
# Basic choropleth
data.plot.choropleth(column="population", title="Population by County").show()

# Advanced styling
data.plot.choropleth(
    column="median_income",
    title="Median Household Income",
    cmap="RdYlBu_r",
    legend=True,
    tooltip=["NAME", "median_income"],
    popup=["NAME", "median_income", "total_households"],
    style_kwds={
        "fillOpacity": 0.7,
        "weight": 0.5,
        "color": "black"
    },
    legend_kwds={
        "caption": "Median Income ($)",
        "max_labels": 5
    }
).show()
```

## ⚡ Cache API

PyMapGIS provides a caching system for improved performance.

### `pymapgis.cache`

Global cache instance for manual cache operations.

#### `.get(key: str) -> Optional[Any]`

Retrieve a value from cache.

```python
value = pmg.cache.get("my_key")
```

#### `.put(key: str, value: Any, ttl: Optional[str] = None) -> None`

Store a value in cache with optional TTL.

```python
pmg.cache.put("my_key", "my_value", ttl="1h")
```

#### `.clear() -> None`

Clear all cached data.

```python
pmg.cache.clear()
```

#### Properties

- `.size` (int): Number of items in cache
- `.location` (str): Cache database file path

**Example:**
```python
# Check cache status
print(f"Cache has {pmg.cache.size} items")
print(f"Cache location: {pmg.cache.location}")

# Manual cache operations
pmg.cache.put("user_data", {"name": "John"}, ttl="24h")
user_data = pmg.cache.get("user_data")

# Clear cache
pmg.cache.clear()
```

## ⚙️ Settings API

Configuration management through `pymapgis.settings`.

### `pymapgis.settings`

Global settings object with the following attributes:

#### Cache Settings
- `cache_ttl` (str): Default cache time-to-live (default: "24h")
- `disable_cache` (bool): Disable caching entirely (default: False)
- `cache_dir` (str): Cache directory path (default: "./cache")

#### Request Settings
- `request_timeout` (int): HTTP request timeout in seconds (default: 30)
- `user_agent` (str): User agent string for HTTP requests
- `max_retries` (int): Maximum number of request retries (default: 3)

#### Data Source Settings
- `census_year` (int): Default Census data year (default: 2022)
- `census_api_key` (str, optional): Census API key for higher rate limits

**Example:**
```python
import pymapgis as pmg

# View current settings
print(pmg.settings)

# Modify settings
pmg.settings.cache_ttl = "12h"
pmg.settings.request_timeout = 60
pmg.settings.census_year = 2021

# Disable caching
pmg.settings.disable_cache = True
```

### Environment Variables

Settings can be configured via environment variables with `PYMAPGIS_` prefix:

```bash
export PYMAPGIS_CACHE_TTL="24h"
export PYMAPGIS_DISABLE_CACHE="false"
export PYMAPGIS_REQUEST_TIMEOUT="30"
export PYMAPGIS_CENSUS_YEAR="2022"
export PYMAPGIS_CENSUS_API_KEY="your_api_key"
```

## 📊 Data Sources

### Census ACS Variables

Common American Community Survey variable codes:

#### Population & Demographics
- `B01003_001E`: Total population
- `B25001_001E`: Total housing units
- `B08303_001E`: Total commuters

#### Housing
- `B25070_001E`: Total households (for cost burden calculation)
- `B25070_010E`: Households spending 30%+ of income on housing
- `B25077_001E`: Median home value
- `B25064_001E`: Median gross rent

#### Income & Employment
- `B19013_001E`: Median household income
- `B19301_001E`: Per capita income
- `B23025_003E`: Labor force
- `B23025_004E`: Employed population
- `B23025_005E`: Unemployed population

#### Education
- `B15003_022E`: Bachelor's degree
- `B15003_023E`: Master's degree
- `B15003_024E`: Professional degree
- `B15003_025E`: Doctorate degree

### Geographic Codes

#### State FIPS Codes (Common)
- `01`: Alabama
- `06`: California  
- `12`: Florida
- `17`: Illinois
- `36`: New York
- `48`: Texas

#### Geography Levels
- `state`: State boundaries (~50 features)
- `county`: County boundaries (~3,000 features)
- `tract`: Census tract boundaries (~80,000 features)
- `block group`: Block group boundaries (~240,000 features)

## 🔗 Type Hints

PyMapGIS uses comprehensive type hints for better IDE support:

```python
from typing import Optional, List, Dict, Any
import geopandas as gpd
import leafmap

def read(url: str, cache_ttl: Optional[str] = None) -> gpd.GeoDataFrame: ...
def choropleth(column: str, title: Optional[str] = None) -> leafmap.Map: ...
```

## 🚨 Error Handling

Common exceptions and how to handle them:

```python
try:
    data = pmg.read("census://acs/acs5?year=2022&geography=county&variables=INVALID")
except ValueError as e:
    print(f"Invalid parameter: {e}")
except ConnectionError as e:
    print(f"Network error: {e}")
except TimeoutError as e:
    print(f"Request timeout: {e}")
```

## 💾 Vector Data Utilities

This section covers utilities for working with vector data, including conversions and operations.

### GeoArrow Conversion

PyMapGIS provides functions to convert GeoDataFrames to and from the GeoArrow format, an efficient columnar format for geospatial data based on Apache Arrow. This is useful for interoperability with other systems and for potentially faster I/O or operations within Arrow-native environments.

These utilities require the `geoarrow-py` library.

#### `pymapgis.vector.geodataframe_to_geoarrow()`

Converts a GeoPandas GeoDataFrame to a PyArrow Table with GeoArrow-encoded geometry.

```python
def geodataframe_to_geoarrow(gdf: gpd.GeoDataFrame) -> pa.Table:
    """
    Converts a GeoPandas GeoDataFrame to a PyArrow Table with GeoArrow-encoded geometry.

    Args:
        gdf (gpd.GeoDataFrame): The input GeoDataFrame.

    Returns:
        pa.Table: A PyArrow Table with geometry encoded in GeoArrow format.
                  CRS information is stored in the geometry field's metadata.
    """
    # Example:
    # import geopandas as gpd
    # from shapely.geometry import Point
    # from pymapgis.vector import geodataframe_to_geoarrow
    # data = {'id': [1], 'geometry': [Point(0, 0)]}
    # gdf = gpd.GeoDataFrame(data, crs="EPSG:4326")
    # arrow_table = geodataframe_to_geoarrow(gdf)
    # print(arrow_table.schema)
```

#### `pymapgis.vector.geoarrow_to_geodataframe()`

Converts a PyArrow Table (with GeoArrow-encoded geometry) back to a GeoPandas GeoDataFrame.

```python
def geoarrow_to_geodataframe(arrow_table: pa.Table, geometry_col_name: Optional[str] = None) -> gpd.GeoDataFrame:
    """
    Converts a PyArrow Table (with GeoArrow-encoded geometry) back to a GeoPandas GeoDataFrame.

    Args:
        arrow_table (pa.Table): Input PyArrow Table with a GeoArrow-encoded geometry column.
        geometry_col_name (Optional[str]): Name of the geometry column.
            If None, auto-detects the GeoArrow column.

    Returns:
        gpd.GeoDataFrame: A GeoPandas GeoDataFrame.
    """
    # Example:
    # # Assuming arrow_table from the previous example
    # from pymapgis.vector import geoarrow_to_geodataframe
    # gdf_roundtrip = geoarrow_to_geodataframe(arrow_table)
    # print(gdf_roundtrip.crs)
```

**Note on Zero-Copy:** While Apache Arrow is designed for zero-copy data access, converting to/from GeoDataFrames typically involves data copying and transformation. The primary benefits of these utilities are for efficient data serialization, storage, and interoperability with systems that understand the GeoArrow format.


## 🎞️ Raster Data (`pymapgis.raster`)

The `pymapgis.raster` module provides utilities for working with raster datasets, including cloud-optimized formats and spatio-temporal data structures.

### `lazy_windowed_read_zarr()`

Lazily reads a window of data from a specific level of a Zarr multiscale pyramid. This is particularly useful for efficiently accessing subsets of large, cloud-hosted raster datasets.

```python
def lazy_windowed_read_zarr(
    store_path_or_url: str,
    window: Dict[str, int],
    level: Union[str, int],
    consolidated: bool = True,
    multiscale_group_name: str = "",
    axis_order: str = "YX",
) -> xr.DataArray:
    """
    Args:
        store_path_or_url (str): Path or URL to the Zarr store.
        window (Dict[str, int]): Dictionary specifying the window {'x', 'y', 'width', 'height'}.
        level (Union[str, int]): Scale level to read from (integer index or string name).
        consolidated (bool): Whether Zarr metadata is consolidated.
        multiscale_group_name (str): Path to the multiscale group within Zarr store.
        axis_order (str): Axis order convention (e.g., "YX", "CYX").

    Returns:
        xr.DataArray: Lazily-loaded DataArray for the selected window and level.
    """
    # Example:
    # window = {'x': 1024, 'y': 2048, 'width': 512, 'height': 512}
    # data_chunk = pmg.raster.lazy_windowed_read_zarr("s3://my-zarr-bucket/image.zarr", window, level=0)
    # actual_data = data_chunk.compute() # Data is loaded here
```

### `create_spatiotemporal_cube()`

Creates a spatio-temporal cube (`xarray.DataArray`) by concatenating a list of 2D spatial `xr.DataArray` objects along a new time dimension.

```python
def create_spatiotemporal_cube(
    data_arrays: List[xr.DataArray],
    times: List[np.datetime64],
    time_dim_name: str = "time"
) -> xr.DataArray:
    """
    Args:
        data_arrays (List[xr.DataArray]): List of 2D spatial DataArrays.
                                           Must have identical spatial coordinates and dimensions.
        times (List[np.datetime64]): List of timestamps for each DataArray.
        time_dim_name (str): Name for the new time dimension (default: "time").

    Returns:
        xr.DataArray: A 3D (time, y, x) DataArray. CRS from the first input array is preserved.
    """
    # Example:
    # # Assuming da1, da2 are 2D xr.DataArrays with same spatial grid
    # times_list = [np.datetime64('2023-01-01'), np.datetime64('2023-01-02')]
    # space_time_cube = pmg.raster.create_spatiotemporal_cube([da1, da2], times_list)
```

### `reproject()`
(Already documented in Phase 1/2, ensure it's complete if not)
Re-projects an `xarray.DataArray` to a new Coordinate Reference System (CRS). (Details omitted if already present)

### `normalized_difference()`
(Already documented in Phase 1/2, ensure it's complete if not)
Computes the normalized difference between two bands of a raster. (Details omitted if already present)


## 🌐 Network Analysis (`pymapgis.network`)

The `pymapgis.network` module provides tools for creating network graphs from vector line data and performing common network analyses such as shortest path calculation and isochrone generation. It uses `NetworkX` as its underlying graph processing library.

**Important Note on Performance and Complexity:**
The functions provided are based on standard `NetworkX` algorithms. For very large networks (e.g., entire cities or regions), the performance of these algorithms (especially Dijkstra's for shortest path and isochrones) can be slow. More advanced techniques like Contraction Hierarchies (CH) or A* search with better heuristics are often used in production systems but are more complex to implement and might require specialized libraries. PyMapGIS may explore these in future enhancements. The current isochrone generation uses a convex hull, which is a simplification; more accurate isochrones might require alpha shapes or buffer-based methods.

### `create_network_from_geodataframe()`

Converts a GeoDataFrame of LineStrings (representing network segments) into a `networkx.Graph`.

```python
def create_network_from_geodataframe(
    gdf: gpd.GeoDataFrame,
    weight_col: Optional[str] = None,
    simplify_graph: bool = True
) -> nx.Graph:
    """
    Creates a NetworkX graph from a GeoDataFrame of LineStrings.
    Nodes are (x,y) coordinate tuples. Edges store 'length' (geometric)
    and 'weight' (derived from `weight_col` or defaults to length).

    Args:
        gdf (gpd.GeoDataFrame): Input GeoDataFrame with LineString geometries.
        weight_col (Optional[str]): Column for edge weights. Uses length if None.
        simplify_graph (bool): Placeholder for future graph simplification logic.
                               Currently has minimal effect.

    Returns:
        nx.Graph: The resulting network graph.
    """
    # Example:
    # streets_gdf = gpd.read_file("path/to/streets.shp")
    # streets_gdf['travel_time'] = streets_gdf.length / streets_gdf['speed_mph']
    # graph = pmg.network.create_network_from_geodataframe(streets_gdf, weight_col='travel_time')
```

### `find_nearest_node()`

Finds the closest graph node (coordinate tuple) to an arbitrary point.

```python
def find_nearest_node(graph: nx.Graph, point: Tuple[float, float]) -> Any:
    """
    Finds the closest graph node to an (x, y) coordinate tuple.

    Args:
        graph (nx.Graph): The NetworkX graph.
        point (Tuple[float, float]): The (x, y) coordinate.

    Returns:
        Any: The identifier of the nearest node (typically an (x,y) tuple).
             Returns None if graph is empty.
    """
    # Example:
    # my_coord = (123.45, 67.89)
    # nearest = pmg.network.find_nearest_node(graph, my_coord)
```

### `shortest_path()`

Calculates the shortest path between two nodes in the graph using a specified edge weight.

```python
def shortest_path(
    graph: nx.Graph,
    source_node: Tuple[float, float],
    target_node: Tuple[float, float],
    weight: str = 'length'
) -> Tuple[List[Tuple[float, float]], float]:
    """
    Calculates the shortest path using Dijkstra's algorithm.

    Args:
        graph (nx.Graph): The NetworkX graph.
        source_node (Tuple[float, float]): Start node (x,y) for the path.
        target_node (Tuple[float, float]): End node (x,y) for the path.
        weight (str): Edge attribute for cost (default: 'length').

    Returns:
        Tuple[List[Tuple[float, float]], float]: List of nodes in the path
                                                 and the total path cost.
    Raises:
        nx.NodeNotFound: If source or target node is not in the graph.
        nx.NetworkXNoPath: If no path exists.
    """
    # Example:
    # start_node = pmg.network.find_nearest_node(graph, (0,0))
    # end_node = pmg.network.find_nearest_node(graph, (10,10))
    # if start_node and end_node:
    #   path_nodes, cost = pmg.network.shortest_path(graph, start_node, end_node, weight='travel_time')
    #   print("Path:", path_nodes, "Cost:", cost)
```

### `generate_isochrone()`

Generates an isochrone polygon representing the reachable area from a source node within a maximum travel cost. The current implementation uses a convex hull of reachable nodes.

```python
def generate_isochrone(
    graph: nx.Graph,
    source_node: Tuple[float, float],
    max_cost: float,
    weight: str = 'length'
) -> gpd.GeoDataFrame:
    """
    Generates an isochrone (convex hull of reachable nodes).

    Args:
        graph (nx.Graph): The NetworkX graph.
        source_node (Tuple[float, float]): Source node (x,y) for the isochrone.
        max_cost (float): Maximum travel cost from the source.
        weight (str): Edge attribute for cost (default: 'length').
                      If None, cost is number of hops.

    Returns:
        gpd.GeoDataFrame: GeoDataFrame with the isochrone polygon. Empty if
                          fewer than 3 reachable nodes. Default CRS is EPSG:4326.
    """
    # Example:
    # origin = pmg.network.find_nearest_node(graph, (1,1))
    # if origin:
    #   isochrone_poly_gdf = pmg.network.generate_isochrone(graph, origin, max_cost=500, weight='length')
    #   isochrone_poly_gdf.plot()
```

## ☁️ Point Cloud (`pymapgis.pointcloud`)

The `pymapgis.pointcloud` module provides functionalities for reading and processing point cloud data, primarily LAS and LAZ files, leveraging the PDAL (Point Data Abstraction Library).

**Important Note on PDAL Installation:**
PDAL is a powerful library for point cloud processing, but it can be
challenging to install correctly with all its drivers and dependencies using pip alone.
It is **highly recommended to install PDAL using Conda**:
```bash
conda install -c conda-forge pdal python-pdal
```
If PDAL is not correctly installed and accessible in your Python environment, the functions in this module will likely fail.

### `read_point_cloud()`

Reads a point cloud file (e.g., LAS, LAZ) using a PDAL pipeline and returns the executed pipeline object.

```python
def read_point_cloud(filepath: str, **kwargs: Any) -> pdal.Pipeline:
    """
    Constructs and executes a PDAL pipeline to read the specified point cloud file.

    Args:
        filepath (str): Path to the point cloud file.
        **kwargs: Additional options passed to the PDAL reader stage (e.g., `count`).

    Returns:
        pdal.Pipeline: The executed PDAL pipeline object.
    """
    # Example:
    # pipeline = pmg.pointcloud.read_point_cloud("data/points.laz", count=100000)
    # points = pmg.pointcloud.get_point_cloud_points(pipeline)
```
The main `pymapgis.read()` function uses this internally when a `.las` or `.laz` file is provided, and directly returns the NumPy structured array of points.

### `get_point_cloud_points()`

Extracts points as a NumPy structured array from an executed PDAL pipeline.

```python
def get_point_cloud_points(pipeline: pdal.Pipeline) -> np.ndarray:
    """
    Args:
        pipeline (pdal.Pipeline): An executed PDAL pipeline.

    Returns:
        np.ndarray: Structured NumPy array of points. Fields correspond to
                    dimensions like 'X', 'Y', 'Z', 'Intensity'.
    """
```

### `get_point_cloud_metadata()`

Extracts metadata from an executed PDAL pipeline.

```python
def get_point_cloud_metadata(pipeline: pdal.Pipeline) -> Dict[str, Any]:
    """
    Args:
        pipeline (pdal.Pipeline): An executed PDAL pipeline.

    Returns:
        Dict[str, Any]: Dictionary of metadata, including quickinfo, schema, etc.
    """
```

### `get_point_cloud_srs()`

Extracts Spatial Reference System (SRS) information (typically WKT) from an executed PDAL pipeline.

```python
def get_point_cloud_srs(pipeline: pdal.Pipeline) -> str:
    """
    Args:
        pipeline (pdal.Pipeline): An executed PDAL pipeline.

    Returns:
        str: SRS information, usually in WKT format. Empty if not found.
    """
```

## 🌊 Streaming Data (`pymapgis.streaming`)

The `pymapgis.streaming` module provides utilities for connecting to real-time data streams like Kafka and MQTT, and for handling time-series data.

**Note on Optional Dependencies:**
Kafka and MQTT functionalities require extra dependencies. Install them using:
```bash
pip install pymapgis[kafka]  # For Kafka support
pip install pymapgis[mqtt]   # For MQTT support
pip install pymapgis[streaming] # For both
```

### `connect_kafka_consumer()`

Establishes a connection to a Kafka topic and returns a `kafka.KafkaConsumer`.

```python
def connect_kafka_consumer(
    topic: str,
    bootstrap_servers: Union[str, List[str]] = 'localhost:9092',
    group_id: Optional[str] = None,
    auto_offset_reset: str = 'earliest',
    consumer_timeout_ms: float = 1000,
    **kwargs: Any
) -> kafka.KafkaConsumer:
    """
    Args:
        topic (str): Kafka topic to subscribe to.
        bootstrap_servers (Union[str, List[str]]): Kafka broker addresses.
        group_id (Optional[str]): Consumer group ID.
        auto_offset_reset (str): Offset reset policy ('earliest', 'latest').
        consumer_timeout_ms (float): Timeout for consumer blocking.
        **kwargs: Additional arguments for kafka.KafkaConsumer.

    Returns:
        kafka.KafkaConsumer: Configured KafkaConsumer instance.
    """
    # Example:
    # consumer = pmg.streaming.connect_kafka_consumer(
    #     'my_sensor_topic',
    #     bootstrap_servers='my_kafka_broker:9092',
    #     value_deserializer=lambda v: json.loads(v.decode('utf-8')))
    # for message in consumer:
    #     print(message.value)
```

### `connect_mqtt_client()`

Creates, configures, and connects an MQTT client, starting its network loop.

```python
def connect_mqtt_client(
    broker_address: str = "localhost",
    port: int = 1883,
    client_id: str = "",
    keepalive: int = 60,
    **kwargs: Any
) -> mqtt.Client:
    """
    Args:
        broker_address (str): MQTT broker address.
        port (int): MQTT broker port.
        client_id (str): MQTT client ID.
        keepalive (int): Keepalive interval in seconds.
        **kwargs: Additional arguments (currently not used by paho.mqtt.Client constructor directly).

    Returns:
        paho.mqtt.client.Client: Connected Paho MQTT client with loop started.
    """
    # Example:
    # def my_on_message_callback(client, userdata, msg):
    #     print(f"Topic: {msg.topic}, Payload: {msg.payload.decode()}")
    #
    # mqtt_client = pmg.streaming.connect_mqtt_client("test.mosquitto.org")
    # mqtt_client.on_message = my_on_message_callback
    # mqtt_client.subscribe("geospatial/data/#")
```

### `create_spatiotemporal_cube_from_numpy()` (in `pymapgis.streaming`)

Creates a spatiotemporal data cube (`xarray.DataArray`) from NumPy arrays. This is useful for structuring raw sensor data streams.

```python
def create_spatiotemporal_cube_from_numpy(
    data: np.ndarray,
    timestamps: Union[List, np.ndarray, pd.DatetimeIndex],
    x_coords: np.ndarray,
    y_coords: np.ndarray,
    z_coords: Optional[np.ndarray] = None,
    variable_name: str = 'sensor_value',
    attrs: Optional[Dict[str, Any]] = None
) -> xr.DataArray:
    """
    Args:
        data (np.ndarray): Data values (time, [z], y, x).
        timestamps (Union[List, np.ndarray, pd.DatetimeIndex]): Timestamps for 'time' coordinate.
        x_coords (np.ndarray): X-coordinates.
        y_coords (np.ndarray): Y-coordinates.
        z_coords (Optional[np.ndarray]): Z-coordinates (optional).
        variable_name (str): Name for the data variable.
        attrs (Optional[Dict[str, Any]]): Attributes for the DataArray.

    Returns:
        xr.DataArray: Spatiotemporal data cube.
    """
```
**Note:** Another `create_spatiotemporal_cube` exists in `pymapgis.raster` which takes a list of `xr.DataArray` objects.


## Extended Plotting API (`pymapgis.viz.deckgl_utils`)

PyMapGIS provides 3D visualization capabilities using `pydeck` for deck.gl integration, particularly useful for point clouds and spatio-temporal data.

**Note on PyDeck Installation:**
Requires `pydeck` to be installed (`pip install pydeck`) and a compatible Jupyter environment (Notebook or Lab with pydeck extension).

### `view_3d_cube()`

Visualizes a 2D slice of a 3D (time, y, x) `xarray.DataArray` using `pydeck`.

```python
def view_3d_cube(
    cube: xr.DataArray,
    time_index: int = 0,
    variable_name: str = "value",
    colormap: str = "viridis",
    opacity: float = 0.8,
    cell_size: int = 1000,
    elevation_scale: float = 100,
    **kwargs_pydeck_layer
) -> pydeck.Deck:
    """
    Args:
        cube (xr.DataArray): 3D DataArray (time, y, x).
        time_index (int): Time slice to visualize.
        variable_name (str): Name of the variable in the cube.
        colormap (str): Matplotlib colormap name or custom color list.
        opacity (float): Layer opacity.
        cell_size (int): Grid cell size in meters.
        elevation_scale (float): Scaling for elevation.
        **kwargs_pydeck_layer: Additional arguments for pydeck.Layer.

    Returns:
        pydeck.Deck: A pydeck.Deck object for display.
    """
    # Example:
    # # Assuming 'my_cube' is an xarray.DataArray (time, y, x)
    # deck_render = pmg.viz.view_3d_cube(my_cube, time_index=0)
    # deck_render.show() # In Jupyter
```

### `view_point_cloud_3d()`

Visualizes a point cloud (NumPy array) using `pydeck.PointCloudLayer`.

```python
def view_point_cloud_3d(
    points: np.ndarray,
    srs: str = "EPSG:4326",
    point_size: int = 3,
    color: list = [255, 0, 0, 180],
    **kwargs_pydeck_layer
) -> pydeck.Deck:
    """
    Args:
        points (np.ndarray): NumPy structured array with 'X', 'Y', 'Z' fields.
        srs (str): SRS of input coordinates (informational, assumes lon/lat for map).
        point_size (int): Point size in pixels.
        color (list): Default point color [R,G,B,A].
        **kwargs_pydeck_layer: Additional arguments for pydeck.Layer('PointCloudLayer', ...).
                               Example: get_color='[Red, Green, Blue]' if color fields exist.

    Returns:
        pydeck.Deck: A pydeck.Deck object for display.
    """
    # Example:
    # # Assuming 'point_array' is a NumPy structured array from pmg.read("points.las")
    # deck_render = pmg.viz.view_point_cloud_3d(point_array, point_size=2)
    # deck_render.show() # In Jupyter
```

---

For more examples and tutorials, see the [User Guide](user-guide.md) and [Examples](examples.md).
