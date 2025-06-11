__version__ = "0.3.2"

from pathlib import Path  # Existing import
from typing import (
    Union,
    Sequence,
    Hashable,
    Callable,
    Any,
    Optional,
    List,
)  # For type annotations


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
except ImportError:

    def read(uri: Union[str, Path], *, x="longitude", y="latitude", **kw):  # type: ignore[misc]
        raise ImportError("Could not import read function")


try:
    from .cache import _init_session, clear as clear_cache, stats, purge
except ImportError:

    def clear_cache() -> None:
        raise ImportError("Could not import cache functions")

    def stats() -> dict:
        raise ImportError("Could not import cache functions")

    def purge() -> None:
        raise ImportError("Could not import cache functions")


try:
    from .acs import get_county_table
except ImportError:

    def get_county_table(
        year: int,
        variables: Sequence[str],
        *,
        state: str | None = None,
        ttl: str = "6h",
    ):
        raise ImportError("Could not import ACS functions")


try:
    from .tiger import counties
except ImportError:

    def counties(year: int = 2022, scale: str = "500k"):
        raise ImportError("Could not import TIGER functions")


try:
    from .plotting import choropleth
except ImportError:

    def choropleth(
        gdf, column: str, *, cmap: str = "viridis", title: str | None = None
    ):
        raise ImportError("Could not import plotting functions")


try:
    from .vector import buffer, clip, overlay, spatial_join
except ImportError:

    def buffer(gdf, distance: float, **kwargs):
        raise ImportError("Could not import vector functions")

    def clip(gdf, mask_geometry, **kwargs):
        raise ImportError("Could not import vector functions")

    def overlay(gdf1, gdf2, how: str = "intersection", **kwargs):
        raise ImportError("Could not import vector functions")

    def spatial_join(
        left_gdf, right_gdf, op: str = "intersects", how: str = "inner", **kwargs
    ):
        raise ImportError("Could not import vector functions")


try:
    from .raster import reproject, normalized_difference
except ImportError:

    def reproject(data_array, target_crs: Union[str, int], **kwargs):  # type: ignore[misc]
        raise ImportError("Could not import raster functions")

    def normalized_difference(array, band1: Hashable, band2: Hashable):  # type: ignore[misc]
        raise ImportError("Could not import raster functions")


try:
    from .viz import explore, plot_interactive
except ImportError:

    def explore(data, m=None, **kwargs):  # type: ignore[misc]
        raise ImportError("Could not import viz functions")

    def plot_interactive(data, m=None, **kwargs):  # type: ignore[misc]
        raise ImportError("Could not import viz functions")


try:
    from .serve import serve
except ImportError:

    def serve(data, service_type: str = "xyz", layer_name: str = "layer", host: str = "127.0.0.1", port: int = 8000, **options):  # type: ignore[misc]
        raise ImportError("Could not import serve function")


try:
    from .async_processing import (
        AsyncGeoProcessor,
        async_read_large_file,
        async_process_in_chunks,
        parallel_geo_operations,
    )
except ImportError:

    def AsyncGeoProcessor(*args, **kwargs):  # type: ignore[no-redef]
        raise ImportError("Could not import async processing")

    async def async_read_large_file(filepath: Union[str, Path], chunk_size: int = 50000, **kwargs):  # type: ignore[misc]
        raise ImportError("Could not import async processing")

    async def async_process_in_chunks(filepath: Union[str, Path], operation: Callable, chunk_size: int = 50000, output_path: Optional[Union[str, Path]] = None, **kwargs):  # type: ignore[misc]
        raise ImportError("Could not import async processing")

    async def parallel_geo_operations(data_items: List[Any], operation: Callable, max_workers: Optional[int] = None, use_processes: bool = False):  # type: ignore[misc]
        raise ImportError("Could not import async processing")


try:
    from .cloud import (
        cloud_read,
        cloud_write,
        list_cloud_files,
        get_cloud_info,
        CloudStorageManager,
        register_s3_provider,
        register_gcs_provider,
        register_azure_provider,
    )
except ImportError:

    def cloud_read(cloud_url: str, provider_name: str = None, **kwargs):
        raise ImportError("Could not import cloud integration")

    def cloud_write(data, cloud_url: str, provider_name: str = None, **kwargs):
        raise ImportError("Could not import cloud integration")

    def list_cloud_files(cloud_url: str, provider_name: str = None, max_files: int = 1000):  # type: ignore[misc]
        raise ImportError("Could not import cloud integration")

    def get_cloud_info(cloud_url: str, provider_name: str = None):  # type: ignore[misc]
        raise ImportError("Could not import cloud integration")

    class CloudStorageManager:  # type: ignore[no-redef]
        def __init__(self, *args, **kwargs):
            raise ImportError("Could not import cloud integration")

    def register_s3_provider(name: str, bucket: str, region: str = None, **kwargs):  # type: ignore[misc]
        raise ImportError("Could not import cloud integration")

    def register_gcs_provider(name: str, bucket: str, project: str = None, **kwargs):  # type: ignore[misc]
        raise ImportError("Could not import cloud integration")

    def register_azure_provider(name: str, account_name: str, container: str, account_key: str = None, **kwargs):  # type: ignore[misc]
        raise ImportError("Could not import cloud integration")


