"""Utility functions for GolemBase SDK tests."""

import logging
import uuid
from collections.abc import Sequence

from golem_base_sdk import (
    Annotation,
    CreateEntityReturnType,
    EntityKey,
    GolemBaseClient,
    GolemBaseCreate,
    GolemBaseUpdate,
)

logger = logging.getLogger(__name__)


async def create_single_entity(
    client: GolemBaseClient,
    payload: bytes,
    btl: int = 60,
    annotations: dict[str, str | int] | None = None,
) -> Sequence[CreateEntityReturnType]:
    """Create a single entity and returns the creation receipt."""
    return await client.create_entities([to_create_entity(payload, btl, annotations)])


async def get_entity_count(client: GolemBaseClient, detail: str) -> int:
    """Get entity count and log it with a short wait for blockchain propagation."""
    count = await client.get_entity_count()
    assert isinstance(count, int), "Entity count should be an integer"
    assert count >= 0, "Entity count should be non-negative"
    logger.info(f"Entity count {detail}: {count}")  # noqa: G004
    return count


def to_create_entity(
    payload: bytes, btl: int = 60, annotations: dict[str, str | int] | None = None
) -> GolemBaseCreate:
    """Create a GolemBaseCreate instance with given payload and annotations."""
    if annotations is None:
        annotations = {}

    # Split merged_annotations into str and int mappings
    str_annotations = {k: v for k, v in annotations.items() if isinstance(v, str)}
    int_annotations = {k: v for k, v in annotations.items() if isinstance(v, int)}

    return GolemBaseCreate(
        payload,
        btl,
        to_annotations_str(str_annotations),
        to_annotations_int(int_annotations),
    )


def to_update_entity(
    entity_key: EntityKey,
    payload: bytes,
    btl: int = 60,
    annotations: dict[str, str | int] | None = None,
) -> GolemBaseUpdate:
    """Create a GolemBaseUpdate instance with given payload and annotations."""
    if annotations is None:
        annotations = {}

    # Split merged_annotations into str and int mappings
    str_annotations = {k: v for k, v in annotations.items() if isinstance(v, str)}
    int_annotations = {k: v for k, v in annotations.items() if isinstance(v, int)}

    return GolemBaseUpdate(
        entity_key,
        payload,
        btl,
        to_annotations_str(str_annotations),
        to_annotations_int(int_annotations),
    )


def to_annotations_str(a: dict[str, str]) -> list[Annotation[str]]:  # noqa: D103
    annotations = []
    for key, value in a.items():
        annotations.append(Annotation(key, value))
    return annotations


def to_annotations_int(a: dict[str, int]) -> list[Annotation[int]]:  # noqa: D103
    annotations = []
    for key, value in a.items():
        annotations.append(Annotation(key, value))
    return annotations


def generate_uuid() -> str:
    """Generate a UUID value as a string."""
    return str(uuid.uuid4())
