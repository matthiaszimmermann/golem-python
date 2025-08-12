"""Configuration constants for the Golem Python client."""

# Network Configuration
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

# Default Configuration
DEFAULT_INSTANCE = "local"
DEFAULT_LOG_LEVEL = "info"
LISTENER_LOG_LEVEL = "info"
CLIENT_LOG_LEVEL = "warn"

# Logging Configuration
LOG_LEVELS = {"info": "INFO", "warn": "WARNING", "error": "ERROR"}

# Exit Codes
ERR_WALLET_PASSWORD = 1
ERR_CLIENT_CONNECT = 2
ERR_CLIENT_DISCONNECT = 3
ERR_LISTENER = 4

# Chat Configuration
QUIT_COMMAND = "quit"
CHAT_WIDTH = 80

# Entity Annotations
VERSION_KEY = "version"
COLLECTION_KEY = "collection"
MESSAGES_COLLECTION = "message"
USERS_COLLECTION = "users"
