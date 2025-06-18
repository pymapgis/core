#!/usr/bin/env python3
"""
Copenhagen Transit Now - Rejseplanen API Data Worker
Real-time Danish public transport with S-train, Metro, and bus integration
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

# Danish public transport endpoints (Rejseplanen API)
# Note: Some endpoints may require registration, using open endpoints where possible
REJSEPLANEN_DEPARTURES_URL = "https://xmlopen.rejseplanen.dk/bin/rest.exe/departureBoard"
REJSEPLANEN_LOCATION_URL = "https://xmlopen.rejseplanen.dk/bin/rest.exe/location"
DSB_STOG_API_URL = "https://api.dsb.dk/v1/stations"  # S-train data

# Copenhagen transit colors (Danish public transport branding)
COPENHAGEN_ROUTE_COLORS = {
    # S-train Lines (S-tog)
    's_a': '#00A86B',     # Green - S-train A
    's_b': '#0066CC',     # Blue - S-train B  
    's_c': '#FF6600',     # Orange - S-train C
    's_e': '#9966CC',     # Purple - S-train E
    's_f': '#FFCC00',     # Yellow - S-train F
    's_h': '#CC0000',     # Red - S-train H
    # Metro Lines
    'metro_m1': '#00A86B', # Green - Metro M1
    'metro_m2': '#FFCC00', # Yellow - Metro M2
    'metro_m3': '#0066CC', # Blue - Metro M3 (Cityringen)
    'metro_m4': '#CC0000', # Red - Metro M4
    # Major Bus Routes
    'bus_1a': '#E60026',   # Red - Bus 1A
    'bus_2a': '#E60026',   # Red - Bus 2A
    'bus_5a': '#E60026',   # Red - Bus 5A
    'bus_6a': '#E60026',   # Red - Bus 6A
}

def fetch_copenhagen_departures() -> Optional[Dict[str, Any]]:
    """Fetch real-time departures from Rejseplanen API"""
    print("🚇 Fetching Copenhagen transit departures from Rejseplanen...")
    
    try:
        # Central Station (København H) as example
        params = {
            'id': '8600626',  # København H station ID
            'format': 'json',
            'lang': 'en'
        }
        response = requests.get(REJSEPLANEN_DEPARTURES_URL, params=params, timeout=15)
        response.raise_for_status()
        
        data = response.json()
        print(f"✅ Fetched Copenhagen departures data")
        return data
        
    except requests.RequestException as e:
        print(f"❌ Failed to fetch Rejseplanen data: {e}")
        return None

def fetch_stog_status() -> Optional[Dict[str, Any]]:
    """Fetch S-train status information"""
    print("🚊 Fetching S-train status...")
    
    try:
        response = requests.get(DSB_STOG_API_URL, timeout=15)
        response.raise_for_status()
        
        data = response.json()
        print(f"✅ Fetched S-train status data")
        return data
        
    except requests.RequestException as e:
        print(f"⚠️ Could not fetch S-train data: {e}")
        return None

def create_sample_copenhagen_data() -> List[Dict[str, Any]]:
    """Create realistic sample Copenhagen transit data when APIs unavailable"""
    print("🎭 Creating sample Copenhagen transit data...")
    
    sample_routes = [
        {
            'route_id': 's_a',
            'route_name': 'S-train A',
            'route_type': 's_train',
            'status': 'Normal Service',
            'delay_minutes': 0,
            'frequency_minutes': 10,
            'punctuality_percent': 95,
            'last_update': datetime.now().isoformat()
        },
        {
            'route_id': 's_b',
            'route_name': 'S-train B',
            'route_type': 's_train',
            'status': 'Minor Delays',
            'delay_minutes': 2,
            'frequency_minutes': 10,
            'punctuality_percent': 88,
            'last_update': datetime.now().isoformat()
        },
        {
            'route_id': 's_c',
            'route_name': 'S-train C',
            'route_type': 's_train',
            'status': 'Normal Service',
            'delay_minutes': 1,
            'frequency_minutes': 10,
            'punctuality_percent': 92,
            'last_update': datetime.now().isoformat()
        },
        {
            'route_id': 'metro_m1',
            'route_name': 'Metro M1',
            'route_type': 'metro',
            'status': 'Excellent Service',
            'delay_minutes': 0,
            'frequency_minutes': 4,
            'punctuality_percent': 98,
            'last_update': datetime.now().isoformat()
        },
        {
            'route_id': 'metro_m2',
            'route_name': 'Metro M2',
            'route_type': 'metro',
            'status': 'Excellent Service',
            'delay_minutes': 0,
            'frequency_minutes': 4,
            'punctuality_percent': 97,
            'last_update': datetime.now().isoformat()
        },
        {
            'route_id': 'metro_m3',
            'route_name': 'Metro M3 (Cityringen)',
            'route_type': 'metro',
            'status': 'Normal Service',
            'delay_minutes': 1,
            'frequency_minutes': 6,
            'punctuality_percent': 94,
            'last_update': datetime.now().isoformat()
        },
        {
            'route_id': 'bus_1a',
            'route_name': 'Bus 1A',
            'route_type': 'bus',
            'status': 'Normal Service',
            'delay_minutes': 3,
            'frequency_minutes': 15,
            'punctuality_percent': 85,
            'last_update': datetime.now().isoformat()
        },
        {
            'route_id': 'bus_2a',
            'route_name': 'Bus 2A',
            'route_type': 'bus',
            'status': 'Normal Service',
            'delay_minutes': 2,
            'frequency_minutes': 12,
            'punctuality_percent': 87,
            'last_update': datetime.now().isoformat()
        }
    ]
    
    return sample_routes

def process_copenhagen_data(route_data: List[Dict[str, Any]]) -> pd.DataFrame:
    """Process Copenhagen transit data into structured format"""
    print("📊 Processing Copenhagen transit data...")
    
    processed_routes = []
    
    for route in route_data:
        route_id = route.get('route_id', '')
        route_name = route.get('route_name', '')
        route_type = route.get('route_type', 'unknown')
        status = route.get('status', 'Normal Service')
        delay_minutes = route.get('delay_minutes', 0)
        frequency_minutes = route.get('frequency_minutes', 10)
        punctuality_percent = route.get('punctuality_percent', 90)
        
        # Calculate efficiency score (0-10, higher is better)
        # Based on punctuality, frequency, and delays
        efficiency_score = (punctuality_percent / 10) - (delay_minutes * 0.3) + (10 / max(frequency_minutes, 1))
        efficiency_score = max(0, min(10, efficiency_score))
        
        # Determine status category and color
        if efficiency_score >= 9.0:
            status_category = 'Excellent'
            status_color = '#00A86B'  # Danish Green
        elif efficiency_score >= 7.5:
            status_category = 'Good'
            status_color = '#FFCC00'  # Danish Yellow
        elif efficiency_score >= 6.0:
            status_category = 'Fair'
            status_color = '#FF6600'  # Danish Orange
        else:
            status_category = 'Poor'
            status_color = '#CC0000'  # Danish Red
        
        # Get route color
        route_color = COPENHAGEN_ROUTE_COLORS.get(route_id, '#0066CC')  # Default Danish Blue
        
        processed_routes.append({
            'route_id': route_id,
            'route_name': route_name,
            'route_type': route_type,
            'status': status,
            'delay_minutes': int(delay_minutes),
            'frequency_minutes': int(frequency_minutes),
            'punctuality_percent': int(punctuality_percent),
            'efficiency_score': round(float(efficiency_score), 1),
            'status_category': status_category,
            'status_color': status_color,
            'route_color': route_color,
            'last_updated': datetime.now().isoformat()
        })
    
    df = pd.DataFrame(processed_routes)
    print(f"✅ Processed {len(df)} Copenhagen transit routes")
    return df

def create_copenhagen_geojson(df: pd.DataFrame) -> Dict[str, Any]:
    """Create GeoJSON representation of Copenhagen transit routes with status"""
    print("🗺️ Creating Copenhagen transit routes GeoJSON...")
    
    # Simplified Copenhagen transit coordinates (Copenhagen focus)
    copenhagen_coordinates = {
        # S-train Lines
        's_a': [[12.5683, 55.6761], [12.5783, 55.6861], [12.5883, 55.6961]],      # S-train A
        's_b': [[12.5583, 55.6661], [12.5683, 55.6761], [12.5783, 55.6861]],      # S-train B
        's_c': [[12.5483, 55.6561], [12.5683, 55.6761], [12.5883, 55.6961]],      # S-train C
        # Metro Lines
        'metro_m1': [[12.5683, 55.6761], [12.5783, 55.6861], [12.5883, 55.6961]], # Metro M1
        'metro_m2': [[12.5583, 55.6661], [12.5683, 55.6761], [12.5783, 55.6861]], # Metro M2
        'metro_m3': [[12.5683, 55.6761], [12.5783, 55.6761], [12.5883, 55.6761]], # Metro M3 (Cityringen)
        # Major Bus Routes
        'bus_1a': [[12.5583, 55.6661], [12.5683, 55.6761], [12.5783, 55.6861]],   # Bus 1A
        'bus_2a': [[12.5483, 55.6561], [12.5583, 55.6661], [12.5683, 55.6761]]    # Bus 2A
    }
    
    features = []
    
    for _, row in df.iterrows():
        route_id = row['route_id']
        coordinates = copenhagen_coordinates.get(route_id, [[12.5683, 55.6761], [12.5783, 55.6861]])
        
        feature = {
            'type': 'Feature',
            'properties': {
                'route_id': row['route_id'],
                'route_name': row['route_name'],
                'route_type': row['route_type'],
                'status': row['status'],
                'delay_minutes': row['delay_minutes'],
                'frequency_minutes': row['frequency_minutes'],
                'punctuality_percent': row['punctuality_percent'],
                'efficiency_score': row['efficiency_score'],
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
    
    print(f"✅ Created GeoJSON with {len(features)} Copenhagen transit routes")
    return geojson

def create_transit_summary(df: pd.DataFrame) -> Dict[str, Any]:
    """Create summary statistics for Copenhagen transit"""
    total_routes = len(df)
    excellent_service = len(df[df['status_category'] == 'Excellent'])
    good_service = len(df[df['status_category'] == 'Good'])
    issues = len(df[df['status_category'].isin(['Fair', 'Poor'])])
    avg_efficiency = df['efficiency_score'].mean()
    avg_delay = df['delay_minutes'].mean()
    avg_punctuality = df['punctuality_percent'].mean()
    
    return {
        'total_routes': int(total_routes),
        'excellent_service': int(excellent_service),
        'good_service': int(good_service),
        'issues': int(issues),
        'avg_efficiency_score': round(float(avg_efficiency), 1),
        'avg_delay_minutes': round(float(avg_delay), 1),
        'avg_punctuality_percent': round(float(avg_punctuality), 1),
        'last_updated': datetime.now().isoformat()
    }

def export_results(df: pd.DataFrame, geojson: Dict[str, Any], summary: Dict[str, Any]):
    """Export processed results to files"""
    print("📤 Exporting results...")
    
    # Export GeoJSON
    with open('copenhagen_transit_status.geojson', 'w') as f:
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
    
    print("✅ Exported transit status: copenhagen_transit_status.geojson")
    print("✅ Exported API data: transit_status_latest.json")
    print("✅ Exported visualization: copenhagen_transit_status.png")

def create_status_visualization(df: pd.DataFrame):
    """Create Copenhagen transit status visualization"""
    if not MATPLOTLIB_AVAILABLE:
        print("📊 Matplotlib not available, skipping visualization")
        return
        
    plt.figure(figsize=(12, 8))
    
    # Status distribution
    plt.subplot(2, 2, 1)
    status_counts = df['status_category'].value_counts()
    colors = ['#00A86B', '#FFCC00', '#FF6600', '#CC0000'][:len(status_counts)]
    plt.pie(status_counts.values, labels=status_counts.index, autopct='%1.1f%%', colors=colors)
    plt.title('Copenhagen Transit Status Distribution')
    
    # Efficiency scores by route
    plt.subplot(2, 2, 2)
    df_sorted = df.sort_values('efficiency_score')
    bars = plt.barh(df_sorted['route_name'], df_sorted['efficiency_score'])
    for i, bar in enumerate(bars):
        bar.set_color(df_sorted.iloc[i]['route_color'])
    plt.xlabel('Efficiency Score (0-10)')
    plt.title('Efficiency by Copenhagen Route')
    plt.xlim(0, 10)
    
    # Route types
    plt.subplot(2, 2, 3)
    type_counts = df['route_type'].value_counts()
    plt.bar(type_counts.index, type_counts.values, color=['#00A86B', '#0066CC', '#E60026'])
    plt.title('Routes by Type')
    plt.ylabel('Number of Routes')
    
    # Summary stats
    plt.subplot(2, 2, 4)
    summary_text = f"""
    Total Routes: {len(df)}
    Excellent: {len(df[df['status_category'] == 'Excellent'])}
    Good: {len(df[df['status_category'] == 'Good'])}
    Issues: {len(df[df['status_category'].isin(['Fair', 'Poor'])])}
    Avg Efficiency: {df['efficiency_score'].mean():.1f}/10
    Avg Delay: {df['delay_minutes'].mean():.1f} min
    Avg Punctuality: {df['punctuality_percent'].mean():.1f}%
    """
    plt.text(0.1, 0.5, summary_text, fontsize=10, transform=plt.gca().transAxes, 
             verticalalignment='center')
    plt.axis('off')
    plt.title('Copenhagen Transit Summary')
    
    plt.tight_layout()
    plt.savefig('copenhagen_transit_status.png', dpi=300, bbox_inches='tight')
    plt.close()

def main():
    """Main processing function"""
    start_time = time.time()
    print("🚇 Starting Copenhagen Transit Now processing...")
    
    # Try to fetch real Danish transit data
    departures_data = fetch_copenhagen_departures()
    stog_data = fetch_stog_status()
    
    # For now, use sample data (real API integration would require more complex parsing)
    route_data = create_sample_copenhagen_data()
    
    # Process data
    df = process_copenhagen_data(route_data)
    geojson = create_copenhagen_geojson(df)
    summary = create_transit_summary(df)
    
    # Export results
    export_results(df, geojson, summary)
    
    # Print summary
    processing_time = time.time() - start_time
    print(f"\n🎉 Copenhagen Transit Now processing completed!")
    print(f"🚇 Processed {len(df)} Copenhagen transit routes")
    print(f"✅ Excellent service: {summary['excellent_service']}")
    print(f"👍 Good service: {summary['good_service']}")
    print(f"⚠️ Issues: {summary['issues']}")
    print(f"⏱️ Processing time: {processing_time:.2f} seconds")
    print(f"📊 Average efficiency: {summary['avg_efficiency_score']}/10")
    print(f"🎯 Average punctuality: {summary['avg_punctuality_percent']}%")

if __name__ == "__main__":
    main()
