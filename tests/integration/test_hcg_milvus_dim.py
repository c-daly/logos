"""HCGMilvusSync must size hcg_* collections to the *measured* embedding dim and
recreate a stale-dim collection instead of silently reusing it (logos#542,
sub-ticket of the embedding-dim coherence epic #535).

Integration test — needs a reachable Milvus. Uses throwaway collection names so
real hcg_* collections are never touched. Follows the repo's integration pattern
(``pytestmark = pytest.mark.integration`` + ``requires_milvus``) and reads
MILVUS_HOST/MILVUS_PORT so it runs against whatever stack CI starts, not just a
hardcoded localhost:19530 dev stack.
"""

from __future__ import annotations

import os

import pytest
from pymilvus import connections

from logos_hcg import sync
from logos_hcg.sync import HCGMilvusSync

MILVUS_HOST = os.getenv("MILVUS_HOST", "localhost")
MILVUS_PORT = os.getenv("MILVUS_PORT", "19530")

pytestmark = pytest.mark.integration


def _milvus_available() -> bool:
    """Return True if a live Milvus accepts a connection at the configured host."""
    try:
        connections.connect(
            alias="dim_probe", host=MILVUS_HOST, port=MILVUS_PORT, timeout=5
        )
        connections.disconnect("dim_probe")
        return True
    except Exception:
        return False


requires_milvus = pytest.mark.skipif(
    not _milvus_available(),
    reason=f"Milvus is not available on {MILVUS_HOST}:{MILVUS_PORT}",
)


@requires_milvus
def test_ensure_collection_recreates_on_dim_mismatch(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from pymilvus import (
        Collection,
        CollectionSchema,
        DataType,
        FieldSchema,
        utility,
    )

    name = "test_542_dim_recreate"
    alias = "test542"
    monkeypatch.setitem(sync.COLLECTION_NAMES, "Entity", name)
    monkeypatch.delenv("LOGOS_EMBEDDING_DIM", raising=False)

    s = HCGMilvusSync(milvus_host=MILVUS_HOST, milvus_port=MILVUS_PORT, alias=alias)
    s.connect()

    # Seed a STALE 384-dim collection (the pre-fix state).
    if utility.has_collection(name, using=alias):
        utility.drop_collection(name, using=alias)
    Collection(
        name=name,
        schema=CollectionSchema(
            [
                FieldSchema("id", DataType.INT64, is_primary=True, auto_id=True),
                FieldSchema("uuid", DataType.VARCHAR, max_length=64),
                FieldSchema("embedding", DataType.FLOAT_VECTOR, dim=384),
                FieldSchema("embedding_model", DataType.VARCHAR, max_length=128),
                FieldSchema("last_sync", DataType.INT64),
            ]
        ),
        using=alias,
    )

    try:
        # The incoming embeddings are 1536-dim -> ensure_collection must recreate.
        s.ensure_collection("Entity", 1536)

        coll = Collection(name=name, using=alias)
        dim = next(
            f.params.get("dim") for f in coll.schema.fields if f.name == "embedding"
        )
        assert dim == 1536
    finally:
        if utility.has_collection(name, using=alias):
            utility.drop_collection(name, using=alias)


@requires_milvus
def test_batch_upsert_sizes_collection_to_measured_dim(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """batch_upsert_embeddings creates the collection at the measured dim and persists."""
    import uuid as _uuid

    from pymilvus import Collection, utility

    name = "test_542_batch_dim"
    alias = "test542b"
    monkeypatch.setitem(sync.COLLECTION_NAMES, "Concept", name)
    monkeypatch.delenv("LOGOS_EMBEDDING_DIM", raising=False)

    s = HCGMilvusSync(milvus_host=MILVUS_HOST, milvus_port=MILVUS_PORT, alias=alias)
    s.connect()
    if utility.has_collection(name, using=alias):
        utility.drop_collection(name, using=alias)

    try:
        embs = [
            {"uuid": str(_uuid.uuid4()), "embedding": [0.1] * 1536, "model": "test"}
        ]
        s.batch_upsert_embeddings("Concept", embs)

        coll = Collection(name=name, using=alias)
        coll.flush()
        dim = next(
            f.params.get("dim") for f in coll.schema.fields if f.name == "embedding"
        )
        assert dim == 1536
        assert coll.num_entities == 1
    finally:
        if utility.has_collection(name, using=alias):
            utility.drop_collection(name, using=alias)
