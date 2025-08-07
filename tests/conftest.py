"""Global test configuration and fixtures."""

import logging
from collections.abc import Generator

import anyio
import pytest
from golem_base_sdk import GolemBaseClient

# test account key file
# TODO move to wallet file (needs updated golem base cli client)
ACCOUNT_KEY_FILE = "./private.key"

# define log level for tests
LOG_LEVEL = logging.DEBUG

# golem base instonce to use for tests
INSTANCE = "local"

# localhost: when running script directly on local machine
# host.docker.internal: when running script inside a Docker container
# eg from a devcontainer setup
LOCALHOST = "host.docker.internal"

# actual urls for different instances
INSTANCE_URLS = {
    "demo": {
        "rpc": "https://api.golembase.demo.golem-base.io",
    },
    "local": {
        "rpc": f"http://{LOCALHOST}:8545",
        "ws": f"ws://{LOCALHOST}:8545",
    },
    "kaolin": {
        "rpc": "https://rpc.kaolin.holesky.golem-base.io",
        "ws": "wss://ws.rpc.kaolin.holesky.golem-base.io",
    },
}


@pytest.fixture(scope="session", autouse=True)
def setup_test_environment() -> Generator[None, None, None]:
    """Session level fixture to configure logging."""
    # Configure logging for tests
    logging.basicConfig(
        level=LOG_LEVEL,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    yield  # This is where all tests run

    # Teardown after all tests complete
    print("Tearing down test environment...")


@pytest.fixture(scope="session")
async def client() -> GolemBaseClient:
    """Fixture to provide a GolemBaseClient instance for tests."""
    private_key = await _get_private_key()
    return await _get_client(private_key)


async def _get_private_key() -> bytes:
    async with await anyio.open_file(
        ACCOUNT_KEY_FILE,
        "rb",
    ) as f:
        return await f.read(32)


async def _get_client(private_key: bytes) -> GolemBaseClient:
    """Create a GolemBaseClient instance."""
    return await GolemBaseClient.create(
        rpc_url=INSTANCE_URLS[INSTANCE]["rpc"],
        ws_url=INSTANCE_URLS[INSTANCE]["ws"],
        private_key=private_key,
    )
