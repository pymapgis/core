"""
Simple Supply Chain Optimization Example using PyMapGIS

This example demonstrates:
1. Warehouse location optimization
2. Distribution network analysis
3. Cost minimization
4. Interactive visualization

Author: Nicholas Karlson
License: MIT
"""

import pandas as pd
import geopandas as gpd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import folium
from typing import List, Tuple, Dict, Optional
from dataclasses import dataclass
from sklearn.cluster import KMeans
from sklearn.metrics import pairwise_distances
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import json

# Try to import pymapgis, fallback to basic functionality if not available
try:
    import pymapgis as pmg
    PYMAPGIS_AVAILABLE = True
    print("✓ PyMapGIS loaded successfully")
except ImportError:
    PYMAPGIS_AVAILABLE = False
    print("⚠ PyMapGIS not available, using basic functionality")


@dataclass
class Location:
    """Represents a geographic location with coordinates and metadata."""
    name: str
    latitude: float
    longitude: float
    demand: float = 0.0
    capacity: float = 0.0
    cost_per_unit: float = 0.0


@dataclass
class SupplyChainSolution:
    """Represents a supply chain optimization solution."""
    warehouse_locations: List[Location]
    customer_assignments: Dict[str, str]
    total_cost: float
    total_distance: float
    utilization_rate: float


