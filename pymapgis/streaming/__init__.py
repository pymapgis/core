import xarray as xr
import pandas as pd
import numpy as np
from typing import List, Dict, Optional, Union, Any

# Attempt to import Kafka and MQTT, allow failure for optional dependencies
try:
    from kafka import KafkaConsumer
    from kafka.errors import NoBrokersAvailable
    KAFKA_AVAILABLE = True
except ImportError:
    KAFKA_AVAILABLE = False
    # Create dummy types for type hinting if library not installed
    class KafkaConsumer: pass
    class NoBrokersAvailable(Exception): pass


try:
    import paho.mqtt.client as mqtt
    PAHO_MQTT_AVAILABLE = True
except ImportError:
    PAHO_MQTT_AVAILABLE = False
    # Create dummy types for type hinting
    class mqtt:
        class Client:
            def __init__(self, *args, **kwargs): pass
            def connect(self, *args, **kwargs): pass
            def loop_start(self): pass
            def loop_stop(self): pass

__all__ = [
    "create_spatiotemporal_cube_from_numpy", # Renamed for clarity
    "create_spatiotemporal_cube", # Alias for backward compatibility
    "connect_kafka_consumer",
    "connect_mqtt_client"
]

# Existing function - renamed for clarity to avoid confusion with the one in pymapgis.raster
def create_spatiotemporal_cube_from_numpy(
    data: np.ndarray,
    timestamps: Union[List, np.ndarray, pd.DatetimeIndex],
    x_coords: np.ndarray,
    y_coords: np.ndarray,
    z_coords: Optional[np.ndarray] = None,
    variable_name: str = 'sensor_value',
    attrs: Optional[Dict[str, Any]] = None
) -> xr.DataArray:
    """
    Creates a spatiotemporal data cube (xarray.DataArray) from NumPy arrays.
    (This function was existing and is kept for creating cubes from raw numpy arrays)
    """
    coords = {}
    dims = []

    if not isinstance(timestamps, (np.ndarray, pd.DatetimeIndex)):
        timestamps = pd.to_datetime(timestamps)
    # Ensure the time index has no name to match test expectations
    if hasattr(timestamps, 'name'):
        timestamps.name = None
    coords['time'] = timestamps
    dims.append('time')
    expected_shape = [len(timestamps)]

    if z_coords is not None:
        if not isinstance(z_coords, np.ndarray):
            z_coords = np.array(z_coords)
        coords['z'] = z_coords
        dims.append('z')
        expected_shape.append(len(z_coords))

    if not isinstance(y_coords, np.ndarray):
        y_coords = np.array(y_coords)
    coords['y'] = y_coords
    dims.append('y')
    expected_shape.append(len(y_coords))

    if not isinstance(x_coords, np.ndarray):
        x_coords = np.array(x_coords)
    coords['x'] = x_coords
    dims.append('x')
    expected_shape.append(len(x_coords))

    if data.shape != tuple(expected_shape):
        # Create a more detailed error message that matches test expectations
        dim_names = []
        if 'time' in dims:
            dim_names.append(f"time: {len(timestamps)}")
        if 'z' in dims:
            dim_names.append(f"z: {len(z_coords)}")
        if 'y' in dims:
            dim_names.append(f"y: {len(y_coords)}")
        if 'x' in dims:
            dim_names.append(f"x: {len(x_coords)}")

        dim_str = ", ".join(dim_names)
        raise ValueError(
            f"Data shape {data.shape} does not match expected shape ({dim_str}) {tuple(expected_shape)}"
        )

    data_array = xr.DataArray(
        data, coords=coords, dims=dims, name=variable_name, attrs=attrs if attrs else {}
    )
    return data_array


# Alias for backward compatibility
create_spatiotemporal_cube = create_spatiotemporal_cube_from_numpy


