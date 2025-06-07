"""
AFTER: Housing Cost Burden using PyMapGIS
Run:  python app.py
Produces:  housing_burden_map.png
"""

import pymapgis as pm

# --- 1. Fetch data ----------------------------------------------------------
VARS = ["B25070_001E", "B25070_007E", "B25070_008E", "B25070_009E", "B25070_010E"]
acs = pm.get_county_table(2022, VARS)

# --- 2. Calculate burden rate -----------------------------------------------
# Calculate housing cost burden (30%+ of income on housing)
acs["burden_30plus"] = (
    acs["B25070_007E"] + acs["B25070_008E"] + acs["B25070_009E"] + acs["B25070_010E"]
)
acs["burden_rate"] = acs["burden_30plus"] / acs["B25070_001E"]

# --- 3. Join geometry -------------------------------------------------------
gdf = pm.counties(2022, "20m")
# Ensure consistent column names for joining
if "GEOID" in gdf.columns:
    gdf = gdf.rename(columns={"GEOID": "geoid"})
merged = gdf.merge(acs[["geoid", "burden_rate"]], on="geoid", how="left")

# --- 4. Plot ----------------------------------------------------------------
ax = pm.choropleth(
    merged,
    "burden_rate",
    cmap="Reds",
    title="Housing Cost Burden (30%+ of Income), 2022 ACS",
)
ax.figure.savefig("housing_burden_map.png", dpi=150, bbox_inches="tight")
print("✓ Map saved to housing_burden_map.png")
