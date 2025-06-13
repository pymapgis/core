"""
PyMapGIS CLI Module (pmg.cli)

This module provides the command-line interface for PyMapGIS, offering utility
functions for managing PyMapGIS and interacting with geospatial data from the terminal.

The CLI is built using Typer for robust argument parsing and command structuring.
"""

# Import the main CLI app from the main module
from .main import app

# Import the global variables and functions that tests expect
from .main import (
    settings_obj as settings,
    clear_cache_api_func as clear_cache_api,
    purge_cache_api_func as purge_cache_api,
    stats_api_func as stats_api,
    load_driver_plugins,
    load_algorithm_plugins,
    load_viz_backend_plugins,
    pymapgis_module as pymapgis,
)

# Import shutil for tests that expect it
import shutil

__all__ = [
    "app",
    "settings",
    "clear_cache_api",
    "purge_cache_api",
    "stats_api",
    "load_driver_plugins",
    "load_algorithm_plugins",
    "load_viz_backend_plugins",
    "pymapgis",
    "shutil",
]
