#!/usr/bin/env python3
"""
Flight Delay Now - Real-time airport delay analysis
A 35-line microservice that turns FAA OIS delay data into live airport congestion maps
"""

import json
import math
import time
import requests
import pandas as pd
import geopandas as gpd
from pathlib import Path
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings('ignore')

def main():
    print("✈️ Starting Flight Delay Now processing...")
    start_time = time.time()
    
    # 1. Fetch FAA OIS current delay data
    print("🌐 Fetching flight delay data from FAA OIS...")
    try:
        ois_response = requests.get("https://www.fly.faa.gov/ois/OIS_current.json", timeout=10)
        ois_response.raise_for_status()
        ois_data = ois_response.json()
        print(f"✅ Fetched OIS data: {len(ois_data)} airports")
    except Exception as e:
        print(f"⚠️ Error fetching OIS data: {e}")
        print("🎭 Creating mock flight delay data for demo...")
        ois_data = create_mock_delay_data()
    
    # 2. Load airport locations
    print("📍 Loading airport data from data/top_airports.geojson")
    airports_path = Path("data/top_airports.geojson")
    if not airports_path.exists():
        print("📝 Creating top airports GeoJSON...")
        create_top_airports_geojson()
    
    airports_gdf = gpd.read_file(airports_path)
    print(f"✅ Loaded {len(airports_gdf)} airport locations")
    
    # 3. Process and normalize OIS data
    ois_df = pd.DataFrame(ois_data)
    if 'iata' not in ois_df.columns and len(ois_data) > 0:
        # Handle different OIS data formats
        ois_df = normalize_ois_data(ois_data)
    
    # 4. Merge airport locations with delay data
    merged_gdf = airports_gdf.merge(ois_df, on='iata', how='left')
    
    # 5. Clean and standardize data
    merged_gdf['avg_delay'] = merged_gdf.get('avg_delay', merged_gdf.get('delay_minutes', 0)).fillna(0)
    merged_gdf['flights_total'] = merged_gdf.get('flights_total', merged_gdf.get('total_flights', 20)).fillna(20)
    merged_gdf['status'] = merged_gdf.get('status', 'Normal').fillna('Normal')
    
    # 6. Calculate delay score: log1p(avg_delay) × flights_affected
    merged_gdf['delay_score'] = merged_gdf.apply(
        lambda row: math.log1p(max(0, row['avg_delay'])) * max(1, row['flights_total']), axis=1
    )
    
    # 7. Export results
    print("📤 Exporting results...")
    
    # Export GeoJSON
    output_geojson = "flight_impact.geojson"
    merged_gdf.to_file(output_geojson, driver="GeoJSON")
    print(f"✅ Exported GeoJSON: {output_geojson}")
    
    # Export JSON for API
    api_data = {
        "type": "FeatureCollection",
        "features": json.loads(merged_gdf.to_json())["features"]
    }
    
    with open("flight_latest.json", "w") as f:
        json.dump(api_data, f, indent=2)
    
    # Create visualization
    fig, ax = plt.subplots(1, 1, figsize=(12, 8))
    merged_gdf.plot(
        column='delay_score',
        cmap='RdYlGn_r',
        markersize=merged_gdf['flights_total'] * 2,
        alpha=0.7,
        ax=ax,
        legend=True
    )
    ax.set_title("Flight Delay Now - Airport Congestion Analysis", fontsize=16, fontweight='bold')
    ax.set_xlabel("Longitude")
    ax.set_ylabel("Latitude")
    plt.tight_layout()
    plt.savefig("flight_impact.png", dpi=120, bbox_inches='tight')
    plt.close()
    print("✅ Exported visualization: flight_impact.png")
    
    # 8. Summary statistics
    processing_time = time.time() - start_time
    avg_delay = merged_gdf['avg_delay'].mean()
    max_delay = merged_gdf['avg_delay'].max()
    total_airports = len(merged_gdf)
    
    print("🎉 Flight Delay Now processing completed!")
    print(f"📊 Processed {total_airports} airports")
    print(f"⏱️ Processing time: {processing_time:.2f} seconds")
    print(f"📈 Average delay: {avg_delay:.1f} minutes")
    print(f"🔴 Maximum delay: {max_delay:.1f} minutes")

def normalize_ois_data(ois_data):
    """Normalize different OIS data formats"""
    normalized = []
    for item in ois_data:
        if isinstance(item, dict):
            # Extract IATA code and delay info
            iata = item.get('iata', item.get('airport', item.get('code', '')))
            delay = item.get('delay', item.get('avg_delay', item.get('departure_delay', 0)))
            flights = item.get('flights', item.get('total_flights', item.get('departures', 20)))
            status = item.get('status', 'Normal')
            
            normalized.append({
                'iata': iata,
                'avg_delay': delay,
                'flights_total': flights,
                'status': status
            })
    
    return pd.DataFrame(normalized)

