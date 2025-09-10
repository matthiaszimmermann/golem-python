# Golem DB

Golem DB is a flexible, permissioned entity storage and management system designed for decentralized and distributed applications. It provides a robust model for creating, updating, querying, and managing entities, each of which can store binary data, structured annotations, and rich metadata. The system is built to support both simple and advanced use cases, from personal asset management to complex multi-party workflows.

## Benefits of Golem DB

Golem DB radically reduces onchain storage costs and complexity, enabling decentralized apps to manage rich, permissioned data without relying on centralized cloud providers.

Golem DB aspires to lower storage costs by 100x to 1000x over current L2 evm chains.
This enables new decentralized use cases that are currently implemented using centralized storage services like AWS and Azure.

### Data Architecture with Golem DB:

| Data Type                      | Onchain              | Golem DB                | Cloud                            | Golem Benefits    |
|--------------------------------|----------------------|-------------------------|----------------------------------|-------------------|
| Cryptographic proofs & anchors | Yes (minimal hashes) | No                      | No                               | -                 |
| Dynamic decentralized data     | No                   | Yes                     | No                               | Lower costs       |
| Application critical state     | No                   | Yes (with expiry)       | No                               | Higher resilience |
| User metadata & annotations    | No                   | Yes                     | Optional (Backup/analytics)      | Higher resilience |
| Large binary assets (files)    | No                   | Optional, selective     | Yes (bulky data)                 | -                 |
| Historical archives & logs     | No                   | Yes (short-medium term) | Yes (long-term archival storage) | -                 |

### Golem DB Use Cases

The list below provides a number of use cases that directly benefit from Golem DB features.
These use cases go beyond generic storage to demonstrate how Golem DB's model supports efficient, secure, and scalable decentralized apps managing ephemeral or consumable data naturally.

1. **Messaging and Communication Systems**
    - Data Type: Messages, chats, multimedia that expire after defined retention time (e.g., 7 days, 1 month).
    - Use of Golem DB: Store encrypted messages and metadata with expiry to ensure automatic deletion after retention period, maintaining user privacy and compliance.
    - Value Added
        - Decentralized, censorship-resistant message storage with built-in expiry.
        - Avoids permanent on-chain data bloat.
        - Ensures data automatically pruned, reducing storage overhead for nodes and users.
1. **DeFi Transaction States & Cross-Chain Transfers**
    - Data Type: Temporary transaction states, proofs of fulfillment, order statuses that only need to persist until transactions or cross-chain transfers finalize.
    - Use of Golem DB: Track pending or in-flight transaction metadata, signatures, and event annotations with expiry aligned to transaction settlement times.
    - Value Added
        - Reduces reliance on expensive permanent onchain logs.
        - Enables state pruning once transfers or trades settle, lowering gas and storage costs.
        - Provides verifiable, audit-ready data throughout transaction lifecycles.
1. **Consumable and Time-Limited Virtual Goods**
    - Data Type: Virtual consumable assets (e.g., limited-use game items, event tickets) that exist only for a specified duration or until consumed.
    - Use of Golem DB: Store ownership, usage state, and metadata with expiry aligned to item lifespan or event date.
    - Value Added
        - Automatically cleans up expired/used assets.
        - Avoids accumulation of obsolete onchain state.
        - Supports decentralized virtual economy with trustless lifecycle management.
1.  **Subscription and License Management**
    - Data Type: Licenses, subscriptions, or permissions valid only for limited periods.
    - Use of Golem DB: Manage license metadata, proof of entitlement, and usage records with expiry tied to subscription length.
    - Value Added
        - Simplifies access control by enforcing expiry automatically.
        - Enhances user privacy by pruning old license data.
        - Allows flexible renewal and revocation workflows, all decentralized.
1. **Event-Driven Data & Temporary Workflows**
    - Data Type: Workflow states, event logs, or sensor data valid during active operations that expire post-completion.
    - Use of Golem DB: Store incremental workflow or event metadata with expiry as workflows complete or events become irrelevant.
    - Value Added
        - Keeps active data verifiable and decentralized while preventing indefinite storage.
        - Optimizes resource use for long-running decentralized applications.
        - Facilitates auditability during critical active periods.

**Benefit Summary**
- Massive Cost Savings: Store and manage data at 100x–1000x lower cost than current L2 EVM chains.
- Decentralized by Default: Eliminate reliance on AWS, Azure, or other centralized storage for critical state and metadata.
- Rich Data Model: Support for binary data, structured annotations, and metadata—all with fine-grained permissions.
- Auditability & Security: All state changes are cryptographically signed and fully auditable, both onchain and offchain.
- Flexible Expiry & Retention: Built-in support for data expiry (BTL), short/medium-term storage, and seamless offchain archival.
- Easy Integration: Simple, type-safe API and event model for rapid prototyping and production use.


