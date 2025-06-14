#!/usr/bin/env python3
"""
Arkansas Counties Example using PyMapGIS

This example demonstrates:
1. Downloading Arkansas counties data from US Census Bureau
2. Processing the data with PyMapGIS
3. Creating visualizations and analysis
4. Preparing data for QGIS integration

Author: PyMapGIS Team
"""

import os
import sys
import requests
import zipfile
from pathlib import Path
import geopandas as gpd
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import seaborn as sns
import urllib3

# Suppress SSL warnings for Census Bureau downloads
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Add PyMapGIS to path if running from examples directory
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

try:
    import pymapgis as pmg
    print("✅ PyMapGIS imported successfully")
except ImportError as e:
    print(f"❌ Error importing PyMapGIS: {e}")
    print("Make sure PyMapGIS is installed: pip install pymapgis")
    sys.exit(1)

# Configuration
STATE_NAME = "Arkansas"
STATE_FIPS = "05"  # Arkansas FIPS code
DATA_DIR = Path(__file__).parent / "data"
TIGER_URL = "https://www2.census.gov/geo/tiger/TIGER2023/COUNTY/tl_2023_us_county.zip"

def setup_data_directory():
    """Create data directory if it doesn't exist."""
    DATA_DIR.mkdir(exist_ok=True)
    print(f"📁 Data directory: {DATA_DIR}")

def create_sample_data():
    """Create sample Arkansas counties data if download fails."""
    print("🔧 Creating sample Arkansas counties data...")

    from shapely.geometry import Polygon
    import pandas as pd

    # Sample Arkansas counties with approximate boundaries
    sample_counties = [
        {"NAME": "Pulaski", "STATEFP": "05", "COUNTYFP": "119",
         "geometry": Polygon([(-92.5, 34.6), (-92.2, 34.6), (-92.2, 34.9), (-92.5, 34.9)])},
        {"NAME": "Washington", "STATEFP": "05", "COUNTYFP": "143",
         "geometry": Polygon([(-94.5, 35.8), (-94.0, 35.8), (-94.0, 36.3), (-94.5, 36.3)])},
        {"NAME": "Benton", "STATEFP": "05", "COUNTYFP": "007",
         "geometry": Polygon([(-94.5, 36.0), (-94.0, 36.0), (-94.0, 36.5), (-94.5, 36.5)])},
        {"NAME": "Sebastian", "STATEFP": "05", "COUNTYFP": "131",
         "geometry": Polygon([(-94.5, 35.2), (-94.0, 35.2), (-94.0, 35.7), (-94.5, 35.7)])},
        {"NAME": "Garland", "STATEFP": "05", "COUNTYFP": "051",
         "geometry": Polygon([(-93.5, 34.3), (-93.0, 34.3), (-93.0, 34.8), (-93.5, 34.8)])},
    ]

    # Create GeoDataFrame
    sample_gdf = gpd.GeoDataFrame(sample_counties, crs="EPSG:4326")

    # Save as shapefile
    sample_shp = DATA_DIR / "tl_2023_us_county.shp"
    sample_gdf.to_file(sample_shp)

    print(f"✅ Created sample data with {len(sample_gdf)} counties: {sample_shp}")
    return sample_shp

def download_counties_data():
    """Download US counties shapefile from Census Bureau."""
    zip_path = DATA_DIR / "tl_2023_us_county.zip"

    if zip_path.exists():
        print("📦 Counties data already downloaded, skipping...")
        return zip_path

    print(f"🌐 Downloading US counties data from Census Bureau...")
    print(f"   URL: {TIGER_URL}")

    try:
        # Disable SSL verification for Census Bureau (common issue)
        response = requests.get(TIGER_URL, stream=True, verify=False)
        response.raise_for_status()

        with open(zip_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)

        print(f"✅ Download complete: {zip_path}")
        return zip_path

    except requests.RequestException as e:
        print(f"❌ Download failed: {e}")
        print("🔄 Trying to create sample data instead...")
        return create_sample_data()

