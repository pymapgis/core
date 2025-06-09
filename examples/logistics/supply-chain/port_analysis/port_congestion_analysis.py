#!/usr/bin/env python3
"""
Port Congestion Analysis Example

This example demonstrates how to use PyMapGIS for comprehensive port congestion
analysis and alternative route planning. The analysis evaluates port efficiency,
capacity utilization, and transportation infrastructure to optimize shipping
logistics and reduce supply chain bottlenecks.

Backstory:
---------
Pacific Shipping Logistics is a major container shipping company operating along
the US West Coast. Recent supply chain disruptions have highlighted critical
bottlenecks at major ports, causing significant delays and increased costs.

The company needs to:
1. Analyze congestion levels across their port network
2. Identify alternative routing options during peak congestion
3. Evaluate transportation infrastructure capacity and utilization
4. Optimize vessel scheduling and port allocation
5. Develop contingency plans for supply chain resilience

The analysis covers 8 major ports from San Diego to Vancouver, examining:
- Port capacity and throughput metrics
- Congestion indices and wait times
- Rail and highway connectivity
- Shipping route efficiency and reliability
- Infrastructure bottlenecks and expansion plans

Usage:
------
python port_congestion_analysis.py

Requirements:
------------
- pymapgis
- geopandas
- pandas
- matplotlib
- seaborn
- networkx
"""

import pymapgis as pmg
import geopandas as gpd
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from shapely.geometry import Point, LineString
import warnings
warnings.filterwarnings('ignore')

def load_port_data():
    """Load port, shipping route, and infrastructure data."""
    print("🚢 Loading port congestion analysis data...")
    
    # Load port information
    ports = pmg.read("file://data/ports.geojson")
    print(f"   ✓ Loaded {len(ports)} ports")
    
    # Load shipping routes
    shipping_routes = pmg.read("file://data/shipping_routes.geojson")
    print(f"   ✓ Loaded {len(shipping_routes)} shipping routes")
    
    # Load transportation infrastructure
    infrastructure = pmg.read("file://data/transportation_infrastructure.geojson")
    print(f"   ✓ Loaded {len(infrastructure)} infrastructure elements")
    
    return ports, shipping_routes, infrastructure

def analyze_port_congestion(ports):
    """Analyze congestion levels and efficiency metrics for each port."""
    print("📊 Analyzing port congestion and efficiency...")
    
    congestion_analysis = []
    
    for _, port in ports.iterrows():
        # Calculate capacity utilization
        theoretical_capacity = port['berth_count'] * 200000  # Assume 200k TEU per berth annually
        capacity_utilization = port['annual_teu'] / theoretical_capacity
        
        # Calculate efficiency score (inverse of congestion and wait time)
        efficiency_score = (
            (1 - port['congestion_index']) * 0.4 +
            port['operational_efficiency'] * 0.3 +
            (1 - min(port['avg_wait_time_hours'] / 24, 1)) * 0.3
        )
        
        # Determine congestion level
        if port['congestion_index'] >= 0.7:
            congestion_level = 'Critical'
        elif port['congestion_index'] >= 0.5:
            congestion_level = 'High'
        elif port['congestion_index'] >= 0.3:
            congestion_level = 'Moderate'
        else:
            congestion_level = 'Low'
        
        # Calculate infrastructure connectivity score
        connectivity_score = (
            port['rail_connections'] * 0.4 +
            port['highway_connections'] * 0.3 +
            min(port['storage_capacity_teu'] / 500000, 1) * 0.3
        )
        
        congestion_analysis.append({
            'port_id': port['port_id'],
            'name': port['name'],
            'annual_teu': port['annual_teu'],
            'congestion_index': port['congestion_index'],
            'congestion_level': congestion_level,
            'avg_wait_time_hours': port['avg_wait_time_hours'],
            'capacity_utilization': capacity_utilization,
            'efficiency_score': efficiency_score,
            'connectivity_score': connectivity_score,
            'operational_efficiency': port['operational_efficiency'],
            'berth_count': port['berth_count'],
            'storage_capacity_teu': port['storage_capacity_teu']
        })
    
    return pd.DataFrame(congestion_analysis)