class SimpleSupplyChainOptimizer:
    """
    A simple supply chain optimizer that demonstrates basic optimization
    concepts using clustering and distance minimization.
    """
    
    def __init__(self, random_seed: int = 42):
        """Initialize the optimizer with a random seed for reproducibility."""
        self.random_seed = random_seed
        np.random.seed(random_seed)
        self.customers: List[Location] = []
        self.potential_warehouses: List[Location] = []
        self.solution: Optional[SupplyChainSolution] = None
        
    def generate_sample_data(self, 
                           num_customers: int = 50, 
                           num_potential_warehouses: int = 10,
                           region_bounds: Tuple[float, float, float, float] = (40.0, 45.0, -85.0, -75.0)):
        """
        Generate sample customer and warehouse location data.
        
        Args:
            num_customers: Number of customer locations to generate
            num_potential_warehouses: Number of potential warehouse locations
            region_bounds: (min_lat, max_lat, min_lon, max_lon) for the region
        """
        min_lat, max_lat, min_lon, max_lon = region_bounds
        
        # Generate customer locations
        self.customers = []
        for i in range(num_customers):
            lat = np.random.uniform(min_lat, max_lat)
            lon = np.random.uniform(min_lon, max_lon)
            demand = np.random.uniform(10, 100)  # Random demand between 10-100 units
            
            customer = Location(
                name=f"Customer_{i+1}",
                latitude=lat,
                longitude=lon,
                demand=demand
            )
            self.customers.append(customer)
        
        # Generate potential warehouse locations
        self.potential_warehouses = []
        for i in range(num_potential_warehouses):
            lat = np.random.uniform(min_lat, max_lat)
            lon = np.random.uniform(min_lon, max_lon)
            capacity = np.random.uniform(200, 500)  # Random capacity
            cost = np.random.uniform(1000, 5000)    # Random fixed cost
            
            warehouse = Location(
                name=f"Warehouse_{i+1}",
                latitude=lat,
                longitude=lon,
                capacity=capacity,
                cost_per_unit=cost
            )
            self.potential_warehouses.append(warehouse)
    
    def calculate_distance(self, loc1: Location, loc2: Location) -> float:
        """Calculate Euclidean distance between two locations (simplified)."""
        return np.sqrt((loc1.latitude - loc2.latitude)**2 + 
                      (loc1.longitude - loc2.longitude)**2)
    
    def optimize_warehouse_locations(self, num_warehouses: int = 3) -> SupplyChainSolution:
        """
        Optimize warehouse locations using K-means clustering.
        
        Args:
            num_warehouses: Number of warehouses to select
            
        Returns:
            SupplyChainSolution with optimized locations and assignments
        """
        if not self.customers:
            raise ValueError("No customer data available. Call generate_sample_data() first.")
        
        # Prepare customer coordinates for clustering
        customer_coords = np.array([[c.latitude, c.longitude] for c in self.customers])
        customer_demands = np.array([c.demand for c in self.customers])
        
        # Use K-means to find optimal warehouse locations
        kmeans = KMeans(n_clusters=num_warehouses, random_state=self.random_seed, n_init=10)
        cluster_labels = kmeans.fit_predict(customer_coords)
        
        # Create warehouse locations at cluster centers
        warehouse_locations = []
        for i, center in enumerate(kmeans.cluster_centers_):
            # Calculate required capacity for this cluster
            cluster_customers = [j for j, label in enumerate(cluster_labels) if label == i]
            required_capacity = sum(self.customers[j].demand for j in cluster_customers)
            
            warehouse = Location(
                name=f"Optimized_Warehouse_{i+1}",
                latitude=center[0],
                longitude=center[1],
                capacity=required_capacity * 1.2,  # 20% buffer
                cost_per_unit=2000 + required_capacity * 10  # Cost based on capacity
            )
            warehouse_locations.append(warehouse)
        
        # Assign customers to warehouses
        customer_assignments = {}
        for i, customer in enumerate(self.customers):
            assigned_warehouse = warehouse_locations[cluster_labels[i]]
            customer_assignments[customer.name] = assigned_warehouse.name
        
        # Calculate total cost and distance
        total_cost = 0
        total_distance = 0
        
        for i, customer in enumerate(self.customers):
            warehouse = warehouse_locations[cluster_labels[i]]
            distance = self.calculate_distance(customer, warehouse)
            cost = distance * 10 + customer.demand * 5  # Simplified cost calculation
            
            total_cost += cost
            total_distance += distance
        
        # Add warehouse fixed costs
        total_cost += sum(w.cost_per_unit for w in warehouse_locations)
        
        # Calculate utilization rate
        total_demand = sum(c.demand for c in self.customers)
        total_capacity = sum(w.capacity for w in warehouse_locations)
        utilization_rate = total_demand / total_capacity if total_capacity > 0 else 0
        
        self.solution = SupplyChainSolution(
            warehouse_locations=warehouse_locations,
            customer_assignments=customer_assignments,
            total_cost=total_cost,
            total_distance=total_distance,
            utilization_rate=utilization_rate
        )
        
        return self.solution
    
    def create_visualization(self, save_path: Optional[str] = None) -> folium.Map:
        """
        Create an interactive map visualization of the supply chain solution.
        
        Args:
            save_path: Optional path to save the HTML map
            
        Returns:
            Folium map object
        """
        if not self.solution:
            raise ValueError("No solution available. Call optimize_warehouse_locations() first.")
        
        # Calculate map center
        all_lats = [c.latitude for c in self.customers] + [w.latitude for w in self.solution.warehouse_locations]
        all_lons = [c.longitude for c in self.customers] + [w.longitude for w in self.solution.warehouse_locations]
        
        center_lat = np.mean(all_lats)
        center_lon = np.mean(all_lons)
        
        # Create base map
        m = folium.Map(
            location=[center_lat, center_lon],
            zoom_start=8,
            tiles='OpenStreetMap'
        )
        
        # Add warehouse locations
        for warehouse in self.solution.warehouse_locations:
            folium.Marker(
                location=[warehouse.latitude, warehouse.longitude],
                popup=f"""
                <b>{warehouse.name}</b><br>
                Capacity: {warehouse.capacity:.1f}<br>
                Cost: ${warehouse.cost_per_unit:.0f}
                """,
                icon=folium.Icon(color='red', icon='home', prefix='fa')
            ).add_to(m)
        
        # Add customer locations with color coding by assignment
        colors = ['blue', 'green', 'purple', 'orange', 'darkred', 'lightred', 
                 'beige', 'darkblue', 'darkgreen', 'cadetblue']
        
        warehouse_color_map = {w.name: colors[i % len(colors)] 
                              for i, w in enumerate(self.solution.warehouse_locations)}
        
        for customer in self.customers:
            assigned_warehouse = self.solution.customer_assignments[customer.name]
            color = warehouse_color_map[assigned_warehouse]
            
            folium.CircleMarker(
                location=[customer.latitude, customer.longitude],
                radius=max(3, customer.demand / 10),
                popup=f"""
                <b>{customer.name}</b><br>
                Demand: {customer.demand:.1f}<br>
                Assigned to: {assigned_warehouse}
                """,
                color=color,
                fill=True,
                fillColor=color,
                fillOpacity=0.6
            ).add_to(m)
        
        # Add title
        title_html = '''
        <h3 align="center" style="font-size:20px"><b>Supply Chain Optimization Results</b></h3>
        '''
        m.get_root().html.add_child(folium.Element(title_html))
        
        if save_path:
            m.save(save_path)
        
        return m
    
    def generate_report(self) -> Dict:
        """Generate a comprehensive report of the optimization results."""
        if not self.solution:
            raise ValueError("No solution available. Call optimize_warehouse_locations() first.")
        
        report = {
            "optimization_summary": {
                "total_customers": len(self.customers),
                "total_warehouses": len(self.solution.warehouse_locations),
                "total_cost": self.solution.total_cost,
                "total_distance": self.solution.total_distance,
                "utilization_rate": self.solution.utilization_rate,
                "average_cost_per_customer": self.solution.total_cost / len(self.customers),
                "average_distance_per_customer": self.solution.total_distance / len(self.customers)
            },
            "warehouse_details": [],
            "customer_assignments": self.solution.customer_assignments,
            "generated_at": datetime.now().isoformat()
        }
        
        # Add warehouse details
        for warehouse in self.solution.warehouse_locations:
            assigned_customers = [c for c in self.customers 
                                if self.solution.customer_assignments[c.name] == warehouse.name]
            total_demand = sum(c.demand for c in assigned_customers)
            
            warehouse_info = {
                "name": warehouse.name,
                "location": {"latitude": warehouse.latitude, "longitude": warehouse.longitude},
                "capacity": warehouse.capacity,
                "cost": warehouse.cost_per_unit,
                "assigned_customers": len(assigned_customers),
                "total_demand_served": total_demand,
                "utilization": total_demand / warehouse.capacity if warehouse.capacity > 0 else 0
            }
            report["warehouse_details"].append(warehouse_info)
        
        return report


