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
from typing import Any, Callable, Optional
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
        if (pymapgis_module and
            hasattr(pymapgis_module, '__file__') and
            pymapgis_module.__file__ != "unknown"):
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
                    typer.echo(f"  {friendly_key}: {value if value is not None else 'N/A'}")
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
                "All PyMapGIS caches have been cleared successfully.", fg=typer.colors.GREEN
            )
        else:
            typer.secho("Cache clear function not available", fg=typer.colors.RED, err=True)
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
            typer.secho("Cache purge function not available", fg=typer.colors.RED, err=True)
    except Exception as e:
        typer.secho(f"Error purging cache: {e}", fg=typer.colors.RED, err=True)


# --- Rio Command (Pass-through) ---
@app.command(
    name="rio",
    help="Run Rasterio CLI commands. (Pass-through to 'rio' executable)",
    context_settings={"allow_extra_args": True, "ignore_unknown_options": True},
)
def rio_command(ctx: typer.Context):
    """
    Passes arguments directly to the 'rio' command-line interface.

    Example: pymapgis rio info my_raster.tif
    """
    rio_executable = shutil.which("rio")

    if not rio_executable:
        typer.secho(
            "Error: 'rio' (Rasterio CLI) not found in your system's PATH.",
            fg=typer.colors.RED,
            err=True,
        )
        typer.secho(
            "Please ensure Rasterio is installed correctly and 'rio' is accessible.",
            fg=typer.colors.RED,
            err=True,
        )
        raise typer.Exit(code=1)

    try:
        # Using list addition for arguments
        process_args = [rio_executable] + ctx.args
        result = subprocess.run(
            process_args, check=False
        )  # check=False to handle rio's own errors
        sys.exit(result.returncode)
    except Exception as e:
        typer.secho(
            f"Error executing 'rio' command: {e}", fg=typer.colors.RED, err=True
        )
        raise typer.Exit(code=1)


if __name__ == "__main__":
    app()
