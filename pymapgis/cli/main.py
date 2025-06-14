"""
Main CLI implementation for PyMapGIS.

This module contains the core CLI commands and functionality.
"""

import typer
import os
import sys
import subprocess
import shutil
import importlib.metadata
from typing_extensions import Annotated

# Initialize global variables with proper typing
from typing import Any, Callable, Optional, Dict
import types

# Type definitions for better MyPy compatibility
pymapgis_module: Optional[types.ModuleType] = None
settings_obj: Any = None
stats_api_func: Optional[Callable[[], dict[Any, Any]]] = None
clear_cache_api_func: Optional[Callable[[], None]] = None
purge_cache_api_func: Optional[Callable[[], None]] = None

# Plugin functions
load_driver_plugins: Optional[Callable[[], dict[str, Any]]] = None
load_algorithm_plugins: Optional[Callable[[], dict[str, Any]]] = None
load_viz_backend_plugins: Optional[Callable[[], dict[str, Any]]] = None
PYMAPGIS_DRIVERS_GROUP = "pymapgis.drivers"
PYMAPGIS_ALGORITHMS_GROUP = "pymapgis.algorithms"
PYMAPGIS_VIZ_BACKENDS_GROUP = "pymapgis.viz_backends"

# Try to import pymapgis modules
try:
    import pymapgis as _pymapgis

    pymapgis_module = _pymapgis

    from pymapgis.settings import settings as _settings

    settings_obj = _settings

    from pymapgis.cache import (
        stats as _stats_api,
        clear as _clear_cache_api,
        purge as _purge_cache_api,
    )

    stats_api_func = _stats_api
    clear_cache_api_func = _clear_cache_api
    purge_cache_api_func = _purge_cache_api

    try:
        from pymapgis.plugins import (
            load_driver_plugins as _load_driver_plugins,
            load_algorithm_plugins as _load_algorithm_plugins,
            load_viz_backend_plugins as _load_viz_backend_plugins,
            PYMAPGIS_DRIVERS_GROUP as _PYMAPGIS_DRIVERS_GROUP,
            PYMAPGIS_ALGORITHMS_GROUP as _PYMAPGIS_ALGORITHMS_GROUP,
            PYMAPGIS_VIZ_BACKENDS_GROUP as _PYMAPGIS_VIZ_BACKENDS_GROUP,
        )

        load_driver_plugins = _load_driver_plugins
        load_algorithm_plugins = _load_algorithm_plugins
        load_viz_backend_plugins = _load_viz_backend_plugins
        PYMAPGIS_DRIVERS_GROUP = _PYMAPGIS_DRIVERS_GROUP
        PYMAPGIS_ALGORITHMS_GROUP = _PYMAPGIS_ALGORITHMS_GROUP
        PYMAPGIS_VIZ_BACKENDS_GROUP = _PYMAPGIS_VIZ_BACKENDS_GROUP
    except ImportError:
        # Plugins might not be available - keep defaults
        pass

except ImportError as e:
    # This allows the CLI to be somewhat functional for --help even if pymapgis isn't fully installed
    print(
        f"Warning: Could not import pymapgis modules: {e}.\nCertain CLI features might be unavailable.",
        file=sys.stderr,
    )

    # Define dummy versions/settings for basic CLI functionality if pymapgis is not found
    class DummySettings:
        cache_dir = "pymapgis not found"
        default_crs = "pymapgis not found"

    settings_obj = DummySettings()

    class DummyPymapgis:
        __version__ = "unknown"
        __file__ = "unknown"

    pymapgis_module = DummyPymapgis()  # type: ignore


app = typer.Typer(
    name="pymapgis",
    help="PyMapGIS: Modern GIS toolkit for Python.",
    add_completion=True,
)


# --- Helper function to get package versions ---
def get_package_version(package_name: str) -> str:
    try:
        return importlib.metadata.version(package_name)
    except importlib.metadata.PackageNotFoundError:
        return "Not installed"


