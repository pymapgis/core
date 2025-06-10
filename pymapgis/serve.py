from fastapi import FastAPI, HTTPException
from fastapi.routing import APIRoute
from starlette.responses import Response, HTMLResponse
import uvicorn
import geopandas as gpd
import xarray as xr
from typing import Union, Any, Optional, Dict
import pymapgis  # To access pymapgis.read
from pymapgis.settings import settings  # Potentially for CRS defaults or other settings

# Raster specific imports
from rio_tiler.io import Reader as RioTilerReader  # Renamed to avoid conflict
from rio_tiler.profiles import img_profiles
from rio_tiler.utils import render as render_tile
from rio_tiler.utils import get_colormap

# Vector specific imports
from fastapi_mvt.utils import gdf_to_mvt
import mercantile  # For tile bounds if needed by gdf_to_mvt or for viewer

# For HTML viewer
import leafmap.leafmap as leafmap


# Global app instance that `serve` will configure and run
# This is a common pattern if serve is a blocking call.
# Alternatively, serve could return the app for more advanced usage.
_app = FastAPI()
_tile_server_data_source: Any = None
_tile_server_layer_name: str = "layer"
_service_type: Optional[str] = None  # "raster" or "vector"


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


@_app.get("/", response_class=HTMLResponse, tags=["Viewer"])
async def root_viewer():
    """Serves a simple HTML page with Leaflet to view the tile layer."""
    global _tile_server_layer_name, _service_type, _tile_server_data_source

    if _service_type is None or _tile_server_layer_name is None:
        return HTMLResponse(
            "<html><body><h1>PyMapGIS Tile Server</h1><p>No layer configured yet. Call serve() first.</p></body></html>"
        )

    m = leafmap.Map(center=(0, 0), zoom=2)  # Basic map
    tile_url_suffix = "png" if _service_type == "raster" else "mvt"
    tile_url = f"/xyz/{_tile_server_layer_name}/{{z}}/{{x}}/{{y}}.{tile_url_suffix}"

    if _service_type == "raster":
        m.add_tile_layer(
            tile_url, name=_tile_server_layer_name, attribution="PyMapGIS Raster"
        )
    elif _service_type == "vector":
        # Leafmap's add_vector_tile_layer or add_tile_layer might need specific styling options for MVT.
        # For simplicity, we use add_tile_layer which works for MVT if client like maplibre/mapbox handles styling.
        # Or, Leafmap might have a more specific MVT function.
        # `m.add_vector_tile_layer(tile_url, name=_tile_server_layer_name, attribution="PyMapGIS Vector")`
        # Check leafmap documentation for the best way to add MVT.
        # `add_tile_layer` is generic. For MVT, styling is client-side.
        # A simple MVT viewer might require Mapbox GL JS or similar.
        # Leaflet with VectorGrid plugin can show MVTs. Leafmap might wrap this.
        # For now, provide the URL; user can use with appropriate client.
        # Let's try with add_tile_layer and see if default Leafmap handles it or if it requires specific vector options.
        # Leafmap's `add_vector_tile_layer` is better.
        # It requires a style. If no style, it might not show much.
        # Let's just provide a simple HTML with the URL.

        # Fallback: Basic HTML if direct MVT display in leafmap is complex without styles
        # For a robust MVT viewer, one would typically use Mapbox GL JS or Leaflet with plugins + style.
        # Leafmap's add_vector_tile_layer requires a 'style' dict for Mapbox GL layers.
        # For a simple XYZ MVT layer in Leaflet via Leafmap, it might not show much without client-side styling.
        # A simple link is safer for Phase 1 if auto-styling is not trivial.

        # Try to add it directly. If it works, great.
        try:
            # A basic default style for `add_vector_tile_layer`
            # This is a Mapbox GL Style Spec. Layer ID should match the one in gdf_to_mvt.
            default_mvt_style = {
                _tile_server_layer_name: {  # Corresponds to layer_name in gdf_to_mvt
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
        except Exception:  # If add_vector_tile_layer fails or needs more complex setup
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
            with RioTilerReader(_tile_server_data_source) as src:
                bounds = src.bounds
                m.fit_bounds([[bounds[1], bounds[0]], [bounds[3], bounds[2]]])
        except Exception:
            pass  # Cannot get bounds, use default view

    return HTMLResponse(m.to_html())


def serve(
    data_source: Union[str, gpd.GeoDataFrame, xr.DataArray, xr.Dataset],
    layer_name: str = "layer",
    # service_type: str = "xyz", # service_type is inferred for now
    host: str = "127.0.0.1",
    port: int = 8000,
    **kwargs: Any,  # Placeholder for future rio-tiler options or other server configs
):
    """
    Serves geospatial data (rasters or vectors) as XYZ map tiles via a FastAPI app.

    Args:
        data_source (Union[str, gpd.GeoDataFrame, xr.DataArray, xr.Dataset]):
            The data to serve.
            - If str: Path to a raster file (COG recommended) or vector file readable by GeoPandas.
            - If gpd.GeoDataFrame: In-memory vector data.
            - If xr.DataArray/xr.Dataset: In-memory raster data.
              (Note: For Phase 1, raster serving primarily supports COG file paths due to rio-tiler's direct file handling optimization).
        layer_name (str, optional): Name for the layer in tile URLs. Defaults to "layer".
        host (str, optional): Host address to bind the server to. Defaults to "127.0.0.1".
        port (int, optional): Port number for the server. Defaults to 8000.
        **kwargs: Additional arguments. Currently unused, placeholder for future tile serving options.
    """
    global _tile_server_data_source, _tile_server_layer_name, _service_type, _app

    _tile_server_layer_name = layer_name

    if isinstance(data_source, str):
        # Try to read it to determine type
        try:
            # Type inference for string data_source:
            # This is currently a basic suffix-based approach.
            # Future improvements could include more robust methods like:
            #  - MIME type checking if the string is a URL.
            #  - Attempting to read with multiple libraries (e.g., try rasterio, then geopandas)
            #    for ambiguous file types or files without standard suffixes.
            file_suffix = data_source.split(".")[-1].lower()
            if file_suffix in ["shp", "geojson", "gpkg", "parquet", "geoparquet"]:
                _tile_server_data_source = pymapgis.read(data_source)
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
                _tile_server_data_source = data_source  # Keep as path for rio-tiler
                _service_type = "raster"
            else:
                # Default try read, could be vector or other
                print(f"Attempting to read {data_source} to infer type for serving...")
                loaded_data = pymapgis.read(data_source)
                if isinstance(loaded_data, gpd.GeoDataFrame):
                    _tile_server_data_source = loaded_data
                    _service_type = "vector"
                # Add check for xarray if pymapgis.read can return it directly for some string inputs
                # For now, if it's a path and not common vector, assume path for raster
                elif isinstance(loaded_data, (xr.DataArray, xr.Dataset)):
                    # This case implies pymapgis.read loaded it into memory.
                    # For Phase 1 raster, we want path.
                    print(
                        f"Warning: Loaded {data_source} as in-memory xarray object. Raster tile server expects a file path for now."
                    )
                    _tile_server_data_source = data_source  # Pass the original path
                    _service_type = "raster"
                else:
                    raise ValueError(
                        f"Unsupported file type or unable to infer service type for: {data_source}"
                    )

        except Exception as e:
            raise ValueError(
                f"Could not read or infer type of data_source string '{data_source}'. Ensure it's a valid path/URL to a supported file format. Original error: {e}"
            )

    elif isinstance(data_source, gpd.GeoDataFrame):
        _tile_server_data_source = data_source
        _service_type = "vector"
    elif isinstance(data_source, (xr.DataArray, xr.Dataset)):
        # For Phase 1, if an in-memory xarray object is passed, we raise NotImplemented
        # Or, we could try to save it to a temporary COG, but that's more involved.
        # For now, sticking to "path-based COG for Phase 1 raster serving".
        print(
            "Warning: Serving in-memory xarray.DataArray/Dataset directly is not fully supported for raster tiles in this version. Please provide a file path to a COG for best results with rio-tiler."
        )
        _tile_server_data_source = data_source  # Storing it, but the raster endpoint might fail if it's not a path
        _service_type = "raster"
        # The raster endpoint currently expects _tile_server_data_source to be a string path.
        # This will need adjustment if we want to serve in-memory xr.DataArray.
    else:
        raise TypeError(f"Unsupported data_source type: {type(data_source)}")

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

    # Dynamically prune FastAPI routes to only expose endpoints relevant to the selected service_type.
    # This approach modifies the global _app.routes list directly.
    # For more complex applications or if finer-grained control is needed, alternative FastAPI patterns
    # such as using APIRouters for different functionalities (e.g., one for raster, one for vector)
    # and conditionally including them in the main app, or using FastAPI's dependency injection system
    # to enable/disable routes or features, might be more conventional and maintainable.
    # However, for the current scope (single active layer type per server instance), this direct pruning is straightforward.
    active_routes = []
    for route in _app.routes:
        if isinstance(route, APIRoute):
            if route.path == "/" or "Viewer" in route.tags:  # Keep viewer
                active_routes.append(route)
            elif _service_type == "raster" and "Raster Tiles" in route.tags:
                active_routes.append(route)
            elif _service_type == "vector" and "Vector Tiles" in route.tags:
                active_routes.append(route)
    _app.routes = active_routes  # Prune routes

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
