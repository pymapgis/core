import pymapgis as pmg
import leafmap.foliumap as leafmap # Explicitly import for clarity in example

def create_interactive_map():
    """
    Loads US state-level TIGER/Line data and creates an interactive choropleth map
    showing the land area of each state.
    """
    try:
        # Load US states data using the TIGER/Line provider
        # ALAND is the land area attribute
        print("Loading US states data...")
        states = pmg.read("tiger://states?year=2022&variables=ALAND")

        if states is None or states.empty:
            print("Failed to load states data or data is empty.")
            return

        print(f"Loaded {len(states)} states.")
        print("First few rows of the data:")
        print(states.head())

        # Ensure ALAND is numeric for mapping
        states['ALAND'] = pmg.pd.to_numeric(states['ALAND'], errors='coerce')
        states = states.dropna(subset=['ALAND']) # Remove rows where ALAND could not be coerced

        if states.empty:
            print("No valid ALAND data available after conversion.")
            return

        # Create an interactive choropleth map
        print("Creating interactive map...")
        m = states.plot.choropleth(
            column="ALAND",       # Column to use for color intensity
            tooltip=["NAME", "ALAND"], # Columns to show in tooltip
            cmap="viridis",       # Colormap
            legend_name="Land Area (sq. meters)",
            title="US States by Land Area (2022)",
            # Default interactive map is via leafmap if installed
        )

        if m is None:
            print("Map object was not created. Ensure leafmap is installed and integrated.")
            return

        # The .show() method in pymapgis for GeoDataFrame plots usually handles this.
        # If running in a script, the map might be saved to HTML or displayed
        # depending on the environment and leafmap's default behavior.
        # For explicit saving to HTML:
        output_html_path = "us_states_land_area_map.html"
        m.to_html(output_html_path)
        print(f"Interactive map saved to {output_html_path}")
        print("If running in a Jupyter environment, the map should display automatically.")
        print("Otherwise, open the .html file in a web browser to view the map.")

    except Exception as e:
        print(f"An error occurred: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    create_interactive_map()
