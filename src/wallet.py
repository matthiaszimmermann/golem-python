import getpass
import json
import sys
from pathlib import Path

from eth_account import Account

WALLET_PATH = Path("wallet.json")

if WALLET_PATH.exists():
    print(f'File "{WALLET_PATH}" already exists. Aborting.')
    sys.exit(0)

password = getpass.getpass("Enter wallet password: ")
account = Account.create()
encrypted = account.encrypt(password)

with WALLET_PATH.open("w") as f:
    json.dump(encrypted, f)

print(f"Account address: {account.address}")
print(f"Wallet file: {WALLET_PATH}")

# fetch private key from the wallet file
# with WALLET_PATH.open("r") as f:
#     wallet_json = json.load(f)
#     print(f"\nWallet json: {wallet_json}")
#     account_key = Account.decrypt(wallet_json, password)
#     print(f"Account private key: 0x{account_key.hex()}")
