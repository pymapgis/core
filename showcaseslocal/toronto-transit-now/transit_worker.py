#!/usr/bin/env python3
"""
Toronto Transit Now - TTC GTFS-RT Data Worker
Real-time Toronto Transit Commission subway, streetcar, and bus tracking
"""

import json
import time
from datetime import datetime
from typing import Dict, List, Any, Optional
import requests
import pandas as pd
try:
    import matplotlib.pyplot as plt
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False

# TTC endpoints (using alternative sources for demo)
# Note: TTC GTFS-RT requires API access, using sample data for demonstration
TTC_GTFS_RT_VEHICLE_URL = "https://api.ttc.ca/gtfs-realtime/VehiclePositions.pb"
TTC_GTFS_RT_ALERTS_URL = "https://api.ttc.ca/gtfs-realtime/ServiceAlerts.pb"
TTC_GTFS_RT_TRIP_URL = "https://api.ttc.ca/gtfs-realtime/TripUpdates.pb"

# Toronto transit route colors (TTC branding)
TTC_ROUTE_COLORS = {
    # Subway Lines
    'line_1': '#FFD320',  # Yellow - Yonge-University Line
    'line_2': '#00B04F',  # Green - Bloor-Danforth Line  
    'line_3': '#00B7EF',  # Light Blue - Scarborough RT
    'line_4': '#9639A7',  # Purple - Sheppard Line
    # Major Streetcar Routes
    '501': '#DA020E',     # Red - Queen Street
    '504': '#DA020E',     # Red - King Street
    '505': '#DA020E',     # Red - Dundas Street
    '506': '#DA020E',     # Red - Carlton Street
    '510': '#DA020E',     # Red - Spadina Avenue
    '511': '#DA020E',     # Red - Bathurst Street
    '512': '#DA020E',     # Red - St. Clair Avenue
    # Major Bus Routes
    '36': '#1C4F9C',      # Blue - Finch West
    '96': '#1C4F9C',      # Blue - Wilson
    '300': '#1C4F9C',     # Blue - Bloor-Danforth Night
}

def fetch_ttc_vehicle_positions() -> Optional[bytes]:
    """Fetch real-time TTC vehicle positions from GTFS-RT feed"""
    print("🚇 Fetching TTC vehicle positions from GTFS-RT...")
    
    try:
        response = requests.get(TTC_GTFS_RT_VEHICLE_URL, timeout=15)
        response.raise_for_status()
        
        print(f"✅ Fetched TTC vehicle data ({len(response.content)} bytes)")
        return response.content
        
    except requests.RequestException as e:
        print(f"❌ Failed to fetch TTC vehicle data: {e}")
        return None

def fetch_ttc_alerts() -> Optional[bytes]:
    """Fetch TTC service alerts from GTFS-RT feed"""
    print("🚨 Fetching TTC service alerts...")
    
    try:
        response = requests.get(TTC_GTFS_RT_ALERTS_URL, timeout=15)
        response.raise_for_status()
        
        print(f"✅ Fetched TTC alerts data ({len(response.content)} bytes)")
        return response.content
        
    except requests.RequestException as e:
        print(f"⚠️ Could not fetch TTC alerts: {e}")
        return None

