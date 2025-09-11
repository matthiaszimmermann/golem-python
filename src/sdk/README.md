# Golem DB SDK

Golem DB is a permissioned storage system for decentralized apps, supporting flexible entities with binary data, annotations, and metadata.

The Golem DB SDK is the official Python library for interacting with Golem DB networks. It offers a type-safe, developer-friendly API for managing entities, querying data, subscribing to events, and offchain verification—ideal for both rapid prototyping and production use.

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
- Rich Data Model: Support for binary data, structured annotations, and metadata.
- Auditability & Security: All state changes are cryptographically signed and fully auditable, both onchain and offchain.
- Flexible Expiry & Retention: Built-in support for data expiry (BTL), short/medium-term storage, and seamless offchain archival.
- Easy Integration: Simple, type-safe API and event model for rapid prototyping and production use.


## Entities

Entities are the core concept of Golem DB to store data.
Entities can hold both unstructured and structured data and have a defined lifetime.

Creating entities is permissionless.
Once created, write access to entities in Golem DB is permissioned: The entity creator/owner is the only account that is allowed to change entity data and lifecycle.
All state changes are cryptographically signed, ensuring strong guarantees of authenticity, integrity, and auditability—both on-chain and off-chain.

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
client.update(entity_key, annotations={"purpose": "demo", "version": 1})

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
print("Created entities:", [res.entity_key for res in batch_result.creates])

# Query for all entities with annotation type: "demo"
# The Golem DB query language is a valid subset of SQL
select_result = client.select('type = "demo"')
print('Query results (type="demo"):', [e.metadata.entity_key for e in select_result.entities])

# Query for all entities with annotation type: "test" and group: "A"
select_result = client.select('type = "test" and group = "A"')
print('Query results (type="demo" and group = "A"):', [e.metadata.entity_key for e in select_result.entities])
```

You can easily subscribe to entity lifecycle events using the subscribe method. For example, to listen for entity creation events and print all available information:

```python
from golemdb import Client, EntityField

# Callback method that is called whenever a new entity is created.
def handle_created(event: EntityCreated) -> None:
    print("Entity created:")
    print(f"  entity_key: {event.entity_key}")
    print(f"  version: {event.version}")
    print(f"  owner: {event.owner}")
    print(f"  expires_at_block: {event.expires_at_block}")
    print(f"  data_hash: {event.data_hash.hex()}")
    print(f"  annotations_root: {event.annotations_root.hex()}")

# Initialize the client (details may vary depending on your setup)
client = Client(RPC_URL, wallet, password)

# Subscribe to creation events
handle: SubscriptionHandle = await client.subscribe(
    label="creation-watcher",
    on_created=handle_created
)

# Trigger an entity creation callback
client.create(data=b"Hello World!")

