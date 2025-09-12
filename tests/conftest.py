"""Global test configuration and fixtures."""

import logging
import time
from collections.abc import Generator

import pytest
import requests
from eth_account import Account
from eth_account.signers.local import LocalAccount
from golem_base_sdk import GolemBaseClient
from testcontainers.core.container import DockerContainer

logger = logging.getLogger(__name__)

NODE_IMAGE = "golemdb-node:latest"
NODE_PORT = 8545


@pytest.fixture(scope="session", autouse=True)
def setup_test_environment() -> Generator[None, None, None]:
    """Session level fixture to configure logging."""
    # Pytest handles logging configuration via --log-level, --log-cli-level, etc.
    # No need for custom logging setup here

    yield  # This is where all tests run

    # Teardown after all tests complete
    print("Tearing down test environment...")


@pytest.fixture(scope="session")
def golemdb_node() -> Generator[tuple[DockerContainer, str], None, None]:
    """Fixture to run a temporary GolemDB container for testing."""
    logger.info("Starting up GolemDB node (testcontainer) ...")

    with (
        DockerContainer(NODE_IMAGE)
        .with_exposed_ports(NODE_PORT)
        .with_command(
            "--dev "
            "--http "
            "--http.api 'eth,web3,net,debug,golembase' "
            "--verbosity 3 "
            "--http.addr '0.0.0.0' "
            f"--http.port {NODE_PORT} "
            "--http.corsdomain '*' "
            "--http.vhosts '*' "
            "--ws "
            "--ws.addr '0.0.0.0' "
            f"--ws.port {NODE_PORT} "
            "--datadir '/geth_data'"
        ) as container
    ):
        host = container.get_container_host_ip()
        port = container.get_exposed_port(NODE_PORT)

        # Wait for the node to be ready
        for _ in range(10):
            try:
                if requests.get(f"http://{host}:{port}").status_code == 200:
                    break
            except Exception:
                time.sleep(1)

        logger.info(f"GolemDB node (testcontainer) running at {host}:{port}")  # noqa: G004
        yield container, f"{host}:{port}"

        # Teardown after tests complete
        logger.info("GolemDB node (testcontainer) removed")


@pytest.fixture(scope="session")
def client_account(golemdb_node: tuple[DockerContainer, str]) -> LocalAccount:
    """Fixture to create and fund client_account using the GolemDB node."""
    return _create_funded_account(golemdb_node[0])


@pytest.fixture(scope="session")
def client_account2(golemdb_node: tuple[DockerContainer, str]) -> LocalAccount:
    """Fixture to create and fund client_account using the GolemDB node."""
    return _create_funded_account(golemdb_node[0])


@pytest.fixture(scope="session")
async def client(
    golemdb_node: tuple[DockerContainer, str], client_account: LocalAccount
) -> GolemBaseClient:
    """Fixture to provide a GolemBaseClient instance for tests."""
    _, host_port = golemdb_node
    return await create_client(host_port=host_port, account=client_account)


@pytest.fixture(scope="session")
async def client2(
    golemdb_node: tuple[DockerContainer, str], client_account2: LocalAccount
) -> GolemBaseClient:
    """Fixture to provide a GolemBaseClient instance for tests."""
    _, host_port = golemdb_node
    return await create_client(host_port=host_port, account=client_account2)


async def create_client(host_port: str, account: LocalAccount) -> GolemBaseClient:
    """Create a GolemBaseClient instance."""
    print(f"Connecting {account.address} at {host_port}")

    client = await GolemBaseClient.create(
        rpc_url=f"http://{host_port}",
        ws_url=f"ws://{host_port}",
        private_key=account.key,
    )

    # fetch eth balance of client account and abort if zero
    balance = await client.http_client().eth.get_balance(account.address)
    print(f"ETH balance for {account.address}: {balance / 10**18}")

    # abort tests if balance is zero
    if balance == 0:
        await client.disconnect()
        pytest.exit(f"Zero balance for {account.address}")

    return client


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
