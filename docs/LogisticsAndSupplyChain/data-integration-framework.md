# 🔄 Data Integration Framework

## Comprehensive Multi-Source Data Coordination for Supply Chain Analytics

This guide provides complete implementation of data integration frameworks for PyMapGIS logistics applications, covering multi-source coordination, real-time processing, and enterprise data management.

### 1. Data Integration Architecture

#### Enterprise Data Integration Pattern
```
External Data Sources → Data Ingestion Layer → 
Data Processing Pipeline → Data Storage Layer → 
Data Access Layer → Analytics Applications
```

#### Core Integration Components
```python
import asyncio
import pandas as pd
import pymapgis as pmg
from sqlalchemy import create_engine
from kafka import KafkaProducer, KafkaConsumer
import redis
from typing import Dict, List, Any, Optional

class DataIntegrationFramework:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.data_sources = {}
        self.processors = {}
        self.storage_engines = {}
        self.cache_client = redis.Redis(**config['redis'])
        
        # Initialize data sources
        self.initialize_data_sources()
        
        # Initialize storage engines
        self.initialize_storage()
        
        # Initialize message queues
        self.initialize_messaging()
    
    def initialize_data_sources(self):
        """Initialize connections to various data sources."""
        
        # ERP System Connection
        if 'erp' in self.config:
            self.data_sources['erp'] = ERPConnector(self.config['erp'])
        
        # Transportation Management System
        if 'tms' in self.config:
            self.data_sources['tms'] = TMSConnector(self.config['tms'])
        
        # Warehouse Management System
        if 'wms' in self.config:
            self.data_sources['wms'] = WMSConnector(self.config['wms'])
        
        # GPS/Telematics Systems
        if 'gps' in self.config:
            self.data_sources['gps'] = GPSConnector(self.config['gps'])
        
        # Weather APIs
        if 'weather' in self.config:
            self.data_sources['weather'] = WeatherConnector(self.config['weather'])
        
        # Traffic APIs
        if 'traffic' in self.config:
            self.data_sources['traffic'] = TrafficConnector(self.config['traffic'])
    
    def initialize_storage(self):
        """Initialize storage engines for different data types."""
        
        # Operational Database (PostgreSQL with PostGIS)
        self.storage_engines['operational'] = create_engine(
            self.config['databases']['operational']
        )
        
        # Time-series Database (InfluxDB)
        if 'timeseries' in self.config['databases']:
            self.storage_engines['timeseries'] = InfluxDBClient(
                **self.config['databases']['timeseries']
            )
        
        # Document Database (MongoDB)
        if 'document' in self.config['databases']:
            self.storage_engines['document'] = MongoClient(
                **self.config['databases']['document']
            )
        
        # Data Warehouse (BigQuery/Snowflake)
        if 'warehouse' in self.config['databases']:
            self.storage_engines['warehouse'] = WarehouseClient(
                **self.config['databases']['warehouse']
            )
```

### 2. Data Source Connectors

