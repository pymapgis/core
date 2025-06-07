"""
AFTER: Prime-Age Labor-Force Participation map using PyMapGIS
Run:  python app.py
Produces:  gap_map.png
"""

import pymapgis as pm

# --- 1. Fetch data ----------------------------------------------------------
VARS = ["B23025_004E", "B23025_003E"]  # In labor force, Total population
acs = pm.get_county_table(2022, VARS)

# --- 2. Calculate ratio -----------------------------------------------------
acs["lfp"] = acs["B23025_004E"] / acs["B23025_003E"]
acs["gap"] = 1 - acs["lfp"]  # Gap from 100% participation

# --- 3. Join geometry -------------------------------------------------------
gdf = pm.counties(2022, "20m")
# Ensure consistent column names for joining
if "GEOID" in gdf.columns:
    gdf = gdf.rename(columns={"GEOID": "geoid"})
merged = gdf.merge(acs[["geoid", "gap", "lfp"]], on="geoid", how="left")

# --- 4. Plot ----------------------------------------------------------------
ax = pm.choropleth(
    merged,
    "gap",
    cmap="YlOrRd",
    title="Prime-Age Labor-Force Participation GAP, 2022 ACS",
)
ax.figure.savefig("gap_map.png", dpi=150, bbox_inches="tight")
print("✓ Map saved to gap_map.png")
