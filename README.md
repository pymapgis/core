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

## ✨ Key Features

- **🔗 Built-in Data Sources**: Census ACS, TIGER/Line, and more
- **⚡ Smart Caching**: Automatic HTTP caching with TTL support
- **🗺️ Interactive Maps**: Beautiful visualizations with Leaflet
- **🧹 Clean APIs**: Fluent, pandas-like interface
- **🔧 Extensible**: Plugin architecture for custom data sources

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