#### ERP System Integration
```python
class ERPConnector:
    def __init__(self, config):
        self.config = config
        self.client = self.create_client()
        self.last_sync = {}
    
    async def extract_customers(self) -> pd.DataFrame:
        """Extract customer data from ERP system."""
        
        # Get incremental updates since last sync
        last_sync_time = self.last_sync.get('customers', '1900-01-01')
        
        query = f"""
        SELECT 
            customer_id,
            customer_name,
            address_line1,
            address_line2,
            city,
            state,
            postal_code,
            country,
            latitude,
            longitude,
            customer_type,
            credit_limit,
            payment_terms,
            created_date,
            modified_date
        FROM customers 
        WHERE modified_date > '{last_sync_time}'
        ORDER BY modified_date
        """
        
        customers_df = await self.execute_query(query)
        
        # Data quality validation
        customers_df = self.validate_customer_data(customers_df)
        
        # Update last sync time
        if not customers_df.empty:
            self.last_sync['customers'] = customers_df['modified_date'].max()
        
        return customers_df
    
    async def extract_orders(self) -> pd.DataFrame:
        """Extract order data from ERP system."""
        
        last_sync_time = self.last_sync.get('orders', '1900-01-01')
        
        query = f"""
        SELECT 
            o.order_id,
            o.customer_id,
            o.order_date,
            o.required_date,
            o.ship_date,
            o.order_status,
            o.total_amount,
            ol.product_id,
            ol.quantity,
            ol.unit_price,
            ol.weight,
            ol.volume,
            p.product_name,
            p.product_category,
            p.hazmat_class
        FROM orders o
        JOIN order_lines ol ON o.order_id = ol.order_id
        JOIN products p ON ol.product_id = p.product_id
        WHERE o.modified_date > '{last_sync_time}'
        ORDER BY o.modified_date
        """
        
        orders_df = await self.execute_query(query)
        
        # Aggregate order lines by order
        orders_df = self.aggregate_order_data(orders_df)
        
        return orders_df
    
    def validate_customer_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Validate and clean customer data."""
        
        # Remove duplicates
        df = df.drop_duplicates(subset=['customer_id'])
        
        # Validate coordinates
        df = df[
            (df['latitude'].between(-90, 90)) & 
            (df['longitude'].between(-180, 180))
        ]
        
        # Standardize address format
        df['full_address'] = df.apply(self.format_address, axis=1)
        
        # Geocode missing coordinates
        missing_coords = df[df['latitude'].isna() | df['longitude'].isna()]
        if not missing_coords.empty:
            geocoded = self.geocode_addresses(missing_coords['full_address'])
            df.loc[missing_coords.index, ['latitude', 'longitude']] = geocoded
        
        return df
    
    def format_address(self, row) -> str:
        """Format address components into full address."""
        components = [
            row['address_line1'],
            row['address_line2'],
            row['city'],
            row['state'],
            row['postal_code'],
            row['country']
        ]
        return ', '.join([comp for comp in components if pd.notna(comp)])
```

#### GPS/Telematics Integration
```python
class GPSConnector:
    def __init__(self, config):
        self.config = config
        self.kafka_producer = KafkaProducer(
            bootstrap_servers=config['kafka_servers'],
            value_serializer=lambda v: json.dumps(v).encode('utf-8')
        )
    
    async def stream_vehicle_positions(self):
        """Stream real-time vehicle position data."""
        
        async for position_data in self.gps_stream():
            # Validate GPS data
            if self.validate_gps_data(position_data):
                # Enrich with additional data
                enriched_data = await self.enrich_position_data(position_data)
                
                # Send to Kafka topic
                self.kafka_producer.send(
                    'vehicle-positions',
                    value=enriched_data
                )
                
                # Update real-time cache
                await self.update_position_cache(enriched_data)
    
    def validate_gps_data(self, data: Dict) -> bool:
        """Validate GPS data quality."""
        
        required_fields = ['vehicle_id', 'latitude', 'longitude', 'timestamp']
        if not all(field in data for field in required_fields):
            return False
        
        # Coordinate validation
        if not (-90 <= data['latitude'] <= 90):
            return False
        if not (-180 <= data['longitude'] <= 180):
            return False
        
        # Speed validation (reasonable limits)
        if 'speed' in data and data['speed'] > 200:  # 200 km/h max
            return False
        
        # Timestamp validation (not too old or future)
        timestamp = pd.to_datetime(data['timestamp'])
        now = pd.Timestamp.now()
        if abs((timestamp - now).total_seconds()) > 3600:  # 1 hour tolerance
            return False
        
        return True
    
    async def enrich_position_data(self, position_data: Dict) -> Dict:
        """Enrich GPS data with additional context."""
        
        enriched = position_data.copy()
        
        # Add geofence information
        geofences = await self.check_geofences(
            position_data['latitude'],
            position_data['longitude']
        )
        enriched['geofences'] = geofences
        
        # Add route progress if vehicle is on route
        if 'route_id' in position_data:
            route_progress = await self.calculate_route_progress(
                position_data['route_id'],
                position_data['latitude'],
                position_data['longitude']
            )
            enriched['route_progress'] = route_progress
        
        # Add traffic conditions
        traffic_info = await self.get_local_traffic(
            position_data['latitude'],
            position_data['longitude']
        )
        enriched['traffic_conditions'] = traffic_info
        
        return enriched
```

### 3. Data Processing Pipeline

