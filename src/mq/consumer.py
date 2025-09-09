import json
from datetime import datetime

import pika
from pika.adapters.blocking_connection import BlockingChannel

# When running inside Docker containers (dev containers etc.)
HOST = "host.docker.internal"

# RabbitMQ queue name
GOLEM_DB_QUEUE = "golem_db_events"


def get_timestamp() -> str:
    """Get the current timestamp in ISO 8601 format with milliseconds precision."""
    return datetime.now().isoformat(timespec="milliseconds")  # noqa: DTZ005


# Callback function to process messages
def message_received(ch, method, properties, body) -> None:  # noqa: ANN001, ARG001, D103
    message = body.decode()
    event = json.loads(message)
    entity_key = event.get("entity_key", "N/A")
    key_short = (
        f"{entity_key[:6]}...{entity_key[-4:]}" if entity_key != "N/A" else "N/A"
    )
    print(f"{get_timestamp()} MQ message received: {key_short}")


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
    import argparse

    parser = argparse.ArgumentParser(description="RabbitMQ Golem Consumer")
    parser.add_argument("name", type=str, help="Consumer name")
    args = parser.parse_args()
    consumer_name = args.name

    try:
        channel = setup_mq_consumer()
        print(f"Consumer {consumer_name}. To exit press CTRL+C")
        channel.start_consuming()

    except KeyboardInterrupt:
        print("Shutting down...")
