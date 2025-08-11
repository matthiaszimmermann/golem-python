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


# Global variable to handle graceful shutdown
shutdown_event = asyncio.Event()


def signal_handler(signum: int, _: object) -> None:
    """Handle shutdown signals gracefully."""
    logger.info("Received signal %s, shutting down...", signum)
    shutdown_event.set()


async def listen_to_contract_events(instance: str) -> None:
    """Listen to all events from the specified contract."""
    client = None
    try:
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
            return

        logger.info("Connected to %s network", instance)
        logger.info("Monitoring GolemBase contract events")
        logger.info(
            "GolemBase contract address: %s", client.golem_base_contract.address
        )

        # Use the SDK's built-in event watching
        await client.watch_logs(
            label="contract_listener",
            create_callback=lambda create: logger.info(
                "CREATE Event - Entity Key: %s",
                create.entity_key.as_hex_string(),
            ),
            update_callback=lambda update: logger.info(
                "UPDATE Event - Entity Key: %s",
                update.entity_key.as_hex_string(),
            ),
            delete_callback=lambda delete: logger.info(
                "DELETE Event - Entity Key: %s",
                delete.as_hex_string(),
            ),
            extend_callback=lambda extend: logger.info(
                "EXTEND Event - Entity Key: %s, New Expiration: %s",
                extend.entity_key.as_hex_string(),
                extend.new_expiration_block,
            ),
        )

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
                logger.exception("Error during disconnect")


async def listen_with_websocket_subscription(instance: str) -> None:
    """Alternative method using direct WebSocket subscriptions."""
    client = None
    try:
        async with await anyio.open_file("./private.key", "rb") as private_key_file:
            key_bytes = await private_key_file.read(32)

        client = await GolemBaseClient.create(
            rpc_url=INSTANCE_URLS[instance]["rpc"],
            ws_url=INSTANCE_URLS[instance]["ws"],
            private_key=key_bytes,
        )

        if not await client.is_connected():
            logger.error("Could not connect to the network")
            return

        logger.info("Connected to %s network", instance)
        logger.info("Monitoring GolemBase contract events")

        # Use the SDK's built-in event watching (same as the polling method)
        await client.watch_logs(
            label="websocket_listener",
            create_callback=lambda create: logger.info(
                "CREATE Event - Entity Key: %s",
                create.entity_key.as_hex_string(),
            ),
            update_callback=lambda update: logger.info(
                "UPDATE Event - Entity Key: %s",
                update.entity_key.as_hex_string(),
            ),
            delete_callback=lambda delete: logger.info(
                "DELETE Event - Entity Key: %s",
                delete.as_hex_string(),
            ),
            extend_callback=lambda extend: logger.info(
                "EXTEND Event - Entity Key: %s, New Expiration: %s",
                extend.entity_key.as_hex_string(),
                extend.new_expiration_block,
            ),
        )

        logger.info("WebSocket event listener started. Press Ctrl+C to stop...")

        # Keep the listener running
        try:
            await shutdown_event.wait()
        except asyncio.CancelledError:
            logger.info("Event listening cancelled")

    except Exception:
        logger.exception("Failed to start WebSocket listener")
    finally:
        if client:
            try:
                await client.disconnect()
                logger.info("Disconnected from client")
            except Exception:
                logger.exception("Error during disconnect")


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
        if args.method == "websocket":
            asyncio.run(listen_with_websocket_subscription(args.instance))
        else:
            asyncio.run(listen_to_contract_events(args.instance))
    except KeyboardInterrupt:
        logger.info("Event listener stopped by user")
    except Exception:
        logger.exception("Event listener failed")
        sys.exit(1)


if __name__ == "__main__":
    main()
