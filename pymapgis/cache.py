"""
File-system + SQLite HTTP cache for PyMapGIS.

Usage
-----
>>> from pymapgis import cache
>>> url = "https://api.census.gov/data/..."
>>> data = cache.get(url, ttl="3h")           # transparently cached
>>> cache.clear()                             # wipe"""

from __future__ import annotations

import os
import re
from datetime import timedelta
from pathlib import Path
from typing import Optional, Union

import requests
import requests_cache
import urllib3

# ----------- configuration -------------------------------------------------

_ENV_DISABLE = bool(int(os.getenv("PYMAPGIS_DISABLE_CACHE", "0")))
_DEFAULT_DIR = Path.home() / ".pymapgis" / "cache"
_DEFAULT_EXPIRE = timedelta(days=7)

_session: Optional[requests_cache.CachedSession] = None

# Disable SSL warnings for government sites with certificate issues
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def _init_session(
    cache_dir: Union[str, Path] = _DEFAULT_DIR,
    expire_after: timedelta = _DEFAULT_EXPIRE,
) -> None:
    """Lazy-initialise the global CachedSession."""
    global _session
    if _ENV_DISABLE:
        return

    cache_dir = Path(cache_dir).expanduser()
    cache_dir.mkdir(parents=True, exist_ok=True)
    _session = requests_cache.CachedSession(
        cache_name=str(cache_dir / "http_cache"),
        backend="sqlite",
        expire_after=expire_after,
        allowable_codes=(200,),
        allowable_methods=("GET", "HEAD"),
    )


def _ensure_session() -> None:
    # Check environment variable each time
    if _session is None and not bool(int(os.getenv("PYMAPGIS_DISABLE_CACHE", "0"))):
        _init_session()


# ----------- public helpers -------------------------------------------------


def get(
    url: str,
    *,
    ttl: Union[int, float, str, timedelta, None] = None,
    **kwargs,
) -> requests.Response:
    """
    Fetch *url* with caching.

    Parameters
    ----------
    ttl : int | float | str | timedelta | None
        • None → default expiry (7 days)
        • int/float (seconds)
        • "24h", "90m" shorthand
        • timedelta
    kwargs : passed straight to requests (headers, params …)
    """
    # Check environment variable each time
    if bool(int(os.getenv("PYMAPGIS_DISABLE_CACHE", "0"))):
        # Use verify=False for government sites with SSL issues
        kwargs.setdefault("verify", False)
        return requests.get(url, **kwargs)

    _ensure_session()
    expire_after = _parse_ttl(ttl)
    # Use verify=False for government sites with SSL issues
    kwargs.setdefault("verify", False)
    with _session.cache_disabled() if expire_after == 0 else _session:
        return _session.get(url, expire_after=expire_after, **kwargs)


def put(binary: bytes, dest: Path, *, overwrite: bool = False) -> Path:
    """
    Persist raw bytes (e.g. a ZIP shapefile) onto disk cache.
    Returns the written Path.
    """
    dest = Path(dest)
    if dest.exists() and not overwrite:
        return dest
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(binary)
    return dest


def clear() -> None:
    """Drop the entire cache directory."""
    global _session
    if _session:
        _session.cache.clear()
        _session.close()
        _session = None


# ----------- internals ------------------------------------------------------

_RE_SHORTHAND = re.compile(r"^(?P<num>\d+)(?P<unit>[smhd])$")


def _parse_ttl(val) -> Optional[timedelta]:
    if val is None:
        return _DEFAULT_EXPIRE
    if isinstance(val, timedelta):
        return val
    if isinstance(val, (int, float)):
        return timedelta(seconds=val)

    match = _RE_SHORTHAND.match(str(val).lower())
    if match:
        mult = int(match["num"])
        return timedelta(
            **{
                {"s": "seconds", "m": "minutes", "h": "hours", "d": "days"}[
                    match["unit"]
                ]: mult
            }
        )
    raise ValueError(f"Un-recognised TTL: {val!r}")
