# 🛣️ Route Optimization

## Comprehensive Guide to Route Optimization with PyMapGIS

This guide provides complete coverage of route optimization techniques, algorithms, and implementations for logistics and supply chain applications.

### 1. Route Optimization Fundamentals

#### The Vehicle Routing Problem (VRP)
The Vehicle Routing Problem is a combinatorial optimization challenge that seeks to find optimal routes for a fleet of vehicles to serve a set of customers while minimizing total cost and satisfying various constraints.

**Basic VRP Components:**
- **Depot**: Starting and ending point for vehicles
- **Customers**: Locations requiring service or delivery
- **Vehicles**: Fleet with specific capacities and characteristics
- **Constraints**: Capacity, time windows, driver hours, etc.
- **Objective**: Minimize cost, distance, time, or maximize service

#### Mathematical Formulation
```
Minimize: Σ(i,j) c_ij * x_ij
Subject to:
- Σ_j x_ij = 1 for all customers i
- Σ_i x_ij = 1 for all customers j  
- Vehicle capacity constraints
- Time window constraints
- Route continuity constraints
```

### 2. VRP Variants and Classifications

#### Capacitated VRP (CVRP)
**Description**: Vehicles have limited capacity for weight, volume, or item count.

```python
import pymapgis as pmg

# Define vehicles with capacity constraints
vehicles = [
    {'id': 'TRUCK-001', 'capacity_kg': 5000, 'capacity_m3': 25},
    {'id': 'VAN-001', 'capacity_kg': 2000, 'capacity_m3': 12}
]

# Define customers with demands
customers = pmg.read_csv('customers.csv')  # includes demand_kg, demand_m3

# Solve CVRP
optimizer = pmg.RouteOptimizer(problem_type='CVRP')
routes = optimizer.solve(
    customers=customers,
    vehicles=vehicles,
    depot_location=(40.7128, -74.0060)
)
```

#### VRP with Time Windows (VRPTW)
**Description**: Customers must be served within specific time intervals.

```python
# Customers with time windows
customers_tw = pmg.read_csv('customers_with_time_windows.csv')
# Columns: customer_id, lat, lon, demand, earliest_time, latest_time, service_time

# Solve VRPTW
optimizer = pmg.RouteOptimizer(problem_type='VRPTW')
routes = optimizer.solve(
    customers=customers_tw,
    vehicles=vehicles,
    depot_location=(40.7128, -74.0060),
    start_time='08:00',
    max_route_duration=480  # 8 hours in minutes
)
```

#### Multi-Depot VRP (MDVRP)
**Description**: Multiple depots serve customers, optimizing depot assignment and routing.

```python
# Multiple depot locations
depots = [
    {'id': 'DEPOT-NORTH', 'location': (40.7589, -73.9851), 'capacity': 10},
    {'id': 'DEPOT-SOUTH', 'location': (40.6892, -74.0445), 'capacity': 8}
]

# Solve MDVRP
optimizer = pmg.RouteOptimizer(problem_type='MDVRP')
routes = optimizer.solve(
    customers=customers,
    vehicles=vehicles,
    depots=depots
)
```

#### Pickup and Delivery Problem (PDP)
**Description**: Items must be picked up from one location and delivered to another.

```python
# Pickup and delivery pairs
pickup_delivery = pmg.read_csv('pickup_delivery.csv')
# Columns: pair_id, pickup_lat, pickup_lon, delivery_lat, delivery_lon, 
#          pickup_time_window, delivery_time_window, item_weight

# Solve PDP
optimizer = pmg.RouteOptimizer(problem_type='PDP')
routes = optimizer.solve(
    pickup_delivery_pairs=pickup_delivery,
    vehicles=vehicles,
    depot_location=(40.7128, -74.0060)
)
```

### 3. Optimization Algorithms

#### Exact Algorithms

**Branch and Bound**
```python
# For small problems (< 20 customers)
optimizer = pmg.RouteOptimizer(
    algorithm='branch_and_bound',
    time_limit=3600,  # 1 hour maximum
    optimality_gap=0.01  # 1% gap tolerance
)

routes = optimizer.solve(customers, vehicles, depot_location)
print(f"Optimal solution found: {optimizer.is_optimal()}")
print(f"Optimality gap: {optimizer.get_gap():.2%}")
```

