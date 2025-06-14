# 🧪 Testing and Validation

## Comprehensive Quality Assurance for Logistics Applications

This guide provides complete testing and validation frameworks for PyMapGIS logistics applications, covering unit testing, integration testing, performance testing, and quality assurance procedures.

### 1. Testing Framework Architecture

#### Test Pyramid Structure
```
End-to-End Tests (10%)
├── User Journey Tests
├── System Integration Tests
└── Performance Tests

Integration Tests (20%)
├── API Integration Tests
├── Database Integration Tests
├── External Service Tests
└── Container Integration Tests

Unit Tests (70%)
├── Algorithm Tests
├── Data Processing Tests
├── Business Logic Tests
└── Utility Function Tests
```

#### Testing Technology Stack
```python
# Core testing frameworks
import pytest
import unittest
from unittest.mock import Mock, patch, MagicMock
import asyncio
import aiohttp
import requests

# Testing utilities
from faker import Faker
import factory
from hypothesis import given, strategies as st
import parameterized

# Performance testing
import locust
from locust import HttpUser, task, between

# Database testing
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import pytest_postgresql

# Container testing
import docker
import testcontainers
from testcontainers.postgres import PostgresContainer

fake = Faker()
```

### 2. Unit Testing for Logistics Algorithms

#### Route Optimization Testing
```python
import pytest
import pymapgis as pmg
from pymapgis.logistics import RouteOptimizer
import numpy as np

class TestRouteOptimization:

    @pytest.fixture
    def sample_customers(self):
        """Generate sample customer data for testing."""
        return [
            {'id': 1, 'lat': 40.7128, 'lon': -74.0060, 'demand': 100},
            {'id': 2, 'lat': 40.7589, 'lon': -73.9851, 'demand': 150},
            {'id': 3, 'lat': 40.6892, 'lon': -74.0445, 'demand': 200},
            {'id': 4, 'lat': 40.7505, 'lon': -73.9934, 'demand': 120},
            {'id': 5, 'lat': 40.7282, 'lon': -73.7949, 'demand': 180}
        ]

    @pytest.fixture
    def sample_vehicles(self):
        """Generate sample vehicle data for testing."""
        return [
            {'id': 'V1', 'capacity': 1000, 'cost_per_km': 0.5},
            {'id': 'V2', 'capacity': 800, 'cost_per_km': 0.4}
        ]

    @pytest.fixture
    def depot_location(self):
        """Sample depot location."""
        return {'lat': 40.7128, 'lon': -74.0060}

    def test_basic_route_optimization(self, sample_customers, sample_vehicles, depot_location):
        """Test basic route optimization functionality."""
        optimizer = RouteOptimizer(algorithm='nearest_neighbor')

        routes = optimizer.solve(
            customers=sample_customers,
            vehicles=sample_vehicles,
            depot=depot_location
        )

        # Validate results
        assert len(routes) <= len(sample_vehicles)
        assert all(route.total_demand <= route.vehicle.capacity for route in routes)
        assert sum(len(route.customers) for route in routes) == len(sample_customers)

    def test_capacity_constraints(self, sample_customers, sample_vehicles, depot_location):
        """Test that capacity constraints are respected."""
        # Create vehicles with limited capacity
        limited_vehicles = [
            {'id': 'V1', 'capacity': 250, 'cost_per_km': 0.5},
            {'id': 'V2', 'capacity': 250, 'cost_per_km': 0.4}
        ]

        optimizer = RouteOptimizer(algorithm='clarke_wright')
        routes = optimizer.solve(
            customers=sample_customers,
            vehicles=limited_vehicles,
            depot=depot_location
        )

        # Check capacity constraints
        for route in routes:
            total_demand = sum(customer['demand'] for customer in route.customers)
            assert total_demand <= route.vehicle['capacity']

    @pytest.mark.parametrize("algorithm", [
        'nearest_neighbor',
        'clarke_wright',
        'genetic_algorithm',
        'simulated_annealing'
    ])
    def test_algorithm_consistency(self, algorithm, sample_customers, sample_vehicles, depot_location):
        """Test that different algorithms produce valid solutions."""
        optimizer = RouteOptimizer(algorithm=algorithm, time_limit=30)

        routes = optimizer.solve(
            customers=sample_customers,
            vehicles=sample_vehicles,
            depot=depot_location
        )

        # Basic validation
        assert routes is not None
        assert len(routes) > 0
        assert all(hasattr(route, 'total_distance') for route in routes)
        assert all(hasattr(route, 'total_time') for route in routes)

    def test_empty_customer_list(self, sample_vehicles, depot_location):
        """Test handling of empty customer list."""
        optimizer = RouteOptimizer()

        routes = optimizer.solve(
            customers=[],
            vehicles=sample_vehicles,
            depot=depot_location
        )

        assert routes == []

    def test_single_customer(self, sample_vehicles, depot_location):
        """Test optimization with single customer."""
        single_customer = [{'id': 1, 'lat': 40.7589, 'lon': -73.9851, 'demand': 100}]

        optimizer = RouteOptimizer()
        routes = optimizer.solve(
            customers=single_customer,
            vehicles=sample_vehicles,
            depot=depot_location
        )

        assert len(routes) == 1
        assert len(routes[0].customers) == 1
        assert routes[0].customers[0]['id'] == 1

    @given(
        num_customers=st.integers(min_value=1, max_value=20),
        num_vehicles=st.integers(min_value=1, max_value=5)
    )
    def test_property_based_optimization(self, num_customers, num_vehicles):
        """Property-based testing for route optimization."""
        # Generate random customers and vehicles
        customers = [
            {
                'id': i,
                'lat': fake.latitude(),
                'lon': fake.longitude(),
                'demand': fake.random_int(min=10, max=200)
            }
            for i in range(num_customers)
        ]

        vehicles = [
            {
                'id': f'V{i}',
                'capacity': fake.random_int(min=500, max=2000),
                'cost_per_km': fake.random.uniform(0.3, 0.8)
            }
            for i in range(num_vehicles)
        ]

        depot = {'lat': fake.latitude(), 'lon': fake.longitude()}

        optimizer = RouteOptimizer(algorithm='nearest_neighbor')
        routes = optimizer.solve(customers=customers, vehicles=vehicles, depot=depot)

        # Properties that should always hold
        total_customers_in_routes = sum(len(route.customers) for route in routes)
        assert total_customers_in_routes == len(customers)

        for route in routes:
            route_demand = sum(customer['demand'] for customer in route.customers)
            assert route_demand <= route.vehicle['capacity']
```