def create_mock_delay_data():
    """Create realistic mock delay data for demo purposes"""
    import random
    
    # Top 35 US airports with realistic delay patterns
    airports = [
        'ATL', 'LAX', 'ORD', 'DFW', 'DEN', 'JFK', 'SFO', 'SEA', 'LAS', 'MCO',
        'EWR', 'CLT', 'PHX', 'IAH', 'MIA', 'BOS', 'MSP', 'FLL', 'DTW', 'PHL',
        'LGA', 'BWI', 'SLC', 'IAD', 'DCA', 'MDW', 'TPA', 'PDX', 'STL', 'HNL',
        'AUS', 'MSY', 'RDU', 'SAN', 'RSW'
    ]
    
    mock_data = []
    for iata in airports:
        # Simulate realistic delay patterns
        base_delay = random.uniform(0, 45)  # 0-45 minute delays
        if iata in ['JFK', 'LGA', 'EWR', 'ORD']:  # Busy airports tend to have more delays
            base_delay += random.uniform(10, 30)
        
        mock_data.append({
            'iata': iata,
            'avg_delay': round(base_delay, 1),
            'flights_total': random.randint(15, 150),
            'status': 'Normal' if base_delay < 30 else 'Delayed' if base_delay < 60 else 'Severe'
        })
    
    return mock_data

