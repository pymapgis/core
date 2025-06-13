# 📊 Data Analysis Workflows

## Comprehensive Supply Chain Analytics Methodologies

This guide provides complete data analysis workflows for PyMapGIS logistics applications, covering objectives, data sources, collection methods, and advanced analysis techniques for supply chain optimization.

### 1. Analytics Workflow Framework

#### End-to-End Analytics Process
```
Business Problem → Data Requirements → Data Collection → 
Data Preparation → Exploratory Analysis → Modeling → 
Validation → Deployment → Monitoring → Optimization
```

#### Workflow Implementation
```python
import pymapgis as pmg
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
import plotly.express as px
import plotly.graph_objects as go

class SupplyChainAnalyticsWorkflow:
    def __init__(self, config):
        self.config = config
        self.data_sources = {}
        self.processed_data = {}
        self.models = {}
        self.results = {}
    
    def define_business_objectives(self, objectives):
        """Define clear business objectives for analysis."""
        self.objectives = {
            'primary_goal': objectives.get('primary_goal'),
            'success_metrics': objectives.get('success_metrics', []),
            'constraints': objectives.get('constraints', []),
            'timeline': objectives.get('timeline'),
            'stakeholders': objectives.get('stakeholders', [])
        }
        
        # Map objectives to analysis types
        self.analysis_types = self.map_objectives_to_analysis(objectives)
        
        return self.objectives
    
    def map_objectives_to_analysis(self, objectives):
        """Map business objectives to specific analysis types."""
        analysis_mapping = {
            'cost_reduction': ['cost_analysis', 'route_optimization', 'facility_optimization'],
            'service_improvement': ['delivery_performance', 'customer_satisfaction', 'capacity_analysis'],
            'efficiency_optimization': ['resource_utilization', 'process_optimization', 'automation_opportunities'],
            'risk_mitigation': ['risk_assessment', 'scenario_analysis', 'contingency_planning'],
            'growth_planning': ['demand_forecasting', 'capacity_planning', 'network_expansion']
        }
        
        primary_goal = objectives.get('primary_goal')
        return analysis_mapping.get(primary_goal, ['general_analysis'])
```

### 2. Data Collection and Preparation Workflows

#### Multi-Source Data Collection
```python
class DataCollectionWorkflow:
    def __init__(self):
        self.collection_strategies = {}
        self.data_quality_checks = {}
        self.integration_rules = {}
    
    async def collect_operational_data(self):
        """Collect operational data from various sources."""
        
        # Transportation data
        transportation_data = await self.collect_transportation_data()
        
        # Warehouse operations data
        warehouse_data = await self.collect_warehouse_data()
        
        # Customer and order data
        customer_order_data = await self.collect_customer_order_data()
        
        # Vehicle and fleet data
        fleet_data = await self.collect_fleet_data()
        
        # External data (weather, traffic, economic)
        external_data = await self.collect_external_data()
        
        return {
            'transportation': transportation_data,
            'warehouse': warehouse_data,
            'customer_orders': customer_order_data,
            'fleet': fleet_data,
            'external': external_data
        }
    
    async def collect_transportation_data(self):
        """Collect comprehensive transportation data."""
        
        # Route performance data
        route_performance = await self.query_database("""
            SELECT 
                r.route_id,
                r.planned_distance,
                r.actual_distance,
                r.planned_duration,
                r.actual_duration,
                r.fuel_consumed,
                r.cost_actual,
                r.delivery_date,
                v.vehicle_type,
                v.capacity_weight,
                COUNT(d.delivery_id) as delivery_count,
                SUM(d.weight_kg) as total_weight,
                AVG(d.delivery_time_minutes) as avg_delivery_time
            FROM routes r
            JOIN vehicles v ON r.vehicle_id = v.id
            JOIN deliveries d ON r.route_id = d.route_id
            WHERE r.delivery_date >= CURRENT_DATE - INTERVAL '90 days'
            GROUP BY r.route_id, v.vehicle_type, v.capacity_weight
        """)
        
        # Traffic and road condition data
        traffic_data = await self.collect_traffic_data()
        
        # Delivery performance data
        delivery_performance = await self.query_database("""
            SELECT 
                d.delivery_id,
                d.customer_id,
                d.scheduled_time,
                d.actual_time,
                d.delivery_status,
                d.weight_kg,
                d.volume_m3,
                c.customer_type,
                c.location_type,
                ST_X(c.geometry) as longitude,
                ST_Y(c.geometry) as latitude
            FROM deliveries d
            JOIN customers c ON d.customer_id = c.id
            WHERE d.delivery_date >= CURRENT_DATE - INTERVAL '90 days'
        """)
        
        return {
            'route_performance': route_performance,
            'traffic_data': traffic_data,
            'delivery_performance': delivery_performance
        }
    
    async def collect_warehouse_data(self):
        """Collect warehouse operations data."""
        
        # Inventory levels and turnover
        inventory_data = await self.query_database("""
            SELECT 
                i.product_id,
                i.warehouse_id,
                i.current_stock,
                i.reorder_point,
                i.max_stock,
                i.last_restock_date,
                p.product_category,
                p.unit_weight,
                p.unit_volume,
                w.warehouse_name,
                w.capacity_weight,
                w.capacity_volume
            FROM inventory i
            JOIN products p ON i.product_id = p.id
            JOIN warehouses w ON i.warehouse_id = w.id
        """)
        
        # Picking and packing performance
        fulfillment_data = await self.query_database("""
            SELECT 
                o.order_id,
                o.order_date,
                o.pick_start_time,
                o.pick_end_time,
                o.pack_start_time,
                o.pack_end_time,
                o.ship_time,
                COUNT(ol.order_line_id) as line_count,
                SUM(ol.quantity) as total_items,
                SUM(ol.weight) as total_weight
            FROM orders o
            JOIN order_lines ol ON o.order_id = ol.order_id
            WHERE o.order_date >= CURRENT_DATE - INTERVAL '30 days'
            GROUP BY o.order_id
        """)
        
        return {
            'inventory': inventory_data,
            'fulfillment': fulfillment_data
        }
```

