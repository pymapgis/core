# 🚀 PyMapGIS Quick Start

Get up and running with PyMapGIS in just 5 minutes! This guide will walk you through installation, basic usage, and your first interactive map.

## 📦 Installation

### Option 1: Install from PyPI (Recommended)
```bash
pip install pymapgis
```

### Option 2: Install from Source
```bash
git clone https://github.com/pymapgis/core.git
cd core
poetry install
```

## 🎯 Your First Map in 30 Seconds

Let's create an interactive map showing housing cost burden across US counties:

```python
import pymapgis as pmg

# Load Census data with automatic geometry
data = pmg.read("census://acs/acs5?year=2022&geography=county&variables=B25070_010E,B25070_001E")

# Calculate housing cost burden (30%+ of income on housing)
data["cost_burden_rate"] = data["B25070_010E"] / data["B25070_001E"]

# Create interactive map
data.plot.choropleth(
    column="cost_burden_rate",
    title="Housing Cost Burden by County (2022)",
    cmap="Reds",
    legend=True
).show()
```

That's it! You just created an interactive map with real Census data in 6 lines of code.

## 🔍 What Just Happened?

1. **`pmg.read()`** - Automatically fetched Census ACS data and county boundaries
2. **Data calculation** - Computed housing cost burden percentage
3. **`.plot.choropleth()`** - Generated an interactive Leaflet map
4. **`.show()`** - Displayed the map in your browser

## 🎨 Customizing Your Map

### Change Colors and Styling
```python
data.plot.choropleth(
    column="cost_burden_rate",
    title="Housing Cost Burden by County",
    cmap="viridis",           # Try: 'Blues', 'Reds', 'plasma', 'coolwarm'
    legend=True,
    legend_kwds={'caption': 'Burden Rate'},
    style_kwds={'fillOpacity': 0.7, 'weight': 0.5}
).show()
```

### Add Tooltips and Popups
```python
data.plot.choropleth(
    column="cost_burden_rate",
    tooltip=['NAME', 'cost_burden_rate'],
    popup=['NAME', 'B25070_010E', 'B25070_001E'],
    title="Interactive Housing Cost Map"
).show()
```

## 📊 More Data Sources

### Labor Force Participation
```python
# Get labor force data
labor = pmg.read("census://acs/acs5?year=2022&geography=county&variables=B23025_004E,B23025_003E")
labor["lfp_rate"] = labor["B23025_004E"] / labor["B23025_003E"]
labor.plot.choropleth(column="lfp_rate", title="Labor Force Participation").show()
```

### Geographic Boundaries Only
```python
# Get just county boundaries
counties = pmg.read("tiger://county?year=2022&state=06")  # California counties
counties.plot.interactive().show()
```

### Local Files
```python
# Load your own geospatial data
my_data = pmg.read("file://path/to/your/data.geojson")
my_data.plot.interactive().show()
```

## 🛠️ Configuration

### Caching Settings
```python
import pymapgis as pmg

# Configure cache TTL (time-to-live)
pmg.settings.cache_ttl = "24h"  # Cache for 24 hours
pmg.settings.cache_ttl = "90m"  # Cache for 90 minutes

# Disable caching (not recommended)
pmg.settings.disable_cache = True
```

### Data Source Settings
```python
# Set default Census API year
pmg.settings.census_year = 2021

# Configure request timeout
pmg.settings.request_timeout = 30  # seconds
```

## 🎓 Next Steps

Now that you've created your first map, explore more advanced features:

1. **[📖 User Guide](user-guide.md)** - Comprehensive tutorials and concepts
2. **[🔧 API Reference](api-reference.md)** - Detailed function documentation  
3. **[💡 Examples](examples.md)** - Real-world use cases and patterns
4. **[🤝 Contributing](../CONTRIBUTING.md)** - Help improve PyMapGIS

## 🆘 Getting Help

- **GitHub Issues**: [Report bugs or request features](https://github.com/pymapgis/core/issues)
- **GitHub Discussions**: [Ask questions and share ideas](https://github.com/pymapgis/core/discussions)
- **Email**: nicholaskarlson@gmail.com

## 🎉 What's Next?

Try these challenges to explore PyMapGIS further:

1. **Compare Years**: Load data from different years and create side-by-side maps
2. **State Focus**: Filter data to a specific state using FIPS codes
3. **Custom Variables**: Explore different Census variables from the ACS
4. **Export Maps**: Save your maps as HTML files to share

Happy mapping! 🗺️✨
