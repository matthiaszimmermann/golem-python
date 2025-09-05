import asyncio
import json
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


async def query_entities(client, entity_key):
    print(f"Entity metadata: {await client.get_entity_metadata(entity_key)}")
    print(f"Entity storage: {await client.get_storage_value(entity_key)}")

    # 1. Simple equality query for strings (use double quotes)
    greetings = await client.query_entities('type="greeting"')
    print(f"Found {len(greetings)} greeting entities")

    # 2. Processing results
    for result in greetings:
        entity_key = result.entity_key
        decoded = result.storage_value.decode("utf-8")
        try:
            data = json.loads(decoded)
            print(f"Entity: {entity_key}, Decoded JSON data {data}")
        except (json.JSONDecodeError, ValueError):
            print(f"Entity: {entity_key}, Decoded data {decoded}")

    # 3. Numeric equality (no quotes for numbers)
    print(f"version_one: {await client.query_entities('version=1')}")
    print(f"high_priority: {await client.query_entities('priority=5')}")

    # 4. Numeric comparison operators
    print(f"above_threshold: {await client.query_entities('priority>3')}")
    print(f"old_versions: {await client.query_entities('version<10')}")
    print(f"in_range: {await client.query_entities('score>=80')}")

    # 5. Combining conditions with AND (&&)
    print(f"specific: {await client.query_entities('type="message" && version=2')}")
    print(f"filtered: {await client.query_entities('status="active" && priority>3')}")

    # 6. Using OR (||) for multiple options
    print(f"messages: {await client.query_entities('type="message" || type="alert"')}")

    # 7. Complex queries with parentheses
    print(
        f"complex_query: {
            await client.query_entities(
                '(type="greeting" && version>2) || status="urgent"'
            )
        }"
    )

    # 8. Query by owner with variable
    owner = client.get_account_address()
    print(f"by_owner: {await client.query_entities(f'$owner="{owner}"')}")

    # Note: String values need double quotes: type="message"
    # Numbers don't need quotes: priority=5
    # Use && for AND operator, || for OR operator in complex queries


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
    entity_key = await create_first_entity(client)
    await query_entities(client, entity_key)

    if isinstance(client, GolemBaseClient):
        await client.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
