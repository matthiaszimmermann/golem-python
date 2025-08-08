"""Tests for GolemBase entity deletion functionality."""

import logging

import pytest
from golem_base_sdk import (
    EntityKey,
    GenericBytes,
    GolemBaseClient,
    GolemBaseDelete,
)
from web3.exceptions import Web3RPCError

from .utils import create_single_entity, get_entity_count, to_create_entity

logger = logging.getLogger(__name__)


@pytest.mark.asyncio
async def test_delete_entity(client: GolemBaseClient) -> None:
    """Test creating and then deleting an entity."""
    logger.info("Testing entity deletion...")

    test_data = b"entity_to_delete"

    # Create entity
    create_receipt = await create_single_entity(
        client, test_data, btl=60, annotations={"app": "delete_test"}
    )

    entity_key = create_receipt[0].entity_key
    logger.info(f"Created entity with key: {entity_key.as_hex_string()}")  # noqa: G004

    entities_before = await get_entity_count(client, "before deletion")

    # Delete the entity
    delete_receipt = await client.delete_entities([GolemBaseDelete(entity_key)])
    assert delete_receipt is not None, "Delete receipt should not be None"
    logger.info(f"Delete receipt: {delete_receipt}")  # noqa: G004

    # Verify entity count decreased back to original
    entities_after_delete = await get_entity_count(client, "after deletion")
    assert entities_after_delete < entities_before, (
        "Entity count should decrease after deletion"
    )

    # Verify entity no longer exists
    deleted_value = await client.get_storage_value(entity_key)
    assert deleted_value == b"", (
        f"Storage value should be b'' after entity deletion but is {deleted_value}"
    )
    logger.info("Storage value for deleted entity checked")

    # Verify entity metadata is no longer accessible
    with pytest.raises(Web3RPCError) as exc_info:
        await client.get_entity_metadata(entity_key)
    logger.info(
        f"Expected exception when accessing deleted entity metadata: {exc_info.value}"  # noqa: G004
    )

    logger.info("Entity deletion test completed successfully")


@pytest.mark.asyncio
async def test_delete_nonexistent_entity(client: GolemBaseClient) -> None:
    """Test attempting to delete a non-existent entity."""
    logger.info("Testing deletion of non-existent entity...")

    # Create a fake entity key (this should not exist)
    fake_entity_key = EntityKey(
        GenericBytes(
            bytes.fromhex(
                "0000000000d2b1b41ceb6fad6e2c93849b488fb9bad0446ee8bee1278a9c89c7"
            )
        )
    )

    # Attempt to delete non-existent entity
    with pytest.raises(Web3RPCError) as exc_info:
        await client.delete_entities([GolemBaseDelete(fake_entity_key)])
    logger.info(
        f"Expected exception when deleting non-existent entity: {exc_info.value}"  # noqa: G004
    )

    logger.info("Non-existent entity deletion test completed successfully")


@pytest.mark.asyncio
async def test_delete_multiple_entities(client: GolemBaseClient) -> None:
    """Test creating and deleting multiple entities in batch."""
    logger.info("Testing multiple entity deletion...")

    # Create multiple entities
    create_receipts = await client.create_entities(
        [
            to_create_entity(b"delete_entity1", 60, {"app": "delete_batch"}),
            to_create_entity(b"delete_entity2", 60, {"app": "delete_batch"}),
            to_create_entity(b"delete_entity3", 60, {"app": "delete_batch"}),
        ]
    )
    entity_keys = [receipt.entity_key for receipt in create_receipts]

    # Get entity count
    entities_before = await get_entity_count(client, "before deletion")

    # Verify all entities exist
    for i, entity_key in enumerate(entity_keys):
        storage_value = await client.get_storage_value(entity_key)
        expected_value = f"delete_entity{i + 1}".encode()
        assert storage_value == expected_value, (
            f"Storage value mismatch for entity {i + 1}"
        )

    # Delete all entities in batch
    delete_objects = [GolemBaseDelete(key) for key in entity_keys]
    delete_receipts = await client.delete_entities(delete_objects)
    assert delete_receipts is not None, "Delete receipts should not be None"
    logger.info(f"Delete receipts: {delete_receipts}")  # noqa: G004

    # Verify entity count decreased in a meaningful way
    entities_after_delete = await get_entity_count(client, "after deletion")
    assert entities_after_delete <= entities_before - len(entity_keys), (
        f"Entity count should decrease after deletion by at least {len(entity_keys)}"
    )

    # Verify all entities no longer exist
    for entity_key in entity_keys:
        deleted_storage_value = await client.get_storage_value(entity_key)
        assert deleted_storage_value == b"", (
            f"Storage value should be b'' after deletion for key {entity_key}"
        )

    logger.info("Multiple entity deletion test completed successfully")
