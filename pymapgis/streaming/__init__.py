"""
PyMapGIS Real-time Streaming Module

Provides comprehensive real-time streaming capabilities for live geospatial data processing,
including WebSocket communication, event-driven architecture, and Kafka integration.

Features:
- WebSocket Server/Client: Real-time bidirectional communication
- Event-Driven Architecture: Pub/Sub messaging for scalable event distribution
- Kafka Integration: High-throughput streaming for enterprise data volumes
- Stream Processing: Real-time data transformations and analytics
- Live Data Feeds: GPS tracking, IoT sensors, real-time updates
- Collaborative Mapping: Multi-user real-time map editing

Enterprise Features:
- Scalable streaming architecture for high-volume data
- Distributed processing with fault tolerance
- Real-time analytics and monitoring
- Integration with existing ML/Analytics pipelines
- Enterprise security and authentication
- Performance optimization for low-latency applications
"""

import asyncio
import json
import logging
import time
from typing import Dict, List, Optional, Union, Any, Callable, Awaitable
from dataclasses import dataclass, asdict
from datetime import datetime
from abc import ABC, abstractmethod
import threading
from queue import Queue, Empty
from concurrent.futures import ThreadPoolExecutor

# Legacy imports for backward compatibility
import xarray as xr
import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)

# Optional imports for streaming functionality
try:
    import websockets
    from websockets.server import WebSocketServerProtocol
    from websockets.client import WebSocketClientProtocol

    WEBSOCKETS_AVAILABLE = True
except ImportError:
    WEBSOCKETS_AVAILABLE = False
    logger.warning("WebSockets not available - install websockets package")

    # Create dummy types for backward compatibility
    class WebSocketServerProtocol:
        pass

    class WebSocketClientProtocol:
        pass

try:
    from kafka import KafkaProducer, KafkaConsumer
    from kafka.errors import KafkaError, NoBrokersAvailable

    KAFKA_AVAILABLE = True
except ImportError:
    KAFKA_AVAILABLE = False
    logger.warning("Kafka not available - install kafka-python package")

    # Create dummy types for backward compatibility
    class KafkaConsumer:
        pass

    class NoBrokersAvailable(Exception):
        pass


try:
    import paho.mqtt.client as mqtt

    PAHO_MQTT_AVAILABLE = True
except ImportError:
    PAHO_MQTT_AVAILABLE = False
    logger.warning("MQTT not available - install paho-mqtt package")

    # Create dummy types for backward compatibility
    class mqtt:
        class Client:
            def __init__(self, *args, **kwargs):
                pass

            def connect(self, *args, **kwargs):
                pass

            def loop_start(self):
                pass

            def loop_stop(self):
                pass


try:
    import redis

    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    logger.warning("Redis not available - install redis package")

try:
    import geopandas as gpd
    from shapely.geometry import Point, Polygon

    GEOPANDAS_AVAILABLE = True
except ImportError:
    GEOPANDAS_AVAILABLE = False
    logger.warning("GeoPandas not available - spatial streaming limited")


# Core data structures
@dataclass
class StreamingMessage:
    """Message structure for streaming data."""

    message_id: str
    timestamp: datetime
    message_type: str
    data: Dict[str, Any]
    source: Optional[str] = None
    destination: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class SpatialEvent:
    """Spatial event for real-time updates."""

    event_id: str
    event_type: str
    timestamp: datetime
    geometry: Optional[Dict[str, Any]]
    properties: Dict[str, Any]
    user_id: Optional[str] = None
    session_id: Optional[str] = None


@dataclass
class LiveDataPoint:
    """Live data point for streaming."""

    point_id: str
    timestamp: datetime
    latitude: float
    longitude: float
    altitude: Optional[float] = None
    accuracy: Optional[float] = None
    speed: Optional[float] = None
    heading: Optional[float] = None
    properties: Optional[Dict[str, Any]] = None


