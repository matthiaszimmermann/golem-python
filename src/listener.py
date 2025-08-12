"""Simple script to listen to all events from a specific contract."""

import argparse
import asyncio
import logging
import sys

from golem_base_sdk import GolemBaseClient

from config import (
    DEFAULT_INSTANCE,
    DEFAULT_LOG_LEVEL,
    ERR_LISTENER,
    INSTANCE_URLS,
    LOG_LEVELS,
)
from utils import create_golem_client, setup_logging

logger = logging.getLogger(__name__)


# Event handler functions for Golem Base events
def _entity_creation_handler(create_event: object) -> None:
    logger.info(f"Entity creation event {create_event}")  # noqa: G004


def _entity_update_handler(update_event: object) -> None:
    logger.info(f"Entity update event {update_event}")  # noqa: G004


def _entity_deletion_handler(delete_event: object) -> None:
    logger.info(f"Entity deletion event {delete_event}")  # noqa: G004


def _entity_extension_handler(extension_event: object) -> None:
    logger.info(f"Entity extension event {extension_event}")  # noqa: G004


# Other internal functions
async def _setup_event_watching(client: GolemBaseClient, label: str) -> None:
    """Set up event watching with callbacks for all event types."""
    logger.info(
        "Monitoring GolemBase contract events at %s",
        client.golem_base_contract.address,
    )

    await client.watch_logs(
        label=label,
        create_callback=lambda create: _entity_creation_handler(create),
        update_callback=lambda update: _entity_update_handler(update),
        delete_callback=lambda delete: _entity_deletion_handler(delete),
        extend_callback=lambda extend: _entity_extension_handler(extend),
    )


# Public functions
async def _listen_to_golem_events(client: GolemBaseClient) -> None:
    """Set up and start listening to Golem Base contract events."""
    try:
        # Create client and start listening
        await _setup_event_watching(client, "entity_creation_listener")
        logger.info("Event listener started. Press Ctrl+C to stop...")

        # Keep the listener running indefinitely
        await asyncio.Event().wait()

    except asyncio.CancelledError:
        logger.info("Event listening stopped gracefully")
    except Exception:
        logger.exception("Failed to start event listener")
    finally:
        try:
            await client.disconnect()
            logger.info("Disconnected from client")
        except Exception as e:  # noqa: BLE001
            # Don't treat disconnection errors as fatal during shutdown
            # Common errors: ProviderConnectionError, ConnectionError, OSError
            logger.warning("Error during disconnection (normal during shutdown): %s", e)


async def _run_listener(instance: str, wallet_file: str) -> None:
    """Run the event listener with the specified instance and wallet."""
    client = await create_golem_client(instance, wallet_file)
    await _listen_to_golem_events(client)


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
        logger.info("Starting event listener for GolemBase contract events")
        asyncio.run(_run_listener(args.instance, args.wallet))
    except KeyboardInterrupt:
        logger.info("Event listener stopped by user")
    except Exception:
        logger.exception("Event listener failed")
        sys.exit(ERR_LISTENER)


if __name__ == "__main__":
    main()
