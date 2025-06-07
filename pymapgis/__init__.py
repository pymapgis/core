__version__ = "0.0.0-dev0"

from pathlib import Path
from .io import read as read
from .cache import _init_session, clear as clear_cache
from .acs import get_county_table
from .tiger import counties
from .plotting import choropleth


def set_cache(dir_: str | Path | None = None, *, ttl_days: int = 7) -> None:
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

        cache_module._session = None
        _init_session(dir_, expire_after=timedelta(days=ttl_days))


__all__ = [
    "read",
    "set_cache",
    "clear_cache",
    "get_county_table",
    "counties",
    "choropleth",
]
