"""
BEFORE: Housing Cost Burden map
Run with:  python app.py  <your-census-key>
"""

import sys
import requests
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt

key = sys.argv[1] if len(sys.argv) > 1 else "DEMO_KEY"
vars = "B25070_001E,B25070_007E,B25070_008E,B25070_009E,B25070_010E"
url = (
    f"https://api.census.gov/data/2022/acs/acs5"
    f"?get=NAME,{vars}&for=county:*&key={key}"
)

df = pd.DataFrame(
    requests.get(url).json()[1:],
    columns=[
        "name",
        "total",
        "b30_35",
        "b35_40",
        "b40_50",
        "b50plus",
        "state",
        "county",
    ],
)

# Calculate housing cost burden (30%+ of income on housing)
df["burden_30plus"] = (
    df.b30_35.astype(int)
    + df.b35_40.astype(int)
    + df.b40_50.astype(int)
    + df.b50plus.astype(int)
)
df["burden_rate"] = df.burden_30plus / df.total.astype(int)

shp = gpd.read_file("../../data/counties/cb_2022_us_county_500k.shp")
gdf = shp.merge(df, left_on=["STATEFP", "COUNTYFP"], right_on=["state", "county"])

ax = gdf.plot("burden_rate", cmap="Reds", figsize=(12, 7), legend=True, edgecolor="0.4")
ax.set_title("Housing Cost Burden (30%+ of Income)")
ax.axis("off")
plt.tight_layout()
plt.show()
