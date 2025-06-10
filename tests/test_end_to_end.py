import pandas as pd
from pymapgis import get_county_table


def test_acs_smoke():
    """Test ACS data fetching functionality."""
    vars_ = ["B23025_004E", "B23025_003E"]  # labour-force
    df = get_county_table(2022, vars_, state="06")  # CA only – tiny payload
    assert isinstance(df, pd.DataFrame)
    assert set(vars_) <= set(df.columns)
    assert "geoid" in df.columns
    assert len(df) > 0  # Should have some counties


def test_counties_smoke():
    """Test county shapefile download with SSL fix."""
    import geopandas as gpd
    from pymapgis import counties

    gdf = counties(2022, "20m")
    assert isinstance(gdf, gpd.GeoDataFrame)
    # join key must be present
    assert "GEOID" in gdf.columns
    assert len(gdf) > 3000  # Should have all US counties


import subprocess
import sys
import os
import pytest

# Define the path to the examples directory
EXAMPLES_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "docs", "examples")

def run_example_script(script_path, script_name, expected_keywords=None, expect_fail_pdal=False):
    """Helper function to run an example script and check its output."""
    full_script_path = os.path.join(script_path, script_name)

    # Ensure the script itself exists
    assert os.path.exists(full_script_path), f"{script_name} not found at {full_script_path}"

    # For GeoArrow example, ensure sample_data.parquet exists
    if script_name == "geoarrow_example.py":
        sample_data_path = os.path.join(script_path, "sample_data.parquet")
        assert os.path.exists(sample_data_path), f"sample_data.parquet not found for {script_name}"

    process = subprocess.run(
        [sys.executable, full_script_path],
        capture_output=True,
        text=True,
        cwd=script_path  # Run script from its own directory if it expects relative paths for data
    )

    if expect_fail_pdal:
        # For Point Cloud example, we expect failure due to PDAL issues
        assert process.returncode != 0, f"{script_name} expected to fail but exited with code 0."
        # Check for PDAL related error messages
        assert "PDAL" in process.stderr or "pdal" in process.stderr or \
               "ImportError" in process.stderr or "RuntimeError" in process.stderr, \
               f"{script_name} failed, but not with an expected PDAL-related error message. Stderr:\n{process.stderr}"
        # If it failed as expected with PDAL error, the test itself has "passed" by confirming the xfail condition
        return


    assert process.returncode == 0, \
        f"{script_name} failed with exit code {process.returncode}.\nStdout:\n{process.stdout}\nStderr:\n{process.stderr}"

    if expected_keywords:
        for keyword in expected_keywords:
            assert keyword in process.stdout, \
                f"Keyword '{keyword}' not found in {script_name} output.\nStdout:\n{process.stdout}"

def test_zarr_example():
    """Test the Cloud-Native Zarr Example."""
    script_dir = os.path.join(EXAMPLES_DIR, "cloud_native_zarr")
    expected_output = [
        "Successfully opened Zarr dataset",
        "Mean temperature",
        "Max temperature",
        "Temperature at a specific point"
    ]
    # This test might be slow due to network access, consider pytest.mark.slow if needed
    # For now, let's assume it's acceptable.
    # Also, ensure s3fs and zarr are installed in the test environment.
    # The example script itself has a pip install suggestion, which is good for users.
    # Here, we rely on the environment having these.
    try:
        import s3fs
        import zarr
    except ImportError:
        pytest.skip("Skipping Zarr example test: s3fs or zarr not installed.")

    run_example_script(script_dir, "zarr_example.py", expected_output)

def test_geoarrow_example():
    """Test the GeoArrow DataFrames Example."""
    script_dir = os.path.join(EXAMPLES_DIR, "geoarrow_example")
    expected_output = [
        "Original GeoDataFrame loaded",
        "GeoDataFrame geometry array type is not the latest GeoArrow-backed type, but operations might still leverage Arrow",
        "Filtered GeoDataFrame (polygons with area > 0.5)",
        "Filtered GeoDataFrame (features with 'value' > 25)"
    ]
    # Ensure geopandas and pyarrow are installed.
    try:
        import geopandas
        import pyarrow
    except ImportError:
        pytest.skip("Skipping GeoArrow example test: geopandas or pyarrow not installed.")

    run_example_script(script_dir, "geoarrow_example.py", expected_output)

def test_network_analysis_example():
    """Test the Network Analysis Example."""
    script_dir = os.path.join(EXAMPLES_DIR, "network_analysis_advanced")
    expected_output = [
        "Fetching street network for",
        "Shortest path length:",
        "Shortest path plot saved",
        "Generated isochrone polygon(s)",
        "Isochrone plot saved"
    ]
    # Ensure osmnx, networkx, matplotlib are installed.
    try:
        import osmnx
        import networkx
        import matplotlib
    except ImportError:
        pytest.skip("Skipping Network Analysis example test: osmnx, networkx, or matplotlib not installed.")

    run_example_script(script_dir, "network_analysis_example.py", expected_output)
    # Clean up generated plot files
    for plot_file in ["shortest_path_plot.png", "isochrone_plot.png"]:
        plot_path = os.path.join(script_dir, plot_file)
        if os.path.exists(plot_path):
            os.remove(plot_path)


@pytest.mark.xfail(reason="PDAL installation is problematic in CI/testing environment, script is expected to fail.")
def test_point_cloud_example_expected_failure():
    """
    Test the Point Cloud Support Example.
    This test is expected to fail because PDAL is not available.
    The script should indicate this failure.
    """
    script_dir = os.path.join(EXAMPLES_DIR, "point_cloud_basic")
    readme_path = os.path.join(script_dir, "README.md")
    sample_las_path = os.path.join(script_dir, "sample.las")

    assert os.path.exists(readme_path), "Point Cloud example README.md not found."
    assert os.path.exists(sample_las_path), "Point Cloud example sample.las not found."

    # This will assert for non-zero exit and PDAL-specific error messages.
    run_example_script(script_dir, "point_cloud_example.py", expect_fail_pdal=True)
