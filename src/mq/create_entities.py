import asyncio
import os
import time
import uuid
from datetime import datetime

from dotenv import load_dotenv
from golem_base_sdk import Annotation, EntityKey, GolemBaseClient, GolemBaseCreate

# Load environment variables
load_dotenv()

# Configuration
PRIVATE_KEY = os.getenv(
    "PRIVATE_KEY", "0x0000000000000000000000000000000000000000000000000000000000000001"
)
RPC_URL = os.getenv("RPC_URL", "https://ethwarsaw.holesky.golemdb.io/rpc")
WS_URL = os.getenv("WS_URL", "wss://ethwarsaw.holesky.golemdb.io/rpc/ws")

BATCHES = 10
BATCH_SIZE = 1000  # max (almost): 1500


def get_timestamp_ms() -> int:
    """Return the current timestamp in milliseconds since 1970-01-01T00:00:00Z."""
    return int(time.time() * 1000)


def get_timestamp_iso() -> str:
    """Get the current timestamp in ISO 8601 format with milliseconds precision."""
    return datetime.now().isoformat(timespec="milliseconds")  # noqa: DTZ005


async def create_entity(
    client: GolemBaseClient, entity_type: str, number: int
) -> EntityKey:
    """Create entity with provided type and number annotations."""
    entity = GolemBaseCreate(
        data=b"",
        btl=1000,
        string_annotations=[
            Annotation(key="entity_type", value=entity_type),
        ],
        numeric_annotations=[
            Annotation(key="number", value=number),
            Annotation(key="timestamp", value=get_timestamp_ms()),
        ],
    )

    receipts = await client.create_entities([entity])
    entity_key: EntityKey = receipts[0].entity_key
    print(f"{get_timestamp_iso()} Golem DB entity created: {entity_key}")
    return entity_key


async def create_batch(client: GolemBaseClient, batch_no: int) -> None:
    """Create a batch of entities with batch_id and index annotations."""
    batch_id = str(uuid.uuid4())
    entities = []

    for i in range(BATCH_SIZE):
        entity = GolemBaseCreate(
            data=f"Message {i}".encode(),
            btl=100,
            string_annotations=[
                Annotation(key="batch_id", value=batch_id),
            ],
            numeric_annotations=[
                Annotation(key="batch_no", value=batch_no),
                Annotation(key="idx", value=i),
                Annotation(key="timestamp", value=get_timestamp_ms()),
            ],
        )

        entities.append(entity)

    # Send batch
    receipts = await client.create_entities(entities)
    print(f"{get_timestamp_iso()} Golem DB batch created, entities: {len(receipts)}")


async def create_client() -> GolemBaseClient | None:
    """Create and return GolemBaseClient instance or None on error."""
    try:
        # Convert hex string to bytes
        private_key_hex = PRIVATE_KEY.replace("0x", "")
        private_key_bytes = bytes.fromhex(private_key_hex)

        # Create and return client
        return await GolemBaseClient.create_rw_client(
            rpc_url=RPC_URL, ws_url=WS_URL, private_key=private_key_bytes
        )

    # in case of an exception/error just return None
    except Exception as e:  # noqa: BLE001
        print(f"Error during client creation/connection (returning None): {e}")
        return None


async def main() -> None:
    """Create multiple entities with different annotations."""
    print("\n=== Golem DB entity creator ===")

    client = await create_client()
    print(f"{get_timestamp_iso()} Connected to Golem DB")

    if isinstance(client, GolemBaseClient):
        for i in range(BATCHES):
            await create_batch(client, i)

        await client.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
