# Real-time Data Streaming with MQTT

PyMapGIS includes basic connectors for MQTT (Message Queuing Telemetry Transport), a lightweight messaging protocol ideal for IoT devices and real-time updates. This example shows how to set up an MQTT client to subscribe to topics.

## 1. Prerequisites

- **MQTT Broker:** You need access to an MQTT broker. This could be a local installation (e.g., Mosquitto) or a cloud-based MQTT service.
- **`paho-mqtt` Library:** PyMapGIS uses the `paho-mqtt` library. Install it if you haven't:
  ```bash
  pip install pymapgis[mqtt]
  # or directly: pip install paho-mqtt
  ```

## 2. Setting up an MQTT Client

The `connect_mqtt_client` function from `pymapgis.streaming` helps initialize and connect an MQTT client from the `paho-mqtt` library. The client's network loop is started automatically in a background thread.

You need to define callback functions to handle events like successful connection and incoming messages.

```python
import pymapgis.streaming as pmg_stream
import time
import json # Example if your messages are JSON

# MQTT Broker Configuration
MQTT_BROKER_ADDRESS = "localhost"  # Replace with your broker's address (e.g., "test.mosquitto.org")
MQTT_PORT = 1883                   # Default MQTT port
MQTT_TOPIC = "geospatial/sensor/+/data" # Example topic with wildcard for sensor ID
# The '+' is a single-level wildcard. '#' is a multi-level wildcard for end of topic.

# --- Callback Functions ---
# These functions will be called by the Paho MQTT client upon certain events.

def on_connect(client, userdata, flags, rc):
    """Called when the client receives a CONNACK response from the server."""
    if rc == 0:
        print(f"Successfully connected to MQTT broker at {MQTT_BROKER_ADDRESS}:{MQTT_PORT}")
        # Subscribe to the topic(s) once connected
        client.subscribe(MQTT_TOPIC)
        print(f"Subscribed to topic: {MQTT_TOPIC}")
    else:
        print(f"Failed to connect to MQTT broker, return code {rc}\n")
        # rc values:
        # 0: Connection successful
        # 1: Connection refused - incorrect protocol version
        # 2: Connection refused - invalid client identifier
        # 3: Connection refused - server unavailable
        # 4: Connection refused - bad username or password
        # 5: Connection refused - not authorised
        # 6-255: Currently unused.

def on_message(client, userdata, msg):
    """Called when a message has been received on a topic that the client subscribes to."""
    print(f"\nReceived message on topic '{msg.topic}':")
    payload_str = msg.payload.decode('utf-8', 'ignore') # Decode payload to string
    print(f"  Payload: {payload_str}")
    print(f"  QoS: {msg.qos}, Retain: {msg.retain}")

    # --- Your data processing logic here ---
    # Example: Attempt to parse payload as JSON
    try:
        data_payload = json.loads(payload_str)
        if isinstance(data_payload, dict) and 'latitude' in data_payload and 'longitude' in data_payload:
            print(f"  Sensor ID from topic: {msg.topic.split('/')[-2]}") # If using wildcard like "sensor/+/data"
            print(f"  Location: Lat {data_payload['latitude']}, Lon {data_payload['longitude']}")
            print(f"  Value: {data_payload.get('value', 'N/A')}")
            # Further processing...
    except json.JSONDecodeError:
        print("  Payload is not valid JSON.")
    # -----------------------------------------

def on_disconnect(client, userdata, rc):
    """Called when the client disconnects from the broker."""
    if rc != 0:
        print(f"Unexpected MQTT disconnection. Will attempt to reconnect. Return code: {rc}")
    else:
        print("MQTT client disconnected gracefully.")

# --- Main MQTT Client Setup ---
try:
    # Create and connect the MQTT client
    mqtt_client = pmg_stream.connect_mqtt_client(
        broker_address=MQTT_BROKER_ADDRESS,
        port=MQTT_PORT,
        client_id="pymapgis_mqtt_client_01" # Choose a unique client ID or leave empty
    )

    # Assign the callback functions to the client
    mqtt_client.on_connect = on_connect
    mqtt_client.on_message = on_message
    mqtt_client.on_disconnect = on_disconnect

    print("MQTT client setup complete. Waiting for messages... (Press Ctrl+C to stop)")

    # Keep the main thread alive to allow the background loop to run
    # and callbacks to be processed.
    while True:
        time.sleep(1) # Keep main thread alive

except ImportError:
    print("Error: paho-mqtt library is not installed. Please run: pip install pymapgis[mqtt]")
except RuntimeError as e:
    print(f"Error setting up MQTT client: {e}")
    print("Ensure the MQTT broker is running and accessible.")
except KeyboardInterrupt:
    print("\nMQTT client stopped by user.")
finally:
    if 'mqtt_client' in locals() and mqtt_client:
        print("Disconnecting MQTT client...")
        mqtt_client.loop_stop() # Stop the background network loop
        mqtt_client.disconnect()
```

## 3. Publishing Messages to MQTT (Conceptual)

To test your subscriber or for your applications, you might need to publish messages to your MQTT broker.

```python
# Conceptual example for publishing messages (not a PyMapGIS function)
# import paho.mqtt.publish as publish
# import json
# import time

# for i in range(5):
#     sensor_id = f"sensor{(i%2)+1}" # e.g., sensor1, sensor2
#     topic = f"geospatial/sensor/{sensor_id}/data"
#     payload_data = {
#         'latitude': 34.0522 + (i*0.01),
#         'longitude': -118.2437 + (i*0.01),
#         'value': 20 + i,
#         'timestamp': time.time()
#     }
#     payload_json = json.dumps(payload_data)

#     try:
#         publish.single(topic, payload_json, hostname=MQTT_BROKER_ADDRESS, port=MQTT_PORT)
#         print(f"Published to {topic}: {payload_json}")
#     except Exception as e:
#         print(f"Failed to publish: {e}")
#     time.sleep(2)
```

## Important Considerations

- **Callbacks:** The core of an MQTT application is in its callback functions (`on_connect`, `on_message`, etc.).
- **Topics:** MQTT uses a hierarchical topic structure. Wildcards (`+` for single level, `#` for multiple levels) are powerful for subscribing to multiple feeds.
- **Quality of Service (QoS):** MQTT supports three QoS levels for message delivery:
    - 0: At most once (fire and forget)
    - 1: At least once (acknowledgment required)
    - 2: Exactly once (two-phase acknowledgment)
  The `paho-mqtt` library handles these.
- **Security:** For production, ensure your MQTT communication is secured (e.g., using TLS, username/password authentication, client certificates). `paho-mqtt` supports these.
- **Keep Alive:** The `keepalive` parameter in `connect_mqtt_client` helps the client and broker detect unresponsive connections.
```
