"""Tests for GolemBaseClient connection and basic functionality."""

import logging
from typing import TYPE_CHECKING, Final

import pytest
from eth_typing import HexStr
from golem_base_sdk import Address, GenericBytes, GolemBaseClient
from web3 import AsyncWeb3

if TYPE_CHECKING:
    from web3.types import LogsSubscriptionArg

STORAGE_ADDRESS: Final[Address] = Address(
    GenericBytes.from_hex_string("0x0000000000000000000000000000000060138453")
)


logger = logging.getLogger(__name__)


@pytest.mark.asyncio
async def test_subscribe_to_create_event(client: GolemBaseClient) -> None:
    """Test that the client fixture provides a valid GolemBaseClient instance."""
    ws_client = client.ws_client()
    assert ws_client, "WebSocket client should not be None"
    assert isinstance(ws_client, AsyncWeb3), (
        "WebSocket client should be an instance of AsyncWeb3"
    )
    assert await ws_client.is_connected(), "WebSocket client should be connected"

    async with ws_client as w3:
        create_event_topic = w3.keccak(
            text="GolemBaseStorageEntityCreated(uint256,uint256)"
        )
        filter_params: LogsSubscriptionArg = {
            "address": STORAGE_ADDRESS.as_address(),
            "topics": [HexStr(create_event_topic.to_0x_hex())],
        }

        logger.info("Creating create subscription: %s", filter_params)
        subscription_id = await w3.eth.subscribe("logs", subscription_arg=filter_params)
        logger.info("Subscription %s successfully created.", subscription_id)
        assert subscription_id, "Subscription ID should not be None"
