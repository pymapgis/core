# Import dependencies with graceful fallbacks
import sys
from typing import Union, Any, Optional

# Core dependencies that should always be available
try:
    import geopandas as gpd
    import xarray as xr
except ImportError as e:
    print(f"Warning: Core dependencies not available: {e}", file=sys.stderr)
    raise

# FastAPI dependencies - required for serve functionality
try:
    from fastapi import FastAPI, HTTPException
    from fastapi.routing import APIRoute
    from starlette.responses import Response, HTMLResponse
    import uvicorn

    FASTAPI_AVAILABLE = True
except ImportError as e:
    print(f"Warning: FastAPI dependencies not available: {e}", file=sys.stderr)
    FASTAPI_AVAILABLE = False
    uvicorn = None

    # Create dummy classes for type hints
    class FastAPI:
        pass

    class HTTPException(Exception):
        pass

    class Response:
        pass

    class HTMLResponse:
        pass


# Raster serving dependencies
try:
    from rio_tiler.io import Reader as RioTilerReader
    from rio_tiler.profiles import img_profiles

    # Try different import paths for get_colormap
    try:
        from rio_tiler.colormap import get_colormap
    except ImportError:
        try:
            from rio_tiler.utils import get_colormap
        except ImportError:
            # Create a fallback colormap function
            def get_colormap(name):
                # Basic colormap fallback
                return {
                    0: [0, 0, 0, 0],  # transparent
                    255: [255, 255, 255, 255],  # white
                }

    RIO_TILER_AVAILABLE = True
except ImportError as e:
    print(f"Warning: rio-tiler not available: {e}", file=sys.stderr)
    RIO_TILER_AVAILABLE = False

    # Create dummy classes for type hints
    class RioTilerReader:
        pass

    img_profiles = {}

    def get_colormap(name):
        return {}

except Exception as e:
    print(f"Warning: rio-tiler compatibility issue: {e}", file=sys.stderr)
    RIO_TILER_AVAILABLE = False

    # Create dummy classes for type hints
    class RioTilerReader:
        pass

    img_profiles = {}

    def get_colormap(name):
        return {}


# Vector serving dependencies
try:
    import mapbox_vector_tile
    import mercantile

    VECTOR_DEPS_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Vector tile dependencies not available: {e}", file=sys.stderr)
    VECTOR_DEPS_AVAILABLE = False

# Coordinate transformation
try:
    from pyproj import Transformer

    PYPROJ_AVAILABLE = True
except ImportError as e:
    print(f"Warning: pyproj not available: {e}", file=sys.stderr)
    PYPROJ_AVAILABLE = False

# HTML viewer
try:
    import leafmap.leafmap as leafmap

    LEAFMAP_AVAILABLE = True
except ImportError as e:
    print(f"Warning: leafmap not available: {e}", file=sys.stderr)
    LEAFMAP_AVAILABLE = False

# Shapely for geometry operations
try:
    from shapely.geometry import box

    SHAPELY_AVAILABLE = True
except ImportError as e:
    print(f"Warning: shapely not available: {e}", file=sys.stderr)
    SHAPELY_AVAILABLE = False


