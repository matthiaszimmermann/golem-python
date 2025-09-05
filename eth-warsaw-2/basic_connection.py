import asyncio
import os

from dotenv import load_dotenv
from golem_base_sdk import GolemBaseClient

# Load environment variables
load_dotenv()
# Configuration
PRIVATE_KEY = os.getenv(
    "PRIVATE_KEY", "0x0000000000000000000000000000000000000000000000000000000000000001"
)
RPC_URL = os.getenv("RPC_URL", "https://ethwarsaw.holesky.golemdb.io/rpc")
WS_URL = os.getenv("WS_URL", "wss://ethwarsaw.holesky.golemdb.io/rpc/ws")


async def create_client():
    try:
        # Convert hex string to bytes
        private_key_hex = PRIVATE_KEY.replace("0x", "")
        private_key_bytes = bytes.fromhex(private_key_hex)
        # Create client
        client = await GolemBaseClient.create_rw_client(
            rpc_url=RPC_URL, ws_url=WS_URL, private_key=private_key_bytes
        )
        print("Connected to Golem DB via ETHWarsaw!")
        # Get owner address
        owner_address = client.get_account_address()
        print(f"Connected with address: {owner_address}")

        # Get and check client account balance
        balance = await client.http_client().eth.get_balance(owner_address)
        print(f"Client account balance: {balance / 10**18} ETH")

        if balance == 0:
            print(
                "Warning: Account balance is 0 ETH. Please acquire test tokens from the faucet."
            )

        return client
    # in case of an exception/error just return None
    except Exception as e:
        print(f"Error during client creation/connection (returning None): {e}")
        return None


async def main():
    client = await create_client()
    if isinstance(client, GolemBaseClient):
        await client.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
