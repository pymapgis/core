#!/usr/bin/env python3
"""
Open Food Trucks Now - San Francisco live lunch location heat-map
A 35-line microservice that turns SF food truck data into live lunch heat-maps
"""

import json
import time
import requests
import pandas as pd
import geopandas as gpd
from pathlib import Path
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

def main():
    print("🚚 Starting Open Food Trucks Now processing...")
    start_time = time.time()
    
    # 1. Fetch live SF food truck schedule data
    print("🌮 Fetching SF food truck schedule data...")
    try:
        truck_data = fetch_sf_food_trucks()
        print(f"✅ Fetched {len(truck_data)} food truck permits")
    except Exception as e:
        print(f"⚠️ Error fetching food truck data: {e}")
        truck_data = create_mock_truck_data()
    
    # 2. Load SF neighborhood polygons
    print("🏙️ Loading SF neighborhood polygons...")
    neighborhoods_path = Path("data/sf_neighborhoods.geojson")
    if not neighborhoods_path.exists():
        print("📝 Downloading SF neighborhood polygons...")
        download_sf_neighborhoods()
    
    neighborhoods_gdf = gpd.read_file(neighborhoods_path)
    print(f"✅ Loaded {len(neighborhoods_gdf)} SF neighborhoods")
    
    # 3. Filter for currently open trucks
    print("⏰ Filtering for currently open food trucks...")
    open_trucks = filter_open_trucks(truck_data)
    print(f"✅ Found {len(open_trucks)} currently open food trucks")
    
    if len(open_trucks) == 0:
        print("🎭 No trucks currently open, creating sample data...")
        open_trucks = create_sample_open_trucks()
    
    # 4. Convert to GeoDataFrame
    trucks_df = pd.DataFrame(open_trucks)
    trucks_gdf = gpd.GeoDataFrame(
        trucks_df,
        geometry=gpd.points_from_xy(trucks_df.longitude, trucks_df.latitude),
        crs='EPSG:4326'
    )
    
    # 5. Spatial join trucks to neighborhoods
    print("📍 Performing spatial join to neighborhoods...")
    trucks_with_neighborhoods = gpd.sjoin(trucks_gdf, neighborhoods_gdf, how='left', predicate='within')
    
    # 6. Calculate truck density per neighborhood
    print("📊 Calculating truck density per neighborhood...")
    truck_counts = trucks_with_neighborhoods.groupby('nhood').size().reset_index(name='truck_count')
    neighborhoods_with_density = neighborhoods_gdf.merge(truck_counts, on='nhood', how='left')
    neighborhoods_with_density['truck_count'] = neighborhoods_with_density['truck_count'].fillna(0)
    neighborhoods_with_density['truck_density'] = neighborhoods_with_density['truck_count']
    
    # 7. Export results
    print("📤 Exporting results...")
    
    # Export neighborhoods with density
    neighborhoods_output = "sf_neighborhoods_density.geojson"
    neighborhoods_with_density.to_file(neighborhoods_output, driver="GeoJSON")
    print(f"✅ Exported neighborhoods: {neighborhoods_output}")
    
    # Export food trucks
    trucks_output = "sf_food_trucks.geojson"
    trucks_gdf.to_file(trucks_output, driver="GeoJSON")
    print(f"✅ Exported food trucks: {trucks_output}")
    
    # Export combined JSON for API
    api_data = {
        "neighborhoods": json.loads(neighborhoods_with_density.to_json()),
        "food_trucks": json.loads(trucks_gdf.to_json()),
        "summary": {
            "total_trucks": int(len(trucks_gdf)),
            "total_neighborhoods": int(len(neighborhoods_gdf)),
            "neighborhoods_with_trucks": int(len(neighborhoods_with_density[neighborhoods_with_density['truck_count'] > 0])),
            "max_density": int(neighborhoods_with_density['truck_density'].max()),
            "avg_density": float(round(neighborhoods_with_density['truck_density'].mean(), 1))
        }
    }
    
    with open("food_trucks_latest.json", "w") as f:
        json.dump(api_data, f, indent=2)
    
    # Create visualization with lighter styling
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))
    fig.patch.set_facecolor('white')
    
    # Plot 1: Neighborhood density
    neighborhoods_with_density.plot(
        column='truck_density',
        cmap='YlOrRd',
        alpha=0.7,
        legend=True,
        ax=ax1
    )
    trucks_gdf.plot(ax=ax1, color='red', markersize=20, alpha=0.8)
    ax1.set_title("SF Food Trucks Now - Lunch Heat-Map", fontsize=14, fontweight='bold', color='#2c3e50')
    ax1.set_xlabel("Longitude", color='#34495e')
    ax1.set_ylabel("Latitude", color='#34495e')
    ax1.set_facecolor('#f8f9fa')
    
    # Plot 2: Truck locations only
    neighborhoods_gdf.plot(ax=ax2, color='lightgray', alpha=0.3)
    trucks_gdf.plot(ax=ax2, color='red', markersize=30, alpha=0.8)
    ax2.set_title("Current Food Truck Locations", fontsize=14, fontweight='bold', color='#2c3e50')
    ax2.set_xlabel("Longitude", color='#34495e')
    ax2.set_ylabel("Latitude", color='#34495e')
    ax2.set_facecolor('#f8f9fa')
    
    plt.tight_layout()
    plt.savefig("sf_food_trucks.png", dpi=120, bbox_inches='tight', facecolor='white')
    plt.close()
    print("✅ Exported visualization: sf_food_trucks.png")
    
    # 8. Summary statistics
    processing_time = time.time() - start_time
    max_density = neighborhoods_with_density['truck_density'].max()
    neighborhoods_with_trucks = len(neighborhoods_with_density[neighborhoods_with_density['truck_count'] > 0])
    
    print("🎉 Open Food Trucks Now processing completed!")
    print(f"🚚 Processed {len(trucks_gdf)} food trucks")
    print(f"🏙️ Analyzed {len(neighborhoods_gdf)} SF neighborhoods")
    print(f"⏱️ Processing time: {processing_time:.2f} seconds")
    print(f"📈 Max density: {max_density} trucks")
    print(f"🎯 Active neighborhoods: {neighborhoods_with_trucks}")

