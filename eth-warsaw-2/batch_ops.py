import asyncio
import os
import uuid

from dotenv import load_dotenv
from golem_base_sdk import Annotation, GolemBaseClient, GolemBaseCreate

# Load environment variables
load_dotenv()
# Configuration
PRIVATE_KEY = os.getenv(
    "PRIVATE_KEY", "0x0000000000000000000000000000000000000000000000000000000000000001"
)
RPC_URL = os.getenv("RPC_URL", "https://ethwarsaw.holesky.golemdb.io/rpc")
WS_URL = os.getenv("WS_URL", "wss://ethwarsaw.holesky.golemdb.io/rpc/ws")


async def batch_operations(client):
    # Create multiple entities at once
    entities = []
    batch_id = str(uuid.uuid4())

    for i in range(10):
        entity = GolemBaseCreate(
            data=f"Message {i}".encode(),
            btl=100,
            string_annotations=[
                Annotation(key="type", value="batch"),
                Annotation(key="batch_id", value=batch_id),
                Annotation(key="index", value=str(i)),
            ],
            numeric_annotations=[
                Annotation(
                    key="sequence", value=i + 1
                )  # Start from 1, not 0 (SDK bug with value 0)
            ],
        )

        entities.append(entity)

    # Send batch
    receipts = await client.create_entities(entities)
    print(f"Created {len(receipts)} entities in batch")

    # Query batch entities
    batch_results = await client.query_entities(
        f'type="batch" && batch_id="{batch_id}"'
    )
    print(f"Found {len(batch_results)} batch entities")


async def create_client():
    try:
        # Convert hex string to bytes
        private_key_hex = PRIVATE_KEY.replace("0x", "")
        private_key_bytes = bytes.fromhex(private_key_hex)
        # Create client
        client = await GolemBaseClient.create_rw_client(
            rpc_url=RPC_URL, ws_url=WS_URL, private_key=private_key_bytes
        )
        print("Connected to Golem DB via ETHWarsaw!")
        # Get owner address
        owner_address = client.get_account_address()
        print(f"Connected with address: {owner_address}")
        return client
    # in case of an exception/error just return None
    except Exception as e:
        print(f"Error during client creation/connection (returning None): {e}")
        return None


async def main():
    client = await create_client()
    await batch_operations(client)

    if isinstance(client, GolemBaseClient):
        await client.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
