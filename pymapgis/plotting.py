"""
One-liner choropleth helper (matplotlib backend).
"""

from __future__ import annotations

import matplotlib.pyplot as plt
import geopandas as gpd
import pandas as pd
from pathlib import Path
from typing import Optional, Union


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


def save_png(
    gdf: gpd.GeoDataFrame,
    output_path: Union[str, Path],
    column: Optional[str] = None,
    *,
    cmap: str = "viridis",
    title: str | None = None,
    dpi: int = 150,
    figsize: tuple = (10, 6),
    **kwargs,
) -> None:
    """
    Save GeoDataFrame as PNG image.

    Args:
        gdf: GeoDataFrame to plot
        output_path: Output file path
        column: Column to use for choropleth coloring (optional)
        cmap: Colormap to use
        title: Plot title
        dpi: Image resolution
        figsize: Figure size (width, height)
        **kwargs: Additional arguments for gdf.plot()
    """
    fig, ax = plt.subplots(figsize=figsize)

    if column and column in gdf.columns:
        gdf.plot(
            column=column,
            cmap=cmap,
            linewidth=0.1,
            edgecolor="black",
            ax=ax,
            **kwargs,
        )
    else:
        gdf.plot(
            linewidth=0.1,
            edgecolor="black",
            ax=ax,
            **kwargs,
        )

    ax.axis("off")
    if title:
        ax.set_title(title)

    plt.tight_layout()
    plt.savefig(output_path, dpi=dpi, bbox_inches="tight")
    plt.close(fig)


@pd.api.extensions.register_dataframe_accessor("pmg_plot")
class PmgPlotAccessor:
    """
    Plot accessor for GeoDataFrames to add save_png method.
    """

    def __init__(self, gdf_obj):
        self._obj = gdf_obj

    def save_png(
        self,
        output_path: Union[str, Path],
        column: Optional[str] = None,
        *,
        cmap: str = "viridis",
        title: str | None = None,
        dpi: int = 150,
        figsize: tuple = (10, 6),
        **kwargs,
    ) -> None:
        """
        Save GeoDataFrame as PNG image.

        Args:
            output_path: Output file path
            column: Column to use for choropleth coloring (optional)
            cmap: Colormap to use
            title: Plot title
            dpi: Image resolution
            figsize: Figure size (width, height)
            **kwargs: Additional arguments for gdf.plot()
        """
        return save_png(
            self._obj,
            output_path,
            column=column,
            cmap=cmap,
            title=title,
            dpi=dpi,
            figsize=figsize,
            **kwargs,
        )
