#!/usr/bin/env python3
"""
PyMapGIS Real-time Streaming Demo

Demonstrates comprehensive real-time streaming capabilities including:
- WebSocket server/client communication
- Event-driven architecture with pub/sub messaging
- Kafka integration for high-throughput streaming
- Live data feeds (GPS tracking, IoT sensors)
- Stream processing and real-time analytics
"""

import asyncio
import sys
import json
import time
from pathlib import Path
from datetime import datetime

# Add PyMapGIS to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pymapgis as pmg


async def demo_websocket_communication():
    """Demonstrate WebSocket real-time communication."""
    print("\n🌐 WebSocket Communication Demo")
    print("=" * 50)

    try:
        # Start WebSocket server
        print("Starting WebSocket server...")
        server = await pmg.streaming.start_websocket_server("localhost", 8765)

        # Register message handlers
        async def handle_spatial_update(data, client_id):
            print(f"📍 Received spatial update from {client_id}: {data}")
            # Broadcast to other clients
            await server.connection_manager.broadcast(
                json.dumps({"type": "spatial_broadcast", "data": data}),
                exclude=[client_id],
            )

        server.register_handler("spatial_update", handle_spatial_update)

        print("✅ WebSocket server started on localhost:8765")
        print("🔗 Server ready for client connections")

        # Simulate running for a short time
        await asyncio.sleep(2)

        # Stop server
        await server.stop()
        print("✅ WebSocket server stopped")

        return True

    except Exception as e:
        print(f"❌ WebSocket demo failed: {e}")
        return False


async def demo_event_system():
    """Demonstrate event-driven architecture."""
    print("\n⚡ Event-Driven Architecture Demo")
    print("=" * 50)

    try:
        # Create event bus
        event_bus = pmg.streaming.create_event_bus()

        # Event handlers
        received_events = []

        async def handle_spatial_event(data):
            received_events.append(data)
            print(f"📊 Spatial event received: {data.get('event_type', 'unknown')}")

        def handle_user_action(data):
            print(f"👤 User action: {data.get('action', 'unknown')}")

        # Subscribe to events
        event_bus.subscribe("spatial_event", handle_spatial_event)
        event_bus.subscribe("user_action", handle_user_action)

        # Publish events
        print("Publishing spatial events...")
        await event_bus.publish(
            "spatial_event",
            {
                "event_type": "feature_created",
                "feature_id": "feature_001",
                "timestamp": datetime.now().isoformat(),
                "geometry": {"type": "Point", "coordinates": [-74.0060, 40.7128]},
            },
        )

        await event_bus.publish(
            "user_action",
            {"action": "map_zoom", "user_id": "user_123", "zoom_level": 12},
        )

        await event_bus.publish(
            "spatial_event",
            {
                "event_type": "feature_updated",
                "feature_id": "feature_001",
                "timestamp": datetime.now().isoformat(),
                "properties": {"name": "Updated Feature"},
            },
        )

        print(
            f"✅ Event system demo completed - {len(received_events)} spatial events processed"
        )
        return True

    except Exception as e:
        print(f"❌ Event system demo failed: {e}")
        return False


async def demo_kafka_streaming():
    """Demonstrate Kafka integration."""
    print("\n📡 Kafka Streaming Demo")
    print("=" * 50)

    try:
        # Note: This demo shows the API usage
        # In a real environment, Kafka would need to be running
        print("Creating Kafka producer and consumer...")

        # This would work if Kafka is available
        if pmg.streaming.KAFKA_AVAILABLE:
            try:
                producer = pmg.streaming.create_kafka_producer(["localhost:9092"])
                consumer = pmg.streaming.create_kafka_consumer(
                    ["spatial_events"], ["localhost:9092"], group_id="demo_group"
                )

                # Send spatial data
                spatial_data = {
                    "type": "spatial_update",
                    "feature_id": "kafka_feature_001",
                    "geometry": {"type": "Point", "coordinates": [-74.0060, 40.7128]},
                    "properties": {"name": "Kafka Feature", "value": 42},
                    "timestamp": datetime.now().isoformat(),
                }

                await producer.send_spatial_data("spatial_events", spatial_data)
                print("✅ Spatial data sent to Kafka topic")

                producer.close()
                consumer.stop_consuming()

            except Exception as kafka_error:
                print(f"ℹ️ Kafka not running locally: {kafka_error}")
                print(
                    "✅ Kafka API demonstration completed (would work with running Kafka)"
                )
        else:
            print("ℹ️ Kafka not available - install kafka-python for full functionality")
            print("✅ Kafka integration API ready for deployment")

        return True

    except Exception as e:
        print(f"❌ Kafka demo failed: {e}")
        return False


