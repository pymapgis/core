# 📡 Real-Time Data Integration

## Comprehensive Guide to Real-Time Data Processing for Supply Chain

This guide provides complete implementation of real-time data integration for PyMapGIS logistics applications, covering IoT sensors, GPS tracking, and dynamic supply chain management.

### 1. Real-Time Data Architecture

#### Streaming Data Pipeline
```
Data Sources → Message Brokers → Stream Processors → 
Real-Time Analytics → Decision Engine → Action Triggers
```

#### Core Components
- **Data Ingestion**: Kafka, RabbitMQ, AWS Kinesis
- **Stream Processing**: Apache Spark Streaming, Apache Flink
- **Real-Time Storage**: Redis, InfluxDB, TimescaleDB
- **Event Processing**: Complex Event Processing (CEP) engines
- **Notification Systems**: WebSockets, Server-Sent Events, Push notifications

### 2. GPS and Vehicle Tracking Integration

#### GPS Data Ingestion
```python
import asyncio
import json
from kafka import KafkaProducer, KafkaConsumer
import pymapgis as pmg

class GPSDataProcessor:
    def __init__(self, kafka_config):
        self.producer = KafkaProducer(
            bootstrap_servers=kafka_config['servers'],
            value_serializer=lambda v: json.dumps(v).encode('utf-8')
        )
        self.consumer = KafkaConsumer(
            'gps-tracking',
            bootstrap_servers=kafka_config['servers'],
            value_deserializer=lambda m: json.loads(m.decode('utf-8'))
        )
    
    async def process_gps_stream(self):
        """Process real-time GPS data stream."""
        for message in self.consumer:
            gps_data = message.value
            
            # Validate GPS data
            if self.validate_gps_data(gps_data):
                # Update vehicle position
                await self.update_vehicle_position(gps_data)
                
                # Check for geofence violations
                await self.check_geofences(gps_data)
                
                # Update route progress
                await self.update_route_progress(gps_data)
                
                # Trigger alerts if needed
                await self.check_alert_conditions(gps_data)
    
    def validate_gps_data(self, data):
        """Validate GPS data quality."""
        required_fields = ['vehicle_id', 'latitude', 'longitude', 'timestamp', 'speed']
        
        # Check required fields
        if not all(field in data for field in required_fields):
            return False
        
        # Validate coordinate ranges
        if not (-90 <= data['latitude'] <= 90):
            return False
        if not (-180 <= data['longitude'] <= 180):
            return False
        
        # Check for reasonable speed (< 200 km/h for trucks)
        if data['speed'] > 200:
            return False
        
        return True
    
    async def update_vehicle_position(self, gps_data):
        """Update vehicle position in real-time database."""
        vehicle_update = {
            'vehicle_id': gps_data['vehicle_id'],
            'position': {
                'lat': gps_data['latitude'],
                'lon': gps_data['longitude']
            },
            'speed': gps_data['speed'],
            'heading': gps_data.get('heading', 0),
            'timestamp': gps_data['timestamp']
        }
        
        # Update Redis for fast access
        await self.redis_client.hset(
            f"vehicle:{gps_data['vehicle_id']}", 
            mapping=vehicle_update
        )
        
        # Update time-series database
        await self.influx_client.write_point(
            measurement='vehicle_positions',
            tags={'vehicle_id': gps_data['vehicle_id']},
            fields=vehicle_update,
            time=gps_data['timestamp']
        )
```

#### Real-Time Route Monitoring
```python
class RouteMonitor:
    def __init__(self):
        self.active_routes = {}
        self.route_deviations = {}
    
    async def monitor_route_adherence(self, vehicle_id, current_position):
        """Monitor vehicle adherence to planned route."""
        if vehicle_id not in self.active_routes:
            return
        
        planned_route = self.active_routes[vehicle_id]
        
        # Calculate distance from planned route
        deviation_distance = self.calculate_route_deviation(
            current_position, planned_route
        )
        
        # Check if deviation exceeds threshold
        if deviation_distance > planned_route.deviation_threshold:
            await self.handle_route_deviation(vehicle_id, deviation_distance)
        
        # Update ETA based on current progress
        updated_eta = self.calculate_updated_eta(vehicle_id, current_position)
        await self.update_customer_notifications(vehicle_id, updated_eta)
    
    def calculate_route_deviation(self, current_pos, planned_route):
        """Calculate perpendicular distance from planned route."""
        route_line = planned_route.geometry
        current_point = pmg.Point(current_pos['lon'], current_pos['lat'])
        
        # Find closest point on route
        closest_point = route_line.interpolate(
            route_line.project(current_point)
        )
        
        # Calculate distance
        return pmg.distance(current_point, closest_point).meters
    
    async def handle_route_deviation(self, vehicle_id, deviation_distance):
        """Handle significant route deviation."""
        # Log deviation
        deviation_event = {
            'vehicle_id': vehicle_id,
            'deviation_distance': deviation_distance,
            'timestamp': datetime.utcnow(),
            'severity': 'high' if deviation_distance > 1000 else 'medium'
        }
        
        # Store in database
        await self.log_deviation_event(deviation_event)
        
        # Notify dispatcher
        await self.notify_dispatcher(deviation_event)
        
        # Trigger route recalculation if needed
        if deviation_distance > 2000:  # 2km threshold
            await self.trigger_route_recalculation(vehicle_id)
```

