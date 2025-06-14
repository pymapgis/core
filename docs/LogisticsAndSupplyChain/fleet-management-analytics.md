# 🚛 Fleet Management Analytics

## Comprehensive Vehicle Tracking and Performance Optimization

This guide provides complete fleet management analytics capabilities for PyMapGIS logistics applications, covering vehicle tracking, performance monitoring, predictive maintenance, and fleet optimization strategies.

### 1. Fleet Analytics Framework

#### Comprehensive Fleet Management System
```python
import pymapgis as pmg
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
from sklearn.ensemble import IsolationForest
from sklearn.cluster import KMeans

class FleetManagementAnalytics:
    def __init__(self, config):
        self.config = config
        self.fleet_data = {}
        self.performance_metrics = {}
        self.predictive_models = {}
        self.optimization_results = {}
    
    def initialize_fleet_analytics(self):
        """Initialize comprehensive fleet analytics system."""
        
        # Load fleet data
        self.fleet_data = self.load_fleet_data()
        
        # Initialize tracking systems
        self.tracking_system = VehicleTrackingSystem()
        
        # Initialize performance monitoring
        self.performance_monitor = PerformanceMonitor()
        
        # Initialize predictive maintenance
        self.maintenance_predictor = PredictiveMaintenanceSystem()
        
        # Initialize optimization engine
        self.fleet_optimizer = FleetOptimizationEngine()
        
        return self
    
    def load_fleet_data(self):
        """Load comprehensive fleet data from multiple sources."""
        
        # Vehicle master data
        vehicles = self.load_vehicle_master_data()
        
        # GPS tracking data
        gps_data = self.load_gps_tracking_data()
        
        # Maintenance records
        maintenance_data = self.load_maintenance_records()
        
        # Fuel consumption data
        fuel_data = self.load_fuel_consumption_data()
        
        # Driver data
        driver_data = self.load_driver_data()
        
        # Route assignment data
        route_data = self.load_route_assignments()
        
        return {
            'vehicles': vehicles,
            'gps_tracking': gps_data,
            'maintenance': maintenance_data,
            'fuel_consumption': fuel_data,
            'drivers': driver_data,
            'routes': route_data
        }
```

### 2. Real-Time Vehicle Tracking

