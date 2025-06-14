#!/usr/bin/env python3
"""
Last-Mile Delivery Optimization Example

This example demonstrates how to use PyMapGIS for last-mile delivery optimization
in urban logistics networks. The analysis focuses on route planning, delivery
time windows, and distribution center assignment.

Backstory:
---------
QuickDeliver Express is an e-commerce logistics company operating in the Los Angeles
metropolitan area. They handle same-day and next-day deliveries for online retailers
and need to optimize their last-mile delivery operations to:

1. Minimize delivery times and costs
2. Respect customer delivery time windows
3. Optimize vehicle routing and capacity utilization
4. Balance workload across distribution centers
5. Improve customer satisfaction through reliable delivery

The company operates 3 distribution centers and needs to assign 15 daily deliveries
to the most efficient routes while considering:
- Package priorities (standard, express, premium)
- Delivery time windows
- Traffic patterns and road network constraints
- Vehicle capacity and type restrictions
- Distribution center processing capabilities

Usage:
------
python last_mile_optimization.py

Requirements:
------------
- pymapgis
- geopandas
- networkx
- matplotlib
- pandas
"""

import pymapgis as pmg
import geopandas as gpd
import pandas as pd
import numpy as np
import networkx as nx
from shapely.geometry import Point, LineString
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

def load_delivery_data():
    """Load delivery addresses, distribution centers, and road network."""
    print("📦 Loading delivery optimization data...")
    
    # Load delivery addresses
    deliveries = pmg.read("file://data/delivery_addresses.geojson")
    print(f"   ✓ Loaded {len(deliveries)} delivery addresses")
    
    # Load distribution centers
    distribution_centers = pmg.read("file://data/distribution_centers.geojson")
    print(f"   ✓ Loaded {len(distribution_centers)} distribution centers")
    
    # Load road network
    road_network = pmg.read("file://data/road_network.geojson")
    print(f"   ✓ Loaded {len(road_network)} road segments")
    
    return deliveries, distribution_centers, road_network

def create_delivery_network(road_network):
    """Create a network graph from road segments for routing analysis."""
    print("🛣️  Creating delivery network graph...")
    
    # Create NetworkX graph from road segments
    G = nx.Graph()
    
    for _, road in road_network.iterrows():
        coords = road.geometry.coords
        
        # Add nodes and edges for each road segment
        for i in range(len(coords) - 1):
            start_node = coords[i]
            end_node = coords[i + 1]
            
            # Calculate segment length and travel time
            segment_length = Point(start_node).distance(Point(end_node)) * 111  # Convert to km
            travel_time = (segment_length / road['speed_limit']) * road['traffic_factor'] * 60  # Minutes
            
            G.add_edge(start_node, end_node, 
                      length=segment_length,
                      travel_time=travel_time,
                      road_type=road['road_type'],
                      speed_limit=road['speed_limit'])
    
    print(f"   ✓ Created network with {G.number_of_nodes()} nodes and {G.number_of_edges()} edges")
    return G

def assign_deliveries_to_centers(deliveries, distribution_centers):
    """Assign deliveries to the nearest distribution center."""
    print("🎯 Assigning deliveries to distribution centers...")
    
    assignments = []
    
    for _, delivery in deliveries.iterrows():
        delivery_point = delivery.geometry
        
        # Calculate distances to all distribution centers
        center_distances = []
        for _, center in distribution_centers.iterrows():
            distance = delivery_point.distance(center.geometry) * 111  # Convert to km
            center_distances.append({
                'center_id': center['center_id'],
                'center_name': center['name'],
                'distance_km': distance,
                'processing_time': center['avg_processing_time']
            })
        
        # Assign to nearest center
        nearest_center = min(center_distances, key=lambda x: x['distance_km'])
        
        assignments.append({
            'delivery_id': delivery['delivery_id'],
            'customer_name': delivery['customer_name'],
            'assigned_center': nearest_center['center_id'],
            'center_name': nearest_center['center_name'],
            'distance_to_center': nearest_center['distance_km'],
            'priority': delivery['priority'],
            'delivery_window': delivery['delivery_window'],
            'package_weight': delivery['package_weight']
        })
    
    return pd.DataFrame(assignments)

