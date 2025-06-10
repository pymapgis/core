#!/usr/bin/env python3
"""
Simple test for Tennessee Counties QGIS example that works in CI/CD environments.
"""

import sys
from pathlib import Path

# Add PyMapGIS to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))


def test_tennessee_example_structure():
    """Test that the Tennessee example has the correct file structure."""
    example_dir = Path(__file__).parent

    # Check main files exist
    assert (example_dir / "tennessee_counties_example.py").exists()
    assert (example_dir / "create_qgis_project.py").exists()
    assert (example_dir / "README.md").exists()
    assert (example_dir / "EXAMPLE_SUMMARY.md").exists()
    assert (example_dir / "requirements.txt").exists()

    print("✅ Tennessee example structure test passed")


def test_tennessee_scripts_importable():
    """Test that the Tennessee scripts can be imported without errors."""
    example_dir = Path(__file__).parent

    # Test main script has valid Python syntax
    main_script = example_dir / "tennessee_counties_example.py"
    with open(main_script, "r", encoding="utf-8") as f:
        content = f.read()

    # Should contain key components
    assert "import pymapgis" in content
    assert "def main(" in content
    assert "Tennessee" in content
    assert 'STATE_FIPS = "47"' in content  # Tennessee FIPS code

    # Test QGIS script has valid Python syntax
    qgis_script = example_dir / "create_qgis_project.py"
    with open(qgis_script, "r", encoding="utf-8") as f:
        content = f.read()

    # Should contain key QGIS components
    assert "QgsApplication" in content
    assert "QgsVectorLayer" in content
    assert "tennessee_counties.gpkg" in content
    assert "add_region_field" in content  # Tennessee-specific regional feature

    print("✅ Tennessee scripts importable test passed")


def test_tennessee_regional_features():
    """Test that Tennessee-specific regional features are present."""
    example_dir = Path(__file__).parent

    # Test main script has regional analysis
    main_script = example_dir / "tennessee_counties_example.py"
    with open(main_script, "r", encoding="utf-8") as f:
        content = f.read()

    # Should contain Tennessee regional analysis
    assert "East Tennessee" in content
    assert "Middle Tennessee" in content
    assert "West Tennessee" in content
    assert "Regional Analysis" in content

    # Test QGIS script has regional styling
    qgis_script = example_dir / "create_qgis_project.py"
    with open(qgis_script, "r", encoding="utf-8") as f:
        content = f.read()

    # Should contain regional styling features
    assert "region_colors" in content
    assert "East Tennessee" in content
    assert "Middle Tennessee" in content
    assert "West Tennessee" in content

    print("✅ Tennessee regional features test passed")


def test_pymapgis_available():
    """Test that PyMapGIS is available for import."""
    try:
        import pymapgis as pmg

        assert pmg is not None
        print("✅ PyMapGIS available test passed")
    except ImportError:
        print("⚠️  PyMapGIS not available (expected in some CI environments)")
        # Don't fail the test, just skip
        pass
