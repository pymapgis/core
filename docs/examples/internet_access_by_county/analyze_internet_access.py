import pymapgis as pmg
import pandas as pd
import json
import matplotlib.pyplot as plt # Import for showing the plot

# Define the input JSON file path
JSON_FILE = "ca_county_internet_access_2022.json"

def main():
    # 1. Load the JSON data
    try:
        with open(JSON_FILE, 'r') as f:
            raw_data = json.load(f)
    except FileNotFoundError:
        print(f"Error: The file {JSON_FILE} was not found in the current directory.")
        print("Please make sure the ACS data file is present. It can be downloaded using the instructions in the README.")
        return

    # Create a pandas DataFrame from the JSON data
    # The first list is the header, the rest are data rows.
    header = raw_data[0]
    data_rows = raw_data[1:]
    acs_df = pd.DataFrame(data_rows, columns=header)

    # 2. Data Cleaning and Preparation
    # Identify relevant columns
    total_households_col = 'B28002_001E'
    internet_access_col = 'B28002_002E'
    broadband_access_col = 'B28002_004E'
    state_col = 'state'
    county_col = 'county'

    # Columns to convert to numeric
    numeric_cols = [total_households_col, internet_access_col, broadband_access_col]
    for col in numeric_cols:
        acs_df[col] = pd.to_numeric(acs_df[col], errors='coerce')

    # Create a 'GEOID' column by combining the 'state' and 'county' FIPS codes
    # Ensure state and county columns are strings and padded if necessary
    acs_df['GEOID'] = acs_df[state_col].astype(str).str.zfill(2) + acs_df[county_col].astype(str).str.zfill(3)

    # 3. Load Geospatial Data
    print("Loading California county geometries from TIGER/Line...")
    try:
        # It's good practice to specify the coordinate reference system (CRS) if known,
        # and to reproject if necessary to match the data or for visualization.
        # Common CRS for US maps is EPSG:4269 (NAD83) or EPSG:4326 (WGS84)
        # TIGER/Line data is typically NAD83.
        gdf_counties = pmg.read_tiger("county", year=2022, state="06", crs="EPSG:4269")
    except Exception as e:
        print(f"Error loading TIGER/Line county data: {e}")
        print("Please ensure you have an internet connection and pymapgis is installed correctly.")
        return

    # Ensure gdf_counties has a 'GEOID' column for merging.
    # TIGER/Line files for counties typically have 'STATEFP' and 'COUNTYFP'.
    if 'GEOID' not in gdf_counties.columns:
        if 'STATEFP' in gdf_counties.columns and 'COUNTYFP' in gdf_counties.columns:
            gdf_counties['GEOID'] = gdf_counties['STATEFP'] + gdf_counties['COUNTYFP']
        else:
            print("Error: County GeoDataFrame does not have 'GEOID', 'STATEFP', or 'COUNTYFP' columns.")
            return

    # 4. Merge ACS Data with Geometries
    # Ensure GEOID columns are of the same type for merging
    gdf_counties['GEOID'] = gdf_counties['GEOID'].astype(str)
    acs_df['GEOID'] = acs_df['GEOID'].astype(str)

    merged_gdf = pd.merge(gdf_counties, acs_df, on='GEOID', how='left')

    # Check if merge was successful
    if merged_gdf.empty or merged_gdf[total_households_col].isnull().all():
        print("Error: Merge resulted in an empty DataFrame or no matching ACS data.")
        print("ACS GEOIDs available:", acs_df['GEOID'].unique())
        print("County GEOIDs available:", gdf_counties['GEOID'].unique())
        # Potentially print some head of both dataframes before merge for debugging
        # print("ACS DF Head:\n", acs_df.head())
        # print("County GDF Head:\n", gdf_counties.head())
        return

    # 5. Calculate Percentages
    # Handle potential division by zero by replacing 0s in denominator with NaN
    # This ensures that 0/0 results in NaN, not an error.
    merged_gdf[total_households_col] = merged_gdf[total_households_col].replace(0, float('nan'))

    merged_gdf['percent_internet_access'] = (merged_gdf[internet_access_col] / merged_gdf[total_households_col]) * 100
    merged_gdf['percent_broadband_access'] = (merged_gdf[broadband_access_col] / merged_gdf[total_households_col]) * 100

    # Clean up potential NaN/inf values in percentage columns (e.g., if total_households was NaN)
    merged_gdf['percent_internet_access'] = merged_gdf['percent_internet_access'].fillna(0)
    merged_gdf['percent_broadband_access'] = merged_gdf['percent_broadband_access'].fillna(0)

    # 6. Generate Map
    print("Generating map...")
    try:
        fig, ax = plt.subplots(1, 1, figsize=(12, 10))
        merged_gdf.plot.choropleth(
            column="percent_broadband_access",
            ax=ax,
            legend=True,
            cmap="viridis",
            legend_kwds={'label': "Percent of Households with Broadband Access", 'orientation': "horizontal"}
        )
        ax.set_title("Broadband Internet Access by CA County (2022)", fontsize=15)
        ax.set_axis_off() # Turn off the axis for a cleaner map

        # Save the map to a file
        map_output_filename = "ca_county_broadband_access_map.png"
        plt.savefig(map_output_filename)
        print(f"Map saved as {map_output_filename}")
        # To display the map in a script context, you might need plt.show()
        # However, for automated scripts, saving is often preferred.
        # plt.show() # This might block script execution until the plot window is closed.

    except Exception as e:
        print(f"Error generating map: {e}")
        # If plotting fails, still try to print summary statistics
        pass


    # 7. Print Summary Statistics
    print("\nSummary Statistics for Internet Access by County:")
    summary_stats = merged_gdf[["NAME", "percent_internet_access", "percent_broadband_access"]].describe()
    print(summary_stats)

    print("\nHead of the data (Top 5 counties by default):")
    head_data = merged_gdf[["NAME", "percent_internet_access", "percent_broadband_access"]].head()
    print(head_data)

if __name__ == "__main__":
    main()
