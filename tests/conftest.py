"""Global test configuration and fixtures."""

import logging
from collections.abc import Generator

import anyio
import pytest
from eth_account import Account
from golem_base_sdk import GolemBaseClient

from utils import NETWORK_URLS

logger = logging.getLogger(__name__)

# test account key files
ACCOUNT_KEY_FILE = "./test1_private.key"
ACCOUNT_KEY_FILE2 = "./test2_private.key"

# localhost: when running script directly on local machine
# host.docker.internal: when running script inside a Docker container
# eg from a devcontainer setup
LOCALHOST = "host.docker.internal"


def pytest_addoption(parser) -> None:  # noqa: ANN001
    """Add custom command line options for pytest."""
    parser.addoption(
        "--network",
        action="store",
        default="local",
        choices=["local", "kaolin"],
        help="Network to use for tests (default: local)",
    )


@pytest.fixture(scope="session")
def network(request) -> str:  # noqa: ANN001
    """Get the network option from command line."""
    return request.config.getoption("--network")


@pytest.fixture(scope="session", autouse=True)
def setup_test_environment() -> Generator[None, None, None]:
    """Session level fixture to configure logging."""
    # Pytest handles logging configuration via --log-level, --log-cli-level, etc.
    # No need for custom logging setup here

    yield  # This is where all tests run

    # Teardown after all tests complete
    print("Tearing down test environment...")


@pytest.fixture(scope="session")
async def client(network: str) -> GolemBaseClient:
    """Fixture to provide a GolemBaseClient instance for tests."""
    return await get_client(network=network)


@pytest.fixture(scope="session")
async def client2(network: str) -> GolemBaseClient:
    """Fixture to provide a second GolemBaseClient instance for tests."""
    return await get_client(network=network, key_file=ACCOUNT_KEY_FILE2)


async def get_client(
    network: str = "local", key_file: str = ACCOUNT_KEY_FILE
) -> GolemBaseClient:
    """Create a GolemBaseClient instance."""
    private_key = await _get_private_key(key_file)
    account = Account.from_key(private_key)
    rpc_url = NETWORK_URLS[network]["rpc"]
    print(f"Connecting {account.address} at {rpc_url}")

    client = await GolemBaseClient.create(
        rpc_url=rpc_url,
        ws_url=NETWORK_URLS[network]["ws"],
        private_key=private_key,
    )

    # fetch eth balance of client account and abort if zero
    balance = await client.http_client().eth.get_balance(account.address)
    print(f"ETH balance for {account.address}: {balance / 10**18}")

    # abort tests if balance is zero
    if balance == 0:
        await client.disconnect()
        pytest.exit(f"Zero balance for {account.address}")

    return client


async def _get_private_key(key_file: str) -> bytes:
    async with await anyio.open_file(
        key_file,
        "rb",
    ) as f:
        return await f.read(32)