#### GPS Tracking and Monitoring
```python
class VehicleTrackingSystem:
    def __init__(self):
        self.active_vehicles = {}
        self.tracking_history = {}
        self.geofences = {}
        self.alerts = {}
    
    async def process_gps_update(self, vehicle_id, gps_data):
        """Process real-time GPS updates for vehicles."""
        
        # Validate GPS data
        if not self.validate_gps_data(gps_data):
            return False
        
        # Update vehicle position
        self.active_vehicles[vehicle_id] = {
            'position': {
                'latitude': gps_data['latitude'],
                'longitude': gps_data['longitude']
            },
            'speed': gps_data['speed'],
            'heading': gps_data['heading'],
            'timestamp': gps_data['timestamp'],
            'engine_status': gps_data.get('engine_status', 'unknown'),
            'fuel_level': gps_data.get('fuel_level', 0)
        }
        
        # Store in tracking history
        await self.store_tracking_history(vehicle_id, gps_data)
        
        # Check geofences
        geofence_alerts = await self.check_geofences(vehicle_id, gps_data)
        
        # Check speed limits
        speed_alerts = await self.check_speed_limits(vehicle_id, gps_data)
        
        # Check route adherence
        route_alerts = await self.check_route_adherence(vehicle_id, gps_data)
        
        # Process alerts
        all_alerts = geofence_alerts + speed_alerts + route_alerts
        if all_alerts:
            await self.process_alerts(vehicle_id, all_alerts)
        
        return True
    
    async def calculate_vehicle_metrics(self, vehicle_id, time_period='24h'):
        """Calculate comprehensive vehicle performance metrics."""
        
        # Get tracking data for time period
        tracking_data = await self.get_tracking_data(vehicle_id, time_period)
        
        if tracking_data.empty:
            return None
        
        metrics = {}
        
        # Distance traveled
        metrics['total_distance'] = self.calculate_total_distance(tracking_data)
        
        # Time in motion vs idle
        metrics['motion_time'], metrics['idle_time'] = self.calculate_motion_idle_time(tracking_data)
        
        # Average speed
        metrics['avg_speed'] = tracking_data[tracking_data['speed'] > 0]['speed'].mean()
        metrics['max_speed'] = tracking_data['speed'].max()
        
        # Fuel efficiency
        fuel_data = await self.get_fuel_data(vehicle_id, time_period)
        if not fuel_data.empty:
            metrics['fuel_efficiency'] = metrics['total_distance'] / fuel_data['fuel_consumed'].sum()
        
        # Harsh driving events
        metrics['harsh_acceleration'] = self.detect_harsh_acceleration(tracking_data)
        metrics['harsh_braking'] = self.detect_harsh_braking(tracking_data)
        metrics['harsh_cornering'] = self.detect_harsh_cornering(tracking_data)
        
        # Geofence violations
        metrics['geofence_violations'] = await self.count_geofence_violations(vehicle_id, time_period)
        
        # Speed violations
        metrics['speed_violations'] = await self.count_speed_violations(vehicle_id, time_period)
        
        return metrics
    
    def calculate_total_distance(self, tracking_data):
        """Calculate total distance traveled using GPS coordinates."""
        
        if len(tracking_data) < 2:
            return 0
        
        total_distance = 0
        
        for i in range(1, len(tracking_data)):
            prev_point = (tracking_data.iloc[i-1]['latitude'], tracking_data.iloc[i-1]['longitude'])
            curr_point = (tracking_data.iloc[i]['latitude'], tracking_data.iloc[i]['longitude'])
            
            # Calculate distance between consecutive points
            distance = pmg.distance(prev_point, curr_point).meters
            
            # Only add if distance is reasonable (filter out GPS errors)
            if distance < 1000:  # Less than 1km between consecutive points
                total_distance += distance
        
        return total_distance / 1000  # Convert to kilometers
    
    def detect_harsh_acceleration(self, tracking_data):
        """Detect harsh acceleration events."""
        
        harsh_events = []
        
        # Calculate acceleration from speed changes
        tracking_data['acceleration'] = tracking_data['speed'].diff() / tracking_data['timestamp'].diff().dt.total_seconds()
        
        # Threshold for harsh acceleration (m/s²)
        harsh_threshold = 2.5
        
        harsh_acceleration_events = tracking_data[tracking_data['acceleration'] > harsh_threshold]
        
        for _, event in harsh_acceleration_events.iterrows():
            harsh_events.append({
                'type': 'harsh_acceleration',
                'timestamp': event['timestamp'],
                'location': (event['latitude'], event['longitude']),
                'acceleration': event['acceleration'],
                'speed_before': event['speed'] - (event['acceleration'] * 1),  # Approximate
                'speed_after': event['speed']
            })
        
        return harsh_events
```

### 3. Performance Monitoring and KPIs

