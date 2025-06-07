"""
BEFORE: Prime-Age Labor-Force Participation map
Run with:  python app.py  <your-census-key>
"""

import sys
import requests
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt

key = sys.argv[1] if len(sys.argv) > 1 else "DEMO_KEY"
vars = "B23001_001E,B23001_004E"
url = (
    f"https://api.census.gov/data/2022/acs/acs5"
    f"?get=NAME,{vars}&for=county:*&key={key}"
)

df = pd.DataFrame(
    requests.get(url).json()[1:], columns=["name", "labor", "pop", "state", "county"]
)
df["lfp"] = df.labor.astype(int) / df.pop.astype(int)

shp = gpd.read_file("../../data/counties/cb_2022_us_county_500k.shp")
gdf = shp.merge(df, left_on=["STATEFP", "COUNTYFP"], right_on=["state", "county"])

ax = gdf.plot("lfp", cmap="viridis", figsize=(12, 7), legend=True, edgecolor="0.4")
ax.set_title("Prime-Age Labor-Force Participation")
ax.axis("off")
plt.tight_layout()
plt.show()
