# Real-time Data Streaming with Kafka

PyMapGIS provides basic connectors to help you integrate with real-time data streams from Kafka. This example demonstrates how to set up a Kafka consumer.

## 1. Prerequisites

- **Kafka Installation:** You need a running Kafka instance (broker). You can download Kafka from [apache.kafka.org](https://kafka.apache.org/downloads) or use a managed Kafka service.
- **`kafka-python` Library:** PyMapGIS uses `kafka-python`. Install it if you haven't:
  ```bash
  pip install pymapgis[kafka]
  # or directly: pip install kafka-python
  ```

## 2. Setting up a Kafka Consumer

The `connect_kafka_consumer` function helps initialize a `KafkaConsumer` object from the `kafka-python` library.

```python
import pymapgis.streaming as pmg_stream
import json # Example if your messages are JSON

# Kafka connection parameters
KAFKA_TOPIC = 'geospatial_data_stream' # Replace with your topic
KAFKA_BROKERS = 'localhost:9092'      # Replace with your Kafka broker address(es)
# KAFKA_BROKERS = ['broker1:9092', 'broker2:9092'] # For multiple brokers

# Optional: Consumer group ID
# If you want multiple instances of your consumer to share the load (and not get duplicate messages),
# use the same group_id. If None, it's an independent consumer.
CONSUMER_GROUP_ID = 'pymapgis_consumer_group_1'

try:
    # Connect to Kafka
    consumer = pmg_stream.connect_kafka_consumer(
        topic=KAFKA_TOPIC,
        bootstrap_servers=KAFKA_BROKERS,
        group_id=CONSUMER_GROUP_ID,
        auto_offset_reset='earliest',  # Start reading from the beginning of the topic if no offset committed
        # Example: If your messages are JSON strings, add a deserializer
        value_deserializer=lambda v: json.loads(v.decode('utf-8', 'ignore')),
        # consumer_timeout_ms=10000 # Stop blocking for messages after 10s
    )
    print(f"Successfully connected to Kafka topic: {KAFKA_TOPIC} at {KAFKA_BROKERS}")
    print("Listening for messages... (Press Ctrl+C to stop)")

    # Consuming messages
    # The consumer is an iterator. It will block until a message is available
    # or consumer_timeout_ms is reached.
    for message in consumer:
        # `message` is an object containing metadata and the actual value.
        # message.topic, message.partition, message.offset, message.key, message.value
        print(f"\nReceived message from topic '{message.topic}' (partition {message.partition}, offset {message.offset}):")

        # Assuming the message value is a dictionary (due to JSON deserializer)
        data_payload = message.value
        print(f"  Key: {message.key}") # If you use keyed messages
        print(f"  Timestamp (Kafka): {message.timestamp}") # Message timestamp from Kafka
        print(f"  Value (payload): {data_payload}")

        # --- Your data processing logic here ---
        # Example: if data_payload contains coordinates and a sensor reading
        # if isinstance(data_payload, dict) and 'latitude' in data_payload and 'longitude' in data_payload:
        #     print(f"  Sensor ID: {data_payload.get('sensor_id', 'N/A')}")
        #     print(f"  Location: Lat {data_payload['latitude']}, Lon {data_payload['longitude']}")
        #     print(f"  Reading: {data_payload.get('value', 'N/A')}")
        #     # Further processing: e.g., update a map, store in database, aggregate, etc.
        # -----------------------------------------

except ImportError:
    print("Error: kafka-python library is not installed. Please run: pip install pymapgis[kafka]")
except RuntimeError as e:
    print(f"Error connecting to or consuming from Kafka: {e}")
    print("Ensure Kafka is running and accessible, and the topic exists.")
except KeyboardInterrupt:
    print("\nConsumer stopped by user.")
finally:
    if 'consumer' in locals() and consumer:
        print("Closing Kafka consumer...")
        consumer.close() # Important to release resources
```

## 3. Producing Messages to Kafka (Conceptual)

PyMapGIS currently focuses on providing a consumer connector. To produce messages to Kafka for testing or for your applications, you would use `kafka-python`'s `KafkaProducer`.

```python
# Conceptual example for producing messages (not a PyMapGIS function)
# from kafka import KafkaProducer
# import json
# import time

# producer = KafkaProducer(
#     bootstrap_servers=KAFKA_BROKERS,
#     value_serializer=lambda v: json.dumps(v).encode('utf-8')
# )

# for i in range(5):
#     sample_data = {
#         'sensor_id': f'sensor_py_{i%2}',
#         'latitude': 34.0522 + (i*0.01),
#         'longitude': -118.2437 + (i*0.01),
#         'value': 20 + i,
#         'event_time': time.time()
#     }
#     producer.send(KAFKA_TOPIC, value=sample_data)
#     print(f"Sent: {sample_data}")
#     time.sleep(2)

# producer.flush() # Ensure all messages are sent
# producer.close()
```

## Important Considerations

- **Error Handling:** Robust applications require more comprehensive error handling (e.g., for deserialization errors, Kafka broker outages, schema changes).
- **Deserialization:** The `value_deserializer` is crucial. It should match how your data is produced (e.g., JSON, Avro, Protobuf).
- **Configuration:** `kafka-python` offers many configuration options for the consumer (security, performance tuning, offset management). Refer to the [kafka-python documentation](https://kafka-python.readthedocs.io/) for details.
- **Asynchronous Processing:** For high-throughput applications, you might process messages asynchronously or in batches.
- **Message Schemas:** Using a schema registry (like Confluent Schema Registry with Avro) is recommended for production systems to manage data evolution.
```