#### Facility Location Testing
```python
class TestFacilityLocation:

    @pytest.fixture
    def sample_demand_points(self):
        """Generate sample demand points."""
        return [
            {'id': 1, 'lat': 40.7128, 'lon': -74.0060, 'demand': 1000},
            {'id': 2, 'lat': 40.7589, 'lon': -73.9851, 'demand': 800},
            {'id': 3, 'lat': 40.6892, 'lon': -74.0445, 'demand': 1200},
            {'id': 4, 'lat': 40.7505, 'lon': -73.9934, 'demand': 600},
            {'id': 5, 'lat': 40.7282, 'lon': -73.7949, 'demand': 900}
        ]

    @pytest.fixture
    def candidate_locations(self):
        """Generate candidate facility locations."""
        return [
            {'id': 'F1', 'lat': 40.7300, 'lon': -74.0000, 'capacity': 2000, 'cost': 100000},
            {'id': 'F2', 'lat': 40.7400, 'lon': -73.9900, 'capacity': 1500, 'cost': 80000},
            {'id': 'F3', 'lat': 40.7000, 'lon': -74.0200, 'capacity': 2500, 'cost': 120000}
        ]

    def test_p_median_optimization(self, sample_demand_points, candidate_locations):
        """Test p-median facility location optimization."""
        optimizer = pmg.FacilityLocationOptimizer(problem_type='p_median')

        selected_facilities = optimizer.solve(
            demand_points=sample_demand_points,
            candidate_locations=candidate_locations,
            num_facilities=2
        )

        assert len(selected_facilities) == 2
        assert all(facility['id'] in [loc['id'] for loc in candidate_locations]
                  for facility in selected_facilities)

    def test_capacity_constraints(self, sample_demand_points, candidate_locations):
        """Test facility capacity constraints."""
        optimizer = pmg.FacilityLocationOptimizer(
            problem_type='capacitated',
            enforce_capacity=True
        )

        solution = optimizer.solve(
            demand_points=sample_demand_points,
            candidate_locations=candidate_locations,
            num_facilities=2
        )

        # Check capacity constraints
        for facility in solution['selected_facilities']:
            assigned_demand = sum(
                point['demand'] for point in solution['assignments']
                if solution['assignments'][point['id']] == facility['id']
            )
            assert assigned_demand <= facility['capacity']

    def test_service_distance_constraints(self, sample_demand_points, candidate_locations):
        """Test maximum service distance constraints."""
        max_service_distance = 10000  # 10km

        optimizer = pmg.FacilityLocationOptimizer(
            max_service_distance=max_service_distance
        )

        solution = optimizer.solve(
            demand_points=sample_demand_points,
            candidate_locations=candidate_locations,
            num_facilities=3
        )

        # Check service distance constraints
        for point_id, facility_id in solution['assignments'].items():
            point = next(p for p in sample_demand_points if p['id'] == point_id)
            facility = next(f for f in solution['selected_facilities'] if f['id'] == facility_id)

            distance = pmg.distance(
                (point['lat'], point['lon']),
                (facility['lat'], facility['lon'])
            ).meters

            assert distance <= max_service_distance
```

