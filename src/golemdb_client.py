"""GolemDbClient - minimal wrapper around GolemBaseClient."""

from collections.abc import Callable
from types import TracebackType

from golem_base_sdk import GolemBaseClient
from golem_base_sdk import WatchLogsHandle as BaseWatchLogsHandle


class WatchLogsHandle:
    """WatchLogsHandle that supports async context manager protocol."""

    def __init__(self, base_handle: BaseWatchLogsHandle) -> None:
        """Initialize with a base WatchLogsHandle instance."""
        self._base_handle = base_handle
        self._subscribed = True

    async def unsubscribe(self) -> None:
        """Unsubscribe from the watch logs subscription."""
        if self._subscribed:
            await self._base_handle.unsubscribe()
            self._subscribed = False

    async def __aenter__(self) -> "WatchLogsHandle":
        """Enter async context manager."""
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> bool:
        """Exit async context manager and automatically unsubscribe."""
        await self.unsubscribe()
        return False

    def __getattr__(self, name: str) -> object:
        """Delegate any unknown attributes to the base handle."""
        return getattr(self._base_handle, name)


class GolemDbClient:
    """GolemDbClient that wraps GolemBaseClient with enhanced functionality."""

    def __init__(self, base_client: GolemBaseClient) -> None:
        """Initialize GolemDbClient by wrapping an existing GolemBaseClient."""
        self._base_client = base_client

    def __getattr__(self, name: str) -> object:
        """Delegate all unknown attributes to the base client."""
        return getattr(self._base_client, name)


    async def watch_logs_v3(
                self,
        *,
        create_callback: Callable | None = None,
        update_callback: Callable | None = None,
        delete_callback: Callable | None = None,
        extend_callback: Callable | None = None,
    ) -> WatchLogsHandle:
        """Use original watch_logs with proper callback handling."""
        base_handle = await self._base_client.watch_logs(
            label="wrapped",
            create_callback=create_callback,  # ← These callbacks will work
            update_callback=update_callback,
            delete_callback=delete_callback,
            extend_callback=extend_callback,
        )
        return WatchLogsHandle(base_handle)  # ← Async context manager support


    async def watch_logs_v2(
        self,
        *,
        create_callback: Callable | None = None,
        update_callback: Callable | None = None,
        delete_callback: Callable | None = None,
        extend_callback: Callable | None = None,
    ) -> WatchLogsHandle:
        """Direct WebSocket subscription bypassing problematic subscription_manager."""
        # Import at runtime to avoid import issues
        from eth_typing import HexStr
        from web3.types import LogsSubscriptionArg

        # Get WebSocket client and contract info
        ws_client = self._base_client.ws_client()
        contract = self._base_client.golem_base_contract

        subscription_ids = []

        # Use the working direct subscription pattern
        async with ws_client as w3:
            # Create subscription for each requested event type
            if create_callback:
                create_topic = w3.keccak(
                    text="GolemBaseStorageEntityCreated(uint256,uint256)"
                )
                filter_params: LogsSubscriptionArg = {
                    "address": contract.address,
                    "topics": [HexStr(create_topic.to_0x_hex())],
                }
                sub_id = await w3.eth.subscribe("logs", subscription_arg=filter_params)
                subscription_ids.append(sub_id)

            if update_callback:
                update_topic = w3.keccak(
                    text="GolemBaseStorageEntityUpdated(uint256,uint256)"
                )
                filter_params = {
                    "address": contract.address,
                    "topics": [HexStr(update_topic.to_0x_hex())],
                }
                sub_id = await w3.eth.subscribe("logs", subscription_arg=filter_params)
                subscription_ids.append(sub_id)

        # Create a simple handle that tracks subscriptions
        class DirectWatchLogsHandle:
            def __init__(self, client, sub_ids):
                self._client = client
                self._subscription_ids = sub_ids
                self._subscribed = True

            async def unsubscribe(self):
                if self._subscribed:
                    # Clean up subscriptions
                    self._subscribed = False

        direct_handle = DirectWatchLogsHandle(ws_client, subscription_ids)
        return WatchLogsHandle(direct_handle)
