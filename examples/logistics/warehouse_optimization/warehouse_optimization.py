#!/usr/bin/env python3
"""
Warehouse Location Optimization Example

This example demonstrates how to use PyMapGIS for warehouse location optimization
in a logistics network. The scenario involves a retail distribution company
looking to optimize warehouse placement to minimize delivery costs and times.

Backstory:
---------
MegaRetail Corp operates a chain of stores across the Los Angeles metropolitan area.
They currently use multiple small warehouses but want to consolidate into 2-3 
strategically located facilities to reduce operational costs while maintaining
service levels. The company has identified 6 potential warehouse sites and needs
to determine the optimal combination based on:
- Customer demand volumes
- Delivery distances and times
- Facility costs and capacity
- Transportation network accessibility

Usage:
------
python warehouse_optimization.py

Requirements:
------------
- pymapgis
- geopandas
- networkx
- matplotlib
- folium
"""

import pymapgis as pmg
import geopandas as gpd
import pandas as pd
import numpy as np
from shapely.geometry import Point
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings('ignore')

def load_data():
    """Load customer and warehouse data from local files."""
    print("📦 Loading logistics data...")
    
    # Load customer locations with demand data
    customers = pmg.read("file://data/customer_locations.geojson")
    print(f"   ✓ Loaded {len(customers)} customer locations")
    
    # Load potential warehouse sites
    warehouses = pmg.read("file://data/potential_warehouses.geojson")
    print(f"   ✓ Loaded {len(warehouses)} potential warehouse sites")
    
    return customers, warehouses

def calculate_distances(customers, warehouses):
    """Calculate distances between all customers and potential warehouses."""
    print("📏 Calculating distances...")
    
    # Create distance matrix
    distances = {}
    
    for _, warehouse in warehouses.iterrows():
        wh_point = warehouse.geometry
        wh_id = warehouse['site_id']
        
        # Calculate distances to all customers
        customer_distances = []
        for _, customer in customers.iterrows():
            # Use geodesic distance (approximate)
            dist = wh_point.distance(customer.geometry) * 111  # Convert to km (rough approximation)
            customer_distances.append({
                'customer_id': customer['customer_id'],
                'warehouse_id': wh_id,
                'distance_km': dist,
                'demand_volume': customer['demand_volume']
            })
        
        distances[wh_id] = customer_distances
    
    return distances

def analyze_warehouse_efficiency(customers, warehouses, distances):
    """Analyze efficiency metrics for each warehouse."""
    print("📊 Analyzing warehouse efficiency...")
    
    efficiency_metrics = []
    
    for wh_id, wh_distances in distances.items():
        warehouse_info = warehouses[warehouses['site_id'] == wh_id].iloc[0]
        
        # Calculate weighted average distance (by demand volume)
        total_demand = sum(d['demand_volume'] for d in wh_distances)
        weighted_distance = sum(d['distance_km'] * d['demand_volume'] for d in wh_distances) / total_demand
        
        # Calculate cost efficiency
        monthly_cost = warehouse_info['monthly_cost']
        capacity = warehouse_info['capacity']
        cost_per_unit = monthly_cost / capacity
        
        # Calculate service coverage (customers within 25km)
        nearby_customers = len([d for d in wh_distances if d['distance_km'] <= 25])
        coverage_ratio = nearby_customers / len(customers)
        
        efficiency_metrics.append({
            'warehouse_id': wh_id,
            'name': warehouse_info['name'],
            'weighted_avg_distance': weighted_distance,
            'monthly_cost': monthly_cost,
            'capacity': capacity,
            'cost_per_unit': cost_per_unit,
            'coverage_ratio': coverage_ratio,
            'nearby_customers': nearby_customers,
            'efficiency_score': (coverage_ratio * 100) / (weighted_distance + cost_per_unit/1000)
        })
    
    return pd.DataFrame(efficiency_metrics)

def create_service_areas(warehouses, max_distance_km=25):
    """Create service area buffers around warehouses."""
    print("🗺️  Creating service area analysis...")
    
    # Create buffer zones (approximate service areas)
    # Note: This is a simplified approach using geographic buffers
    # In practice, you'd use network-based service areas
    
    warehouses_buffered = warehouses.copy()
    # Convert km to degrees (rough approximation: 1 degree ≈ 111 km)
    buffer_degrees = max_distance_km / 111
    warehouses_buffered['service_area'] = warehouses_buffered.geometry.buffer(buffer_degrees)
    
    return warehouses_buffered