**Integer Linear Programming (ILP)**
```python
# Using commercial solvers (Gurobi, CPLEX)
optimizer = pmg.RouteOptimizer(
    algorithm='ilp',
    solver='gurobi',
    time_limit=7200,  # 2 hours
    mip_gap=0.05  # 5% gap tolerance
)

routes = optimizer.solve(customers, vehicles, depot_location)
```

#### Heuristic Algorithms

**Nearest Neighbor Heuristic**
```python
# Fast construction heuristic
optimizer = pmg.RouteOptimizer(algorithm='nearest_neighbor')
routes = optimizer.solve(customers, vehicles, depot_location)

# Good for initial solutions or real-time applications
print(f"Solution time: {optimizer.solve_time:.2f} seconds")
```

**Savings Algorithm (Clarke-Wright)**
```python
# Classic savings-based construction
optimizer = pmg.RouteOptimizer(
    algorithm='clarke_wright',
    savings_factor=1.0,  # Weight for distance savings
    route_shape_factor=0.1  # Penalty for route shape
)

routes = optimizer.solve(customers, vehicles, depot_location)
```

**Sweep Algorithm**
```python
# Polar coordinate-based construction
optimizer = pmg.RouteOptimizer(
    algorithm='sweep',
    sweep_direction='clockwise',
    starting_angle=0  # Start from east (0 degrees)
)

routes = optimizer.solve(customers, vehicles, depot_location)
```

#### Metaheuristic Algorithms

**Genetic Algorithm**
```python
# Evolutionary optimization
optimizer = pmg.RouteOptimizer(
    algorithm='genetic_algorithm',
    population_size=100,
    max_generations=500,
    crossover_rate=0.8,
    mutation_rate=0.1,
    elite_size=10
)

routes = optimizer.solve(customers, vehicles, depot_location)
```

**Simulated Annealing**
```python
# Probabilistic local search
optimizer = pmg.RouteOptimizer(
    algorithm='simulated_annealing',
    initial_temperature=1000,
    cooling_rate=0.95,
    min_temperature=1,
    max_iterations=10000
)

routes = optimizer.solve(customers, vehicles, depot_location)
```

**Tabu Search**
```python
# Memory-based local search
optimizer = pmg.RouteOptimizer(
    algorithm='tabu_search',
    tabu_tenure=7,
    max_iterations=1000,
    aspiration_criterion='best_solution'
)

routes = optimizer.solve(customers, vehicles, depot_location)
```

**Variable Neighborhood Search (VNS)**
```python
# Multiple neighborhood exploration
optimizer = pmg.RouteOptimizer(
    algorithm='vns',
    neighborhoods=['2-opt', '3-opt', 'or-opt', 'cross-exchange'],
    max_iterations=500,
    local_search='best_improvement'
)

routes = optimizer.solve(customers, vehicles, depot_location)
```

### 4. Local Search Improvements

#### 2-opt Improvement
```python
# Edge exchange within routes
def two_opt_improvement(route):
    """Improve route using 2-opt edge exchanges."""
    improved = True
    while improved:
        improved = False
        for i in range(1, len(route) - 2):
            for j in range(i + 1, len(route)):
                if j - i == 1: continue  # Skip adjacent edges
                
                # Calculate improvement
                current_distance = (
                    distance(route[i-1], route[i]) + 
                    distance(route[j-1], route[j])
                )
                new_distance = (
                    distance(route[i-1], route[j-1]) + 
                    distance(route[i], route[j])
                )
                
                if new_distance < current_distance:
                    # Reverse segment between i and j-1
                    route[i:j] = route[i:j][::-1]
                    improved = True
                    break
            if improved:
                break
    return route

# Apply to all routes
improved_routes = [two_opt_improvement(route) for route in routes]
```

#### Or-opt Improvement
```python
# Relocate sequences of customers
def or_opt_improvement(route, max_sequence_length=3):
    """Improve route by relocating customer sequences."""
    improved = True
    while improved:
        improved = False
        for seq_len in range(1, min(max_sequence_length + 1, len(route) - 1)):
            for i in range(1, len(route) - seq_len):
                for j in range(1, len(route) - seq_len + 1):
                    if abs(i - j) <= seq_len: continue
                    
                    # Calculate improvement
                    if is_improvement(route, i, i + seq_len, j):
                        # Relocate sequence
                        sequence = route[i:i + seq_len]
                        del route[i:i + seq_len]
                        route[j:j] = sequence
                        improved = True
                        break
                if improved:
                    break
            if improved:
                break
    return route
```

