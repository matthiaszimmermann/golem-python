import argparse
import asyncio
import json
import os
import sys
import threading
import time
from datetime import datetime

import pika
from dotenv import load_dotenv
from golem_base_sdk import EntityKey, GenericBytes, GolemBaseClient
from pika.adapters.blocking_connection import BlockingChannel

# When running inside Docker containers (dev containers etc.)
HOST = "host.docker.internal"

# Configuration
PRIVATE_KEY = os.getenv(
    "PRIVATE_KEY", "0x0000000000000000000000000000000000000000000000000000000000000001"
)
RPC_URL = os.getenv("RPC_URL", "https://ethwarsaw.holesky.golemdb.io/rpc")
WS_URL = os.getenv("WS_URL", "wss://ethwarsaw.holesky.golemdb.io/rpc/ws")

# RabbitMQ queue name
GOLEM_DB_QUEUE = "golem_db_events"

# Global client variable
client = None
channel = None
callback_counter = 0

# Load environment variables
load_dotenv()


def get_timestamp_ms() -> int:
    """Return the current timestamp in milliseconds since 1970-01-01T00:00:00Z."""
    return int(time.time() * 1000)


def get_timestamp_iso() -> str:
    """Get the current timestamp in ISO 8601 format with milliseconds precision."""
    return datetime.now().isoformat(timespec="milliseconds")  # noqa: DTZ005


def start_background_loop() -> asyncio.AbstractEventLoop:
    """Start an asyncio event loop in a background thread."""
    loop = asyncio.new_event_loop()
    t = threading.Thread(target=loop.run_forever, daemon=True)
    t.start()
    return loop


def _print_entity_created_info(
    entity_key: str, created_ms: int, received_ms: int
) -> None:
    latency_ms = received_ms - created_ms if created_ms > 0 else -1

    key_short = (
        f"{entity_key[:6]}...{entity_key[-4:]}" if entity_key != "N/A" else "N/A"
    )

    print(f"{get_timestamp_iso()} MQ message: {key_short}, latency [ms]: {latency_ms}")


async def _get_and_print_entity_created_info(
    entity_key_str: str, received_ms: int
) -> None:
    """Get the 'timestamp' numeric annotation from entity metadata."""
    if client is None:
        _print_entity_created_info(entity_key_str, 0, received_ms)
        return

    try:
        entity_key = EntityKey(GenericBytes.from_hex_string(entity_key_str))
        metadata = await client.get_entity_metadata(entity_key=entity_key)
        if hasattr(metadata, "numeric_annotations"):
            for annotation in metadata.numeric_annotations:
                if annotation.key == "timestamp":
                    created_ms = annotation.value
                    _print_entity_created_info(entity_key_str, created_ms, received_ms)
                    return

    except Exception as e:  # noqa: BLE001
        print(f"Error fetching metadata for {entity_key_str}: {e}")

    _print_entity_created_info(entity_key_str, 0, received_ms)
    return


# Callback function to process messages
def message_received(ch, method, properties, body) -> None:  # noqa: ANN001, ARG001, D103
    global callback_counter  # noqa: PLW0603

    received_ms = get_timestamp_ms()
    message = body.decode()
    event = json.loads(message)
    entity_key = event.get("entity_key", "N/A")
    callback_counter += 1

    # Throttle Golem DB reads
    if callback_counter % 50 == 0:
        asyncio.run_coroutine_threadsafe(
            _get_and_print_entity_created_info(entity_key, received_ms), background_loop
        )
    else:
        _print_entity_created_info(entity_key, 0, received_ms)


async def create_client() -> None:
    """Create and return GolemBaseClient instance or None on error."""
    global client  # noqa: PLW0603

    try:
        # Convert hex string to bytes
        private_key_hex = PRIVATE_KEY.replace("0x", "")
        private_key_bytes = bytes.fromhex(private_key_hex)

        # Create client
        client = await GolemBaseClient.create_rw_client(
            rpc_url=RPC_URL, ws_url=WS_URL, private_key=private_key_bytes
        )

    # in case of an exception/error just return None
    except Exception as e:  # noqa: BLE001
        print(f"Error during client creation/connection (returning None): {e}")


def setup_mq_consumer() -> BlockingChannel:
    """Set up RabbitMQ consumer to listen for messages."""
    # Connect and create channel object
    connection = pika.BlockingConnection(pika.ConnectionParameters(HOST))
    channel = connection.channel()

    # Ensure queue exists
    channel.queue_declare(queue="golem_db_events")

    # Subscribe to my_queue and start consuming messages
    channel.basic_consume(
        queue="golem_db_events", on_message_callback=message_received, auto_ack=True
    )

    print(f"Connected to Rabbit MQ with queue: {GOLEM_DB_QUEUE}")
    return channel


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="RabbitMQ Golem Consumer")
    parser.add_argument("name", type=str, help="Consumer name")
    args = parser.parse_args()
    consumer_name = args.name
    print(f"\n=== Rabbit MQ consumer '{consumer_name}' ===")

    background_loop = start_background_loop()

    try:
        asyncio.run(create_client())
        if client is None:
            print("Failed to create GolemBaseClient, exiting...")
            sys.exit(1)
    except Exception as e:  # noqa: BLE001
        print(f"Error during client creation: {e}\nExiting...")
        sys.exit(2)

    # Set the event loop for the main thread, allows for graceful shutdown
    asyncio.set_event_loop(asyncio.new_event_loop())

    try:
        channel = setup_mq_consumer()
        print("To exit press CTRL+C")
        channel.start_consuming()
    except KeyboardInterrupt:
        print("Shutting down...")