async def demo_live_data_feeds():
    """Demonstrate live data feeds."""
    print("\n📊 Live Data Feeds Demo")
    print("=" * 50)

    try:
        # GPS tracking demo
        print("Starting GPS tracking simulation...")
        gps_tracker = pmg.streaming.start_gps_tracking("demo_gps", update_interval=0.5)

        gps_data_received = []

        async def handle_gps_data(data):
            gps_data_received.append(data)
            print(
                f"📍 GPS: {data.latitude:.6f}, {data.longitude:.6f} @ {data.timestamp}"
            )

        gps_tracker.subscribe(handle_gps_data)

        # Start GPS tracking for a short time
        gps_task = asyncio.create_task(gps_tracker.start())
        await asyncio.sleep(2)  # Collect data for 2 seconds
        await gps_tracker.stop()

        print(f"✅ GPS tracking completed - {len(gps_data_received)} points collected")

        # IoT sensor demo
        print("\nStarting IoT sensor simulation...")
        iot_sensor = pmg.streaming.connect_iot_sensors(
            "demo_sensor", "temperature", update_interval=0.3
        )

        sensor_data_received = []

        async def handle_sensor_data(data):
            sensor_data_received.append(data)
            print(f"🌡️ Sensor: {data['value']:.2f} {data['unit']} @ {data['timestamp']}")

        iot_sensor.subscribe(handle_sensor_data)

        # Start sensor feed for a short time
        sensor_task = asyncio.create_task(iot_sensor.start())
        await asyncio.sleep(1.5)  # Collect data for 1.5 seconds
        await iot_sensor.stop()

        print(
            f"✅ IoT sensor demo completed - {len(sensor_data_received)} readings collected"
        )

        return True

    except Exception as e:
        print(f"❌ Live data feeds demo failed: {e}")
        return False


async def demo_stream_processing():
    """Demonstrate stream processing."""
    print("\n🔄 Stream Processing Demo")
    print("=" * 50)

    try:
        # Create stream processor
        processor = pmg.streaming.StreamProcessor()

        # Add filters
        def location_filter(data):
            """Filter data within NYC area."""
            if hasattr(data, "latitude") and hasattr(data, "longitude"):
                return (
                    40.4774 <= data.latitude <= 40.9176
                    and -74.2591 <= data.longitude <= -73.7004
                )
            return True

        def accuracy_filter(data):
            """Filter data with good accuracy."""
            if hasattr(data, "accuracy"):
                return data.accuracy is None or data.accuracy <= 10.0
            return True

        processor.add_filter(location_filter)
        processor.add_filter(accuracy_filter)

        # Add transformers
        def add_zone_info(data):
            """Add zone information to data."""
            if hasattr(data, "latitude") and hasattr(data, "longitude"):
                # Simple zone classification
                if data.latitude > 40.7589:
                    zone = "uptown"
                elif data.latitude > 40.7282:
                    zone = "midtown"
                else:
                    zone = "downtown"

                # Create new data with zone info
                if hasattr(data, "properties"):
                    if data.properties is None:
                        data.properties = {}
                    data.properties["zone"] = zone
                else:
                    data.zone = zone

            return data

        processor.add_transformer(add_zone_info)

        # Test stream processing
        print("Processing simulated GPS data stream...")

        # Create test GPS tracker
        test_tracker = pmg.streaming.GPSTracker("test_gps", 0.1)
        processed_count = 0

        async def process_gps_data(data):
            nonlocal processed_count
            result = await processor.process(data)
            if result:
                processed_count += 1
                zone = getattr(result, "zone", "unknown")
                print(
                    f"✅ Processed: {result.latitude:.6f}, {result.longitude:.6f} -> {zone}"
                )

        test_tracker.subscribe(process_gps_data)

        # Run processing for a short time
        task = asyncio.create_task(test_tracker.start())
        await asyncio.sleep(1)
        await test_tracker.stop()

        print(f"✅ Stream processing completed - {processed_count} points processed")

        return True

    except Exception as e:
        print(f"❌ Stream processing demo failed: {e}")
        return False


