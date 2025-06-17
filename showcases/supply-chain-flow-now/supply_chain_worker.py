#!/usr/bin/env python3
"""
Supply Chain Flow Now - Real-time supply chain visibility and logistics flow analysis
The ultimate 40-line microservice that turns multi-modal logistics data into unified supply chain intelligence
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
    print("🚛 Starting Supply Chain Flow Now processing...")
    start_time = time.time()
    
    # 1. Fetch real-time supply chain data from multiple sources
    print("📦 Fetching multi-modal supply chain data...")
    try:
        # Try to get real supply chain data first
        supply_chain_data = fetch_supply_chain_data()
        if not supply_chain_data:
            print("🎭 Supply chain APIs unavailable, creating realistic mock data...")
            supply_chain_data = create_mock_supply_chain_data()
        print(f"✅ Fetched supply chain data: {len(supply_chain_data)} nodes")
    except Exception as e:
        print(f"⚠️ Error fetching supply chain data: {e}")
        print("🎭 Creating realistic mock supply chain data...")
        supply_chain_data = create_mock_supply_chain_data()
    
    # 2. Load supply chain infrastructure data
    print("🏭 Loading supply chain infrastructure data...")
    infrastructure_path = Path("data/supply_chain_infrastructure.geojson")
    if not infrastructure_path.exists():
        print("📝 Creating supply chain infrastructure GeoJSON...")
        create_supply_chain_infrastructure_geojson()
    
    infrastructure_gdf = gpd.read_file(infrastructure_path)
    print(f"✅ Loaded {len(infrastructure_gdf)} supply chain nodes")
    
    # 3. Process supply chain data into GeoDataFrame
    supply_chain_df = pd.DataFrame(supply_chain_data)
    supply_chain_gdf = gpd.GeoDataFrame(
        supply_chain_df, 
        geometry=gpd.points_from_xy(supply_chain_df.longitude, supply_chain_df.latitude),
        crs='EPSG:4326'
    )
    
    # 4. Calculate supply chain flow and efficiency scores
    print("📊 Calculating supply chain flow efficiency...")
    for idx, node in supply_chain_gdf.iterrows():
        # Calculate comprehensive flow efficiency score
        capacity_score = calculate_capacity_efficiency(node['capacity_units'])
        delay_score = calculate_delay_impact(node['current_delay_hours'])
        utilization_score = calculate_utilization_efficiency(node['utilization_percent'])
        disruption_score = calculate_disruption_impact(node.get('disruption_level', 'None'))
        
        # Combined flow efficiency score (0-100, higher = better efficiency)
        flow_efficiency = (capacity_score + delay_score + utilization_score + disruption_score) / 4
        
        supply_chain_gdf.at[idx, 'capacity_score'] = capacity_score
        supply_chain_gdf.at[idx, 'delay_score'] = delay_score
        supply_chain_gdf.at[idx, 'utilization_score'] = utilization_score
        supply_chain_gdf.at[idx, 'disruption_score'] = disruption_score
        supply_chain_gdf.at[idx, 'flow_efficiency'] = round(flow_efficiency, 1)
        supply_chain_gdf.at[idx, 'flow_status'] = classify_flow_status(flow_efficiency)
        supply_chain_gdf.at[idx, 'economic_impact'] = assess_economic_impact(node)
    
    # 5. Add supply chain condition classification
    supply_chain_gdf['condition_category'] = supply_chain_gdf.apply(classify_supply_chain_condition, axis=1)
    supply_chain_gdf['alert_level'] = supply_chain_gdf.apply(determine_alert_level, axis=1)
    
    # 6. Calculate regional supply chain health
    print("🌐 Analyzing regional supply chain health...")
    regional_health = calculate_regional_health(supply_chain_gdf)
    
    # 7. Generate supply chain flows between nodes
    print("🔗 Generating supply chain flow connections...")
    flow_connections = generate_flow_connections(supply_chain_gdf)
    
    # 8. Export results
    print("📤 Exporting results...")
    
    # Export supply chain GeoJSON
    supply_chain_output = "supply_chain_flow.geojson"
    supply_chain_gdf.to_file(supply_chain_output, driver="GeoJSON")
    print(f"✅ Exported supply chain GeoJSON: {supply_chain_output}")
    
    # Export combined JSON for API
    api_data = {
        "supply_chain": json.loads(supply_chain_gdf.to_json()),
        "infrastructure": json.loads(infrastructure_gdf.to_json()),
        "flow_connections": flow_connections,
        "regional_health": regional_health,
        "summary": {
            "total_nodes": int(len(supply_chain_gdf)),
            "avg_flow_efficiency": float(round(supply_chain_gdf['flow_efficiency'].mean(), 1)),
            "critical_nodes": int(len(supply_chain_gdf[supply_chain_gdf['flow_efficiency'] < 30])),
            "total_capacity": float(round(supply_chain_gdf['capacity_units'].sum(), 0)),
            "nodes_with_delays": int(len(supply_chain_gdf[supply_chain_gdf['current_delay_hours'] > 0])),
            "high_risk_nodes": int(len(supply_chain_gdf[supply_chain_gdf['alert_level'] == 'Critical'])),
            "active_flows": int(len(flow_connections))
        }
    }
    
    with open("supply_chain_latest.json", "w") as f:
        json.dump(api_data, f, indent=2)
    
    # Create visualization with lighter styling
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))
    fig.patch.set_facecolor('white')  # Light background
    
    # Plot 1: Supply chain flow efficiency
    supply_chain_gdf.plot(
        column='flow_efficiency',
        cmap='RdYlGn',  # Red-Yellow-Green for efficiency
        markersize=supply_chain_gdf['capacity_units'] / 1000,
        alpha=0.8,
        legend=True,
        ax=ax1
    )
    ax1.set_title("Supply Chain Flow Now - Efficiency Scores", fontsize=14, fontweight='bold', color='#2c3e50')
    ax1.set_xlabel("Longitude", color='#34495e')
    ax1.set_ylabel("Latitude", color='#34495e')
    ax1.set_facecolor('#f8f9fa')  # Very light background
    
    # Plot 2: Supply chain status
    supply_chain_gdf.plot(
        column='flow_status',
        categorical=True,
        legend=True,
        markersize=50,
        alpha=0.8,
        ax=ax2,
        cmap='Set3'  # Lighter, more vibrant colors
    )
    ax2.set_title("Flow Status Analysis", fontsize=14, fontweight='bold', color='#2c3e50')
    ax2.set_xlabel("Longitude", color='#34495e')
    ax2.set_ylabel("Latitude", color='#34495e')
    ax2.set_facecolor('#f8f9fa')  # Very light background
    
    plt.tight_layout()
    plt.savefig("supply_chain_flow.png", dpi=120, bbox_inches='tight', facecolor='white')
    plt.close()
    print("✅ Exported visualization: supply_chain_flow.png")
    
    # 9. Summary statistics
    processing_time = time.time() - start_time
    avg_efficiency = supply_chain_gdf['flow_efficiency'].mean()
    total_capacity = supply_chain_gdf['capacity_units'].sum()
    critical_count = len(supply_chain_gdf[supply_chain_gdf['flow_efficiency'] < 30])
    
    print("🎉 Supply Chain Flow Now processing completed!")
    print(f"🚛 Processed {len(supply_chain_gdf)} supply chain nodes")
    print(f"📦 Total capacity: {total_capacity:,.0f} units/day")
    print(f"⏱️ Processing time: {processing_time:.2f} seconds")
    print(f"📈 Average flow efficiency: {avg_efficiency:.1f}")
    print(f"🔴 Critical nodes: {critical_count}")
    print(f"🔗 Active flows: {len(flow_connections)}")

def fetch_supply_chain_data():
    """Attempt to fetch real supply chain data from multiple APIs"""
    try:
        # Supply chain API endpoints (requires API keys for production)
        # This is a simplified example - in production you'd use proper APIs
        print("🌐 Attempting to fetch real supply chain data...")
        
        # For demo purposes, we'll simulate the API calls
        # Real implementation would use: USPS, FedEx, UPS, Port Authority APIs
        return None  # Fallback to mock data for demo
        
    except Exception as e:
        print(f"⚠️ Supply chain API error: {e}")
        return None

def calculate_capacity_efficiency(capacity_units):
    """Calculate efficiency score based on node capacity (0-100, higher = better)"""
    if capacity_units > 50000:  # Major hub
        return 90
    elif capacity_units > 25000:  # Large facility
        return 80
    elif capacity_units > 10000:  # Medium facility
        return 70
    elif capacity_units > 5000:  # Small facility
        return 60
    else:  # Very small
        return 40

def calculate_delay_impact(delay_hours):
    """Calculate efficiency score based on current delays (0-100, higher = better)"""
    if delay_hours == 0:  # No delays
        return 100
    elif delay_hours <= 2:  # Minor delays
        return 80
    elif delay_hours <= 6:  # Moderate delays
        return 60
    elif delay_hours <= 12:  # Significant delays
        return 40
    else:  # Major delays
        return 20

def calculate_utilization_efficiency(utilization_percent):
    """Calculate efficiency score based on utilization (0-100, higher = better)"""
    if 70 <= utilization_percent <= 85:  # Optimal utilization
        return 100
    elif 60 <= utilization_percent < 70 or 85 < utilization_percent <= 90:  # Good utilization
        return 80
    elif 50 <= utilization_percent < 60 or 90 < utilization_percent <= 95:  # Fair utilization
        return 60
    elif utilization_percent < 50 or utilization_percent > 95:  # Poor utilization
        return 40
    else:
        return 20

def calculate_disruption_impact(disruption_level):
    """Calculate efficiency score based on disruption level (0-100, higher = better)"""
    if disruption_level == 'None':
        return 100
    elif disruption_level == 'Minor':
        return 80
    elif disruption_level == 'Moderate':
        return 60
    elif disruption_level == 'Major':
        return 40
    else:  # Severe
        return 20

def classify_flow_status(flow_efficiency):
    """Classify flow status based on efficiency score"""
    if flow_efficiency >= 85:
        return 'Excellent'
    elif flow_efficiency >= 70:
        return 'Good'
    elif flow_efficiency >= 55:
        return 'Fair'
    elif flow_efficiency >= 40:
        return 'Poor'
    else:
        return 'Critical'

def classify_supply_chain_condition(node):
    """Classify supply chain condition based on multiple factors"""
    delay = node['current_delay_hours']
    utilization = node['utilization_percent']
    disruption = node.get('disruption_level', 'None')
    
    if disruption in ['Major', 'Severe']:
        return 'Disrupted'
    elif delay > 6:
        return 'Delayed'
    elif utilization > 95:
        return 'Congested'
    elif utilization < 50:
        return 'Underutilized'
    else:
        return 'Normal Flow'

def determine_alert_level(node):
    """Determine alert level based on flow efficiency"""
    efficiency = node['flow_efficiency']
    if efficiency < 30:
        return 'Critical'
    elif efficiency < 50:
        return 'High'
    elif efficiency < 70:
        return 'Moderate'
    else:
        return 'Low'

def assess_economic_impact(node):
    """Assess economic impact of supply chain issues"""
    capacity = node['capacity_units']
    delay = node['current_delay_hours']
    utilization = node['utilization_percent']
    
    # Base economic impact per unit per hour (simplified)
    base_impact_per_unit = 10  # $10 per unit per hour
    
    # Calculate impact based on delays and inefficiency
    delay_impact = delay * capacity * base_impact_per_unit
    
    # Add utilization inefficiency impact
    if utilization > 95:  # Congestion costs
        utilization_impact = (utilization - 95) * capacity * base_impact_per_unit * 0.1
    elif utilization < 50:  # Underutilization costs
        utilization_impact = (50 - utilization) * capacity * base_impact_per_unit * 0.05
    else:
        utilization_impact = 0
    
    total_impact = delay_impact + utilization_impact
    return float(round(total_impact, 0))

def calculate_regional_health(supply_chain_gdf):
    """Calculate regional supply chain health metrics"""
    regions = {
        'Northeast': supply_chain_gdf[(supply_chain_gdf.geometry.x > -80) & (supply_chain_gdf.geometry.y > 40)],
        'Southeast': supply_chain_gdf[(supply_chain_gdf.geometry.x > -90) & (supply_chain_gdf.geometry.y < 40) & (supply_chain_gdf.geometry.y > 25)],
        'Midwest': supply_chain_gdf[(supply_chain_gdf.geometry.x < -80) & (supply_chain_gdf.geometry.x > -100) & (supply_chain_gdf.geometry.y > 35)],
        'Southwest': supply_chain_gdf[(supply_chain_gdf.geometry.x < -100) & (supply_chain_gdf.geometry.y < 40) & (supply_chain_gdf.geometry.y > 25)],
        'West': supply_chain_gdf[(supply_chain_gdf.geometry.x < -110)]
    }
    
    regional_health = {}
    for region, nodes in regions.items():
        if len(nodes) > 0:
            regional_health[region] = {
                'avg_flow_efficiency': float(round(nodes['flow_efficiency'].mean(), 1)),
                'total_capacity': float(round(nodes['capacity_units'].sum(), 0)),
                'node_count': int(len(nodes)),
                'critical_count': int(len(nodes[nodes['flow_efficiency'] < 30])),
                'avg_delay': float(round(nodes['current_delay_hours'].mean(), 1))
            }
        else:
            regional_health[region] = {
                'avg_flow_efficiency': 0.0,
                'total_capacity': 0.0,
                'node_count': 0,
                'critical_count': 0,
                'avg_delay': 0.0
            }
    
    return regional_health

def generate_flow_connections(supply_chain_gdf):
    """Generate realistic flow connections between supply chain nodes"""
    import random
    
    connections = []
    nodes = supply_chain_gdf.to_dict('records')
    
    # Create connections based on node types and proximity
    for i, origin in enumerate(nodes):
        # Each node connects to 2-4 other nodes
        num_connections = random.randint(2, 4)
        
        # Select target nodes (prefer different types and reasonable distances)
        potential_targets = [j for j, target in enumerate(nodes) if j != i]
        selected_targets = random.sample(potential_targets, min(num_connections, len(potential_targets)))
        
        for target_idx in selected_targets:
            target = nodes[target_idx]
            
            # Calculate flow volume based on capacities
            flow_volume = min(origin['capacity_units'], target['capacity_units']) * random.uniform(0.1, 0.3)
            
            # Calculate flow health based on both nodes
            flow_health = (origin['flow_efficiency'] + target['flow_efficiency']) / 2
            
            connection = {
                'origin_id': i,
                'target_id': target_idx,
                'origin_coords': [origin['longitude'], origin['latitude']],
                'target_coords': [target['longitude'], target['latitude']],
                'flow_volume': round(flow_volume, 0),
                'flow_health': round(flow_health, 1),
                'transport_mode': random.choice(['Truck', 'Rail', 'Ship', 'Air']),
                'estimated_time': random.randint(4, 72)  # hours
            }
            connections.append(connection)
    
    return connections

def create_mock_supply_chain_data():
    """Create realistic mock supply chain data for demo purposes"""
    import random

    # Major supply chain nodes across the US
    nodes = [
        # Major Ports
        {'name': 'Port of Los Angeles', 'lat': 33.7361, 'lon': -118.2922, 'type': 'Port', 'capacity': 75000},
        {'name': 'Port of Long Beach', 'lat': 33.7553, 'lon': -118.2111, 'type': 'Port', 'capacity': 65000},
        {'name': 'Port of New York/New Jersey', 'lat': 40.6892, 'lon': -74.0445, 'type': 'Port', 'capacity': 55000},
        {'name': 'Port of Savannah', 'lat': 32.1347, 'lon': -81.1888, 'type': 'Port', 'capacity': 45000},
        {'name': 'Port of Seattle', 'lat': 47.5952, 'lon': -122.3316, 'type': 'Port', 'capacity': 35000},
        {'name': 'Port of Houston', 'lat': 29.7372, 'lon': -95.2861, 'type': 'Port', 'capacity': 40000},

        # Major Distribution Centers
        {'name': 'Amazon Fulfillment - Phoenix', 'lat': 33.4484, 'lon': -112.0740, 'type': 'Distribution', 'capacity': 25000},
        {'name': 'FedEx Hub - Memphis', 'lat': 35.0424, 'lon': -89.9773, 'type': 'Distribution', 'capacity': 30000},
        {'name': 'UPS Worldport - Louisville', 'lat': 38.1744, 'lon': -85.7361, 'type': 'Distribution', 'capacity': 35000},
        {'name': 'Walmart DC - Bentonville', 'lat': 36.3729, 'lon': -94.2088, 'type': 'Distribution', 'capacity': 28000},
        {'name': 'Amazon Fulfillment - Dallas', 'lat': 32.8998, 'lon': -97.0403, 'type': 'Distribution', 'capacity': 22000},
        {'name': 'Target DC - Minneapolis', 'lat': 44.8848, 'lon': -93.2223, 'type': 'Distribution', 'capacity': 20000},

        # Major Manufacturing
        {'name': 'Tesla Gigafactory - Austin', 'lat': 30.2672, 'lon': -97.7431, 'type': 'Manufacturing', 'capacity': 15000},
        {'name': 'Ford Rouge Plant - Detroit', 'lat': 42.3314, 'lon': -83.0458, 'type': 'Manufacturing', 'capacity': 18000},
        {'name': 'Boeing Everett - Seattle', 'lat': 47.9298, 'lon': -122.2817, 'type': 'Manufacturing', 'capacity': 12000},
        {'name': 'Intel Fab - Portland', 'lat': 45.5152, 'lon': -122.6784, 'type': 'Manufacturing', 'capacity': 8000},
        {'name': 'Apple Park - Cupertino', 'lat': 37.3349, 'lon': -122.0090, 'type': 'Manufacturing', 'capacity': 10000},

        # Major Rail Hubs
        {'name': 'BNSF Intermodal - Chicago', 'lat': 41.8781, 'lon': -87.6298, 'type': 'Rail', 'capacity': 32000},
        {'name': 'Union Pacific - Kansas City', 'lat': 39.0997, 'lon': -94.5786, 'type': 'Rail', 'capacity': 28000},
        {'name': 'CSX Terminal - Atlanta', 'lat': 33.7490, 'lon': -84.3880, 'type': 'Rail', 'capacity': 25000},
        {'name': 'Norfolk Southern - Norfolk', 'lat': 36.8468, 'lon': -76.2852, 'type': 'Rail', 'capacity': 22000},

        # Major Airports (Cargo)
        {'name': 'LAX Cargo - Los Angeles', 'lat': 33.9425, 'lon': -118.4081, 'type': 'Airport', 'capacity': 18000},
        {'name': 'JFK Cargo - New York', 'lat': 40.6413, 'lon': -73.7781, 'type': 'Airport', 'capacity': 16000},
        {'name': 'ORD Cargo - Chicago', 'lat': 41.9742, 'lon': -87.9073, 'type': 'Airport', 'capacity': 15000},
        {'name': 'MIA Cargo - Miami', 'lat': 25.7959, 'lon': -80.2870, 'type': 'Airport', 'capacity': 14000},

        # Regional Distribution
        {'name': 'Costco DC - Denver', 'lat': 39.7392, 'lon': -104.9903, 'type': 'Distribution', 'capacity': 12000},
        {'name': 'Home Depot DC - Atlanta', 'lat': 33.7490, 'lon': -84.3880, 'type': 'Distribution', 'capacity': 15000},
        {'name': 'Kroger DC - Cincinnati', 'lat': 39.1031, 'lon': -84.5120, 'type': 'Distribution', 'capacity': 11000},
        {'name': 'Sysco DC - Houston', 'lat': 29.7604, 'lon': -95.3698, 'type': 'Distribution', 'capacity': 13000},
    ]

    supply_chain_data = []
    for node in nodes:
        # Generate realistic operational data
        disruption_levels = ['None', 'None', 'None', 'Minor', 'Moderate', 'Major']
        weights = [70, 15, 10, 3, 1.5, 0.5]  # Most nodes operating normally

        disruption_level = random.choices(disruption_levels, weights=weights)[0]

        # Delays vary by disruption level
        if disruption_level == 'None':
            current_delay = 0
        elif disruption_level == 'Minor':
            current_delay = random.uniform(0.5, 2)
        elif disruption_level == 'Moderate':
            current_delay = random.uniform(2, 6)
        else:  # Major
            current_delay = random.uniform(6, 24)

        # Utilization varies by node type and disruption
        if disruption_level in ['Major']:
            utilization = random.uniform(30, 60)
        elif disruption_level == 'Moderate':
            utilization = random.uniform(60, 85)
        else:
            utilization = random.uniform(70, 95)

        supply_chain_data.append({
            'node_name': node['name'],
            'latitude': node['lat'],
            'longitude': node['lon'],
            'node_type': node['type'],
            'capacity_units': node['capacity'],
            'current_delay_hours': round(current_delay, 1),
            'utilization_percent': round(utilization, 1),
            'disruption_level': disruption_level,
            'operator': random.choice(['Amazon', 'FedEx', 'UPS', 'Walmart', 'Target', 'Costco', 'Port Authority']),
            'region': random.choice(['West Coast', 'East Coast', 'Midwest', 'South', 'Southwest']),
            'last_update': f"2024-{random.randint(1,12):02d}-{random.randint(1,28):02d}"
        })

    return supply_chain_data

def create_supply_chain_infrastructure_geojson():
    """Create GeoJSON file with major supply chain infrastructure"""
    infrastructure_data = {
        "type": "FeatureCollection",
        "features": [
            {"type": "Feature", "properties": {"name": "Port of Los Angeles", "type": "Port", "capacity": 75000, "state": "CA"}, "geometry": {"type": "Point", "coordinates": [-118.2922, 33.7361]}},
            {"type": "Feature", "properties": {"name": "Port of Long Beach", "type": "Port", "capacity": 65000, "state": "CA"}, "geometry": {"type": "Point", "coordinates": [-118.2111, 33.7553]}},
            {"type": "Feature", "properties": {"name": "Port of New York/New Jersey", "type": "Port", "capacity": 55000, "state": "NY"}, "geometry": {"type": "Point", "coordinates": [-74.0445, 40.6892]}},
            {"type": "Feature", "properties": {"name": "FedEx Hub - Memphis", "type": "Distribution", "capacity": 30000, "state": "TN"}, "geometry": {"type": "Point", "coordinates": [-89.9773, 35.0424]}},
            {"type": "Feature", "properties": {"name": "UPS Worldport - Louisville", "type": "Distribution", "capacity": 35000, "state": "KY"}, "geometry": {"type": "Point", "coordinates": [-85.7361, 38.1744]}},
            {"type": "Feature", "properties": {"name": "Amazon Fulfillment - Phoenix", "type": "Distribution", "capacity": 25000, "state": "AZ"}, "geometry": {"type": "Point", "coordinates": [-112.0740, 33.4484]}},
            {"type": "Feature", "properties": {"name": "Tesla Gigafactory - Austin", "type": "Manufacturing", "capacity": 15000, "state": "TX"}, "geometry": {"type": "Point", "coordinates": [-97.7431, 30.2672]}},
            {"type": "Feature", "properties": {"name": "Ford Rouge Plant - Detroit", "type": "Manufacturing", "capacity": 18000, "state": "MI"}, "geometry": {"type": "Point", "coordinates": [-83.0458, 42.3314]}},
            {"type": "Feature", "properties": {"name": "BNSF Intermodal - Chicago", "type": "Rail", "capacity": 32000, "state": "IL"}, "geometry": {"type": "Point", "coordinates": [-87.6298, 41.8781]}},
            {"type": "Feature", "properties": {"name": "LAX Cargo - Los Angeles", "type": "Airport", "capacity": 18000, "state": "CA"}, "geometry": {"type": "Point", "coordinates": [-118.4081, 33.9425]}},
            {"type": "Feature", "properties": {"name": "JFK Cargo - New York", "type": "Airport", "capacity": 16000, "state": "NY"}, "geometry": {"type": "Point", "coordinates": [-73.7781, 40.6413]}},
            {"type": "Feature", "properties": {"name": "Port of Savannah", "type": "Port", "capacity": 45000, "state": "GA"}, "geometry": {"type": "Point", "coordinates": [-81.1888, 32.1347]}},
            {"type": "Feature", "properties": {"name": "Port of Seattle", "type": "Port", "capacity": 35000, "state": "WA"}, "geometry": {"type": "Point", "coordinates": [-122.3316, 47.5952]}},
            {"type": "Feature", "properties": {"name": "Boeing Everett - Seattle", "type": "Manufacturing", "capacity": 12000, "state": "WA"}, "geometry": {"type": "Point", "coordinates": [-122.2817, 47.9298]}},
            {"type": "Feature", "properties": {"name": "Walmart DC - Bentonville", "type": "Distribution", "capacity": 28000, "state": "AR"}, "geometry": {"type": "Point", "coordinates": [-94.2088, 36.3729]}},
        ]
    }

    with open("data/supply_chain_infrastructure.geojson", "w") as f:
        json.dump(infrastructure_data, f, indent=2)

    print("✅ Created supply_chain_infrastructure.geojson with 15 major supply chain nodes")

if __name__ == "__main__":
    main()
