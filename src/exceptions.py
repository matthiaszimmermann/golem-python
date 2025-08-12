"""Custom exceptions for the Golem Python client."""


class GolemClientError(Exception):
    """Base exception for Golem client errors."""


class WalletDecryptionError(GolemClientError):
    """Raised when wallet decryption fails."""


class ClientConnectionError(GolemClientError):
    """Raised when client cannot connect to network."""


class EventListenerError(GolemClientError):
    """Raised when event listener encounters an error."""
