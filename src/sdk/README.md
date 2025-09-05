# Golem DB

## Entities

TODO general overview


## Entity Role Model: Owner & Operator

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

## Client Methods

```python
from typing import NamedTuple, List, Optional, Dict, Union, Any
from enum import Enum, auto

class OrderField(Enum):
    ASC = auto()
    DESC = auto()

class EntityField(Enum):
    DATA = auto()
    ANNOTATIONS = auto()
    METADATA = auto()

class Entity(NamedTuple):
    data: Optional[bytes] = None
    annotations: Optional[Dict[str, Union[str, int]]] = None
    metadata: Optional[Dict[str, Union[EntityKey, Address, int, bytes]] = None

class SortSpec(NamedTuple):
    field: str,
    order: OrderField

class Address(str):
    pass

class Cursor(str):
    pass

class Pagination(NamedTuple):
    limit: int = 100
    cursor: Optional[Cursor] = None # str, EntityKey or something else?

class GetResult(NamedTuple):
    entities: List[Entity]
    block_number: int
    next_cursor: Optional[Cursor] = None

class CountResult(NamedTuple):
    count: int
    block_number: int

def create(
    self,
    data: bytes,
    annotations: dict = None,
    btl: int = 60,
    operator: Address = None
) -> EntityKey:
    """
    Create a new entity. Optionally specify an operator (manager/issuer).
    """

def update(
    self,
    entity_key: EntityKey,
    data: bytes = None,
    annotations: dict = None,
    btl: int = None,
    new_operator: Address = None
) -> bool:
    """
    Update data, annotations, transfer operator role, or extend the entitys lifetime.
    Arguments that are set to None will not lead to any changes.
    Only allowed for the current operator.
    """

def transfer(self, entity_key: EntityKey, new_owner: Address) -> bool:
    """
    Transfer ownership role. Only allowed for current owner.
    """

def delete(self, entity_key: EntityKey) -> bool:
    """
    Delete the entity. Allowed for owner or operator.
    """

def get(
    self,
    query: str,
    fields: Optional[List[EntityField]] = None,
    sort: Optional[List[SortSpec]] = None,
    pagination: Optional[Pagination] = None,
    block_number: Optional[int] = None
) -> GetResult:
    """
    Fetch entities by annotation fields and metadata elements like $entity_key, $owner, etc.
    Optionally specify which entity fields to retrieve.
    Available fiels are "data", "annotations", and "metadata".
    The default populates all available fields.
    For block number None (default) the latest block number available to the client connection is used.
    Only block_numbers covering the last n minutes are supported.
    """

def count(self, query: str, block_number: int = None) -> CountResult:
    """
    Count matching entities for specified query and block_number.
    For block number None (default) the latest block number available to the client connection is used.
    Only block_numbers covering the last n minutes are supported.
    """
```
