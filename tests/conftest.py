"""Global test configuration and fixtures."""

import asyncio
import logging
import os
from collections.abc import Generator
from pathlib import Path

import pytest
import websockets
from dotenv import load_dotenv
from eth_account import Account
from eth_account.signers.local import LocalAccount
from golem_base_sdk import GolemBaseClient
from testcontainers.core.container import DockerContainer
from testcontainers.core.wait_strategies import HttpWaitStrategy
from testcontainers.core.waiting_utils import wait_container_is_ready

logger = logging.getLogger(__name__)

DOT_ENV_FILE = ".env"

NODE_IMAGE = "golemnetwork/golembase-op-geth:latest"
NODE_PORT_HTTP = 8545
NODE_PORT_WS = 8546

# Environment variable names for external wallet configuration
WALLET_FILE_ENV_PREFIX = "WALLET_FILE"
WALLET_PASSWORD_ENV_PREFIX = "WALLET_PASSWORD"  # noqa: S105

# Environment variable names for external node configuration
RPC_URL_ENV = "RPC_URL"
WS_URL_ENV = "WS_URL"

# Load environment variables from .env file if it exists.
env_file = Path(DOT_ENV_FILE)
if env_file.exists():
    logger.info("Loading environment variables from .env file")
    load_dotenv(env_file)
else:
    logger.info("Using system environment variables only (no .env file found)")


@pytest.fixture(scope="session")
def use_testcontainers() -> bool:
    """Return true if GolemDB node is served by test testcontainer."""
    # Check if external node configuration is provided
    rpc_url = os.getenv(RPC_URL_ENV)
    ws_url = os.getenv(WS_URL_ENV)

    # Return False if external node is configured, True if using testcontainers
    return not (rpc_url and ws_url)


@pytest.fixture(scope="session")
def golemdb_node() -> Generator[tuple[DockerContainer | None, str, str], None, None]:
    """Fixture to provide GolemDB node connection details."""
    external_config = _get_external_node_config()

    if external_config:
        rpc_http, rpc_ws = external_config
        yield None, rpc_http, rpc_ws
        logger.info("External GolemDB node session completed")
    else:
        yield from _create_testcontainer_node()


@pytest.fixture(scope="session")
def client_account(
    golemdb_node: tuple[DockerContainer | None, str, int, int],
) -> LocalAccount:
    """Fixture to get client_account from env vars or create using GolemDB node."""
    return _get_or_create_account(1, golemdb_node[0])


@pytest.fixture(scope="session")
def client_account2(
    golemdb_node: tuple[DockerContainer | None, str, int, int],
) -> LocalAccount:
    """Fixture to get client_account2 from env vars or create using GolemDB node."""
    return _get_or_create_account(2, golemdb_node[0])


@pytest.fixture(scope="session")
async def client(
    golemdb_node: tuple[DockerContainer | None, str, str],
    client_account: LocalAccount,
) -> GolemBaseClient:
    """Fixture to provide a GolemBaseClient instance for tests."""
    _, rpc_url, ws_url = golemdb_node
    return await create_client(rpc_url, ws_url, account=client_account)


@pytest.fixture(scope="session")
async def client2(
    golemdb_node: tuple[DockerContainer | None, str, str],
    client_account2: LocalAccount,
) -> GolemBaseClient:
    """Fixture to provide a GolemBaseClient instance for tests."""
    _, rpc_url, ws_url = golemdb_node
    return await create_client(rpc_url, ws_url, account=client_account2)


async def create_client(
    rpc_url: str, ws_url: str, account: LocalAccount
) -> GolemBaseClient:
    """Create a GolemBaseClient instance."""
    logger.info(f"Connecting (http) {account.address} at {rpc_url}")  # noqa: G004
    logger.info(f"Connecting (ws) at {ws_url}")  # noqa: G004

    client = await GolemBaseClient.create(
        rpc_url=rpc_url,
        ws_url=ws_url,
        private_key=account.key,
    )

    # Wait for client to connect
    if not await client.is_connected():
        pytest.exit("Could not connect client.")

    # fetch eth balance of client account and abort if zero
    balance = await client.http_client().eth.get_balance(account.address)
    print(f"ETH balance for {account.address}: {balance / 10**18}")

    # abort tests if balance is zero
    if balance == 0:
        await client.disconnect()
        pytest.exit(f"Zero balance for {account.address}")

    return client


def _get_external_node_config() -> tuple[str, str] | None:
    """Get external node configuration from environment variables."""
    rpc_url = os.getenv(RPC_URL_ENV)
    ws_url = os.getenv(WS_URL_ENV)

    if not (rpc_url and ws_url):
        return None

    logger.info(f"Using external GolemDB node {rpc_url}/{ws_url}")  # noqa: G004
    return rpc_url, ws_url


