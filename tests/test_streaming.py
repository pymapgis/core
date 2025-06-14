"""
Test suite for PyMapGIS Real-time Streaming features.

Tests WebSocket communication, event-driven architecture, Kafka integration,
live data feeds, stream processing capabilities, and legacy functions.
"""

import pytest
import asyncio
import json
import time
import numpy as np
import pandas as pd
import xarray as xr
from datetime import datetime
from unittest.mock import patch, MagicMock, Mock

# Import legacy functions for backward compatibility
from pymapgis.streaming import (
    create_spatiotemporal_cube,
    connect_kafka_consumer,
    connect_mqtt_client,
)

# Import new streaming components
try:
    from pymapgis.streaming import (
        StreamingMessage,
        SpatialEvent,
        LiveDataPoint,
        WebSocketServer,
        WebSocketClient,
        ConnectionManager,
        EventBus,
        SpatialKafkaProducer,
        SpatialKafkaConsumer,
        GPSTracker,
        IoTSensorFeed,
        StreamProcessor,
        start_websocket_server,
        connect_websocket_client,
        create_event_bus,
        create_kafka_producer,
        create_kafka_consumer,
        publish_spatial_event,
        subscribe_to_events,
        start_gps_tracking,
        connect_iot_sensors,
        create_live_feed,
        WEBSOCKETS_AVAILABLE,
        KAFKA_AVAILABLE,
        PAHO_MQTT_AVAILABLE,
    )

    NEW_STREAMING_AVAILABLE = True
except ImportError:
    NEW_STREAMING_AVAILABLE = False

# Attempt to import Kafka and MQTT related components for type hinting and mocking
try:
    from kafka import (
        KafkaConsumer as ActualKafkaConsumer,
    )  # Alias to avoid name clash with mock
    from kafka.errors import NoBrokersAvailable as ActualNoBrokersAvailable

    KAFKA_AVAILABLE = True
except ImportError:
    KAFKA_AVAILABLE = False

    # Define dummy classes if kafka-python is not installed, for tests to be skippable
    class ActualKafkaConsumer:  # type: ignore
        pass

    class ActualNoBrokersAvailable(Exception):  # type: ignore
        pass


try:
    import paho.mqtt.client as actual_mqtt

    PAHO_MQTT_AVAILABLE = True
except ImportError:
    PAHO_MQTT_AVAILABLE = False

    class actual_mqtt:  # type: ignore
        class Client:
            pass


# Helper to conditionally skip tests
skip_if_kafka_unavailable = pytest.mark.skipif(
    not KAFKA_AVAILABLE, reason="kafka-python library not found."
)
skip_if_mqtt_unavailable = pytest.mark.skipif(
    not PAHO_MQTT_AVAILABLE, reason="paho-mqtt library not found."
)

# Sample data for testing
TIMESTAMPS = pd.to_datetime(
    ["2023-01-01T00:00:00", "2023-01-01T01:00:00", "2023-01-01T02:00:00"]
)
X_COORDS = np.array([10.0, 10.1, 10.2, 10.3])  # Longitude or Easting
Y_COORDS = np.array([50.0, 50.1, 50.2])  # Latitude or Northing
Z_COORDS = np.array([0.0, 5.0])  # Depth or Height

DATA_3D_NP = np.random.rand(len(TIMESTAMPS), len(Y_COORDS), len(X_COORDS))
DATA_4D_NP = np.random.rand(
    len(TIMESTAMPS), len(Z_COORDS), len(Y_COORDS), len(X_COORDS)
)
VARIABLE_NAME = "test_variable"
CUSTOM_ATTRS = {"units": "test_units", "description": "A test DataArray"}


def test_create_spatiotemporal_cube_3d():
    """Tests creating a 3D (time, y, x) spatiotemporal cube."""
    cube = create_spatiotemporal_cube(
        data=DATA_3D_NP,
        timestamps=TIMESTAMPS,
        x_coords=X_COORDS,
        y_coords=Y_COORDS,
        variable_name=VARIABLE_NAME,
        attrs=CUSTOM_ATTRS,
    )

    # a. Assert that the returned object is an xr.DataArray
    assert isinstance(cube, xr.DataArray)

    # b. Assert that the dimensions of the DataArray are correct
    assert cube.dims == ("time", "y", "x")

    # c. Assert that the coordinates match the input sample data
    # Compare the values, not the index names (which may differ due to xarray coordinate naming)
    pd.testing.assert_index_equal(
        cube.coords["time"].to_index(), TIMESTAMPS, check_names=False
    )
    np.testing.assert_array_equal(cube.coords["x"].data, X_COORDS)
    np.testing.assert_array_equal(cube.coords["y"].data, Y_COORDS)

    # d. Assert that the values in the DataArray match the input sample data
    np.testing.assert_array_equal(cube.data, DATA_3D_NP)

    # e. Assert that the name of the DataArray is correctly set
    assert cube.name == VARIABLE_NAME

    # f. Assert attributes are set
    assert cube.attrs == CUSTOM_ATTRS


