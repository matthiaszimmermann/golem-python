"""Tests for GolemBase entity creation functionality."""

import logging

import pytest
from golem_base_sdk import EntityKey, GolemBaseClient, GolemBaseDelete
from web3.exceptions import Web3RPCError

from utils import get_address, get_annotations

from .utils import create_single_entity, to_update_entity

logger = logging.getLogger(__name__)


@pytest.mark.asyncio
async def test_update_entity_by_owner(client: GolemBaseClient) -> None:
    """Test updating an entity by its owner."""
    logger.info("Testing entity creation receipt...")

    entity_key = await _create_and_test_entity(client, b"owner_test", {"my_value": "a"})

    await _update_and_test_entity(
        client, entity_key, b"owner_test_updated", {"my_value": "a_updated"}
    )


@pytest.mark.asyncio
async def test_update_entity_by_non_owner(
    client: GolemBaseClient, client2: GolemBaseClient
) -> None:
    """Test updating an entity by non-owner fails with appropriate error."""
    entity_key = await _create_and_test_entity(client, b"owner_test", {"my_value": "a"})

    # This should fail because client2 is not the owner
    with pytest.raises(Web3RPCError, match="is not the owner") as exc_info:
        await _update_and_test_entity(
            client2, entity_key, b"owner_test_updated", {"my_value": "a_updated"}
        )

    logger.info(f"Expected exception: {exc_info.value}")
    logger.info("Entity update by non-owner correctly failed: %s", exc_info.value)


@pytest.mark.asyncio
async def test_delete_entity_by_non_owner(
    client: GolemBaseClient, client2: GolemBaseClient
) -> None:
    """Test deleting an entity by non-owner fails with appropriate error."""
    entity_key = await _create_and_test_entity(client, b"owner_test", {"my_value": "a"})

    # This should fail because client2 is not the owner
    with pytest.raises(Web3RPCError, match="is not the owner"):
        await client2.delete_entities([GolemBaseDelete(entity_key)])

    logger.info("Entity delete by non-owner correctly failed")


async def _create_and_test_entity(
    client: GolemBaseClient, payload: bytes, annotations: dict
) -> EntityKey:
    # Get owner
    owner = client.get_account_address()

    # Create entity with specific test data
    create_receipt = await create_single_entity(
        client, payload, annotations=annotations
    )
    entity_key = create_receipt[0].entity_key

    # Verify entity owner
    metadata = await client.get_entity_metadata(entity_key)
    assert get_address(metadata.owner) == get_address(owner), (
        f"Metadata owner should match creator. "
        f"Expected {get_address(owner)}, got {get_address(metadata.owner)}"
    )

    # Verify annotations
    annotations = get_annotations(metadata)
    assert annotations == {"my_value": "a"}, (
        f"Entity annotations should match. "
        f"Expected {{'my_value': 'a'}}, got {annotations}"
    )

    logger.info("Entity update by owner verified")
    return entity_key


async def _update_and_test_entity(
    client: GolemBaseClient, entity_key: EntityKey, payload: bytes, annotations: dict
) -> None:
    # Update entity with new data
    update_entity = to_update_entity(entity_key, payload, annotations=annotations)
    update_receipt = await client.update_entities([update_entity])
    logger.info(f"Update receipt: {update_receipt}")  # noqa: G004

    # Verify entity owner
    owner = client.get_account_address()
    metadata = await client.get_entity_metadata(entity_key)
    assert get_address(metadata.owner) == get_address(owner), (
        f"Metadata owner should match creator/updator. "
        f"Expected {get_address(owner)}, got {get_address(metadata.owner)}"
    )

    # Verify annotations
    annotations_to_verify = get_annotations(metadata)
    assert annotations_to_verify == annotations, (
        f"Entity annotations should match. "
        f"Expected {annotations}, got {annotations_to_verify}"
    )

    logger.info("Entity update by owner verified")