#### Fleet Performance Dashboard
```python
class PerformanceMonitor:
    def __init__(self):
        self.kpi_definitions = self.define_fleet_kpis()
        self.performance_history = {}
        self.benchmarks = {}
    
    def define_fleet_kpis(self):
        """Define comprehensive fleet KPIs."""
        
        return {
            'operational_efficiency': {
                'vehicle_utilization': {
                    'formula': 'active_hours / available_hours',
                    'target': 0.85,
                    'unit': 'percentage'
                },
                'fuel_efficiency': {
                    'formula': 'distance_traveled / fuel_consumed',
                    'target': 8.5,
                    'unit': 'km/liter'
                },
                'average_speed': {
                    'formula': 'total_distance / driving_time',
                    'target': 45,
                    'unit': 'km/h'
                }
            },
            'safety_metrics': {
                'harsh_driving_events': {
                    'formula': 'harsh_events / total_distance',
                    'target': 0.1,
                    'unit': 'events/100km'
                },
                'speed_violations': {
                    'formula': 'speed_violations / total_distance',
                    'target': 0.05,
                    'unit': 'violations/100km'
                },
                'accident_rate': {
                    'formula': 'accidents / million_km',
                    'target': 0.5,
                    'unit': 'accidents/million km'
                }
            },
            'cost_metrics': {
                'cost_per_km': {
                    'formula': 'total_operating_cost / total_distance',
                    'target': 1.2,
                    'unit': 'currency/km'
                },
                'maintenance_cost_ratio': {
                    'formula': 'maintenance_cost / total_operating_cost',
                    'target': 0.15,
                    'unit': 'percentage'
                }
            },
            'service_quality': {
                'on_time_delivery': {
                    'formula': 'on_time_deliveries / total_deliveries',
                    'target': 0.95,
                    'unit': 'percentage'
                },
                'customer_satisfaction': {
                    'formula': 'satisfied_customers / total_customers',
                    'target': 0.90,
                    'unit': 'percentage'
                }
            }
        }
    
    async def calculate_fleet_performance(self, time_period='30d'):
        """Calculate comprehensive fleet performance metrics."""
        
        performance_data = {}
        
        # Get all active vehicles
        vehicles = await self.get_active_vehicles()
        
        for vehicle_id in vehicles:
            vehicle_performance = await self.calculate_vehicle_performance(vehicle_id, time_period)
            performance_data[vehicle_id] = vehicle_performance
        
        # Calculate fleet-wide aggregates
        fleet_performance = self.aggregate_fleet_performance(performance_data)
        
        # Compare against benchmarks
        performance_analysis = self.analyze_performance_against_benchmarks(fleet_performance)
        
        return {
            'individual_vehicles': performance_data,
            'fleet_aggregate': fleet_performance,
            'performance_analysis': performance_analysis,
            'improvement_opportunities': self.identify_improvement_opportunities(performance_analysis)
        }
    
    async def calculate_vehicle_performance(self, vehicle_id, time_period):
        """Calculate individual vehicle performance metrics."""
        
        # Get vehicle data for time period
        tracking_data = await self.get_vehicle_tracking_data(vehicle_id, time_period)
        maintenance_data = await self.get_vehicle_maintenance_data(vehicle_id, time_period)
        fuel_data = await self.get_vehicle_fuel_data(vehicle_id, time_period)
        route_data = await self.get_vehicle_route_data(vehicle_id, time_period)
        
        performance = {}
        
        # Operational efficiency metrics
        performance['operational_efficiency'] = {
            'vehicle_utilization': self.calculate_vehicle_utilization(tracking_data),
            'fuel_efficiency': self.calculate_fuel_efficiency(tracking_data, fuel_data),
            'average_speed': self.calculate_average_speed(tracking_data),
            'distance_traveled': self.calculate_total_distance(tracking_data)
        }
        
        # Safety metrics
        performance['safety_metrics'] = {
            'harsh_driving_events': self.calculate_harsh_driving_rate(tracking_data),
            'speed_violations': self.calculate_speed_violation_rate(tracking_data),
            'geofence_violations': self.calculate_geofence_violation_rate(tracking_data)
        }
        
        # Cost metrics
        performance['cost_metrics'] = {
            'fuel_cost': self.calculate_fuel_cost(fuel_data),
            'maintenance_cost': self.calculate_maintenance_cost(maintenance_data),
            'cost_per_km': self.calculate_cost_per_km(tracking_data, fuel_data, maintenance_data)
        }
        
        # Service quality metrics
        performance['service_quality'] = {
            'on_time_delivery': self.calculate_on_time_delivery_rate(route_data),
            'route_adherence': self.calculate_route_adherence(tracking_data, route_data)
        }
        
        return performance
    
    def create_performance_dashboard(self, performance_data):
        """Create interactive fleet performance dashboard."""
        
        from plotly.subplots import make_subplots
        import plotly.graph_objects as go
        
        # Create dashboard layout
        fig = make_subplots(
            rows=3, cols=3,
            subplot_titles=(
                'Fleet Utilization', 'Fuel Efficiency Trend', 'Safety Score',
                'Cost per KM by Vehicle', 'On-Time Delivery Rate', 'Maintenance Schedule',
                'Speed Distribution', 'Route Efficiency', 'Performance Summary'
            ),
            specs=[
                [{"type": "indicator"}, {}, {"type": "indicator"}],
                [{}, {"type": "indicator"}, {}],
                [{}, {}, {"type": "table"}]
            ]
        )
        
        # Fleet utilization gauge
        avg_utilization = np.mean([
            v['operational_efficiency']['vehicle_utilization'] 
            for v in performance_data['individual_vehicles'].values()
        ])
        
        fig.add_trace(
            go.Indicator(
                mode="gauge+number+delta",
                value=avg_utilization * 100,
                domain={'x': [0, 1], 'y': [0, 1]},
                title={'text': "Fleet Utilization %"},
                delta={'reference': 85},
                gauge={
                    'axis': {'range': [None, 100]},
                    'bar': {'color': "darkblue"},
                    'steps': [
                        {'range': [0, 50], 'color': "lightgray"},
                        {'range': [50, 85], 'color': "gray"}
                    ],
                    'threshold': {
                        'line': {'color': "red", 'width': 4},
                        'thickness': 0.75,
                        'value': 90
                    }
                }
            ),
            row=1, col=1
        )
        
        # Fuel efficiency trend
        fuel_efficiency_data = self.get_fuel_efficiency_trend(performance_data)
        fig.add_trace(
            go.Scatter(
                x=fuel_efficiency_data['date'],
                y=fuel_efficiency_data['efficiency'],
                mode='lines+markers',
                name='Fuel Efficiency'
            ),
            row=1, col=2
        )
        
        # Safety score indicator
        safety_score = self.calculate_overall_safety_score(performance_data)
        fig.add_trace(
            go.Indicator(
                mode="gauge+number",
                value=safety_score,
                title={'text': "Safety Score"},
                gauge={
                    'axis': {'range': [None, 100]},
                    'bar': {'color': "green"},
                    'steps': [
                        {'range': [0, 60], 'color': "red"},
                        {'range': [60, 80], 'color': "yellow"},
                        {'range': [80, 100], 'color': "lightgreen"}
                    ]
                }
            ),
            row=1, col=3
        )
        
        fig.update_layout(
            title="Fleet Management Dashboard",
            height=900
        )
        
        return fig
```