# ... later, to clean up:
await handle.unsubscribe()
await client.disconnect()
```

## Entity Elements

### Current Elements

| Element            | Set on Create | Updatable    | Who Can Set/Change? | Notes                                        |
|--------------------|:-------------:|:------------:|---------------------|----------------------------------------------|
| `entity_key`       | Yes           | No           | System/Contract     | Unique identifier, auto-generated, immutable |
| `data`             | Yes           | Yes          | Owner               | Unstructured payload, updatable              |
| `annotations`      | Yes           | Yes          | Owner               | Key-value metadata, updatable                |
| `owner`            | Yes (default: signer) | Yes  | Owner               | Can be transferred                           |
| `expires_at_block` | Yes (via btl) | Yes          | Owner               | Set on create, can be extended               |

### Elements to be discussed/added

| Element             | Set on Create | Updatable  | Who Can Set/Change? | Notes                                         |
|---------------------|:-------------:|:----------:|---------------------|-----------------------------------------------|
| `created_at_block`  | Yes (auto)    | No         | System/Contract     | Block No at creation, immutable               |
| `updated_at_block`  | Yes (auto)    | Yes (auto) | System/Contract     | Updated on each change, auto-managed          |
| `version`           | Yes (auto)    | Yes (auto) | System/Contract     | Incremented on each update including the owner, auto-managed |
| `data_hash`         | Yes (auto)    | Yes (auto) | System/Contract     | Hash over data field, recalculated at every change  |
| `annotations_root`  | Yes (auto)    | Yes (auto) | System/Contract     | Merkle root over annotations                  |
| `previous_owner`    | Yes (auto)    | Yes (auto) | System/Contract     | Updated on each owner change, auto-managed    |
| `entity_root`       | Yes (auto)    | Yes (auto) | System/Contract     | Hash over all entity Merkle tree              |
| `signature`         | Yes (auto)    | Yes (auto) | System/Contract     | signature over entity hash by previous owner  |

**Previous Owner**

Records the previous owner.
After the creation of a new entity the owner and previous owner both contain the signer address of the create transaction.
Entity changes that do not change the owner will have identical owner and previous owner attributes.
When the current owner transfers ownership to a new owner, the previous owner is set to the signer of the transfer transaction, the owner address is set to the new owner of the entity.

**Version**

Any change in data, annotations, lifetime, or owner increases the version.
It ensures that signatures are always bound to a specific state of the entity, guaranteeing that off-chain consumers can verify the exact version of the data they are trusting.

**Data Hash**

Hash over the unstructured data field.
Used for the calculation of the entity hash.

**Annotations Root**

Merkle root over the annotations.
Supports Merkle proofs of the value of individual annotations.

**Entity Hash**

Hash over version, entity key, expires_at_block, data_hash, annotations_root, previous_owner, owner.

**Signature**

A cryptographic signature created by the owner of an entity over the entity hash.
It serves as proof that the owner has authorized changes and the resulting state of the entity.

For ownership transfers, the signature must be generated by the previous owner, ensuring that only the legitimate owner can approve such changes.

### Offchain Verification

To verify the authenticity and integrity of the entity offchain:

1. Obtain the entity record (including data, annotations, and metadata including signature).
1. Recompute the hashes:
- `data_hash = hash(data)`
- `annotations_root = merkle_root(annotations)`
- `entity_root = merkle_root(entity)`
1. Verify the owner’s signature of the entity root:
1. Use the owner’s public key to check that owner_signature is valid for entity_root.

**To verify individual annotation values**

Use a Merkle proof to show that a specific annotation is included in annotations_root.
The annotation_root itself is embedded in the entity_root as shown below.

```
entity_root
├── metadata_root
│   ├── identity_root
│   │   ├── entity_key (default value for creation)
│   │   ├── version
│   │   ├── owner
│   │   └── previous_owner
│   └── lifecycle_root
│       ├── created_at_block (default value for creation)
│       └── expires_at_block
├── data_root
│   ├── data_hash
│   └── annotations_root
```

The entity root is only computed over attributes that are owner controlled.
This is why updated_at_block is not shown in the Merkle tree.

Annotations root needs to be computed in a deterministic way using the available annotation key value pairs.

## Query DSL


The Query DSL covers a subset of the SQL WHERE clause exclusing joins and groupings.

### Query Examples

Here are some useful example queries using the Golem DB Query DSL:

| Query | Description |
|-------|-------------|
| `score > 100` | Entities with a numeric `score` greater than 100. |
| `$expires_at_block <= 200000` | Entities expiring at or before block 2,000,000. |
| `$owner = '0x1234...abcd'` | Entities owned by a specific address. |
| `type IS NULL` | Entities where the `type` attribute is undefined. |
| `purpose IS NOT NULL` | Entities where the `purpose` attribute is defined. |
| `name LIKE 'Al%'` | Entities where the `name` attribute starts with 'Al'. |
| `score >= 0 AND score < 100` | Entities with a `score` in the range [0, 100). |
| `(type = 'demo' OR type = 'test') AND group = 'A'` | Entities of type 'demo' or 'test' in group 'A'. |
| `$version != 1` | Entities where the `version` is not 1. |


### DSL Features

| Feature         | Syntax Example              | Description                                      |
|-----------------|-----------------------------|--------------------------------------------------|
| Equality        | `field = value`             | Field equals value                               |
| Inequality      | `field != value`            | Field not equal to value                         |
| Greater than    | `field > value`             | Field greater than value                         |
| Greater/equal   | `field >= value`            | Field greater than or equal to value             |
| Less than       | `field < value`             | Field less than value                            |
| Less/equal      | `field <= value`            | Field less than or equal to value                |
| IS NULL         | `field IS NULL`             | Field/attribute is undefined for the entity      |
| IS NOT NULL     | `field IS NOT NULL`         | Field/attribute is defined for the entity        |
| AND             | `expr1 AND expr2`           | Logical AND of two expressions                   |
| OR              | `expr1 OR expr2`            | Logical OR of two expressions                    |
| NOT             | `NOT expr`                  | Logical NOT of an expression                     |
| Parentheses     | `(expr1 OR expr2) AND expr3`| Grouping and precedence control                  |
| Numeric value   | `field = 123`               | Numeric values are unquoted                      |
| String value    | `field = 'string'`          | String values must be single-quoted              |
| Prefix match    | `field LIKE 'prefix%'`      | Field starts with a given string prefix          |

### DSL Grammar

```
query        ::= expr
expr         ::= term (("AND" | "OR") term)*
term         ::= "NOT" term | factor
factor       ::= comparison | null_check | "(" expr ")"
comparison   ::= field op value
null_check   ::= field "IS NULL" | field "IS NOT NULL"
op           ::= "=" | "!=" | ">" | ">=" | "<" | "<=" | "LIKE"
field        ::= identifier
value        ::= string | number
string       ::= "'" chars "'"
chars        ::= (char | "''")*
char         ::= any character except single quote (')
                 or two single quotes ("''") for an escaped single quote
number       ::= [+-]?[0-9]+
```

### Metadata Elements

All metadata element names start with `$`.

| Name                | Comment                       |
|---------------------|-------------------------------|
| `$id`               | Entity key (or $entity_key ?) |
| `$owner`            | |
| `$previous_owner`   | Owner before entity change |
| `$version`          | |
| `$created_at_block` | |
| `$updated_at_block` | |
| `$expires_at_block` | |
| `$data_hash`        | |
| `$annotations_root` | |
| `$entity_root`      | |
| `$signature`        | |

### Entity Data and Annotations

For `$data` and `$annotations` only null checks are supported.
Annotation names must start with a letter `[a-z,A-Z]`.
TODO define allowed charset for rest of the annotation names.

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
    previous_owner: ChecksumAddress
    created_at_block: int
    updated_at_block: int
    expires_at_block: int
    version: int
    data_hash: bytes
    annotations_root: bytes
    entity_root: bytes
    signature: bytes

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
    owner: Optional[ChecksumAddress] = None

class UpdateOp(NamedTuple):
    entity_key: EntityKey
    data: Optional[bytes] = None
    annotations: Optional[Annotations] = None
    btl: Optional[int] = None
    new_owner: Optional[ChecksumAddress] = None

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
    If no matching entities are found, an empty list is returned.
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
    version: int
    created_at_block: int
    expires_at_block: int
    data_hash: HexStr
    annotations_root: HexStr

class EntityUpdated(NamedTuple):
    entity_key: EntityKey
    owner: ChecksumAddress
    version: int
    updated_at_block: int
    data_hash: HexStr
    annotations_root: HexStr

class EntityTransferred(NamedTuple):
    entity_key: EntityKey
    owner: ChecksumAddress
    version: int
    previous_owner: ChecksumAddress

class EntityExtended(NamedTuple):
    entity_key: EntityKey
    owner: ChecksumAddress
    previous_expires_at_block: int
    expires_at_block: int

class EntityDeleted(NamedTuple):
    entity_key: EntityKey
    owner: ChecksumAddress
    version: int

class EntityExpired(NamedTuple):
    entity_key: EntityKey
    owner: ChecksumAddress
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

class NodeError(EntityError):
    """Raised for other Golem DB errors."""

```

### Methods (Create, Update, Delete)

```python
def create(
    self,
    data: bytes,
    annotations: Optional[Annotations] = None,
    btl: int = 60,
    owner: ChecksumAddress = None
) -> EntityKey:
    """
    Create a new entity.
    Optionally specify an owner (default owner is signer).
    Permissionless.
    Raises InvalidInputError for invalid arguments.
    """

def update(
    self,
    entity_key: EntityKey,
    data: bytes = None,
    annotations: Optional[Annotations] = None,
    btl: int = None,
    new_owner: ChecksumAddress = None
) -> bool:
    """
    Update data, annotations, transfer owner, or extend the lifetime of the entity.
    Arguments that are set to None will not lead to any changes.
    Permissioned. Only allowed for current owner.
    Raises EntityNotFoundError if no such entity exists.
    Raises PermissionDeniedError if signer is not current owner.
    Raises InvalidInputError for invalid arguments.
    """

def delete(self, entity_key: EntityKey) -> bool:
    """
    Delete the entity.
    Permissioned. Only allowed for current owner.
    Raises EntityNotFoundError if no such entity exists.
    Raises PermissionDeniedError if signer is not owner.
    Raises InvalidInputError for invalid arguments.
    """

def process(
    self,
    creates: List[CreateOp] = None,
    updates: List[UpdateOp] = None,
    deletes: List[DeleteOp] = None
) -> ProcessResult:
    """
    Batch process multiple entity operations (create, update, delete) in a single transaction.

    - `creates`: List of CreateOp objects (same fields as the `create` method).
    - `updates`: List of UpdateOp objects (same fields as the `update` method).
    - `deletes`: List of DeleteOp objects (entity_key only).

    Each entity key may only be used once over all specified operations.
    I.e. using an entity key in multiple updates or using the same entity key in an update and/or a transfer and delete operation is not supported.
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
    For block number None (default) the latest available block number is used.
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
    For block number None (default) the latest available block number is used.
    Only block_numbers covering the last n minutes are supported.
    Raises EntityNotFoundError if no such entity exists.
    Raises InvalidInputError for invalid arguments.
    """

def count(self, query: str, block_number: int = None) -> CountResult:
    """
    Count matching entities for specified query and block_number.
    The query argument specifies which entries to return.
    A subset of the SQL WHERE clause regarding annotations and metadata attributes is supported.
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
    The query argument specifies which entries to return.
    A subset of the SQL WHERE clause regarding annotations and metadata attributes is supported.
    Optionally specify which entity fields to retrieve.
    The default populates all available fields.
    Available fields are "data", "annotations", and "metadata".
    Optionally specify sort criteria.
    The default sorts according to ascending entity keys.
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
    on_transferred: Optional[Callable[[EntityTransferred], None]] = None,
    on_deleted: Optional[Callable[[EntityDeleted], None]] = None,
    on_expired: Optional[Callable[[EntityExpired], None]] = None,
) -> SubscriptionHandle:
    """
    Subscribe to entity events.

    Register a callback for any combination of:
      - on_created
      - on_updated
      - on_extended
      - on_transferred
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
    uint256 indexed version,
    address indexed owner,
    uint256 expiresIn,
    bytes32 dataHash,         // keccak256 hash of the initial data
    bytes32 annotationsRoot   // keccak256 hash of the initial annotations
);

event EntityUpdated(
    bytes32 indexed entityKey,
    uint256 indexed version,
    address indexed owner,
    bytes32 dataHash,         // keccak256 hash of the new data
    bytes32 annotationsRoot   // keccak256 hash of the new annotations
);

event EntityTransferred(
    bytes32 indexed entityKey,
    uint256 indexed version,
    address indexed owner,
    address previousOwner
);

event EntityExtended(
    bytes32 indexed entityKey,
    uint256 indexed version,
    address indexed owner,
    uint256 oldExpiresIn,
    uint256 expiresIn
);

event EntityDeleted(
    bytes32 indexed entityKey,
    uint256 indexed version,
    address indexed owner
);

event EntityExpired(
    bytes32 indexed entityKey,
    uint256 indexed version,
    address indexed owner
);
```


## AI Generated Hypothetical Feedback to Golem DB and its API

### Simplicity-Focused Mid-Senior Web3 Dev

Golem DB’s README is clear, well-structured, and approachable. The quick start examples are practical and easy to follow, showing how to create, update, and query entities with minimal boilerplate. The API feels familiar to anyone who’s used web3.py or similar SDKs, and the type hints and NamedTuple usage make it easy to reason about data structures.
The batch/process API is also a nice feature for efficiency.

The event subscription section is especially strong:

The subscribe method is minimal and explicit, and the callback pattern is easy to use.
The example for entity creation events is copy-paste ready and shows all the info I’d want.
The SubscriptionHandle pattern is familiar and makes resource management straightforward.
The error handling and result types are explicit, so I know what to expect and how to handle edge cases. The offchain verification section is a bit dense, but it’s good to see that auditability is a first-class concern.

**What I like**

Minimal, readable code samples—no magic, no unnecessary abstraction.
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

Golem DB’s design is refreshingly clear and well-structured, especially compared to many onchain data solutions I’ve worked with. The API’s type safety and explicit error handling are also welcome; it’s obvious that developer experience was a priority.

That said, my main concern is the cost and practicality of storing rich entity data and metadata onchain. The model supports binary data, annotations, and extensive metadata, but on most EVM chains, storing even a few kilobytes per entity is prohibitively expensive. I’d want to see clear guidance or patterns for offchain storage (e.g., IPFS, Arweave) with onchain anchoring, or at least a way to store only hashes or references onchain. The offchain verification section is a good start, but I’d like to see more concrete examples of hybrid storage patterns and how to keep onchain costs low.

Overall, Golem DB’s API is a big step up in terms of clarity and permissioning, but for production use, I’d want to see best practices for minimizing onchain storage, handling large data, and integrating with offchain storage networks. If those are addressed, this could be a very compelling foundation for complex, multi-party web3 applications.

### Sceptical Expert Web3 Dev

Feedback from a Skeptical Senior Web3 Developer
As someone who’s built and audited complex NFT protocols, DAOs, and real-world asset tokenization systems, I’m not immediately convinced that Golem DB offers something fundamentally new. Most of what I see—entity metadata, offchain verification—can be (and often is) implemented with custom smart contracts, and the cost/complexity of onchain storage remains a major concern. I’m wary of introducing another abstraction layer unless it demonstrably reduces friction, cost, or risk compared to established patterns.

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