# --- Info Command ---
@app.command()
def info():
    """
    Displays information about the PyMapGIS installation and its environment.
    """
    global pymapgis_module, settings_obj

    typer.echo(
        typer.style(
            "PyMapGIS Environment Information", fg=typer.colors.BRIGHT_GREEN, bold=True
        )
    )

    typer.echo("\nPyMapGIS:")
    if pymapgis_module:
        typer.echo(f"  Version: {pymapgis_module.__version__}")
    else:
        typer.echo("  Version: unknown")

    # Installation path
    try:
        if (
            pymapgis_module
            and hasattr(pymapgis_module, "__file__")
            and pymapgis_module.__file__ != "unknown"
        ):
            install_path = os.path.dirname(pymapgis_module.__file__)
            typer.echo(f"  Installation Path: {install_path}")
        else:
            typer.echo("  Installation Path: Unknown")
    except (AttributeError, TypeError):
        typer.echo("  Installation Path: Unknown")

    if settings_obj:
        typer.echo(f"  Cache Directory: {settings_obj.cache_dir}")
        typer.echo(f"  Default CRS: {settings_obj.default_crs}")
    else:
        typer.echo("  Cache Directory: Unknown")
        typer.echo("  Default CRS: Unknown")

    typer.echo("\nSystem:")
    typer.echo(f"  Python Version: {sys.version.splitlines()[0]}")
    typer.echo(f"  OS: {sys.platform}")

    typer.echo("\nCore Dependencies:")
    deps = [
        "geopandas",
        "rasterio",
        "xarray",
        "leafmap",
        "fastapi",
        "fsspec",
    ]
    for dep in deps:
        version = get_package_version(dep)
        typer.echo(f"  - {dep}: {version}")

    # Check rio CLI
    rio_path = shutil.which("rio")
    if rio_path:
        try:
            rio_version_out = subprocess.run(
                [rio_path, "--version"], capture_output=True, text=True, check=True
            )
            rio_version = rio_version_out.stdout.strip()
        except Exception:
            rio_version = f"Found at {rio_path}, but version check failed."
    else:
        rio_version = "Not found"
    typer.echo(f"  - rasterio CLI (rio): {rio_version}")


# --- Cache Subcommand ---
cache_app = typer.Typer(
    name="cache", help="Manage PyMapGIS cache.", no_args_is_help=True
)
app.add_typer(cache_app)


@cache_app.command(name="dir")
def cache_dir_command():
    """
    Display the path to the cache directory.
    """
    if settings_obj:
        typer.echo(settings_obj.cache_dir)
    else:
        typer.echo("Cache directory not available")


@cache_app.command(name="info")
def cache_info_command():
    """
    Displays detailed statistics about the PyMapGIS caches.
    """
    typer.echo(
        typer.style(
            "PyMapGIS Cache Information", fg=typer.colors.BRIGHT_BLUE, bold=True
        )
    )
    try:
        if stats_api_func:
            cache_stats = stats_api_func()
            if not cache_stats:
                typer.echo(
                    "Could not retrieve cache statistics. Cache might be disabled or not initialized."
                )
                return

            for key, value in cache_stats.items():
                friendly_key = key.replace("_", " ").title()
                if isinstance(value, bool):
                    status = (
                        typer.style("Enabled", fg=typer.colors.GREEN)
                        if value
                        else typer.style("Disabled", fg=typer.colors.RED)
                    )
                    typer.echo(f"  {friendly_key}: {status}")
                elif isinstance(value, (int, float)) and "bytes" in key:
                    # Convert bytes to human-readable format
                    if value > 1024 * 1024 * 1024:  # GB
                        val_hr = f"{value / (1024**3):.2f} GB"
                    elif value > 1024 * 1024:  # MB
                        val_hr = f"{value / (1024**2):.2f} MB"
                    elif value > 1024:  # KB
                        val_hr = f"{value / 1024:.2f} KB"
                    else:
                        val_hr = f"{value} Bytes"
                    typer.echo(f"  {friendly_key}: {val_hr} ({value} bytes)")
                else:
                    typer.echo(
                        f"  {friendly_key}: {value if value is not None else 'N/A'}"
                    )
        else:
            typer.echo("Cache statistics not available - cache module not loaded")
    except Exception as e:
        typer.secho(
            f"Error retrieving cache statistics: {e}", fg=typer.colors.RED, err=True
        )


@cache_app.command(name="clear")
def cache_clear_command():
    """
    Clears all PyMapGIS caches (requests and fsspec).
    """
    try:
        if clear_cache_api_func:
            clear_cache_api_func()
            typer.secho(
                "All PyMapGIS caches have been cleared successfully.",
                fg=typer.colors.GREEN,
            )
        else:
            typer.secho(
                "Cache clear function not available", fg=typer.colors.RED, err=True
            )
    except Exception as e:
        typer.secho(f"Error clearing caches: {e}", fg=typer.colors.RED, err=True)