#### ETL Pipeline Implementation
```python
class DataProcessingPipeline:
    def __init__(self, integration_framework):
        self.framework = integration_framework
        self.processors = {
            'customers': CustomerProcessor(),
            'orders': OrderProcessor(),
            'vehicles': VehicleProcessor(),
            'routes': RouteProcessor(),
            'positions': PositionProcessor()
        }
    
    async def process_data_batch(self, data_type: str, data: pd.DataFrame):
        """Process a batch of data through the pipeline."""
        
        processor = self.processors.get(data_type)
        if not processor:
            raise ValueError(f"No processor found for data type: {data_type}")
        
        # Stage 1: Data Validation
        validated_data = await processor.validate(data)
        
        # Stage 2: Data Transformation
        transformed_data = await processor.transform(validated_data)
        
        # Stage 3: Data Enrichment
        enriched_data = await processor.enrich(transformed_data)
        
        # Stage 4: Data Storage
        await self.store_processed_data(data_type, enriched_data)
        
        # Stage 5: Trigger Downstream Processes
        await self.trigger_downstream_processes(data_type, enriched_data)
        
        return enriched_data
    
    async def store_processed_data(self, data_type: str, data: pd.DataFrame):
        """Store processed data in appropriate storage systems."""
        
        # Store in operational database
        await self.store_operational_data(data_type, data)
        
        # Store in time-series database if applicable
        if data_type in ['positions', 'sensor_data']:
            await self.store_timeseries_data(data_type, data)
        
        # Store in data warehouse for analytics
        await self.store_warehouse_data(data_type, data)
        
        # Update cache for real-time access
        await self.update_cache(data_type, data)
    
    async def store_operational_data(self, data_type: str, data: pd.DataFrame):
        """Store data in operational PostgreSQL database."""
        
        engine = self.framework.storage_engines['operational']
        
        # Use upsert operation for idempotency
        if data_type == 'customers':
            await self.upsert_customers(engine, data)
        elif data_type == 'orders':
            await self.upsert_orders(engine, data)
        elif data_type == 'vehicles':
            await self.upsert_vehicles(engine, data)
        elif data_type == 'routes':
            await self.upsert_routes(engine, data)
    
    async def upsert_customers(self, engine, customers_df: pd.DataFrame):
        """Upsert customer data with conflict resolution."""
        
        # Prepare data for upsert
        customers_df['geometry'] = customers_df.apply(
            lambda row: f"POINT({row['longitude']} {row['latitude']})",
            axis=1
        )
        
        # Use PostgreSQL UPSERT (ON CONFLICT)
        upsert_query = """
        INSERT INTO customers (
            customer_id, customer_name, full_address, 
            latitude, longitude, geometry, customer_type,
            credit_limit, payment_terms, updated_at
        ) VALUES (
            %(customer_id)s, %(customer_name)s, %(full_address)s,
            %(latitude)s, %(longitude)s, ST_GeomFromText(%(geometry)s, 4326),
            %(customer_type)s, %(credit_limit)s, %(payment_terms)s, NOW()
        )
        ON CONFLICT (customer_id) 
        DO UPDATE SET
            customer_name = EXCLUDED.customer_name,
            full_address = EXCLUDED.full_address,
            latitude = EXCLUDED.latitude,
            longitude = EXCLUDED.longitude,
            geometry = EXCLUDED.geometry,
            customer_type = EXCLUDED.customer_type,
            credit_limit = EXCLUDED.credit_limit,
            payment_terms = EXCLUDED.payment_terms,
            updated_at = NOW()
        """
        
        with engine.connect() as conn:
            for _, row in customers_df.iterrows():
                conn.execute(upsert_query, row.to_dict())
```

### 4. Real-Time Data Streaming