## Entities

Entities in Golem DB are governed by a dual-role model: every entity has an owner and an operator, each with clearly defined permissions. The owner controls transfer and deletion, while the operator manages data, annotations, and entity lifetime. All state changes are cryptographically signed, ensuring strong guarantees of authenticity, integrity, and auditability—both on-chain and off-chain.

The API is designed for clarity, type safety, and extensibility. It supports efficient partial data access, dynamic querying, sorting, and pagination, as well as historical queries by block number. Error handling is explicit and minimal, making it easy to integrate Golem DB into a wide range of applications and services.

## Quick Start

The following quick start example demonstrates how easy it is to create, update, fetch, and delete entities using Golem DB. With sensible defaults for all optional fields, you can get up and running with just a few lines of code—perfect for rapid prototyping or exploring the API’s core features.

```python
from golemdb import Client, EntityField

# Initialize the client (details may vary depending on your setup)
client = Client(RPC_URL, wallet, password)

# Create a new entity (only data fields used here)
result = client.create(data=b"Hello, Golem!")
print(f"Created entity: {result.entity_key}")

# Fetch the entity metadata only
result = client.get(
    entity_key,
    fields=[EntityField.METADATA]
)
print(f"Fetched entity metadata: {result.entity.metadata}")

# Update/amend the entity with optional annotations
client.update(
    entity_key=entity_key,
    annotations={"purpose": "demo", "version": 1}
)

# Fetch the full entity (default: all fields)
result = client.get(entity_key)
print(f"Full entity: {result.entity}")

# Delete the entity
result = client.delete(entity_key)
print(f"Entity deleted: {result.entity_key}")

# Check if the entity still exists
exists_result = client.exists(entity_key)
print(f"Entity exists after delete: {exists_result.exists}")
```

The following example demonstrates how to efficiently create multiple entities in a single batch operation using the process method, and then retrieve a filtered subset of those entities with the flexible select query. This approach is ideal for scenarios where you need to onboard or update many records at once and then quickly access only those matching specific criteria.

```python
from golemdb import Client, EntityField

# Initialize the client (details may vary depending on your setup)
client = Client(RPC_URL, wallet, password)

# Batch create multiple entities
batch_result = client.process(
    creates=[
        CreateOp(data=b"Alpha", annotations={"type": "demo", "group": "A"}),
        CreateOp(data=b"Beta", annotations={"type": "demo", "group": "B"}),
        CreateOp(data=b"Gamma", annotations={"type": "test", "group": "A"}),
    ]
)
print("Created entities:" [res.entity_key for res in batch_result.creates])

# Query for all entities with annotation type: "demo"
select_result = db.select('type = "demo"')
print('Query results (type="demo"):', [e.metadata.entity_key for e in select_result.entities])

# Query for all entities with annotation type: "test" and group: "A"
select_result = db.select('type = "test" && group = "A"')
print('Query results (type="demo" && group = "A"):', [e.metadata.entity_key for e in select_result.entities])
```

You can easily subscribe to entity lifecycle events using the subscribe method. For example, to listen for entity creation events and print all available information:

```python
from golemdb import Client, EntityField

# Callback method that is called whenever a new entity is created.
def handle_created(event: EntityCreated) -> None:
    print("Entity created:")
    print(f"  entity_key: {event.entity_key}")
    print(f"  owner: {event.owner}")
    print(f"  operator: {event.operator}")
    print(f"  expires_at: {event.expires_at}")
    print(f"  version: {event.version}")
    print(f"  data_hash: {event.data_hash.hex()}")
    print(f"  annotations_hash: {event.annotations_hash.hex()}")

# Initialize the client (details may vary depending on your setup)
client = Client(RPC_URL, wallet, password)

# Subscribe to creation events
handle: SubscriptionHandle = await client.subscribe(
    label="creation-watcher",
    on_created=handle_created
)

# Trigger a entity creation callback
client.create(data=b"Hello World!")

# ... later, to clean up:
await handle.unsubscribe()
await client.disconnect()
```

## Entity Role Model: Owner & Operator

Entities have two distinct roles: Owners and operators.
This distinction is vital to support many valuable use cases.