def gdf_to_mvt(
    gdf: gpd.GeoDataFrame, x: int, y: int, z: int, layer_name: str = "layer"
) -> bytes:
    """
    Convert a GeoDataFrame to Mapbox Vector Tile (MVT) format for a specific tile.

    Args:
        gdf: GeoDataFrame in Web Mercator (EPSG:3857) projection
        x, y, z: Tile coordinates
        layer_name: Name for the layer in the MVT

    Returns:
        MVT tile as bytes
    """
    if not VECTOR_DEPS_AVAILABLE:
        raise ImportError(
            "Vector tile dependencies (mapbox_vector_tile, mercantile) not available"
        )

    if not PYPROJ_AVAILABLE:
        raise ImportError("pyproj not available for coordinate transformation")

    if not SHAPELY_AVAILABLE:
        raise ImportError("shapely not available for geometry operations")

    # Get tile bounds in Web Mercator
    tile_bounds = mercantile.bounds(x, y, z)

    # Convert bounds to a bounding box for clipping
    minx, miny, maxx, maxy = (
        tile_bounds.west,
        tile_bounds.south,
        tile_bounds.east,
        tile_bounds.north,
    )

    # Convert bounds to Web Mercator for clipping
    from pyproj import Transformer

    transformer = Transformer.from_crs("EPSG:4326", "EPSG:3857", always_xy=True)
    minx_merc, miny_merc = transformer.transform(minx, miny)
    maxx_merc, maxy_merc = transformer.transform(maxx, maxy)

    # Clip GeoDataFrame to tile bounds
    from shapely.geometry import box

    tile_bbox = box(minx_merc, miny_merc, maxx_merc, maxy_merc)
    clipped_gdf = gdf[gdf.geometry.intersects(tile_bbox)]

    if clipped_gdf.empty:
        # Return empty MVT
        return mapbox_vector_tile.encode({})

    # Convert to features for MVT encoding
    features = []
    for _, row in clipped_gdf.iterrows():
        try:
            # Convert geometry to tile coordinates (0-4096 range)
            geom = row.geometry

            # Get properties (exclude geometry column)
            # Use dict() to ensure we get a proper dictionary
            properties = {}
            for k in clipped_gdf.columns:
                if k != clipped_gdf.geometry.name:  # Use the actual geometry column name
                    try:
                        value = row[k]
                        # Convert any non-serializable types to strings
                        if not isinstance(value, (str, int, float, bool, type(None))):
                            properties[k] = str(value)
                        else:
                            properties[k] = value
                    except (KeyError, IndexError):
                        # Skip columns that can't be accessed
                        continue

            features.append({"geometry": geom.__geo_interface__, "properties": properties})
        except Exception as e:
            # Skip problematic features but continue processing
            print(f"Warning: Skipping feature due to error: {e}")
            continue

    # Create layer data
    layer_data = {
        layer_name: {"features": features, "extent": 4096}  # Standard MVT extent
    }

    # Encode as MVT
    return mapbox_vector_tile.encode(layer_data)


# Global app instance that `serve` will configure and run
# This is a common pattern if serve is a blocking call.
# Alternatively, serve could return the app for more advanced usage.
if FASTAPI_AVAILABLE:
    _app = FastAPI()
else:
    _app = None

_tile_server_data_source: Any = None
_tile_server_layer_name: str = "layer"
_service_type: Optional[str] = None  # "raster" or "vector"