def evaluate_shipping_routes(shipping_routes, ports):
    """Evaluate shipping route performance and identify bottlenecks."""
    print("🛳️  Evaluating shipping route performance...")
    
    route_analysis = []
    
    for _, route in shipping_routes.iterrows():
        # Get origin port information
        origin_port = ports[ports['port_id'] == route['origin_port']].iloc[0]
        
        # Calculate route efficiency metrics
        daily_capacity = (route['frequency_per_week'] / 7) * route['vessel_capacity_avg']
        utilization_rate = route['annual_volume_teu'] / (daily_capacity * 365)
        
        # Calculate delay risk based on origin port congestion
        delay_risk = origin_port['congestion_index'] * (1 - route['route_reliability'])
        
        # Determine route status
        if utilization_rate >= 0.9:
            route_status = 'Overcapacity'
        elif utilization_rate >= 0.75:
            route_status = 'High Utilization'
        elif utilization_rate >= 0.5:
            route_status = 'Moderate Utilization'
        else:
            route_status = 'Underutilized'
        
        route_analysis.append({
            'route_id': route['route_id'],
            'name': route['name'],
            'origin_port': route['origin_port'],
            'destination_region': route['destination_region'],
            'annual_volume_teu': route['annual_volume_teu'],
            'avg_transit_days': route['avg_transit_days'],
            'frequency_per_week': route['frequency_per_week'],
            'route_reliability': route['route_reliability'],
            'utilization_rate': utilization_rate,
            'delay_risk': delay_risk,
            'route_status': route_status,
            'daily_capacity': daily_capacity
        })
    
    return pd.DataFrame(route_analysis)

def analyze_infrastructure_bottlenecks(infrastructure, ports):
    """Analyze transportation infrastructure capacity and bottlenecks."""
    print("🚛 Analyzing infrastructure bottlenecks...")
    
    infrastructure_analysis = []
    
    for _, infra in infrastructure.iterrows():
        # Calculate bottleneck severity
        utilization = infra['current_utilization']
        
        if utilization >= 0.9:
            bottleneck_severity = 'Critical'
        elif utilization >= 0.75:
            bottleneck_severity = 'High'
        elif utilization >= 0.6:
            bottleneck_severity = 'Moderate'
        else:
            bottleneck_severity = 'Low'
        
        # Calculate capacity buffer
        capacity_buffer = 1 - utilization
        
        # Determine maintenance priority
        maintenance_priority = {
            'poor': 'High',
            'fair': 'Medium',
            'good': 'Low',
            'excellent': 'Low'
        }.get(infra['maintenance_status'], 'Medium')
        
        infrastructure_analysis.append({
            'infra_id': infra['infra_id'],
            'name': infra['name'],
            'type': infra['type'],
            'current_utilization': utilization,
            'capacity_buffer': capacity_buffer,
            'bottleneck_severity': bottleneck_severity,
            'maintenance_status': infra['maintenance_status'],
            'maintenance_priority': maintenance_priority,
            'expansion_planned': infra['expansion_planned'],
            'connected_ports': infra.get('connected_ports', [])
        })
    
    return pd.DataFrame(infrastructure_analysis)

def identify_alternative_routes(ports, congestion_analysis, route_analysis):
    """Identify alternative routing options during congestion."""
    print("🔄 Identifying alternative routing options...")
    
    # Find low-congestion ports that could serve as alternatives
    low_congestion_ports = congestion_analysis[
        congestion_analysis['congestion_level'].isin(['Low', 'Moderate'])
    ].sort_values('efficiency_score', ascending=False)
    
    # Find high-congestion routes that need alternatives
    problematic_routes = route_analysis[
        route_analysis['route_status'].isin(['Overcapacity', 'High Utilization'])
    ]
    
    alternative_recommendations = []
    
    for _, route in problematic_routes.iterrows():
        origin_port_info = congestion_analysis[
            congestion_analysis['port_id'] == route['origin_port']
        ].iloc[0]
        
        # Find nearby alternative ports (simplified distance calculation)
        origin_coords = ports[ports['port_id'] == route['origin_port']].iloc[0].geometry
        
        alternatives = []
        for _, alt_port in low_congestion_ports.iterrows():
            alt_coords = ports[ports['port_id'] == alt_port['port_id']].iloc[0].geometry
            distance = origin_coords.distance(alt_coords) * 111  # Convert to km
            
            if distance <= 500:  # Within 500km
                alternatives.append({
                    'port_id': alt_port['port_id'],
                    'name': alt_port['name'],
                    'distance_km': distance,
                    'efficiency_score': alt_port['efficiency_score'],
                    'congestion_level': alt_port['congestion_level']
                })
        
        # Sort alternatives by efficiency and distance
        alternatives = sorted(alternatives, 
                            key=lambda x: (x['efficiency_score'], -x['distance_km']), 
                            reverse=True)
        
        alternative_recommendations.append({
            'problematic_route': route['name'],
            'origin_port': route['origin_port'],
            'current_congestion': origin_port_info['congestion_level'],
            'alternatives': alternatives[:3]  # Top 3 alternatives
        })
    
    return alternative_recommendations

