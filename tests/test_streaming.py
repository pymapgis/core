import pytest
import numpy as np
import pandas as pd
import xarray as xr
from unittest.mock import patch, MagicMock

from pymapgis.streaming import create_spatiotemporal_cube, connect_kafka_consumer, connect_mqtt_client

# Attempt to import Kafka and MQTT related components for type hinting and mocking
try:
    from kafka import KafkaConsumer as ActualKafkaConsumer # Alias to avoid name clash with mock
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
    class actual_mqtt: # type: ignore
        class Client:
            pass

# Helper to conditionally skip tests
skip_if_kafka_unavailable = pytest.mark.skipif(not KAFKA_AVAILABLE, reason="kafka-python library not found.")
skip_if_mqtt_unavailable = pytest.mark.skipif(not PAHO_MQTT_AVAILABLE, reason="paho-mqtt library not found.")

# Sample data for testing
TIMESTAMPS = pd.to_datetime(['2023-01-01T00:00:00', '2023-01-01T01:00:00', '2023-01-01T02:00:00'])
X_COORDS = np.array([10.0, 10.1, 10.2, 10.3]) # Longitude or Easting
Y_COORDS = np.array([50.0, 50.1, 50.2])     # Latitude or Northing
Z_COORDS = np.array([0.0, 5.0])             # Depth or Height

DATA_3D_NP = np.random.rand(len(TIMESTAMPS), len(Y_COORDS), len(X_COORDS))
DATA_4D_NP = np.random.rand(len(TIMESTAMPS), len(Z_COORDS), len(Y_COORDS), len(X_COORDS))
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
        attrs=CUSTOM_ATTRS
    )

    # a. Assert that the returned object is an xr.DataArray
    assert isinstance(cube, xr.DataArray)

    # b. Assert that the dimensions of the DataArray are correct
    assert cube.dims == ('time', 'y', 'x')

    # c. Assert that the coordinates match the input sample data
    # Compare the values, not the index names (which may differ due to xarray coordinate naming)
    pd.testing.assert_index_equal(cube.coords['time'].to_index(), TIMESTAMPS, check_names=False)
    np.testing.assert_array_equal(cube.coords['x'].data, X_COORDS)
    np.testing.assert_array_equal(cube.coords['y'].data, Y_COORDS)

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
        attrs=CUSTOM_ATTRS
    )

    # a. Assert that the returned object is an xr.DataArray
    assert isinstance(cube, xr.DataArray)

    # b. Assert that the dimensions of the DataArray are correct
    assert cube.dims == ('time', 'z', 'y', 'x')

    # c. Assert that the coordinates match the input sample data
    # Compare the values, not the index names (which may differ due to xarray coordinate naming)
    pd.testing.assert_index_equal(cube.coords['time'].to_index(), TIMESTAMPS, check_names=False)
    np.testing.assert_array_equal(cube.coords['x'].data, X_COORDS)
    np.testing.assert_array_equal(cube.coords['y'].data, Y_COORDS)
    np.testing.assert_array_equal(cube.coords['z'].data, Z_COORDS)

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
        y_coords=Y_COORDS
        # No variable_name, no attrs
    )
    assert isinstance(cube, xr.DataArray)
    assert cube.name == 'sensor_value' # Default name
    assert cube.attrs == {} # Default empty attrs


def test_create_spatiotemporal_cube_shape_mismatch_error():
    """Tests that a ValueError is raised for mismatched data and coordinate shapes."""
    # Data shape (3, 3, 3) does not match X_COORDS length 4
    mismatched_data_3d = np.random.rand(len(TIMESTAMPS), len(Y_COORDS), len(Y_COORDS))

    with pytest.raises(ValueError) as excinfo:
        create_spatiotemporal_cube(
            data=mismatched_data_3d,
            timestamps=TIMESTAMPS,
            x_coords=X_COORDS, # X_COORDS has length 4
            y_coords=Y_COORDS
        )
    assert "Data shape" in str(excinfo.value)
    assert f"(time: {len(TIMESTAMPS)}," in str(excinfo.value)
    assert f"y: {len(Y_COORDS)}, x: {len(X_COORDS)})" in str(excinfo.value)
    assert f"does not match expected shape ({len(TIMESTAMPS)}, {len(Y_COORDS)}, {len(X_COORDS)})" # Corrected expected shape in assertion


    # Test 4D mismatch
    # Data shape (3, 2, 3, 3) does not match X_COORDS length 4
    mismatched_data_4d = np.random.rand(len(TIMESTAMPS), len(Z_COORDS), len(Y_COORDS), len(Y_COORDS))
    with pytest.raises(ValueError) as excinfo_4d:
        create_spatiotemporal_cube(
            data=mismatched_data_4d,
            timestamps=TIMESTAMPS,
            x_coords=X_COORDS, # X_COORDS has length 4
            y_coords=Y_COORDS,
            z_coords=Z_COORDS
        )
    assert "Data shape" in str(excinfo_4d.value)
    assert f"(time: {len(TIMESTAMPS)}, z: {len(Z_COORDS)}," in str(excinfo_4d.value)
    assert f"y: {len(Y_COORDS)}, x: {len(X_COORDS)})" in str(excinfo_4d.value)
    assert f"does not match expected shape ({len(TIMESTAMPS)}, {len(Z_COORDS)}, {len(Y_COORDS)}, {len(X_COORDS)})" # Corrected expected shape in assertion


