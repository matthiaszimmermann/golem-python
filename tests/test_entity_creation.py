"""Tests for GolemBase entity creation functionality."""

import logging

import pytest
from golem_base_sdk import (
    Annotation,
    CreateEntityReturnType,
    EntityMetadata,
    GenericBytes,
    GolemBaseClient,
    GolemBaseCreate,
    GolemBaseDelete,
)

logger = logging.getLogger(__name__)


@pytest.mark.asyncio
async def test_create_entity_receipt(client: GolemBaseClient) -> None:
    """Test creating an entity and verify there is a creation receipt."""
    logger.info("Testing entity creation receipt...")

    # Get initial entity count
    entities_before = await client.get_entity_count()
    assert entities_before is not None, "Entities count should not be None"
    assert isinstance(entities_before, int), "Entities count should be int"
    assert entities_before >= 0, "Entities count should be non-negative"
    logger.info(f"Entities count before creation: {entities_before}")  # noqa: G004

    # Create single entity
    # for GolemBaseCreate see https://github.com/Golem-Base/python-sdk/blob/main/golem_base_sdk/types.py
    create_receipt = await client.create_entities(
        [
            GolemBaseCreate(
                b"hello",  # data: bytes (payload to store)
                60,  # ttl: int (time to live in blocks)
                [
                    Annotation("app", "demo")
                ],  # string_annotations: Sequence[Annotation[str]]
                [],
            )  # numeric_annotations: Sequence[Annotation[int]
        ]
    )

    # Get entity count after creation of a new entity
    entities_after = await client.get_entity_count()
    assert entities_after == entities_before + 1, (
        "Entities count should increase by 1 after creation"
    )
    logger.info(f"Entities count after creation: {entities_after}")  # noqa: G004

    # Verify receipt exists and has expected structure
    assert create_receipt is not None, "Creation receipt should not be None"
    assert len(create_receipt) == 1, "Should have exactly one receipt for one entity"

    receipt = create_receipt[0]
    assert receipt is not None, "Receipt should not be None"
    assert isinstance(receipt, CreateEntityReturnType), (
        "Receipt should be an instance of GolemBaseCreate"
    )
    assert hasattr(receipt, "entity_key"), "Receipt should have entity_key attribute"
    assert receipt.entity_key is not None, "Entity key should not be None"
    assert isinstance(receipt.entity_key, GenericBytes), (
        "Entity key should be a GenericBytes"
    )

    logger.info(f"Creation receipt: {receipt}")  # noqa: G004
    logger.info(f"Entity created with key: {receipt.entity_key.as_hex_string()}")  # noqa: G004


@pytest.mark.asyncio
async def test_create_entity_storage_value(client: GolemBaseClient) -> None:
    """Test creating an entity and verify the storage value."""
    logger.info("Testing entity creation and storage value...")

    test_data = b"test_storage_data"

    # Create entity with specific test data
    create_receipt = await client.create_entities(
        [GolemBaseCreate(test_data, 60, [], [])]
    )

    entity_key = create_receipt[0].entity_key
    logger.info(f"Created entity with key: {entity_key.as_hex_string()}")  # noqa: G004

    # Verify storage value
    storage_value = await client.get_storage_value(entity_key)
    assert storage_value is not None, "Storage value should not be None"
    assert isinstance(storage_value, bytes), "Storage value should be bytes"
    assert storage_value == test_data, (
        f"Storage value should match: expected {test_data}, got {storage_value}"
    )

    logger.info(f"Storage value verified: {storage_value}")  # noqa: G004


@pytest.mark.asyncio
async def test_create_entity_metadata(client: GolemBaseClient) -> None:
    """Test creating an entity and verify the metadata."""
    logger.info("Testing entity creation and metadata...")

    payload = b"test_metadata_data"
    string_annotations = [
        Annotation("app", "metadata_test"),
        Annotation("version", "1.0"),
    ]
    numeric_annotations = [
        Annotation("hasPayload", 1),
        Annotation("priority", 10),
        Annotation("size", 100),
    ]

    # Create entity with metadata annotations
    create_receipt = await client.create_entities(
        [GolemBaseCreate(payload, 60, string_annotations, numeric_annotations)]
    )

    entity_key = create_receipt[0].entity_key
    logger.info("Created entity with key: %s", entity_key)

    # Verify metadata
    metadata = await client.get_entity_metadata(entity_key)
    assert metadata is not None, "Metadata should not be None"
    assert isinstance(metadata, EntityMetadata), "Metadata should be a EntityMetadata"
    assert hasattr(metadata, "expires_at_block"), (
        "Metadata should have expires_at_block"
    )
    assert hasattr(metadata, "string_annotations") or hasattr(
        metadata, "numeric_annotations"
    ), "Metadata should have string_annotations or numeric_annotations"

    logger.info("Metadata verified: %s", metadata)


@pytest.mark.asyncio
async def test_create_multiple_entities(client: GolemBaseClient) -> None:
    """Test creating multiple entities in a single call."""
    logger.info("Testing multiple entity creation...")

    # Create multiple entities
    entities_to_create = [
        GolemBaseCreate(b"entity1", 60, [Annotation("app", "batch_test")], []),
        GolemBaseCreate(b"entity2", 60, [Annotation("app", "batch_test")], []),
        GolemBaseCreate(b"entity3", 60, [Annotation("app", "batch_test")], []),
    ]

    create_receipts = await client.create_entities(entities_to_create)

    # Verify all entities were created
    assert create_receipts is not None, "Creation receipts should not be None"
    assert len(create_receipts) == 3, "Should have three receipts for three entities"

    entity_keys = [receipt.entity_key for receipt in create_receipts]

    # Verify all entity keys are unique
    assert len(set(entity_keys)) == 3, "All entity keys should be unique"

    logger.info("Created %d entities with keys: %s", len(entity_keys), entity_keys)

    # Verify each entity exists and has correct storage value
    for i, entity_key in enumerate(entity_keys):
        storage_value = await client.get_storage_value(entity_key)
        expected_value = f"entity{i + 1}".encode()
        assert storage_value == expected_value, (
            f"Storage value mismatch for entity {i + 1}"
        )

    # Clean up - delete all entities
    delete_objects = [GolemBaseDelete(key) for key in entity_keys]
    await client.delete_entities(delete_objects)
