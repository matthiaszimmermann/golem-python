import pika
from pika.adapters.blocking_connection import BlockingChannel

# When running inside Docker containers (dev containers etc.)
HOST = "host.docker.internal"

# RabbitMQ queue name
GOLEM_DB_QUEUE = "golem_db_events"


# Callback function to process messages
def message_received(ch, method, properties, body) -> None:  # noqa: ANN001, ARG001, D103
    print(f"- MQ message received. body: {body.decode()}")


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
    try:
        channel = setup_mq_consumer()
        print("To exit press CTRL+C")
        channel.start_consuming()

    except KeyboardInterrupt:
        print("Shutting down...")