1. NFTs and Digital Collectibles
- Unique digital assets (art, music, in-game items, domain names) that can be bought, sold, or gifted.
- Ownership: The core value is the ability to transfer, trade, or sell the asset.
2. IoT Device Ownership and Delegation
- Smart devices (routers, sensors, vehicles) whose control and management rights must be transferred (e.g., resale, leasing, or end-of-life).
- Ownership: Ensures secure handover and prevents unauthorized access after transfer.
3. Supply Chain Assets and Provenance
- Physical goods, containers, or batches tracked onchain as they move between manufacturers, shippers, warehouses, and retailers.
- Ownership: Each handoff must be cryptographically recorded to ensure provenance and accountability.
4. Real Estate and Property Titles
- Onchain representation of property deeds, leases, or rental agreements.
- Ownership: Legal compliance and market liquidity depend on secure, auditable transfer.
5. Intellectual Property and Patents
- Digital representation of patents, trademarks, or copyrights.
Ownership: Licensing, sale, or inheritance of IP requires clear, enforceable transfer.
6. Digital Twin and Asset Tokenization
- Onchain tokens representing real-world assets (machinery, vehicles, energy credits).
- Ownership: Enables fractional ownership, secondary markets, and regulatory compliance.
7. Decentralized Finance (DeFi) Positions
- Ownership of liquidity positions, vaults, or derivatives.
- Ownership: Enables composability, trading, and portfolio management.

### Owner

- The address that owns the entity.
- Can always transfer ownership to another address.
- Can delete the entity.
- Cannot update data/annotations or extend the entity.
- Cannot transfer operator (see below).

### Operator

- The address with management rights over the entity.
- Can update data and annotations.
- Can extend the entity’s lifetime.
- Can transfer operator rights.
- Can delete the entity.
- Cannot transfer ownership.

### Permission Table

| Action                  | Owner | Operator | Notes                                         |
|-------------------------|:-----:|:--------:|-----------------------------------------------|
| Create                  |  Yes  |   Yes    | Both can create entities                      |
| Update Data/Annotations |   No  |   Yes    | Only operator can update                      |
| Extend Lifetime         |   No  |   Yes    | Only operator can extend                      |
| Delete                  |  Yes  |   Yes    | Both can delete                               |
| Transfer Ownership      |  Yes  |    No    | Only owner can transfer                       |
| Transfer Operator       |   No  |   Yes    | Only operator can transfer                    |
| Make Immutable          |   No  |   Yes    | Special case for operator transfer, by setting to null/burn address |

Newly created entities assign the signer to both owner and operator.
This is sufficient for many simple use cases.

More sophisticated use cases will need to then use `transfer` (or `update` for opererator transfers) to move to the desired role model.

The creation of immutable entities may be achieved by setting the operator to a burn address (e.g., 0x000...1).
Once immutable, neither owner nor operator can update or extend the entity, but the owner can still transfer or delete (if allowed).

### Counter Arguments

**Separate Ownership Not Needed**

All logic and data can live on the Golem DB chain.
Single owner per entity, all updates and verification handled offchain or on the Golem DB chain.

Ideal for identity, reputation, static records, and non-transferable data.

In addition: Offline Verification with separate owner and operator is a headache.

**Separate Ownership Needed**

Hybrid approach:
Smart contract on mainnet/L2 manages ownership, transfer, and permissions.

Pointer/reference in the contract to the corresponding Golem DB entity (e.g., entity key or hash).

Extensive data and metadata stored and managed on the Golem DB chain for scalability and flexibility.
This enables trustless, composable, and auditable ownership, while keeping rich data offchain.
This hybrid model gives you the best of both worlds:

Simplicity and efficiency for most use cases.
Full composability, security, and scalability for advanced, asset-centric scenarios.


## Entity Elements

### Current Elements

| Element       | Set on Create | Updatable    | Who Can Set/Change?             | Notes                                         |
|---------------|:-------------:|:------------:|---------------------------------|-----------------------------------------------|
| `entity_key`  | Yes           | No           | System/Contract                 | Unique identifier, auto-generated or derived  |
| `data`        | Yes           | Yes          | Operator                        | Main payload, updatable by operator           |
| `annotations` | Yes           | Yes          | Operator                        | Key-value metadata, updatable by operator     |
| `owner`       | Yes (default: signer) | Yes (via transfer) | Owner (transfer_owner)       | Can be transferred after creation  |
| `expires_at`  | Yes (via btl) | Yes (extend) | Operator                        | Set on create, can be extended by operator    |

### Elements already discussed to be added