### 3. Exploratory Data Analysis Workflows

#### Comprehensive EDA Framework
```python
class ExploratoryAnalysisWorkflow:
    def __init__(self, data):
        self.data = data
        self.insights = {}
        self.visualizations = {}
    
    def perform_comprehensive_eda(self):
        """Perform comprehensive exploratory data analysis."""
        
        # Data overview and quality assessment
        self.data_overview = self.analyze_data_overview()
        
        # Temporal analysis
        self.temporal_insights = self.analyze_temporal_patterns()
        
        # Spatial analysis
        self.spatial_insights = self.analyze_spatial_patterns()
        
        # Performance analysis
        self.performance_insights = self.analyze_performance_metrics()
        
        # Correlation analysis
        self.correlation_insights = self.analyze_correlations()
        
        # Anomaly detection
        self.anomaly_insights = self.detect_anomalies()
        
        return self.compile_eda_report()
    
    def analyze_temporal_patterns(self):
        """Analyze temporal patterns in logistics data."""
        
        insights = {}
        
        # Delivery performance over time
        if 'delivery_performance' in self.data:
            delivery_df = self.data['delivery_performance']
            delivery_df['delivery_date'] = pd.to_datetime(delivery_df['actual_time']).dt.date
            
            # Daily delivery patterns
            daily_performance = delivery_df.groupby('delivery_date').agg({
                'delivery_id': 'count',
                'actual_time': lambda x: (pd.to_datetime(x) - pd.to_datetime(delivery_df.loc[x.index, 'scheduled_time'])).dt.total_seconds().mean() / 60
            }).rename(columns={'delivery_id': 'delivery_count', 'actual_time': 'avg_delay_minutes'})
            
            insights['daily_delivery_trends'] = daily_performance
            
            # Weekly patterns
            delivery_df['day_of_week'] = pd.to_datetime(delivery_df['actual_time']).dt.day_name()
            weekly_patterns = delivery_df.groupby('day_of_week').agg({
                'delivery_id': 'count',
                'weight_kg': 'mean'
            })
            
            insights['weekly_patterns'] = weekly_patterns
            
            # Hourly patterns
            delivery_df['hour'] = pd.to_datetime(delivery_df['actual_time']).dt.hour
            hourly_patterns = delivery_df.groupby('hour').agg({
                'delivery_id': 'count',
                'weight_kg': 'sum'
            })
            
            insights['hourly_patterns'] = hourly_patterns
        
        return insights
    
    def analyze_spatial_patterns(self):
        """Analyze spatial patterns in logistics operations."""
        
        insights = {}
        
        if 'delivery_performance' in self.data:
            delivery_df = self.data['delivery_performance']
            
            # Create spatial clusters of deliveries
            delivery_gdf = pmg.GeoDataFrame(
                delivery_df,
                geometry=pmg.points_from_xy(delivery_df.longitude, delivery_df.latitude)
            )
            
            # Density analysis
            delivery_density = delivery_gdf.pmg.calculate_density(
                cell_size=1000,  # 1km grid
                method='kernel'
            )
            
            insights['delivery_density'] = delivery_density
            
            # Service area analysis
            service_areas = delivery_gdf.pmg.calculate_service_areas(
                facilities=self.get_facility_locations(),
                travel_time_minutes=[15, 30, 45, 60]
            )
            
            insights['service_areas'] = service_areas
            
            # Route efficiency analysis
            route_efficiency = self.analyze_route_efficiency(delivery_gdf)
            insights['route_efficiency'] = route_efficiency
        
        return insights
    
    def analyze_performance_metrics(self):
        """Analyze key performance metrics."""
        
        insights = {}
        
        # On-time delivery performance
        if 'delivery_performance' in self.data:
            delivery_df = self.data['delivery_performance']
            
            delivery_df['scheduled_time'] = pd.to_datetime(delivery_df['scheduled_time'])
            delivery_df['actual_time'] = pd.to_datetime(delivery_df['actual_time'])
            delivery_df['delay_minutes'] = (delivery_df['actual_time'] - delivery_df['scheduled_time']).dt.total_seconds() / 60
            delivery_df['on_time'] = delivery_df['delay_minutes'] <= 15  # 15-minute tolerance
            
            otd_performance = {
                'overall_otd_rate': delivery_df['on_time'].mean(),
                'avg_delay_minutes': delivery_df['delay_minutes'].mean(),
                'median_delay_minutes': delivery_df['delay_minutes'].median(),
                'delay_std': delivery_df['delay_minutes'].std()
            }
            
            # Performance by customer type
            otd_by_customer_type = delivery_df.groupby('customer_type').agg({
                'on_time': 'mean',
                'delay_minutes': 'mean'
            })
            
            insights['otd_performance'] = otd_performance
            insights['otd_by_customer_type'] = otd_by_customer_type
        
        # Vehicle utilization analysis
        if 'route_performance' in self.data:
            route_df = self.data['route_performance']
            
            route_df['weight_utilization'] = route_df['total_weight'] / route_df['capacity_weight']
            route_df['distance_efficiency'] = route_df['planned_distance'] / route_df['actual_distance']
            route_df['time_efficiency'] = route_df['planned_duration'] / route_df['actual_duration']
            
            utilization_metrics = {
                'avg_weight_utilization': route_df['weight_utilization'].mean(),
                'avg_distance_efficiency': route_df['distance_efficiency'].mean(),
                'avg_time_efficiency': route_df['time_efficiency'].mean()
            }
            
            insights['utilization_metrics'] = utilization_metrics
        
        return insights
```

