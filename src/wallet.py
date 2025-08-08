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

# fetch private key from the wallet file: wallet_json = json.load(f)
# to obtain decrypted key: account.decrypt(wallet_json, password)
