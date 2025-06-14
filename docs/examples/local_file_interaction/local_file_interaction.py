import pymapgis as pmg

# Load the local GeoJSON file
# Assuming the script is run from examples/local_file_interaction/
local_pois = pmg.read("file://sample_data.geojson")

# Load Census county boundaries for California
counties = pmg.read("tiger://county?year=2022&state=06")

# Filter for Los Angeles County
la_county = counties[counties["NAME"] == "Los Angeles"]

# Perform a spatial join
pois_in_la = local_pois.sjoin(la_county, how="inner", predicate="within")

# Create a base map of LA County
base_map = la_county.plot.boundary(edgecolor="black")

# Plot the points of interest on top of the county map
pois_in_la.plot.scatter(ax=base_map, column="amenity", legend=True, tooltip=["name", "amenity"])

# Add a title
base_map.set_title("Points of Interest in Los Angeles County")

# Show the map
# Assuming pmg.plt is available and is matplotlib.pyplot
# If not, this might need adjustment e.g. base_map.figure.show()
if hasattr(pmg, 'plt') and hasattr(pmg.plt, 'show'):
    pmg.plt.show()
elif hasattr(base_map, 'figure') and hasattr(base_map.figure, 'show'):
    base_map.figure.show()
else:
    print("Could not display plot. Please ensure Matplotlib is configured correctly for your environment.")
