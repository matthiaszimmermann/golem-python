"""Creates a new Ethereum wallet (JSON format)."""

import getpass
import json
import sys
from pathlib import Path

from eth_account import Account

WALLET_PATH = Path("wallet.json")
KEY_PATH = Path("private.key")

if WALLET_PATH.exists():
    print(f'File "{WALLET_PATH}" already exists. Aborting.')
    sys.exit(0)

account = None

if KEY_PATH.exists():
    print(f'Using "{KEY_PATH}" for account creation.')
    with KEY_PATH.open("rb") as key_file:
        key_bytes = key_file.read(32)
        account = Account.from_key(key_bytes)
else:
    account = Account.create()

password = getpass.getpass("Enter wallet password: ")
encrypted = account.encrypt(password)

with WALLET_PATH.open("w") as f:
    json.dump(encrypted, f)

print(f"Account address: {account.address}")
print(f"Wallet file: {WALLET_PATH}")

# fetch private key from the wallet file: wallet_json = json.load(f)
# to obtain decrypted key: account.decrypt(wallet_json, password)