@cache_app.command(name="purge")
def cache_purge_command():
    """
    Purges expired entries from the requests-cache.
    """
    try:
        if purge_cache_api_func:
            purge_cache_api_func()
            typer.secho(
                "Expired entries purged from requests-cache successfully.",
                fg=typer.colors.GREEN,
            )
        else:
            typer.secho(
                "Cache purge function not available", fg=typer.colors.RED, err=True
            )
    except Exception as e:
        typer.secho(f"Error purging cache: {e}", fg=typer.colors.RED, err=True)


# --- Rio Command (Pass-through) ---
# Note: Rio command temporarily disabled due to Typer compatibility issues in CI
# This will be re-enabled once the Typer version compatibility is resolved


# --- Doctor Command ---
@app.command()
def doctor():
    """
    Perform environment health checks for PyMapGIS.

    This command checks the installation and configuration of PyMapGIS
    and its dependencies, reporting any issues found.
    """
    typer.echo(
        typer.style(
            "PyMapGIS Environment Health Check", fg=typer.colors.BRIGHT_BLUE, bold=True
        )
    )

    issues_found = 0
    ok_color = typer.colors.GREEN
    warning_color = typer.colors.YELLOW
    error_color = typer.colors.RED

    # Check PyMapGIS installation
    typer.echo("\n--- PyMapGIS Installation ---")
    if pymapgis_module:
        typer.secho(f"✓ PyMapGIS version: {pymapgis_module.__version__}", fg=ok_color)
        typer.secho(
            f"✓ PyMapGIS location: {getattr(pymapgis_module, '__file__', 'unknown')}",
            fg=ok_color,
        )
    else:
        typer.secho("✗ PyMapGIS not properly installed", fg=error_color)
        issues_found += 1

    # Check core dependencies
    typer.echo("\n--- Core Dependencies ---")
    core_deps = [
        "geopandas",
        "xarray",
        "rioxarray",
        "pandas",
        "numpy",
        "fastapi",
        "uvicorn",
        "typer",
        "requests_cache",
        "fsspec",
    ]

    for dep in core_deps:
        try:
            version = importlib.metadata.version(dep)
            typer.secho(f"✓ {dep}: {version}", fg=ok_color)
        except importlib.metadata.PackageNotFoundError:
            typer.secho(f"✗ {dep}: Not installed", fg=error_color)
            issues_found += 1
        except Exception as e:
            typer.secho(f"? {dep}: Error checking version ({e})", fg=warning_color)

    # Check optional dependencies
    typer.echo("\n--- Optional Dependencies ---")
    optional_deps = [
        ("pdal", "Point cloud processing"),
        ("leafmap", "Interactive mapping"),
        ("mapbox_vector_tile", "Vector tile serving"),
        ("mercantile", "Tile utilities"),
        ("pyproj", "Coordinate transformations"),
        ("shapely", "Geometry operations"),
    ]

    for dep, description in optional_deps:
        try:
            version = importlib.metadata.version(dep)
            typer.secho(f"✓ {dep}: {version} ({description})", fg=ok_color)
        except importlib.metadata.PackageNotFoundError:
            typer.secho(f"- {dep}: Not installed ({description})", fg=warning_color)
        except Exception as e:
            typer.secho(f"? {dep}: Error checking version ({e})", fg=warning_color)

    # Check cache configuration
    typer.echo("\n--- Cache Configuration ---")
    if settings_obj:
        cache_dir = getattr(settings_obj, "cache_dir", "unknown")
        typer.secho(f"✓ Cache directory: {cache_dir}", fg=ok_color)

        # Check if cache directory exists and is writable
        try:
            from pathlib import Path

            cache_path = Path(cache_dir).expanduser()
            if cache_path.exists():
                if cache_path.is_dir():
                    typer.secho(
                        f"✓ Cache directory exists and is accessible", fg=ok_color
                    )
                else:
                    typer.secho(
                        f"✗ Cache path exists but is not a directory", fg=error_color
                    )
                    issues_found += 1
            else:
                typer.secho(
                    f"- Cache directory does not exist (will be created when needed)",
                    fg=warning_color,
                )
        except Exception as e:
            typer.secho(f"? Error checking cache directory: {e}", fg=warning_color)
    else:
        typer.secho("✗ Settings not available", fg=error_color)
        issues_found += 1

    # Check environment variables
    typer.echo("\n--- Environment Variables ---")
    env_vars = [
        ("PYMAPGIS_DISABLE_CACHE", "Cache control"),
        ("PROJ_LIB", "PROJ library path"),
        ("GDAL_DATA", "GDAL data path"),
    ]

    for var, description in env_vars:
        value = os.getenv(var)
        if value:
            typer.secho(f"✓ {var}: {value} ({description})", fg=ok_color)
        else:
            typer.secho(f"- {var}: Not set ({description})", fg=warning_color)

    # Summary
    typer.echo(typer.style("\n--- Summary ---", fg=typer.colors.BRIGHT_BLUE, bold=True))
    if issues_found == 0:
        typer.secho("✓ PyMapGIS environment looks healthy!", fg=ok_color, bold=True)
    else:
        typer.secho(
            f"⚠ Found {issues_found} potential issue(s). Review items marked with ✗.",
            fg=warning_color,
            bold=True,
        )
    typer.echo(
        "Note: Items marked with '-' are optional and may not affect functionality."
    )