def visualize_optimization_results(customers, warehouses, efficiency_df, service_areas):
    """Create comprehensive visualization of the optimization analysis."""
    print("📈 Creating optimization visualization...")
    
    # Create the main map
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(20, 16))
    
    # Map 1: Customer demand and warehouse locations
    ax1.set_title("Customer Locations and Demand Volume", fontsize=14, fontweight='bold')
    
    # Plot customers with size based on demand
    customers.plot(ax=ax1, 
                  markersize=customers['demand_volume']/50,
                  color='red', 
                  alpha=0.7,
                  label='Customers')
    
    # Plot potential warehouses
    warehouses.plot(ax=ax1, 
                   markersize=200,
                   color='blue',
                   marker='s',
                   alpha=0.8,
                   label='Potential Warehouses')
    
    # Add warehouse labels
    for _, row in warehouses.iterrows():
        ax1.annotate(row['site_id'], 
                    (row.geometry.x, row.geometry.y),
                    xytext=(5, 5), textcoords='offset points',
                    fontsize=8, fontweight='bold')
    
    ax1.legend()
    ax1.set_xlabel('Longitude')
    ax1.set_ylabel('Latitude')
    
    # Map 2: Service areas
    ax2.set_title("Warehouse Service Areas (25km radius)", fontsize=14, fontweight='bold')
    
    # Plot service areas
    service_areas_gdf = gpd.GeoDataFrame(service_areas)
    service_areas_gdf.set_geometry('service_area').plot(ax=ax2, 
                                                        alpha=0.3, 
                                                        color='lightblue',
                                                        edgecolor='blue')
    
    customers.plot(ax=ax2, markersize=30, color='red', alpha=0.7)
    warehouses.plot(ax=ax2, markersize=100, color='blue', marker='s')
    
    ax2.set_xlabel('Longitude')
    ax2.set_ylabel('Latitude')
    
    # Chart 3: Efficiency comparison
    ax3.set_title("Warehouse Efficiency Scores", fontsize=14, fontweight='bold')
    
    bars = ax3.bar(efficiency_df['warehouse_id'], efficiency_df['efficiency_score'], 
                   color='green', alpha=0.7)
    ax3.set_xlabel('Warehouse Site')
    ax3.set_ylabel('Efficiency Score')
    ax3.tick_params(axis='x', rotation=45)
    
    # Add value labels on bars
    for bar, score in zip(bars, efficiency_df['efficiency_score']):
        ax3.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1,
                f'{score:.1f}', ha='center', va='bottom', fontweight='bold')
    
    # Chart 4: Cost vs Coverage analysis
    ax4.set_title("Cost vs Coverage Analysis", fontsize=14, fontweight='bold')
    
    scatter = ax4.scatter(efficiency_df['coverage_ratio'] * 100, 
                         efficiency_df['monthly_cost'],
                         s=efficiency_df['capacity']/500,
                         c=efficiency_df['efficiency_score'],
                         cmap='RdYlGn',
                         alpha=0.7)
    
    # Add warehouse labels
    for _, row in efficiency_df.iterrows():
        ax4.annotate(row['warehouse_id'], 
                    (row['coverage_ratio'] * 100, row['monthly_cost']),
                    xytext=(5, 5), textcoords='offset points',
                    fontsize=8)
    
    ax4.set_xlabel('Coverage Ratio (%)')
    ax4.set_ylabel('Monthly Cost ($)')
    
    # Add colorbar
    cbar = plt.colorbar(scatter, ax=ax4)
    cbar.set_label('Efficiency Score')
    
    plt.tight_layout()
    plt.savefig('warehouse_optimization_analysis.png', dpi=300, bbox_inches='tight')
    plt.show()

def generate_recommendations(efficiency_df):
    """Generate optimization recommendations based on analysis."""
    print("\n" + "="*60)
    print("🎯 WAREHOUSE OPTIMIZATION RECOMMENDATIONS")
    print("="*60)
    
    # Sort by efficiency score
    top_warehouses = efficiency_df.sort_values('efficiency_score', ascending=False)
    
    print(f"\n📊 EFFICIENCY RANKING:")
    print("-" * 40)
    for i, (_, row) in enumerate(top_warehouses.iterrows(), 1):
        print(f"{i}. {row['warehouse_id']} - {row['name']}")
        print(f"   Efficiency Score: {row['efficiency_score']:.1f}")
        print(f"   Coverage: {row['coverage_ratio']*100:.1f}% of customers")
        print(f"   Avg Distance: {row['weighted_avg_distance']:.1f} km")
        print(f"   Monthly Cost: ${row['monthly_cost']:,}")
        print()
    
    # Recommend top 2-3 warehouses
    recommended = top_warehouses.head(3)
    total_cost = recommended['monthly_cost'].sum()
    avg_coverage = recommended['coverage_ratio'].mean()
    
    print(f"💡 RECOMMENDED SOLUTION:")
    print("-" * 40)
    print(f"Select top 3 warehouses: {', '.join(recommended['warehouse_id'].tolist())}")
    print(f"Total Monthly Cost: ${total_cost:,}")
    print(f"Average Coverage: {avg_coverage*100:.1f}%")
    print(f"Combined Efficiency Score: {recommended['efficiency_score'].mean():.1f}")
    
    return recommended

def main():
    """Main execution function."""
    print("🚛 WAREHOUSE LOCATION OPTIMIZATION ANALYSIS")
    print("=" * 50)
    print("Analyzing optimal warehouse placement for MegaRetail Corp")
    print("Los Angeles Metropolitan Area Distribution Network")
    print()
    
    try:
        # Load data
        customers, warehouses = load_data()
        
        # Calculate distances
        distances = calculate_distances(customers, warehouses)
        
        # Analyze efficiency
        efficiency_df = analyze_warehouse_efficiency(customers, warehouses, distances)
        
        # Create service areas
        service_areas = create_service_areas(warehouses)
        
        # Visualize results
        visualize_optimization_results(customers, warehouses, efficiency_df, service_areas)
        
        # Generate recommendations
        recommendations = generate_recommendations(efficiency_df)
        
        print(f"\n✅ Analysis complete! Check 'warehouse_optimization_analysis.png' for detailed visualizations.")
        
    except Exception as e:
        print(f"❌ Error during analysis: {e}")
        raise

if __name__ == "__main__":
    main()
