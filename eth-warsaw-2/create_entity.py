import asyncio
import os

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


async def create_first_entity(client):
    # Create entity
    entity = GolemBaseCreate(
        data=b"Hello, Golem DB from Python!",
        btl=100,  # Expires after 100 blocks
        string_annotations=[
            Annotation(key="type", value="greeting"),
            Annotation(key="language", value="python"),
        ],
        numeric_annotations=[
            Annotation(key="priority", value=1),
            Annotation(key="version", value=3),
        ],
    )

    # Send to blockchain
    receipts = await client.create_entities([entity])
    receipt = receipts[0]

    print("Entity created!")
    print(f"Entity key: {receipt.entity_key}")
    print(f"Expires at block: {receipt.expiration_block}")

    return receipt.entity_key


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
    await create_first_entity(client)

    if isinstance(client, GolemBaseClient):
        await client.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