# Define FastAPI routes only if FastAPI is available
if FASTAPI_AVAILABLE and _app is not None:

    @_app.get("/xyz/{layer_name}/{z}/{x}/{y}.png", tags=["Raster Tiles"])
    async def get_raster_tile(
        layer_name: str,
        z: int,
        x: int,
        y: int,
        rescale: Optional[str] = None,  # e.g., "0,1000"
        colormap: Optional[str] = None,  # e.g., "viridis"
    ):
        """Serve raster tiles in PNG format."""
        global _tile_server_data_source, _tile_server_layer_name, _service_type
        if _service_type != "raster" or layer_name != _tile_server_layer_name:
            raise HTTPException(
                status_code=404, detail="Raster layer not found or not configured"
            )

        if not isinstance(
            _tile_server_data_source, (str, xr.DataArray, xr.Dataset)
        ):  # Path or xarray object
            raise HTTPException(
                status_code=500, detail="Raster data source improperly configured."
            )

        # For Phase 1, _tile_server_data_source for raster is assumed to be a file path (COG)
        # In-memory xr.DataArray would require MemoryFile from rio_tiler.io or custom Reader
        if not isinstance(_tile_server_data_source, str):
            raise HTTPException(
                status_code=501,
                detail="Serving in-memory xarray data not yet supported for raster. Please provide a file path (e.g., COG).",
            )

        try:
            with RioTilerReader(_tile_server_data_source) as src:
                # rio-tiler can infer dataset parameters (min/max, etc.) or they can be passed
                # For multi-band imagery, 'indexes' or 'expression' might be needed in tile()
                img = src.tile(x, y, z)  # Returns an rio_tiler.models.ImageData object

                # Optional processing: rescale, colormap
                if rescale:
                    rescale_params = tuple(map(float, rescale.split(",")))
                    img.rescale(in_range=(rescale_params,))

                if colormap:
                    cmap = get_colormap(name=colormap)
                    img.apply_colormap(cmap)

                # Render to PNG
                # img_profiles["png"] gives default PNG creation options
                content = img.render(img_format="PNG", **img_profiles.get("png", {}))
                return Response(content, media_type="image/png")

        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to generate raster tile for {layer_name} at {z}/{x}/{y}. Error: {str(e)}",
            )

    @_app.get("/xyz/{layer_name}/{z}/{x}/{y}.mvt", tags=["Vector Tiles"])
    async def get_vector_tile(layer_name: str, z: int, x: int, y: int):
        """Serve vector tiles in MVT format."""
        global _tile_server_data_source, _tile_server_layer_name, _service_type
        if _service_type != "vector" or layer_name != _tile_server_layer_name:
            raise HTTPException(
                status_code=404, detail="Vector layer not found or not configured"
            )

        if not isinstance(_tile_server_data_source, gpd.GeoDataFrame):
            raise HTTPException(
                status_code=500, detail="Vector data source is not a GeoDataFrame."
            )

        try:
            # Reproject GDF to Web Mercator (EPSG:3857) if not already, as MVT is typically in this CRS
            gdf_web_mercator = _tile_server_data_source.to_crs(epsg=3857)

            # fastapi-mvt's gdf_to_mvt expects tile coordinates (x,y,z)
            # and other options like layer_name within the MVT, properties to include, etc.
            # By default, it uses all properties.
            # The 'layer_name' here is for the endpoint, 'id_column' and 'props_columns' can be passed to gdf_to_mvt.
            content = gdf_to_mvt(
                gdf_web_mercator, x, y, z, layer_name=layer_name
            )  # Pass endpoint layer_name as MVT internal layer_name
            return Response(content, media_type="application/vnd.mapbox-vector-tile")

        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to generate vector tile for {layer_name} at {z}/{x}/{y}. Error: {str(e)}",
            )

    @_app.get("/health", tags=["Health"])
    async def health_check():
        """Health check endpoint for Docker and monitoring."""
        try:
            from datetime import datetime
            health_status = {
                "status": "healthy",
                "timestamp": datetime.now().isoformat(),
                "version": "0.3.2",
                "service": "pymapgis-tile-server",
                "checks": {
                    "fastapi": "ok",
                    "dependencies": "ok"
                }
            }

            # Check if a layer is configured
            if _service_type and _tile_server_layer_name:
                health_status["checks"]["layer_configured"] = "ok"
                health_status["layer_info"] = {
                    "name": _tile_server_layer_name,
                    "type": _service_type
                }
            else:
                health_status["checks"]["layer_configured"] = "no_layer"
                health_status["message"] = "No layer configured"

            return health_status

        except Exception as e:
            from fastapi.responses import JSONResponse
            return JSONResponse(
                status_code=503,
                content={
                    "status": "unhealthy",
                    "error": str(e),
                    "timestamp": datetime.now().isoformat()
                }
            )

    @_app.get("/", response_class=HTMLResponse, tags=["Viewer"])
    async def root_viewer():
        """Serves a simple HTML page with Leaflet to view the tile layer."""
        global _tile_server_layer_name, _service_type, _tile_server_data_source

        if _service_type is None or _tile_server_layer_name is None:
            return HTMLResponse(
                "<html><body><h1>PyMapGIS Tile Server</h1><p>No layer configured yet. Call serve() first.</p></body></html>"
            )

        # Check if leafmap is available
        if not LEAFMAP_AVAILABLE:
            return HTMLResponse(
                f"""
                <html><head><title>PyMapGIS Viewer</title></head><body>
                <h1>PyMapGIS Tile Server</h1>
                <p>Serving layer '<strong>{_tile_server_layer_name}</strong>' ({_service_type}).</p>
                <p>Leafmap not available for interactive viewer. Install leafmap for full functionality.</p>
                </body></html>
                """
            )

        m = leafmap.Map(center=(0, 0), zoom=2)  # Basic map
        tile_url_suffix = "png" if _service_type == "raster" else "mvt"
        tile_url = f"/xyz/{_tile_server_layer_name}/{{z}}/{{x}}/{{y}}.{tile_url_suffix}"

        if _service_type == "raster":
            m.add_tile_layer(
                tile_url, name=_tile_server_layer_name, attribution="PyMapGIS Raster"
            )
        elif _service_type == "vector":
            # Try to add vector tile layer with basic styling
            try:
                # A basic default style for vector tiles
                default_mvt_style = {
                    _tile_server_layer_name: {
                        "fill_color": "#3388ff",
                        "weight": 1,
                        "color": "#3388ff",
                        "opacity": 0.7,
                        "fill_opacity": 0.5,
                    }
                }
                m.add_vector_tile_layer(
                    tile_url,
                    name=_tile_server_layer_name,
                    style=default_mvt_style,
                    attribution="PyMapGIS Vector",
                )
            except Exception:  # If add_vector_tile_layer fails
                return HTMLResponse(
                    f"""
                    <html><head><title>PyMapGIS Viewer</title></head><body>
                    <h1>PyMapGIS Tile Server</h1>
                    <p>Serving vector layer '<strong>{_tile_server_layer_name}</strong>' at <code>{tile_url}</code>.</p>
                    <p>To view MVT tiles, use a client like Mapbox GL JS, QGIS, or Leaflet with appropriate plugins.</p>
                    </body></html>
                    """
                )

        # Fit bounds if possible
        if _service_type == "vector" and isinstance(
            _tile_server_data_source, gpd.GeoDataFrame
        ):
            bounds = _tile_server_data_source.total_bounds  # [minx, miny, maxx, maxy]
            if len(bounds) == 4:
                m.fit_bounds(
                    [[bounds[1], bounds[0]], [bounds[3], bounds[2]]]
                )  # Leaflet format: [[lat_min, lon_min], [lat_max, lon_max]]
        elif _service_type == "raster" and isinstance(
            _tile_server_data_source, str
        ):  # Path to COG
            try:
                if RIO_TILER_AVAILABLE:
                    with RioTilerReader(_tile_server_data_source) as src:
                        bounds = src.bounds
                        m.fit_bounds([[bounds[1], bounds[0]], [bounds[3], bounds[2]]])
            except Exception:
                pass  # Cannot get bounds, use default view

        return HTMLResponse(m.to_html())


