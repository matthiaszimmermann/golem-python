"""Tests for event listener functionality - focused on creation case only."""

import logging

import pytest
from golem_base_sdk import GolemBaseClient

from tests.utils import create_single_entity

logger = logging.getLogger(__name__)


@pytest.mark.asyncio
async def test_create_event_callback(
    client: GolemBaseClient,  # , client2: GolemBaseClient
    use_testcontainers: bool,
) -> None:
    """Test creation event callback - simple focused test."""
    _skip_if_testcontainers(use_testcontainers)
    logger.info("Testing create event callback...")

    # Track if callback was called using a list to capture events
    captured_events = []

    # callback function for create events
    def create_callback(create_event: object) -> None:
        captured_events.append(create_event)
        logger.info(
            "CREATE Event - Entity Key: {create_event.entity_key.as_hex_string()}"
        )  # type: ignore  # noqa: PGH003

    # Wait for max_wait seconds to capture events
    # async def capture_events(max_wait: int = 15, wait_interval: float = 0.5) -> None:
    #    waited = 0

    #    while len(captured_events) == 0 and waited < max_wait:
    #        await asyncio.sleep(wait_interval)
    #        waited += wait_interval
    #        if waited % 2 == 0:  # Log every 2 seconds
    #            logger.info("Waiting for events... (%s/%s seconds)", waited, max_wait)

    #    # 4. Check that callback for creation event was caught
    #    if len(captured_events) == 0:
    #        logger.warning("No events captured after %s seconds", max_wait)
    #        pytest.skip("No events captured - may be timing-related")

    #    logger.info("Captured %s events total", len(captured_events))

    # 1. Connect client (already done via fixtures)
    # assert await client.is_connected(), "Main client should be connected"
    # logger.info("Client connected, proceeding with event subscription...")

    # 2. Create subscription with better error handling
    logger.info("Subscribing to create events...")
    try:
        await client.watch_logs(
            label="test_create_notifications",
            create_callback=create_callback,
        )
        logger.info("Successfully subscribed for create events: %s", watch_handle)
    except TimeoutError:
        pytest.skip("WebSocket subscription timed out - likely infrastructure issue")

    # 3. Create entity using regular client
    create_receipt = await create_single_entity(client, b"test_create_event")
    logger.info("Create receipt: %s", create_receipt)

    entity_key = create_receipt[0].entity_key
    logger.info("Created entity with key: %s", entity_key.as_hex_string())

    # 4. Wait for event to be processed with timeout
    # await capture_events()

    # Check for our specific event
    matching_events = [
        event for event in captured_events if event.entity_key == entity_key
    ]

    assert len(matching_events) == 1, (
        f"Expected exactly one matching event, but found {matching_events}"
    )

    logger.info(f"Successfully captured CREATE event: {matching_events}")  # noqa: G004

    # Clean up
    try:
        await watch_handle.unsubscribe()
    except (ConnectionError, TimeoutError) as e:
        logger.warning("Error during cleanup: %s", e)

    logger.info("Create event callback test passed")


def _skip_if_testcontainers(use_testcontainers: bool) -> None:
    if use_testcontainers:
        pytest.skip(
            "WebSocket subscriptions are not supported with testcontainers "
            "due to known web3.py timeout issues"
        )