def extract_counties_data(zip_path):
    """Extract the counties shapefile."""
    # If zip_path is actually a shapefile (from sample data), return it directly
    if str(zip_path).endswith('.shp'):
        print(f"📂 Using existing shapefile: {zip_path}")
        return zip_path

    print("📂 Extracting counties data...")

    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(DATA_DIR)

    shp_path = DATA_DIR / "tl_2023_us_county.shp"
    if shp_path.exists():
        print(f"✅ Extraction complete: {shp_path}")
        return shp_path
    else:
        print("❌ Shapefile not found after extraction")
        sys.exit(1)

def filter_arkansas_counties(shp_path):
    """Filter counties data for Arkansas using PyMapGIS."""
    print(f"🗺️  Loading counties data with PyMapGIS...")

    # Use PyMapGIS to read the shapefile
    counties_gdf = pmg.read(str(shp_path))
    print(f"   Loaded {len(counties_gdf)} total counties")

    # Filter for Arkansas counties
    arkansas_counties = counties_gdf[counties_gdf["STATEFP"] == STATE_FIPS].copy()
    print(f"   Found {len(arkansas_counties)} counties in {STATE_NAME}")

    # Save Arkansas counties
    arkansas_shp = DATA_DIR / f"arkansas_counties.gpkg"
    arkansas_counties.to_file(arkansas_shp, driver="GPKG")
    print(f"✅ Saved Arkansas counties: {arkansas_shp}")

    return arkansas_counties, arkansas_shp

def analyze_counties_data(arkansas_counties):
    """Perform basic analysis on Arkansas counties."""
    print(f"\n📊 Arkansas Counties Analysis")
    print("=" * 40)

    # Basic statistics
    print(f"Total counties: {len(arkansas_counties)}")
    print(f"Total area: {arkansas_counties.geometry.area.sum():.2f} square degrees")

    # Calculate areas in square kilometers (approximate)
    arkansas_counties_proj = arkansas_counties.to_crs('EPSG:3857')  # Web Mercator
    areas_km2 = arkansas_counties_proj.geometry.area / 1_000_000  # Convert to km²
    arkansas_counties['area_km2'] = areas_km2

    print(f"Total area: {areas_km2.sum():.0f} km²")
    print(f"Largest county: {arkansas_counties.loc[areas_km2.idxmax(), 'NAME']} ({areas_km2.max():.0f} km²)")
    print(f"Smallest county: {arkansas_counties.loc[areas_km2.idxmin(), 'NAME']} ({areas_km2.min():.0f} km²)")
    print(f"Average county area: {areas_km2.mean():.0f} km²")

    return arkansas_counties

def create_visualizations(arkansas_counties):
    """Create visualizations of Arkansas counties."""
    print(f"\n🎨 Creating visualizations...")

    # Set up the plot style
    plt.style.use('default')
    sns.set_palette("husl")

    # Create figure with subplots
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
    fig.suptitle('Arkansas Counties Analysis', fontsize=16, fontweight='bold')

    # 1. Basic map
    arkansas_counties.plot(ax=ax1, color='lightblue', edgecolor='black', linewidth=0.5)
    ax1.set_title('Arkansas Counties')
    ax1.set_xlabel('Longitude')
    ax1.set_ylabel('Latitude')
    ax1.grid(True, alpha=0.3)

    # 2. Choropleth by area
    arkansas_counties.plot(column='area_km2', ax=ax2, cmap='YlOrRd',
                          legend=True, edgecolor='black', linewidth=0.5)
    ax2.set_title('Counties by Area (km²)')
    ax2.set_xlabel('Longitude')
    ax2.set_ylabel('Latitude')
    ax2.grid(True, alpha=0.3)

    # 3. Area distribution histogram
    ax3.hist(arkansas_counties['area_km2'], bins=15, color='skyblue', alpha=0.7, edgecolor='black')
    ax3.set_title('Distribution of County Areas')
    ax3.set_xlabel('Area (km²)')
    ax3.set_ylabel('Number of Counties')
    ax3.grid(True, alpha=0.3)

    # 4. Top 10 largest counties
    top_counties = arkansas_counties.nlargest(10, 'area_km2')
    ax4.barh(range(len(top_counties)), top_counties['area_km2'], color='coral')
    ax4.set_yticks(range(len(top_counties)))
    ax4.set_yticklabels(top_counties['NAME'], fontsize=8)
    ax4.set_title('Top 10 Largest Counties')
    ax4.set_xlabel('Area (km²)')
    ax4.grid(True, alpha=0.3, axis='x')

    plt.tight_layout()

    # Save the plot
    plot_path = DATA_DIR / "arkansas_counties_analysis.png"
    plt.savefig(plot_path, dpi=300, bbox_inches='tight')
    print(f"✅ Saved visualization: {plot_path}")

    # Close the plot (don't show in headless environment)
    plt.close()

