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
from golem_base_sdk import EntityKey, EntityMetadata, GenericBytes, GolemBaseClient
from web3 import Web3

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


def get_annotations(metadata: EntityMetadata) -> dict[str, str | int]:
    """Extract annotations as dict from entity metadata."""
    if not metadata:
        return {}

    annotations = {}

    if metadata.string_annotations:
        annotations |= {a.key: a.value for a in metadata.string_annotations}

    if metadata.numeric_annotations:
        annotations |= {a.key: a.value for a in metadata.numeric_annotations}

    return annotations


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


def get_username(wallet_file: str) -> str | None:
    """Get the username from the wallet file name: wallet_<username>.json."""
    # Strip leading directories
    filename = Path(wallet_file).name
    if filename.startswith("wallet_") and filename.endswith(".json"):
        return filename[len("wallet_") : -len(".json")]

    return None


def get_entity_key(entity_key: object) -> EntityKey:
    """Get the entity key as an EntityKey object."""
    if isinstance(entity_key, str):
        return EntityKey(GenericBytes.from_hex_string(entity_key))

    if isinstance(entity_key, GenericBytes):
        return EntityKey(entity_key)

    logger.warning(
        "Invalid entity key type %s. Returning empty EntityKey",
        type(entity_key).__name__,
    )
    return EntityKey(GenericBytes(b""))


def get_address(address: object) -> str:
    """Get a checksummed address."""
    if isinstance(address, GenericBytes):
        return address.as_address()

    if isinstance(address, str):
        return Web3.to_checksum_address(address)

    logger.warning(
        "Invalid address type %s. Returning empty string", type(address).__name__
    )
    return ""


def get_user_string(sender_address: str, username: str | None) -> str:
    """Return a user string for CLI usage."""
    if not username or len(username) == 0:
        return get_short_address(sender_address)

    return f"[{username} {get_short_address(sender_address)}]"


def get_short_address(address: object) -> str:
    """Get a shortened version of the address.

    Args:
        address: Full ethereum address

    Returns:
        Shortened address in format 0x1234...abcd

    """
    address = get_address(address)
    if address is None:
        return "Invalid address"

    return address[:6] + "..." + address[-4:]