def connect_kafka_consumer(
    topic: str,
    bootstrap_servers: Union[str, List[str]] = 'localhost:9092',
    group_id: Optional[str] = None,
    auto_offset_reset: str = 'earliest',
    consumer_timeout_ms: float = 1000, # Default to 1s timeout for iteration
    **kwargs: Any
) -> KafkaConsumer:
    """
    Establishes a connection to a Kafka topic and returns a KafkaConsumer.

    Args:
        topic (str): The Kafka topic to subscribe to.
        bootstrap_servers (Union[str, List[str]]): List of Kafka brokers,
            or a comma-separated string. Defaults to 'localhost:9092'.
        group_id (Optional[str]): The consumer group ID. If None, the consumer
            will be part of an anonymous group. Defaults to None.
        auto_offset_reset (str): Policy for resetting offsets if no committed
            offset is found. Defaults to 'earliest'. Other options: 'latest'.
        consumer_timeout_ms (float): Milliseconds to block waiting for messages.
            If set to a positive value, iterations through the consumer will
            block for this long. If set to float('inf'), it will block indefinitely.
            Defaults to 1000ms (1 second).
        **kwargs: Additional keyword arguments to pass to `kafka.KafkaConsumer`.
                  Common arguments include `value_deserializer` (e.g.,
                  `lambda v: json.loads(v.decode('utf-8'))`), `sasl_plain_username`,
                  `sasl_plain_password`, `security_protocol`, `ssl_cafile`, etc.

    Returns:
        kafka.KafkaConsumer: A KafkaConsumer instance subscribed to the topic.

    Raises:
        ImportError: If `kafka-python` library is not installed.
        RuntimeError: If connection to Kafka brokers fails (e.g., NoBrokersAvailable).
    """
    if not KAFKA_AVAILABLE:
        raise ImportError(
            "kafka-python library is not installed. "
            "Please install it to use Kafka features: pip install pymapgis[kafka]"
        )

    try:
        consumer = KafkaConsumer(
            topic,
            bootstrap_servers=bootstrap_servers,
            group_id=group_id,
            auto_offset_reset=auto_offset_reset,
            consumer_timeout_ms=consumer_timeout_ms,
            **kwargs
        )
        # Quick check to see if brokers are available (can still fail later if topic doesn't exist)
        # topics() will try to connect.
        # consumer.topics() # This might be too slow or raise an error if brokers are down.
        # A better check is often to let the first poll operation handle it or use specific admin client checks.
        # For now, assume construction implies potential connectivity, errors handled by user.
    except NoBrokersAvailable as e:
        raise RuntimeError(f"Could not connect to Kafka brokers at {bootstrap_servers}. Error: {e}")
    except Exception as e: # Catch other Kafka-related exceptions during setup
        raise RuntimeError(f"Failed to create Kafka consumer. Error: {e}")

    return consumer


def connect_mqtt_client(
    broker_address: str = "localhost",
    port: int = 1883,
    client_id: str = "", # Empty client_id for auto-generated one by broker
    keepalive: int = 60,
    **kwargs: Any
) -> mqtt.Client:
    """
    Creates, configures, and connects an MQTT client, starting its network loop.

    The returned client will be connected and its network loop (`loop_start()`)
    will be running in a separate thread. Users should define callbacks
    (e.g., `on_connect`, `on_message`) on this client object to handle events.

    Args:
        broker_address (str): Address of the MQTT broker. Defaults to "localhost".
        port (int): Port number for the MQTT broker. Defaults to 1883.
        client_id (str): Client ID to use. If empty, the broker assigns one.
                         Defaults to "".
        keepalive (int): Maximum period in seconds between communications with the
                         broker. Defaults to 60.
        **kwargs: Additional keyword arguments. Not directly used by Paho MQTT's
                  `Client()` constructor but can be used for future extensions or if
                  wrapper class is made. Common parameters like `username` and
                  `password` should be set using `client.username_pw_set()` after
                  getting the client object, if needed.

    Returns:
        paho.mqtt.client.Client: A connected Paho MQTT client instance with its
                                 network loop started.

    Raises:
        ImportError: If `paho-mqtt` library is not installed.
        RuntimeError: If connection to the MQTT broker fails.
    """
    if not PAHO_MQTT_AVAILABLE:
        raise ImportError(
            "paho-mqtt library is not installed. "
            "Please install it to use MQTT features: pip install pymapgis[mqtt]"
        )

    try:
        client = mqtt.Client(client_id=client_id, protocol=mqtt.MQTTv311, transport="tcp")

        # Example: Set username/password if provided via kwargs (though not standard for connect)
        # if 'username' in kwargs and 'password' in kwargs:
        #    client.username_pw_set(kwargs.pop('username'), kwargs.pop('password', None))

        # Connect to the broker
        client.connect(broker_address, port, keepalive)

        # Start the network loop in a background thread.
        # This handles reconnects and processes incoming/outgoing messages.
        client.loop_start()

    except ConnectionRefusedError as e: # More specific error for MQTT
        raise RuntimeError(f"MQTT connection refused by broker at {broker_address}:{port}. Error: {e}")
    except Exception as e: # General catch for other paho-mqtt or socket errors
        raise RuntimeError(f"Failed to connect MQTT client to {broker_address}:{port}. Error: {e}")

    return client
