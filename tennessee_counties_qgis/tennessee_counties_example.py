#!/usr/bin/env python3
"""
Tennessee Counties Example using PyMapGIS

This example demonstrates:
1. Downloading Tennessee counties data from US Census Bureau
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
STATE_NAME = "Tennessee"
STATE_FIPS = "47"  # Tennessee FIPS code
DATA_DIR = Path(__file__).parent / "data"
TIGER_URL = "https://www2.census.gov/geo/tiger/TIGER2023/COUNTY/tl_2023_us_county.zip"

def setup_data_directory():
    """Create data directory if it doesn't exist."""
    DATA_DIR.mkdir(exist_ok=True)
    print(f"📁 Data directory: {DATA_DIR}")

def create_sample_data():
    """Create sample Tennessee counties data if download fails."""
    print("🔧 Creating sample Tennessee counties data...")

    from shapely.geometry import Polygon
    import pandas as pd

    # Sample Tennessee counties with approximate boundaries
    sample_counties = [
        {"NAME": "Davidson", "STATEFP": "47", "COUNTYFP": "037",
         "geometry": Polygon([(-87.0, 36.0), (-86.5, 36.0), (-86.5, 36.5), (-87.0, 36.5)])},
        {"NAME": "Shelby", "STATEFP": "47", "COUNTYFP": "157",
         "geometry": Polygon([(-90.5, 35.0), (-89.5, 35.0), (-89.5, 35.5), (-90.5, 35.5)])},
        {"NAME": "Knox", "STATEFP": "47", "COUNTYFP": "093",
         "geometry": Polygon([(-84.5, 35.8), (-83.5, 35.8), (-83.5, 36.3), (-84.5, 36.3)])},
        {"NAME": "Hamilton", "STATEFP": "47", "COUNTYFP": "065",
         "geometry": Polygon([(-85.5, 35.0), (-85.0, 35.0), (-85.0, 35.5), (-85.5, 35.5)])},
        {"NAME": "Williamson", "STATEFP": "47", "COUNTYFP": "187",
         "geometry": Polygon([(-87.2, 35.8), (-86.8, 35.8), (-86.8, 36.2), (-87.2, 36.2)])},
        {"NAME": "Rutherford", "STATEFP": "47", "COUNTYFP": "149",
         "geometry": Polygon([(-86.8, 35.7), (-86.2, 35.7), (-86.2, 36.1), (-86.8, 36.1)])},
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

def filter_tennessee_counties(shp_path):
    """Filter counties data for Tennessee using PyMapGIS."""
    print(f"🗺️  Loading counties data with PyMapGIS...")

    # Use PyMapGIS to read the shapefile
    counties_gdf = pmg.read(str(shp_path))
    print(f"   Loaded {len(counties_gdf)} total counties")

    # Filter for Tennessee counties
    tennessee_counties = counties_gdf[counties_gdf["STATEFP"] == STATE_FIPS].copy()
    print(f"   Found {len(tennessee_counties)} counties in {STATE_NAME}")

    # Save Tennessee counties
    tennessee_shp = DATA_DIR / f"tennessee_counties.gpkg"
    tennessee_counties.to_file(tennessee_shp, driver="GPKG")
    print(f"✅ Saved Tennessee counties: {tennessee_shp}")

    return tennessee_counties, tennessee_shp

def analyze_counties_data(tennessee_counties):
    """Perform basic analysis on Tennessee counties."""
    print(f"\n📊 Tennessee Counties Analysis")
    print("=" * 40)

    # Basic statistics
    print(f"Total counties: {len(tennessee_counties)}")
    print(f"Total area: {tennessee_counties.geometry.area.sum():.2f} square degrees")

    # Calculate areas in square kilometers (approximate)
    tennessee_counties_proj = tennessee_counties.to_crs('EPSG:3857')  # Web Mercator
    areas_km2 = tennessee_counties_proj.geometry.area / 1_000_000  # Convert to km²
    tennessee_counties['area_km2'] = areas_km2

    print(f"Total area: {areas_km2.sum():.0f} km²")
    print(f"Largest county: {tennessee_counties.loc[areas_km2.idxmax(), 'NAME']} ({areas_km2.max():.0f} km²)")
    print(f"Smallest county: {tennessee_counties.loc[areas_km2.idxmin(), 'NAME']} ({areas_km2.min():.0f} km²)")
    print(f"Average county area: {areas_km2.mean():.0f} km²")

    # Tennessee regional analysis
    print(f"\n🏔️  Regional Analysis")
    print("-" * 30)
    
    # Approximate regional boundaries (longitude-based)
    east_tn = tennessee_counties[tennessee_counties.geometry.centroid.x > -85.5]
    middle_tn = tennessee_counties[(tennessee_counties.geometry.centroid.x >= -87.5) & 
                                  (tennessee_counties.geometry.centroid.x <= -85.5)]
    west_tn = tennessee_counties[tennessee_counties.geometry.centroid.x < -87.5]
    
    print(f"East Tennessee: {len(east_tn)} counties")
    print(f"Middle Tennessee: {len(middle_tn)} counties") 
    print(f"West Tennessee: {len(west_tn)} counties")

    return tennessee_counties

def create_visualizations(tennessee_counties):
    """Create visualizations of Tennessee counties."""
    print(f"\n🎨 Creating visualizations...")

    # Set up the plot style
    plt.style.use('default')
    sns.set_palette("husl")

    # Create figure with subplots
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
    fig.suptitle('Tennessee Counties Analysis', fontsize=16, fontweight='bold')

    # 1. Basic map
    tennessee_counties.plot(ax=ax1, color='lightblue', edgecolor='black', linewidth=0.5)
    ax1.set_title('Tennessee Counties')
    ax1.set_xlabel('Longitude')
    ax1.set_ylabel('Latitude')
    ax1.grid(True, alpha=0.3)

    # 2. Choropleth by area
    tennessee_counties.plot(column='area_km2', ax=ax2, cmap='YlOrRd',
                          legend=True, edgecolor='black', linewidth=0.5)
    ax2.set_title('Counties by Area (km²)')
    ax2.set_xlabel('Longitude')
    ax2.set_ylabel('Latitude')
    ax2.grid(True, alpha=0.3)

    # 3. Area distribution histogram
    ax3.hist(tennessee_counties['area_km2'], bins=20, color='skyblue', alpha=0.7, edgecolor='black')
    ax3.set_title('Distribution of County Areas')
    ax3.set_xlabel('Area (km²)')
    ax3.set_ylabel('Number of Counties')
    ax3.grid(True, alpha=0.3)

    # 4. Regional distribution
    # Approximate regional boundaries (longitude-based)
    east_tn = tennessee_counties[tennessee_counties.geometry.centroid.x > -85.5]
    middle_tn = tennessee_counties[(tennessee_counties.geometry.centroid.x >= -87.5) & 
                                  (tennessee_counties.geometry.centroid.x <= -85.5)]
    west_tn = tennessee_counties[tennessee_counties.geometry.centroid.x < -87.5]
    
    regions = ['East TN', 'Middle TN', 'West TN']
    counts = [len(east_tn), len(middle_tn), len(west_tn)]
    colors = ['lightcoral', 'lightgreen', 'lightskyblue']
    
    bars = ax4.bar(regions, counts, color=colors, alpha=0.7, edgecolor='black')
    ax4.set_title('Counties by Tennessee Region')
    ax4.set_ylabel('Number of Counties')
    ax4.grid(True, alpha=0.3, axis='y')
    
    # Add count labels on bars
    for bar, count in zip(bars, counts):
        ax4.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5,
                str(count), ha='center', va='bottom', fontweight='bold')

    plt.tight_layout()

    # Save the plot
    plot_path = DATA_DIR / "tennessee_counties_analysis.png"
    plt.savefig(plot_path, dpi=300, bbox_inches='tight')
    print(f"✅ Saved visualization: {plot_path}")

    # Close the plot (don't show in headless environment)
    plt.close()

