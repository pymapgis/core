import pymapgis as pmg

# Load TIGER/Line data for roads in Los Angeles County, CA (state='06', county='037')
roads = pmg.read("tiger://roads?year=2022&state=06&county=037")

# Visualize the loaded road data
fig = roads.plot.line(column="RTTYP", title="Roads in Los Angeles County by Type", legend=True)
fig.show()
