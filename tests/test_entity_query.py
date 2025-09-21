"""Tests for GolemBase entity query functionality."""

import logging
from collections.abc import Sequence

import pytest
from golem_base_sdk import (
    CreateEntityReturnType,
    GolemBaseClient,
    QueryEntitiesResult,
)

from .utils import create_single_entity, generate_uuid, to_create_entity

AND = "&&"
OR = "||"

logger = logging.getLogger(__name__)


@pytest.mark.asyncio
async def test_entity_query_single(client: GolemBaseClient) -> None:
    """Create and query a single entity."""
    uuid = generate_uuid()
    payload = b"test_" + uuid.encode()

    create_entity = await create_single_entity(
        client, payload, annotations={"id": uuid}
    )
    entity_key = create_entity[0].entity_key.as_hex_string()
    logger.info(f"Created entity {create_entity}")  # noqa: G004

    query = f'id = "{uuid}"'
    logger.info(f"Using query: '{query}'")  # noqa: G004
    query_result = await client.query_entities(query)
    logger.info("Query result: %s", query_result)

    assert query_result is not None, "Query result should not be None"
    assert len(query_result) == 1, "Query should return exactly one entity"
    assert query_result[0].entity_key == entity_key, (
        "Query result should match the created entity key"
    )

    logger.info("Unique entity query test passed successfully.")


@pytest.mark.asyncio
async def test_entity_query_batch(client: GolemBaseClient) -> None:
    """Create multiple entities and query them."""
    # Create multiple entities
    batch_id = generate_uuid()
    create_receipts = await _create_entries(client, batch_id)
    assert create_receipts is not None, "Create receipts should not be None"
    assert len(create_receipts) == 4, "Should have created exactly 4 entities"
    entity_keys = [receipt.entity_key.as_hex_string() for receipt in create_receipts]
    logger.info(f"Created entities with keys: {entity_keys}")  # noqa: G004

    # Query by batch ID
    query = f'id = "{batch_id}"'
    logger.info(f"Using query: '{query}'")  # noqa: G004
    query_result = await client.query_entities(query)
    assert query_result is not None, "Query result should not be None"
    assert len(query_result) == 4, "Query should return exactly 4 entities"
    result_keys = [entity.entity_key for entity in query_result]
    logger.info(f"Fetched results with keys: {result_keys}")  # noqa: G004

    # Verify all created entities are in the query result
    for key in entity_keys:
        assert key in result_keys, (
            f"Entity key {key.as_hex_string()} should be in the query result"
        )

    # Check that querying with a non-existent batch ID returns no results
    fake_batch_id = generate_uuid()
    fake_query = f'id = "{fake_batch_id}"'
    logger.info(f"Using fake query: '{fake_query}'")  # noqa: G004
    fake_query_result = await client.query_entities(fake_query)
    assert fake_query_result is not None, "Fake query result should not be None"
    assert len(fake_query_result) == 0, "Fake query should return no entities"

    logger.info("Multiple entity query test passed successfully.")


@pytest.mark.asyncio
async def test_entity_query_with_operator_and_fixme(client: GolemBaseClient) -> None:
    """Modified test_entity_query_and_operator that always fails."""
    # Create first batch
    data_1 = b"1"
    data_2 = b"2"
    batch_id = generate_uuid()
    create_receipts = await client.create_entities(
        [
            to_create_entity(data_1, 60, {"id": batch_id, "color": "red", "size": 10}),
            to_create_entity(
                data_2, 60, {"id": batch_id, "color": "green", "size": 10}
            ),
        ]
    )
    entity_keys = [receipt.entity_key.as_hex_string() for receipt in create_receipts]
    logger.info(f"Created entities with keys: {entity_keys}")  # noqa: G004

    # Create second batch with different ID
    other_id = generate_uuid()
    assert batch_id != other_id, "Batch ID should be unique"
    other_receipts = await client.create_entities(
        [
            to_create_entity(data_1, 60, {"id": other_id, "color": "red", "size": 10}),
            to_create_entity(
                data_2, 60, {"id": other_id, "color": "green", "size": 10}
            ),
        ]
    )
    other_keys = [receipt.entity_key.as_hex_string() for receipt in other_receipts]
    logger.info(f"Created other entities with keys: {other_keys}")  # noqa: G004

    # Query with two 'and' operators (1 result expected)
    query = f'id = "{batch_id}" {AND} color = "red" {AND} size = 10'
    logger.info(f"Query: '{query}'")  # noqa: G004
    query_result = await client.query_entities(query)
    logger.info(f"Result: '{query_result}'")  # noqa: G004
    _check_result("A", query_result, entity_keys, [data_1])  # type: ignore  # noqa: PGH003