### 4. Predictive Analytics Workflows

#### Demand Forecasting Workflow
```python
class DemandForecastingWorkflow:
    def __init__(self):
        self.models = {}
        self.forecasts = {}
        self.accuracy_metrics = {}
    
    def build_demand_forecast_model(self, historical_data, forecast_horizon=30):
        """Build comprehensive demand forecasting model."""
        
        # Prepare time series data
        demand_ts = self.prepare_demand_timeseries(historical_data)
        
        # Feature engineering
        features_df = self.engineer_demand_features(demand_ts)
        
        # Multiple forecasting approaches
        forecasting_models = {
            'arima': self.build_arima_model(demand_ts),
            'prophet': self.build_prophet_model(demand_ts),
            'lstm': self.build_lstm_model(features_df),
            'ensemble': self.build_ensemble_model(demand_ts, features_df)
        }
        
        # Model validation and selection
        best_model = self.validate_and_select_model(forecasting_models, demand_ts)
        
        # Generate forecasts
        forecasts = self.generate_forecasts(best_model, forecast_horizon)
        
        return {
            'model': best_model,
            'forecasts': forecasts,
            'accuracy_metrics': self.calculate_accuracy_metrics(best_model, demand_ts)
        }
    
    def prepare_demand_timeseries(self, historical_data):
        """Prepare demand data for time series analysis."""
        
        # Aggregate demand by day
        daily_demand = historical_data.groupby('delivery_date').agg({
            'delivery_id': 'count',
            'weight_kg': 'sum',
            'volume_m3': 'sum'
        }).rename(columns={
            'delivery_id': 'order_count',
            'weight_kg': 'total_weight',
            'volume_m3': 'total_volume'
        })
        
        # Fill missing dates
        date_range = pd.date_range(
            start=daily_demand.index.min(),
            end=daily_demand.index.max(),
            freq='D'
        )
        daily_demand = daily_demand.reindex(date_range, fill_value=0)
        
        # Add time-based features
        daily_demand['day_of_week'] = daily_demand.index.dayofweek
        daily_demand['month'] = daily_demand.index.month
        daily_demand['quarter'] = daily_demand.index.quarter
        daily_demand['is_weekend'] = daily_demand['day_of_week'].isin([5, 6])
        
        return daily_demand
    
    def engineer_demand_features(self, demand_ts):
        """Engineer features for demand forecasting."""
        
        features_df = demand_ts.copy()
        
        # Lag features
        for lag in [1, 7, 14, 30]:
            features_df[f'order_count_lag_{lag}'] = features_df['order_count'].shift(lag)
            features_df[f'total_weight_lag_{lag}'] = features_df['total_weight'].shift(lag)
        
        # Rolling statistics
        for window in [7, 14, 30]:
            features_df[f'order_count_rolling_mean_{window}'] = features_df['order_count'].rolling(window).mean()
            features_df[f'order_count_rolling_std_{window}'] = features_df['order_count'].rolling(window).std()
        
        # Seasonal decomposition features
        from statsmodels.tsa.seasonal import seasonal_decompose
        
        decomposition = seasonal_decompose(
            features_df['order_count'].fillna(method='ffill'),
            model='additive',
            period=7
        )
        
        features_df['trend'] = decomposition.trend
        features_df['seasonal'] = decomposition.seasonal
        features_df['residual'] = decomposition.resid
        
        # External factors (weather, holidays, economic indicators)
        features_df = self.add_external_features(features_df)
        
        return features_df.dropna()
    
    def add_external_features(self, features_df):
        """Add external factors that influence demand."""
        
        # Weather data
        weather_data = self.get_weather_data(features_df.index)
        if weather_data is not None:
            features_df = features_df.join(weather_data, how='left')
        
        # Holiday indicators
        holidays = self.get_holiday_indicators(features_df.index)
        features_df = features_df.join(holidays, how='left')
        
        # Economic indicators
        economic_data = self.get_economic_indicators(features_df.index)
        if economic_data is not None:
            features_df = features_df.join(economic_data, how='left')
        
        return features_df
```