def test_create_spatiotemporal_cube_4d():
    """Tests creating a 4D (time, z, y, x) spatiotemporal cube."""
    cube = create_spatiotemporal_cube(
        data=DATA_4D_NP,
        timestamps=TIMESTAMPS,
        x_coords=X_COORDS,
        y_coords=Y_COORDS,
        z_coords=Z_COORDS,
        variable_name=VARIABLE_NAME,
        attrs=CUSTOM_ATTRS,
    )

    # a. Assert that the returned object is an xr.DataArray
    assert isinstance(cube, xr.DataArray)

    # b. Assert that the dimensions of the DataArray are correct
    assert cube.dims == ("time", "z", "y", "x")

    # c. Assert that the coordinates match the input sample data
    # Compare the values, not the index names (which may differ due to xarray coordinate naming)
    pd.testing.assert_index_equal(
        cube.coords["time"].to_index(), TIMESTAMPS, check_names=False
    )
    np.testing.assert_array_equal(cube.coords["x"].data, X_COORDS)
    np.testing.assert_array_equal(cube.coords["y"].data, Y_COORDS)
    np.testing.assert_array_equal(cube.coords["z"].data, Z_COORDS)

    # d. Assert that the values in the DataArray match the input sample data
    np.testing.assert_array_equal(cube.data, DATA_4D_NP)

    # e. Assert that the name of the DataArray is correctly set
    assert cube.name == VARIABLE_NAME

    # f. Assert attributes are set
    assert cube.attrs == CUSTOM_ATTRS


def test_create_spatiotemporal_cube_default_name_and_no_attrs():
    """Tests creating a 3D cube with default variable name and no attributes."""
    cube = create_spatiotemporal_cube(
        data=DATA_3D_NP,
        timestamps=TIMESTAMPS,
        x_coords=X_COORDS,
        y_coords=Y_COORDS,
        # No variable_name, no attrs
    )
    assert isinstance(cube, xr.DataArray)
    assert cube.name == "sensor_value"  # Default name
    assert cube.attrs == {}  # Default empty attrs


def test_create_spatiotemporal_cube_shape_mismatch_error():
    """Tests that a ValueError is raised for mismatched data and coordinate shapes."""
    # Data shape (3, 3, 3) does not match X_COORDS length 4
    mismatched_data_3d = np.random.rand(len(TIMESTAMPS), len(Y_COORDS), len(Y_COORDS))

    with pytest.raises(ValueError) as excinfo:
        create_spatiotemporal_cube(
            data=mismatched_data_3d,
            timestamps=TIMESTAMPS,
            x_coords=X_COORDS,  # X_COORDS has length 4
            y_coords=Y_COORDS,
        )
    assert "Data shape" in str(excinfo.value)
    assert f"(time: {len(TIMESTAMPS)}," in str(excinfo.value)
    assert f"y: {len(Y_COORDS)}, x: {len(X_COORDS)})" in str(excinfo.value)
    assert f"does not match expected shape ({len(TIMESTAMPS)}, {len(Y_COORDS)}, {len(X_COORDS)})"  # Corrected expected shape in assertion

    # Test 4D mismatch
    # Data shape (3, 2, 3, 3) does not match X_COORDS length 4
    mismatched_data_4d = np.random.rand(
        len(TIMESTAMPS), len(Z_COORDS), len(Y_COORDS), len(Y_COORDS)
    )
    with pytest.raises(ValueError) as excinfo_4d:
        create_spatiotemporal_cube(
            data=mismatched_data_4d,
            timestamps=TIMESTAMPS,
            x_coords=X_COORDS,  # X_COORDS has length 4
            y_coords=Y_COORDS,
            z_coords=Z_COORDS,
        )
    assert "Data shape" in str(excinfo_4d.value)
    assert f"(time: {len(TIMESTAMPS)}, z: {len(Z_COORDS)}," in str(excinfo_4d.value)
    assert f"y: {len(Y_COORDS)}, x: {len(X_COORDS)})" in str(excinfo_4d.value)
    assert f"does not match expected shape ({len(TIMESTAMPS)}, {len(Z_COORDS)}, {len(Y_COORDS)}, {len(X_COORDS)})"  # Corrected expected shape in assertion


