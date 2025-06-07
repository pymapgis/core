"""
TIGER/Cartographic-Boundary helpers (county polygons).
"""

from __future__ import annotations

from pathlib import Path

import geopandas as gpd

from .cache import get as cached_get, put as cache_put

_URL_TMPL = (
    "https://www2.census.gov/geo/tiger/GENZ{year}/shp/"
    "cb_{year}_us_county_{scale}.zip"
)


def counties(year: int = 2022, scale: str = "500k") -> gpd.GeoDataFrame:
    """
    Cached download → GeoDataFrame for all US counties (incl. PR).

    `scale` ∈ {"500k", "5m", "20m"}.
    """
    url = _URL_TMPL.format(year=year, scale=scale)
    cache_dir = Path.home() / ".pymapgis" / "shapes"
    zip_path = cache_dir / Path(url).name

    if not zip_path.exists():
        resp = cached_get(url, ttl="90d")
        resp.raise_for_status()
        cache_put(resp.content, zip_path, overwrite=True)

    return gpd.read_file(f"zip://{zip_path}")