#### Cross-exchange (2-opt*)
```python
# Exchange segments between different routes
def cross_exchange(route1, route2):
    """Exchange segments between two routes."""
    best_improvement = 0
    best_exchange = None
    
    for i1 in range(1, len(route1)):
        for j1 in range(i1 + 1, len(route1)):
            for i2 in range(1, len(route2)):
                for j2 in range(i2 + 1, len(route2)):
                    # Calculate improvement
                    improvement = calculate_cross_exchange_improvement(
                        route1, route2, i1, j1, i2, j2
                    )
                    
                    if improvement > best_improvement:
                        best_improvement = improvement
                        best_exchange = (i1, j1, i2, j2)
    
    if best_exchange:
        # Perform the exchange
        i1, j1, i2, j2 = best_exchange
        seg1 = route1[i1:j1]
        seg2 = route2[i2:j2]
        
        route1[i1:j1] = seg2
        route2[i2:j2] = seg1
    
    return route1, route2, best_improvement
```

### 5. Real-Time and Dynamic Routing

#### Dynamic VRP (DVRP)
```python
class DynamicRouteOptimizer:
    def __init__(self):
        self.current_routes = []
        self.unassigned_customers = []
        self.vehicle_positions = {}
    
    def update_vehicle_position(self, vehicle_id, position, timestamp):
        """Update real-time vehicle position."""
        self.vehicle_positions[vehicle_id] = {
            'position': position,
            'timestamp': timestamp
        }
    
    def add_new_customer(self, customer):
        """Add new customer request dynamically."""
        # Try to insert into existing routes
        best_insertion = self.find_best_insertion(customer)
        
        if best_insertion['cost'] < self.insertion_threshold:
            self.insert_customer(customer, best_insertion)
        else:
            self.unassigned_customers.append(customer)
            self.trigger_reoptimization()
    
    def handle_disruption(self, disruption_type, affected_locations):
        """Handle traffic, weather, or other disruptions."""
        affected_routes = self.identify_affected_routes(affected_locations)
        
        for route in affected_routes:
            # Recalculate route considering disruption
            updated_route = self.reoptimize_route(
                route, 
                avoid_locations=affected_locations
            )
            self.update_route(route.id, updated_route)
```

#### Real-Time Route Adjustment
```python
# Monitor and adjust routes based on real-time conditions
def real_time_route_monitor():
    """Continuously monitor and adjust routes."""
    while True:
        # Get current traffic conditions
        traffic_data = get_traffic_data()
        
        # Get vehicle positions
        vehicle_positions = get_vehicle_positions()
        
        # Check for significant delays
        for route in active_routes:
            current_delay = calculate_route_delay(route, traffic_data)
            
            if current_delay > delay_threshold:
                # Reoptimize remaining route
                remaining_customers = get_remaining_customers(route)
                optimized_route = optimize_route(
                    remaining_customers,
                    start_position=vehicle_positions[route.vehicle_id],
                    traffic_conditions=traffic_data
                )
                
                # Update route
                update_vehicle_route(route.vehicle_id, optimized_route)
                notify_driver(route.vehicle_id, optimized_route)
        
        time.sleep(60)  # Check every minute
```

### 6. Multi-Objective Optimization

#### Weighted Objective Function
```python
# Optimize multiple objectives simultaneously
optimizer = pmg.RouteOptimizer(
    objectives={
        'total_distance': {'weight': 0.4, 'minimize': True},
        'total_time': {'weight': 0.3, 'minimize': True},
        'fuel_cost': {'weight': 0.2, 'minimize': True},
        'driver_overtime': {'weight': 0.1, 'minimize': True}
    }
)

routes = optimizer.solve(customers, vehicles, depot_location)
```

