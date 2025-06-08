# PyMapGIS

[![PyPI version](https://badge.fury.io/py/pymapgis.svg)](https://pypi.org/project/pymapgis/)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![CI](https://github.com/pymapgis/core/workflows/CI/badge.svg)](https://github.com/pymapgis/core/actions)
[![Documentation](https://img.shields.io/badge/docs-available-brightgreen.svg)](https://pymapgis.github.io/core/)

**Modern GIS toolkit for Python** - Simplifying geospatial workflows with built-in data sources, intelligent caching, and fluent APIs.

🎉 **[Now available on PyPI!](https://pypi.org/project/pymapgis/)** Install with `pip install pymapgis`

## 🚀 Quick Start

```bash
pip install pymapgis
```

```python
import pymapgis as pmg

# Load Census data with automatic geometry
acs = pmg.read("census://acs/acs5?year=2022&geography=county&variables=B25070_010E,B25070_001E")

# Calculate housing cost burden (30%+ of income on housing)
acs["cost_burden_rate"] = acs["B25070_010E"] / acs["B25070_001E"]

# Create interactive map
acs.plot.choropleth(
    column="cost_burden_rate",
    title="Housing Cost Burden by County (2022)",
    cmap="Reds"
).show()
```

## ✨ Key Features Summary

- **Universal IO**: Simplified data loading and saving for various geospatial formats.
- **Vector/Raster Accessors**: Intuitive `vector` and `raster` accessors for GeoDataFrames and Xarray DataArrays/Datasets.
- **Interactive Maps**: Support for creating interactive maps using Leafmap and deck.gl.
- **Cloud-Native Raster**: Efficient access to cloud-optimized raster data (e.g., COG, Zarr).
- **GeoArrow**: Integration with Apache Arrow for efficient data exchange and in-memory analytics.
- **Network Analysis Basics**: Fundamental tools for shortest path and isochrone calculations.
- **Point Cloud Basics**: Support for reading and processing point cloud data (LAS/LAZ via PDAL).
- **Streaming Connectors**: Basic integration with streaming platforms like Kafka and MQTT.
- **Cache Management**: Robust caching mechanisms for improved performance and offline access, with CLI controls.
- **Plugin System Basics**: Core infrastructure for extending PyMapGIS with custom plugins.
- **CLI Tools**: Command-line interface for common tasks (`info`, `doctor`, `cache`, `rio`).

## 📝 Project Status and Roadmap

PyMapGIS is being developed in phases. Here's an overview of our progress and future plans:

### **Phase 1: Core MVP (v0.1) - Status: Complete**
- Basic Package Structure & Configuration: Implemented.
- Core Data Model (GeoPandas, Xarray): Implemented.
- Universal `pmg.read()` and `pmg.write()`: Implemented.
- Vector Accessor (`.vector`): Implemented.
- Raster Accessor (`.raster`): Implemented.
- Basic TIGER/Line Provider: Implemented.
- Basic Census ACS Provider: Implemented.
- HTTP Caching (`requests-cache`): Implemented.
- Initial CLI (`pymapgis info`): Implemented.
- Documentation (MkDocs, initial content): Implemented.
- Testing Framework (Pytest): Implemented.
- CI/CD (GitHub Actions): Implemented.

### **Phase 2: Enhancements & Community (v0.2) - Status: Largely Complete**
- Interactive Mapping (Leafmap integration): Implemented.
- Cache Management (CLI and API): Implemented.
- Plugin System: Implemented (core registry and interfaces). Cookiecutter template outline available, full template in progress.
- Enhanced CLI: `pymapgis doctor` (Implemented), `pymapgis plugin list` (Implemented). Full plugin management CLI is planned.
- Expanded Data Source Support (e.g., more file types, initial remote sources beyond Census/TIGER): Implemented.
- User Guide and Examples: Implemented.

### **Phase 3: Advanced Capabilities - Status: In Progress & Experimental**
- Cloud-Native Analysis (Lazy windowed Zarr): Implemented.
- GeoArrow DataFrames: Implemented.
- Network Analysis (Shortest path, Isochrones): Implemented. Advanced algorithms like Contraction Hierarchies are planned for future performance enhancements.
- Point Cloud Support (LAS/LAZ via PDAL): Implemented.
- 3D & Time Streaming Sensor Ingestion (Spatio-temporal cubes, deck.gl, Kafka/MQTT): Implemented (core components).
- QGIS Plugin: Initial structure present. Full functionality requires significant development.

### **Features Requiring Further Development / Future Focus:**
- **QGIS Plugin**: Full development and integration to provide a seamless experience within QGIS.
- **Advanced Network Analysis**: Implementation of Contraction Hierarchies and other advanced algorithms for improved performance and capabilities.
- **Plugin Ecosystem**: Finalizing cookiecutter templates for plugin development and potentially expanding plugin management CLI tools to foster a vibrant community.
- **Enhanced Streaming Capabilities**: Broader support for different streaming protocols and more robust error handling.
- **Comprehensive Point Cloud Processing**: Adding more advanced point cloud analysis and manipulation features.

## 📊 Supported Data Sources

| Source | URL Pattern | Description |
|--------|-------------|-------------|
| **Census ACS** | `census://acs/acs5?year=2022&geography=county` | American Community Survey data |
| **TIGER/Line** | `tiger://county?year=2022&state=06` | Census geographic boundaries |
| **Local Files** | `file://path/to/data.geojson` | Local geospatial files |

## 🎯 Examples

### Labor Force Participation Analysis
```python
# Traditional approach: 20+ lines of boilerplate
# PyMapGIS approach: 3 lines

acs = pmg.read("census://acs/acs5?year=2022&geography=county&variables=B23025_004E,B23025_003E")
acs["lfp_rate"] = acs["B23025_004E"] / acs["B23025_003E"]
acs.plot.choropleth(column="lfp_rate", title="Labor Force Participation").show()
```

### Housing Cost Burden Explorer
```python
# Load housing cost data with automatic county boundaries
housing = pmg.read("census://acs/acs5?year=2022&geography=county&variables=B25070_010E,B25070_001E")

# Calculate and visualize cost burden
housing["burden_30plus"] = housing["B25070_010E"] / housing["B25070_001E"]
housing.plot.choropleth(
    column="burden_30plus",
    title="% Households Spending 30%+ on Housing",
    cmap="OrRd",
    legend=True
).show()
```

## 🛠️ Installation

### From PyPI (Recommended)
```bash
pip install pymapgis
```

### From Source
```bash
git clone https://github.com/pymapgis/core.git
cd core
poetry install
```

## 📚 Documentation

- **[📖 User Guide](docs/user-guide.md)** - Complete tutorial and usage guide
- **[🔧 API Reference](docs/api-reference.md)** - Detailed API documentation
- **[💡 Examples](docs/examples.md)** - Real-world usage examples
- **[🚀 Quick Start](docs/quickstart.md)** - Get up and running in 5 minutes
- **[🤝 Contributing Guide](CONTRIBUTING.md)** - How to contribute to PyMapGIS

### Building Documentation Locally

The documentation is built using MkDocs with the Material theme.

1.  **Install dependencies:**
    ```bash
    pip install -r docs/requirements.txt
    ```

2.  **Build and serve the documentation:**
    ```bash
    mkdocs serve
    ```
    This will start a local development server, typically at `http://127.0.0.1:8000/`. Changes to the documentation source files will be automatically rebuilt.

3.  **Build static site:**
    To build the static HTML site (e.g., for deployment):
    ```bash
    mkdocs build
    ```
    The output will be in the `site/` directory.

## 🤝 Contributing

We welcome contributions! PyMapGIS is an open-source project under the MIT license.

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/amazing-feature`)
3. **Commit** your changes (`git commit -m 'Add amazing feature'`)
4. **Push** to the branch (`git push origin feature/amazing-feature`)
5. **Open** a Pull Request

See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built on top of [GeoPandas](https://geopandas.org/), [Leafmap](https://leafmap.org/), and [Requests-Cache](https://requests-cache.readthedocs.io/)
- Inspired by the need for simpler geospatial workflows in Python
- Thanks to all [contributors](https://github.com/pymapgis/core/graphs/contributors)

---

**Made with ❤️ by the PyMapGIS community**
