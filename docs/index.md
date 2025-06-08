---
layout: default
title: PyMapGIS Documentation
---

# 🗺️ PyMapGIS Documentation

**Modern GIS toolkit for Python** - Simplifying geospatial workflows with built-in data sources, intelligent caching, and fluent APIs.

[![PyPI version](https://badge.fury.io/py/pymapgis.svg)](https://badge.fury.io/py/pymapgis)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## 🚀 Quick Start

```bash
pip install pymapgis
```

```python
import pymapgis as pmg

# Load Census data with automatic geometry
data = pmg.read("census://acs/acs5?year=2022&geography=county&variables=B25070_010E,B25070_001E")

# Calculate housing cost burden
data["cost_burden_rate"] = data["B25070_010E"] / data["B25070_001E"]

# Create interactive map
data.plot.choropleth(
    column="cost_burden_rate",
    title="Housing Cost Burden by County (2022)",
    cmap="Reds"
).show()
```

---

## 📚 Documentation

<div class="doc-grid">
  <div class="doc-card">
    <h3>🚀 <a href="quickstart.html">Quick Start</a></h3>
    <p>Get up and running in 5 minutes. Create your first interactive map with real Census data.</p>
  </div>
  
  <div class="doc-card">
    <h3>📖 <a href="user-guide.html">User Guide</a></h3>
    <p>Comprehensive guide covering all PyMapGIS concepts, features, and workflows.</p>
  </div>
  
  <div class="doc-card">
    <h3>🔧 <a href="api-reference.html">API Reference</a></h3>
    <p>Complete API documentation with function signatures, parameters, and examples.</p>
  </div>
  
  <div class="doc-card">
    <h3>💡 <a href="examples.html">Examples</a></h3>
    <p>Real-world examples and use cases with complete, runnable code.</p>
  </div>
  <div class="doc-card">
    <h3>🧑‍💻 <a href="developer/index.html">Developer Docs</a></h3>
    <p>Information for contributors: architecture, setup, and extending PyMapGIS.</p>
  </div>
</div>

---

## ✨ Key Features

- **🔗 Built-in Data Sources**: Census ACS, TIGER/Line, and more
- **⚡ Smart Caching**: Automatic HTTP caching with TTL support
- **🗺️ Interactive Maps**: Beautiful visualizations with Leaflet
- **🧹 Clean APIs**: Fluent, pandas-like interface
- **🔧 Extensible**: Plugin architecture for custom data sources

---

## 📊 Supported Data Sources

| Source | URL Pattern | Description |
|--------|-------------|-------------|
| **Census ACS** | `census://acs/acs5?year=2022&geography=county` | American Community Survey data |
| **TIGER/Line** | `tiger://county?year=2022&state=06` | Census geographic boundaries |
| **Local Files** | `file://path/to/data.geojson` | Local geospatial files |

---

## 🎯 Example Use Cases

### Housing Analysis
```python
# Housing cost burden analysis
housing = pmg.read("census://acs/acs5?year=2022&geography=county&variables=B25070_010E,B25070_001E")
housing["cost_burden_rate"] = housing["B25070_010E"] / housing["B25070_001E"]
housing.plot.choropleth(column="cost_burden_rate", title="Housing Cost Burden").show()
```

### Labor Market Analysis
```python
# Labor force participation
labor = pmg.read("census://acs/acs5?year=2022&geography=county&variables=B23025_004E,B23025_003E")
labor["lfp_rate"] = labor["B23025_004E"] / labor["B23025_003E"]
labor.plot.choropleth(column="lfp_rate", title="Labor Force Participation").show()
```

### Demographic Mapping
```python
# Population density
pop = pmg.read("census://acs/acs5?year=2022&geography=county&variables=B01003_001E")
pop["density"] = pop["B01003_001E"] / (pop.geometry.area / 2589988.11)  # per sq mile
pop.plot.choropleth(column="density", title="Population Density").show()
```

---

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

---

## 🤝 Community

- **[GitHub Repository](https://github.com/pymapgis/core)** - Source code and development
- **[PyPI Package](https://pypi.org/project/pymapgis/)** - Package installation
- **[Issues](https://github.com/pymapgis/core/issues)** - Bug reports and feature requests
- **[Discussions](https://github.com/pymapgis/core/discussions)** - Community Q&A
- **[Contributing Guide](https://github.com/pymapgis/core/blob/main/CONTRIBUTING.md)** - How to contribute
- **[Developer Documentation](developer/index.md)** - For contributors and those extending PyMapGIS.

---

## 📄 License

PyMapGIS is open source software licensed under the [MIT License](https://github.com/pymapgis/core/blob/main/LICENSE).

---

**Made with ❤️ by the PyMapGIS community**

<style>
.doc-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
  margin: 20px 0;
}

.doc-card {
  border: 1px solid #e1e4e8;
  border-radius: 6px;
  padding: 20px;
  background: #f6f8fa;
}

.doc-card h3 {
  margin-top: 0;
  margin-bottom: 10px;
}

.doc-card p {
  margin-bottom: 0;
  color: #586069;
}

.doc-card a {
  text-decoration: none;
  color: #0366d6;
}

.doc-card a:hover {
  text-decoration: underline;
}
</style>