#### Pareto Optimization
```python
# Find Pareto-optimal solutions
pareto_optimizer = pmg.ParetoRouteOptimizer(
    objectives=['cost', 'time', 'emissions'],
    population_size=100,
    max_generations=200
)

pareto_solutions = pareto_optimizer.solve(customers, vehicles, depot_location)

# Analyze trade-offs
for solution in pareto_solutions:
    print(f"Cost: ${solution.cost:.2f}, "
          f"Time: {solution.time:.1f}h, "
          f"Emissions: {solution.emissions:.1f}kg CO2")
```

### 7. Constraint Handling

#### Time Window Constraints
```python
def check_time_window_feasibility(route, customer, insertion_position):
    """Check if inserting customer maintains time window feasibility."""
    # Calculate arrival time at insertion position
    arrival_time = calculate_arrival_time(route, insertion_position)
    
    # Check customer time window
    if arrival_time < customer.earliest_time:
        # Wait until earliest time
        service_start = customer.earliest_time
    elif arrival_time > customer.latest_time:
        # Infeasible insertion
        return False, float('inf')
    else:
        service_start = arrival_time
    
    # Check impact on subsequent customers
    departure_time = service_start + customer.service_time
    return check_subsequent_feasibility(route, insertion_position + 1, departure_time)
```

#### Capacity Constraints
```python
def check_capacity_constraints(route, customer):
    """Verify vehicle capacity constraints."""
    current_load = sum(c.demand for c in route.customers)
    
    # Check weight capacity
    if current_load + customer.demand > route.vehicle.capacity_weight:
        return False, "Weight capacity exceeded"
    
    # Check volume capacity
    current_volume = sum(c.volume for c in route.customers)
    if current_volume + customer.volume > route.vehicle.capacity_volume:
        return False, "Volume capacity exceeded"
    
    # Check item count capacity
    if len(route.customers) + 1 > route.vehicle.max_items:
        return False, "Item count capacity exceeded"
    
    return True, "Feasible"
```

#### Driver Hour Regulations
```python
def check_driver_hours(route):
    """Ensure compliance with driver hour regulations."""
    total_driving_time = calculate_total_driving_time(route)
    total_duty_time = calculate_total_duty_time(route)
    
    # EU regulations example
    if total_driving_time > 9 * 60:  # 9 hours driving
        return False, "Daily driving time exceeded"
    
    if total_duty_time > 13 * 60:  # 13 hours duty
        return False, "Daily duty time exceeded"
    
    # Check break requirements
    if not has_required_breaks(route):
        return False, "Break requirements not met"
    
    return True, "Compliant"
```

### 8. Performance Optimization

#### Algorithm Selection Strategy
```python
def select_optimization_algorithm(problem_size, time_limit, quality_requirement):
    """Select appropriate algorithm based on problem characteristics."""
    
    if problem_size <= 20 and time_limit > 3600:
        # Small problem with ample time - use exact method
        return 'branch_and_bound'
    
    elif problem_size <= 100 and quality_requirement == 'high':
        # Medium problem requiring high quality
        return 'hybrid_genetic_algorithm'
    
    elif time_limit < 60:
        # Real-time requirement - use fast heuristic
        return 'nearest_neighbor'
    
    elif problem_size > 500:
        # Large problem - use scalable metaheuristic
        return 'large_neighborhood_search'
    
    else:
        # Default balanced approach
        return 'variable_neighborhood_search'
```

#### Parallel Processing
```python
import multiprocessing as mp
from concurrent.futures import ProcessPoolExecutor

def parallel_route_optimization(customer_clusters, vehicles, depot):
    """Optimize multiple route clusters in parallel."""
    
    def optimize_cluster(cluster):
        optimizer = pmg.RouteOptimizer(algorithm='genetic_algorithm')
        return optimizer.solve(cluster, vehicles, depot)
    
    # Use all available CPU cores
    with ProcessPoolExecutor(max_workers=mp.cpu_count()) as executor:
        cluster_results = list(executor.map(optimize_cluster, customer_clusters))
    
    # Combine results and apply inter-cluster optimization
    combined_routes = combine_cluster_routes(cluster_results)
    return apply_inter_cluster_optimization(combined_routes)
```

### 9. Solution Quality Assessment

