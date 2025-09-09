import asyncio
import os
import uuid

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

BATCH_SIZE = 1000
BATCHES = 3


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
        ],
    )

    receipts = await client.create_entities([entity])
    return receipts[0].entity_key


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
            ],
        )

        entities.append(entity)

    # Send batch
    receipts = await client.create_entities(entities)
    print(f"Batch no {batch_no}: Created {len(receipts)} entities")


async def create_client() -> GolemBaseClient | None:
    """Create and return GolemBaseClient instance or None on error."""
    try:
        # Convert hex string to bytes
        private_key_hex = PRIVATE_KEY.replace("0x", "")
        private_key_bytes = bytes.fromhex(private_key_hex)

        # Create client
        client = await GolemBaseClient.create_rw_client(
            rpc_url=RPC_URL, ws_url=WS_URL, private_key=private_key_bytes
        )
        print("Connected to Golem DB")
        return client  # noqa: TRY300

    # in case of an exception/error just return None
    except Exception as e:  # noqa: BLE001
        print(f"Error during client creation/connection (returning None): {e}")
        return None


async def main() -> None:
    """Create multiple entities with different annotations."""
    client = await create_client()

    if isinstance(client, GolemBaseClient):
        for i in range(BATCHES):
            await create_batch(client, i)

        await client.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