def test_input_types_conversion():
    """Tests if list inputs for coordinates and timestamps are correctly converted."""
    list_timestamps = TIMESTAMPS.tolist() # Python list of Timestamps
    list_x_coords = X_COORDS.tolist()
    list_y_coords = Y_COORDS.tolist()
    list_z_coords = Z_COORDS.tolist()

    cube_3d_list_inputs = create_spatiotemporal_cube(
        data=DATA_3D_NP,
        timestamps=list_timestamps,
        x_coords=list_x_coords,
        y_coords=list_y_coords
    )
    assert isinstance(cube_3d_list_inputs.coords['time'].to_index(), pd.DatetimeIndex)
    assert isinstance(cube_3d_list_inputs.coords['x'].data, np.ndarray)
    assert isinstance(cube_3d_list_inputs.coords['y'].data, np.ndarray)

    cube_4d_list_inputs = create_spatiotemporal_cube(
        data=DATA_4D_NP,
        timestamps=list_timestamps,
        x_coords=list_x_coords,
        y_coords=list_y_coords,
        z_coords=list_z_coords
    )
    assert isinstance(cube_4d_list_inputs.coords['z'].data, np.ndarray)

# To run these tests:
# Ensure pymapgis is in PYTHONPATH
# pytest tests/test_streaming.py

# --- Tests for Kafka and MQTT Connectors ---


@skip_if_kafka_unavailable
@patch('pymapgis.streaming.KafkaConsumer') # Mock the KafkaConsumer class used in pymapgis.streaming
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
        auto_offset_reset='latest',
        custom_param='value'
    )

    MockKafkaConsumerAliased.assert_called_once_with(
        topic,
        bootstrap_servers=bootstrap_servers,
        group_id=group_id,
        auto_offset_reset='latest',
        consumer_timeout_ms=1000, # Default value
        custom_param='value'
    )
    assert consumer == mock_consumer_instance

@skip_if_kafka_unavailable
@patch('pymapgis.streaming.KafkaConsumer')
def test_connect_kafka_consumer_no_brokers(MockKafkaConsumerAliased):
    """Tests Kafka connection failure due to NoBrokersAvailable."""
    MockKafkaConsumerAliased.side_effect = ActualNoBrokersAvailable("Mocked NoBrokersAvailable")

    with pytest.raises(RuntimeError, match="Could not connect to Kafka brokers"):
        connect_kafka_consumer("test_topic", bootstrap_servers="bad_host:9092")

@patch('pymapgis.streaming.KAFKA_AVAILABLE', False) # Temporarily mock module-level constant
def test_connect_kafka_consumer_import_error_simulated():
    """Tests behavior when kafka-python is not installed (simulated by mocking KAFKA_AVAILABLE)."""
    with pytest.raises(ImportError, match="kafka-python library is not installed"):
         connect_kafka_consumer("any_topic")


@skip_if_mqtt_unavailable
@patch('pymapgis.streaming.mqtt.Client') # Mock the paho.mqtt.client.Client class used in pymapgis.streaming
def test_connect_mqtt_client_success(MockMqttClientAliased):
    """Tests successful MQTT client connection and setup."""
    mock_client_instance = MagicMock(spec=actual_mqtt.Client)
    MockMqttClientAliased.return_value = mock_client_instance

    broker = "mqtt.example.com"
    port = 1884
    client_id = "test_mqtt_client"

    client = connect_mqtt_client(
        broker_address=broker,
        port=port,
        client_id=client_id,
        keepalive=120
    )

    MockMqttClientAliased.assert_called_once_with(client_id=client_id, protocol=actual_mqtt.MQTTv311, transport="tcp")
    mock_client_instance.connect.assert_called_once_with(broker, port, 120)
    mock_client_instance.loop_start.assert_called_once()
    assert client == mock_client_instance

@skip_if_mqtt_unavailable
@patch('pymapgis.streaming.mqtt.Client')
def test_connect_mqtt_client_connection_refused(MockMqttClientAliased):
    """Tests MQTT connection failure (e.g., ConnectionRefusedError)."""
    mock_client_instance = MagicMock(spec=actual_mqtt.Client)
    MockMqttClientAliased.return_value = mock_client_instance
    mock_client_instance.connect.side_effect = ConnectionRefusedError("Mocked ConnectionRefusedError")

    with pytest.raises(RuntimeError, match="MQTT connection refused by broker"):
        connect_mqtt_client("refused_host", 1883)

@patch('pymapgis.streaming.PAHO_MQTT_AVAILABLE', False) # Temporarily mock module-level constant
def test_connect_mqtt_client_import_error_simulated():
    """Tests behavior when paho-mqtt is not installed (simulated by mocking PAHO_MQTT_AVAILABLE)."""
    with pytest.raises(ImportError, match="paho-mqtt library is not installed"):
        connect_mqtt_client("any_broker")
