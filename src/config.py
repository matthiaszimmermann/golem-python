"""Configuration constants for the Golem Python client."""

# Network Configuration
LOCALHOST = "host.docker.internal"

NETWORK_URLS = {
    "local": {
        "rpc": f"http://{LOCALHOST}:8545",
        "ws": f"ws://{LOCALHOST}:8545",
    },
    "kaolin": {
        "rpc": "https://kaolin.holesky.golem-base.io/rpc",
        "ws": "wss://kaolin.holesky.golem-base.io/rpc/ws",
    },
    "warsaw": {
        "rpc": "https://ethwarsaw.holesky.golemdb.io/rpc",
        "ws": "wss://ethwarsaw.holesky.golemdb.io/rpc/ws",
    },
}

# Default Configuration
DEFAULT_NETWORK = "local"
DEFAULT_LOG_LEVEL = "info"

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
