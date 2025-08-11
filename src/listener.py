"""Simple script to listen to all events from a specific contract."""

import argparse
import asyncio
import logging
import logging.config
import signal
import sys

import anyio
from golem_base_sdk import GolemBaseClient

# default instanc to run script
INSTANCE = "local"

LOG_LEVEL = "INFO"

ERR_CLIENT_CONNECT = 1
ERR_CLIENT_DISCONNECT = 2
ERR_LISTENER = 3

logging.config.dictConfig(
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


# Global variable to handle graceful shutdown of process
shutdown_event = asyncio.Event()


# Callback handler for Golem Base events
def entity_creation_handler(create_event: object) -> None:  # noqa: D103
    logger.info(f"Entity creation event {create_event}")  # noqa: G004


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


async def listen_to_contract_events(instance: str) -> None:
    """Shared method to listen to contract events."""
    client = None
    try:
        # Create client and start listening
        client = await _create_client(instance)
        await _setup_event_watching(client, "entity_creation_listener")
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


async def _create_client(instance: str) -> GolemBaseClient:
    # Load private key
    async with await anyio.open_file("./private.key", "rb") as private_key_file:
        key_bytes = await private_key_file.read(32)

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


async def _setup_event_watching(client: GolemBaseClient, label: str) -> None:
    """Set up event watching with callbacks for all event types."""
    await client.watch_logs(
        label=label,
        create_callback=lambda create: entity_creation_handler(create),
        update_callback=lambda update: entity_update_handler(update),
        delete_callback=lambda delete: entity_deletion_handler(delete),
        extend_callback=lambda extend: entity_extension_handler(extend),
    )


def main() -> None:
    """Run the event listener."""
    parser = argparse.ArgumentParser(description="Contract Event Listener")
    parser.add_argument(
        "--instance",
        choices=INSTANCE_URLS.keys(),
        default=INSTANCE,
        help="Which instance to connect to (default: kaolin)",
    )
    parser.add_argument(
        "--method",
        choices=["polling", "websocket"],
        default="polling",
        help="Event listening method (default: polling)",
    )
    args = parser.parse_args()

    # Set up signal handlers for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    logger.info("Starting event listener for GolemBase contract events")
    logger.info("Using %s method on %s network", args.method, args.instance)

    try:
        asyncio.run(listen_to_contract_events(args.instance))
    except KeyboardInterrupt:
        logger.info("Event listener stopped by user")
    except Exception:
        logger.exception("Event listener failed")
        sys.exit(ERR_LISTENER)


if __name__ == "__main__":
    main()
