"""Simple script to listen to all events from a specific contract."""

import argparse
import asyncio
import logging
import sys
import threading

from golem_base_sdk import (
    Annotation,
    CreateEntityReturnType,
    EntityMetadata,
    GolemBaseClient,
    GolemBaseCreate,
)

from config import (
    DEFAULT_INSTANCE,
    DEFAULT_LOG_LEVEL,
    ERR_LISTENER,
    INSTANCE_URLS,
    LOG_LEVELS,
)
from utils import create_golem_client, get_short_address, run_sync, setup_logging

# Constants for message loop
QUIT = "quit"
CHAT_WIDTH = 80

# Entity annotation data
VERSION = "version"
VERSION_ANNOTATION = Annotation(VERSION, "1.0")

COLLECTION = "collection"
MESSAGES = "message"
MESSAGE_ANNOTATION = Annotation(COLLECTION, MESSAGES)


# Global vars
logger = logging.getLogger(__name__)
client: GolemBaseClient


def _print_incoming_message(payload: bytes, message_address: str) -> None:
    """Print the message at the end of a 80 chars line."""
    message = payload.decode("utf-8").strip()
    if len(message) == 0:
        return

    sender = get_short_address(message_address)
    message = f"{message} [{sender}]"

    # Truncate message if it's too long
    if len(message) > CHAT_WIDTH:
        message = message[:CHAT_WIDTH]

    # Pad with spaces to right-align within 80 chars
    print(message.rjust(CHAT_WIDTH))


def _get_annotations(metadata: EntityMetadata) -> dict[str, str | int]:
    if not metadata:
        return {}

    annotations = {}

    if metadata.string_annotations:
        annotations |= {a.key: a.value for a in metadata.string_annotations}

    if metadata.numeric_annotations:
        annotations |= {a.key: a.value for a in metadata.numeric_annotations}

    return annotations


# Event handler functions for Golem Base events
def _entity_creation_handler(create_event: CreateEntityReturnType) -> None:
    """Print message from other client."""
    global client  # noqa: PLW0602

    entity_key = create_event.entity_key
    metadata: EntityMetadata = run_sync(client.get_entity_metadata(entity_key))
    annotations = _get_annotations(metadata)

    # Missing annotation
    if COLLECTION not in annotations:
        return

    # Wrong collection
    if annotations[COLLECTION] != MESSAGES:
        return

    # Sender is this client
    message_address = metadata.owner.as_hex_string()
    client_address = client.get_account_address().lower()
    if message_address == client_address:
        return

    # message from some other client
    payload: bytes = run_sync(client.get_storage_value(entity_key))
    _print_incoming_message(payload, message_address)


def _entity_update_handler(update_event: object) -> None:
    logger.info(f"Entity update event {update_event}")  # noqa: G004


async def _handle_golem_events() -> None:
    global client  # noqa: PLW0602

    try:
        # Register golem events to listen for
        logger.info(
            "Monitoring create and update events at %s",
            client.golem_base_contract.address,
        )
        await client.watch_logs(
            label="chat_client",
            create_callback=lambda create: _entity_creation_handler(create),
            update_callback=lambda update: _entity_update_handler(update),
        )
        logger.info("Golem Base event listener started")

        # Keep the listener running indefinitely
        await asyncio.Event().wait()

    except asyncio.CancelledError:
        logger.info("Golem Base event listening stopped gracefully")
    except Exception:
        logger.exception("Failed to start Golem Base event listener")
    finally:
        try:
            await client.disconnect()
            logger.info("Disconnected from client")
        except Exception as e:  # noqa: BLE001
            # Don't treat disconnection errors as fatal during shutdown
            # Common errors: ProviderConnectionError, ConnectionError, OSError
            logger.warning("Error during disconnection (normal during shutdown): %s", e)


async def _send_message(message: str) -> None:
    global client  # noqa: PLW0602
    await client.create_entities(
        [
            GolemBaseCreate(
                message.encode("utf-8"),
                60,  # TTL in blocks
                [MESSAGE_ANNOTATION, VERSION_ANNOTATION],
                [],
            )
        ]
    )


def _handle_user_input(loop: asyncio.AbstractEventLoop) -> None:
    print(f"Type messages, type '{QUIT}' or press Ctrl+C to exit.")
    while True:
        try:
            # Get next message from user
            message = input().strip()
            if message == QUIT:
                break

            # Send the message if it's not empty
            if len(message) > 0:
                asyncio.run_coroutine_threadsafe(_send_message(message), loop)

        except (EOFError, KeyboardInterrupt):
            break


async def _run_chat_client(instance: str, wallet_file: str) -> None:
    # Create and connect client to Golem Base
    global client  # noqa: PLW0603
    client = await create_golem_client(instance, wallet_file)

    # Start the user input loop in a separate thread
    loop = asyncio.get_running_loop()
    threading.Thread(target=_handle_user_input, args=(loop,), daemon=True).start()

    # Run message handling until interrupted
    await _handle_golem_events()


def main() -> None:
    """Run the event listener."""
    parser = argparse.ArgumentParser(description="Contract Event Listener")
    parser.add_argument(
        "--instance",
        choices=INSTANCE_URLS.keys(),
        default=DEFAULT_INSTANCE,
        help="Which instance to connect to (default: local)",
    )
    parser.add_argument(
        "--logging",
        choices=LOG_LEVELS.keys(),
        default=DEFAULT_LOG_LEVEL,
        help=f"Log level (default: {DEFAULT_LOG_LEVEL})",
    )
    parser.add_argument(
        "wallet",
        help="JSON wallet filename (required)",
    )
    args = parser.parse_args()
    setup_logging(args.logging)

    try:
        asyncio.run(_run_chat_client(args.instance, args.wallet))
    except KeyboardInterrupt:
        logger.info("Event listener stopped by user")
    except Exception:
        logger.exception("Event listener failed")
        sys.exit(ERR_LISTENER)


if __name__ == "__main__":
    main()
