import typer
import os
import sys
import subprocess
import shutil
import importlib.metadata
from typing_extensions import (
    Annotated,
)  # For Typer <0.10 compatibility if needed, Typer >=0.9 uses it.

# Assuming pymapgis.__version__ and settings are accessible
# This might require pymapgis to be installed or PYTHONPATH to be set correctly
# For development, it's common to have the package installable in editable mode.
try:
    import pymapgis
    from pymapgis.settings import settings
    from pymapgis.cache import (
        stats as stats_api,
        clear as clear_cache_api,
        purge as purge_cache_api,
    )
    from pymapgis.plugins import (
        load_driver_plugins,
        load_algorithm_plugins,
        load_viz_backend_plugins,
        PYMAPGIS_DRIVERS_GROUP,
        PYMAPGIS_ALGORITHMS_GROUP,
        PYMAPGIS_VIZ_BACKENDS_GROUP,
    )
except ImportError as e:
    # This allows the CLI to be somewhat functional for --help even if pymapgis isn't fully installed/found,
    # though commands relying on its modules will fail.
    print(
        f"Warning: Could not import pymapgis modules: {e}.\nCertain CLI features might be unavailable.",
        file=sys.stderr,
    )

    # Define dummy versions/settings for basic CLI functionality if pymapgis is not found
    class DummySettings:
        cache_dir = "pymapgis not found"
        default_crs = "pymapgis not found"

    settings = DummySettings()

    class DummyPymapgis:
        __version__ = "unknown"

    pymapgis = DummyPymapgis()


