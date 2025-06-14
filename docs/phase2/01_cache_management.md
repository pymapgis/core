# Phase 2: Cache Management

This document outlines the requirements for cache management in PyMapGIS Phase 2.

## CLI Helpers

- `pymapgis cache info`: Display statistics about the cache, such as total size, number of files, and cache location.
- `pymapgis cache clear`: Clear all items from the cache. Optionally, allow clearing specific files or files older than a certain date.

## API Helpers

- `pmg.cache.stats()`: Programmatic access to cache statistics.
- `pmg.cache.purge()`: Programmatic way to clear all or parts of the cache.
