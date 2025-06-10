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
import shutil
from datetime import timedelta
from pathlib import Path
from typing import Optional, Union

import requests
import requests_cache
import urllib3

from pymapgis.settings import settings


# ----------- configuration -------------------------------------------------


def _get_fsspec_cache_dir() -> Path:
    """Return the fsspec cache directory."""
    return Path(settings.cache_dir).expanduser()


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


def stats() -> dict:
    """
    Collect statistics for requests-cache and fsspec cache.

    Returns
    -------
    dict
        A dictionary containing cache statistics.
    """
    _ensure_session()

    # requests-cache statistics
    requests_cache_path = None
    requests_cache_size_bytes = 0
    requests_cache_total_urls = 0
    requests_cache_is_enabled = False
    if _session and _session.cache:
        requests_cache_path = _session.cache.db_path
        if Path(requests_cache_path).exists():
            requests_cache_size_bytes = Path(requests_cache_path).stat().st_size
        requests_cache_total_urls = len(_session.cache.responses)
        requests_cache_is_enabled = not _ENV_DISABLE

    # fsspec cache statistics
    fsspec_cache_dir = _get_fsspec_cache_dir()
    fsspec_cache_size_bytes = 0
    fsspec_cache_file_count = 0
    fsspec_cache_is_configured = False
    if fsspec_cache_dir.exists() and fsspec_cache_dir.is_dir():
        fsspec_cache_is_configured = True
        for p in fsspec_cache_dir.rglob("*"):
            if p.is_file():
                fsspec_cache_size_bytes += p.stat().st_size
                fsspec_cache_file_count += 1

    return {
        "requests_cache_path": (
            str(requests_cache_path) if requests_cache_path else None
        ),
        "requests_cache_size_bytes": requests_cache_size_bytes,
        "requests_cache_total_urls": requests_cache_total_urls,
        "requests_cache_is_enabled": requests_cache_is_enabled,
        "fsspec_cache_dir_path": str(fsspec_cache_dir),
        "fsspec_cache_size_bytes": fsspec_cache_size_bytes,
        "fsspec_cache_file_count": fsspec_cache_file_count,
        "fsspec_cache_is_configured": fsspec_cache_is_configured,
    }


def purge() -> None:
    """
    Purge expired entries from the requests-cache.
    """
    _ensure_session()
    if _session and _session.cache and not _ENV_DISABLE:
        # Prefer `delete(expired=True)` if available (requests-cache >= 0.9.0)
        if hasattr(_session.cache, "delete"):
            _session.cache.delete(expired=True)
        # Fallback for older versions
        elif hasattr(_session.cache, "remove_expired_responses"):
            _session.cache.remove_expired_responses()


def clear() -> None:
    """
    Clear both requests-cache and fsspec cache.

    This function clears all items from the requests-cache and deletes all
    files and subdirectories within the fsspec cache directory. The fsspec
    cache directory itself is not removed.
    """
    global _session
    # Clear requests-cache
    if _session:
        if _session.cache:
            _session.cache.clear()
        _session.close()
        _session = None

    # Clear fsspec cache
    fsspec_cache_dir = _get_fsspec_cache_dir()
    if fsspec_cache_dir.exists() and fsspec_cache_dir.is_dir():
        for item in fsspec_cache_dir.iterdir():
            if item.is_file():
                item.unlink()
            elif item.is_dir():
                shutil.rmtree(item)


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