### 5. Optimization Workflows

#### Route Optimization Analysis Workflow
```python
class RouteOptimizationWorkflow:
    def __init__(self):
        self.optimization_results = {}
        self.performance_metrics = {}
    
    def analyze_route_optimization_opportunities(self, current_routes, historical_performance):
        """Analyze opportunities for route optimization."""
        
        # Current state analysis
        current_performance = self.analyze_current_routes(current_routes)
        
        # Benchmark analysis
        benchmark_performance = self.calculate_benchmark_performance(historical_performance)
        
        # Optimization scenarios
        optimization_scenarios = self.generate_optimization_scenarios(current_routes)
        
        # Cost-benefit analysis
        cost_benefit = self.calculate_optimization_benefits(
            current_performance,
            optimization_scenarios
        )
        
        return {
            'current_performance': current_performance,
            'benchmark_performance': benchmark_performance,
            'optimization_scenarios': optimization_scenarios,
            'cost_benefit_analysis': cost_benefit,
            'recommendations': self.generate_optimization_recommendations(cost_benefit)
        }
    
    def analyze_current_routes(self, routes_data):
        """Analyze current route performance."""
        
        performance_metrics = {}
        
        # Distance and time efficiency
        performance_metrics['distance_efficiency'] = {
            'total_distance': routes_data['actual_distance'].sum(),
            'avg_distance_per_route': routes_data['actual_distance'].mean(),
            'distance_variance': routes_data['actual_distance'].var()
        }
        
        performance_metrics['time_efficiency'] = {
            'total_time': routes_data['actual_duration'].sum(),
            'avg_time_per_route': routes_data['actual_duration'].mean(),
            'time_variance': routes_data['actual_duration'].var()
        }
        
        # Cost analysis
        performance_metrics['cost_analysis'] = {
            'total_cost': routes_data['cost_actual'].sum(),
            'cost_per_km': (routes_data['cost_actual'] / routes_data['actual_distance']).mean(),
            'cost_per_delivery': (routes_data['cost_actual'] / routes_data['delivery_count']).mean()
        }
        
        # Vehicle utilization
        performance_metrics['utilization'] = {
            'avg_weight_utilization': (routes_data['total_weight'] / routes_data['capacity_weight']).mean(),
            'utilization_variance': (routes_data['total_weight'] / routes_data['capacity_weight']).var()
        }
        
        return performance_metrics
    
    def generate_optimization_scenarios(self, current_routes):
        """Generate different optimization scenarios."""
        
        scenarios = {}
        
        # Scenario 1: Route consolidation
        scenarios['consolidation'] = self.analyze_route_consolidation(current_routes)
        
        # Scenario 2: Vehicle type optimization
        scenarios['vehicle_optimization'] = self.analyze_vehicle_optimization(current_routes)
        
        # Scenario 3: Delivery time window optimization
        scenarios['time_window_optimization'] = self.analyze_time_window_optimization(current_routes)
        
        # Scenario 4: Hub-and-spoke vs direct delivery
        scenarios['network_optimization'] = self.analyze_network_optimization(current_routes)
        
        return scenarios
```