### 3. IoT Sensor Integration

#### Temperature and Condition Monitoring
```python
class IoTSensorProcessor:
    def __init__(self):
        self.sensor_thresholds = {
            'temperature': {'min': -20, 'max': 25},  # Cold chain
            'humidity': {'min': 30, 'max': 70},
            'shock': {'max': 5.0},  # G-force
            'door_status': ['closed', 'open']
        }
    
    async def process_sensor_data(self, sensor_data):
        """Process IoT sensor data from vehicles and containers."""
        
        # Validate sensor data
        if not self.validate_sensor_data(sensor_data):
            return
        
        # Check for threshold violations
        violations = self.check_threshold_violations(sensor_data)
        
        if violations:
            await self.handle_threshold_violations(sensor_data, violations)
        
        # Store sensor data
        await self.store_sensor_data(sensor_data)
        
        # Update real-time dashboard
        await self.update_dashboard(sensor_data)
    
    def check_threshold_violations(self, sensor_data):
        """Check if sensor readings violate defined thresholds."""
        violations = []
        
        for sensor_type, reading in sensor_data['readings'].items():
            if sensor_type in self.sensor_thresholds:
                threshold = self.sensor_thresholds[sensor_type]
                
                if 'min' in threshold and reading < threshold['min']:
                    violations.append({
                        'sensor_type': sensor_type,
                        'reading': reading,
                        'threshold': threshold['min'],
                        'violation_type': 'below_minimum'
                    })
                
                if 'max' in threshold and reading > threshold['max']:
                    violations.append({
                        'sensor_type': sensor_type,
                        'reading': reading,
                        'threshold': threshold['max'],
                        'violation_type': 'above_maximum'
                    })
        
        return violations
    
    async def handle_threshold_violations(self, sensor_data, violations):
        """Handle sensor threshold violations."""
        for violation in violations:
            # Create alert
            alert = {
                'vehicle_id': sensor_data['vehicle_id'],
                'sensor_type': violation['sensor_type'],
                'current_reading': violation['reading'],
                'threshold': violation['threshold'],
                'violation_type': violation['violation_type'],
                'timestamp': sensor_data['timestamp'],
                'severity': self.determine_severity(violation)
            }
            
            # Store alert
            await self.store_alert(alert)
            
            # Send notifications
            await self.send_alert_notifications(alert)
            
            # Trigger automated responses
            await self.trigger_automated_response(alert)
```

#### Predictive Maintenance Integration
```python
class PredictiveMaintenanceProcessor:
    def __init__(self):
        self.ml_models = {}
        self.maintenance_thresholds = {}
    
    async def process_vehicle_telemetry(self, telemetry_data):
        """Process vehicle telemetry for predictive maintenance."""
        
        vehicle_id = telemetry_data['vehicle_id']
        
        # Extract relevant features
        features = self.extract_maintenance_features(telemetry_data)
        
        # Run predictive models
        predictions = await self.run_maintenance_predictions(vehicle_id, features)
        
        # Check for maintenance alerts
        maintenance_alerts = self.check_maintenance_alerts(predictions)
        
        if maintenance_alerts:
            await self.schedule_maintenance(vehicle_id, maintenance_alerts)
    
    def extract_maintenance_features(self, telemetry_data):
        """Extract features relevant to maintenance prediction."""
        return {
            'engine_temperature': telemetry_data.get('engine_temp', 0),
            'oil_pressure': telemetry_data.get('oil_pressure', 0),
            'brake_wear': telemetry_data.get('brake_wear', 0),
            'tire_pressure': telemetry_data.get('tire_pressure', []),
            'fuel_efficiency': telemetry_data.get('fuel_efficiency', 0),
            'vibration_levels': telemetry_data.get('vibration', 0),
            'mileage': telemetry_data.get('odometer', 0)
        }
    
    async def run_maintenance_predictions(self, vehicle_id, features):
        """Run ML models to predict maintenance needs."""
        predictions = {}
        
        for component, model in self.ml_models.items():
            # Predict failure probability
            failure_prob = model.predict_proba([list(features.values())])[0][1]
            
            # Predict time to failure
            time_to_failure = model.predict_time_to_failure([list(features.values())])[0]
            
            predictions[component] = {
                'failure_probability': failure_prob,
                'estimated_time_to_failure': time_to_failure,
                'confidence': model.get_prediction_confidence()
            }
        
        return predictions
```