def optimize_delivery_routes(assignments, deliveries, distribution_centers, network_graph=None):
    """Optimize delivery routes for each distribution center."""
    print("🚚 Optimizing delivery routes...")

    route_plans = {}

    # Group deliveries by assigned distribution center
    for center_id in assignments['assigned_center'].unique():
        center_deliveries = assignments[assignments['assigned_center'] == center_id]
        center_info = distribution_centers[distribution_centers['center_id'] == center_id].iloc[0]

        print(f"   Planning routes for {center_info['name']} ({len(center_deliveries)} deliveries)")

        # Sort deliveries by priority and time window
        priority_order = {'premium': 1, 'express': 2, 'standard': 3}
        center_deliveries = center_deliveries.copy()
        center_deliveries['priority_rank'] = center_deliveries['priority'].map(priority_order)
        center_deliveries = center_deliveries.sort_values(['priority_rank', 'delivery_window'])

        # Create route optimization
        route_optimization = optimize_single_center_routes(
            center_deliveries, center_info, deliveries, network_graph
        )

        route_plans[center_id] = route_optimization

    return route_plans

def optimize_single_center_routes(center_deliveries, center_info, all_deliveries, network_graph):
    """Optimize routes for a single distribution center using simplified TSP approach."""
    
    # Get delivery coordinates
    delivery_coords = []
    delivery_details = []
    
    center_coord = (center_info.geometry.x, center_info.geometry.y)
    
    for _, delivery in center_deliveries.iterrows():
        delivery_detail = all_deliveries[all_deliveries['delivery_id'] == delivery['delivery_id']].iloc[0]
        coord = (delivery_detail.geometry.x, delivery_detail.geometry.y)
        delivery_coords.append(coord)
        delivery_details.append(delivery_detail)
    
    # Simple nearest neighbor route optimization
    route = [center_coord]  # Start at distribution center
    unvisited = delivery_coords.copy()
    current_pos = center_coord
    
    total_distance = 0
    total_time = 0
    
    while unvisited:
        # Find nearest unvisited delivery
        distances = [Point(current_pos).distance(Point(coord)) * 111 for coord in unvisited]
        nearest_idx = distances.index(min(distances))
        nearest_coord = unvisited[nearest_idx]
        
        # Add to route
        route.append(nearest_coord)
        total_distance += distances[nearest_idx]
        total_time += distances[nearest_idx] / 40 * 60  # Assume 40 km/h average speed, convert to minutes
        
        # Update current position and remove from unvisited
        current_pos = nearest_coord
        unvisited.pop(nearest_idx)
    
    # Return to distribution center
    return_distance = Point(current_pos).distance(Point(center_coord)) * 111
    route.append(center_coord)
    total_distance += return_distance
    total_time += return_distance / 40 * 60
    
    return {
        'route': route,
        'deliveries': delivery_details,
        'total_distance_km': total_distance,
        'total_time_minutes': total_time,
        'delivery_count': len(delivery_details)
    }

def calculate_service_areas(distribution_centers, max_distance_km=15):
    """Calculate service areas for each distribution center."""
    print("🗺️  Calculating service areas...")
    
    service_areas = distribution_centers.copy()
    
    # Create buffer zones around distribution centers
    buffer_degrees = max_distance_km / 111  # Convert km to degrees (approximate)
    service_areas['service_area'] = service_areas.geometry.buffer(buffer_degrees)
    
    return service_areas

