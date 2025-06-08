import typer
import os
import sys
import subprocess
import shutil
import importlib.metadata
from typing_extensions import Annotated # For Typer <0.10 compatibility if needed, Typer >=0.9 uses it.

# Assuming pymapgis.__version__ and settings are accessible
# This might require pymapgis to be installed or PYTHONPATH to be set correctly
# For development, it's common to have the package installable in editable mode.
try:
    import pymapgis
    from pymapgis.settings import settings
except ImportError as e:
    # This allows the CLI to be somewhat functional for --help even if pymapgis isn't fully installed/found,
    # though commands relying on its modules will fail.
    print(f"Warning: Could not import pymapgis modules: {e}. Some CLI features might not work.", file=sys.stderr)
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
    add_completion=True # Typer's default, but explicit can be good
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
    typer.echo(typer.style("PyMapGIS Environment Information", fg=typer.colors.BRIGHT_GREEN, bold=True))

    typer.echo("\nPyMapGIS:")
    typer.echo(f"  Version: {pymapgis.__version__}")
    typer.echo(f"  Cache Directory: {settings.cache_dir}")
    typer.echo(f"  Default CRS: {settings.default_crs}")

    typer.echo("\nSystem:")
    typer.echo(f"  Python Version: {sys.version.splitlines()[0]}")
    typer.echo(f"  OS: {sys.platform}") # More concise than os.name for common platforms

    typer.echo("\nKey Dependencies:")
    deps = ["geopandas", "xarray", "rioxarray", "rasterio", "leafmap", "fsspec", "pandas", "typer"]
    for dep in deps:
        typer.echo(f"  {dep}: {get_package_version(dep)}")

    rio_path = shutil.which('rio')
    if rio_path:
        try:
            rio_version_out = subprocess.run([rio_path, '--version'], capture_output=True, text=True, check=True)
            rio_version = rio_version_out.stdout.strip()
        except Exception:
            rio_version = f"Found at {rio_path}, but version check failed."
    else:
        rio_version = "Not found"
    typer.echo(f"  rasterio CLI (rio): {rio_version}")


# --- Cache Subcommand ---
cache_app = typer.Typer(name="cache", help="Manage PyMapGIS cache.", no_args_is_help=True)
app.add_typer(cache_app)

@cache_app.command(name="dir")
def cache_dir_command():
    """
    Prints the location of the PyMapGIS cache directory.
    """
    typer.echo(settings.cache_dir)

# --- Rio Command (Pass-through) ---
# Use Annotated for extra_args if needed, though Typer >=0.9 often handles it directly
# from typer import Context # Already imported via typer itself if needed

@app.command(
    name="rio",
    help="Run Rasterio CLI commands. (Pass-through to 'rio' executable)",
    context_settings={"allow_extra_args": True, "ignore_unknown_options": True}
)
def rio_command(ctx: typer.Context):
    """
    Passes arguments directly to the 'rio' command-line interface.

    Example: pymapgis rio insp /path/to/your/raster.tif
    """
    rio_executable = shutil.which('rio')

    if not rio_executable:
        typer.secho(
            "Error: 'rio' (Rasterio CLI) not found in your system's PATH.",
            fg=typer.colors.RED,
            err=True
        )
        typer.secho(
            "Please ensure Rasterio is installed correctly and 'rio' is accessible.",
            fg=typer.colors.RED,
            err=True
        )
        raise typer.Exit(code=1)

    try:
        # Using list addition for arguments
        process_args = [rio_executable] + ctx.args
        result = subprocess.run(process_args, check=False) # check=False to handle rio's own errors
        sys.exit(result.returncode)
    except Exception as e:
        typer.secho(f"Error executing 'rio' command: {e}", fg=typer.colors.RED, err=True)
        raise typer.Exit(code=1)

if __name__ == "__main__":
    app()
