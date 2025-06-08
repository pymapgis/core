__version__ = "0.0.0-dev0"

from pathlib import Path # Existing import
# from typing import Union # Not strictly needed for Python 3.10+ type hints like `|`

from .io import read
from .cache import _init_session, clear as clear_cache
from .acs import get_county_table
from .tiger import counties
from .plotting import choropleth

# New imports for added functionalities
from .vector import buffer, clip, overlay, spatial_join
from .raster import reproject, normalized_difference
from .viz import explore, plot_interactive
from .serve import serve # Exposing the serve function at the top level


def set_cache(dir_: Path | str | None = None, *, ttl_days: int = 7) -> None: # Python 3.10+ type hint
    """
    Enable or disable caching at runtime.

    set_cache(None)        → disable
    set_cache("~/mycache") → enable & use that folder
    """
    import os
    from datetime import timedelta

    if dir_ is None:
        os.environ["PYMAPGIS_DISABLE_CACHE"] = "1"
    else:
        os.environ.pop("PYMAPGIS_DISABLE_CACHE", None)
        # Reset the global session
        import pymapgis.cache as cache_module

        cache_module._session = None # type: ignore[attr-defined]
        _init_session(dir_, expire_after=timedelta(days=ttl_days))


__all__ = [
    # Existing public API (order preserved)
    "read",
    "set_cache",
    "clear_cache",
    "get_county_table",
    "counties",
    "choropleth",
    # New additions from subtasks
    "buffer",
    "clip",
    "overlay",
    "spatial_join",
    "reproject",
    "normalized_difference",
    "explore",
    "plot_interactive",
    "serve",
    # Package version
    "__version__",
]