def analyze_delivery_performance(route_plans, assignments):
    """Analyze delivery performance metrics."""
    print("📊 Analyzing delivery performance...")
    
    performance_metrics = []
    
    for center_id, route_plan in route_plans.items():
        center_assignments = assignments[assignments['assigned_center'] == center_id]
        
        # Calculate performance metrics
        avg_distance = route_plan['total_distance_km'] / route_plan['delivery_count']
        avg_time_per_delivery = route_plan['total_time_minutes'] / route_plan['delivery_count']
        
        # Priority distribution
        priority_counts = center_assignments['priority'].value_counts()
        
        # Package weight analysis
        total_weight = center_assignments['package_weight'].sum()
        avg_weight = center_assignments['package_weight'].mean()
        
        performance_metrics.append({
            'center_id': center_id,
            'delivery_count': route_plan['delivery_count'],
            'total_distance_km': route_plan['total_distance_km'],
            'total_time_minutes': route_plan['total_time_minutes'],
            'avg_distance_per_delivery': avg_distance,
            'avg_time_per_delivery': avg_time_per_delivery,
            'total_package_weight': total_weight,
            'avg_package_weight': avg_weight,
            'premium_deliveries': priority_counts.get('premium', 0),
            'express_deliveries': priority_counts.get('express', 0),
            'standard_deliveries': priority_counts.get('standard', 0)
        })
    
    return pd.DataFrame(performance_metrics)

def visualize_delivery_optimization(deliveries, distribution_centers, assignments, route_plans, service_areas, performance_metrics):
    """Create comprehensive delivery optimization visualizations."""
    print("📈 Creating delivery optimization visualizations...")
    
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(20, 16))
    
    # Map 1: Delivery assignments and service areas
    ax1.set_title("Delivery Assignments and Service Areas", fontsize=14, fontweight='bold')
    
    # Plot service areas
    service_areas_gdf = gpd.GeoDataFrame(service_areas)
    service_areas_gdf.set_geometry('service_area').plot(ax=ax1, alpha=0.2, 
                                                        color=['red', 'blue', 'green'])
    
    # Plot distribution centers
    distribution_centers.plot(ax=ax1, color='black', markersize=200, marker='s', 
                             alpha=0.8, label='Distribution Centers')
    
    # Plot deliveries with color coding by assigned center
    center_colors = {'DC_CENTRAL': 'red', 'DC_WEST': 'blue', 'DC_SOUTH': 'green'}
    for center_id, color in center_colors.items():
        center_deliveries = assignments[assignments['assigned_center'] == center_id]
        if not center_deliveries.empty:
            delivery_points = deliveries[deliveries['delivery_id'].isin(center_deliveries['delivery_id'])]
            delivery_points.plot(ax=ax1, color=color, markersize=50, alpha=0.7, 
                               label=f'{center_id} Deliveries')
    
    ax1.legend()
    ax1.set_xlabel('Longitude')
    ax1.set_ylabel('Latitude')
    
    # Map 2: Optimized routes
    ax2.set_title("Optimized Delivery Routes", fontsize=14, fontweight='bold')
    
    # Plot distribution centers
    distribution_centers.plot(ax=ax2, color='black', markersize=200, marker='s', alpha=0.8)
    
    # Plot routes for each center
    route_colors = ['red', 'blue', 'green']
    for i, (center_id, route_plan) in enumerate(route_plans.items()):
        route_coords = route_plan['route']
        
        # Create route line
        if len(route_coords) > 1:
            route_line = LineString(route_coords)
            route_gdf = gpd.GeoDataFrame([1], geometry=[route_line])
            route_gdf.plot(ax=ax2, color=route_colors[i], linewidth=3, alpha=0.7, 
                          label=f'{center_id} Route')
        
        # Plot delivery points
        for coord in route_coords[1:-1]:  # Exclude start/end (distribution center)
            ax2.scatter(coord[0], coord[1], color=route_colors[i], s=60, alpha=0.8)
    
    ax2.legend()
    ax2.set_xlabel('Longitude')
    ax2.set_ylabel('Latitude')
    
    # Chart 3: Performance comparison
    ax3.set_title("Distribution Center Performance Comparison", fontsize=14, fontweight='bold')
    
    x_pos = np.arange(len(performance_metrics))
    width = 0.35
    
    bars1 = ax3.bar(x_pos - width/2, performance_metrics['delivery_count'], width, 
                   label='Delivery Count', alpha=0.7, color='skyblue')
    
    ax3_twin = ax3.twinx()
    bars2 = ax3_twin.bar(x_pos + width/2, performance_metrics['total_distance_km'], width,
                        label='Total Distance (km)', alpha=0.7, color='lightcoral')
    
    ax3.set_xlabel('Distribution Centers')
    ax3.set_ylabel('Delivery Count', color='blue')
    ax3_twin.set_ylabel('Total Distance (km)', color='red')
    ax3.set_xticks(x_pos)
    ax3.set_xticklabels(performance_metrics['center_id'])
    
    # Add value labels
    for bar, value in zip(bars1, performance_metrics['delivery_count']):
        ax3.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1,
                f'{value}', ha='center', va='bottom', fontweight='bold')
    
    for bar, value in zip(bars2, performance_metrics['total_distance_km']):
        ax3_twin.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5,
                     f'{value:.1f}', ha='center', va='bottom', fontweight='bold')
    
    ax3.legend(loc='upper left')
    ax3_twin.legend(loc='upper right')
    
    # Chart 4: Priority distribution
    ax4.set_title("Delivery Priority Distribution", fontsize=14, fontweight='bold')
    
    priority_data = []
    centers = []
    for _, row in performance_metrics.iterrows():
        priority_data.append([row['premium_deliveries'], row['express_deliveries'], row['standard_deliveries']])
        centers.append(row['center_id'])
    
    priority_data = np.array(priority_data)
    
    bottom1 = np.zeros(len(centers))
    bottom2 = priority_data[:, 0]
    bottom3 = priority_data[:, 0] + priority_data[:, 1]
    
    ax4.bar(centers, priority_data[:, 0], label='Premium', color='gold', alpha=0.8)
    ax4.bar(centers, priority_data[:, 1], bottom=bottom2, label='Express', color='orange', alpha=0.8)
    ax4.bar(centers, priority_data[:, 2], bottom=bottom3, label='Standard', color='lightblue', alpha=0.8)
    
    ax4.set_xlabel('Distribution Centers')
    ax4.set_ylabel('Number of Deliveries')
    ax4.legend()
    
    plt.tight_layout()
    plt.savefig('last_mile_delivery_optimization.png', dpi=300, bbox_inches='tight')
    plt.show()

