import asyncio
import os
import sys

import pika
from dotenv import load_dotenv
from golem_base_sdk import (
    CreateEntityReturnType,
    ExtendEntityReturnType,
    GolemBaseClient,
    UpdateEntityReturnType,
)
from pika.adapters.blocking_connection import BlockingChannel

# When running inside Docker containers (dev containers etc.)
HOST = "host.docker.internal"

# RabbitMQ queue name
GOLEM_DB_QUEUE = "golem_db_events"

# Load environment variables
load_dotenv()

# Configuration
PRIVATE_KEY = os.getenv(
    "PRIVATE_KEY", "0x0000000000000000000000000000000000000000000000000000000000000001"
)
RPC_URL = os.getenv("RPC_URL", "https://ethwarsaw.holesky.golemdb.io/rpc")
WS_URL = os.getenv("WS_URL", "wss://ethwarsaw.holesky.golemdb.io/rpc/ws")


class EventProcessor:
    """Process Golem DB events and send them as messages to RabbitMQ."""

    client: GolemBaseClient
    event_subscription: any  # SubscriptionHandle  # type: ignore # noqa: PGH003

    mq_connection: pika.BlockingConnection
    mq_channel: BlockingChannel

    def __init__(self) -> None:
        """Initialize the EventProcessor and set up the RabbitMQ producer."""
        self._setup_mq_producer()  # Set up RabbitMQ connection and queue

    async def start(self) -> None:
        """Start Golem DB event monitoring."""
        await self._setup_event_monitoring()

        print("Press Ctrl+C to exit.")
        await asyncio.Event().wait()

    def _publish_to_mq(self, message: str) -> None:
        self.mq_channel.basic_publish(
            routing_key=GOLEM_DB_QUEUE, exchange="", body=message
        )
        print(f"Sent to Rabbit MQ queue '{GOLEM_DB_QUEUE}' -> message:'{message}'")

    def _on_created(self, event: CreateEntityReturnType) -> None:
        self._publish_to_mq(f"Entity created: {event}")

    def _on_updated(self, event: UpdateEntityReturnType) -> None:
        self._publish_to_mq(f"Entity updated: {event}")

    def _on_extended(self, event: ExtendEntityReturnType) -> None:
        self._publish_to_mq(f"Entity extended: {event}")

    def _on_deleted(self, event) -> None:  # noqa: ANN001
        self._publish_to_mq(f"Entity deleted: {event}")

    async def _setup_event_monitoring(self) -> None:
        """Set up and start Golem DB client and event monitoring."""
        try:
            # Convert hex string to bytes
            private_key_hex = PRIVATE_KEY.replace("0x", "")
            private_key_bytes = bytes.fromhex(private_key_hex)

            # Create client
            self.client = await GolemBaseClient.create_rw_client(
                rpc_url=RPC_URL, ws_url=WS_URL, private_key=private_key_bytes
            )
            print("Connected to Golem DB")

        except Exception as e:  # noqa: BLE001
            print(f"Error during client creation/connection: {e}")
            sys.exit(1)

        # Start watching events
        self.event_subscription = await self.client.watch_logs(
            label="",
            create_callback=self._on_created,
            update_callback=self._on_updated,
            extend_callback=self._on_extended,
            delete_callback=self._on_deleted,
        )

        print("Golem DB event monitoring started")

    def _setup_mq_producer(self) -> None:
        """Connect to RabbitMQ and return Golem DB queue."""
        self.mq_connection = pika.BlockingConnection(pika.ConnectionParameters(HOST))
        self.mq_channel = self.mq_connection.channel()

        # Ensure queue exists
        self.mq_channel.queue_declare(queue=GOLEM_DB_QUEUE)
        print(f"Connected to Rabbit MQ with queue: {GOLEM_DB_QUEUE}")


if __name__ == "__main__":
    processor = EventProcessor()
    asyncio.run(processor.start())