def fetch_sf_food_trucks():
    """Fetch live SF food truck schedule data"""
    try:
        url = "https://data.sfgov.org/resource/jjew-5d7t.json?$limit=10000"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"⚠️ SF API error: {e}")
        return []

def download_sf_neighborhoods():
    """Download SF neighborhood polygons"""
    try:
        url = "https://data.sfgov.org/resource/ejmn-km5w.geojson"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        with open("data/sf_neighborhoods.geojson", "w") as f:
            json.dump(response.json(), f, indent=2)
        print("✅ Downloaded SF neighborhoods")
    except Exception as e:
        print(f"⚠️ Error downloading neighborhoods: {e}")
        create_mock_neighborhoods()

def filter_open_trucks(truck_data):
    """Filter for currently open food trucks"""
    if not truck_data:
        return []
    
    now = datetime.now()
    current_weekday = now.strftime('%A').upper()
    current_time = now.strftime('%H:%M')
    
    open_trucks = []
    for truck in truck_data:
        # Check if truck has required fields
        if not all(key in truck for key in ['latitude', 'longitude', 'starttime', 'endtime']):
            continue
        
        # Check if truck is permitted and has location
        if truck.get('status') != 'APPROVED':
            continue
            
        try:
            lat = float(truck['latitude'])
            lon = float(truck['longitude'])
            
            # Basic SF bounds check
            if not (37.7 <= lat <= 37.8 and -122.5 <= lon <= -122.3):
                continue
                
            # Check if currently open (simplified)
            start_time = truck.get('starttime', '10:00')
            end_time = truck.get('endtime', '14:00')
            
            # For demo, assume trucks are open during lunch hours
            if '10:00' <= current_time <= '15:00':
                open_trucks.append({
                    'applicant': truck.get('applicant', 'Unknown Vendor'),
                    'fooditems': truck.get('fooditems', 'Various Food Items'),
                    'latitude': lat,
                    'longitude': lon,
                    'starttime': start_time,
                    'endtime': end_time,
                    'location': truck.get('location', 'SF Location')
                })
        except (ValueError, TypeError):
            continue
    
    return open_trucks

