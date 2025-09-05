# Full working example with all features
# Save as: golem_example.py

import asyncio
import json
import os
import time
import uuid

from dotenv import load_dotenv
from golem_base_sdk import (
    Annotation,
    GolemBaseClient,
    GolemBaseCreate,
    GolemBaseDelete,
    GolemBaseUpdate,
)

# Load environment variables
load_dotenv()

# Configuration
PRIVATE_KEY = os.getenv(
    "PRIVATE_KEY", "0x0000000000000000000000000000000000000000000000000000000000000001"
)
RPC_URL = "https://ethwarsaw.holesky.golemdb.io/rpc"
WS_URL = "wss://ethwarsaw.holesky.golemdb.io/rpc/ws"


async def main():
    # === Initialize Client ===
    private_key_hex = PRIVATE_KEY.replace("0x", "")
    private_key_bytes = bytes.fromhex(private_key_hex)

    client = await GolemBaseClient.create(
        rpc_url=RPC_URL, ws_url=WS_URL, private_key=private_key_bytes
    )

    print("Connected to Golem DB!")
    print(f"Address: {client.get_account_address()}")

    # Set up real-time event watching
    await client.watch_logs(
        label="",
        create_callback=lambda create: print(f"WATCH-> Create: {create}"),
        update_callback=lambda update: print(f"WATCH-> Update: {update}"),
        delete_callback=lambda delete: print(f"WATCH-> Delete: {delete}"),
        extend_callback=lambda extend: print(f"WATCH-> Extend: {extend}"),
    )

    # === CREATE Operations ===
    print("\n=== CREATE Operations ===")

    # Create entity with unique ID
    entity_id = str(uuid.uuid4())
    data = {
        "message": "Hello from ETHWarsaw 2025!",
        "timestamp": int(time.time()),
        "author": "Python Developer",
    }

    entity = GolemBaseCreate(
        data=json.dumps(data).encode("utf-8"),
        btl=300,  # ~10 minutes (300 blocks at ~2 seconds each)
        string_annotations=[
            Annotation(key="type", value="message"),
            Annotation(key="event", value="ethwarsaw"),
            Annotation(key="id", value=entity_id),
        ],
        numeric_annotations=[
            Annotation(key="version", value=1),
            Annotation(key="timestamp", value=int(time.time())),
        ],
    )

    receipts = await client.create_entities([entity])
    entity_key = receipts[0].entity_key
    print(f"Created entity: {entity_key}")

    # === QUERY Operations ===
    print("\n=== QUERY Operations ===")

    # Query entity by annotations
    results = await client.query_entities(f'id = "{entity_id}" && version = 1')
    print(f"Found {len(results)} entities")

    for result in results:
        data = json.loads(result.storage_value.decode("utf-8"))
        print(f"  Entity: {data}")

    # === UPDATE Operations ===
    print("\n=== UPDATE Operations ===")

    updated_data = {
        "message": "Updated message from ETHWarsaw!",
        "updated": True,
        "updateTime": int(time.time()),
    }

    update = GolemBaseUpdate(
        entity_key=entity_key,
        data=json.dumps(updated_data).encode("utf-8"),
        btl=600,  # ~20 minutes (600 blocks at ~2 seconds each)
        string_annotations=[
            Annotation(key="type", value="message"),
            Annotation(key="id", value=entity_id),
            Annotation(key="status", value="updated"),
        ],
        numeric_annotations=[Annotation(key="version", value=2)],
    )

    update_receipts = await client.update_entities([update])
    print(f"Updated entity: {update_receipts[0].entity_key}")

    # Query updated entity
    updated_results = await client.query_entities(f'id = "{entity_id}" && version = 2')
    for result in updated_results:
        data = json.loads(result.storage_value.decode("utf-8"))
        print(f"  Updated entity: {data}")
        # Get entity key for deletion
        final_entity_key = result.entity_key

    # === DELETE Operations ===
    print("\n=== DELETE Operations ===")

    # Delete the entity
    delete_receipt = await client.delete_entities(
        [
            GolemBaseDelete(
                entity_key,  # Already a GenericBytes object
            )
        ]
    )
    print(f"Deleted entity: {delete_receipt[0]}")

    # Clean exit
    import sys

    await asyncio.sleep(2)  # Give time for events to be logged
    print("\nExample completed!")
    sys.exit(0)


if __name__ == "__main__":
    # Install requirements:
    # python3 -m venv venv
    # source venv/bin/activate
    # pip install golem-base-sdk==0.1.0 python-dotenv

    asyncio.run(main())