#### Kafka-based Streaming Architecture
```python
class RealTimeStreamProcessor:
    def __init__(self, config):
        self.config = config
        self.consumers = {}
        self.producers = {}
        self.stream_processors = {}
        
        self.initialize_streams()
    
    def initialize_streams(self):
        """Initialize Kafka streams for different data types."""
        
        # Vehicle position stream
        self.consumers['positions'] = KafkaConsumer(
            'vehicle-positions',
            bootstrap_servers=self.config['kafka_servers'],
            value_deserializer=lambda m: json.loads(m.decode('utf-8')),
            group_id='position-processor'
        )
        
        # Order stream
        self.consumers['orders'] = KafkaConsumer(
            'new-orders',
            bootstrap_servers=self.config['kafka_servers'],
            value_deserializer=lambda m: json.loads(m.decode('utf-8')),
            group_id='order-processor'
        )
        
        # Alert stream
        self.producers['alerts'] = KafkaProducer(
            bootstrap_servers=self.config['kafka_servers'],
            value_serializer=lambda v: json.dumps(v).encode('utf-8')
        )
    
    async def process_position_stream(self):
        """Process real-time vehicle position updates."""
        
        for message in self.consumers['positions']:
            position_data = message.value
            
            try:
                # Update vehicle position in cache
                await self.update_vehicle_position(position_data)
                
                # Check for alerts
                alerts = await self.check_position_alerts(position_data)
                
                # Send alerts if any
                for alert in alerts:
                    self.producers['alerts'].send('logistics-alerts', value=alert)
                
                # Update route progress
                await self.update_route_progress(position_data)
                
                # Trigger dynamic routing if needed
                if await self.should_recalculate_route(position_data):
                    await self.trigger_route_recalculation(position_data)
                
            except Exception as e:
                logger.error(f"Error processing position data: {e}")
                # Send to dead letter queue
                await self.send_to_dlq('position-errors', position_data, str(e))
    
    async def check_position_alerts(self, position_data: Dict) -> List[Dict]:
        """Check for various alert conditions based on position."""
        
        alerts = []
        vehicle_id = position_data['vehicle_id']
        
        # Geofence violations
        if 'geofences' in position_data:
            for geofence in position_data['geofences']:
                if geofence['violation_type'] == 'exit_restricted':
                    alerts.append({
                        'type': 'geofence_violation',
                        'vehicle_id': vehicle_id,
                        'geofence_id': geofence['id'],
                        'severity': 'high',
                        'message': f"Vehicle {vehicle_id} exited restricted area"
                    })
        
        # Speed violations
        if 'speed' in position_data:
            speed_limit = await self.get_speed_limit(
                position_data['latitude'],
                position_data['longitude']
            )
            
            if position_data['speed'] > speed_limit * 1.1:  # 10% tolerance
                alerts.append({
                    'type': 'speed_violation',
                    'vehicle_id': vehicle_id,
                    'current_speed': position_data['speed'],
                    'speed_limit': speed_limit,
                    'severity': 'medium',
                    'message': f"Vehicle {vehicle_id} exceeding speed limit"
                })
        
        # Route deviation
        if 'route_progress' in position_data:
            deviation = position_data['route_progress'].get('deviation_distance', 0)
            if deviation > 1000:  # 1km threshold
                alerts.append({
                    'type': 'route_deviation',
                    'vehicle_id': vehicle_id,
                    'deviation_distance': deviation,
                    'severity': 'medium',
                    'message': f"Vehicle {vehicle_id} deviating from planned route"
                })
        
        return alerts
```

### 5. Data Quality Management