try:
    from .performance import (
        optimize_performance,
        get_performance_stats,
        clear_performance_cache,
        enable_auto_optimization,
        disable_auto_optimization,
        PerformanceOptimizer,
        cache_result,
        lazy_load,
        profile_performance,
    )
except ImportError:

    def optimize_performance(obj, **kwargs):
        raise ImportError("Could not import performance optimization")

    def get_performance_stats():
        raise ImportError("Could not import performance optimization")

    def clear_performance_cache():
        raise ImportError("Could not import performance optimization")

    def enable_auto_optimization():
        raise ImportError("Could not import performance optimization")

    def disable_auto_optimization():
        raise ImportError("Could not import performance optimization")

    class PerformanceOptimizer:  # type: ignore[no-redef]
        def __init__(self, *args, **kwargs):
            raise ImportError("Could not import performance optimization")

    def cache_result(cache_key: str = None, ttl: int = None):
        raise ImportError("Could not import performance optimization")

    def lazy_load(func):
        raise ImportError("Could not import performance optimization")

    def profile_performance(func):
        raise ImportError("Could not import performance optimization")

# Authentication & Security
try:
    from .auth import (
        # API Keys
        APIKeyManager,
        APIKey,
        generate_api_key,
        validate_api_key,
        rotate_api_key,

        # OAuth
        OAuthManager,
        OAuthProvider,
        GoogleOAuthProvider,
        MicrosoftOAuthProvider,
        GitHubOAuthProvider,
        authenticate_oauth,
        refresh_oauth_token,

        # RBAC
        RBACManager,
        Role,
        Permission,
        User,
        create_role,
        assign_role,
        check_permission,
        has_permission,

        # Session Management
        SessionManager,
        Session,
        create_session,
        validate_session,
        invalidate_session,

        # Security
        SecurityConfig,
        encrypt_data,
        decrypt_data,
        hash_password,
        verify_password,
        generate_secure_token,

        # Middleware
        AuthenticationMiddleware,
        RateLimitMiddleware,
        SecurityMiddleware,
        require_auth,
        require_permission,
        rate_limit,

        # Manager instances
        get_api_key_manager,
        get_oauth_manager,
        get_rbac_manager,
        get_session_manager,

        # Convenience functions
        authenticate,
        authorize,
    )
except ImportError:

    def generate_api_key(name: str, scopes: List[str], expires_in_days: Optional[int] = None):
        raise ImportError("Could not import authentication features")

    def validate_api_key(raw_key: str, required_scope: Optional[str] = None):
        raise ImportError("Could not import authentication features")

    def authenticate_oauth(provider_name: str, user_id: str):
        raise ImportError("Could not import authentication features")

    def create_role(name: str, description: str, permissions: Optional[List[str]] = None):
        raise ImportError("Could not import authentication features")

    def assign_role(user_id: str, role_name: str):
        raise ImportError("Could not import authentication features")

    def check_permission(user_id: str, permission_name: str, resource: str = "*"):
        raise ImportError("Could not import authentication features")

    def create_session(user_id: str, timeout_seconds: Optional[int] = None):
        raise ImportError("Could not import authentication features")

    def validate_session(session_id: str, refresh: bool = True):
        raise ImportError("Could not import authentication features")

    def hash_password(password: str):
        raise ImportError("Could not import authentication features")

    def verify_password(password: str, hashed: str):
        raise ImportError("Could not import authentication features")

    def authenticate(api_key: str = None, oauth_token: str = None, session_id: str = None):
        raise ImportError("Could not import authentication features")

    def authorize(user_id: str, permission: str):
        raise ImportError("Could not import authentication features")

    class APIKeyManager:  # type: ignore[no-redef]
        def __init__(self, *args, **kwargs):
            raise ImportError("Could not import authentication features")

    class OAuthManager:  # type: ignore[no-redef]
        def __init__(self, *args, **kwargs):
            raise ImportError("Could not import authentication features")

    class RBACManager:  # type: ignore[no-redef]
        def __init__(self, *args, **kwargs):
            raise ImportError("Could not import authentication features")

    class SessionManager:  # type: ignore[no-redef]
        def __init__(self, *args, **kwargs):
            raise ImportError("Could not import authentication features")


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
    # Phase 3: Cloud integration
    "cloud_read",
    "cloud_write",
    "list_cloud_files",
    "get_cloud_info",
    "CloudStorageManager",
    "register_s3_provider",
    "register_gcs_provider",
    "register_azure_provider",
    # Phase 3: Performance optimization
    "optimize_performance",
    "get_performance_stats",
    "clear_performance_cache",
    "enable_auto_optimization",
    "disable_auto_optimization",
    "PerformanceOptimizer",
    "cache_result",
    "lazy_load",
    "profile_performance",
    # Package version
    "__version__",
]