def generate_optimization_report(performance_metrics, route_plans, assignments):
    """Generate comprehensive optimization report."""
    print("\n" + "="*60)
    print("🚚 LAST-MILE DELIVERY OPTIMIZATION REPORT")
    print("="*60)
    
    # Overall summary
    total_deliveries = performance_metrics['delivery_count'].sum()
    total_distance = performance_metrics['total_distance_km'].sum()
    total_time = performance_metrics['total_time_minutes'].sum()
    
    print(f"\n📊 OVERALL PERFORMANCE SUMMARY:")
    print("-" * 40)
    print(f"Total Deliveries: {total_deliveries}")
    print(f"Total Distance: {total_distance:.1f} km")
    print(f"Total Time: {total_time:.0f} minutes ({total_time/60:.1f} hours)")
    print(f"Average Distance per Delivery: {total_distance/total_deliveries:.1f} km")
    print(f"Average Time per Delivery: {total_time/total_deliveries:.1f} minutes")
    
    # Distribution center performance
    print(f"\n🏢 DISTRIBUTION CENTER PERFORMANCE:")
    print("-" * 40)
    for _, center in performance_metrics.iterrows():
        print(f"\n{center['center_id']}:")
        print(f"  Deliveries: {center['delivery_count']}")
        print(f"  Route Distance: {center['total_distance_km']:.1f} km")
        print(f"  Route Time: {center['total_time_minutes']:.0f} minutes")
        print(f"  Avg Distance/Delivery: {center['avg_distance_per_delivery']:.1f} km")
        print(f"  Avg Time/Delivery: {center['avg_time_per_delivery']:.1f} minutes")
        print(f"  Priority Mix: {center['premium_deliveries']}P/{center['express_deliveries']}E/{center['standard_deliveries']}S")
    
    # Priority analysis
    priority_summary = assignments['priority'].value_counts()
    print(f"\n🎯 PRIORITY DISTRIBUTION:")
    print("-" * 40)
    for priority, count in priority_summary.items():
        percentage = (count / total_deliveries) * 100
        print(f"{priority.capitalize()}: {count} deliveries ({percentage:.1f}%)")
    
    # Optimization recommendations
    print(f"\n💡 OPTIMIZATION RECOMMENDATIONS:")
    print("-" * 40)
    
    # Find most efficient center
    performance_metrics['efficiency_score'] = (
        performance_metrics['delivery_count'] / performance_metrics['total_distance_km']
    )
    most_efficient = performance_metrics.loc[performance_metrics['efficiency_score'].idxmax()]
    
    recommendations = [
        f"1. ROUTE EFFICIENCY:",
        f"   • Most efficient center: {most_efficient['center_id']} ({most_efficient['efficiency_score']:.2f} deliveries/km)",
        f"   • Consider rebalancing delivery assignments to improve overall efficiency",
        f"   • Implement dynamic routing based on real-time traffic conditions",
        "",
        f"2. CAPACITY OPTIMIZATION:",
        f"   • Current utilization varies significantly across centers",
        f"   • Consider flexible staffing based on daily delivery volumes",
        f"   • Evaluate adding micro-fulfillment centers in high-density areas",
        "",
        f"3. DELIVERY WINDOWS:",
        f"   • Optimize time windows to reduce route complexity",
        f"   • Implement customer incentives for flexible delivery times",
        f"   • Consider evening delivery options for premium customers",
        "",
        f"4. TECHNOLOGY ENHANCEMENTS:",
        f"   • Implement real-time GPS tracking and route optimization",
        f"   • Use machine learning for demand forecasting",
        f"   • Deploy mobile apps for driver route guidance"
    ]
    
    for rec in recommendations:
        print(rec)
    
    return {
        'total_deliveries': total_deliveries,
        'total_distance': total_distance,
        'total_time': total_time,
        'efficiency_leader': most_efficient['center_id'],
        'recommendations': recommendations
    }

