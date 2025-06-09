"""
AFTER: Oklahoma Economic Indicators using PyMapGIS
Run:  python app.py
Produces:  oklahoma_income_map.png

This script creates a map of median household income by county in Oklahoma
using the streamlined PyMapGIS approach.
"""

import pymapgis as pmg

print("🚀 OKLAHOMA ECONOMIC INDICATORS - PyMapGIS Approach")
print("=" * 55)

# --- 1. Fetch economic data for Oklahoma counties -------------------------------
print("📊 Fetching Oklahoma economic data...")

# Get median household income data for Oklahoma (state FIPS: 40)
VARS = ["B19013_001E"]  # Median household income
oklahoma_data = pmg.get_county_table(2022, VARS, state="40")

print(f"   ✓ Retrieved data for {len(oklahoma_data)} Oklahoma counties")

# --- 2. Process and clean data -----------------------------------------------
print("🔧 Processing economic indicators...")

# Rename for clarity
oklahoma_data = oklahoma_data.rename(columns={"B19013_001E": "median_income"})

# Remove counties with missing data
oklahoma_data = oklahoma_data.dropna(subset=["median_income"])

print(f"   ✓ Processed {len(oklahoma_data)} counties with valid income data")
print(f"   📈 Income range: ${oklahoma_data['median_income'].min():,.0f} - ${oklahoma_data['median_income'].max():,.0f}")

# --- 3. Load Oklahoma county boundaries --------------------------------------
print("🗺️  Loading Oklahoma county boundaries...")

# Get all US county geometries and filter for Oklahoma (state FIPS: 40)
all_counties = pmg.counties(2022, "20m")
oklahoma_counties = all_counties[all_counties["STATEFP"] == "40"].copy()

# Ensure consistent column names for joining
if "GEOID" in oklahoma_counties.columns:
    oklahoma_counties = oklahoma_counties.rename(columns={"GEOID": "geoid"})

print(f"   ✓ Loaded {len(oklahoma_counties)} Oklahoma county boundaries")

# --- 4. Join data with geometries -------------------------------------------
print("🔗 Joining economic data with county boundaries...")

# Merge economic data with county boundaries
merged = oklahoma_counties.merge(
    oklahoma_data[["geoid", "median_income"]], 
    on="geoid", 
    how="left"
)

print(f"   ✓ Successfully joined data for {len(merged[merged['median_income'].notna()])} counties")

# --- 5. Create visualization ------------------------------------------------
print("📈 Creating income distribution map...")

# Create choropleth map using matplotlib backend
import matplotlib.pyplot as plt

fig, ax = plt.subplots(1, 1, figsize=(14, 10))

# Create choropleth map
merged.plot(
    column="median_income",
    cmap="RdYlGn",  # Red-Yellow-Green colormap
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
    "Oklahoma Median Household Income by County\n2022 ACS 5-Year Estimates",
    fontsize=16,
    fontweight="bold",
    pad=20
)

# Remove axes
ax.set_axis_off()

# Save the map
plt.tight_layout()
plt.savefig("oklahoma_income_map.png", dpi=300, bbox_inches="tight")
print("✅ Map saved as 'oklahoma_income_map.png'")

# --- 6. Generate summary statistics -----------------------------------------
print("\n📊 OKLAHOMA ECONOMIC INDICATORS SUMMARY")
print("=" * 50)

valid_data = merged[merged['median_income'].notna()]
print(f"Total counties analyzed: {len(valid_data)}")
print(f"Median household income range: ${valid_data['median_income'].min():,.0f} - ${valid_data['median_income'].max():,.0f}")
print(f"State average: ${valid_data['median_income'].mean():,.0f}")
print(f"Standard deviation: ${valid_data['median_income'].std():,.0f}")

# Top and bottom 5 counties
print(f"\n🏆 TOP 5 COUNTIES BY MEDIAN INCOME:")
top_counties = valid_data.nlargest(5, "median_income")[["NAME", "median_income"]]
for _, row in top_counties.iterrows():
    county_name = row['NAME'].replace(" County, Oklahoma", "")
    print(f"   • {county_name}: ${row['median_income']:,.0f}")

print(f"\n📉 BOTTOM 5 COUNTIES BY MEDIAN INCOME:")
bottom_counties = valid_data.nsmallest(5, "median_income")[["NAME", "median_income"]]
for _, row in bottom_counties.iterrows():
    county_name = row['NAME'].replace(" County, Oklahoma", "")
    print(f"   • {county_name}: ${row['median_income']:,.0f}")

print(f"\n🎯 Analysis complete! Interactive map and data ready for further analysis.")
print(f"💡 Tip: Load 'oklahoma_income_map.png' in QGIS for advanced spatial analysis.")