def main():
    """Main function to demonstrate the supply chain optimizer."""
    print("🚚 Simple Supply Chain Optimization Demo")
    print("=" * 50)
    
    # Initialize optimizer
    optimizer = SimpleSupplyChainOptimizer(random_seed=42)
    
    # Generate sample data
    print("📍 Generating sample customer and warehouse data...")
    optimizer.generate_sample_data(
        num_customers=30,
        num_potential_warehouses=8,
        region_bounds=(40.0, 45.0, -85.0, -75.0)  # Great Lakes region
    )
    
    # Optimize warehouse locations
    print("🔧 Optimizing warehouse locations...")
    solution = optimizer.optimize_warehouse_locations(num_warehouses=3)
    
    # Generate report
    print("📊 Generating optimization report...")
    report = optimizer.generate_report()
    
    # Print summary
    print("\n📈 Optimization Results:")
    print(f"  • Total Cost: ${report['optimization_summary']['total_cost']:,.2f}")
    print(f"  • Total Distance: {report['optimization_summary']['total_distance']:.2f} units")
    print(f"  • Utilization Rate: {report['optimization_summary']['utilization_rate']:.1%}")
    print(f"  • Average Cost per Customer: ${report['optimization_summary']['average_cost_per_customer']:,.2f}")
    
    print("\n🏭 Warehouse Details:")
    for warehouse_info in report['warehouse_details']:
        print(f"  • {warehouse_info['name']}: "
              f"{warehouse_info['assigned_customers']} customers, "
              f"{warehouse_info['utilization']:.1%} utilization")
    
    # Create visualization
    print("🗺️  Creating interactive map...")
    map_obj = optimizer.create_visualization(save_path="supply_chain_map.html")
    print("   Map saved as 'supply_chain_map.html'")
    
    # Save report
    with open("optimization_report.json", "w") as f:
        json.dump(report, f, indent=2)
    print("   Report saved as 'optimization_report.json'")
    
    print("\n✅ Demo completed successfully!")
    return optimizer, solution, report


if __name__ == "__main__":
    main()
