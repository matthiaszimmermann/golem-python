"""Simple script to listen to all events from a specific contract."""

import argparse
import asyncio
import getpass
import json
import logging
import signal
import sys
import threading
from collections.abc import Coroutine
from concurrent.futures import ThreadPoolExecutor
from logging.config import dictConfig
from typing import Any

import anyio
from eth_account import Account
from golem_base_sdk import (
    Annotation,
    CreateEntityReturnType,
    EntityMetadata,
    GolemBaseClient,
    GolemBaseCreate,
)

# default instanc to run script
INSTANCE = "local"

LOG_LEVEL = "INFO"

# Width of the chat window
CHAT_WIDTH = 80

ERR_CLIENT_CONNECT = 1
ERR_CLIENT_DISCONNECT = 2
ERR_LISTENER = 3

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
            "": {"level": LOG_LEVEL, "handlers": ["console"]},
        },
        "disable_existing_loggers": False,
    }
)
logger = logging.getLogger(__name__)

# localhost: when running script directly on local machine
# host.docker.internal: when running script inside a Docker container
# eg from a devcontainer setup
LOCALHOST = "host.docker.internal"

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

# Global client variable
client: GolemBaseClient

# Global variable to handle graceful shutdown of process
shutdown_event = asyncio.Event()


# Callback handler for Golem Base events
def entity_creation_handler(create_event: CreateEntityReturnType) -> None:
    """Handle entity creation events."""
    global client  # noqa: PLW0602
    entity_key = create_event.entity_key
    metadata: EntityMetadata = _run_sync(client.get_entity_metadata(entity_key))

    # Only react to messages from other clients (= entities we don't own)
    message_address = metadata.owner.as_hex_string()
    client_address = client.get_account_address().lower()
    if message_address != client_address:
        payload: bytes = _run_sync(client.get_storage_value(entity_key))
        print_incoming_message(payload)


def print_incoming_message(payload: bytes) -> None:
    """Print the message at the end of a 80 chars line."""
    # Truncate message if it's too long
    message = payload.decode("utf-8")
    if len(message) > CHAT_WIDTH:
        message = message[:CHAT_WIDTH]
    # Pad with spaces to right-align within 80 chars
    padded_message = message.rjust(CHAT_WIDTH)
    print(padded_message)


def entity_update_handler(update_event: object) -> None:  # noqa: D103
    logger.info(f"Entity update event {update_event}")  # noqa: G004


def entity_deletion_handler(delete_event: object) -> None:  # noqa: D103
    logger.info(f"Entity deletion event {delete_event}")  # noqa: G004


def entity_extension_handler(extension_event: object) -> None:  # noqa: D103
    logger.info(f"Entity extension event {extension_event}")  # noqa: G004


# Signal handler for graceful shutdown
def signal_handler(signum: int, _: object) -> None:
    """Handle shutdown signals gracefully."""
    logger.info("Received signal %s, shutting down...", signum)
    shutdown_event.set()


async def run_interactive_client(instance: str, wallet_file: str) -> None:
    """Run client with event listening and interactive entity creation."""
    global client  # noqa: PLW0602

    try:
        # Create client and start event listening in background
        await _create_client(instance, wallet_file)

        # Start event listening as a background task
        event_task = asyncio.create_task(_setup_event_watching(client))

        logger.info("Event listener started in background")
        logger.info("You can now type messages to create entities")
        logger.info("Type 'quit' or press Ctrl+C to exit")

        # Run interactive loop in a separate thread to not block the event loop
        def interactive_loop() -> None:
            while not shutdown_event.is_set():
                try:
                    message = input("")

                    if message.lower() in ["quit"]:
                        logger.info("User requested exit")
                        shutdown_event.set()
                        break

                    if message.strip():
                        # Create entity with the user's message
                        create_obj = GolemBaseCreate(
                            message.encode("utf-8"),
                            60,  # TTL in blocks
                            [Annotation("app", "interactive_client")],
                            [],
                        )

                        # Schedule the entity creation on the event loop
                        _run_sync(client.create_entities([create_obj]))

                except EOFError:
                    logger.info("EOF received, stopping interactive mode")
                    shutdown_event.set()
                    break
                except Exception:
                    logger.exception("Error creating entity")

        # Run the interactive loop in a thread
        input_thread = threading.Thread(target=interactive_loop, daemon=True)
        input_thread.start()

        # Wait for shutdown event
        await shutdown_event.wait()

        # Cancel the event task
        event_task.cancel()
        try:
            await event_task
        except asyncio.CancelledError:
            pass

    except Exception:
        logger.exception("Failed to run interactive client")
    finally:
        if client:
            try:
                await client.disconnect()
                logger.info("Client disconnected")
            except Exception:
                logger.exception("Error disconnecting client")