| Element       | Set on Create | Updatable    | Who Can Set/Change?             | Notes                                         |
|---------------|:-------------:|:------------:|---------------------------------|-----------------------------------------------|
| `operator`    | Yes (default: signer) | Yes (via transfer) | Operator (transfer_operator) | Can be transferred after creation  |

### Elements to be discussed to be added

| Element               | Set on Create | Updatable    | Who Can Set/Change? | Notes                                         |
|-----------------------|:-------------:|:------------:|---------------------|-----------------------------------------------|
| `created_at`          | Yes (auto)    | No           | System/Contract     | Block number at creation, immutable           |
| `updated_at`          | Yes (auto)    | Yes (auto)   | System/Contract     | Updated on each change, auto-managed          |
| `previous_owner`      | Yes (auto)    | Yes (auto)   | System/Contract     | Updated on each owner change, auto-managed    |
| `previous_operator`   | Yes (auto)    | Yes (auto)   | System/Contract     | Updated on each operator change, auto-managed |
| `operator_version`    | Yes (auto)    | Yes (auto)   | System/Contract     | Incremented on each update including the operator, auto-managed |
| `owner_version`       | Yes (auto)    | Yes (auto)   | System/Contract     | Incremented on each update including the owner, auto-managed |
| `owner_signature`     | Yes (auto)    | Yes (auto)   | Previous owner      | Proves authorization of ownership transfer    |
| `operator_signature`  | Yes (auto)    | Yes (auto)   | Previous operator   | Proves authorization of operator-related changes (e.g., data, annotations, expiry, operator transfer)   |

**Previous Owner**

Records the previous owner.
After the creation of a new entity the owner and previous owner both contain the signer address of the create transaction.
When the current owner transfers ownership to a new owner, the previous owner is set to the signer of the transfer transaction, the owner address is set to the new owner of the entity.

**Previous Operator**

Records the previous operator.
After the creation of a new entity the operator and previous operator both contain the signer address of the create transaction.
When the current operator transfers ownership to a new operator, the previous operator is set to the signer of the transfer transaction, the operator address is set to the new operator of the entity.

**Version**

Any change in data, annotations, lifetime, owner, operator increases the version.
It ensures that signatures are always bound to a specific state of the entity, guaranteeing that off-chain consumers can verify the exact version of the data they are trusting.

**Owner Signature**

A cryptographic signature created by the owner of an entity.
It serves as proof that the owner has authorized changes to owner-controlled fields.
Specifically, the signed payload must include the previous_owner, the new owner, and the version of the entity (version after the ownership change).

For ownership transfers, the signature must be generated by the previous owner, ensuring that only the legitimate owner can approve such changes.
The owner signature is only updated for ownership changes.

This mechanism provides strong guarantees of authenticity and prevents unauthorized modifications to ownership.

**Operator Signature**

A cryptographic signature created by the operator of an entity.
It serves as proof that the operator has authorized changes to operator-controlled fields.

Specifically, the signed payload must include the previous_operator, the new operator (if applicable), all operator-controlled fields (such as data, annotations, and expires_at), and the version of the entity (version after the change). For operator transfers, the signature must be generated by the previous operator, ensuring that only the legitimate operator can approve such changes. The operator signature is only updated when operator-controlled fields are changed.

This mechanism provides strong guarantees of authenticity and prevents unauthorized modifications to operator-managed aspects of the entity.

### Offchain Verification

Offchain verification allows any party to independently confirm the authenticity and integrity of an entity’s data without relying on the Golem data chain.
This is achieved through cryptographic signatures provided by the owner and operator, which prove that all changes to the entity were authorized by the correct parties.

To verify an entity offchain, a verifier must obtain the full entity state, including all relevant metadata fields, the current and previous owner and operator addresses, the version, and both the owner_signature and operator_signature.
The verifier then reconstructs the signed payloads for each signature, ensuring that all required fields (such as previous/current owner or operator, data, annotations, expires_at, and version) are included exactly as they were at the time of signing.

Using the public keys of the previous owner and operator, the verifier checks that the signatures are valid for the given payloads.
This process guarantees that no unauthorized changes have been made to the entity’s state and that each transition (such as ownership or operator changes) was explicitly approved by the correct party.

If any signature fails to verify, or if the entity state does not match the signed payloads, the entity data must be considered untrustworthy.

Likely need to consider alternatives as complexity and practicability for verification by smart contracts does not seem practical...

## Client API

### Types

