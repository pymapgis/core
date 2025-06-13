"""
Entry point for running PyMapGIS CLI as a module.

This allows the CLI to be executed with: python -m pymapgis.cli
"""

from .main import app

if __name__ == "__main__":
    app()
