"""Tests for GolemBaseClient connection and basic functionality."""

import logging

import pytest
from golem_base_sdk import GolemBaseClient

logger = logging.getLogger(__name__)


@pytest.mark.asyncio
async def test_client_instance(client: GolemBaseClient) -> None:
    """Test that the client fixture provides a valid GolemBaseClient instance."""
    assert client is not None, "Client fixture should not be None"
    assert isinstance(client, GolemBaseClient), (
        "Client fixture should be an instance of GolemBaseClient"
    )


@pytest.mark.asyncio
async def test_client_http(client: GolemBaseClient) -> None:
    """Test that the client fixture provides a valid GolemBaseClient instance."""
    http_client = client.http_client()
    assert http_client, "HTTP client should not be None"

    assert hasattr(http_client, "provider"), (
        "HTTP client should have an 'provider' attribute"
    )
    assert hasattr(http_client.provider, "endpoint_uri"), (
        "HTTP client should have an 'endpoint_uri' attribute"
    )

    endpoint_uri = http_client.provider.endpoint_uri
    assert endpoint_uri, "Endpoint URI should not be None"
    assert isinstance(endpoint_uri, str), "Endpoint URI should be a string"
    logger.info("Client connection URI: %s", endpoint_uri)

    assert endpoint_uri.startswith(("http://", "https://")), (
        "Endpoint URI should start with 'http'"
    )


@pytest.mark.asyncio
async def test_client_connection(client: GolemBaseClient) -> None:
    """Test that the client can establish a connection to the Golem Base network."""
    logger.debug("Testing client connection...")
    is_connected = await client.is_connected()
    logger.info("Client connection status: %s", is_connected)
    assert isinstance(is_connected, bool), "Connection status should be a boolean"
    assert is_connected, "Client should be connected to the Golem Base network"


@pytest.mark.asyncio
async def test_client_contract_address(client: GolemBaseClient) -> None:
    """Test that the client has access to the GolemBase contract."""
    contract_address = client.golem_base_contract.address
    logger.info("Contract address: %s", contract_address)
    assert contract_address is not None
    assert isinstance(contract_address, str)


@pytest.mark.asyncio
async def test_client_http_client(client: GolemBaseClient) -> None:
    """Test that the client provides access to the HTTP client."""
    # Test accessing the HTTP client
    http_client = client.http_client()
    assert http_client is not None