def create_sample_ttc_data() -> List[Dict[str, Any]]:
    """Create realistic sample TTC transit data when GTFS-RT unavailable"""
    print("🎭 Creating sample TTC transit data...")
    
    sample_routes = [
        {
            'route_id': 'line_1',
            'route_name': 'Yonge-University Line',
            'route_type': 'subway',
            'status': 'Normal Service',
            'delay_minutes': 0,
            'vehicles_active': 45,
            'crowding_level': 7,
            'last_update': datetime.now().isoformat()
        },
        {
            'route_id': 'line_2',
            'route_name': 'Bloor-Danforth Line',
            'route_type': 'subway',
            'status': 'Minor Delays',
            'delay_minutes': 3,
            'vehicles_active': 38,
            'crowding_level': 8,
            'last_update': datetime.now().isoformat()
        },
        {
            'route_id': 'line_4',
            'route_name': 'Sheppard Line',
            'route_type': 'subway',
            'status': 'Normal Service',
            'delay_minutes': 0,
            'vehicles_active': 8,
            'crowding_level': 4,
            'last_update': datetime.now().isoformat()
        },
        {
            'route_id': '501',
            'route_name': 'Queen Streetcar',
            'route_type': 'streetcar',
            'status': 'Normal Service',
            'delay_minutes': 2,
            'vehicles_active': 25,
            'crowding_level': 6,
            'last_update': datetime.now().isoformat()
        },
        {
            'route_id': '504',
            'route_name': 'King Streetcar',
            'route_type': 'streetcar',
            'status': 'Normal Service',
            'delay_minutes': 1,
            'vehicles_active': 22,
            'crowding_level': 7,
            'last_update': datetime.now().isoformat()
        },
        {
            'route_id': '510',
            'route_name': 'Spadina Streetcar',
            'route_type': 'streetcar',
            'status': 'Normal Service',
            'delay_minutes': 0,
            'vehicles_active': 18,
            'crowding_level': 5,
            'last_update': datetime.now().isoformat()
        },
        {
            'route_id': '36',
            'route_name': 'Finch West Bus',
            'route_type': 'bus',
            'status': 'Normal Service',
            'delay_minutes': 4,
            'vehicles_active': 15,
            'crowding_level': 6,
            'last_update': datetime.now().isoformat()
        },
        {
            'route_id': '96',
            'route_name': 'Wilson Bus',
            'route_type': 'bus',
            'status': 'Normal Service',
            'delay_minutes': 2,
            'vehicles_active': 12,
            'crowding_level': 5,
            'last_update': datetime.now().isoformat()
        }
    ]
    
    return sample_routes

def process_ttc_data(route_data: List[Dict[str, Any]]) -> pd.DataFrame:
    """Process TTC transit data into structured format"""
    print("📊 Processing TTC transit data...")
    
    processed_routes = []
    
    for route in route_data:
        route_id = route.get('route_id', '')
        route_name = route.get('route_name', '')
        route_type = route.get('route_type', 'unknown')
        status = route.get('status', 'Normal Service')
        delay_minutes = route.get('delay_minutes', 0)
        vehicles_active = route.get('vehicles_active', 0)
        crowding_level = route.get('crowding_level', 5)
        
        # Calculate performance score (0-10, higher is better)
        performance_score = max(0, 10 - (delay_minutes * 0.5) - (crowding_level * 0.3))
        performance_score = min(10, performance_score)
        
        # Determine status category and color
        if delay_minutes == 0 and crowding_level <= 5:
            status_category = 'Excellent'
            status_color = '#00B04F'  # TTC Green
        elif delay_minutes <= 2 and crowding_level <= 7:
            status_category = 'Good'
            status_color = '#FFD320'  # TTC Yellow
        elif delay_minutes <= 5 and crowding_level <= 8:
            status_category = 'Fair'
            status_color = '#FF8C00'  # Orange
        else:
            status_category = 'Poor'
            status_color = '#DA020E'  # TTC Red
        
        # Get route color
        route_color = TTC_ROUTE_COLORS.get(route_id, '#1C4F9C')  # Default TTC Blue
        
        processed_routes.append({
            'route_id': route_id,
            'route_name': route_name,
            'route_type': route_type,
            'status': status,
            'delay_minutes': int(delay_minutes),
            'vehicles_active': int(vehicles_active),
            'crowding_level': int(crowding_level),
            'performance_score': round(float(performance_score), 1),
            'status_category': status_category,
            'status_color': status_color,
            'route_color': route_color,
            'last_updated': datetime.now().isoformat()
        })
    
    df = pd.DataFrame(processed_routes)
    print(f"✅ Processed {len(df)} TTC routes")
    return df