### 4. Predictive Maintenance Analytics

#### Maintenance Prediction System
```python
class PredictiveMaintenanceSystem:
    def __init__(self):
        self.maintenance_models = {}
        self.failure_predictors = {}
        self.maintenance_schedules = {}
    
    def build_maintenance_prediction_models(self, historical_data):
        """Build predictive models for vehicle maintenance."""
        
        # Prepare maintenance data
        maintenance_features = self.prepare_maintenance_features(historical_data)
        
        # Build component-specific models
        components = ['engine', 'transmission', 'brakes', 'tires', 'battery']
        
        for component in components:
            # Prepare component-specific data
            component_data = self.prepare_component_data(maintenance_features, component)
            
            # Build failure prediction model
            failure_model = self.build_failure_prediction_model(component_data)
            
            # Build time-to-failure model
            ttf_model = self.build_time_to_failure_model(component_data)
            
            self.maintenance_models[component] = {
                'failure_prediction': failure_model,
                'time_to_failure': ttf_model,
                'feature_importance': failure_model.feature_importances_
            }
        
        return self.maintenance_models
    
    def prepare_maintenance_features(self, historical_data):
        """Prepare features for maintenance prediction."""
        
        features_df = pd.DataFrame()
        
        # Vehicle characteristics
        features_df['vehicle_age'] = historical_data['vehicle_age']
        features_df['mileage'] = historical_data['mileage']
        features_df['vehicle_type'] = historical_data['vehicle_type']
        
        # Usage patterns
        features_df['avg_daily_distance'] = historical_data['daily_distance'].rolling(30).mean()
        features_df['avg_speed'] = historical_data['avg_speed']
        features_df['idle_time_ratio'] = historical_data['idle_time'] / historical_data['total_time']
        
        # Driving behavior
        features_df['harsh_acceleration_rate'] = historical_data['harsh_acceleration_events'] / historical_data['distance']
        features_df['harsh_braking_rate'] = historical_data['harsh_braking_events'] / historical_data['distance']
        features_df['speed_violation_rate'] = historical_data['speed_violations'] / historical_data['distance']
        
        # Environmental factors
        features_df['avg_temperature'] = historical_data['temperature']
        features_df['humidity'] = historical_data['humidity']
        features_df['road_quality_score'] = historical_data['road_quality']
        
        # Maintenance history
        features_df['days_since_last_service'] = historical_data['days_since_last_service']
        features_df['maintenance_frequency'] = historical_data['maintenance_count'] / historical_data['vehicle_age']
        
        return features_df
    
    async def predict_maintenance_needs(self, vehicle_id):
        """Predict maintenance needs for a specific vehicle."""
        
        # Get current vehicle data
        vehicle_data = await self.get_current_vehicle_data(vehicle_id)
        
        # Prepare features
        features = self.prepare_vehicle_features(vehicle_data)
        
        predictions = {}
        
        for component, models in self.maintenance_models.items():
            # Predict failure probability
            failure_prob = models['failure_prediction'].predict_proba([features])[0][1]
            
            # Predict time to failure
            time_to_failure = models['time_to_failure'].predict([features])[0]
            
            # Calculate maintenance urgency
            urgency = self.calculate_maintenance_urgency(failure_prob, time_to_failure)
            
            predictions[component] = {
                'failure_probability': failure_prob,
                'estimated_time_to_failure_days': time_to_failure,
                'urgency_level': urgency,
                'recommended_action': self.get_recommended_action(urgency, component)
            }
        
        return predictions
    
    def calculate_maintenance_urgency(self, failure_prob, time_to_failure):
        """Calculate maintenance urgency based on failure probability and time."""
        
        # Normalize factors
        prob_score = failure_prob * 100  # 0-100
        time_score = max(0, 100 - (time_to_failure / 30) * 100)  # Higher score for shorter time
        
        # Weighted urgency score
        urgency_score = (prob_score * 0.6) + (time_score * 0.4)
        
        if urgency_score >= 80:
            return 'critical'
        elif urgency_score >= 60:
            return 'high'
        elif urgency_score >= 40:
            return 'medium'
        else:
            return 'low'
    
    def optimize_maintenance_schedule(self, fleet_predictions):
        """Optimize maintenance schedule across the fleet."""
        
        # Collect all maintenance needs
        maintenance_tasks = []
        
        for vehicle_id, predictions in fleet_predictions.items():
            for component, prediction in predictions.items():
                if prediction['urgency_level'] in ['critical', 'high', 'medium']:
                    maintenance_tasks.append({
                        'vehicle_id': vehicle_id,
                        'component': component,
                        'urgency': prediction['urgency_level'],
                        'estimated_time': prediction['estimated_time_to_failure_days'],
                        'failure_probability': prediction['failure_probability']
                    })
        
        # Sort by urgency and failure probability
        maintenance_tasks.sort(
            key=lambda x: (
                {'critical': 0, 'high': 1, 'medium': 2, 'low': 3}[x['urgency']],
                -x['failure_probability']
            )
        )
        
        # Optimize scheduling considering resource constraints
        optimized_schedule = self.schedule_maintenance_tasks(maintenance_tasks)
        
        return optimized_schedule
```