```python
from typing import NamedTuple, List, Optional, Dict, Union, Any
from enum import Enum, auto

from eth_typing import ChecksumAddress, HexStr

#--- Types --------------------------------------#
class EntityKey(str):
    pass
    """Valid length and format is required."""

class EntityField(Enum):
    DATA = auto()
    ANNOTATIONS = auto()
    METADATA = auto()

class Metadata(NamedTuple):
    entity_key: EntityKey
    owner: ChecksumAddress
    operator: ChecksumAddress
    expires_at: int
    created_at: int
    updated_at: int
    previous_owner: ChecksumAddress
    previous_operator: ChecksumAddress
    owner_version: int
    operator_version: int
    owner_signature: bytes
    operator_signature: bytes

Annotations = Dict[str, Union[str, int]]

class Entity(NamedTuple):
    data: Optional[bytes] = None
    annotations: Optional[Annotations] = None
    metadata: Metadata

class OrderField(Enum):
    ASC = auto()
    DESC = auto()

class SortSpec(NamedTuple):
    field: str
    order: OrderField

class Cursor(str):
    """
    Opaque cursor field to specify the 1st record of the next page to be returned.
    Defaults to the 1st record of the full entity list.
    """
    pass

class Pagination(NamedTuple):
    limit: int = 100
    cursor: Optional[Cursor] = None

class CreateOp(NamedTuple):
    data: Optional[bytes] = None
    annotations: Optional[Annotations] = None
    btl: Optional[int] = None
    operator: Optional[ChecksumAddress] = None

class UpdateOp(NamedTuple):
    entity_key: EntityKey
    data: Optional[bytes] = None
    annotations: Optional[Annotations] = None
    btl: Optional[int] = None
    new_operator: Optional[ChecksumAddress] = None

class TransferOp(NamedTuple):
    entity_key: EntityKey
    new_owner: ChecksumAddress

class DeleteOp(NamedTuple):
    entity_key: EntityKey

class CreateResult(NamedTuple):
    """
    Both block_number and tx_hash are included for convenience and consistency.
    The block number is provided directly to avoid extra lookups, but can always be derived from the transaction hash if needed.
    """
    entity_key: EntityKey
    success: bool
    block_number: int
    tx_hash: HexStr

class UpdateResult(NamedTuple):
    entity_key: EntityKey
    success: bool
    block_number: int
    tx_hash: HexStr

class TransferResult(NamedTuple):
    entity_key: EntityKey
    success: bool
    block_number: int
    tx_hash: HexStr

class DeleteResult(NamedTuple):
    entity_key: EntityKey
    success: bool
    block_number: int
    tx_hash: HexStr

class ProcessResult(NamedTuple):
    creates: List[CreateResult]
    updates: List[UpdateResult]
    deletes: List[DeleteResult]

class ExistsResult(NamedTuple):
    exists: bool
    block_number: int

class GetResult(NamedTuple):
    entity: Entity
    block_number: int

class CountResult(NamedTuple):
    count: int
    block_number: int

class SelectResult(NamedTuple):
    """
    Provides matching results as a sorted list.
    If not matching entities are found, an empty list is returned.
    """
    entities: List[Entity]
    block_number: int
    next_cursor: Optional[Cursor] = None

```

### Event Handling

```python

class EntityCreated(NamedTuple):
    entity_key: EntityKey
    owner: ChecksumAddress
    operator: ChecksumAddress
    expires_at: int
    version: int
    data_hash: HexStr
    annotations_hash: HexStr

class EntityUpdated(NamedTuple):
    entity_key: EntityKey
    operator: ChecksumAddress
    version: int
    data_hash: HexStr
    annotations_hash: HexStr

class EntityDeleted(NamedTuple):
    entity_key: EntityKey
    by: ChecksumAddress

class EntityExtended(NamedTuple):
    entity_key: EntityKey
    operator: ChecksumAddress
    old_expires_at: int
    new_expires_at: int

class EntityExpired(NamedTuple):
    entity_key: EntityKey

class EntityOwnershipTransferred(NamedTuple):
    entity_key: EntityKey
    previous_owner: ChecksumAddress
    new_owner: ChecksumAddress
    version: int

class EntityOperatorTransferred(NamedTuple):
    entity_key: EntityKey
    previous_operator: ChecksumAddress
    new_operator: ChecksumAddress
    version: int

class SubscriptionHandle:
    def label(self) -> str:
        """
        Return the label provided when creating the subscription.
        """

    async def unsubscribe(self) -> None:
        """
        Unsubscribe from the entity events for this subscription.
        After calling this method, no further event callbacks will be invoked.
        """
```

### Client Error Handling

