import tempfile
from pathlib import Path

import pytest
from pymapgis import cache

TEST_URL = "https://httpbin.org/get"


def test_caching_roundtrip():
    with tempfile.TemporaryDirectory() as td:
        cache._init_session(Path(td))
        # first call -> miss
        r1 = cache.get(TEST_URL, ttl=1)
        assert not getattr(r1, "from_cache", False)

        # second call within TTL -> hit
        r2 = cache.get(TEST_URL, ttl=1)
        assert getattr(r2, "from_cache", False)


def test_clear():
    with tempfile.TemporaryDirectory() as td:
        cache._init_session(Path(td))
        cache.get(TEST_URL, ttl=60)
        cache.clear()
        # After clear, session should be None
        assert cache._session is None


def test_ttl_parsing():
    """Test TTL parsing functionality"""
    from datetime import timedelta

    # Test None (default)
    assert cache._parse_ttl(None) == timedelta(days=7)

    # Test timedelta
    td = timedelta(hours=2)
    assert cache._parse_ttl(td) == td

    # Test seconds (int/float)
    assert cache._parse_ttl(3600) == timedelta(seconds=3600)
    assert cache._parse_ttl(3600.5) == timedelta(seconds=3600.5)

    # Test shorthand
    assert cache._parse_ttl("30s") == timedelta(seconds=30)
    assert cache._parse_ttl("5m") == timedelta(minutes=5)
    assert cache._parse_ttl("2h") == timedelta(hours=2)
    assert cache._parse_ttl("3d") == timedelta(days=3)

    # Test invalid
    with pytest.raises(ValueError):
        cache._parse_ttl("invalid")


def test_put_file():
    """Test file caching functionality"""
    with tempfile.TemporaryDirectory() as td:
        dest = Path(td) / "test.bin"
        data = b"test data"

        # First write
        result = cache.put(data, dest)
        assert result == dest
        assert dest.read_bytes() == data

        # Second write without overwrite (should not change)
        new_data = b"new data"
        result = cache.put(new_data, dest, overwrite=False)
        assert result == dest
        assert dest.read_bytes() == data  # unchanged

        # With overwrite
        result = cache.put(new_data, dest, overwrite=True)
        assert result == dest
        assert dest.read_bytes() == new_data


def test_disable_cache():
    """Test cache disabling via environment variable"""
    import os

    # Save original state
    original = os.environ.get("PYMAPGIS_DISABLE_CACHE")

    try:
        # Reset session first
        cache._session = None

        # Test with cache disabled
        os.environ["PYMAPGIS_DISABLE_CACHE"] = "1"

        # Should use regular requests, not cached
        response = cache.get(TEST_URL)
        assert not hasattr(response, "from_cache")

    finally:
        # Restore original state
        if original is None:
            os.environ.pop("PYMAPGIS_DISABLE_CACHE", None)
        else:
            os.environ["PYMAPGIS_DISABLE_CACHE"] = original

        # Reset session for other tests
        cache._session = None
