"""Shared utilities for the Golem Python client."""

import asyncio
import getpass
import json
import logging
import sys
from collections.abc import Coroutine
from concurrent.futures import ThreadPoolExecutor
from logging.config import dictConfig
from pathlib import Path
from typing import Any

from eth_account import Account
from golem_base_sdk import GolemBaseClient

from config import ERR_CLIENT_CONNECT, ERR_WALLET_PASSWORD, INSTANCE_URLS, LOG_LEVELS
from exceptions import WalletDecryptionError

logger = logging.getLogger(__name__)


def run_sync(routine: Coroutine[Any, Any, Any]) -> Any:  # noqa: ANN401
    """Run async routine in a synchronous context."""
    try:
        # Check if there's a running event loop
        asyncio.get_running_loop()
    except RuntimeError:
        # No current event loop
        return asyncio.run(routine)
    else:
        # Existing event loop: Run in a new thread
        def run_in_new_loop() -> Any:  # noqa: ANN202, ANN401, RUF100
            new_loop = asyncio.new_event_loop()
            asyncio.set_event_loop(new_loop)
            try:
                return new_loop.run_until_complete(routine)
            finally:
                new_loop.close()

        with ThreadPoolExecutor() as pool:
            future = pool.submit(run_in_new_loop)
            return future.result()


def get_wallet_private_key(wallet_file: str) -> bytes:
    """Obtain private key from specified wallet file.

    Args:
        wallet_file: Path to the JSON wallet file

    Returns:
        Private key bytes

    Raises:
        RuntimeError: If wallet file not found or decryption fails

    """
    # Load wallet from JSON file
    file = Path(wallet_file)
    if not file.exists():
        error_msg = f"Wallet file '{wallet_file}' not found."
        logger.error(error_msg)
        raise RuntimeError(error_msg)

    with file.open("r") as f:
        wallet_json = json.loads(f.read())

    # Get password for wallet decryption
    password = getpass.getpass(f"Enter password for wallet {wallet_file}: ")

    # Decrypt the wallet to get the private key
    try:
        return Account.decrypt(wallet_json, password)
    except ValueError:
        # ValueError is raised for MAC mismatch (wrong password)
        error_msg = "Failed to decrypt wallet - incorrect password"
        logger.error(error_msg)  # noqa: TRY400
        raise WalletDecryptionError(error_msg) from None
    except Exception as e:  # noqa: BLE001
        # Handle other potential decryption errors
        error_msg = f"Failed to decrypt wallet - {type(e).__name__}"
        logger.error(error_msg)  # noqa: TRY400
        raise WalletDecryptionError(error_msg) from None


async def create_golem_client(instance: str, wallet_file: str) -> GolemBaseClient:
    """Create a GolemBase client for the specified instance and wallet.

    Args:
        instance: Network instance name (local, demo, kaolin)
        wallet_file: Path to the JSON wallet file

    Returns:
        Connected GolemBaseClient instance

    Raises:
        SystemExit: If wallet decoding fails or client cannot connect to network

    """
    try:
        key_bytes = get_wallet_private_key(wallet_file)
    except (WalletDecryptionError, RuntimeError):
        # Both wallet decryption and file not found errors should exit cleanly
        sys.exit(ERR_WALLET_PASSWORD)

    # Create client
    client = await GolemBaseClient.create(
        rpc_url=INSTANCE_URLS[instance]["rpc"],
        ws_url=INSTANCE_URLS[instance]["ws"],
        private_key=key_bytes,
    )

    # Wait for client to connect
    if not await client.is_connected():
        logger.error("Could not connect to the network")
        sys.exit(ERR_CLIENT_CONNECT)

    logger.info("Connected to %s network", instance)
    return client


def setup_logging(log_level: str) -> None:
    """Configure logging for the specified log level.

    Args:
        log_level: Log level key (info, warn, error)

    """
    dictConfig(
        {
            "version": 1,
            "formatters": {
                "default": {
                    "format": "[%(asctime)s] %(levelname)s in %(module)s: %(message)s",
                }
            },
            "handlers": {
                "console": {
                    "class": "logging.StreamHandler",
                    "formatter": "default",
                    "level": "DEBUG",
                    "stream": "ext://sys.stdout",
                }
            },
            "loggers": {
                "": {"level": LOG_LEVELS[log_level], "handlers": ["console"]},
            },
            "disable_existing_loggers": False,
        }
    )


def get_short_address(address: str) -> str:
    """Get a shortened version of the address.

    Args:
        address: Full ethereum address

    Returns:
        Shortened address in format 0x1234...abcd

    """
    return address[:6] + "..." + address[-4:]