def create_interactive_map(tennessee_counties):
    """Create an interactive map using folium."""
    print(f"\n🗺️  Creating interactive map...")

    try:
        import folium

        # Calculate center of Tennessee
        bounds = tennessee_counties.total_bounds
        center_lat = (bounds[1] + bounds[3]) / 2
        center_lon = (bounds[0] + bounds[2]) / 2

        # Create folium map
        m = folium.Map(location=[center_lat, center_lon], zoom_start=7)

        # Add counties to map with regional coloring
        def get_region_color(county_centroid_x):
            if county_centroid_x > -85.5:
                return 'lightcoral'  # East TN
            elif county_centroid_x >= -87.5:
                return 'lightgreen'  # Middle TN
            else:
                return 'lightskyblue'  # West TN

        # Add counties to map
        for _, county in tennessee_counties.iterrows():
            centroid_x = county.geometry.centroid.x
            color = get_region_color(centroid_x)
            
            folium.GeoJson(
                county.geometry.__geo_interface__,
                style_function=lambda feature, color=color: {
                    'fillColor': color,
                    'color': 'black',
                    'weight': 1,
                    'fillOpacity': 0.7,
                },
                popup=folium.Popup(f"<b>{county['NAME']} County</b><br>Area: {county['area_km2']:.0f} km²", max_width=200),
                tooltip=folium.Tooltip(f"{county['NAME']} County")
            ).add_to(m)

        # Add legend
        legend_html = '''
        <div style="position: fixed; 
                    bottom: 50px; left: 50px; width: 150px; height: 90px; 
                    background-color: white; border:2px solid grey; z-index:9999; 
                    font-size:14px; padding: 10px">
        <p><b>Tennessee Regions</b></p>
        <p><i class="fa fa-square" style="color:lightcoral"></i> East Tennessee</p>
        <p><i class="fa fa-square" style="color:lightgreen"></i> Middle Tennessee</p>
        <p><i class="fa fa-square" style="color:lightskyblue"></i> West Tennessee</p>
        </div>
        '''
        m.get_root().html.add_child(folium.Element(legend_html))

        # Save map
        map_path = DATA_DIR / "tennessee_counties_interactive.html"
        m.save(str(map_path))
        print(f"✅ Saved interactive map: {map_path}")

    except ImportError:
        print("⚠️  Interactive map creation skipped (folium not available)")
    except Exception as e:
        print(f"⚠️  Interactive map creation failed: {e}")