def calculate_congestion_costs(congestion_analysis, route_analysis):
    """Calculate economic impact of port congestion."""
    print("💰 Calculating congestion cost impact...")
    
    # Cost assumptions (per TEU)
    BASE_HANDLING_COST = 150  # USD per TEU
    DELAY_COST_PER_HOUR = 25  # USD per TEU per hour
    CONGESTION_MULTIPLIER = {
        'Low': 1.0,
        'Moderate': 1.2,
        'High': 1.5,
        'Critical': 2.0
    }
    
    cost_analysis = []
    
    for _, port in congestion_analysis.iterrows():
        # Calculate base costs
        base_cost = port['annual_teu'] * BASE_HANDLING_COST
        
        # Calculate delay costs
        delay_cost = (port['annual_teu'] * 
                     port['avg_wait_time_hours'] * 
                     DELAY_COST_PER_HOUR)
        
        # Calculate congestion premium
        congestion_multiplier = CONGESTION_MULTIPLIER[port['congestion_level']]
        congestion_premium = base_cost * (congestion_multiplier - 1)
        
        # Total cost impact
        total_cost = base_cost + delay_cost + congestion_premium
        
        cost_analysis.append({
            'port_id': port['port_id'],
            'name': port['name'],
            'annual_teu': port['annual_teu'],
            'base_cost_millions': base_cost / 1_000_000,
            'delay_cost_millions': delay_cost / 1_000_000,
            'congestion_premium_millions': congestion_premium / 1_000_000,
            'total_cost_millions': total_cost / 1_000_000,
            'cost_per_teu': total_cost / port['annual_teu']
        })
    
    return pd.DataFrame(cost_analysis)