# --- Plugin Subcommand ---
plugin_app = typer.Typer(
    name="plugin", help="Manage PyMapGIS plugins.", no_args_is_help=True
)
app.add_typer(plugin_app)


@plugin_app.command(name="list")
def plugin_list_command(
    verbose: bool = typer.Option(
        False, "--verbose", "-v", help="Show detailed plugin information"
    )
):
    """
    List installed PyMapGIS plugins.
    """
    typer.echo(
        typer.style(
            "PyMapGIS Installed Plugins", fg=typer.colors.BRIGHT_BLUE, bold=True
        )
    )

    try:
        # Import plugin loading functions
        from pymapgis.plugins import (
            load_driver_plugins,
            load_algorithm_plugins,
            load_viz_backend_plugins,
        )

        # Load plugins
        drivers = load_driver_plugins()
        algorithms = load_algorithm_plugins()  # type: ignore
        viz_backends = load_viz_backend_plugins()  # type: ignore

        total_plugins = len(drivers) + len(algorithms) + len(viz_backends)

        if total_plugins == 0:
            typer.echo("No plugins found.")
            return

        # Display drivers
        if drivers:
            typer.echo(f"\n--- Data Drivers ({len(drivers)}) ---")
            for name, plugin_class in drivers.items():
                if verbose:
                    typer.echo(
                        f"  {name}: {plugin_class.__module__}.{plugin_class.__name__}"
                    )
                    if hasattr(plugin_class, "__doc__") and plugin_class.__doc__:
                        typer.echo(f"    {plugin_class.__doc__.strip()}")
                else:
                    typer.echo(f"  {name}")

        # Display algorithms
        if algorithms:
            typer.echo(f"\n--- Algorithms ({len(algorithms)}) ---")
            for name, plugin_class in algorithms.items():  # type: ignore
                if verbose:
                    typer.echo(
                        f"  {name}: {plugin_class.__module__}.{plugin_class.__name__}"
                    )
                    if hasattr(plugin_class, "__doc__") and plugin_class.__doc__:
                        typer.echo(f"    {plugin_class.__doc__.strip()}")
                else:
                    typer.echo(f"  {name}")

        # Display visualization backends
        if viz_backends:
            typer.echo(f"\n--- Visualization Backends ({len(viz_backends)}) ---")
            for name, plugin_class in viz_backends.items():  # type: ignore
                if verbose:
                    typer.echo(
                        f"  {name}: {plugin_class.__module__}.{plugin_class.__name__}"
                    )
                    if hasattr(plugin_class, "__doc__") and plugin_class.__doc__:
                        typer.echo(f"    {plugin_class.__doc__.strip()}")
                else:
                    typer.echo(f"  {name}")

        typer.echo(f"\nTotal: {total_plugins} plugin(s) found")

    except ImportError as e:
        typer.secho(
            f"Error: Could not load plugin system: {e}", fg=typer.colors.RED, err=True
        )
    except Exception as e:
        typer.secho(f"Error: {e}", fg=typer.colors.RED, err=True)