def prepare_for_qgis(tennessee_shp):
    """Prepare data and instructions for QGIS integration."""
    print(f"\n🎯 QGIS Integration Ready!")
    print("=" * 30)
    print(f"Tennessee counties data saved to: {tennessee_shp}")
    print(f"")
    print(f"To use in QGIS:")
    print(f"1. Open QGIS")
    print(f"2. Add Vector Layer: {tennessee_shp}")
    print(f"3. Or run: python create_qgis_project.py")
    print(f"")
    print(f"For PyQGIS automation:")
    print(f"   counties_layer = QgsVectorLayer('{tennessee_shp}', 'Tennessee Counties', 'ogr')")

def main():
    """Main execution function."""
    print("🏛️  Tennessee Counties Example - PyMapGIS Integration")
    print("=" * 60)

    try:
        # Setup
        setup_data_directory()

        # Download and extract data
        zip_path = download_counties_data()
        shp_path = extract_counties_data(zip_path)

        # Process with PyMapGIS
        tennessee_counties, tennessee_shp = filter_tennessee_counties(shp_path)

        # Analysis
        tennessee_counties = analyze_counties_data(tennessee_counties)

        # Visualizations
        create_visualizations(tennessee_counties)
        create_interactive_map(tennessee_counties)

        # QGIS preparation
        prepare_for_qgis(tennessee_shp)

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