def serve(
    data: Union[str, gpd.GeoDataFrame, xr.DataArray, xr.Dataset],
    service_type: str = "xyz",
    layer_name: str = "layer",
    host: str = "127.0.0.1",
    port: int = 8000,
    **options: Any,  # Additional options for configuring the service
):
    """
    Serves geospatial data (rasters or vectors) as XYZ map tiles via a FastAPI app.

    Args:
        data (Union[str, gpd.GeoDataFrame, xr.DataArray, xr.Dataset]):
            The data to serve.
            - If str: Path to a raster file (COG recommended) or vector file readable by GeoPandas.
            - If gpd.GeoDataFrame: In-memory vector data.
            - If xr.DataArray/xr.Dataset: In-memory raster data.
              (Note: For Phase 1, raster serving primarily supports COG file paths due to rio-tiler's direct file handling optimization).
        service_type (str, optional): Type of service to create ('xyz'). Defaults to "xyz".
        layer_name (str, optional): Name for the layer in tile URLs. Defaults to "layer".
        host (str, optional): Host address to bind the server to. Defaults to "127.0.0.1".
        port (int, optional): Port number for the server. Defaults to 8000.
        **options: Additional options for configuring the service (e.g., styling, colormap).
    """
    # Check for required dependencies
    if not FASTAPI_AVAILABLE:
        raise ImportError(
            "FastAPI dependencies not available. Please install: pip install fastapi uvicorn"
        )

    global _tile_server_data_source, _tile_server_layer_name, _service_type, _app

    _tile_server_layer_name = layer_name

    if isinstance(data, str):
        # Try to read it to determine type
        try:
            # Type inference for string data:
            # This is currently a basic suffix-based approach.
            # Future improvements could include more robust methods like:
            #  - MIME type checking if the string is a URL.
            #  - Attempting to read with multiple libraries (e.g., try rasterio, then geopandas)
            #    for ambiguous file types or files without standard suffixes.
            file_suffix = data.split(".")[-1].lower()
            if file_suffix in ["shp", "geojson", "gpkg", "parquet", "geoparquet"]:
                # Import read function locally to avoid circular imports
                from .io import read

                _tile_server_data_source = read(data)
                _service_type = "vector"
            elif file_suffix in [
                "tif",
                "tiff",
                "cog",
                "nc",
            ]:  # Assuming .nc is read as xr.Dataset path for now
                # For raster, we expect a COG path for rio-tiler
                if file_suffix not in ["tif", "tiff", "cog"]:
                    print(
                        f"Warning: For raster tile serving, COG format is recommended. Provided: {file_suffix}"
                    )
                _tile_server_data_source = data  # Keep as path for rio-tiler
                _service_type = "raster"
            else:
                # Default try read, could be vector or other
                print(f"Attempting to read {data} to infer type for serving...")
                # Import read function locally to avoid circular imports
                from .io import read

                loaded_data = read(data)
                if isinstance(loaded_data, gpd.GeoDataFrame):
                    _tile_server_data_source = loaded_data
                    _service_type = "vector"
                # Add check for xarray if pymapgis.read can return it directly for some string inputs
                # For now, if it's a path and not common vector, assume path for raster
                elif isinstance(loaded_data, (xr.DataArray, xr.Dataset)):
                    # This case implies pymapgis.read loaded it into memory.
                    # For Phase 1 raster, we want path.
                    print(
                        f"Warning: Loaded {data} as in-memory xarray object. Raster tile server expects a file path for now."
                    )
                    _tile_server_data_source = data  # Pass the original path
                    _service_type = "raster"
                else:
                    raise ValueError(
                        f"Unsupported file type or unable to infer service type for: {data}"
                    )

        except Exception as e:
            raise ValueError(
                f"Could not read or infer type of data string '{data}'. Ensure it's a valid path/URL to a supported file format. Original error: {e}"
            )

    elif isinstance(data, gpd.GeoDataFrame):
        _tile_server_data_source = data
        _service_type = "vector"
    elif isinstance(data, (xr.DataArray, xr.Dataset)):
        # For Phase 1, if an in-memory xarray object is passed, we raise NotImplemented
        # Or, we could try to save it to a temporary COG, but that's more involved.
        # For now, sticking to "path-based COG for Phase 1 raster serving".
        print(
            "Warning: Serving in-memory xarray.DataArray/Dataset directly is not fully supported for raster tiles in this version. Please provide a file path to a COG for best results with rio-tiler."
        )
        _tile_server_data_source = (
            data  # Storing it, but the raster endpoint might fail if it's not a path
        )
        _service_type = "raster"
        # The raster endpoint currently expects _tile_server_data_source to be a string path.
        # This will need adjustment if we want to serve in-memory xr.DataArray.
    else:
        raise TypeError(f"Unsupported data type: {type(data)}")

    if _service_type == "raster" and not isinstance(_tile_server_data_source, str):
        # For future enhancement to support in-memory xarray objects for raster tiles:
        # This would likely involve using rio_tiler.io.MemoryFile.
        # Example sketch:
        # from rio_tiler.io import MemoryFile # Add to imports
        # # Assuming _tile_server_data_source is an xr.DataArray or xr.Dataset
        # if isinstance(_tile_server_data_source, (xr.DataArray, xr.Dataset)):
        #     try:
        #         # Ensure it has CRS and necessary spatial information
        #         if not (hasattr(_tile_server_data_source, 'rio') and _tile_server_data_source.rio.crs):
        #             raise ValueError("In-memory xarray object must have CRS for COG conversion.")
        #         cog_bytes = _tile_server_data_source.rio.to_cog() # Or .write_cog() depending on xarray/rioxarray version
        #         # Then use this cog_bytes with MemoryFile in the get_raster_tile endpoint:
        #         # In get_raster_tile:
        #         # if isinstance(_tile_server_data_source, bytes): # (after adjusting global type)
        #         #    with MemoryFile(_tile_server_data_source) as memfile:
        #         #        with RioTilerReader(memfile.name) as src:
        #         #             # ... proceed ...
        #         # This approach requires that the xarray object can be successfully converted to a COG in memory.
        #         print("Developer note: In-memory xarray to COG conversion for serving would happen here.")
        #     except Exception as e:
        #         raise NotImplementedError(f"Failed to prepare in-memory xarray for raster serving: {e}")
        # else: # Original error for non-string, non-xarray types for raster
        raise NotImplementedError(
            "Serving in-memory xarray objects as raster tiles is not yet fully supported. Please provide a file path (e.g., COG)."
        )

    # Note: Route pruning is disabled for now due to FastAPI route immutability
    # In a production environment, you might want to use APIRouters for different service types
    # and conditionally include them, or use dependency injection to control access
    # For now, all routes are available but will return 404 for inactive service types

    print(
        f"Starting PyMapGIS server for layer '{_tile_server_layer_name}' ({_service_type})."
    )
    print(f"View at: http://{host}:{port}/")
    if _service_type == "raster":
        print(
            f"Raster tiles: http://{host}:{port}/xyz/{_tile_server_layer_name}/{{z}}/{{x}}/{{y}}.png"
        )
    elif _service_type == "vector":
        print(
            f"Vector tiles: http://{host}:{port}/xyz/{_tile_server_layer_name}/{{z}}/{{x}}/{{y}}.mvt"
        )

    uvicorn.run(
        _app, host=host, port=port, log_level="info"
    )  # Or use **kwargs for uvicorn settings


if __name__ == "__main__":
    # Example Usage (for testing this file directly)
    # Create a dummy GeoDataFrame
    data = {"id": [1, 2], "geometry": ["POINT (0 0)", "POINT (1 1)"]}
    gdf = gpd.GeoDataFrame(
        data, geometry=gpd.GeoSeries.from_wkt(data["geometry"]), crs="EPSG:4326"
    )

    # To test raster, you'd need a COG file path, e.g.:
    # serve("path/to/your/cog.tif", layer_name="my_raster", service_type="raster")
    # For now, let's run with the GDF
    print("Starting example server with a dummy GeoDataFrame...")
    serve(gdf, layer_name="dummy_vector", host="127.0.0.1", port=8001)
