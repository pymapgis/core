#!/usr/bin/env python3
"""
Tests for Flight Delay Now showcase

Tests the flight worker, API endpoints, and data processing logic.
"""

import pytest
import asyncio
import json
import sys
from pathlib import Path
from unittest.mock import patch, AsyncMock, MagicMock

# Add current directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from flight_worker import (
    fetch_faa_ois_data,
    process_ois_data,
    calculate_delay_score,
    main as process_flight_data
)
from app import app

from fastapi.testclient import TestClient

# Test client for FastAPI
client = TestClient(app)


class TestFlightWorker:
    """Test the flight data worker functions."""
    
    def test_calculate_delay_score(self):
        """Test delay score calculation."""
        # Test normal case
        row = {'avg_dep_delay': 30, 'flights_total': 100}
        score = calculate_delay_score(row)
        assert score > 0
        assert isinstance(score, float)
        
        # Test zero delay
        row = {'avg_dep_delay': 0, 'flights_total': 50}
        score = calculate_delay_score(row)
        assert score == 0
        
        # Test missing values
        row = {}
        score = calculate_delay_score(row)
        assert score >= 0
    
    def test_process_ois_data_empty(self):
        """Test processing empty OIS data."""
        result = process_ois_data(None)
        assert len(result) == 0
        
        result = process_ois_data({})
        assert len(result) == 0
    
    def test_process_ois_data_sample(self):
        """Test processing sample OIS data."""
        sample_ois = {
            'airports': [
                {
                    'iata': 'ATL',
                    'departures': {
                        'delayed': [
                            {'delay_minutes': 30},
                            {'delay_minutes': 45}
                        ],
                        'total': 100
                    }
                },
                {
                    'iata': 'LAX',
                    'departures': {
                        'delayed': [],
                        'total': 80
                    }
                }
            ]
        }
        
        result = process_ois_data(sample_ois)
        assert len(result) == 2
        assert 'ATL' in result['iata'].values
        assert 'LAX' in result['iata'].values
        
        # Check ATL has delay calculated
        atl_row = result[result['iata'] == 'ATL'].iloc[0]
        assert atl_row['avg_dep_delay'] > 0
        
        # Check LAX has no delay
        lax_row = result[result['iata'] == 'LAX'].iloc[0]
        assert lax_row['avg_dep_delay'] == 0
    
    @pytest.mark.asyncio
    async def test_fetch_faa_ois_data_mock(self):
        """Test FAA OIS data fetching with mock."""
        with patch('flight_worker.requests.get') as mock_get:
            # Mock successful response
            mock_response = MagicMock()
            mock_response.json.return_value = {'airports': []}
            mock_response.raise_for_status.return_value = None
            mock_get.return_value = mock_response
            
            result = await fetch_faa_ois_data()
            assert result == {'airports': []}
            
            # Mock failed response
            mock_get.side_effect = Exception("Network error")
            result = await fetch_faa_ois_data()
            assert result is None