### 4. Traffic and Weather Integration

#### Real-Time Traffic Processing
```python
class TrafficDataProcessor:
    def __init__(self, traffic_api_config):
        self.traffic_api = TrafficAPI(traffic_api_config)
        self.route_optimizer = pmg.RouteOptimizer()
    
    async def process_traffic_updates(self):
        """Process real-time traffic updates."""
        while True:
            try:
                # Get traffic data for active routes
                active_routes = await self.get_active_routes()
                
                for route in active_routes:
                    traffic_data = await self.traffic_api.get_route_traffic(
                        route.geometry
                    )
                    
                    # Analyze traffic impact
                    impact = self.analyze_traffic_impact(route, traffic_data)
                    
                    if impact['delay_minutes'] > 15:  # Significant delay
                        # Trigger route recalculation
                        await self.recalculate_route(route, traffic_data)
                
                await asyncio.sleep(300)  # Check every 5 minutes
                
            except Exception as e:
                logger.error(f"Traffic processing error: {e}")
                await asyncio.sleep(60)
    
    def analyze_traffic_impact(self, route, traffic_data):
        """Analyze traffic impact on route timing."""
        total_delay = 0
        affected_segments = []
        
        for segment in route.segments:
            segment_traffic = self.get_segment_traffic(segment, traffic_data)
            
            if segment_traffic['congestion_level'] > 0.7:  # Heavy traffic
                delay = self.calculate_segment_delay(segment, segment_traffic)
                total_delay += delay
                affected_segments.append({
                    'segment': segment,
                    'delay': delay,
                    'congestion_level': segment_traffic['congestion_level']
                })
        
        return {
            'delay_minutes': total_delay,
            'affected_segments': affected_segments,
            'severity': 'high' if total_delay > 30 else 'medium' if total_delay > 15 else 'low'
        }
    
    async def recalculate_route(self, original_route, traffic_data):
        """Recalculate route considering current traffic."""
        # Get remaining stops
        remaining_stops = self.get_remaining_stops(original_route)
        
        # Get current vehicle position
        current_position = await self.get_vehicle_position(original_route.vehicle_id)
        
        # Recalculate optimal route
        new_route = await self.route_optimizer.optimize(
            start_location=current_position,
            destinations=remaining_stops,
            traffic_data=traffic_data,
            avoid_congestion=True
        )
        
        # Update route and notify driver
        await self.update_vehicle_route(original_route.vehicle_id, new_route)
        await self.notify_driver(original_route.vehicle_id, new_route)
```

#### Weather Impact Processing
```python
class WeatherProcessor:
    def __init__(self, weather_api_config):
        self.weather_api = WeatherAPI(weather_api_config)
        self.risk_assessor = WeatherRiskAssessor()
    
    async def monitor_weather_conditions(self):
        """Monitor weather conditions affecting logistics operations."""
        while True:
            try:
                # Get active routes and facilities
                active_locations = await self.get_active_locations()
                
                for location in active_locations:
                    weather_data = await self.weather_api.get_current_weather(
                        location.coordinates
                    )
                    
                    # Assess weather risks
                    risks = self.risk_assessor.assess_risks(
                        weather_data, location.operation_type
                    )
                    
                    if risks:
                        await self.handle_weather_risks(location, risks)
                
                await asyncio.sleep(1800)  # Check every 30 minutes
                
            except Exception as e:
                logger.error(f"Weather monitoring error: {e}")
                await asyncio.sleep(300)
    
    def assess_weather_risks(self, weather_data, operation_type):
        """Assess weather-related risks for logistics operations."""
        risks = []
        
        # Temperature risks for cold chain
        if operation_type == 'cold_chain':
            if weather_data['temperature'] > 30:  # Hot weather
                risks.append({
                    'type': 'temperature_risk',
                    'severity': 'high',
                    'description': 'High ambient temperature may affect cold chain'
                })
        
        # Precipitation risks
        if weather_data['precipitation'] > 10:  # Heavy rain
            risks.append({
                'type': 'precipitation_risk',
                'severity': 'medium',
                'description': 'Heavy precipitation may cause delays'
            })
        
        # Wind risks
        if weather_data['wind_speed'] > 50:  # Strong winds
            risks.append({
                'type': 'wind_risk',
                'severity': 'high',
                'description': 'Strong winds may affect vehicle stability'
            })
        
        # Visibility risks
        if weather_data['visibility'] < 1000:  # Poor visibility
            risks.append({
                'type': 'visibility_risk',
                'severity': 'high',
                'description': 'Poor visibility may require speed reduction'
            })
        
        return risks
```

