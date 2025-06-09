# 💡 PyMapGIS Examples

Real-world examples and use cases for PyMapGIS. Each example includes complete code and explanations.

## Table of Contents

1. [🏠 Housing Analysis](#-housing-analysis)
2. [💼 Labor Market Analysis](#-labor-market-analysis)
3. [📊 Demographic Comparisons](#-demographic-comparisons)
4. [🗺️ Multi-Scale Mapping](#️-multi-scale-mapping)
5. [📈 Time Series Analysis](#-time-series-analysis)
6. [🔄 Data Integration](#-data-integration)

## 🏠 Housing Analysis

### Housing Cost Burden by County

Analyze the percentage of households spending 30% or more of their income on housing costs.

```python
import pymapgis as pmg

# Load housing cost data
housing = pmg.read("census://acs/acs5?year=2022&geography=county&variables=B25070_010E,B25070_001E")

# Calculate cost burden rate
housing["cost_burden_rate"] = housing["B25070_010E"] / housing["B25070_001E"]

# Create interactive map
housing.plot.choropleth(
    column="cost_burden_rate",
    title="Housing Cost Burden by County (2022)",
    cmap="Reds",
    tooltip=["NAME", "cost_burden_rate"],
    popup=["NAME", "B25070_010E", "B25070_001E"],
    legend_kwds={"caption": "% Households with 30%+ Cost Burden"}
).show()
```

### Median Home Values vs Median Income

Compare housing affordability across regions.

```python
# Load home values and income data
home_values = pmg.read("census://acs/acs5?year=2022&geography=county&variables=B25077_001E")
income = pmg.read("census://acs/acs5?year=2022&geography=county&variables=B19013_001E")

# Merge datasets
affordability = home_values.merge(income, on="GEOID")

# Calculate affordability ratio (home value / annual income)
affordability["affordability_ratio"] = affordability["B25077_001E"] / affordability["B19013_001E"]

# Visualize affordability
affordability.plot.choropleth(
    column="affordability_ratio",
    title="Home Value to Income Ratio by County",
    cmap="RdYlBu_r",
    tooltip=["NAME", "affordability_ratio", "B25077_001E", "B19013_001E"],
    legend_kwds={"caption": "Home Value / Annual Income Ratio"}
).show()
```

### Rental Market Analysis

Analyze rental costs and availability.

```python
# Load rental data
rental = pmg.read("census://acs/acs5?year=2022&geography=county&variables=B25064_001E,B25003_003E")

# Calculate rental metrics
rental["median_rent"] = rental["B25064_001E"]
rental["renter_households"] = rental["B25003_003E"]

# Create rental cost map
rental.plot.choropleth(
    column="median_rent",
    title="Median Gross Rent by County (2022)",
    cmap="viridis",
    tooltip=["NAME", "median_rent", "renter_households"],
    legend_kwds={"caption": "Median Gross Rent ($)"}
).show()
```

## 💼 Labor Market Analysis

### Labor Force Participation Rate

Analyze employment patterns across the country.

```python
# Load labor force data
labor = pmg.read("census://acs/acs5?year=2022&geography=county&variables=B23025_003E,B23025_002E")

# Calculate labor force participation rate
labor["lfp_rate"] = labor["B23025_003E"] / labor["B23025_002E"]

# Create participation rate map
labor.plot.choropleth(
    column="lfp_rate",
    title="Labor Force Participation Rate by County (2022)",
    cmap="Blues",
    tooltip=["NAME", "lfp_rate"],
    legend_kwds={"caption": "Labor Force Participation Rate"}
).show()
```

### Unemployment Rate Analysis

Track unemployment patterns and economic health.

```python
# Load employment data
employment = pmg.read("census://acs/acs5?year=2022&geography=county&variables=B23025_003E,B23025_005E")

# Calculate unemployment rate
employment["unemployment_rate"] = employment["B23025_005E"] / employment["B23025_003E"]

# Visualize unemployment
employment.plot.choropleth(
    column="unemployment_rate",
    title="Unemployment Rate by County (2022)",
    cmap="Reds",
    tooltip=["NAME", "unemployment_rate"],
    legend_kwds={"caption": "Unemployment Rate"}
).show()
```

### Educational Attainment and Income

Explore the relationship between education and income.

```python
# Load education and income data
education = pmg.read("census://acs/acs5?year=2022&geography=county&variables=B15003_022E,B15003_001E")
income = pmg.read("census://acs/acs5?year=2022&geography=county&variables=B19013_001E")

# Merge and calculate bachelor's degree rate
edu_income = education.merge(income, on="GEOID")
edu_income["bachelors_rate"] = edu_income["B15003_022E"] / edu_income["B15003_001E"]

# Create education-income map
edu_income.plot.choropleth(
    column="bachelors_rate",
    title="Bachelor's Degree Attainment by County",
    cmap="Greens",
    tooltip=["NAME", "bachelors_rate", "B19013_001E"],
    legend_kwds={"caption": "% with Bachelor's Degree"}
).show()
```

## 📊 Demographic Comparisons

### Population Density Analysis

Compare urban vs rural population patterns.

```python
# Load population and area data
population = pmg.read("census://acs/acs5?year=2022&geography=county&variables=B01003_001E")

# Calculate area in square miles (geometry is in square meters)
population["area_sq_miles"] = population.geometry.area / 2589988.11  # Convert m² to mi²

# Calculate population density
population["pop_density"] = population["B01003_001E"] / population["area_sq_miles"]

# Create density map with log scale for better visualization
import numpy as np
population["log_density"] = np.log10(population["pop_density"] + 1)

population.plot.choropleth(
    column="log_density",
    title="Population Density by County (Log Scale)",
    cmap="plasma",
    tooltip=["NAME", "pop_density", "B01003_001E"],
    legend_kwds={"caption": "Log10(Population per sq mile)"}
).show()
```

### Age Demographics

Analyze age distribution patterns.

```python
# Load age data
age_data = pmg.read("census://acs/acs5?year=2022&geography=county&variables=B01001_001E,B01001_020E,B01001_021E")

# Calculate senior population percentage (65+)
age_data["senior_rate"] = (age_data["B01001_020E"] + age_data["B01001_021E"]) / age_data["B01001_001E"]

# Visualize aging patterns
age_data.plot.choropleth(
    column="senior_rate",
    title="Senior Population (65+) by County",
    cmap="Oranges",
    tooltip=["NAME", "senior_rate"],
    legend_kwds={"caption": "% Population 65+"}
).show()
```

## 🗺️ Multi-Scale Mapping

### State-Level Overview with County Detail

Create hierarchical visualizations from state to county level.

```python
# Start with state-level overview
states = pmg.read("census://acs/acs5?year=2022&geography=state&variables=B19013_001E")

# Create state-level income map
state_map = states.plot.choropleth(
    column="B19013_001E",
    title="Median Household Income by State",
    cmap="viridis",
    tooltip=["NAME", "B19013_001E"]
)

# Focus on a specific state (California)
ca_counties = pmg.read("census://acs/acs5?year=2022&geography=county&state=06&variables=B19013_001E")

# Create detailed county map for California
ca_map = ca_counties.plot.choropleth(
    column="B19013_001E",
    title="Median Household Income - California Counties",
    cmap="viridis",
    tooltip=["NAME", "B19013_001E"]
)

# Show both maps
state_map.show()
ca_map.show()
```

### Census Tract Analysis

Dive deep into neighborhood-level patterns.

```python
# Analyze census tracts in a specific county (Los Angeles County, CA)
la_tracts = pmg.read("census://acs/acs5?year=2022&geography=tract&state=06&county=037&variables=B19013_001E")

# Create detailed tract-level map
la_tracts.plot.choropleth(
    column="B19013_001E",
    title="Median Household Income - Los Angeles County Tracts",
    cmap="RdYlBu_r",
    tooltip=["NAME", "B19013_001E"],
    style_kwds={"weight": 0.2}  # Thinner borders for tract-level detail
).show()
```

## 📈 Time Series Analysis

### Comparing Multiple Years

Analyze changes over time using multiple data requests.

```python
# Load data for multiple years
years = [2018, 2019, 2020, 2021, 2022]
income_data = {}

for year in years:
    data = pmg.read(f"census://acs/acs5?year={year}&geography=state&variables=B19013_001E")
    income_data[year] = data.set_index("NAME")["B19013_001E"]

# Create a comparison DataFrame
import pandas as pd
income_comparison = pd.DataFrame(income_data)

# Calculate change from 2018 to 2022
income_comparison["change_2018_2022"] = (
    (income_comparison[2022] - income_comparison[2018]) / income_comparison[2018] * 100
)

# Merge back with geometry for mapping
states_2022 = pmg.read("census://acs/acs5?year=2022&geography=state&variables=B19013_001E")
income_change = states_2022.merge(
    income_comparison["change_2018_2022"].reset_index(),
    on="NAME"
)

# Map income changes
income_change.plot.choropleth(
    column="change_2018_2022",
    title="Median Income Change 2018-2022 (%)",
    cmap="RdBu_r",
    tooltip=["NAME", "change_2018_2022"],
    legend_kwds={"caption": "% Change in Median Income"}
).show()
```

## 🔄 Data Integration

### Combining Census and Local Data

Integrate PyMapGIS data with your own datasets.

```python
# Load Census data
census_data = pmg.read("census://acs/acs5?year=2022&geography=county&variables=B01003_001E,B19013_001E")

# Load local business data (example)
# business_data = pd.read_csv("local_business_data.csv")

# Example local data structure
import pandas as pd
business_data = pd.DataFrame({
    "GEOID": ["06037", "06059", "06073"],  # LA, Orange, San Diego counties
    "business_count": [150000, 45000, 38000],
    "avg_business_revenue": [2500000, 1800000, 2100000]
})

# Merge with Census data
combined = census_data.merge(business_data, on="GEOID", how="left")

# Calculate businesses per capita
combined["businesses_per_capita"] = combined["business_count"] / combined["B01003_001E"]

# Map business density
combined.plot.choropleth(
    column="businesses_per_capita",
    title="Businesses per Capita by County",
    cmap="Blues",
    tooltip=["NAME", "businesses_per_capita", "business_count"]
).show()
```

### Creating Custom Metrics

Develop complex analytical metrics using multiple data sources.

```python
# Load multiple datasets
housing = pmg.read("census://acs/acs5?year=2022&geography=county&variables=B25070_010E,B25070_001E")
income = pmg.read("census://acs/acs5?year=2022&geography=county&variables=B19013_001E")
population = pmg.read("census://acs/acs5?year=2022&geography=county&variables=B01003_001E")

# Merge all datasets
analysis = housing.merge(income, on="GEOID").merge(population, on="GEOID")

# Create composite affordability index
analysis["cost_burden_rate"] = analysis["B25070_010E"] / analysis["B25070_001E"]
analysis["income_normalized"] = analysis["B19013_001E"] / analysis["B19013_001E"].median()

# Custom affordability index (lower is more affordable)
analysis["affordability_index"] = (
    analysis["cost_burden_rate"] * 0.6 +  # 60% weight on cost burden
    (1 / analysis["income_normalized"]) * 0.4  # 40% weight on relative income
)

# Map the custom index
analysis.plot.choropleth(
    column="affordability_index",
    title="Housing Affordability Index by County",
    cmap="RdYlGn_r",  # Red = less affordable, Green = more affordable
    tooltip=["NAME", "affordability_index", "cost_burden_rate", "B19013_001E"],
    legend_kwds={"caption": "Affordability Index (lower = more affordable)"}
).show()
```

## 🎯 Performance Tips

### Optimizing Large Datasets

```python
# For large geographic levels, filter by state
# Instead of all US tracts (~80k features):
# all_tracts = pmg.read("census://acs/acs5?year=2022&geography=tract&variables=B01003_001E")

# Use state filtering for better performance:
ca_tracts = pmg.read("census://acs/acs5?year=2022&geography=tract&state=06&variables=B01003_001E")

# Use appropriate cache TTL for your use case
pmg.settings.cache_ttl = "7d"  # Cache for a week for stable data

# Load only needed variables
essential_vars = "B01003_001E,B19013_001E"  # Population and income only
data = pmg.read(f"census://acs/acs5?year=2022&geography=county&variables={essential_vars}")
```

### Batch Processing

```python
# Process multiple states efficiently
states_to_analyze = ["06", "36", "48"]  # CA, NY, TX
results = {}

for state_fips in states_to_analyze:
    state_data = pmg.read(
        f"census://acs/acs5?year={year}&geography=county&state={state_fips}&variables=B19013_001E"
    )
    results[state_fips] = state_data

# Combine results
all_states = pd.concat(results.values(), ignore_index=True)
```

---

## 🔗 Next Steps

- **[📖 User Guide](user-guide.md)** - Comprehensive tutorials and concepts
- **[🔧 API Reference](api-reference.md)** - Detailed function documentation
- **[🚀 Quick Start](quickstart.md)** - Get started in 5 minutes

**Happy mapping with PyMapGIS!** 🗺️✨


## 📂 More Examples

The following examples provide more targeted demonstrations of PyMapGIS features and can be found in the `examples/` directory of the repository.

### Visualizing TIGER/Line Roads

This example demonstrates how to load and visualize TIGER/Line data, specifically roads, for a selected county. It showcases fetching data using the `tiger://` URL scheme and plotting linear features.

[Details and Code](./examples/tiger_line_visualization/README.md)

```python
import pymapgis as pmg

# Load road data for Los Angeles County, CA (State FIPS: 06, County FIPS: 037)
# RTTYP is the route type (e.g., 'M' for Motorway, 'S' for State road, 'C' for County road)
roads = pmg.read("tiger://roads?year=2022&state=06&county=037")

# Create an interactive line plot of the roads, colored by their type
# The 'RTTYP' column provides road classifications
roads.plot.line(
    column="RTTYP",
    title="Roads in Los Angeles County by Type (2022)",
    legend=True,
    tooltip=["FULLNAME", "RTTYP"]  # Show road name and type on hover
).show()
```

### Interacting with Local Geospatial Files

This example shows how to load a local GeoJSON file, combine it with Census data (TIGER/Line county boundaries), perform a spatial join, and visualize the result. It highlights the use of `file://` URLs and basic spatial analysis.

[Details and Code](./examples/local_file_interaction/README.md)

```python
import pymapgis as pmg
import matplotlib.pyplot as plt # Typically imported by pymapgis.plot, but good for explicit show()

# Load points of interest from a local GeoJSON file
# Ensure 'sample_data.geojson' is in the same directory or provide the correct path
local_pois = pmg.read("file://sample_data.geojson")

# Load county boundaries for California (State FIPS: 06)
counties = pmg.read("tiger://county?year=2022&state=06")

# Filter for Los Angeles County
la_county = counties[counties["NAME"] == "Los Angeles"]

# Perform a spatial join to find POIs within Los Angeles County
# This also transfers attributes from la_county to the POIs if needed
pois_in_la = local_pois.sjoin(la_county, how="inner", predicate="within")

# Create a base map of LA County's boundary
ax = la_county.plot.boundary(edgecolor="black", figsize=(10, 10))

# Plot the points of interest on the same map
# Style points by 'amenity' and add tooltips
pois_in_la.plot.scatter(
    ax=ax,
    column="amenity",
    legend=True,
    tooltip=["name", "amenity"]
)

ax.set_title("Points of Interest in Los Angeles County")
plt.show() # Ensure the plot is displayed
```

### Generating and Visualizing Simulated Geospatial Data

This example demonstrates creating a GeoDataFrame with simulated point data (random coordinates and attributes) and then visualizing it using PyMapGIS plotting capabilities. This is useful for testing or creating reproducible examples without external data dependencies.

[Details and Code](./examples/simulated_data_example/README.md)

```python
import pymapgis as pmg
import geopandas as gpd
import numpy as np
import pandas as pd
from shapely.geometry import Point

# --- 1. Generate Simulated Data ---
num_points = 50

# Generate random coordinates (e.g., within Los Angeles County bounds)
np.random.seed(42) # for reproducibility
lats = np.random.uniform(33.7, 34.3, num_points)
lons = np.random.uniform(-118.8, -117.8, num_points)

# Generate random attribute data
temperatures = np.random.uniform(15, 30, num_points) # Degrees Celsius
humidity = np.random.uniform(30, 70, num_points)    # Percentage

# Create Shapely Point objects
geometry = [Point(lon, lat) for lon, lat in zip(lons, lats)]

# Create a GeoDataFrame
simulated_gdf = gpd.GeoDataFrame({
    'temperature': temperatures,
    'humidity': humidity,
    'geometry': geometry
}, crs="EPSG:4326")

# --- 2. Display Data Information (Optional) ---
print("Simulated GeoDataFrame (First 5 rows):")
print(simulated_gdf.head())
print(f"\nCRS: {simulated_gdf.crs}")

# --- 3. Visualize Data using PyMapGIS ---
# Create a scatter plot, color points by temperature
# Tooltips will show temperature and humidity on hover
simulated_gdf.plot.scatter(
    column="temperature",
    cmap="coolwarm", # Color map for temperature
    legend=True,
    title="Simulated Environmental Data Points",
    tooltip=['temperature', 'humidity'],
    figsize=(10, 8)
).show()
```


### Interactive Mapping with Leafmap

This example showcases how to load geospatial data (e.g., US States from TIGER/Line) and render an interactive choropleth map using PyMapGIS's Leafmap integration. It demonstrates creating tooltips and customizing map appearance.

[Details and Code](./examples/interactive_mapping_leafmap/README.md)

```python
import pymapgis as pmg

# Load US states data
states = pmg.read("tiger://states?year=2022&variables=ALAND")
states['ALAND'] = pmg.pd.to_numeric(states['ALAND'], errors='coerce')

# Create an interactive choropleth map of land area
states.plot.choropleth(
    column="ALAND",
    tooltip=["NAME", "ALAND"],
    cmap="viridis",
    legend_name="Land Area (sq. meters)",
    title="US States by Land Area (2022)"
).show() # In a script, this might save to HTML or open in browser
```

### Managing PyMapGIS Cache (API & CLI)

This example demonstrates how to inspect and manage the PyMapGIS data cache. It covers using the Python API to get cache path, size, list items, and clear the cache. It also lists the corresponding CLI commands for these operations.

[Details and Code](./examples/cache_management_example/README.md)

```python
import pymapgis as pmg

# --- API Usage ---
# Get cache directory
print(f"Cache directory: {pmg.cache.get_cache_dir()}")

# Make a sample request to add to cache
_ = pmg.read("tiger://rails?year=2022")

# List cached items
print("Cached items:")
for url, details in pmg.cache.list_cache().items():
    print(f"- {url} ({details['size_hr']})")

# Clear the cache
# pmg.cache.clear_cache()
# print("Cache cleared.")

# --- CLI Commands (for reference) ---
# pymapgis cache path
# pymapgis cache list
# pymapgis cache clear
```

### Listing Available Plugins (API & CLI)

This example shows how to discover available plugins in PyMapGIS. It uses the plugin registry API to list registered plugins and also mentions the `pymapgis plugin list` CLI command.

[Details and Code](./examples/plugin_system_example/README.md)

```python
from pymapgis.plugins import plugin_registry # Or appropriate import

# --- API Usage ---
try:
    plugins = plugin_registry.list_plugins()
    if plugins:
        print("Available plugins:")
        for name in plugins: # Or iterate items if it's a dict
            print(f"- {name}")
    else:
        print("No plugins found.")
except Exception as e:
    print(f"Error listing plugins: {e}")


# --- CLI Command (for reference) ---
# pymapgis plugin list
```