def visualize_port_analysis(ports, congestion_analysis, route_analysis, infrastructure, cost_analysis, shipping_routes):
    """Create comprehensive port congestion analysis visualizations."""
    print("📈 Creating port analysis visualizations...")

    # Create figure with subplots
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(20, 16))

    # Map 1: Port congestion levels
    ax1.set_title("Port Congestion Levels and Shipping Routes", fontsize=14, fontweight='bold')

    # Plot shipping routes
    shipping_routes.plot(ax=ax1, color='lightblue', alpha=0.6, linewidth=2)
    
    # Plot ports with congestion color coding
    congestion_colors = {'Low': 'green', 'Moderate': 'yellow', 'High': 'orange', 'Critical': 'red'}
    for level, color in congestion_colors.items():
        level_ports = congestion_analysis[congestion_analysis['congestion_level'] == level]
        if not level_ports.empty:
            port_points = ports[ports['port_id'].isin(level_ports['port_id'])]
            port_points.plot(ax=ax1, color=color, markersize=100, alpha=0.8, 
                           label=f'{level} Congestion')
    
    # Add port labels
    for _, port in ports.iterrows():
        ax1.annotate(port['port_id'], 
                    (port.geometry.x, port.geometry.y),
                    xytext=(5, 5), textcoords='offset points',
                    fontsize=8, fontweight='bold')
    
    ax1.legend()
    ax1.set_xlabel('Longitude')
    ax1.set_ylabel('Latitude')
    
    # Chart 2: Efficiency vs Congestion scatter plot
    ax2.set_title("Port Efficiency vs Congestion Analysis", fontsize=14, fontweight='bold')
    
    scatter = ax2.scatter(congestion_analysis['congestion_index'], 
                         congestion_analysis['efficiency_score'],
                         s=congestion_analysis['annual_teu']/50000,
                         c=congestion_analysis['avg_wait_time_hours'],
                         cmap='Reds', alpha=0.7)
    
    # Add port labels
    for _, port in congestion_analysis.iterrows():
        ax2.annotate(port['port_id'], 
                    (port['congestion_index'], port['efficiency_score']),
                    xytext=(5, 5), textcoords='offset points',
                    fontsize=8)
    
    ax2.set_xlabel('Congestion Index')
    ax2.set_ylabel('Efficiency Score')
    
    # Add colorbar
    cbar = plt.colorbar(scatter, ax=ax2)
    cbar.set_label('Average Wait Time (hours)')
    
    # Chart 3: Infrastructure utilization
    ax3.set_title("Infrastructure Utilization and Bottlenecks", fontsize=14, fontweight='bold')
    
    infra_analysis = analyze_infrastructure_bottlenecks(infrastructure, ports)
    
    # Group by type and calculate average utilization
    infra_by_type = infra_analysis.groupby('type')['current_utilization'].mean()
    
    bars = ax3.bar(infra_by_type.index, infra_by_type.values, 
                   color=['skyblue', 'lightcoral', 'lightgreen'], alpha=0.7)
    
    # Add utilization threshold lines
    ax3.axhline(y=0.75, color='orange', linestyle='--', alpha=0.7, label='High Utilization (75%)')
    ax3.axhline(y=0.9, color='red', linestyle='--', alpha=0.7, label='Critical Utilization (90%)')
    
    ax3.set_xlabel('Infrastructure Type')
    ax3.set_ylabel('Average Utilization')
    ax3.legend()
    
    # Add value labels on bars
    for bar, value in zip(bars, infra_by_type.values):
        ax3.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.02,
                f'{value:.1%}', ha='center', va='bottom', fontweight='bold')
    
    # Chart 4: Cost impact analysis
    ax4.set_title("Congestion Cost Impact by Port", fontsize=14, fontweight='bold')
    
    # Create stacked bar chart
    x_pos = np.arange(len(cost_analysis))
    width = 0.6
    
    bars1 = ax4.bar(x_pos, cost_analysis['base_cost_millions'], width, 
                   label='Base Costs', alpha=0.8, color='lightblue')
    bars2 = ax4.bar(x_pos, cost_analysis['delay_cost_millions'], width,
                   bottom=cost_analysis['base_cost_millions'],
                   label='Delay Costs', alpha=0.8, color='orange')
    bars3 = ax4.bar(x_pos, cost_analysis['congestion_premium_millions'], width,
                   bottom=cost_analysis['base_cost_millions'] + cost_analysis['delay_cost_millions'],
                   label='Congestion Premium', alpha=0.8, color='red')
    
    ax4.set_xlabel('Ports')
    ax4.set_ylabel('Annual Cost (Millions USD)')
    ax4.set_xticks(x_pos)
    ax4.set_xticklabels(cost_analysis['port_id'], rotation=45)
    ax4.legend()
    
    plt.tight_layout()
    plt.savefig('port_congestion_analysis.png', dpi=300, bbox_inches='tight')
    plt.show()