#### Performance Metrics
```python
def evaluate_solution_quality(routes, benchmark_solution=None):
    """Comprehensive solution quality assessment."""
    
    metrics = {
        'total_distance': sum(route.total_distance for route in routes),
        'total_time': sum(route.total_time for route in routes),
        'total_cost': sum(route.total_cost for route in routes),
        'vehicle_utilization': calculate_vehicle_utilization(routes),
        'customer_satisfaction': calculate_customer_satisfaction(routes),
        'route_balance': calculate_route_balance(routes),
        'constraint_violations': count_constraint_violations(routes)
    }
    
    if benchmark_solution:
        metrics['improvement_percentage'] = calculate_improvement(
            metrics, benchmark_solution
        )
    
    return metrics

def calculate_vehicle_utilization(routes):
    """Calculate average vehicle capacity utilization."""
    utilizations = []
    for route in routes:
        weight_util = route.total_weight / route.vehicle.capacity_weight
        volume_util = route.total_volume / route.vehicle.capacity_volume
        utilizations.append(max(weight_util, volume_util))
    
    return sum(utilizations) / len(utilizations) if utilizations else 0
```

### 10. Visualization and Reporting

#### Route Visualization
```python
def visualize_routes(routes, customers, depot):
    """Create interactive route visualization."""
    
    # Create base map
    route_map = pmg.Map(center=depot, zoom=10)
    
    # Add depot
    route_map.add_marker(
        depot, 
        popup="Depot", 
        icon=pmg.Icon(color='red', icon='warehouse')
    )
    
    # Add customers
    for customer in customers:
        route_map.add_marker(
            customer.location,
            popup=f"Customer {customer.id}<br>Demand: {customer.demand}",
            icon=pmg.Icon(color='blue', icon='user')
        )
    
    # Add routes with different colors
    colors = ['red', 'blue', 'green', 'purple', 'orange', 'darkred', 'lightred']
    
    for i, route in enumerate(routes):
        color = colors[i % len(colors)]
        
        # Add route line
        route_coordinates = [depot] + [c.location for c in route.customers] + [depot]
        route_map.add_polyline(
            route_coordinates,
            color=color,
            weight=3,
            popup=f"Route {i+1}<br>Distance: {route.total_distance:.1f}km<br>Time: {route.total_time:.1f}h"
        )
        
        # Add route statistics
        route_map.add_text(
            route.customers[0].location if route.customers else depot,
            f"Route {i+1}",
            font_size=12,
            color=color
        )
    
    return route_map

# Generate and display visualization
route_map = visualize_routes(optimized_routes, customers, depot_location)
route_map.save('route_optimization_results.html')
route_map.show()
```

#### Performance Dashboard
```python
def create_optimization_dashboard(routes, optimization_history):
    """Create comprehensive optimization dashboard."""
    
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots
    
    # Create subplots
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=('Optimization Progress', 'Route Statistics', 
                       'Vehicle Utilization', 'Cost Breakdown'),
        specs=[[{"secondary_y": True}, {}],
               [{}, {"type": "pie"}]]
    )
    
    # Optimization progress
    fig.add_trace(
        go.Scatter(
            x=optimization_history['iteration'],
            y=optimization_history['best_cost'],
            name='Best Cost',
            line=dict(color='blue')
        ),
        row=1, col=1
    )
    
    # Route statistics
    route_stats = [
        len(route.customers) for route in routes
    ]
    fig.add_trace(
        go.Bar(
            x=[f"Route {i+1}" for i in range(len(routes))],
            y=route_stats,
            name='Customers per Route'
        ),
        row=1, col=2
    )
    
    # Vehicle utilization
    utilizations = [
        route.total_weight / route.vehicle.capacity_weight * 100
        for route in routes
    ]
    fig.add_trace(
        go.Bar(
            x=[f"Vehicle {i+1}" for i in range(len(routes))],
            y=utilizations,
            name='Capacity Utilization (%)'
        ),
        row=2, col=1
    )
    
    # Cost breakdown
    cost_breakdown = calculate_cost_breakdown(routes)
    fig.add_trace(
        go.Pie(
            labels=list(cost_breakdown.keys()),
            values=list(cost_breakdown.values()),
            name="Cost Breakdown"
        ),
        row=2, col=2
    )
    
    fig.update_layout(
        title="Route Optimization Results Dashboard",
        showlegend=True,
        height=800
    )
    
    return fig
```

---

*This comprehensive route optimization guide provides complete coverage of algorithms, implementations, and best practices for solving vehicle routing problems using PyMapGIS.*