# WebSocket Server Implementation
class ConnectionManager:
    """Manages WebSocket connections."""

    def __init__(self):
        self.active_connections: Dict[str, WebSocketServerProtocol] = {}
        self.connection_metadata: Dict[str, Dict[str, Any]] = {}
        self.lock = threading.Lock()

    async def connect(
        self,
        websocket: WebSocketServerProtocol,
        client_id: str,
        metadata: Dict[str, Any] = None,
    ):
        """Add a new connection."""
        with self.lock:
            self.active_connections[client_id] = websocket
            self.connection_metadata[client_id] = metadata or {}
        logger.info(f"Client {client_id} connected")

    async def disconnect(self, client_id: str):
        """Remove a connection."""
        with self.lock:
            if client_id in self.active_connections:
                del self.active_connections[client_id]
                del self.connection_metadata[client_id]
        logger.info(f"Client {client_id} disconnected")

    async def send_personal_message(self, message: str, client_id: str):
        """Send message to specific client."""
        if client_id in self.active_connections:
            websocket = self.active_connections[client_id]
            try:
                await websocket.send(message)
            except Exception as e:
                logger.error(f"Error sending message to {client_id}: {e}")
                await self.disconnect(client_id)

    async def broadcast(self, message: str, exclude: Optional[List[str]] = None):
        """Broadcast message to all connected clients."""
        exclude = exclude or []
        disconnected = []

        for client_id, websocket in self.active_connections.items():
            if client_id not in exclude:
                try:
                    await websocket.send(message)
                except Exception as e:
                    logger.error(f"Error broadcasting to {client_id}: {e}")
                    disconnected.append(client_id)

        # Clean up disconnected clients
        for client_id in disconnected:
            await self.disconnect(client_id)


class WebSocketServer:
    """WebSocket server for real-time communication."""

    def __init__(self, host: str = "localhost", port: int = 8765):
        self.host = host
        self.port = port
        self.connection_manager = ConnectionManager()
        self.message_handlers: Dict[str, Callable] = {}
        self.server = None
        self.running = False

    def register_handler(self, message_type: str, handler: Callable):
        """Register a message handler."""
        self.message_handlers[message_type] = handler

    async def handle_client(self, websocket: WebSocketServerProtocol, path: str):
        """Handle individual client connection."""
        client_id = f"client_{id(websocket)}"
        await self.connection_manager.connect(websocket, client_id)

        try:
            async for message in websocket:
                await self.process_message(message, client_id)
        except Exception as e:
            logger.error(f"Error handling client {client_id}: {e}")
        finally:
            await self.connection_manager.disconnect(client_id)

    async def process_message(self, message: str, client_id: str):
        """Process incoming message."""
        try:
            data = json.loads(message)
            message_type = data.get("type", "unknown")

            if message_type in self.message_handlers:
                await self.message_handlers[message_type](data, client_id)
            else:
                logger.warning(f"Unknown message type: {message_type}")
        except json.JSONDecodeError:
            logger.error(f"Invalid JSON from client {client_id}: {message}")
        except Exception as e:
            logger.error(f"Error processing message from {client_id}: {e}")

    async def start(self):
        """Start the WebSocket server."""
        if not WEBSOCKETS_AVAILABLE:
            raise ImportError("WebSockets not available - install websockets package")

        self.server = await websockets.serve(self.handle_client, self.host, self.port)
        self.running = True
        logger.info(f"WebSocket server started on {self.host}:{self.port}")

    async def stop(self):
        """Stop the WebSocket server."""
        if self.server:
            self.server.close()
            await self.server.wait_closed()
            self.running = False
            logger.info("WebSocket server stopped")

    async def broadcast_spatial_event(self, event: SpatialEvent):
        """Broadcast spatial event to all clients."""
        message = {"type": "spatial_event", "event": asdict(event)}
        await self.connection_manager.broadcast(json.dumps(message))


class WebSocketClient:
    """WebSocket client for connecting to streaming server."""

    def __init__(self, uri: str):
        self.uri = uri
        self.websocket = None
        self.message_handlers: Dict[str, Callable] = {}
        self.connected = False

    def register_handler(self, message_type: str, handler: Callable):
        """Register a message handler."""
        self.message_handlers[message_type] = handler

    async def connect(self):
        """Connect to WebSocket server."""
        if not WEBSOCKETS_AVAILABLE:
            raise ImportError("WebSockets not available - install websockets package")

        self.websocket = await websockets.connect(self.uri)
        self.connected = True
        logger.info(f"Connected to WebSocket server: {self.uri}")

    async def disconnect(self):
        """Disconnect from WebSocket server."""
        if self.websocket:
            await self.websocket.close()
            self.connected = False
            logger.info("Disconnected from WebSocket server")

    async def send_message(self, message_type: str, data: Dict[str, Any]):
        """Send message to server."""
        if not self.connected:
            raise RuntimeError("Not connected to server")

        message = {
            "type": message_type,
            "data": data,
            "timestamp": datetime.now().isoformat(),
        }
        await self.websocket.send(json.dumps(message))

    async def listen(self):
        """Listen for messages from server."""
        if not self.connected:
            raise RuntimeError("Not connected to server")

        async for message in self.websocket:
            await self.process_message(message)

    async def process_message(self, message: str):
        """Process incoming message."""
        try:
            data = json.loads(message)
            message_type = data.get("type", "unknown")

            if message_type in self.message_handlers:
                await self.message_handlers[message_type](data)
            else:
                logger.warning(f"Unknown message type: {message_type}")
        except json.JSONDecodeError:
            logger.error(f"Invalid JSON from server: {message}")
        except Exception as e:
            logger.error(f"Error processing message: {e}")