```python
class EntityError(Exception):
    """Base exception for all entity-related errors."""

class EntityNotFoundError(EntityError):
    """Raised when an entity does not exist for the given key."""

class PermissionDeniedError(EntityError):
    """Raised when the caller does not have permission for the operation."""

class InvalidInputError(EntityError):
    """Raised when input arguments are invalid."""

```

### Methods (Create, Update, Delete)

```python
def create(
    self,
    data: bytes,
    annotations: Optional[Annotations] = None,
    btl: int = 60,
    operator: ChecksumAddress = None
) -> EntityKey:
    """
    Create a new entity.
    Optionally specify an operator (manager/issuer).
    Signer gets owner rights.
    If no operator is specified, signer also gets operator rights.
    Non-permissioned.
    Raises InvalidInputError for invalid arguments.
    """

def update(
    self,
    entity_key: EntityKey,
    data: bytes = None,
    annotations: Optional[Annotations] = None,
    btl: int = None,
    operator: ChecksumAddress = None
) -> bool:
    """
    Update data, annotations, transfer operator role, or extend the entitys lifetime.
    Arguments that are set to None will not lead to any changes.
    Permissioned. Only allowed for current operator.
    Raises EntityNotFoundError if no such entity exists.
    Raises PermissionDeniedError if signer is not operator.
    Raises InvalidInputError for invalid arguments.
    """

def transfer(self, entity_key: EntityKey, new_owner: ChecksumAddress) -> bool:
    """
    Transfer ownership role.
    Permissioned. Only allowed for current owner.
    Raises EntityNotFoundError if no such entity exists.
    Raises PermissionDeniedError if signer is not owner.
    Raises InvalidInputError for invalid arguments.
    """

def delete(self, entity_key: EntityKey) -> bool:
    """
    Delete the entity.
    Permissioned. Only allowed for current owner or operator.
    Raises EntityNotFoundError if no such entity exists.
    Raises PermissionDeniedError if signer is not owner or operator.
    Raises InvalidInputError for invalid arguments.
    """

def process(
    self,
    creates: List[CreateOp] = [],
    updates: List[UpdateOp] = [],
    transfers: List[TransferOp] = [],
    deletes: List[DeleteOp] = []
) -> ProcessResult:
    """
    Batch process multiple entity operations (create, update, delete) in a single transaction.

    - `creates`: List of CreateOp objects (same fields as the `create` method).
    - `updates`: List of UpdateOp objects (same fields as the `update` method).
    - `transfers`: List of TransferOp objects (same fields as the `transfer` method).
    - `deletes`: List of DeleteOp objects (entity_key only).

    Each entity key may only be used once over all specified operations.
    I.e. using an entity key in multiple update operators or using the same entity key in an update and/or a transfer and delete operation is not supported.
    Returns a ProcessResult containing lists of result objects for each operation type.

    All operations are executed atomically: either all succeed, or none are applied.
    Raises InvalidInputError for invalid arguments.
    Raises EntityNotFoundError or PermissionDeniedError for failed operations.
    """

```

### Methods (Read)

```python
def exists(self, entity_key: EntityKey, block_number: Optional[int] = None) -> ExistsResult:
    """
    Return True if an entity exists for the specified entity key, False otherwise.
    For block number None (default) the latest avaliable block number is used.
    Only block_numbers covering the last n minutes are supported.
    Raises InvalidInputError for invalid arguments.
    """

def get(
    self,
    entity_key: EntityKey,
    fields: Optional[List[EntityField]] = [EntityField.METADATA],
    block_number: Optional[int] = None
) -> GetResult:
    """
    Fetch single entity by entity key.
    Optionally specify which entity fields to retrieve.
    The default provides entity metadata fields.
    Available fields are "data", "annotations", and "metadata".
    For block number None (default) the latest avaliable block number is used.
    Only block_numbers covering the last n minutes are supported.
    Raises EntityNotFoundError if no such entity exists.
    Raises InvalidInputError for invalid arguments.
    """

def count(self, query: str, block_number: int = None) -> CountResult:
    """
    Count matching entities for specified query and block_number.
    For block number None (default) the latest block number available to the client connection is used.
    Only block_numbers covering the last n minutes are supported.
    Raises InvalidInputError for invalid arguments.
    """

def select(
    self,
    query: str,
    fields: Optional[List[EntityField]] = None,
    sort: Optional[List[SortSpec]] = None,
    pagination: Optional[Pagination] = None,
    block_number: Optional[int] = None
) -> SelectResult:
    """
    Fetch entities by annotation fields and metadata elements like $entity_key, $owner, etc.
    Optionally specify which entity fields to retrieve.
    The default populates all available fields.
    Available fields are "data", "annotations", and "metadata".
    Optionally specify sort criteria.
    The default sorts accorting to ascending entity keys.
    For block number None (default) the latest block number available to the client connection is used.
    Only block_numbers covering the last n minutes are supported.
    Raises InvalidInputError for invalid arguments.
    """

```