### 5. Fleet Optimization Strategies

#### Fleet Composition and Utilization Optimization
```python
class FleetOptimizationEngine:
    def __init__(self):
        self.optimization_models = {}
        self.scenarios = {}
    
    def analyze_fleet_composition(self, current_fleet, demand_patterns, cost_data):
        """Analyze optimal fleet composition."""
        
        # Current fleet analysis
        current_performance = self.analyze_current_fleet_performance(current_fleet)
        
        # Demand analysis
        demand_analysis = self.analyze_demand_patterns(demand_patterns)
        
        # Vehicle type optimization
        optimal_composition = self.optimize_vehicle_types(demand_analysis, cost_data)
        
        # Fleet size optimization
        optimal_size = self.optimize_fleet_size(demand_analysis, cost_data)
        
        # Replacement strategy
        replacement_strategy = self.develop_replacement_strategy(current_fleet, cost_data)
        
        return {
            'current_performance': current_performance,
            'demand_analysis': demand_analysis,
            'optimal_composition': optimal_composition,
            'optimal_size': optimal_size,
            'replacement_strategy': replacement_strategy,
            'cost_benefit_analysis': self.calculate_optimization_benefits(
                current_performance, optimal_composition, optimal_size
            )
        }
    
    def optimize_vehicle_assignment(self, vehicles, routes, constraints):
        """Optimize vehicle assignment to routes."""
        
        from scipy.optimize import linear_sum_assignment
        
        # Create cost matrix
        cost_matrix = self.create_vehicle_route_cost_matrix(vehicles, routes)
        
        # Apply constraints
        constrained_matrix = self.apply_assignment_constraints(cost_matrix, constraints)
        
        # Solve assignment problem
        vehicle_indices, route_indices = linear_sum_assignment(constrained_matrix)
        
        # Create assignment results
        assignments = []
        for v_idx, r_idx in zip(vehicle_indices, route_indices):
            assignments.append({
                'vehicle_id': vehicles[v_idx]['id'],
                'route_id': routes[r_idx]['id'],
                'cost': cost_matrix[v_idx][r_idx],
                'utilization': self.calculate_vehicle_utilization(vehicles[v_idx], routes[r_idx])
            })
        
        return {
            'assignments': assignments,
            'total_cost': sum(assignment['cost'] for assignment in assignments),
            'avg_utilization': np.mean([assignment['utilization'] for assignment in assignments])
        }
```

---

*This comprehensive fleet management analytics guide provides complete vehicle tracking, performance monitoring, predictive maintenance, and optimization capabilities for PyMapGIS logistics applications.*