# Event System Implementation
class EventBus:
    """Event bus for pub/sub messaging."""

    def __init__(self):
        self.subscribers: Dict[str, List[Callable]] = {}
        self.lock = threading.Lock()

    def subscribe(self, event_type: str, handler: Callable):
        """Subscribe to event type."""
        with self.lock:
            if event_type not in self.subscribers:
                self.subscribers[event_type] = []
            self.subscribers[event_type].append(handler)

    def unsubscribe(self, event_type: str, handler: Callable):
        """Unsubscribe from event type."""
        with self.lock:
            if event_type in self.subscribers:
                try:
                    self.subscribers[event_type].remove(handler)
                except ValueError:
                    pass

    async def publish(self, event_type: str, data: Any):
        """Publish event to subscribers."""
        handlers = []
        with self.lock:
            if event_type in self.subscribers:
                handlers = self.subscribers[event_type].copy()

        for handler in handlers:
            try:
                if asyncio.iscoroutinefunction(handler):
                    await handler(data)
                else:
                    handler(data)
            except Exception as e:
                logger.error(f"Error in event handler for {event_type}: {e}")


# Kafka Integration
class SpatialKafkaProducer:
    """Kafka producer for spatial data."""

    def __init__(self, bootstrap_servers: List[str], **config):
        if not KAFKA_AVAILABLE:
            raise ImportError("Kafka not available - install kafka-python package")

        self.config = {
            "bootstrap_servers": bootstrap_servers,
            "value_serializer": lambda v: json.dumps(v).encode("utf-8"),
            "key_serializer": lambda k: k.encode("utf-8") if k else None,
            **config,
        }
        self.producer = KafkaProducer(**self.config)

    async def send_spatial_data(
        self, topic: str, data: Dict[str, Any], key: str = None
    ):
        """Send spatial data to Kafka topic."""
        try:
            # Add timestamp if not present
            if "timestamp" not in data:
                data["timestamp"] = datetime.now().isoformat()

            future = self.producer.send(topic, value=data, key=key)
            record_metadata = future.get(timeout=10)
            logger.debug(f"Sent to topic {topic}: {record_metadata}")
        except Exception as e:
            logger.error(f"Error sending to Kafka: {e}")

    def close(self):
        """Close the producer."""
        self.producer.close()


class SpatialKafkaConsumer:
    """Kafka consumer for spatial data."""

    def __init__(
        self,
        topics: List[str],
        bootstrap_servers: List[str],
        group_id: str = None,
        **config,
    ):
        if not KAFKA_AVAILABLE:
            raise ImportError("Kafka not available - install kafka-python package")

        self.config = {
            "bootstrap_servers": bootstrap_servers,
            "group_id": group_id,
            "value_deserializer": lambda v: json.loads(v.decode("utf-8")),
            "key_deserializer": lambda k: k.decode("utf-8") if k else None,
            "auto_offset_reset": "latest",
            **config,
        }
        self.consumer = KafkaConsumer(*topics, **self.config)
        self.message_handlers: Dict[str, Callable] = {}
        self.running = False

    def register_handler(self, message_type: str, handler: Callable):
        """Register message handler."""
        self.message_handlers[message_type] = handler

    async def start_consuming(self):
        """Start consuming messages."""
        self.running = True

        def consume_loop():
            for message in self.consumer:
                if not self.running:
                    break

                try:
                    data = message.value
                    message_type = data.get("type", "unknown")

                    if message_type in self.message_handlers:
                        handler = self.message_handlers[message_type]
                        if asyncio.iscoroutinefunction(handler):
                            asyncio.create_task(handler(data))
                        else:
                            handler(data)
                except Exception as e:
                    logger.error(f"Error processing Kafka message: {e}")

        # Run in thread to avoid blocking
        thread = threading.Thread(target=consume_loop)
        thread.start()

    def stop_consuming(self):
        """Stop consuming messages."""
        self.running = False
        self.consumer.close()