### Methods (Event Subscription)

```python
async def subscribe(
    self,
    *,
    label: str,
    on_created: Optional[Callable[[EntityCreated], None]] = None,
    on_updated: Optional[Callable[[EntityUpdated], None]] = None,
    on_extended: Optional[Callable[[EntityExtended], None]] = None,
    on_ownership_transferred: Optional[Callable[[EntityOwnershipTransferred], None]] = None,
    on_operator_transferred: Optional[Callable[[EntityOperatorTransferred], None]] = None,
    on_deleted: Optional[Callable[[EntityDeleted], None]] = None,
    on_expired: Optional[Callable[[EntityExpired], None]] = None,
) -> SubscriptionHandle:
    """
    Subscribe to entity events.

    Register a callback for any combination of:
      - on_created
      - on_updated
      - on_extended
      - on_ownership_transferred
      - on_operator_transferred
      - on_deleted
      - on_expired

    Each callback receives a strongly-typed event object matching the Solidity event.
    Returns a SubscriptionHandle for unsubscribing.
    """

```

### Methods (Web3 Low Level)

```python
@property
def http_client(self) -> GolemBaseHttpClient:
    """Return the HTTP Web3 client."""

@property
def ws_client(self) -> AsyncWeb3:
    """Return the HTTP WS client."""

def is_connected(self) -> bool
    """
    Returns True if the client is connected with the RPC node, False otherwise.
    """

def get_account_address(self) -> ChecksumAddress:
    """
    Returns the connected account address.
    """

def get_balance(self) -> int:
    """
    Returns the balance of the connected account address.
    The balance must be positive for state changing methods.
    """

def reconnect_ws(self) -> bool
    """
    Attempt to re-connect a failed WS connection.
    Returns True if connection is successfully re-created, False otherwise.
    """

```

## Solidity (Entity related Events)

```solidity
event EntityCreated(
    bytes32 indexed entityKey,
    address indexed operator,
    address indexed owner,
    uint256 expiresAt,
    uint256 version,
    bytes32 dataHash,         // keccak256 hash of the initial data
    bytes32 annotationsHash   // keccak256 hash of the initial annotations
);

event EntityUpdated(
    bytes32 indexed entityKey,
    address indexed operator,
    uint256 version,
    bytes32 dataHash,         // keccak256 hash of the new data (or zero if unchanged)
    bytes32 annotationsHash   // keccak256 hash of the new annotations (or zero if unchanged)
);

event EntityExtended(
    bytes32 indexed entityKey,
    address indexed operator,
    uint256 oldExpiresAt,
    uint256 newExpiresAt,
    uint256 version
);

event EntityOwnershipTransferred(
    bytes32 indexed entityKey,
    address indexed previousOwner,
    address indexed newOwner,
    uint256 version
);

event EntityOperatorTransferred(
    bytes32 indexed entityKey,
    address indexed previousOperator,
    address indexed newOperator,
    uint256 version
);

event EntityDeleted(
    bytes32 indexed entityKey,
    address indexed by,
    uint256 version
);

event EntityExpired(
    bytes32 indexed entityKey,
    uint256 version
);
```


## AI Generated Hypothetical Feedback to Golem DB and its API

### Simplicity-Focused Mid-Senior Web3 Dev

Golem DB’s README is clear, well-structured, and approachable. The quick start examples are practical and easy to follow, showing how to create, update, and query entities with minimal boilerplate. The API feels familiar to anyone who’s used web3.py or similar SDKs, and the type hints and NamedTuple usage make it easy to reason about data structures.

The permission model (owner/operator) is explained up front, and the permission table is a great touch—it’s immediately obvious who can do what. The batch/process API is also a nice feature for efficiency.

The event subscription section is especially strong:

The subscribe method is minimal and explicit, and the callback pattern is easy to use.
The example for entity creation events is copy-paste ready and shows all the info I’d want.
The SubscriptionHandle pattern is familiar and makes resource management straightforward.
The error handling and result types are explicit, so I know what to expect and how to handle edge cases. The offchain verification section is a bit dense, but it’s good to see that auditability is a first-class concern.

**What I like**

Minimal, readable code samples—no magic, no unnecessary abstraction.
Clear, permissioned model with real-world roles.
Batch operations and event subscriptions are easy to use.
Type safety and explicit error handling.

