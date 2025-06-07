# Changelog

All notable changes to PyMapGIS will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Comprehensive caching system with TTL support
- Census ACS data source integration
- TIGER/Line geographic boundaries support
- Interactive plotting with Leafmap
- Housing cost burden and labor force gap examples
- GitHub Actions CI/CD pipeline
- Pre-commit hooks for code quality

### Changed
- Updated project structure for PyPI publication
- Improved documentation and README
- Enhanced type hints throughout codebase

### Fixed
- Code formatting and linting issues
- Import organization in example files

## [0.1.0] - 2024-01-XX

### Added
- Initial PyMapGIS core library
- Basic data reading functionality
- Settings management with Pydantic
- MIT license
- Poetry-based dependency management

### Infrastructure
- GitHub repository setup
- Basic CI/CD with GitHub Actions
- Pre-commit configuration
- Testing framework with pytest

---

## Release Notes

### Version 0.1.0
This is the initial release of PyMapGIS, a modern GIS toolkit for Python. The library provides:

- **Simplified Data Access**: Built-in support for Census ACS and TIGER/Line data
- **Smart Caching**: Automatic HTTP caching with configurable TTL
- **Interactive Visualization**: Beautiful maps with Leaflet integration
- **Clean APIs**: Pandas-like interface for geospatial workflows

### Upcoming Features
- Additional data sources (OpenStreetMap, Natural Earth)
- Raster data processing capabilities
- Advanced spatial analysis tools
- Plugin system for custom data sources
- Jupyter notebook integration
- Performance optimizations

### Breaking Changes
None in this initial release.

### Migration Guide
This is the first release, so no migration is needed.

---

For more details, see the [GitHub releases page](https://github.com/pymapgis/core/releases).