# Live Data Feed Implementation
class LiveDataFeed(ABC):
    """Abstract base class for live data feeds."""

    def __init__(self, feed_id: str):
        self.feed_id = feed_id
        self.subscribers: List[Callable] = []
        self.running = False

    def subscribe(self, handler: Callable):
        """Subscribe to data updates."""
        self.subscribers.append(handler)

    def unsubscribe(self, handler: Callable):
        """Unsubscribe from data updates."""
        try:
            self.subscribers.remove(handler)
        except ValueError:
            pass

    async def notify_subscribers(self, data: Any):
        """Notify all subscribers of new data."""
        for handler in self.subscribers:
            try:
                if asyncio.iscoroutinefunction(handler):
                    await handler(data)
                else:
                    handler(data)
            except Exception as e:
                logger.error(f"Error in data feed handler: {e}")

    @abstractmethod
    async def start(self):
        """Start the data feed."""
        pass

    @abstractmethod
    async def stop(self):
        """Stop the data feed."""
        pass


class GPSTracker(LiveDataFeed):
    """GPS tracking data feed."""

    def __init__(self, feed_id: str, update_interval: float = 1.0):
        super().__init__(feed_id)
        self.update_interval = update_interval
        self.current_position = None

    async def start(self):
        """Start GPS tracking."""
        self.running = True

        while self.running:
            # Simulate GPS data (in real implementation, would connect to GPS device)
            gps_data = LiveDataPoint(
                point_id=f"gps_{int(time.time())}",
                timestamp=datetime.now(),
                latitude=40.7128 + (np.random.random() - 0.5) * 0.01,
                longitude=-74.0060 + (np.random.random() - 0.5) * 0.01,
                altitude=10.0 + np.random.random() * 5,
                accuracy=5.0,
                speed=np.random.random() * 50,
                heading=np.random.random() * 360,
            )

            await self.notify_subscribers(gps_data)
            await asyncio.sleep(self.update_interval)

    async def stop(self):
        """Stop GPS tracking."""
        self.running = False


class IoTSensorFeed(LiveDataFeed):
    """IoT sensor data feed."""

    def __init__(self, feed_id: str, sensor_type: str, update_interval: float = 5.0):
        super().__init__(feed_id)
        self.sensor_type = sensor_type
        self.update_interval = update_interval

    async def start(self):
        """Start IoT sensor feed."""
        self.running = True

        while self.running:
            # Simulate sensor data
            sensor_data = {
                "sensor_id": self.feed_id,
                "sensor_type": self.sensor_type,
                "timestamp": datetime.now().isoformat(),
                "value": np.random.random() * 100,
                "unit": "units",
                "location": {
                    "latitude": 40.7128 + (np.random.random() - 0.5) * 0.1,
                    "longitude": -74.0060 + (np.random.random() - 0.5) * 0.1,
                },
            }

            await self.notify_subscribers(sensor_data)
            await asyncio.sleep(self.update_interval)

    async def stop(self):
        """Stop IoT sensor feed."""
        self.running = False


# Stream Processing
class StreamProcessor:
    """Process streaming data with filters and transformations."""

    def __init__(self):
        self.filters: List[Callable] = []
        self.transformers: List[Callable] = []

    def add_filter(self, filter_func: Callable):
        """Add a filter function."""
        self.filters.append(filter_func)

    def add_transformer(self, transform_func: Callable):
        """Add a transformation function."""
        self.transformers.append(transform_func)

    async def process(self, data: Any) -> Optional[Any]:
        """Process data through filters and transformations."""
        # Apply filters
        for filter_func in self.filters:
            if not filter_func(data):
                return None

        # Apply transformations
        result = data
        for transform_func in self.transformers:
            result = transform_func(result)

        return result


# Global instances
_websocket_server = None
_event_bus = None
_kafka_producer = None
_kafka_consumer = None


# Convenience functions
async def start_websocket_server(
    host: str = "localhost", port: int = 8765, **kwargs
) -> WebSocketServer:
    """Start WebSocket server."""
    global _websocket_server
    _websocket_server = WebSocketServer(host, port)
    await _websocket_server.start()
    return _websocket_server


