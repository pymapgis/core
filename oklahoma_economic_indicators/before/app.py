"""
BEFORE: Oklahoma Economic Indicators map
Run with:  python app.py  <your-census-key>

This script creates a map of median household income by county in Oklahoma
using traditional GeoPandas + requests + matplotlib approach.
"""

import sys
import requests
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import numpy as np

# Census API key (get from command line or use demo key)
key = sys.argv[1] if len(sys.argv) > 1 else "DEMO_KEY"

# Oklahoma state FIPS code
OKLAHOMA_FIPS = "40"

# ACS variable for median household income
vars = "B19013_001E"  # Median household income in the past 12 months

# Build Census API URL for Oklahoma counties
url = (
    f"https://api.census.gov/data/2022/acs/acs5"
    f"?get=NAME,{vars}&for=county:*&in=state:{OKLAHOMA_FIPS}&key={key}"
)

print("📊 Fetching Oklahoma economic data from Census Bureau...")

try:
    response = requests.get(url)
    response.raise_for_status()
    data = response.json()
    
    # Create DataFrame from API response
    df = pd.DataFrame(
        data[1:],  # Skip header row
        columns=[
            "name",
            "median_income",
            "state",
            "county",
        ],
    )
    
    print(f"   ✓ Retrieved data for {len(df)} Oklahoma counties")
    
except requests.RequestException as e:
    print(f"❌ Error fetching data: {e}")
    sys.exit(1)

# Clean and process data
print("🔧 Processing economic indicators...")

# Convert income to numeric, handle missing values
df["median_income"] = pd.to_numeric(df["median_income"], errors="coerce")

# Remove null values and format county names
df = df.dropna(subset=["median_income"])
df["county_name"] = df["name"].str.replace(" County, Oklahoma", "")

# Create GEOID for joining with shapefile
df["geoid"] = df["state"] + df["county"]

print(f"   ✓ Processed {len(df)} counties with valid income data")
print(f"   📈 Income range: ${df['median_income'].min():,.0f} - ${df['median_income'].max():,.0f}")

# Load county boundaries shapefile
print("🗺️  Loading county boundaries...")

try:
    # Note: This assumes you have county shapefiles available
    # In practice, you'd download from Census TIGER/Line or other source
    shp_path = "../../data/counties/cb_2022_us_county_500k.shp"
    shp = gpd.read_file(shp_path)
    
    # Filter for Oklahoma counties
    oklahoma_counties = shp[shp["STATEFP"] == OKLAHOMA_FIPS].copy()
    
    print(f"   ✓ Loaded {len(oklahoma_counties)} Oklahoma county boundaries")
    
except FileNotFoundError:
    print("❌ County shapefile not found. Please download from:")
    print("   https://www.census.gov/geographies/mapping-files/time-series/geo/carto-boundary-file.html")
    sys.exit(1)

# Merge economic data with geographic boundaries
print("🔗 Joining economic data with county boundaries...")

# Create GEOID in shapefile for joining
oklahoma_counties["geoid"] = oklahoma_counties["STATEFP"] + oklahoma_counties["COUNTYFP"]

# Merge datasets
gdf = oklahoma_counties.merge(
    df[["geoid", "median_income", "county_name"]], 
    on="geoid", 
    how="left"
)

print(f"   ✓ Successfully joined data for {len(gdf[gdf['median_income'].notna()])} counties")

# Create visualization
print("📈 Creating income distribution map...")

# Set up the plot
fig, ax = plt.subplots(1, 1, figsize=(14, 10))

# Create choropleth map
gdf.plot(
    column="median_income",
    cmap="RdYlGn",  # Red-Yellow-Green colormap (red=low, green=high)
    linewidth=0.5,
    edgecolor="white",
    legend=True,
    ax=ax,
    missing_kwds={
        "color": "lightgrey",
        "edgecolor": "white",
        "hatch": "///",
        "label": "No data"
    }
)

# Customize the map
ax.set_title(
    "Oklahoma Median Household Income by County\n2022 American Community Survey 5-Year Estimates",
    fontsize=16,
    fontweight="bold",
    pad=20
)

# Remove axes
ax.set_axis_off()

# Add statistics text box
stats_text = f"""
Oklahoma Economic Summary:
• Counties analyzed: {len(gdf[gdf['median_income'].notna()])}
• Median income range: ${gdf['median_income'].min():,.0f} - ${gdf['median_income'].max():,.0f}
• State average: ${gdf['median_income'].mean():,.0f}
• Standard deviation: ${gdf['median_income'].std():,.0f}
"""

ax.text(
    0.02, 0.02, stats_text,
    transform=ax.transAxes,
    fontsize=10,
    verticalalignment="bottom",
    bbox=dict(boxstyle="round,pad=0.5", facecolor="white", alpha=0.8)
)

# Adjust layout and save
plt.tight_layout()
plt.savefig("oklahoma_income_map.png", dpi=300, bbox_inches="tight")
print("✅ Map saved as 'oklahoma_income_map.png'")

# Display summary statistics
print("\n📊 OKLAHOMA ECONOMIC INDICATORS SUMMARY")
print("=" * 50)
print(f"Total counties analyzed: {len(gdf[gdf['median_income'].notna()])}")
print(f"Median household income range: ${gdf['median_income'].min():,.0f} - ${gdf['median_income'].max():,.0f}")
print(f"State average: ${gdf['median_income'].mean():,.0f}")
print(f"Standard deviation: ${gdf['median_income'].std():,.0f}")

# Top and bottom 5 counties
print(f"\n🏆 TOP 5 COUNTIES BY MEDIAN INCOME:")
top_counties = gdf.nlargest(5, "median_income")[["county_name", "median_income"]]
for _, row in top_counties.iterrows():
    print(f"   • {row['county_name']}: ${row['median_income']:,.0f}")

print(f"\n📉 BOTTOM 5 COUNTIES BY MEDIAN INCOME:")
bottom_counties = gdf.nsmallest(5, "median_income")[["county_name", "median_income"]]
for _, row in bottom_counties.iterrows():
    print(f"   • {row['county_name']}: ${row['median_income']:,.0f}")

plt.show()