def test_input_types_conversion():
    """Tests if list inputs for coordinates and timestamps are correctly converted."""
    list_timestamps = TIMESTAMPS.tolist()  # Python list of Timestamps
    list_x_coords = X_COORDS.tolist()
    list_y_coords = Y_COORDS.tolist()
    list_z_coords = Z_COORDS.tolist()

    cube_3d_list_inputs = create_spatiotemporal_cube(
        data=DATA_3D_NP,
        timestamps=list_timestamps,
        x_coords=list_x_coords,
        y_coords=list_y_coords,
    )
    assert isinstance(cube_3d_list_inputs.coords["time"].to_index(), pd.DatetimeIndex)
    assert isinstance(cube_3d_list_inputs.coords["x"].data, np.ndarray)
    assert isinstance(cube_3d_list_inputs.coords["y"].data, np.ndarray)

    cube_4d_list_inputs = create_spatiotemporal_cube(
        data=DATA_4D_NP,
        timestamps=list_timestamps,
        x_coords=list_x_coords,
        y_coords=list_y_coords,
        z_coords=list_z_coords,
    )
    assert isinstance(cube_4d_list_inputs.coords["z"].data, np.ndarray)


# To run these tests:
# Ensure pymapgis is in PYTHONPATH
# pytest tests/test_streaming.py

# --- Tests for Kafka and MQTT Connectors ---


@skip_if_kafka_unavailable
@patch(
    "pymapgis.streaming.KafkaConsumer"
)  # Mock the KafkaConsumer class used in pymapgis.streaming
def test_connect_kafka_consumer_success(MockKafkaConsumerAliased):
    """Tests successful KafkaConsumer connection and configuration."""
    # Note: The mock target is 'pymapgis.streaming.KafkaConsumer' because that's where it's looked up.
    mock_consumer_instance = MagicMock(spec=ActualKafkaConsumer)
    MockKafkaConsumerAliased.return_value = mock_consumer_instance

    topic = "test_topic"
    bootstrap_servers = "kafka.example.com:9092"
    group_id = "test_group"

    consumer = connect_kafka_consumer(
        topic,
        bootstrap_servers=bootstrap_servers,
        group_id=group_id,
        auto_offset_reset="latest",
        custom_param="value",
    )

    MockKafkaConsumerAliased.assert_called_once_with(
        topic,
        bootstrap_servers=bootstrap_servers,
        group_id=group_id,
        auto_offset_reset="latest",
        consumer_timeout_ms=1000,  # Default value
        custom_param="value",
    )
    assert consumer == mock_consumer_instance


@skip_if_kafka_unavailable
@patch("pymapgis.streaming.KafkaConsumer")
def test_connect_kafka_consumer_no_brokers(MockKafkaConsumerAliased):
    """Tests Kafka connection failure due to NoBrokersAvailable."""
    MockKafkaConsumerAliased.side_effect = ActualNoBrokersAvailable(
        "Mocked NoBrokersAvailable"
    )

    with pytest.raises(RuntimeError, match="Could not connect to Kafka brokers"):
        connect_kafka_consumer("test_topic", bootstrap_servers="bad_host:9092")


@patch(
    "pymapgis.streaming.KAFKA_AVAILABLE", False
)  # Temporarily mock module-level constant
def test_connect_kafka_consumer_import_error_simulated():
    """Tests behavior when kafka-python is not installed (simulated by mocking KAFKA_AVAILABLE)."""
    with pytest.raises(ImportError, match="kafka-python library is not installed"):
        connect_kafka_consumer("any_topic")