def main():
    """Main execution function."""
    print("🚚 LAST-MILE DELIVERY OPTIMIZATION ANALYSIS")
    print("=" * 50)
    print("Optimizing delivery routes for QuickDeliver Express")
    print("Los Angeles Metropolitan Area Operations")
    print()

    try:
        # Load data
        deliveries, distribution_centers, road_network = load_delivery_data()

        # Create network graph (simplified for this example)
        # network_graph = create_delivery_network(road_network)

        # Assign deliveries to centers
        assignments = assign_deliveries_to_centers(deliveries, distribution_centers)

        # Optimize routes (simplified without network graph for now)
        route_plans = optimize_delivery_routes(assignments, deliveries, distribution_centers, None)

        # Calculate service areas
        service_areas = calculate_service_areas(distribution_centers)

        # Analyze performance
        performance_metrics = analyze_delivery_performance(route_plans, assignments)

        # Visualize results
        visualize_delivery_optimization(deliveries, distribution_centers, assignments,
                                      route_plans, service_areas, performance_metrics)

        # Generate report
        optimization_report = generate_optimization_report(performance_metrics, route_plans, assignments)

        print(f"\n✅ Optimization complete! Check 'last_mile_delivery_optimization.png' for detailed visualizations.")

    except Exception as e:
        print(f"❌ Error during optimization: {e}")
        raise

if __name__ == "__main__":
    main()