def create_interactive_map(arkansas_counties):
    """Create an interactive map using PyMapGIS plotting capabilities."""
    print(f"\n🗺️  Creating interactive map...")

    try:
        # Use PyMapGIS plotting functionality if available
        # This demonstrates the plotting capabilities
        if hasattr(arkansas_counties, 'plot') and hasattr(arkansas_counties.plot, 'interactive'):
            interactive_map = arkansas_counties.plot.interactive()

            # Save the map
            map_path = DATA_DIR / "arkansas_counties_interactive.html"
            interactive_map.save(str(map_path))
            print(f"✅ Saved interactive map: {map_path}")

            # Display the map
            interactive_map.show()
        else:
            # Fallback: create a simple interactive map with folium
            try:
                import folium

                # Calculate center of Arkansas
                bounds = arkansas_counties.total_bounds
                center_lat = (bounds[1] + bounds[3]) / 2
                center_lon = (bounds[0] + bounds[2]) / 2

                # Create folium map
                m = folium.Map(location=[center_lat, center_lon], zoom_start=7)

                # Add counties to map
                folium.GeoJson(
                    arkansas_counties.to_json(),
                    style_function=lambda feature: {
                        'fillColor': 'lightblue',
                        'color': 'black',
                        'weight': 1,
                        'fillOpacity': 0.7,
                    },
                    popup=folium.GeoJsonPopup(fields=['NAME'], aliases=['County:']),
                    tooltip=folium.GeoJsonTooltip(fields=['NAME'], aliases=['County:'])
                ).add_to(m)

                # Save map
                map_path = DATA_DIR / "arkansas_counties_interactive.html"
                m.save(str(map_path))
                print(f"✅ Saved interactive map: {map_path}")

            except ImportError:
                print("⚠️  Interactive map creation skipped (folium not available)")

    except Exception as e:
        print(f"⚠️  Interactive map creation failed: {e}")
        print("   This requires leafmap or folium to be installed")

def prepare_for_qgis(arkansas_shp):
    """Prepare data and instructions for QGIS integration."""
    print(f"\n🎯 QGIS Integration Ready!")
    print("=" * 30)
    print(f"Arkansas counties data saved to: {arkansas_shp}")
    print(f"")
    print(f"To use in QGIS:")
    print(f"1. Open QGIS")
    print(f"2. Add Vector Layer: {arkansas_shp}")
    print(f"3. Or run: python create_qgis_project.py")
    print(f"")
    print(f"For PyQGIS automation:")
    print(f"   counties_layer = QgsVectorLayer('{arkansas_shp}', 'Arkansas Counties', 'ogr')")

def main():
    """Main execution function."""
    print("🏛️  Arkansas Counties Example - PyMapGIS Integration")
    print("=" * 60)

    try:
        # Setup
        setup_data_directory()

        # Download and extract data
        zip_path = download_counties_data()
        shp_path = extract_counties_data(zip_path)

        # Process with PyMapGIS
        arkansas_counties, arkansas_shp = filter_arkansas_counties(shp_path)

        # Analysis
        arkansas_counties = analyze_counties_data(arkansas_counties)

        # Visualizations
        create_visualizations(arkansas_counties)
        create_interactive_map(arkansas_counties)

        # QGIS preparation
        prepare_for_qgis(arkansas_shp)

        print(f"\n🎉 Example completed successfully!")
        print(f"Check the {DATA_DIR} directory for all generated files.")

    except KeyboardInterrupt:
        print(f"\n⚠️  Example interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Example failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