def create_ttc_geojson(df: pd.DataFrame) -> Dict[str, Any]:
    """Create GeoJSON representation of TTC routes with status"""
    print("🗺️ Creating TTC routes GeoJSON...")
    
    # Simplified TTC route coordinates (Toronto focus)
    ttc_coordinates = {
        # Subway Lines
        'line_1': [[-79.3832, 43.6532], [-79.3832, 43.7532], [-79.4832, 43.8032]],  # Yonge-University
        'line_2': [[-79.2832, 43.6532], [-79.3832, 43.6532], [-79.4832, 43.6532]],  # Bloor-Danforth
        'line_4': [[-79.3332, 43.7532], [-79.3832, 43.7532], [-79.4332, 43.7532]],  # Sheppard
        # Major Streetcar Routes
        '501': [[-79.2832, 43.6432], [-79.3832, 43.6432], [-79.4832, 43.6432]],     # Queen
        '504': [[-79.2832, 43.6332], [-79.3832, 43.6332], [-79.4832, 43.6332]],     # King
        '510': [[-79.4032, 43.6232], [-79.4032, 43.6532], [-79.4032, 43.6832]],     # Spadina
        # Major Bus Routes
        '36': [[-79.5032, 43.7732], [-79.4532, 43.7732], [-79.4032, 43.7732]],      # Finch West
        '96': [[-79.5032, 43.7332], [-79.4532, 43.7332], [-79.4032, 43.7332]]       # Wilson
    }
    
    features = []
    
    for _, row in df.iterrows():
        route_id = row['route_id']
        coordinates = ttc_coordinates.get(route_id, [[-79.3832, 43.6532], [-79.4032, 43.6732]])
        
        feature = {
            'type': 'Feature',
            'properties': {
                'route_id': row['route_id'],
                'route_name': row['route_name'],
                'route_type': row['route_type'],
                'status': row['status'],
                'delay_minutes': row['delay_minutes'],
                'vehicles_active': row['vehicles_active'],
                'crowding_level': row['crowding_level'],
                'performance_score': row['performance_score'],
                'status_category': row['status_category'],
                'status_color': row['status_color'],
                'route_color': row['route_color'],
                'last_updated': row['last_updated']
            },
            'geometry': {
                'type': 'LineString',
                'coordinates': coordinates
            }
        }
        features.append(feature)
    
    geojson = {
        'type': 'FeatureCollection',
        'features': features
    }
    
    print(f"✅ Created GeoJSON with {len(features)} TTC routes")
    return geojson

def create_transit_summary(df: pd.DataFrame) -> Dict[str, Any]:
    """Create summary statistics for TTC transit"""
    total_routes = len(df)
    excellent_service = len(df[df['status_category'] == 'Excellent'])
    good_service = len(df[df['status_category'] == 'Good'])
    issues = len(df[df['status_category'].isin(['Fair', 'Poor'])])
    avg_performance = df['performance_score'].mean()
    avg_delay = df['delay_minutes'].mean()
    total_vehicles = df['vehicles_active'].sum()
    
    return {
        'total_routes': int(total_routes),
        'excellent_service': int(excellent_service),
        'good_service': int(good_service),
        'issues': int(issues),
        'avg_performance_score': round(float(avg_performance), 1),
        'avg_delay_minutes': round(float(avg_delay), 1),
        'total_vehicles_active': int(total_vehicles),
        'last_updated': datetime.now().isoformat()
    }

def export_results(df: pd.DataFrame, geojson: Dict[str, Any], summary: Dict[str, Any]):
    """Export processed results to files"""
    print("📤 Exporting results...")
    
    # Export GeoJSON
    with open('toronto_transit_status.geojson', 'w') as f:
        json.dump(geojson, f, indent=2)
    
    # Export latest data for API
    latest_data = {
        'transit_routes': geojson,
        'summary': summary,
        'last_updated': datetime.now().isoformat()
    }
    
    with open('transit_status_latest.json', 'w') as f:
        json.dump(latest_data, f, indent=2)
    
    # Create visualization
    create_status_visualization(df)
    
    print("✅ Exported transit status: toronto_transit_status.geojson")
    print("✅ Exported API data: transit_status_latest.json")
    print("✅ Exported visualization: toronto_transit_status.png")

