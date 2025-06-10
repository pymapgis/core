"""
PyMapGIS CLI Module (pmg.cli)

This module provides the command-line interface for PyMapGIS, offering utility
functions for managing PyMapGIS and interacting with geospatial data from the terminal.

The CLI is built using Typer for robust argument parsing and command structuring.
"""

# Import the main CLI app from the main module
from .main import app

__all__ = ["app"]