#### Data Quality Framework
```python
class DataQualityManager:
    def __init__(self):
        self.quality_rules = {}
        self.quality_metrics = {}
        self.quality_thresholds = {
            'completeness': 0.95,
            'accuracy': 0.90,
            'consistency': 0.95,
            'timeliness': 0.85,
            'validity': 0.98
        }
    
    async def assess_data_quality(self, data_type: str, data: pd.DataFrame) -> Dict:
        """Comprehensive data quality assessment."""
        
        quality_report = {
            'data_type': data_type,
            'record_count': len(data),
            'assessment_timestamp': pd.Timestamp.now(),
            'metrics': {},
            'issues': [],
            'overall_score': 0
        }
        
        # Completeness assessment
        completeness_score = self.assess_completeness(data)
        quality_report['metrics']['completeness'] = completeness_score
        
        # Accuracy assessment
        accuracy_score = await self.assess_accuracy(data_type, data)
        quality_report['metrics']['accuracy'] = accuracy_score
        
        # Consistency assessment
        consistency_score = self.assess_consistency(data)
        quality_report['metrics']['consistency'] = consistency_score
        
        # Timeliness assessment
        timeliness_score = self.assess_timeliness(data)
        quality_report['metrics']['timeliness'] = timeliness_score
        
        # Validity assessment
        validity_score = self.assess_validity(data_type, data)
        quality_report['metrics']['validity'] = validity_score
        
        # Calculate overall score
        quality_report['overall_score'] = np.mean(list(quality_report['metrics'].values()))
        
        # Identify quality issues
        quality_report['issues'] = self.identify_quality_issues(quality_report['metrics'])
        
        return quality_report
    
    def assess_completeness(self, data: pd.DataFrame) -> float:
        """Assess data completeness (missing values)."""
        
        total_cells = data.size
        missing_cells = data.isnull().sum().sum()
        
        completeness_score = (total_cells - missing_cells) / total_cells
        return completeness_score
    
    async def assess_accuracy(self, data_type: str, data: pd.DataFrame) -> float:
        """Assess data accuracy using validation rules."""
        
        if data_type == 'customers':
            return await self.assess_customer_accuracy(data)
        elif data_type == 'orders':
            return await self.assess_order_accuracy(data)
        elif data_type == 'vehicles':
            return await self.assess_vehicle_accuracy(data)
        else:
            return 1.0  # Default if no specific rules
    
    async def assess_customer_accuracy(self, customers_df: pd.DataFrame) -> float:
        """Assess customer data accuracy."""
        
        total_records = len(customers_df)
        accurate_records = 0
        
        for _, customer in customers_df.iterrows():
            is_accurate = True
            
            # Validate coordinates
            if not (-90 <= customer.get('latitude', 0) <= 90):
                is_accurate = False
            if not (-180 <= customer.get('longitude', 0) <= 180):
                is_accurate = False
            
            # Validate address format
            if not self.is_valid_address(customer.get('full_address', '')):
                is_accurate = False
            
            # Validate customer type
            valid_types = ['retail', 'wholesale', 'distributor', 'manufacturer']
            if customer.get('customer_type') not in valid_types:
                is_accurate = False
            
            if is_accurate:
                accurate_records += 1
        
        return accurate_records / total_records if total_records > 0 else 0
    
    def assess_consistency(self, data: pd.DataFrame) -> float:
        """Assess data consistency across records."""
        
        consistency_issues = 0
        total_checks = 0
        
        # Check for duplicate records
        duplicates = data.duplicated().sum()
        consistency_issues += duplicates
        total_checks += len(data)
        
        # Check for format consistency
        for column in data.select_dtypes(include=['object']).columns:
            if column.endswith('_id'):
                # Check ID format consistency
                id_patterns = data[column].str.extract(r'([A-Z]+)-(\d+)').dropna()
                inconsistent_ids = len(data[column].dropna()) - len(id_patterns)
                consistency_issues += inconsistent_ids
                total_checks += len(data[column].dropna())
        
        consistency_score = (total_checks - consistency_issues) / total_checks if total_checks > 0 else 1.0
        return max(0, consistency_score)
```

### 6. Data Lineage and Governance

#### Data Lineage Tracking
```python
class DataLineageTracker:
    def __init__(self):
        self.lineage_graph = {}
        self.transformation_log = []
    
    def track_data_flow(self, source: str, target: str, transformation: str, metadata: Dict):
        """Track data flow between systems."""
        
        lineage_entry = {
            'source': source,
            'target': target,
            'transformation': transformation,
            'timestamp': pd.Timestamp.now(),
            'metadata': metadata,
            'id': str(uuid.uuid4())
        }
        
        self.transformation_log.append(lineage_entry)
        
        # Update lineage graph
        if source not in self.lineage_graph:
            self.lineage_graph[source] = {'downstream': [], 'upstream': []}
        if target not in self.lineage_graph:
            self.lineage_graph[target] = {'downstream': [], 'upstream': []}
        
        self.lineage_graph[source]['downstream'].append(target)
        self.lineage_graph[target]['upstream'].append(source)
    
    def get_data_lineage(self, entity: str) -> Dict:
        """Get complete data lineage for an entity."""
        
        lineage = {
            'entity': entity,
            'upstream_sources': self.get_upstream_sources(entity),
            'downstream_targets': self.get_downstream_targets(entity),
            'transformations': self.get_transformations(entity)
        }
        
        return lineage
    
    def get_upstream_sources(self, entity: str, visited: set = None) -> List[str]:
        """Get all upstream data sources for an entity."""
        
        if visited is None:
            visited = set()
        
        if entity in visited or entity not in self.lineage_graph:
            return []
        
        visited.add(entity)
        upstream = []
        
        for source in self.lineage_graph[entity]['upstream']:
            upstream.append(source)
            upstream.extend(self.get_upstream_sources(source, visited))
        
        return list(set(upstream))
```

---

*This comprehensive data integration framework provides complete multi-source coordination, real-time processing, and enterprise data management capabilities for PyMapGIS logistics applications.*
