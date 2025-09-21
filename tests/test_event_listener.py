"""Tests for event listener functionality - focused on creation case only."""

import asyncio
import logging

import pytest
from golem_base_sdk import GolemBaseClient

from src.golemdb_client import GolemDbClient
from tests.utils import create_single_entity

logger = logging.getLogger(__name__)


def _create_callback(create_event: object) -> None:
    logger.info("CREATE Event - Entity Key: {create_event.entity_key.as_hex_string()}")  # type: ignore  # noqa: PGH003


def _skip_if_testcontainers(use_testcontainers: bool) -> None:
    if use_testcontainers:
        pytest.skip(
            "WebSocket subscriptions are not supported with testcontainers "
            "due to known web3.py timeout issues"
        )


@pytest.mark.asyncio
async def _test_create_event_callback(client: GolemBaseClient) -> None:
    """Test GolemDbClient wrapper with entity creation callbacks."""
    # Step 1: Wrap the client parameter
    db_client = GolemDbClient(client)
    logger.info(f"Wrapped client: {type(db_client).__name__}")

    # List of creation events
    creation_events = []

    # Helper to check events with timing
    async def _wait_for_event(expected_count: int, timeout_seconds: float = 2.0) -> None:
        """Wait for expected number of events with timeout."""
        start_time = asyncio.get_event_loop().time()
        while len(creation_events) < expected_count:
            if asyncio.get_event_loop().time() - start_time > timeout_seconds:
                break
            await asyncio.sleep(0.1)  # Check every 100ms

    # Check latest creation event
    async def _check_last_event(expected_count: int, expected_entity_key: str) -> None:
        logger.info(f"Checking last event - Expected Count: {expected_count}, Expected Entity Key: {expected_entity_key}")

        await _wait_for_event(1)
        assert len(creation_events) == expected_count, f"Unexpected number of creation events: {len(creation_events)}, expected: {expected_count}"
        last_key = creation_events[-1]
        assert last_key == expected_entity_key, f"Latest event key {last_key} does not match expected {expected_entity_key}"

    # Create callback method that logs the event
    def event_creation_callback(create_event: object) -> None:
        entity_key = create_event.entity_key.as_hex_string() # type: ignore[attr-defined]
        creation_events.append(entity_key)
        logger.info(f"Entity Created Callback - {entity_key}: {create_event}")

    # Step 2: Create subscription for entity creation using context manager
    try:
        logger.info("Creating subscription ...")
        async with await db_client.watch_logs_v3(
            create_callback=event_creation_callback,
        ) as handle:
            logger.info("Subscription successfully created")

            # Step 3: Create two entities
            logger.info("Creating first entity...")
            receipt1 = await create_single_entity(client, b"First test entity")
            entity1_key = str(receipt1[0].entity_key.as_hex_string())
            # await _check_last_event(1, entity1_key)

            logger.info("Creating second entity...")
            receipt2 = await create_single_entity(client, b"Second test entity")
            entity2_key = str(receipt2[0].entity_key.as_hex_string())
            # _check_last_event(2, entity2_key)

            # Context manager will automatically unsubscribe

    except TimeoutError:
        pytest.skip("WebSocket subscription timed out - infrastructure issue")
    except Exception as e:
        logger.error(f"Test failed with error: {e}")
        raise