### 5. Event-Driven Architecture

#### Complex Event Processing
```python
class LogisticsEventProcessor:
    def __init__(self):
        self.event_rules = {}
        self.event_handlers = {}
        self.event_history = []
    
    async def process_event(self, event):
        """Process logistics events and trigger appropriate actions."""
        
        # Validate event
        if not self.validate_event(event):
            return
        
        # Store event
        self.event_history.append(event)
        
        # Check event rules
        triggered_rules = self.check_event_rules(event)
        
        # Execute triggered actions
        for rule in triggered_rules:
            await self.execute_rule_actions(rule, event)
        
        # Check for complex event patterns
        patterns = self.detect_event_patterns(event)
        
        for pattern in patterns:
            await self.handle_event_pattern(pattern)
    
    def check_event_rules(self, event):
        """Check if event triggers any defined rules."""
        triggered_rules = []
        
        for rule_id, rule in self.event_rules.items():
            if self.evaluate_rule_condition(rule, event):
                triggered_rules.append(rule)
        
        return triggered_rules
    
    def detect_event_patterns(self, current_event):
        """Detect complex patterns in event sequences."""
        patterns = []
        
        # Pattern: Multiple delivery delays for same route
        if current_event['type'] == 'delivery_delay':
            recent_delays = [
                e for e in self.event_history[-10:]
                if e['type'] == 'delivery_delay' 
                and e['route_id'] == current_event['route_id']
                and (current_event['timestamp'] - e['timestamp']).seconds < 3600
            ]
            
            if len(recent_delays) >= 3:
                patterns.append({
                    'type': 'recurring_delays',
                    'route_id': current_event['route_id'],
                    'count': len(recent_delays),
                    'severity': 'high'
                })
        
        # Pattern: Vehicle breakdown indicators
        if current_event['type'] == 'sensor_alert':
            vehicle_id = current_event['vehicle_id']
            recent_alerts = [
                e for e in self.event_history[-20:]
                if e['type'] == 'sensor_alert'
                and e['vehicle_id'] == vehicle_id
                and (current_event['timestamp'] - e['timestamp']).seconds < 7200
            ]
            
            if len(recent_alerts) >= 5:
                patterns.append({
                    'type': 'potential_breakdown',
                    'vehicle_id': vehicle_id,
                    'alert_count': len(recent_alerts),
                    'severity': 'critical'
                })
        
        return patterns
```

### 6. Real-Time Analytics and Dashboards

#### Live Performance Monitoring
```python
class RealTimeAnalytics:
    def __init__(self):
        self.metrics_calculator = MetricsCalculator()
        self.dashboard_updater = DashboardUpdater()
    
    async def update_real_time_metrics(self):
        """Calculate and update real-time performance metrics."""
        while True:
            try:
                # Calculate current metrics
                metrics = await self.calculate_current_metrics()
                
                # Update dashboard
                await self.dashboard_updater.update_metrics(metrics)
                
                # Check for alerts
                alerts = self.check_metric_alerts(metrics)
                
                if alerts:
                    await self.send_metric_alerts(alerts)
                
                await asyncio.sleep(30)  # Update every 30 seconds
                
            except Exception as e:
                logger.error(f"Real-time analytics error: {e}")
                await asyncio.sleep(60)
    
    async def calculate_current_metrics(self):
        """Calculate current performance metrics."""
        
        # Get active vehicles and routes
        active_vehicles = await self.get_active_vehicles()
        active_routes = await self.get_active_routes()
        
        metrics = {
            'fleet_utilization': self.calculate_fleet_utilization(active_vehicles),
            'on_time_performance': await self.calculate_otp(active_routes),
            'average_speed': self.calculate_average_speed(active_vehicles),
            'fuel_efficiency': await self.calculate_fuel_efficiency(active_vehicles),
            'customer_satisfaction': await self.get_customer_satisfaction(),
            'cost_per_mile': await self.calculate_cost_per_mile(),
            'delivery_success_rate': await self.calculate_delivery_success_rate()
        }
        
        return metrics
    
    def calculate_fleet_utilization(self, active_vehicles):
        """Calculate current fleet utilization percentage."""
        total_vehicles = len(self.get_total_fleet())
        active_count = len(active_vehicles)
        
        return (active_count / total_vehicles) * 100 if total_vehicles > 0 else 0
```

