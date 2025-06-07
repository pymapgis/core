#!/usr/bin/env python3
"""Simple test of PyMapGIS functionality"""

import pymapgis as pm

print("Testing ACS data fetch...")
try:
    # Test ACS data fetching for a small state
    acs = pm.get_county_table(2022, ["B23025_004E", "B23025_003E"], state="06")
    print(f"✓ Fetched ACS data for {len(acs)} counties")

    # Calculate ratio
    acs["lfp"] = acs["B23025_004E"] / acs["B23025_003E"]
    print("✓ Calculated labor force participation rates")
    print(f"  Average LFP: {acs['lfp'].mean():.3f}")

except Exception as e:
    print(f"✗ ACS test failed: {e}")
    raise

print("\nTesting counties shapefile...")
try:
    # Test counties download (this might take a while)
    gdf = pm.counties(2022, "20m")
    print(f"✓ Downloaded counties shapefile with {len(gdf)} counties")
    print(f"  Columns: {list(gdf.columns)}")

except Exception as e:
    print(f"✗ Counties test failed: {e}")
    raise

print("\n✅ All tests passed!")