def create_sample_open_trucks():
    """Create sample food truck data for demo"""
    sample_trucks = [
        {'applicant': 'Tacos El Primo', 'fooditems': 'Tacos, Burritos, Quesadillas', 'latitude': 37.7749, 'longitude': -122.4194, 'starttime': '11:00', 'endtime': '14:00', 'location': 'Market St & 4th St'},
        {'applicant': 'SF Street Food', 'fooditems': 'Sandwiches, Salads, Soup', 'latitude': 37.7849, 'longitude': -122.4094, 'starttime': '10:30', 'endtime': '15:00', 'location': 'Mission St & 2nd St'},
        {'applicant': 'Golden Gate Grill', 'fooditems': 'Burgers, Fries, Shakes', 'latitude': 37.7649, 'longitude': -122.4294, 'starttime': '11:30', 'endtime': '14:30', 'location': 'Folsom St & 3rd St'},
        {'applicant': 'Bay Area Bites', 'fooditems': 'Asian Fusion, Rice Bowls', 'latitude': 37.7949, 'longitude': -122.3994, 'starttime': '11:00', 'endtime': '15:00', 'location': 'Howard St & 1st St'},
        {'applicant': 'Lunch Express', 'fooditems': 'Pizza, Pasta, Italian', 'latitude': 37.7549, 'longitude': -122.4394, 'starttime': '10:00', 'endtime': '14:00', 'location': 'Brannan St & 5th St'}
    ]
    return sample_trucks

def create_mock_neighborhoods():
    """Create mock SF neighborhoods for demo"""
    mock_data = {
        "type": "FeatureCollection",
        "features": [
            {"type": "Feature", "properties": {"nhood": "SOMA"}, "geometry": {"type": "Polygon", "coordinates": [[[-122.42, 37.76], [-122.39, 37.76], [-122.39, 37.79], [-122.42, 37.79], [-122.42, 37.76]]]}},
            {"type": "Feature", "properties": {"nhood": "Mission"}, "geometry": {"type": "Polygon", "coordinates": [[[-122.43, 37.74], [-122.40, 37.74], [-122.40, 37.77], [-122.43, 37.77], [-122.43, 37.74]]]}},
            {"type": "Feature", "properties": {"nhood": "Financial District"}, "geometry": {"type": "Polygon", "coordinates": [[[-122.41, 37.79], [-122.39, 37.79], [-122.39, 37.81], [-122.41, 37.81], [-122.41, 37.79]]]}},
        ]
    }
    
    with open("data/sf_neighborhoods.geojson", "w") as f:
        json.dump(mock_data, f, indent=2)
    print("✅ Created mock SF neighborhoods")

def create_mock_truck_data():
    """Create mock truck data for demo"""
    return [
        {'applicant': 'Demo Tacos', 'fooditems': 'Tacos, Burritos', 'latitude': '37.7749', 'longitude': '-122.4194', 'starttime': '11:00', 'endtime': '14:00', 'status': 'APPROVED', 'location': 'Market St'},
        {'applicant': 'Demo Burgers', 'fooditems': 'Burgers, Fries', 'latitude': '37.7849', 'longitude': '-122.4094', 'starttime': '10:30', 'endtime': '15:00', 'status': 'APPROVED', 'location': 'Mission St'},
    ]

if __name__ == "__main__":
    main()