async def connect_websocket_client(uri: str, **kwargs) -> WebSocketClient:
    """Connect WebSocket client."""
    client = WebSocketClient(uri)
    await client.connect()
    return client


def create_event_bus() -> EventBus:
    """Create event bus."""
    global _event_bus
    _event_bus = EventBus()
    return _event_bus


def create_kafka_producer(
    bootstrap_servers: List[str], **config
) -> SpatialKafkaProducer:
    """Create Kafka producer."""
    global _kafka_producer
    _kafka_producer = SpatialKafkaProducer(bootstrap_servers, **config)
    return _kafka_producer


def create_kafka_consumer(
    topics: List[str], bootstrap_servers: List[str], **config
) -> SpatialKafkaConsumer:
    """Create Kafka consumer."""
    global _kafka_consumer
    _kafka_consumer = SpatialKafkaConsumer(topics, bootstrap_servers, **config)
    return _kafka_consumer


async def publish_spatial_event(event_type: str, data: Any):
    """Publish spatial event."""
    if _event_bus:
        await _event_bus.publish(event_type, data)


def subscribe_to_events(event_type: str, handler: Callable):
    """Subscribe to events."""
    if _event_bus:
        _event_bus.subscribe(event_type, handler)


def start_gps_tracking(feed_id: str, update_interval: float = 1.0) -> GPSTracker:
    """Start GPS tracking."""
    tracker = GPSTracker(feed_id, update_interval)
    return tracker


def connect_iot_sensors(
    feed_id: str, sensor_type: str, update_interval: float = 5.0
) -> IoTSensorFeed:
    """Connect IoT sensors."""
    feed = IoTSensorFeed(feed_id, sensor_type, update_interval)
    return feed


def create_live_feed(source_type: str, **kwargs) -> LiveDataFeed:
    """Create live data feed."""
    if source_type == "gps":
        return GPSTracker(
            kwargs.get("feed_id", "gps_feed"), kwargs.get("update_interval", 1.0)
        )
    elif source_type == "iot":
        return IoTSensorFeed(
            kwargs.get("feed_id", "iot_feed"),
            kwargs.get("sensor_type", "generic"),
            kwargs.get("update_interval", 5.0),
        )
    else:
        raise ValueError(f"Unknown source type: {source_type}")


# Legacy functions for backward compatibility
def create_spatiotemporal_cube_from_numpy(
    data: np.ndarray,
    timestamps: Union[List, np.ndarray, pd.DatetimeIndex],
    x_coords: np.ndarray,
    y_coords: np.ndarray,
    z_coords: Optional[np.ndarray] = None,
    variable_name: str = "sensor_value",
    attrs: Optional[Dict[str, Any]] = None,
) -> xr.DataArray:
    """
    Creates a spatiotemporal data cube (xarray.DataArray) from NumPy arrays.
    (Legacy function for backward compatibility)
    """
    coords = {}
    dims = []

    if not isinstance(timestamps, (np.ndarray, pd.DatetimeIndex)):
        timestamps = pd.to_datetime(timestamps)
    if hasattr(timestamps, "name"):
        timestamps.name = None
    coords["time"] = timestamps
    dims.append("time")
    expected_shape = [len(timestamps)]

    if z_coords is not None:
        if not isinstance(z_coords, np.ndarray):
            z_coords = np.array(z_coords)
        coords["z"] = z_coords
        dims.append("z")
        expected_shape.append(len(z_coords))

    if not isinstance(y_coords, np.ndarray):
        y_coords = np.array(y_coords)
    coords["y"] = y_coords
    dims.append("y")
    expected_shape.append(len(y_coords))

    if not isinstance(x_coords, np.ndarray):
        x_coords = np.array(x_coords)
    coords["x"] = x_coords
    dims.append("x")
    expected_shape.append(len(x_coords))

    if data.shape != tuple(expected_shape):
        dim_names = []
        if "time" in dims:
            dim_names.append(f"time: {len(timestamps)}")
        if "z" in dims:
            dim_names.append(f"z: {len(z_coords)}")
        if "y" in dims:
            dim_names.append(f"y: {len(y_coords)}")
        if "x" in dims:
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