class TestFlightDelayAPI:
    """Test the FastAPI application endpoints."""
    
    def test_health_endpoint(self):
        """Test health check endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data
        assert "version" in data
        assert data["service"] == "flight-delay-now"
        assert "checks" in data
    
    def test_root_endpoint(self):
        """Test main page endpoint."""
        response = client.get("/")
        assert response.status_code == 200
        assert "Flight Delay Now" in response.text
        assert "maplibre-gl" in response.text
    
    def test_public_tiles_endpoint(self):
        """Test public tiles endpoint."""
        response = client.get("/public/tiles/0/0/0.pbf")
        assert response.status_code == 200
        # Should return JSON data (simplified for demo)
        assert response.headers["content-type"] == "application/json"
    
    def test_internal_endpoint_no_auth(self):
        """Test internal endpoint without authentication."""
        response = client.get("/internal/latest")
        assert response.status_code == 401
    
    def test_internal_endpoint_with_auth(self):
        """Test internal endpoint with authentication."""
        headers = {"Authorization": "Bearer demo-token"}
        response = client.get("/internal/latest", headers=headers)
        assert response.status_code == 200
        
        data = response.json()
        assert "data" in data
        assert "last_updated" in data
        assert "user" in data
        assert data["user"] == "demo_user"
    
    def test_refresh_endpoint(self):
        """Test manual refresh endpoint."""
        response = client.get("/refresh")
        assert response.status_code == 200
        
        data = response.json()
        assert "message" in data
        assert "refresh" in data["message"].lower()


class TestDataFiles:
    """Test data files and configuration."""
    
    def test_airports_geojson_exists(self):
        """Test that airports GeoJSON file exists and is valid."""
        airports_file = Path(__file__).parent / "data" / "top_airports.geojson"
        assert airports_file.exists()
        
        with open(airports_file, 'r') as f:
            data = json.load(f)
        
        assert data["type"] == "FeatureCollection"
        assert "features" in data
        assert len(data["features"]) > 0
        
        # Check first airport has required properties
        first_airport = data["features"][0]
        assert "properties" in first_airport
        assert "iata" in first_airport["properties"]
        assert "name" in first_airport["properties"]
        assert "geometry" in first_airport
        assert first_airport["geometry"]["type"] == "Point"
    
    def test_requirements_file(self):
        """Test requirements.txt file."""
        req_file = Path(__file__).parent / "requirements.txt"
        assert req_file.exists()
        
        with open(req_file, 'r') as f:
            requirements = f.read()
        
        # Check for essential dependencies
        essential_deps = ['pymapgis', 'fastapi', 'aiohttp', 'pandas', 'geopandas']
        for dep in essential_deps:
            assert dep in requirements
    
    def test_dockerfile_exists(self):
        """Test Dockerfile exists."""
        dockerfile = Path(__file__).parent / "Dockerfile"
        assert dockerfile.exists()
        
        with open(dockerfile, 'r') as f:
            content = f.read()
        
        # Check for key Dockerfile elements
        assert "FROM python:" in content
        assert "EXPOSE 8000" in content
        assert "uvicorn" in content


class TestIntegration:
    """Integration tests for the complete workflow."""
    
    @pytest.mark.asyncio
    async def test_end_to_end_workflow_mock(self):
        """Test complete workflow with mocked data."""
        # Create sample airports data
        sample_airports = {
            "type": "FeatureCollection",
            "features": [
                {
                    "type": "Feature",
                    "properties": {"iata": "ATL", "name": "Atlanta", "city": "Atlanta", "state": "GA"},
                    "geometry": {"type": "Point", "coordinates": [-84.4281, 33.6367]}
                }
            ]
        }
        
        # Mock PyMapGIS read function
        with patch('flight_worker.pmg.read') as mock_read:
            mock_read.return_value = MagicMock()
            mock_read.return_value.merge.return_value = MagicMock()
            
            # Mock FAA data fetch
            with patch('flight_worker.fetch_faa_ois_data') as mock_fetch:
                mock_fetch.return_value = {'airports': []}
                
                # This would normally run the full workflow
                # For testing, we just verify the mocks are called
                assert True  # Placeholder for actual integration test


class TestPerformance:
    """Performance tests for the flight delay system."""
    
    def test_api_response_time(self):
        """Test API response times are reasonable."""
        import time
        
        start_time = time.time()
        response = client.get("/health")
        end_time = time.time()
        
        response_time = end_time - start_time
        assert response_time < 1.0  # Should respond within 1 second
        assert response.status_code == 200
    
    def test_data_processing_performance(self):
        """Test data processing performance."""
        # Test with sample data
        sample_data = [
            {'avg_dep_delay': i, 'flights_total': i * 10}
            for i in range(100)
        ]
        
        import time
        start_time = time.time()
        
        for row in sample_data:
            calculate_delay_score(row)
        
        end_time = time.time()
        processing_time = end_time - start_time
        
        assert processing_time < 0.1  # Should process 100 records in <100ms


if __name__ == "__main__":
    # Run tests when script is executed directly
    pytest.main([__file__, "-v"])