@plugin_app.command(name="info")
def plugin_info_command(plugin_name: str):
    """
    Display detailed information about a specific plugin.
    """
    typer.echo(
        typer.style(
            f"Plugin Information: {plugin_name}", fg=typer.colors.BRIGHT_BLUE, bold=True
        )
    )

    try:
        # Import plugin loading functions
        from pymapgis.plugins import (
            load_driver_plugins,
            load_algorithm_plugins,
            load_viz_backend_plugins,
        )

        # Load all plugins
        all_plugins: Dict[str, Any] = {}
        all_plugins.update(load_driver_plugins())  # type: ignore
        all_plugins.update(load_algorithm_plugins())  # type: ignore
        all_plugins.update(load_viz_backend_plugins())  # type: ignore

        if plugin_name not in all_plugins:
            typer.secho(
                f"Plugin '{plugin_name}' not found.", fg=typer.colors.RED, err=True
            )
            typer.echo("Available plugins:")
            for name in sorted(all_plugins.keys()):
                typer.echo(f"  {name}")
            return

        plugin_class = all_plugins[plugin_name]

        typer.echo(f"Name: {plugin_name}")
        typer.echo(f"Class: {plugin_class.__module__}.{plugin_class.__name__}")

        if hasattr(plugin_class, "__doc__") and plugin_class.__doc__:
            typer.echo(f"Description: {plugin_class.__doc__.strip()}")

        # Try to get plugin type
        from pymapgis.plugins import (
            PymapgisDriver,
            PymapgisAlgorithm,
            PymapgisVizBackend,
        )

        if issubclass(plugin_class, PymapgisDriver):
            typer.echo("Type: Data Driver")
        elif issubclass(plugin_class, PymapgisAlgorithm):
            typer.echo("Type: Algorithm")
        elif issubclass(plugin_class, PymapgisVizBackend):
            typer.echo("Type: Visualization Backend")
        else:
            typer.echo("Type: Unknown")

        # Try to get version info from the module
        try:
            module = importlib.import_module(plugin_class.__module__.split(".")[0])
            if hasattr(module, "__version__"):
                typer.echo(f"Version: {module.__version__}")
        except Exception:
            pass

    except ImportError as e:
        typer.secho(
            f"Error: Could not load plugin system: {e}", fg=typer.colors.RED, err=True
        )
    except Exception as e:
        typer.secho(f"Error: {e}", fg=typer.colors.RED, err=True)


@plugin_app.command(name="install")
def plugin_install_command(plugin_spec: str):
    """
    Install a PyMapGIS plugin from PyPI or a git repository.

    Examples:
        pymapgis plugin install my-plugin-package
        pymapgis plugin install git+https://github.com/user/plugin.git
    """
    typer.echo(
        typer.style(
            f"Installing plugin: {plugin_spec}", fg=typer.colors.BRIGHT_BLUE, bold=True
        )
    )

    try:
        # Use pip to install the plugin
        import subprocess
        import sys

        # Determine if we're in a virtual environment
        pip_cmd = [sys.executable, "-m", "pip", "install", plugin_spec]

        typer.echo(f"Running: {' '.join(pip_cmd)}")

        result = subprocess.run(pip_cmd, capture_output=True, text=True, check=False)

        if result.returncode == 0:
            typer.secho(
                f"✓ Successfully installed {plugin_spec}", fg=typer.colors.GREEN
            )
            typer.echo("Run 'pymapgis plugin list' to see available plugins.")
        else:
            typer.secho(
                f"✗ Failed to install {plugin_spec}", fg=typer.colors.RED, err=True
            )
            typer.echo("Error output:")
            typer.echo(result.stderr)

    except Exception as e:
        typer.secho(f"Error: {e}", fg=typer.colors.RED, err=True)


@plugin_app.command(name="uninstall")
def plugin_uninstall_command(package_name: str):
    """
    Uninstall a PyMapGIS plugin package.

    Note: This uninstalls the entire package, not just the plugin entry points.
    """
    typer.echo(
        typer.style(
            f"Uninstalling plugin package: {package_name}",
            fg=typer.colors.BRIGHT_BLUE,
            bold=True,
        )
    )

    # Confirm before uninstalling
    if not typer.confirm(f"Are you sure you want to uninstall '{package_name}'?"):
        typer.echo("Cancelled.")
        return

    try:
        import subprocess
        import sys

        pip_cmd = [sys.executable, "-m", "pip", "uninstall", package_name, "-y"]

        typer.echo(f"Running: {' '.join(pip_cmd)}")

        result = subprocess.run(pip_cmd, capture_output=True, text=True, check=False)

        if result.returncode == 0:
            typer.secho(
                f"✓ Successfully uninstalled {package_name}", fg=typer.colors.GREEN
            )
        else:
            typer.secho(
                f"✗ Failed to uninstall {package_name}", fg=typer.colors.RED, err=True
            )
            typer.echo("Error output:")
            typer.echo(result.stderr)

    except Exception as e:
        typer.secho(f"Error: {e}", fg=typer.colors.RED, err=True)


if __name__ == "__main__":
    app()