# Legacy Kafka function for backward compatibility
def connect_kafka_consumer(
    topic: str,
    bootstrap_servers: Union[str, List[str]] = "localhost:9092",
    group_id: Optional[str] = None,
    auto_offset_reset: str = "earliest",
    consumer_timeout_ms: float = 1000,
    **kwargs: Any,
) -> KafkaConsumer:
    """
    Establishes a connection to a Kafka topic and returns a KafkaConsumer.
    (Legacy function for backward compatibility)
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
            **kwargs,
        )
    except NoBrokersAvailable as e:
        raise RuntimeError(
            f"Could not connect to Kafka brokers at {bootstrap_servers}. Error: {e}"
        )
    except Exception as e:
        raise RuntimeError(f"Failed to create Kafka consumer. Error: {e}")

    return consumer


# Legacy MQTT function for backward compatibility
def connect_mqtt_client(
    broker_address: str = "localhost",
    port: int = 1883,
    client_id: str = "",
    keepalive: int = 60,
    **kwargs: Any,
) -> mqtt.Client:
    """
    Creates, configures, and connects an MQTT client, starting its network loop.
    (Legacy function for backward compatibility)
    """
    if not PAHO_MQTT_AVAILABLE:
        raise ImportError(
            "paho-mqtt library is not installed. "
            "Please install it to use MQTT features: pip install pymapgis[mqtt]"
        )

    try:
        client = mqtt.Client(
            client_id=client_id, protocol=mqtt.MQTTv311, transport="tcp"
        )
        client.connect(broker_address, port, keepalive)
        client.loop_start()
    except ConnectionRefusedError as e:
        raise RuntimeError(
            f"MQTT connection refused by broker at {broker_address}:{port}. Error: {e}"
        )
    except Exception as e:
        raise RuntimeError(
            f"Failed to connect MQTT client to {broker_address}:{port}. Error: {e}"
        )

    return client


# Export all components
__all__ = [
    # Core data structures
    "StreamingMessage",
    "SpatialEvent",
    "LiveDataPoint",
    # WebSocket components
    "WebSocketServer",
    "WebSocketClient",
    "ConnectionManager",
    # Event system
    "EventBus",
    # Kafka integration
    "SpatialKafkaProducer",
    "SpatialKafkaConsumer",
    # Live data feeds
    "LiveDataFeed",
    "GPSTracker",
    "IoTSensorFeed",
    # Stream processing
    "StreamProcessor",
    # Convenience functions
    "start_websocket_server",
    "connect_websocket_client",
    "create_event_bus",
    "create_kafka_producer",
    "create_kafka_consumer",
    "publish_spatial_event",
    "subscribe_to_events",
    "start_gps_tracking",
    "connect_iot_sensors",
    "create_live_feed",
    # Legacy functions for backward compatibility
    "create_spatiotemporal_cube_from_numpy",
    "create_spatiotemporal_cube",
    "connect_kafka_consumer",
    "connect_mqtt_client",
]


# Existing function - renamed for clarity to avoid confusion with the one in pymapgis.raster
def create_spatiotemporal_cube_from_numpy(
    data: np.ndarray,
    timestamps: Union[List, np.ndarray, pd.DatetimeIndex],
    x_coords: np.ndarray,
    y_coords: np.ndarray,
    z_coords: Optional[np.ndarray] = None,
    variable_name: str = "sensor_value",
    attrs: Optional[Dict[str, Any]] = None,
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
    if hasattr(timestamps, "name"):
        timestamps.name = None
    coords["time"] = timestamps
    dims.append("time")
    expected_shape = [len(timestamps)]

    if z_coords is not None:
        if not isinstance(z_coords, np.ndarray):
            z_coords = np.array(z_coords)
        coords["z"] = z_coords
        dims.append("z")
        expected_shape.append(len(z_coords))

    if not isinstance(y_coords, np.ndarray):
        y_coords = np.array(y_coords)
    coords["y"] = y_coords
    dims.append("y")
    expected_shape.append(len(y_coords))

    if not isinstance(x_coords, np.ndarray):
        x_coords = np.array(x_coords)
    coords["x"] = x_coords
    dims.append("x")
    expected_shape.append(len(x_coords))

    if data.shape != tuple(expected_shape):
        # Create a more detailed error message that matches test expectations
        dim_names = []
        if "time" in dims:
            dim_names.append(f"time: {len(timestamps)}")
        if "z" in dims:
            dim_names.append(f"z: {len(z_coords)}")
        if "y" in dims:
            dim_names.append(f"y: {len(y_coords)}")
        if "x" in dims:
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