@pytest.mark.asyncio
async def test_entity_query_with_operator_and(client: GolemBaseClient) -> None:
    """Create multiple entities and query them with an AND operator."""
    # Create multiple entities
    batch_id = generate_uuid()
    create_receipts = await _create_entries(client, batch_id)
    entity_keys = [receipt.entity_key.as_hex_string() for receipt in create_receipts]

    # Query by batch ID and color = green (1 results expected)
    batch_id_clause = f'id = "{batch_id}"'
    green_clause = 'color = "green"'
    query = f"{batch_id_clause} {AND} {green_clause}"
    logger.info(f"Using query: '{query}'")  # noqa: G004

    query_result = await client.query_entities(query)
    logger.info(f"Query result: '{query_result}'")  # noqa: G004
    _check_result("A", query_result, entity_keys, [b"4"])  # type: ignore  # noqa: PGH003

    # Query by batch ID and color = red (2 results expected)
    batch_id_clause = f'id = "{batch_id}"'
    red_clause = 'color = "red"'
    query = f"{batch_id_clause} {AND} {red_clause}"
    logger.info(f"Using single and query (2 results): '{query}'")  # noqa: G004

    query_result = await client.query_entities(query)
    logger.info(f"Query result: '{query_result}'")  # noqa: G004
    _check_result("B", query_result, entity_keys, [b"1", b"3"])  # type: ignore  # noqa: PGH003

    # Add size clause to the query (1 result expected)
    size_clause = "size = 10"
    query = f"{batch_id_clause} {AND} {red_clause} {AND} {size_clause}"
    logger.info(f"Using double and query (1 result): '{query}'")  # noqa: G004
    query_result = await client.query_entities(query)
    logger.info(f"Query result: '{query_result}'")  # noqa: G004
    _check_result("C", query_result, entity_keys, [b"1"])  # type: ignore  # noqa: PGH003

    # Add second color clause to the query (0 results expected)
    blue_clause = 'color = "blue"'
    query = f"{batch_id_clause} {AND} {red_clause} {AND} {blue_clause}"
    logger.info(f"Using double and query (0 results): '{query}'")  # noqa: G004

    query_result = await client.query_entities(query)
    logger.info(f"Query result: '{query_result}'")  # noqa: G004
    _check_result("D", query_result, entity_keys, [])  # type: ignore  # noqa: PGH003

    logger.info("Multiple entity query with AND operator test passed successfully.")


@pytest.mark.asyncio
async def test_entity_query_with_operator_or(client: GolemBaseClient) -> None:
    """Create multiple entities and query them with an OR operator."""
    # Create multiple entities
    batch_id = generate_uuid()
    create_receipts = await _create_entries(client, batch_id)
    entity_keys = [receipt.entity_key.as_hex_string() for receipt in create_receipts]

    # Query by batch ID and color = green (2 results expected)
    batch_id_clause = f'id = "{batch_id}"'
    green_clause = 'color = "green"'
    blue_clause = 'color = "blue"'
    query = f"{batch_id_clause} {AND} ({green_clause} {OR} {blue_clause})"
    logger.info(f"Using and/or query: '{query}'")  # noqa: G004

    query_result = await client.query_entities(query)
    logger.info(f"Query result: '{query_result}'")  # noqa: G004
    _check_result("A", query_result, entity_keys, [b"2", b"4"])  # type: ignore  # noqa: PGH003


def _check_result(
    label: str,
    query_result: Sequence[QueryEntitiesResult],
    entity_keys: list[str],
    expected_values: list[bytes],
) -> None:
    """Check that the query result matches the expected keys."""
    # Verify that the query result is not None and has the expected length
    assert query_result is not None, f"{label}: Query result should not be None"
    assert len(query_result) == len(expected_values), (
        f"{label}: Query should return exactly {len(expected_values)} entities, but got {query_result}"  # noqa: E501
    )

    # Verify that all result keys are in the expected entity keys
    result_keys = [entity.entity_key for entity in query_result]
    for key in result_keys:
        assert key in entity_keys, (
            f"{label}: Entity key {key} should be in the expected keys"
        )

    # Verify that the result entity values match the expected values
    values = [entity.storage_value for entity in query_result]
    while len(values) > 0:
        value = values.pop(0)
        assert value in expected_values, (
            f"{label}: Query result has unexpected value: {value}, expected: {expected_values}"  # noqa: E501
        )
        logger.info(f"{label}: Value {value} found in expected values")  # noqa: G004


async def _create_entries(
    client: GolemBaseClient, batch_id: str
) -> Sequence[CreateEntityReturnType]:
    return await client.create_entities(
        [
            to_create_entity(b"1", 60, {"id": batch_id, "color": "red", "size": 10}),
            to_create_entity(b"2", 60, {"id": batch_id, "color": "blue", "size": 12}),
            to_create_entity(b"3", 60, {"id": batch_id, "color": "red", "size": 12}),
            to_create_entity(b"4", 60, {"id": batch_id, "color": "green", "size": 10}),
        ]
    )
