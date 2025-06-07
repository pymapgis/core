"""
One-liner choropleth helper (matplotlib backend).
"""

from __future__ import annotations

import matplotlib.pyplot as plt
import geopandas as gpd


def choropleth(
    gdf: gpd.GeoDataFrame,
    column: str,
    *,
    cmap: str = "viridis",
    title: str | None = None,
):
    ax = gdf.plot(
        column=column, cmap=cmap, linewidth=0.1, edgecolor="black", figsize=(10, 6)
    )
    ax.axis("off")
    ax.set_title(title or column)
    plt.tight_layout()
    return ax
