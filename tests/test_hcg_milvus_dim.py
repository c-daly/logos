"""HCGMilvusSync must size hcg_* collections to the *measured* embedding dim and
recreate a stale-dim collection instead of silently reusing it (logos#542,
sub-ticket of the embedding-dim coherence epic #535).

Integration test — needs a reachable Milvus (dev stack on localhost:19530).
Uses a throwaway collection name so real hcg_* collections are never touched.
"""

from __future__ import annotations

import socket
from types import SimpleNamespace

import pytest

from logos_hcg import sync
from logos_hcg.sync import HCGMilvusSync


def _fake_collection(dim: object) -> SimpleNamespace:
    """A stand-in collection whose ``embedding`` field reports ``dim``."""
    return SimpleNamespace(
        schema=SimpleNamespace(
            fields=[
                SimpleNamespace(name="uuid", params={}),
                SimpleNamespace(name="embedding", params={"dim": dim}),
            ]
        )
    )


def test_collection_embedding_dim_casts_string_to_int() -> None:
    """Milvus may report the vector ``dim`` as a string; the helper must return an
    int so dim comparisons don't spuriously trigger a drop+recreate (gemini #543)."""
    assert sync._collection_embedding_dim(_fake_collection("1536")) == 1536
    assert sync._collection_embedding_dim(_fake_collection(384)) == 384


def test_collection_embedding_dim_none_without_embedding_field() -> None:
    coll = SimpleNamespace(
        schema=SimpleNamespace(fields=[SimpleNamespace(name="uuid", params={})])
    )
    assert sync._collection_embedding_dim(coll) is None


def _milvus_up(host: str = "localhost", port: int = 19530) -> bool:
    try:
        with socket.create_connection((host, port), timeout=2):
            return True
    except OSError:
        return False


@pytest.mark.skipif(not _milvus_up(), reason="dev Milvus not reachable on :19530")
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

    s = HCGMilvusSync(milvus_host="localhost", milvus_port="19530", alias=alias)
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


@pytest.mark.skipif(not _milvus_up(), reason="dev Milvus not reachable on :19530")
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

    s = HCGMilvusSync(milvus_host="localhost", milvus_port="19530", alias=alias)
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
