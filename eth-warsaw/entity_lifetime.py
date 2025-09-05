import asyncio
import os

from dotenv import load_dotenv
from golem_base_sdk import Annotation, GolemBaseClient, GolemBaseCreate, GolemBaseExtend

# Load environment variables
load_dotenv()

# Configuration
PRIVATE_KEY = os.getenv(
    "PRIVATE_KEY", "0x0000000000000000000000000000000000000000000000000000000000000001"
)
RPC_URL = os.getenv("RPC_URL", "https://ethwarsaw.holesky.golemdb.io/rpc")
WS_URL = os.getenv("WS_URL", "wss://ethwarsaw.holesky.golemdb.io/rpc/ws")


async def manage_btl(client):
    # Create entity with specific BTL
    entity = GolemBaseCreate(
        data=b"Temporary data",
        btl=50,  # Expires after 50 blocks
        string_annotations=[Annotation(key="type", value="temporary")],
        numeric_annotations=[],
    )

    receipts = await client.create_entities([entity])
    receipt = receipts[0]
    print(f"Created entity expires at block: {receipt.expiration_block}")

    # Extend BTL
    extend = GolemBaseExtend(
        entity_key=receipt.entity_key,
        number_of_blocks=200,  # Additional blocks
    )

    extend_receipts = await client.extend_entities([extend])
    ext_receipt = extend_receipts[0]
    print(
        f"Extended from {ext_receipt.old_expiration_block} to {ext_receipt.new_expiration_block}"
    )

    # Get entity metadata
    metadata = await client.get_entity_metadata(receipt.entity_key)
    print(f"Entity expires at block: {metadata.expires_at_block}")


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
    await manage_btl(client)

    if isinstance(client, GolemBaseClient):
        await client.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