app = typer.Typer(
    name="pymapgis",
    help="PyMapGIS: Modern GIS toolkit for Python.",
    add_completion=True,  # Typer's default, but explicit can be good
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
    typer.echo(
        typer.style(
            "PyMapGIS Environment Information", fg=typer.colors.BRIGHT_GREEN, bold=True
        )
    )

    typer.echo("\nPyMapGIS:")
    typer.echo(f"  Version: {pymapgis.__version__}")
    typer.echo(f"  Cache Directory: {settings.cache_dir}")
    typer.echo(f"  Default CRS: {settings.default_crs}")

    typer.echo("\nSystem:")
    typer.echo(f"  Python Version: {sys.version.splitlines()[0]}")
    typer.echo(
        f"  OS: {sys.platform}"
    )  # More concise than os.name for common platforms

    typer.echo("\nKey Dependencies:")
    deps = [
        "geopandas",
        "xarray",
        "rioxarray",
        "rasterio",
        "leafmap",
        "fsspec",
        "pandas",
        "typer",
    ]
    for dep in deps:
        typer.echo(f"  {dep}: {get_package_version(dep)}")

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
    typer.echo(f"  rasterio CLI (rio): {rio_version}")

    typer.echo("\nNotes:")
    typer.echo("  - Compatibility: Typer (CLI) & Rasterio (core dep) both use 'click'.")
    typer.echo("    Version conflicts can arise. Ensure compatible versions or use a")
    typer.echo("    fresh environment. Poetry helps, but issues can still occur.")


@app.command(name="doctor")
def doctor_command():
    """
    Checks PyMapGIS dependencies and environment for potential issues.
    Provides a health check for the PyMapGIS installation.
    """
    typer.echo(
        typer.style(
            "PyMapGIS Doctor: Checking your environment...",
            fg=typer.colors.CYAN,
            bold=True,
        )
    )
    issues_found = 0
    ok_color = typer.colors.GREEN
    warning_color = typer.colors.YELLOW
    error_color = typer.colors.RED

    def print_check(
        label: str,
        value: str,
        status: str = "INFO",
        status_color: str = typer.colors.WHITE,
    ):
        nonlocal issues_found
        styled_status = typer.style(status, fg=status_color, bold=True)
        typer.echo(f"  {label:<30} [{styled_status:<10}] {value}")
        if status in ["WARNING", "ERROR", "NOT FOUND"]:
            issues_found += 1

    # --- PyMapGIS and System Information ---
    typer.echo(
        typer.style(
            "\n--- System Information ---", fg=typer.colors.BRIGHT_BLUE, bold=True
        )
    )
    print_check(
        "PyMapGIS Version",
        pymapgis.__version__,
        "INFO",
        ok_color if pymapgis.__version__ != "unknown" else warning_color,
    )
    print_check("Python Version", sys.version.splitlines()[0], "INFO", ok_color)
    print_check("Operating System", sys.platform, "INFO", ok_color)

    # --- Python Packages ---
    typer.echo(
        typer.style("\n--- Python Packages ---", fg=typer.colors.BRIGHT_BLUE, bold=True)
    )
    deps_to_check = [
        "geopandas",
        "xarray",
        "rioxarray",
        "rasterio",
        "shapely",
        "fiona",
        "pyproj",
        "leafmap",
        "fsspec",
        "pandas",
        "typer",
        "pydantic",
        "pydantic-settings",
        "requests",
        "requests-cache",
    ]
    for dep in deps_to_check:
        version = get_package_version(dep)
        status, color = (
            ("OK", ok_color)
            if version != "Not installed"
            else ("NOT FOUND", error_color)
        )
        print_check(dep, version, status, color)

    # --- Geospatial Libraries ---
    typer.echo(
        typer.style(
            "\n--- Geospatial Libraries ---", fg=typer.colors.BRIGHT_BLUE, bold=True
        )
    )
    # GDAL Version
    gdal_version_str = "Not found"
    gdal_status, gdal_color = "NOT FOUND", error_color
    try:
        import rasterio

        gdal_version_str = rasterio.gdal_version()
        gdal_status, gdal_color = "OK", ok_color
    except ImportError:
        gdal_version_str = "rasterio not installed"
        gdal_status, gdal_color = "ERROR", error_color
    except Exception as e:
        gdal_version_str = f"Error checking: {e}"
        gdal_status, gdal_color = "ERROR", error_color
    print_check("GDAL Version", gdal_version_str, gdal_status, gdal_color)

    # PROJ Version
    proj_version_str = "Not found"
    proj_status, proj_color = "NOT FOUND", error_color
    try:
        import pyproj

        proj_version_str = pyproj.proj_version_str
        proj_status, proj_color = "OK", ok_color
    except ImportError:
        proj_version_str = "pyproj not installed"
        proj_status, proj_color = "ERROR", error_color
    except Exception as e:
        proj_version_str = f"Error checking: {e}"
        proj_status, proj_color = "ERROR", error_color
    print_check("PROJ Version", proj_version_str, proj_status, proj_color)

    # --- Environment Variables ---
    typer.echo(
        typer.style(
            "\n--- Environment Variables ---", fg=typer.colors.BRIGHT_BLUE, bold=True
        )
    )
    proj_lib = os.getenv("PROJ_LIB")
    status_proj_lib, color_proj_lib = (
        ("SET", ok_color) if proj_lib else ("NOT SET", warning_color)
    )
    val_proj_lib = proj_lib if proj_lib else "Typically managed by Conda/PROJ install"
    print_check("PROJ_LIB", val_proj_lib, status_proj_lib, color_proj_lib)

    gdal_data = os.getenv("GDAL_DATA")
    status_gdal_data, color_gdal_data = (
        ("SET", ok_color) if gdal_data else ("NOT SET", warning_color)
    )
    val_gdal_data = (
        gdal_data if gdal_data else "Typically managed by Conda/GDAL install"
    )
    print_check("GDAL_DATA", val_gdal_data, status_gdal_data, color_gdal_data)

    gdal_version_env = os.getenv("GDAL_VERSION")
    status_gdal_version, color_gdal_version = (
        ("SET", ok_color) if gdal_version_env else ("NOT SET", warning_color)
    )
    val_gdal_version = (
        gdal_version_env
        if gdal_version_env
        else "If set, overrides GDAL version detected by libraries"
    )
    print_check(
        "GDAL_VERSION (env)", val_gdal_version, status_gdal_version, color_gdal_version
    )

    # --- rio CLI status ---
    typer.echo(
        typer.style("\n--- CLI Tools ---", fg=typer.colors.BRIGHT_BLUE, bold=True)
    )
    rio_path = shutil.which("rio")
    rio_version = "Not found"
    rio_status, rio_color = "NOT FOUND", error_color
    if rio_path:
        try:
            rio_version_out = subprocess.run(
                [rio_path, "--version"],
                capture_output=True,
                text=True,
                check=True,
                timeout=5,
            )
            rio_version = (
                f"Found: {rio_path}, Version: {rio_version_out.stdout.strip()}"
            )
            rio_status, rio_color = "OK", ok_color
        except subprocess.TimeoutExpired:
            rio_version = f"Found: {rio_path}, but version check timed out."
            rio_status, rio_color = "WARNING", warning_color
        except subprocess.CalledProcessError as e:
            rio_version = f"Found: {rio_path}, version check failed: {e.stderr.strip()}"
            rio_status, rio_color = "WARNING", warning_color
        except Exception as e:
            rio_version = f"Found at {rio_path}, error during version check: {e}"
            rio_status, rio_color = "WARNING", warning_color
    print_check("Rasterio CLI (rio)", rio_version, rio_status, rio_color)

    # --- Summary ---
    typer.echo(typer.style("\n--- Summary ---", fg=typer.colors.BRIGHT_BLUE, bold=True))
    if issues_found == 0:
        typer.secho("PyMapGIS environment looks healthy!", fg=ok_color, bold=True)
    else:
        typer.secho(
            f"Found {issues_found} potential issue(s). Review items marked WARNING or ERROR.",
            fg=warning_color,
            bold=True,
        )
    typer.echo("Note: 'NOT SET' for PROJ_LIB/GDAL_DATA is often normal in Conda envs.")


# --- Cache Subcommand ---
cache_app = typer.Typer(
    name="cache", help="Manage PyMapGIS cache.", no_args_is_help=True
)
app.add_typer(cache_app)


@cache_app.command(name="dir")
def cache_dir_command():
    """
    Prints the location of the PyMapGIS cache directory.
    """
    typer.echo(settings.cache_dir)


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
        cache_stats = stats_api()
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
                # Crude byte to human-readable format
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
        clear_cache_api()
        typer.secho(
            "All PyMapGIS caches have been cleared successfully.", fg=typer.colors.GREEN
        )
    except Exception as e:
        typer.secho(f"Error clearing caches: {e}", fg=typer.colors.RED, err=True)


@cache_app.command(name="purge")
def cache_purge_command():
    """
    Purges expired entries from the requests-cache.
    """
    try:
        purge_cache_api()
        typer.secho(
            "Expired entries purged from requests-cache successfully.",
            fg=typer.colors.GREEN,
        )
    except Exception as e:
        typer.secho(f"Error purging cache: {e}", fg=typer.colors.RED, err=True)


# --- Plugin Subcommand ---
plugin_app = typer.Typer(
    name="plugin", help="Manage PyMapGIS plugins.", no_args_is_help=True
)
app.add_typer(plugin_app)


def _list_plugins_by_group(
    group_name: str, loader_func: callable, verbose: bool = False
):
    """Helper to list plugins for a given group."""
    typer.echo(
        typer.style(f"\n--- {group_name} ---", fg=typer.colors.BRIGHT_CYAN, bold=True)
    )
    try:
        plugins = loader_func()
        if not plugins:
            typer.echo("  No plugins found for this group.")
            return

        for name, plugin_class in plugins.items():
            module_info = f" (from {plugin_class.__module__})" if verbose else ""
            typer.echo(f"  - {name}{module_info}")
    except Exception as e:
        typer.secho(
            f"  Error loading plugins for group {group_name}: {e}",
            fg=typer.colors.RED,
            err=True,
        )


@plugin_app.command(name="list")
def plugin_list_command(
    verbose: Annotated[
        bool,
        typer.Option(
            "--verbose", "-v", help="Show more plugin details (e.g., module origin)."
        ),
    ] = False,
):
    """
    Lists all discovered PyMapGIS plugins by group.
    """
    typer.echo(
        typer.style("Discovering PyMapGIS Plugins...", fg=typer.colors.CYAN, bold=True)
    )

    # Check if plugin functions are available (i.e., if pymapgis.plugins was imported)
    if "load_driver_plugins" not in globals():
        typer.secho(
            "Plugin system unavailable. PyMapGIS might be incompletely installed.",
            fg=typer.colors.RED,
            err=True,
        )
        raise typer.Exit(code=1)

    _list_plugins_by_group(
        f"Drivers ({PYMAPGIS_DRIVERS_GROUP})", load_driver_plugins, verbose
    )
    _list_plugins_by_group(
        f"Algorithms ({PYMAPGIS_ALGORITHMS_GROUP})", load_algorithm_plugins, verbose
    )
    _list_plugins_by_group(
        f"Visualization Backends ({PYMAPGIS_VIZ_BACKENDS_GROUP})",
        load_viz_backend_plugins,
        verbose,
    )


# --- Rio Command (Pass-through) ---
# Use Annotated for extra_args if needed, though Typer >=0.9 often handles it directly
# from typer import Context # Already imported via typer itself if needed


@app.command(
    name="rio",
    help="Run Rasterio CLI commands. (Pass-through to 'rio' executable)",
    context_settings={"allow_extra_args": True, "ignore_unknown_options": True},
)
def rio_command(ctx: typer.Context):
    """
    Passes arguments directly to the 'rio' command-line interface.

    Example: pymapgis rio insp /path/to/your/raster.tif
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