### 3. Integration Testing

#### API Integration Testing
```python
import pytest
import asyncio
from httpx import AsyncClient
from fastapi.testclient import TestClient
from main import app

class TestLogisticsAPI:

    @pytest.fixture
    def client(self):
        """Create test client."""
        return TestClient(app)

    @pytest.fixture
    async def async_client(self):
        """Create async test client."""
        async with AsyncClient(app=app, base_url="http://test") as ac:
            yield ac

    def test_health_endpoint(self, client):
        """Test API health check endpoint."""
        response = client.get("/api/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"

    def test_create_vehicle(self, client):
        """Test vehicle creation endpoint."""
        vehicle_data = {
            "vehicle_id": "TEST-001",
            "type": "truck",
            "capacity_weight": 5000,
            "capacity_volume": 25,
            "fuel_type": "diesel"
        }

        response = client.post("/api/vehicles", json=vehicle_data)
        assert response.status_code == 200

        created_vehicle = response.json()
        assert created_vehicle["vehicle_id"] == "TEST-001"
        assert created_vehicle["type"] == "truck"

    def test_get_vehicles(self, client):
        """Test vehicle listing endpoint."""
        response = client.get("/api/vehicles")
        assert response.status_code == 200

        vehicles = response.json()
        assert isinstance(vehicles, list)

    def test_route_optimization_endpoint(self, client):
        """Test route optimization endpoint."""
        optimization_request = {
            "customers": [
                {"id": 1, "lat": 40.7128, "lon": -74.0060, "demand": 100},
                {"id": 2, "lat": 40.7589, "lon": -73.9851, "demand": 150}
            ],
            "vehicles": [
                {"id": "V1", "capacity": 1000, "cost_per_km": 0.5}
            ],
            "depot_location": {"lat": 40.7128, "lon": -74.0060}
        }

        response = client.post("/api/optimize/routes", json=optimization_request)
        assert response.status_code == 200

        result = response.json()
        assert "routes" in result
        assert "total_distance" in result
        assert "total_time" in result

    @pytest.mark.asyncio
    async def test_websocket_connection(self, async_client):
        """Test WebSocket connection for real-time updates."""
        async with async_client.websocket_connect("/ws/test-client") as websocket:
            # Send subscription message
            await websocket.send_json({
                "type": "subscribe_vehicle",
                "vehicle_id": "TEST-001"
            })

            # Should receive acknowledgment
            response = await websocket.receive_json()
            assert response["type"] == "subscription_confirmed"

    def test_authentication_required(self, client):
        """Test that protected endpoints require authentication."""
        response = client.post("/api/vehicles", json={})
        assert response.status_code == 401

    def test_invalid_data_handling(self, client):
        """Test API handling of invalid data."""
        invalid_vehicle_data = {
            "vehicle_id": "",  # Invalid empty ID
            "type": "truck",
            "capacity_weight": -100,  # Invalid negative capacity
            "fuel_type": "diesel"
        }

        response = client.post("/api/vehicles", json=invalid_vehicle_data)
        assert response.status_code == 422  # Validation error
```