def generate_congestion_report(congestion_analysis, route_analysis, alternative_recommendations, cost_analysis):
    """Generate comprehensive congestion analysis report."""
    print("\n" + "="*70)
    print("🚢 PORT CONGESTION ANALYSIS REPORT")
    print("="*70)
    
    # Overall summary
    total_teu = congestion_analysis['annual_teu'].sum()
    avg_congestion = congestion_analysis['congestion_index'].mean()
    total_cost = cost_analysis['total_cost_millions'].sum()
    
    print(f"\n📊 OVERALL NETWORK SUMMARY:")
    print("-" * 50)
    print(f"Total Annual Volume: {total_teu:,} TEU")
    print(f"Average Congestion Index: {avg_congestion:.2f}")
    print(f"Total Annual Cost Impact: ${total_cost:.1f} million")
    print(f"Average Cost per TEU: ${total_cost*1_000_000/total_teu:.0f}")
    
    # Congestion hotspots
    critical_ports = congestion_analysis[congestion_analysis['congestion_level'] == 'Critical']
    high_congestion_ports = congestion_analysis[congestion_analysis['congestion_level'] == 'High']
    
    print(f"\n🚨 CONGESTION HOTSPOTS:")
    print("-" * 50)
    
    if not critical_ports.empty:
        print("CRITICAL CONGESTION:")
        for _, port in critical_ports.iterrows():
            print(f"• {port['name']}: {port['congestion_index']:.2f} index, {port['avg_wait_time_hours']:.0f}h wait")
    
    if not high_congestion_ports.empty:
        print("\nHIGH CONGESTION:")
        for _, port in high_congestion_ports.iterrows():
            print(f"• {port['name']}: {port['congestion_index']:.2f} index, {port['avg_wait_time_hours']:.0f}h wait")
    
    # Route performance
    problematic_routes = route_analysis[route_analysis['route_status'].isin(['Overcapacity', 'High Utilization'])]
    
    print(f"\n🛳️  ROUTE PERFORMANCE ISSUES:")
    print("-" * 50)
    for _, route in problematic_routes.iterrows():
        print(f"• {route['name']}: {route['route_status']}")
        print(f"  Utilization: {route['utilization_rate']:.1%}, Delay Risk: {route['delay_risk']:.2f}")
    
    # Alternative routing recommendations
    print(f"\n🔄 ALTERNATIVE ROUTING RECOMMENDATIONS:")
    print("-" * 50)
    for rec in alternative_recommendations:
        print(f"\nProblematic Route: {rec['problematic_route']}")
        print(f"Current Port: {rec['origin_port']} ({rec['current_congestion']} congestion)")
        print("Recommended Alternatives:")
        for i, alt in enumerate(rec['alternatives'][:2], 1):
            print(f"  {i}. {alt['name']} - {alt['congestion_level']} congestion, {alt['distance_km']:.0f}km away")
    
    # Cost impact
    highest_cost_ports = cost_analysis.nlargest(3, 'total_cost_millions')
    
    print(f"\n💰 HIGHEST COST IMPACT PORTS:")
    print("-" * 50)
    for _, port in highest_cost_ports.iterrows():
        print(f"• {port['name']}: ${port['total_cost_millions']:.1f}M annually")
        print(f"  Base: ${port['base_cost_millions']:.1f}M, Delays: ${port['delay_cost_millions']:.1f}M, Premium: ${port['congestion_premium_millions']:.1f}M")
    
    # Recommendations
    print(f"\n💡 STRATEGIC RECOMMENDATIONS:")
    print("-" * 50)
    
    recommendations = [
        "1. IMMEDIATE ACTIONS:",
        f"   • Implement dynamic routing for {len(problematic_routes)} congested routes",
        f"   • Increase off-peak operations at critical congestion ports",
        f"   • Deploy additional resources to ports with >18h wait times",
        "",
        "2. CAPACITY EXPANSION:",
        f"   • Prioritize infrastructure expansion at high-utilization facilities",
        f"   • Develop alternative port capacity in low-congestion regions",
        f"   • Invest in automation to improve operational efficiency",
        "",
        "3. NETWORK OPTIMIZATION:",
        f"   • Redistribute volume from critical to moderate congestion ports",
        f"   • Implement vessel scheduling coordination across port network",
        f"   • Develop contingency routing protocols for peak periods",
        "",
        "4. COST MITIGATION:",
        f"   • Potential savings of ${total_cost*0.2:.1f}M annually through optimization",
        f"   • Implement congestion pricing to balance demand",
        f"   • Negotiate flexible berthing agreements with port authorities"
    ]
    
    for rec in recommendations:
        print(rec)
    
    return {
        'total_volume': total_teu,
        'avg_congestion': avg_congestion,
        'total_cost': total_cost,
        'critical_ports': len(critical_ports),
        'problematic_routes': len(problematic_routes),
        'recommendations': recommendations
    }

def main():
    """Main execution function."""
    print("🚢 PORT CONGESTION ANALYSIS")
    print("=" * 50)
    print("Analyzing port efficiency and congestion for Pacific Shipping Logistics")
    print("US West Coast Port Network Optimization")
    print()
    
    try:
        # Load data
        ports, shipping_routes, infrastructure = load_port_data()
        
        # Analyze port congestion
        congestion_analysis = analyze_port_congestion(ports)
        
        # Evaluate shipping routes
        route_analysis = evaluate_shipping_routes(shipping_routes, ports)
        
        # Identify alternative routes
        alternative_recommendations = identify_alternative_routes(ports, congestion_analysis, route_analysis)
        
        # Calculate cost impact
        cost_analysis = calculate_congestion_costs(congestion_analysis, route_analysis)
        
        # Visualize results
        visualize_port_analysis(ports, congestion_analysis, route_analysis, infrastructure, cost_analysis, shipping_routes)
        
        # Generate report
        congestion_report = generate_congestion_report(congestion_analysis, route_analysis, 
                                                     alternative_recommendations, cost_analysis)
        
        print(f"\n✅ Analysis complete! Check 'port_congestion_analysis.png' for detailed visualizations.")
        
    except Exception as e:
        print(f"❌ Error during analysis: {e}")
        raise

if __name__ == "__main__":
    main()
