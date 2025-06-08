# 📚 PyMapGIS Documentation

Welcome to the comprehensive PyMapGIS documentation! PyMapGIS is a modern GIS toolkit for Python that simplifies geospatial workflows with built-in data sources, intelligent caching, and fluent APIs.

## 🚀 Getting Started

New to PyMapGIS? Start here:

### [🚀 Quick Start Guide](quickstart.md)
Get up and running with PyMapGIS in just 5 minutes. Create your first interactive map with real Census data.

**Perfect for:** First-time users who want to see PyMapGIS in action immediately.

---

## 📖 Core Documentation

### [📖 User Guide](user-guide.md)
Comprehensive guide covering all PyMapGIS concepts, features, and workflows.

**Topics covered:**
- Core concepts and philosophy
- Data sources (Census ACS, TIGER/Line, local files)
- Interactive visualization and mapping
- Caching system and performance
- Configuration and settings
- Advanced usage patterns

**Perfect for:** Users who want to understand PyMapGIS deeply and use it effectively.

### [🔧 API Reference](api-reference.md)
Complete API documentation with function signatures, parameters, and examples.

**Includes:**
- `pymapgis.read()` - Universal data reader
- Plotting API (`.plot.choropleth()`, `.plot.interactive()`)
- Cache API (`pymapgis.cache`)
- Settings API (`pymapgis.settings`)
- Type hints and error handling

**Perfect for:** Developers who need detailed technical reference while coding.

### [💡 Examples](examples.md)
Real-world examples and use cases with complete, runnable code.

**Example categories:**
- 🏠 Housing analysis (cost burden, affordability, rental markets)
- 💼 Labor market analysis (employment, education, income)
- 📊 Demographic comparisons (population, age, density)
- 🗺️ Multi-scale mapping (state to tract level)
- 📈 Time series analysis (year-over-year changes)
- 🔄 Data integration (combining Census and local data)

**Perfect for:** Users who learn best from practical, real-world examples.

---

## 🎯 Quick Navigation

### By Experience Level

#### 🌱 **Beginner**
1. [Quick Start](quickstart.md) - Your first map in 30 seconds
2. [User Guide: Core Concepts](user-guide.md#-core-concepts) - Understanding PyMapGIS
3. [Examples: Housing Analysis](examples.md#-housing-analysis) - Simple, practical examples

#### 🌿 **Intermediate**
1. [User Guide: Data Sources](user-guide.md#-data-sources) - Master all data sources
2. [User Guide: Visualization](user-guide.md#️-visualization) - Advanced mapping techniques
3. [Examples: Multi-Scale Mapping](examples.md#️-multi-scale-mapping) - Complex workflows

#### 🌳 **Advanced**
1. [User Guide: Advanced Usage](user-guide.md#-advanced-usage) - Performance and optimization
2. [API Reference](api-reference.md) - Complete technical reference
3. [Examples: Data Integration](examples.md#-data-integration) - Custom analytics

### By Use Case

#### 📊 **Data Analysis**
- [Housing Cost Burden Analysis](examples.md#housing-cost-burden-by-county)
- [Labor Force Participation](examples.md#labor-force-participation-rate)
- [Demographic Comparisons](examples.md#-demographic-comparisons)

#### 🗺️ **Mapping & Visualization**
- [Interactive Choropleth Maps](user-guide.md#choropleth-maps)
- [Custom Styling and Colors](user-guide.md#color-maps)
- [Multi-Scale Visualizations](examples.md#state-level-overview-with-county-detail)

#### ⚡ **Performance & Optimization**
- [Caching System](user-guide.md#-caching-system)
- [Large Dataset Handling](examples.md#optimizing-large-datasets)
- [Batch Processing](examples.md#batch-processing)

#### 🔧 **Development & Integration**
- [API Reference](api-reference.md)
- [Configuration Management](user-guide.md#-configuration)
- [Custom Data Integration](examples.md#combining-census-and-local-data)

---

## 📋 Common Tasks

### Quick Reference

| Task | Documentation | Code Example |
|------|---------------|--------------|
| **Install PyMapGIS** | [Quick Start](quickstart.md#-installation) | `pip install pymapgis` |
| **Load Census data** | [User Guide: Data Sources](user-guide.md#census-american-community-survey-acs) | `pmg.read("census://acs/acs5?year=2022&geography=county&variables=B01003_001E")` |
| **Create choropleth map** | [User Guide: Visualization](user-guide.md#choropleth-maps) | `data.plot.choropleth(column="population").show()` |
| **Configure caching** | [User Guide: Caching](user-guide.md#cache-configuration) | `pmg.settings.cache_ttl = "24h"` |
| **Load local files** | [API Reference](api-reference.md#local-files) | `pmg.read("file://path/to/data.geojson")` |
| **Filter by state** | [User Guide: Data Sources](user-guide.md#geographic-levels) | `pmg.read("...&state=06")` |

---

## 🔗 External Resources

### PyMapGIS Ecosystem
- **[PyMapGIS Core Repository](https://github.com/pymapgis/core)** - Main codebase
- **[PyMapGIS on PyPI](https://pypi.org/project/pymapgis/)** - Package installation
- **[GitHub Issues](https://github.com/pymapgis/core/issues)** - Bug reports and feature requests
- **[GitHub Discussions](https://github.com/pymapgis/core/discussions)** - Community Q&A

### Related Projects
- **[GeoPandas](https://geopandas.org/)** - Geospatial data manipulation
- **[Leafmap](https://leafmap.org/)** - Interactive mapping
- **[Census API](https://www.census.gov/data/developers/data-sets.html)** - US Census data
- **[TIGER/Line Shapefiles](https://www.census.gov/geographies/mapping-files/time-series/geo/tiger-line-file.html)** - Geographic boundaries

---

## 🤝 Contributing

Want to help improve PyMapGIS? Check out our [Contributing Guide](../CONTRIBUTING.md) for:

- Development setup instructions
- Code style guidelines
- Testing procedures
- Pull request process

---

## 📄 License

PyMapGIS is open source software licensed under the [MIT License](../LICENSE).

---

## 🙏 Acknowledgments

PyMapGIS is built on the shoulders of giants:

- **[GeoPandas](https://geopandas.org/)** - Geospatial data structures and operations
- **[Leafmap](https://leafmap.org/)** - Interactive mapping capabilities
- **[Requests-Cache](https://requests-cache.readthedocs.io/)** - HTTP caching system
- **[Pydantic](https://pydantic.dev/)** - Settings and configuration management

Special thanks to the US Census Bureau for providing free, high-quality geospatial data through their APIs.

---

**Made with ❤️ by the PyMapGIS community**

*Last updated: January 2024*