### 6. Visualization and Reporting Workflows

#### Interactive Dashboard Creation
```python
class VisualizationWorkflow:
    def __init__(self):
        self.dashboards = {}
        self.reports = {}
    
    def create_executive_dashboard(self, analytics_results):
        """Create executive-level analytics dashboard."""
        
        import plotly.graph_objects as go
        from plotly.subplots import make_subplots
        
        # Create subplot structure
        fig = make_subplots(
            rows=3, cols=3,
            subplot_titles=(
                'On-Time Delivery Trend', 'Cost per Mile Trend', 'Fleet Utilization',
                'Delivery Volume by Region', 'Route Efficiency', 'Customer Satisfaction',
                'Fuel Efficiency Trend', 'Capacity Utilization', 'Performance Summary'
            ),
            specs=[
                [{"secondary_y": True}, {"secondary_y": True}, {}],
                [{}, {}, {}],
                [{"secondary_y": True}, {}, {"type": "table"}]
            ]
        )
        
        # On-time delivery trend
        otd_data = analytics_results['performance_insights']['otd_performance']
        fig.add_trace(
            go.Scatter(
                x=otd_data.index,
                y=otd_data['otd_rate'],
                name='OTD Rate',
                line=dict(color='green')
            ),
            row=1, col=1
        )
        
        # Cost per mile trend
        cost_data = analytics_results['performance_insights']['cost_analysis']
        fig.add_trace(
            go.Scatter(
                x=cost_data.index,
                y=cost_data['cost_per_km'],
                name='Cost per KM',
                line=dict(color='red')
            ),
            row=1, col=2
        )
        
        # Fleet utilization
        utilization_data = analytics_results['performance_insights']['utilization_metrics']
        fig.add_trace(
            go.Bar(
                x=['Weight', 'Volume', 'Time'],
                y=[
                    utilization_data['avg_weight_utilization'],
                    utilization_data.get('avg_volume_utilization', 0.8),
                    utilization_data.get('avg_time_utilization', 0.75)
                ],
                name='Utilization %'
            ),
            row=1, col=3
        )
        
        # Update layout
        fig.update_layout(
            title="Supply Chain Performance Dashboard",
            showlegend=True,
            height=900
        )
        
        return fig
    
    def create_operational_report(self, analytics_results):
        """Create detailed operational analytics report."""
        
        report = {
            'executive_summary': self.create_executive_summary(analytics_results),
            'performance_analysis': self.create_performance_analysis(analytics_results),
            'optimization_opportunities': self.create_optimization_analysis(analytics_results),
            'recommendations': self.create_recommendations(analytics_results),
            'appendices': self.create_appendices(analytics_results)
        }
        
        return report
    
    def create_executive_summary(self, results):
        """Create executive summary of analytics results."""
        
        summary = {
            'key_findings': [
                f"On-time delivery rate: {results['performance_insights']['otd_performance']['overall_otd_rate']:.1%}",
                f"Average cost per kilometer: ${results['performance_insights']['cost_analysis']['cost_per_km']:.2f}",
                f"Fleet utilization: {results['performance_insights']['utilization_metrics']['avg_weight_utilization']:.1%}",
                f"Potential cost savings: ${results.get('optimization_opportunities', {}).get('total_savings', 0):,.0f}"
            ],
            'recommendations': [
                "Implement dynamic routing to improve on-time delivery",
                "Optimize vehicle loading to increase utilization",
                "Consider route consolidation for cost reduction",
                "Invest in predictive analytics for demand planning"
            ],
            'next_steps': [
                "Pilot dynamic routing system",
                "Implement real-time tracking",
                "Develop customer communication system",
                "Create performance monitoring dashboard"
            ]
        }
        
        return summary
```

---

*This comprehensive data analysis workflows guide provides complete methodologies for supply chain analytics using PyMapGIS with focus on business value and actionable insights.*
