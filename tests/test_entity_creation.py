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

from .utils import create_single_entity, get_entity_count, to_create_entity

logger = logging.getLogger(__name__)


@pytest.mark.asyncio
async def test_create_entity_receipt(client: GolemBaseClient) -> None:
    """Test creating an entity and verify there is a creation receipt."""
    logger.info("Testing entity creation receipt...")

    # Get entity count
    await get_entity_count(client, "before creation")

    # Create single entity
    create_receipt = await client.create_entities(
        [GolemBaseCreate(b"hello", 60, [Annotation("app", "test")], [])]
    )

    # check entity count after creation might be useless as a number of
    # entities may be deleted by houskeeping

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
    create_receipt = await create_single_entity(client, test_data)

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
    string_annotations = {
        "app": "metadata_test",
        "version": "1.0",
    }
    numeric_annotations = {
        "hasPayload": 1,
        "priority": 10,
        "size": 100,
    }
    a = {**string_annotations, **numeric_annotations}

    # Create entity with metadata annotations
    create_receipt = await create_single_entity(client, payload, annotations=a)

    entity_key = create_receipt[0].entity_key
    logger.info("Created entity with key: %s", entity_key)

    # Verify metadata
    metadata = await client.get_entity_metadata(entity_key)
    assert metadata is not None, "Metadata should not be None"
    assert isinstance(metadata, EntityMetadata), "Metadata should be a EntityMetadata"
    assert hasattr(metadata, "expires_at_block"), (
        "Metadata should have expires_at_block"
    )

    assert hasattr(metadata, "string_annotations"), (
        "Metadata should have string_annotations"
    )
    test_str_annotations = metadata.string_annotations
    # check that string annotations have correct type and values
    assert isinstance(test_str_annotations, list), "String annotations should be a list"
    assert all(isinstance(ann, Annotation) for ann in test_str_annotations), (
        "All string annotations should be Annotation instances"
    )
    assert len(test_str_annotations) == len(string_annotations.keys()), (
        "Number of string annotations should match the size of the original dictionary"
    )
    assert all(
        ann.value == string_annotations[ann.key] for ann in test_str_annotations
    ), "All string annotation values should should match the expected values"

    # check that numeric annotations have correct type and values
    assert hasattr(metadata, "numeric_annotations"), (
        "Metadata should have numeric_annotations"
    )
    test_num_annotations = metadata.numeric_annotations
    assert isinstance(test_num_annotations, list), (
        "Numeric annotations should be a list"
    )
    assert len(test_num_annotations) == len(numeric_annotations.keys()), (
        "Number of numeric annotations should match the size of the original dictionary"
    )
    assert all(isinstance(ann, Annotation) for ann in test_num_annotations), (
        "All numeric annotations should be Annotation instances"
    )
    assert all(
        ann.value == numeric_annotations[ann.key] for ann in test_num_annotations
    ), "All numeric annotation values should should match the expected values"

    logger.info("Entity metadata: %s", metadata)

    logger.info("Metadata verified: %s", metadata)


@pytest.mark.asyncio
async def test_create_multiple_entities(client: GolemBaseClient) -> None:
    """Test creating multiple entities in a single call."""
    logger.info("Testing multiple entity creation...")

    # Create multiple entities
    create_receipts = await client.create_entities(
        [
            to_create_entity(b"entity1", 60, {"app": "batch_test"}),
            to_create_entity(b"entity2", 60, {"app": "batch_test"}),
            to_create_entity(b"entity3", 60, {"app": "batch_test"}),
        ]
    )

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


def _to_annotations(a: dict[str, str]) -> list[Annotation[str]]:
    annotations = []
    for key, value in a.items():
        annotations.append(Annotation(key, value))
    return annotations


def _to_numeric_annotations(a: dict[str, int]) -> list[Annotation[int]]:
    annotations = []
    for key, value in a.items():
        annotations.append(Annotation(key, value))
    return annotations