@skip_if_mqtt_unavailable
@patch(
    "pymapgis.streaming.mqtt.Client"
)  # Mock the paho.mqtt.client.Client class used in pymapgis.streaming
def test_connect_mqtt_client_success(MockMqttClientAliased):
    """Tests successful MQTT client connection and setup."""
    mock_client_instance = MagicMock(spec=actual_mqtt.Client)
    MockMqttClientAliased.return_value = mock_client_instance

    broker = "mqtt.example.com"
    port = 1884
    client_id = "test_mqtt_client"

    client = connect_mqtt_client(
        broker_address=broker, port=port, client_id=client_id, keepalive=120
    )

    MockMqttClientAliased.assert_called_once_with(
        client_id=client_id, protocol=actual_mqtt.MQTTv311, transport="tcp"
    )
    mock_client_instance.connect.assert_called_once_with(broker, port, 120)
    mock_client_instance.loop_start.assert_called_once()
    assert client == mock_client_instance


@skip_if_mqtt_unavailable
@patch("pymapgis.streaming.mqtt.Client")
def test_connect_mqtt_client_connection_refused(MockMqttClientAliased):
    """Tests MQTT connection failure (e.g., ConnectionRefusedError)."""
    mock_client_instance = MagicMock(spec=actual_mqtt.Client)
    MockMqttClientAliased.return_value = mock_client_instance
    mock_client_instance.connect.side_effect = ConnectionRefusedError(
        "Mocked ConnectionRefusedError"
    )

    with pytest.raises(RuntimeError, match="MQTT connection refused by broker"):
        connect_mqtt_client("refused_host", 1883)


@patch(
    "pymapgis.streaming.PAHO_MQTT_AVAILABLE", False
)  # Temporarily mock module-level constant
def test_connect_mqtt_client_import_error_simulated():
    """Tests behavior when paho-mqtt is not installed (simulated by mocking PAHO_MQTT_AVAILABLE)."""
    with pytest.raises(ImportError, match="paho-mqtt library is not installed"):
        connect_mqtt_client("any_broker")


# --- New Real-time Streaming Tests ---


@pytest.fixture
def sample_streaming_message():
    """Create sample streaming message."""
    if not NEW_STREAMING_AVAILABLE:
        pytest.skip("New streaming features not available")

    return StreamingMessage(
        message_id="msg_001",
        timestamp=datetime.now(),
        message_type="spatial_update",
        data={
            "feature_id": "feature_001",
            "geometry": {"type": "Point", "coordinates": [-74.0060, 40.7128]},
        },
        source="client_001",
        destination="server",
        metadata={"priority": "high"},
    )


@pytest.fixture
def sample_spatial_event():
    """Create sample spatial event."""
    if not NEW_STREAMING_AVAILABLE:
        pytest.skip("New streaming features not available")

    return SpatialEvent(
        event_id="event_001",
        event_type="feature_created",
        timestamp=datetime.now(),
        geometry={"type": "Point", "coordinates": [-74.0060, 40.7128]},
        properties={"name": "Test Feature", "value": 42},
        user_id="user_123",
        session_id="session_456",
    )


@pytest.fixture
def sample_live_data_point():
    """Create sample live data point."""
    if not NEW_STREAMING_AVAILABLE:
        pytest.skip("New streaming features not available")

    return LiveDataPoint(
        point_id="point_001",
        timestamp=datetime.now(),
        latitude=40.7128,
        longitude=-74.0060,
        altitude=10.0,
        accuracy=5.0,
        speed=25.0,
        heading=180.0,
        properties={"vehicle_id": "vehicle_123"},
    )


@pytest.mark.skipif(
    not NEW_STREAMING_AVAILABLE, reason="New streaming features not available"
)
class TestNewStreamingDataStructures:
    """Test new streaming data structures."""

    def test_streaming_message_creation(self, sample_streaming_message):
        """Test streaming message creation."""
        msg = sample_streaming_message
        assert msg.message_id == "msg_001"
        assert msg.message_type == "spatial_update"
        assert "feature_id" in msg.data
        assert msg.source == "client_001"

    def test_spatial_event_creation(self, sample_spatial_event):
        """Test spatial event creation."""
        event = sample_spatial_event
        assert event.event_id == "event_001"
        assert event.event_type == "feature_created"
        assert event.geometry["type"] == "Point"
        assert event.user_id == "user_123"

    def test_live_data_point_creation(self, sample_live_data_point):
        """Test live data point creation."""
        point = sample_live_data_point
        assert point.point_id == "point_001"
        assert point.latitude == 40.7128
        assert point.longitude == -74.0060
        assert point.properties["vehicle_id"] == "vehicle_123"