#### Database Integration Testing
```python
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from testcontainers.postgres import PostgresContainer
from database import Base, Vehicle, Route, Customer

class TestDatabaseIntegration:

    @pytest.fixture(scope="class")
    def postgres_container(self):
        """Start PostgreSQL container for testing."""
        with PostgresContainer("postgres:13") as postgres:
            yield postgres

    @pytest.fixture
    def db_session(self, postgres_container):
        """Create database session for testing."""
        engine = create_engine(postgres_container.get_connection_url())
        Base.metadata.create_all(engine)

        SessionLocal = sessionmaker(bind=engine)
        session = SessionLocal()

        yield session

        session.close()

    def test_vehicle_crud_operations(self, db_session):
        """Test vehicle CRUD operations."""
        # Create
        vehicle = Vehicle(
            vehicle_id="TEST-001",
            type="truck",
            capacity_weight=5000,
            capacity_volume=25,
            fuel_type="diesel"
        )
        db_session.add(vehicle)
        db_session.commit()

        # Read
        retrieved_vehicle = db_session.query(Vehicle).filter(
            Vehicle.vehicle_id == "TEST-001"
        ).first()
        assert retrieved_vehicle is not None
        assert retrieved_vehicle.type == "truck"

        # Update
        retrieved_vehicle.status = "in_use"
        db_session.commit()

        updated_vehicle = db_session.query(Vehicle).filter(
            Vehicle.vehicle_id == "TEST-001"
        ).first()
        assert updated_vehicle.status == "in_use"

        # Delete
        db_session.delete(updated_vehicle)
        db_session.commit()

        deleted_vehicle = db_session.query(Vehicle).filter(
            Vehicle.vehicle_id == "TEST-001"
        ).first()
        assert deleted_vehicle is None

    def test_route_vehicle_relationship(self, db_session):
        """Test relationship between routes and vehicles."""
        # Create vehicle
        vehicle = Vehicle(
            vehicle_id="TEST-002",
            type="van",
            capacity_weight=2000,
            fuel_type="electric"
        )
        db_session.add(vehicle)
        db_session.commit()

        # Create route
        route = Route(
            route_name="Test Route",
            vehicle_id=vehicle.id,
            total_distance=50.5,
            total_time=120,
            status="planned"
        )
        db_session.add(route)
        db_session.commit()

        # Test relationship
        retrieved_route = db_session.query(Route).filter(
            Route.route_name == "Test Route"
        ).first()
        assert retrieved_route.vehicle.vehicle_id == "TEST-002"
        assert retrieved_route.vehicle.type == "van"

    def test_spatial_queries(self, db_session):
        """Test spatial database queries."""
        # Create customers with locations
        customer1 = Customer(
            name="Customer 1",
            latitude=40.7128,
            longitude=-74.0060,
            demand=100
        )
        customer2 = Customer(
            name="Customer 2",
            latitude=40.7589,
            longitude=-73.9851,
            demand=150
        )

        db_session.add_all([customer1, customer2])
        db_session.commit()

        # Test spatial query (customers within bounding box)
        customers_in_area = db_session.query(Customer).filter(
            Customer.latitude.between(40.7000, 40.8000),
            Customer.longitude.between(-74.1000, -73.9000)
        ).all()

        assert len(customers_in_area) == 2
```

### 4. Performance Testing

