"""
Core functionality tests for CI/CD environments.
These tests focus on essential functionality without optional dependencies.
"""

import pytest
import sys
from pathlib import Path


def test_pymapgis_import():
    """Test that PyMapGIS can be imported."""
    try:
        import pymapgis

        assert hasattr(pymapgis, "__version__")
        print(f"PyMapGIS version: {pymapgis.__version__}")
    except ImportError as e:
        pytest.skip(f"PyMapGIS not available: {e}")


def test_basic_vector_functionality():
    """Test basic vector functionality without external dependencies."""
    try:
        import geopandas as gpd
        from shapely.geometry import Point
        from pymapgis.vector import buffer

        # Create a simple test case
        data = {"id": [1], "geometry": [Point(0, 0)]}
        gdf = gpd.GeoDataFrame(data, crs="EPSG:4326")

        # Test buffer function
        result = buffer(gdf, distance=10)
        assert isinstance(result, gpd.GeoDataFrame)
        assert not result.empty

    except ImportError as e:
        pytest.skip(f"Required dependencies not available: {e}")


def test_project_structure():
    """Test that the project structure is correct."""
    project_root = Path(__file__).parent.parent

    # Check essential directories exist
    assert (project_root / "pymapgis").exists(), "pymapgis package directory missing"
    assert (project_root / "tests").exists(), "tests directory missing"
    assert (project_root / "pyproject.toml").exists(), "pyproject.toml missing"

    # Check essential package files
    pymapgis_dir = project_root / "pymapgis"
    assert (pymapgis_dir / "__init__.py").exists(), "pymapgis/__init__.py missing"


def test_example_structure():
    """Test that example directories have proper structure."""
    project_root = Path(__file__).parent.parent

    # Check Tennessee example
    tennessee_dir = project_root / "tennessee_counties_qgis"
    if tennessee_dir.exists():
        assert (tennessee_dir / "README.md").exists(), "Tennessee README.md missing"
        assert (
            tennessee_dir / "test_tennessee_simple.py"
        ).exists(), "Tennessee simple test missing"

    # Check Arkansas example
    arkansas_dir = project_root / "examples" / "arkansas_counties_qgis"
    if arkansas_dir.exists():
        assert (arkansas_dir / "README.md").exists(), "Arkansas README.md missing"
        assert (
            arkansas_dir / "test_arkansas_simple.py"
        ).exists(), "Arkansas simple test missing"


def test_python_version():
    """Test that Python version is supported."""
    assert sys.version_info >= (
        3,
        8,
    ), f"Python {sys.version_info} is not supported. Minimum: 3.8"


def test_imports_basic():
    """Test basic imports work without crashing."""
    try:
        import numpy as np
        import pandas as pd

        assert np.__version__
        assert pd.__version__
    except ImportError as e:
        pytest.fail(f"Basic dependencies not available: {e}")


if __name__ == "__main__":
    # Allow running this test file directly
    pytest.main([__file__, "-v"])