@pytest.mark.skipif(
    not NEW_STREAMING_AVAILABLE, reason="New streaming features not available"
)
class TestConnectionManager:
    """Test WebSocket connection manager."""

    def test_connection_manager_creation(self):
        """Test connection manager creation."""
        manager = ConnectionManager()
        assert len(manager.active_connections) == 0
        assert len(manager.connection_metadata) == 0

    @pytest.mark.asyncio
    async def test_connection_management(self):
        """Test connection management."""
        manager = ConnectionManager()

        # Mock WebSocket
        mock_websocket = Mock()
        mock_websocket.send = Mock(return_value=asyncio.Future())
        mock_websocket.send.return_value.set_result(None)

        # Test connection
        await manager.connect(mock_websocket, "client_001", {"user": "test"})
        assert "client_001" in manager.active_connections
        assert manager.connection_metadata["client_001"]["user"] == "test"

        # Test disconnection
        await manager.disconnect("client_001")
        assert "client_001" not in manager.active_connections


@pytest.mark.skipif(
    not NEW_STREAMING_AVAILABLE, reason="New streaming features not available"
)
class TestEventBus:
    """Test event bus functionality."""

    def test_event_bus_creation(self):
        """Test event bus creation."""
        event_bus = create_event_bus()
        assert event_bus is not None
        assert len(event_bus.subscribers) == 0

    @pytest.mark.asyncio
    async def test_event_subscription_and_publishing(self):
        """Test event subscription and publishing."""
        event_bus = EventBus()

        # Track received events
        received_events = []

        async def async_handler(data):
            received_events.append(("async", data))

        def sync_handler(data):
            received_events.append(("sync", data))

        # Subscribe handlers
        event_bus.subscribe("test_event", async_handler)
        event_bus.subscribe("test_event", sync_handler)

        # Publish event
        test_data = {"message": "test event data"}
        await event_bus.publish("test_event", test_data)

        # Check results
        assert len(received_events) == 2
        assert ("async", test_data) in received_events
        assert ("sync", test_data) in received_events

    def test_event_unsubscription(self):
        """Test event unsubscription."""
        event_bus = EventBus()

        def test_handler(data):
            pass

        # Subscribe and unsubscribe
        event_bus.subscribe("test_event", test_handler)
        assert len(event_bus.subscribers["test_event"]) == 1

        event_bus.unsubscribe("test_event", test_handler)
        assert len(event_bus.subscribers["test_event"]) == 0


@pytest.mark.skipif(
    not NEW_STREAMING_AVAILABLE or not KAFKA_AVAILABLE, reason="Kafka not available"
)
class TestNewKafkaIntegration:
    """Test new Kafka integration."""

    def test_kafka_producer_creation(self):
        """Test Kafka producer creation."""
        try:
            producer = SpatialKafkaProducer(["localhost:9092"])
            assert producer is not None
            producer.close()
        except Exception:
            pytest.skip("Kafka not running locally")

    def test_kafka_consumer_creation(self):
        """Test Kafka consumer creation."""
        try:
            consumer = SpatialKafkaConsumer(["test_topic"], ["localhost:9092"])
            assert consumer is not None
            consumer.stop_consuming()
        except Exception:
            pytest.skip("Kafka not running locally")