def _create_testcontainer_node() -> Generator[
    tuple[DockerContainer, str, str], None, None
]:
    """Create and manage testcontainer GolemDB node."""
    logger.info("Starting up GolemDB node (testcontainer) ...")

    # Create HTTP wait strategy for the node to be ready
    http_wait = (
        HttpWaitStrategy(port=NODE_PORT_HTTP)
        .for_status_code(200)
        .with_startup_timeout(60)
        .with_poll_interval(1)
    )

    with (
        DockerContainer(NODE_IMAGE)
        .with_exposed_ports(NODE_PORT_HTTP, NODE_PORT_WS)
        .with_command(
            "--dev "
            "--dev.period 2 "
            "--http "
            "--http.api 'eth,web3,net,debug,golembase' "
            "--verbosity 3 "
            "--http.addr '0.0.0.0' "
            f"--http.port {NODE_PORT_HTTP} "
            "--http.corsdomain '*' "
            "--http.vhosts '*' "
            "--ws "
            "--ws.addr '0.0.0.0' "
            f"--ws.port {NODE_PORT_WS} "
            "--datadir '/geth_data'"
        )
        .waiting_for(http_wait) as container
    ):
        host = container.get_container_host_ip()
        node_rpc_http = f"http://{host}:{container.get_exposed_port(NODE_PORT_HTTP)}"
        node_rpc_ws = f"ws://{host}:{container.get_exposed_port(NODE_PORT_WS)}"

        logger.info("GolemDB node HTTP endpoint is ready.")

        # Additional wait for WebSocket endpoint using wait_container_is_ready
        @wait_container_is_ready(ConnectionRefusedError, TimeoutError)
        def check_websocket_ready() -> bool:
            async def test_ws_connection() -> bool:
                conn = await websockets.connect(node_rpc_ws, open_timeout=2)
                await conn.close()
                return True

            return asyncio.get_event_loop().run_until_complete(test_ws_connection())

        # Wait for WebSocket to be ready
        check_websocket_ready()
        logger.info("GolemDB node WS endpoint is ready.")

        logger.info("GolemDB node (testcontainer) running at %s", node_rpc_http)
        yield container, node_rpc_http, node_rpc_ws

        # Teardown after tests complete
        logger.info("GolemDB node (testcontainer) removed")


def _get_or_create_account(
    account_num: int, golemdb: DockerContainer | None
) -> LocalAccount:
    """Get account from environment variables or create and fund a new one."""
    wallet_file_key = f"{WALLET_FILE_ENV_PREFIX}_{account_num}"
    wallet_password_key = f"{WALLET_PASSWORD_ENV_PREFIX}_{account_num}"

    wallet_file = os.getenv(wallet_file_key)
    wallet_password = os.getenv(wallet_password_key)

    if wallet_file and wallet_password:
        logger.info("Loading account %s from wallet file: %s", account_num, wallet_file)
        return _load_account_from_file(wallet_file, wallet_password)

    if golemdb is None:
        msg = (
            f"No wallet file specified for account {account_num} and no testcontainer "
            "available. Please set environment variables "
            f"{wallet_file_key} and {wallet_password_key}."
        )
        raise ValueError(msg)

    logger.info("Creating and funding new account %s using testcontainer", account_num)
    return _create_funded_account(golemdb)


def _load_account_from_file(wallet_file: str, password: str) -> LocalAccount:
    """Load account from encrypted wallet file."""
    wallet_path = Path(wallet_file)
    if not wallet_path.exists():
        msg = f"Wallet file not found: {wallet_file}"
        raise FileNotFoundError(msg)

    with wallet_path.open() as f:
        encrypted_key = f.read()

    # Decrypt the private key using the password
    private_key = Account.decrypt(encrypted_key, password)

    # Create LocalAccount from the private key
    account = Account.from_key(private_key)

    logger.info("Loaded account from wallet file: %s", account.address)
    return account


def _create_funded_account(golemdb: DockerContainer) -> LocalAccount:
    """Fixture to create and fund a test account in the GolemDB node."""
    # Create a new account (generates a new private key)
    acct: LocalAccount = Account.create()

    # Get the private key (as hex)
    acct_address = acct.address
    acct_private_key = acct.key.hex()

    # Import account inside the container
    exit_code, output = golemdb.exec(
        ["golembase", "account", "import", "--key", acct_private_key]
    )
    assert exit_code == 0, f"Account import failed: {output.decode()}"

    # Fund account inside the container
    exit_code, output = golemdb.exec(["golembase", "account", "fund"])
    assert exit_code == 0, f"Account funding failed: {output.decode()}"
    logger.info(f"Imported and funded account: {acct_address}")  # noqa: G004

    # Printing account balance
    exit_code, output = golemdb.exec(["golembase", "account", "balance"])
    assert exit_code == 0, f"Account balance check failed: {output.decode()}"
    logger.info(f"Account balance: {output.decode().strip()}, exit_code: {exit_code}")  # noqa: G004

    return acct