#### Load Testing with Locust
```python
from locust import HttpUser, task, between
import random
import json

class LogisticsAPIUser(HttpUser):
    wait_time = between(1, 3)

    def on_start(self):
        """Setup for each user."""
        self.vehicle_ids = []
        self.create_test_vehicles()

    def create_test_vehicles(self):
        """Create test vehicles for load testing."""
        for i in range(5):
            vehicle_data = {
                "vehicle_id": f"LOAD-TEST-{self.user_id}-{i}",
                "type": random.choice(["truck", "van"]),
                "capacity_weight": random.randint(1000, 5000),
                "capacity_volume": random.randint(10, 30),
                "fuel_type": random.choice(["diesel", "electric", "gasoline"])
            }

            response = self.client.post("/api/vehicles", json=vehicle_data)
            if response.status_code == 200:
                self.vehicle_ids.append(vehicle_data["vehicle_id"])

    @task(3)
    def get_vehicles(self):
        """Test vehicle listing performance."""
        self.client.get("/api/vehicles")

    @task(2)
    def get_specific_vehicle(self):
        """Test specific vehicle retrieval."""
        if self.vehicle_ids:
            vehicle_id = random.choice(self.vehicle_ids)
            self.client.get(f"/api/vehicles/{vehicle_id}")

    @task(1)
    def optimize_routes(self):
        """Test route optimization performance."""
        customers = [
            {
                "id": i,
                "lat": 40.7128 + random.uniform(-0.1, 0.1),
                "lon": -74.0060 + random.uniform(-0.1, 0.1),
                "demand": random.randint(50, 200)
            }
            for i in range(random.randint(5, 15))
        ]

        vehicles = [
            {
                "id": f"V{i}",
                "capacity": random.randint(800, 1500),
                "cost_per_km": random.uniform(0.3, 0.7)
            }
            for i in range(random.randint(2, 4))
        ]

        optimization_request = {
            "customers": customers,
            "vehicles": vehicles,
            "depot_location": {"lat": 40.7128, "lon": -74.0060}
        }

        with self.client.post(
            "/api/optimize/routes",
            json=optimization_request,
            catch_response=True
        ) as response:
            if response.elapsed.total_seconds() > 30:
                response.failure("Route optimization took too long")

    @task(1)
    def update_vehicle_location(self):
        """Test real-time location updates."""
        if self.vehicle_ids:
            vehicle_id = random.choice(self.vehicle_ids)
            location_data = {
                "latitude": 40.7128 + random.uniform(-0.05, 0.05),
                "longitude": -74.0060 + random.uniform(-0.05, 0.05),
                "speed": random.uniform(0, 80),
                "heading": random.uniform(0, 360),
                "timestamp": "2023-01-01T12:00:00Z"
            }

            self.client.post(
                f"/api/vehicles/{vehicle_id}/location",
                json=location_data
            )

# Performance benchmarks
class PerformanceBenchmarks:

    @pytest.mark.performance
    def test_route_optimization_performance(self):
        """Benchmark route optimization performance."""
        import time

        # Small problem (10 customers, 2 vehicles)
        small_customers = [
            {'id': i, 'lat': 40.7128 + i*0.01, 'lon': -74.0060 + i*0.01, 'demand': 100}
            for i in range(10)
        ]
        small_vehicles = [
            {'id': 'V1', 'capacity': 1000},
            {'id': 'V2', 'capacity': 1000}
        ]

        optimizer = pmg.RouteOptimizer(algorithm='nearest_neighbor')
        start_time = time.time()
        routes = optimizer.solve(
            customers=small_customers,
            vehicles=small_vehicles,
            depot={'lat': 40.7128, 'lon': -74.0060}
        )
        small_time = time.time() - start_time

        assert small_time < 1.0  # Should complete in under 1 second

        # Medium problem (50 customers, 5 vehicles)
        medium_customers = [
            {'id': i, 'lat': 40.7128 + i*0.001, 'lon': -74.0060 + i*0.001, 'demand': 100}
            for i in range(50)
        ]
        medium_vehicles = [
            {'id': f'V{i}', 'capacity': 1000}
            for i in range(5)
        ]

        start_time = time.time()
        routes = optimizer.solve(
            customers=medium_customers,
            vehicles=medium_vehicles,
            depot={'lat': 40.7128, 'lon': -74.0060}
        )
        medium_time = time.time() - start_time

        assert medium_time < 10.0  # Should complete in under 10 seconds

    @pytest.mark.performance
    def test_api_response_times(self):
        """Test API response time requirements."""
        client = TestClient(app)

        # Health check should be very fast
        start_time = time.time()
        response = client.get("/api/health")
        health_time = time.time() - start_time

        assert response.status_code == 200
        assert health_time < 0.1  # Under 100ms

        # Vehicle listing should be fast
        start_time = time.time()
        response = client.get("/api/vehicles?limit=100")
        list_time = time.time() - start_time

        assert response.status_code == 200
        assert list_time < 1.0  # Under 1 second
```

---

*This comprehensive testing and validation guide provides complete quality assurance frameworks for PyMapGIS logistics applications with focus on reliability, performance, and maintainability.*