async def listen_to_contract_events(instance: str, wallet_file: str) -> None:
    """Shared method to listen to contract events."""
    global client  # noqa: PLW0602
    try:
        # Create client and start listening
        await _create_client(instance, wallet_file)
        await _setup_event_watching(client)
        logger.info("Event listener started. Press Ctrl+C to stop...")

        # Keep the listener running
        try:
            await shutdown_event.wait()
        except asyncio.CancelledError:
            logger.info("Event listening cancelled")

    except Exception:
        logger.exception("Failed to start event listener")
    finally:
        if client:
            try:
                await client.disconnect()
                logger.info("Disconnected from client")
            except Exception:
                logger.exception("Disconnecting failed")
                sys.exit(ERR_CLIENT_DISCONNECT)


async def _create_client(instance: str, wallet_file: str) -> GolemBaseClient:
    global client  # noqa: PLW0603

    # Load wallet from JSON file
    async with await anyio.open_file(wallet_file, "r") as f:
        wallet_json = json.loads(await f.read())

    # Get password for wallet decryption
    password = getpass.getpass(f"Enter password for wallet {wallet_file}: ")

    # Decrypt the wallet to get the private key
    try:
        key_bytes = Account.decrypt(wallet_json, password)
    except Exception:
        logger.exception("Failed to decrypt wallet")
        raise

    # Create client
    client = await GolemBaseClient.create(
        rpc_url=INSTANCE_URLS[instance]["rpc"],
        ws_url=INSTANCE_URLS[instance]["ws"],
        private_key=key_bytes,
    )

    if not await client.is_connected():
        logger.error("Could not connect to the network")
        sys.exit(ERR_CLIENT_CONNECT)

    logger.info("Connected to %s network", instance)
    logger.info("Monitoring GolemBase contract events")
    logger.info("GolemBase contract address: %s", client.golem_base_contract.address)

    return client


async def _setup_event_watching(client: GolemBaseClient) -> None:
    """Set up event watching with callbacks for all event types."""
    await client.watch_logs(
        label="entity_creation_listener",
        create_callback=lambda create: entity_creation_handler(create),
        # update_callback=lambda update: entity_update_handler(update),
        # delete_callback=lambda delete: entity_deletion_handler(delete),
        # extend_callback=lambda extend: entity_extension_handler(extend),
    )


def _run_sync(routine: Coroutine[Any, Any, Any]) -> Any:  # noqa: ANN202, ANN401, RUF100
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


def main() -> None:
    """Run the interactive client with event listening."""
    parser = argparse.ArgumentParser(description="Interactive Contract Event Listener")
    parser.add_argument(
        "wallet",
        help="JSON wallet filename (required)",
    )
    parser.add_argument(
        "--instance",
        choices=INSTANCE_URLS.keys(),
        default=INSTANCE,
        help=f"Which instance to connect to (default: {INSTANCE})",
    )
    args = parser.parse_args()

    # Set up signal handlers for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    logger.info("Starting interactive client with event listening")

    try:
        asyncio.run(run_interactive_client(args.instance, args.wallet))
    except KeyboardInterrupt:
        logger.info("Interactive client stopped by user")
    except Exception:
        logger.exception("Interactive client failed")
        sys.exit(ERR_LISTENER)


if __name__ == "__main__":
    main()