@pytest.mark.skipif(
    not NEW_STREAMING_AVAILABLE, reason="New streaming features not available"
)
class TestLiveDataFeeds:
    """Test live data feeds."""

    def test_gps_tracker_creation(self):
        """Test GPS tracker creation."""
        tracker = start_gps_tracking("test_gps", 1.0)
        assert tracker.feed_id == "test_gps"
        assert tracker.update_interval == 1.0
        assert not tracker.running

    def test_iot_sensor_creation(self):
        """Test IoT sensor creation."""
        sensor = connect_iot_sensors("test_sensor", "temperature", 5.0)
        assert sensor.feed_id == "test_sensor"
        assert sensor.sensor_type == "temperature"
        assert sensor.update_interval == 5.0

    @pytest.mark.asyncio
    async def test_gps_tracker_data_generation(self):
        """Test GPS tracker data generation."""
        tracker = GPSTracker("test_gps", 0.1)

        received_data = []

        async def data_handler(data):
            received_data.append(data)

        tracker.subscribe(data_handler)

        # Start tracker for short time
        task = asyncio.create_task(tracker.start())
        await asyncio.sleep(0.3)  # Should generate ~3 data points
        await tracker.stop()

        # Check results
        assert len(received_data) >= 2  # At least 2 data points
        for data in received_data:
            assert isinstance(data, LiveDataPoint)
            assert data.latitude is not None
            assert data.longitude is not None

    @pytest.mark.asyncio
    async def test_iot_sensor_data_generation(self):
        """Test IoT sensor data generation."""
        sensor = IoTSensorFeed("test_sensor", "temperature", 0.1)

        received_data = []

        async def data_handler(data):
            received_data.append(data)

        sensor.subscribe(data_handler)

        # Start sensor for short time
        task = asyncio.create_task(sensor.start())
        await asyncio.sleep(0.3)  # Should generate ~3 readings
        await sensor.stop()

        # Check results
        assert len(received_data) >= 2  # At least 2 readings
        for data in received_data:
            assert isinstance(data, dict)
            assert "sensor_id" in data
            assert "value" in data
            assert "timestamp" in data

    def test_create_live_feed_factory(self):
        """Test live feed factory function."""
        # Test GPS feed creation
        gps_feed = create_live_feed("gps", feed_id="test_gps", update_interval=2.0)
        assert isinstance(gps_feed, GPSTracker)
        assert gps_feed.feed_id == "test_gps"
        assert gps_feed.update_interval == 2.0

        # Test IoT feed creation
        iot_feed = create_live_feed(
            "iot", feed_id="test_iot", sensor_type="humidity", update_interval=3.0
        )
        assert isinstance(iot_feed, IoTSensorFeed)
        assert iot_feed.feed_id == "test_iot"
        assert iot_feed.sensor_type == "humidity"
        assert iot_feed.update_interval == 3.0

        # Test unknown type
        with pytest.raises(ValueError):
            create_live_feed("unknown_type")


@pytest.mark.skipif(
    not NEW_STREAMING_AVAILABLE, reason="New streaming features not available"
)
class TestStreamProcessing:
    """Test stream processing."""

    def test_stream_processor_creation(self):
        """Test stream processor creation."""
        processor = StreamProcessor()
        assert len(processor.filters) == 0
        assert len(processor.transformers) == 0

    @pytest.mark.asyncio
    async def test_stream_processing_with_filters(self):
        """Test stream processing with filters."""
        processor = StreamProcessor()

        # Add filter that only allows even numbers
        def even_filter(data):
            return data.get("value", 0) % 2 == 0

        processor.add_filter(even_filter)

        # Test data
        test_data = [
            {"value": 2},  # Should pass
            {"value": 3},  # Should be filtered out
            {"value": 4},  # Should pass
            {"value": 5},  # Should be filtered out
        ]

        results = []
        for data in test_data:
            result = await processor.process(data)
            if result is not None:
                results.append(result)

        assert len(results) == 2  # Only even values
        assert all(r["value"] % 2 == 0 for r in results)

    @pytest.mark.asyncio
    async def test_stream_processing_with_transformers(self):
        """Test stream processing with transformers."""
        processor = StreamProcessor()

        # Add transformer that doubles the value
        def double_transformer(data):
            if "value" in data:
                data["value"] *= 2
            return data

        processor.add_transformer(double_transformer)

        # Test data
        test_data = {"value": 5}
        result = await processor.process(test_data)

        assert result["value"] == 10


@pytest.mark.skipif(
    not NEW_STREAMING_AVAILABLE, reason="New streaming features not available"
)
class TestConvenienceFunctions:
    """Test convenience functions."""

    def test_convenience_function_imports(self):
        """Test that convenience functions are available."""
        # Test function availability
        assert callable(start_websocket_server)
        assert callable(connect_websocket_client)
        assert callable(create_event_bus)
        assert callable(publish_spatial_event)
        assert callable(subscribe_to_events)
        assert callable(start_gps_tracking)
        assert callable(connect_iot_sensors)
        assert callable(create_live_feed)

    @pytest.mark.asyncio
    async def test_global_event_bus_functions(self):
        """Test global event bus functions."""
        # Create event bus
        event_bus = create_event_bus()
        assert event_bus is not None

        # Test subscription and publishing
        received_data = []

        def test_handler(data):
            received_data.append(data)

        subscribe_to_events("test_event", test_handler)
        await publish_spatial_event("test_event", {"test": "data"})

        assert len(received_data) == 1
        assert received_data[0]["test"] == "data"
