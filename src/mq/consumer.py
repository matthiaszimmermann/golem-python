import pika

# When running inside Docker containers (dev containers etc.)
HOST = "host.docker.internal"

# Connect and create channel object
connection = pika.BlockingConnection(pika.ConnectionParameters(HOST))
channel = connection.channel()

# Ensure queue exists
channel.queue_declare(queue="golem_db_events")


# Callback function to process messages
def callback(ch, method, properties, body) -> None:  # noqa: ANN001, ARG001, D103
    print(f" [x] body: {body.decode()}")


# Subscribe to my_queue and start consuming messages
channel.basic_consume(
    queue="golem_db_events", on_message_callback=callback, auto_ack=True
)

print(" [*] Waiting for messages. To exit press CTRL+C")
channel.start_consuming()