**What I’d want to see improved or clarified**

A short section on how to connect to a testnet or local dev node (e.g., what RPC_URL should look like).
More real-world examples, e.g., how to use annotations for tagging, or how to handle entity expiry in practice.
A quick note on gas costs or best practices for minimizing onchain storage (even just a link to a section below).
Maybe a “common pitfalls” or FAQ section for things like connection loss, permission errors, or large data.

**Summary**
This is one of the more approachable and production-ready web3 SDKs I’ve seen. The README is focused, practical, and doesn’t overwhelm with jargon or unnecessary complexity. I’d feel comfortable integrating this into a project or hackathon with minimal ramp-up.

### Seasoned Web3 Dev

Golem DB’s design is refreshingly clear and well-structured, especially compared to many onchain data solutions I’ve worked with. The dual-role model (owner/operator) and explicit permissioning are a big plus for real-world use cases—this is much more flexible than the typical single-owner NFT or registry pattern. The API’s type safety and explicit error handling are also welcome; it’s obvious that developer experience was a priority.

That said, my main concern is the cost and practicality of storing rich entity data and metadata onchain. The model supports binary data, annotations, and extensive metadata, but on most EVM chains, storing even a few kilobytes per entity is prohibitively expensive. I’d want to see clear guidance or patterns for offchain storage (e.g., IPFS, Arweave) with onchain anchoring, or at least a way to store only hashes or references onchain. The offchain verification section is a good start, but I’d like to see more concrete examples of hybrid storage patterns and how to keep onchain costs low.

Overall, Golem DB’s API is a big step up in terms of clarity and permissioning, but for production use, I’d want to see best practices for minimizing onchain storage, handling large data, and integrating with offchain storage networks. If those are addressed, this could be a very compelling foundation for complex, multi-party web3 applications.

### Sceptical Expert Web3 Dev

Feedback from a Skeptical Senior Web3 Developer
As someone who’s built and audited complex NFT protocols, DAOs, and real-world asset tokenization systems, I’m not immediately convinced that Golem DB offers something fundamentally new. Most of what I see—role-based permissions, entity metadata, offchain verification—can be (and often is) implemented with custom smart contracts, and the cost/complexity of onchain storage remains a major concern. I’m wary of introducing another abstraction layer unless it demonstrably reduces friction, cost, or risk compared to established patterns.

I’d also want to know:

How does Golem DB handle upgrades, migrations, and schema evolution?
What’s the story for composability with existing DeFi/NFT standards?
Is there a proven path for integrating with offchain storage and oracles, or is this just another “store everything onchain” system?
How does it perform under high load, and what are the gas implications for batch operations or large entities?

**Arguments & Changes to Convince the Skeptical Expert**
1. Hybrid Storage Patterns Out-of-the-Box
    - Show that Golem DB natively supports storing only hashes or CIDs onchain, with seamless hooks for IPFS, Arweave, or other decentralized storage.
    - Provide code samples and reference integrations for hybrid onchain/offchain data flows.
1. Composable, Modular Design
    - Demonstrate how Golem DB entities can be wrapped or extended to comply with ERC-721, ERC-1155, or other standards, enabling easy integration with existing NFT/DeFi infrastructure.
    - Offer adapters or plugins for common protocols (e.g., OpenSea, Zora, DAO frameworks).
1. Schema Evolution & Upgradability
    - Document how entity schemas can evolve over time without breaking existing data or requiring contract redeployment.
    - Provide migration tools or patterns for real-world upgrades.
1. Gas & Performance Benchmarks
    - Publish benchmarks comparing Golem DB operations (create, update, batch, query) to hand-rolled Solidity patterns, highlighting any gas savings or trade-offs.
    - Show how batch operations and partial data retrieval can reduce costs in practice.
1. Security & Auditability
    - Highlight how Golem DB’s signature and versioning model simplifies offchain audit trails, dispute resolution, and regulatory compliance compared to ad hoc solutions.
1. Real-World Case Studies
    - Share success stories or reference implementations where Golem DB enabled features or efficiencies that would have been painful or impossible with standard contract patterns.
1. Open, Extensible API
    - Emphasize that Golem DB is not a black box: developers can extend, audit, and customize every layer, and are not locked into a proprietary stack.

**Summary**

To win over skeptical, experienced web3 devs, Golem DB should focus on composability, hybrid storage, upgradability, and real-world cost/performance evidence—plus clear documentation and open extensibility. Show, don’t just tell, how it solves pain points that even the best custom contracts struggle with.
