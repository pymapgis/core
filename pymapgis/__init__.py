__version__ = "0.3.0"

from pathlib import Path  # Existing import

# Lazy imports to avoid circular dependencies and improve startup time
def _lazy_import_io():
    from .io import read
    return read

def _lazy_import_cache():
    from .cache import _init_session, clear as clear_cache, stats, purge
    return _init_session, clear_cache, stats, purge

def _lazy_import_acs():
    from .acs import get_county_table
    return get_county_table

def _lazy_import_tiger():
    from .tiger import counties
    return counties

def _lazy_import_plotting():
    from .plotting import choropleth
    return choropleth

def _lazy_import_vector():
    from .vector import buffer, clip, overlay, spatial_join
    return buffer, clip, overlay, spatial_join

def _lazy_import_raster():
    from .raster import reproject, normalized_difference
    return reproject, normalized_difference

def _lazy_import_viz():
    from .viz import explore, plot_interactive
    return explore, plot_interactive

def _lazy_import_serve():
    from .serve import serve
    return serve

# Actually, let's use a simpler approach - direct imports but with try/except for robustness
try:
    from .io import read
except ImportError as e:
    def read(*args, **kwargs):
        raise ImportError(f"Could not import read function: {e}")

try:
    from .cache import _init_session, clear as clear_cache, stats, purge
except ImportError as e:
    def clear_cache(*args, **kwargs):
        raise ImportError(f"Could not import cache functions: {e}")
    def stats(*args, **kwargs):
        raise ImportError(f"Could not import cache functions: {e}")
    def purge(*args, **kwargs):
        raise ImportError(f"Could not import cache functions: {e}")

try:
    from .acs import get_county_table
except ImportError as e:
    def get_county_table(*args, **kwargs):
        raise ImportError(f"Could not import ACS functions: {e}")

try:
    from .tiger import counties
except ImportError as e:
    def counties(*args, **kwargs):
        raise ImportError(f"Could not import TIGER functions: {e}")

try:
    from .plotting import choropleth
except ImportError as e:
    def choropleth(*args, **kwargs):
        raise ImportError(f"Could not import plotting functions: {e}")

try:
    from .vector import buffer, clip, overlay, spatial_join
except ImportError as e:
    def buffer(*args, **kwargs):
        raise ImportError(f"Could not import vector functions: {e}")
    def clip(*args, **kwargs):
        raise ImportError(f"Could not import vector functions: {e}")
    def overlay(*args, **kwargs):
        raise ImportError(f"Could not import vector functions: {e}")
    def spatial_join(*args, **kwargs):
        raise ImportError(f"Could not import vector functions: {e}")

try:
    from .raster import reproject, normalized_difference
except ImportError as e:
    def reproject(*args, **kwargs):
        raise ImportError(f"Could not import raster functions: {e}")
    def normalized_difference(*args, **kwargs):
        raise ImportError(f"Could not import raster functions: {e}")

try:
    from .viz import explore, plot_interactive
except ImportError as e:
    def explore(*args, **kwargs):
        raise ImportError(f"Could not import viz functions: {e}")
    def plot_interactive(*args, **kwargs):
        raise ImportError(f"Could not import viz functions: {e}")

try:
    from .serve import serve
except ImportError as e:
    def serve(*args, **kwargs):
        raise ImportError(f"Could not import serve function: {e}")

try:
    from .async_processing import (
        AsyncGeoProcessor,
        async_read_large_file,
        async_process_in_chunks,
        parallel_geo_operations
    )
except ImportError as e:
    def AsyncGeoProcessor(*args, **kwargs):
        raise ImportError(f"Could not import async processing: {e}")
    def async_read_large_file(*args, **kwargs):
        raise ImportError(f"Could not import async processing: {e}")
    def async_process_in_chunks(*args, **kwargs):
        raise ImportError(f"Could not import async processing: {e}")
    def parallel_geo_operations(*args, **kwargs):
        raise ImportError(f"Could not import async processing: {e}")


# Keep the set_cache function as a regular function since it's used for configuration
def set_cache(
    dir_: Path | str | None = None, *, ttl_days: int = 7
) -> None:  # Python 3.10+ type hint
    """
    Enable or disable caching at runtime.

    set_cache(None)        → disable
    set_cache("~/mycache") → enable & use that folder
    """
    import os
    from datetime import timedelta

    if dir_ is None:
        os.environ["PYMAPGIS_DISABLE_CACHE"] = "1"
    else:
        os.environ.pop("PYMAPGIS_DISABLE_CACHE", None)
        # Reset the global session
        try:
            import pymapgis.cache as cache_module
            cache_module._session = None  # type: ignore[attr-defined]
            from .cache import _init_session
            _init_session(dir_, expire_after=timedelta(days=ttl_days))
        except ImportError:
            pass  # Cache module not available


__all__ = [
    # Existing public API (order preserved)
    "read",
    "set_cache",
    "clear_cache",
    "stats",
    "purge",
    "get_county_table",
    "counties",
    "choropleth",
    # New additions from subtasks
    "buffer",
    "clip",
    "overlay",
    "spatial_join",
    "reproject",
    "normalized_difference",
    "explore",
    "plot_interactive",
    "serve",
    # Phase 3: Async processing
    "AsyncGeoProcessor",
    "async_read_large_file",
    "async_process_in_chunks",
    "parallel_geo_operations",
    # Package version
    "__version__",
]
