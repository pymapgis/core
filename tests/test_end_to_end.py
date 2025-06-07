import pandas as pd
import pytest
from pymapgis import get_county_table

def test_acs_smoke():
    """Test ACS data fetching functionality."""
    vars_ = ["B23025_004E", "B23025_003E"]  # labour-force
    df = get_county_table(2022, vars_, state="06")  # CA only – tiny payload
    assert isinstance(df, pd.DataFrame)
    assert set(vars_) <= set(df.columns)
    assert "geoid" in df.columns
    assert len(df) > 0  # Should have some counties

@pytest.mark.skip(reason="SSL certificate issues in test environment")
def test_counties_smoke():
    """Test county shapefile download (skipped due to SSL issues)."""
    import geopandas as gpd
    from pymapgis import counties

    gdf = counties(2022, "20m")
    assert isinstance(gdf, gpd.GeoDataFrame)
    # join key must be present
    assert "GEOID" in gdf.columns or "geoidfp" in gdf.columns.str.lower().any()