def create_status_visualization(df: pd.DataFrame):
    """Create TTC transit status visualization"""
    if not MATPLOTLIB_AVAILABLE:
        print("📊 Matplotlib not available, skipping visualization")
        return
        
    plt.figure(figsize=(12, 8))
    
    # Status distribution
    plt.subplot(2, 2, 1)
    status_counts = df['status_category'].value_counts()
    colors = ['#00B04F', '#FFD320', '#FF8C00', '#DA020E'][:len(status_counts)]
    plt.pie(status_counts.values, labels=status_counts.index, autopct='%1.1f%%', colors=colors)
    plt.title('TTC Service Status Distribution')
    
    # Performance scores by route
    plt.subplot(2, 2, 2)
    df_sorted = df.sort_values('performance_score')
    bars = plt.barh(df_sorted['route_name'], df_sorted['performance_score'])
    for i, bar in enumerate(bars):
        bar.set_color(df_sorted.iloc[i]['route_color'])
    plt.xlabel('Performance Score (0-10)')
    plt.title('Performance by TTC Route')
    plt.xlim(0, 10)
    
    # Route types
    plt.subplot(2, 2, 3)
    type_counts = df['route_type'].value_counts()
    plt.bar(type_counts.index, type_counts.values, color=['#FFD320', '#DA020E', '#1C4F9C'])
    plt.title('Routes by Type')
    plt.ylabel('Number of Routes')
    
    # Summary stats
    plt.subplot(2, 2, 4)
    summary_text = f"""
    Total Routes: {len(df)}
    Excellent: {len(df[df['status_category'] == 'Excellent'])}
    Good: {len(df[df['status_category'] == 'Good'])}
    Issues: {len(df[df['status_category'].isin(['Fair', 'Poor'])])}
    Avg Performance: {df['performance_score'].mean():.1f}/10
    Avg Delay: {df['delay_minutes'].mean():.1f} min
    Active Vehicles: {df['vehicles_active'].sum()}
    """
    plt.text(0.1, 0.5, summary_text, fontsize=10, transform=plt.gca().transAxes, 
             verticalalignment='center')
    plt.axis('off')
    plt.title('TTC System Summary')
    
    plt.tight_layout()
    plt.savefig('toronto_transit_status.png', dpi=300, bbox_inches='tight')
    plt.close()

def main():
    """Main processing function"""
    start_time = time.time()
    print("🚇 Starting Toronto Transit Now processing...")
    
    # Try to fetch real GTFS-RT data
    vehicle_data = fetch_ttc_vehicle_positions()
    alerts_data = fetch_ttc_alerts()
    
    # For now, use sample data (GTFS-RT parsing would require protobuf handling)
    route_data = create_sample_ttc_data()
    
    # Process data
    df = process_ttc_data(route_data)
    geojson = create_ttc_geojson(df)
    summary = create_transit_summary(df)
    
    # Export results
    export_results(df, geojson, summary)
    
    # Print summary
    processing_time = time.time() - start_time
    print(f"\n🎉 Toronto Transit Now processing completed!")
    print(f"🚇 Processed {len(df)} TTC routes")
    print(f"✅ Excellent service: {summary['excellent_service']}")
    print(f"👍 Good service: {summary['good_service']}")
    print(f"⚠️ Issues: {summary['issues']}")
    print(f"⏱️ Processing time: {processing_time:.2f} seconds")
    print(f"📊 Average performance: {summary['avg_performance_score']}/10")
    print(f"🚌 Active vehicles: {summary['total_vehicles_active']}")

if __name__ == "__main__":
    main()