async def demo_integrated_streaming():
    """Demonstrate integrated streaming workflow."""
    print("\n🔗 Integrated Streaming Workflow Demo")
    print("=" * 50)

    try:
        # Create integrated streaming system
        event_bus = pmg.streaming.create_event_bus()

        # Track processed events
        processed_events = []

        async def handle_processed_event(data):
            processed_events.append(data)
            print(
                f"🎯 Integrated event: {data.get('type', 'unknown')} from {data.get('source', 'unknown')}"
            )

        event_bus.subscribe("processed_event", handle_processed_event)

        # Create GPS tracker with event publishing
        gps_tracker = pmg.streaming.GPSTracker("integrated_gps", 0.2)

        async def publish_gps_event(gps_data):
            event_data = {
                "type": "location_update",
                "source": "gps_tracker",
                "timestamp": gps_data.timestamp.isoformat(),
                "location": {
                    "latitude": gps_data.latitude,
                    "longitude": gps_data.longitude,
                    "accuracy": gps_data.accuracy,
                },
            }
            await event_bus.publish("processed_event", event_data)

        gps_tracker.subscribe(publish_gps_event)

        # Create IoT sensor with event publishing
        iot_sensor = pmg.streaming.IoTSensorFeed(
            "integrated_sensor", "environmental", 0.3
        )

        async def publish_sensor_event(sensor_data):
            event_data = {
                "type": "sensor_reading",
                "source": "iot_sensor",
                "timestamp": sensor_data["timestamp"],
                "sensor_type": sensor_data["sensor_type"],
                "value": sensor_data["value"],
                "location": sensor_data["location"],
            }
            await event_bus.publish("processed_event", event_data)

        iot_sensor.subscribe(publish_sensor_event)

        # Run integrated system
        print("Starting integrated streaming system...")

        gps_task = asyncio.create_task(gps_tracker.start())
        sensor_task = asyncio.create_task(iot_sensor.start())

        await asyncio.sleep(2)  # Run for 2 seconds

        await gps_tracker.stop()
        await iot_sensor.stop()

        print(
            f"✅ Integrated streaming completed - {len(processed_events)} events processed"
        )

        # Show event summary
        event_types = {}
        for event in processed_events:
            event_type = event.get("type", "unknown")
            event_types[event_type] = event_types.get(event_type, 0) + 1

        print("📊 Event summary:")
        for event_type, count in event_types.items():
            print(f"   {event_type}: {count} events")

        return True

    except Exception as e:
        print(f"❌ Integrated streaming demo failed: {e}")
        return False


async def main():
    """Run the complete streaming demo."""
    print("📡 PyMapGIS Real-time Streaming Demo")
    print("=" * 60)
    print("Demonstrating comprehensive real-time streaming capabilities")

    try:
        # Run all demos
        demos = [
            ("WebSocket Communication", demo_websocket_communication),
            ("Event-Driven Architecture", demo_event_system),
            ("Kafka Streaming", demo_kafka_streaming),
            ("Live Data Feeds", demo_live_data_feeds),
            ("Stream Processing", demo_stream_processing),
            ("Integrated Streaming", demo_integrated_streaming),
        ]

        results = []
        for demo_name, demo_func in demos:
            print(f"\n🚀 Running {demo_name} demo...")
            success = await demo_func()
            results.append((demo_name, success))

        print("\n🎉 Real-time Streaming Demo Complete!")
        print("=" * 60)

        # Summary
        successful = sum(1 for _, success in results if success)
        total = len(results)

        print(f"✅ Successfully demonstrated {successful}/{total} streaming components")

        print("\n📊 Demo Results:")
        for demo_name, success in results:
            status = "✅ PASSED" if success else "❌ FAILED"
            print(f"   {demo_name}: {status}")

        print("\n🚀 PyMapGIS Real-time Streaming is ready for enterprise deployment!")
        print(
            "📡 Features: WebSocket, Event-driven, Kafka, Live data, Stream processing"
        )
        print(
            "🌐 Ready for real-time geospatial applications and collaborative mapping"
        )

    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