### 7. Data Quality and Validation

#### Real-Time Data Quality Monitoring
```python
class DataQualityMonitor:
    def __init__(self):
        self.quality_rules = {}
        self.quality_metrics = {}
    
    async def monitor_data_quality(self, data_stream):
        """Monitor real-time data quality."""
        
        quality_issues = []
        
        # Check data completeness
        completeness_score = self.check_completeness(data_stream)
        if completeness_score < 0.95:  # 95% threshold
            quality_issues.append({
                'type': 'completeness',
                'score': completeness_score,
                'severity': 'medium'
            })
        
        # Check data accuracy
        accuracy_score = await self.check_accuracy(data_stream)
        if accuracy_score < 0.90:  # 90% threshold
            quality_issues.append({
                'type': 'accuracy',
                'score': accuracy_score,
                'severity': 'high'
            })
        
        # Check data timeliness
        timeliness_score = self.check_timeliness(data_stream)
        if timeliness_score < 0.85:  # 85% threshold
            quality_issues.append({
                'type': 'timeliness',
                'score': timeliness_score,
                'severity': 'medium'
            })
        
        # Handle quality issues
        if quality_issues:
            await self.handle_quality_issues(quality_issues)
        
        return quality_issues
    
    def check_completeness(self, data_stream):
        """Check data completeness score."""
        total_records = len(data_stream)
        complete_records = sum(
            1 for record in data_stream 
            if self.is_record_complete(record)
        )
        
        return complete_records / total_records if total_records > 0 else 0
    
    async def check_accuracy(self, data_stream):
        """Check data accuracy using validation rules."""
        total_records = len(data_stream)
        accurate_records = 0
        
        for record in data_stream:
            if await self.validate_record_accuracy(record):
                accurate_records += 1
        
        return accurate_records / total_records if total_records > 0 else 0
```

### 8. Scalability and Performance

#### High-Throughput Data Processing
```python
class HighThroughputProcessor:
    def __init__(self, config):
        self.config = config
        self.worker_pool = asyncio.Queue(maxsize=config['max_workers'])
        self.batch_size = config['batch_size']
        self.processing_stats = {}
    
    async def process_high_volume_stream(self, data_stream):
        """Process high-volume data streams efficiently."""
        
        # Initialize worker pool
        workers = [
            asyncio.create_task(self.worker(f"worker-{i}"))
            for i in range(self.config['max_workers'])
        ]
        
        # Process data in batches
        batch = []
        async for data_point in data_stream:
            batch.append(data_point)
            
            if len(batch) >= self.batch_size:
                await self.worker_pool.put(batch)
                batch = []
        
        # Process remaining data
        if batch:
            await self.worker_pool.put(batch)
        
        # Signal workers to stop
        for _ in workers:
            await self.worker_pool.put(None)
        
        # Wait for workers to complete
        await asyncio.gather(*workers)
    
    async def worker(self, worker_id):
        """Worker process for handling data batches."""
        while True:
            batch = await self.worker_pool.get()
            
            if batch is None:  # Stop signal
                break
            
            try:
                await self.process_batch(batch, worker_id)
                self.update_processing_stats(worker_id, len(batch))
                
            except Exception as e:
                logger.error(f"Worker {worker_id} error: {e}")
            
            finally:
                self.worker_pool.task_done()
    
    async def process_batch(self, batch, worker_id):
        """Process a batch of data points."""
        
        # Parallel processing within batch
        tasks = [
            self.process_single_item(item) 
            for item in batch
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Handle any exceptions
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"Item processing error: {result}")
                await self.handle_processing_error(batch[i], result)
```

---

*This comprehensive real-time data integration guide provides complete implementation of IoT, GPS, and sensor data processing for dynamic supply chain management using PyMapGIS.*