def create_top_airports_geojson():
    """Create GeoJSON file with top 35 US airports"""
    # Top 35 US airports with coordinates
    airports_data = {
        "type": "FeatureCollection",
        "features": [
            {"type": "Feature", "properties": {"iata": "ATL", "name": "Hartsfield-Jackson Atlanta", "city": "Atlanta", "state": "GA", "runways": 5}, "geometry": {"type": "Point", "coordinates": [-84.4281, 33.6367]}},
            {"type": "Feature", "properties": {"iata": "LAX", "name": "Los Angeles International", "city": "Los Angeles", "state": "CA", "runways": 4}, "geometry": {"type": "Point", "coordinates": [-118.4081, 33.9425]}},
            {"type": "Feature", "properties": {"iata": "ORD", "name": "O'Hare International", "city": "Chicago", "state": "IL", "runways": 8}, "geometry": {"type": "Point", "coordinates": [-87.9048, 41.9786]}},
            {"type": "Feature", "properties": {"iata": "DFW", "name": "Dallas/Fort Worth International", "city": "Dallas", "state": "TX", "runways": 7}, "geometry": {"type": "Point", "coordinates": [-97.0372, 32.8968]}},
            {"type": "Feature", "properties": {"iata": "DEN", "name": "Denver International", "city": "Denver", "state": "CO", "runways": 6}, "geometry": {"type": "Point", "coordinates": [-104.6737, 39.8561]}},
            {"type": "Feature", "properties": {"iata": "JFK", "name": "John F. Kennedy International", "city": "New York", "state": "NY", "runways": 4}, "geometry": {"type": "Point", "coordinates": [-73.7781, 40.6413]}},
            {"type": "Feature", "properties": {"iata": "SFO", "name": "San Francisco International", "city": "San Francisco", "state": "CA", "runways": 4}, "geometry": {"type": "Point", "coordinates": [-122.3748, 37.6213]}},
            {"type": "Feature", "properties": {"iata": "SEA", "name": "Seattle-Tacoma International", "city": "Seattle", "state": "WA", "runways": 3}, "geometry": {"type": "Point", "coordinates": [-122.3088, 47.4502]}},
            {"type": "Feature", "properties": {"iata": "LAS", "name": "McCarran International", "city": "Las Vegas", "state": "NV", "runways": 4}, "geometry": {"type": "Point", "coordinates": [-115.1522, 36.0840]}},
            {"type": "Feature", "properties": {"iata": "MCO", "name": "Orlando International", "city": "Orlando", "state": "FL", "runways": 4}, "geometry": {"type": "Point", "coordinates": [-81.3081, 28.4312]}},
            {"type": "Feature", "properties": {"iata": "EWR", "name": "Newark Liberty International", "city": "Newark", "state": "NJ", "runways": 3}, "geometry": {"type": "Point", "coordinates": [-74.1745, 40.6895]}},
            {"type": "Feature", "properties": {"iata": "CLT", "name": "Charlotte Douglas International", "city": "Charlotte", "state": "NC", "runways": 4}, "geometry": {"type": "Point", "coordinates": [-80.9431, 35.2144]}},
            {"type": "Feature", "properties": {"iata": "PHX", "name": "Phoenix Sky Harbor International", "city": "Phoenix", "state": "AZ", "runways": 3}, "geometry": {"type": "Point", "coordinates": [-112.0158, 33.4342]}},
            {"type": "Feature", "properties": {"iata": "IAH", "name": "George Bush Intercontinental", "city": "Houston", "state": "TX", "runways": 5}, "geometry": {"type": "Point", "coordinates": [-95.3414, 29.9902]}},
            {"type": "Feature", "properties": {"iata": "MIA", "name": "Miami International", "city": "Miami", "state": "FL", "runways": 4}, "geometry": {"type": "Point", "coordinates": [-80.2906, 25.7959]}},
            {"type": "Feature", "properties": {"iata": "BOS", "name": "Logan International", "city": "Boston", "state": "MA", "runways": 6}, "geometry": {"type": "Point", "coordinates": [-71.0096, 42.3656]}},
            {"type": "Feature", "properties": {"iata": "MSP", "name": "Minneapolis-St. Paul International", "city": "Minneapolis", "state": "MN", "runways": 4}, "geometry": {"type": "Point", "coordinates": [-93.2218, 44.8848]}},
            {"type": "Feature", "properties": {"iata": "FLL", "name": "Fort Lauderdale-Hollywood International", "city": "Fort Lauderdale", "state": "FL", "runways": 2}, "geometry": {"type": "Point", "coordinates": [-80.1506, 26.0742]}},
            {"type": "Feature", "properties": {"iata": "DTW", "name": "Detroit Metropolitan Wayne County", "city": "Detroit", "state": "MI", "runways": 6}, "geometry": {"type": "Point", "coordinates": [-83.3534, 42.2162]}},
            {"type": "Feature", "properties": {"iata": "PHL", "name": "Philadelphia International", "city": "Philadelphia", "state": "PA", "runways": 4}, "geometry": {"type": "Point", "coordinates": [-75.2424, 39.8744]}},
            {"type": "Feature", "properties": {"iata": "LGA", "name": "LaGuardia Airport", "city": "New York", "state": "NY", "runways": 2}, "geometry": {"type": "Point", "coordinates": [-73.8740, 40.7769]}},
            {"type": "Feature", "properties": {"iata": "BWI", "name": "Baltimore/Washington International", "city": "Baltimore", "state": "MD", "runways": 4}, "geometry": {"type": "Point", "coordinates": [-76.6692, 39.1774]}},
            {"type": "Feature", "properties": {"iata": "SLC", "name": "Salt Lake City International", "city": "Salt Lake City", "state": "UT", "runways": 4}, "geometry": {"type": "Point", "coordinates": [-111.9778, 40.7899]}},
            {"type": "Feature", "properties": {"iata": "IAD", "name": "Washington Dulles International", "city": "Washington", "state": "VA", "runways": 4}, "geometry": {"type": "Point", "coordinates": [-77.4565, 38.9531]}},
            {"type": "Feature", "properties": {"iata": "DCA", "name": "Ronald Reagan Washington National", "city": "Washington", "state": "DC", "runways": 3}, "geometry": {"type": "Point", "coordinates": [-77.0379, 38.8521]}},
            {"type": "Feature", "properties": {"iata": "MDW", "name": "Midway International", "city": "Chicago", "state": "IL", "runways": 5}, "geometry": {"type": "Point", "coordinates": [-87.7524, 41.7868]}},
            {"type": "Feature", "properties": {"iata": "TPA", "name": "Tampa International", "city": "Tampa", "state": "FL", "runways": 3}, "geometry": {"type": "Point", "coordinates": [-82.5332, 27.9755]}},
            {"type": "Feature", "properties": {"iata": "PDX", "name": "Portland International", "city": "Portland", "state": "OR", "runways": 3}, "geometry": {"type": "Point", "coordinates": [-122.5951, 45.5898]}},
            {"type": "Feature", "properties": {"iata": "STL", "name": "Lambert-St. Louis International", "city": "St. Louis", "state": "MO", "runways": 4}, "geometry": {"type": "Point", "coordinates": [-90.3700, 38.7487]}},
            {"type": "Feature", "properties": {"iata": "HNL", "name": "Honolulu International", "city": "Honolulu", "state": "HI", "runways": 4}, "geometry": {"type": "Point", "coordinates": [-157.9248, 21.3099]}},
            {"type": "Feature", "properties": {"iata": "AUS", "name": "Austin-Bergstrom International", "city": "Austin", "state": "TX", "runways": 2}, "geometry": {"type": "Point", "coordinates": [-97.6664, 30.1975]}},
            {"type": "Feature", "properties": {"iata": "MSY", "name": "Louis Armstrong New Orleans International", "city": "New Orleans", "state": "LA", "runways": 3}, "geometry": {"type": "Point", "coordinates": [-90.2580, 29.9934]}},
            {"type": "Feature", "properties": {"iata": "RDU", "name": "Raleigh-Durham International", "city": "Raleigh", "state": "NC", "runways": 3}, "geometry": {"type": "Point", "coordinates": [-78.7875, 35.8776]}},
            {"type": "Feature", "properties": {"iata": "SAN", "name": "San Diego International", "city": "San Diego", "state": "CA", "runways": 1}, "geometry": {"type": "Point", "coordinates": [-117.1933, 32.7338]}},
            {"type": "Feature", "properties": {"iata": "RSW", "name": "Southwest Florida International", "city": "Fort Myers", "state": "FL", "runways": 3}, "geometry": {"type": "Point", "coordinates": [-81.7552, 26.5362]}}
        ]
    }
    
    with open("data/top_airports.geojson", "w") as f:
        json.dump(airports_data, f, indent=2)
    
    print("✅ Created top_airports.geojson with 35 major US airports")

if __name__ == "__main__":
    main()
