"""Simple script to listen to all events from a specific contract."""

import argparse
import asyncio
import logging
import sys
import threading
from collections.abc import Sequence

from golem_base_sdk import (
    Annotation,
    CreateEntityReturnType,
    EntityMetadata,
    GolemBaseClient,
    GolemBaseCreate,
    GolemBaseUpdate,
    QueryEntitiesResult,
    UpdateEntityReturnType,
)
from websockets import ConnectionClosedOK

from config import (
    DEFAULT_INSTANCE,
    ERR_LISTENER,
    INSTANCE_URLS,
    LOG_LEVELS,
)
from utils import (
    create_golem_client,
    get_address,
    get_annotations,
    get_entity_key,
    get_short_address,
    get_user_string,
    get_username,
    run_sync,
    setup_logging,
)

# Constants for message loop
LOG_LEVEL = "warn"
CHAT_WIDTH = 80

# Entity annotation data
VERSION = "version"
VERSION_ANNOTATION = Annotation(VERSION, "1.0")

COLLECTION = "collection"
MESSAGES = "message"
MESSAGE_ANNOTATION = Annotation(COLLECTION, MESSAGES)

USERS = "users"
USERNAME = "username"
USER_ADDRESS = "user_address"
USERS_ANNOTATION = Annotation(COLLECTION, USERS)

# Global vars
logger = logging.getLogger(__name__)
usernames: dict[str, str] = {}


def _get_sender(client: GolemBaseClient, message_address: str | None) -> str | None:
    """Get the sender's username from the message address."""
    global usernames  # noqa: PLW0602

    if message_address is None:
        return "<unknown sender>"

    if message_address in usernames:
        return get_user_string(message_address, usernames[message_address])

    query_result = run_sync(_get_user(client, message_address))

    # No user information found
    if not query_result:
        return get_user_string(message_address, None)

    # Simplistic assumption: 1st record is good enough
    user = query_result[0]
    username_bytes: bytes = user.storage_value
    username = username_bytes.decode("utf-8")

    # Update local user names cache
    usernames[message_address] = username

    return get_user_string(message_address, username)


def _print_incoming_message(
    client: GolemBaseClient, payload: bytes, message_address: str | None
) -> None:
    """Print the message at the end of a 80 chars line."""
    message = payload.decode("utf-8").strip()
    if len(message) == 0:
        return

    sender = _get_sender(client, message_address)
    message_line = f"{message} {sender}"

    # Truncate message if it's too long
    if len(message_line) > CHAT_WIDTH:
        message_line = message_line[:CHAT_WIDTH]

    # Pad with spaces to right-align within 80 chars
    print(message_line.rjust(CHAT_WIDTH))


# Event handler functions for Golem Base events
def _entity_creation_handler(
    client: GolemBaseClient, create_event: CreateEntityReturnType
) -> None:
    """Print message entities from other clients."""
    entity_key = create_event.entity_key
    metadata: EntityMetadata = run_sync(client.get_entity_metadata(entity_key))
    annotations = get_annotations(metadata)

    # Missing annotation
    if COLLECTION not in annotations:
        return

    # Wrong collection
    if annotations[COLLECTION] != MESSAGES:
        return

    # Sender is this client
    message_address = get_address(metadata.owner)
    client_address = get_address(client.get_account_address())
    if message_address == client_address:
        return

    # message from some other client
    payload: bytes = run_sync(client.get_storage_value(entity_key))
    _print_incoming_message(client, payload, message_address)


def _entity_update_handler(
    client: GolemBaseClient,  # noqa: ARG001
    update_event: UpdateEntityReturnType,
) -> None:
    logger.info(f"Entity update event {update_event}")  # noqa: G004


async def _handle_golem_events(client: GolemBaseClient) -> None:
    try:
        # Register golem events to listen for
        logger.info(
            "Monitoring create and update events at %s",
            client.golem_base_contract.address,
        )
        await client.watch_logs(
            label="chat_client",
            create_callback=lambda create: _entity_creation_handler(client, create),
            update_callback=lambda update: _entity_update_handler(client, update),
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

        except ConnectionClosedOK:
            print("Client shutdown")
        except Exception:
            logger.exception("Unexpected error during disconnection")


async def _send_message(client: GolemBaseClient, message: str) -> None:
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


def _handle_user_input(client: GolemBaseClient) -> None:
    global usernames  # noqa: PLW0602
    user_address = get_address(client.get_account_address())
    user_string = get_user_string(user_address, usernames[user_address])

    print(f"You are logged in as: {user_string}")
    print("Type messages, press Ctrl+C to exit")
    while True:
        try:
            # Get and send next message from user
            message = input().strip()
            if len(message) > 0:
                run_sync(_send_message(client, message))

        except (EOFError, KeyboardInterrupt):
            break


async def _get_user(
    client: GolemBaseClient, user_address: str
) -> Sequence[QueryEntitiesResult]:
    query = f'{COLLECTION} = "{USERS}" && {USER_ADDRESS} = "{user_address}"'
    return await client.query_entities(query)


async def _set_update_username(client: GolemBaseClient, wallet_file: str) -> None:
    global usernames  # noqa: PLW0602

    # Create username from wallet file
    user_address = get_address(client.get_account_address())
    username = get_username(wallet_file)
    if not username:
        username = get_short_address(user_address)

    # Update usernames cache
    usernames[user_address] = username

    # Get username entries for user address
    query_result = await _get_user(client, user_address)

    # User not yet registered, add new entry
    if not query_result:
        await client.create_entities(
            [
                GolemBaseCreate(
                    username.encode("UTF-8"),
                    1000,  # TTL in blocks
                    [
                        USERS_ANNOTATION,
                        VERSION_ANNOTATION,
                        Annotation(USER_ADDRESS, user_address),
                    ],
                    [],
                )
            ]
        )
        return

    # Existing user, update entry with new username
    if len(query_result) == 1:
        existing_entity_key = get_entity_key(query_result[0].entity_key)
        await client.update_entities(
            [
                GolemBaseUpdate(
                    existing_entity_key,
                    username.encode("UTF-8"),
                    1000,  # TTL in blocks
                    [
                        USERS_ANNOTATION,
                        VERSION_ANNOTATION,
                        Annotation(USER_ADDRESS, user_address),
                    ],
                    [],
                )
            ]
        )


async def _run_chat_client(instance: str, wallet_file: str) -> None:
    # Create and connect client to Golem Base
    client = await create_golem_client(instance, wallet_file)

    # Update user name record
    await _set_update_username(client, wallet_file)

    # Start the user input loop in a separate thread
    threading.Thread(target=_handle_user_input, args=(client,), daemon=True).start()

    # Run message handling until interrupted
    await _handle_golem_events(client)


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
        default=LOG_LEVEL,
        help=f"Log level (default: {LOG_LEVEL})",
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
