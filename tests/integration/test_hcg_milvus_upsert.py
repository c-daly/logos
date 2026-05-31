"""Integration tests for HCGMilvusSync upsert-by-uuid semantics.

Regression coverage for c-daly/logos#528: ``HCGMilvusSync`` was insert-only
and could not upsert by node uuid (the schema used an auto_id INT64 primary
key with ``uuid`` as a plain VARCHAR field), so re-ingesting the same node
appended a duplicate row instead of replacing it.

These tests run against a live Milvus instance and assert that ingesting the
same uuid twice leaves exactly ONE row for that uuid. The host/port are read
from ``MILVUS_HOST`` / ``MILVUS_PORT`` (the isolated test stack uses
localhost:47530); if Milvus is unavailable the tests are skipped.
"""

from __future__ import annotations

import os
import uuid as uuid_module

import pytest
from pymilvus import connections, utility

from logos_hcg import sync as sync_module
from logos_hcg.sync import HCGMilvusSync

MILVUS_HOST = os.getenv("MILVUS_HOST", "localhost")
MILVUS_PORT = os.getenv("MILVUS_PORT", "19530")

# Embedding dim for these upsert tests. ensure_collection() now requires an
# explicit dim (logos#542): callers resolve it from the measured embedding
# rather than a removed module-level _get_embedding_dim(). 384 matches the
# historical default these tests previously read from LOGOS_EMBEDDING_DIM.
_TEST_EMBEDDING_DIM = 384

pytestmark = pytest.mark.integration


def _milvus_available() -> bool:
    """Return True if a live Milvus accepts a connection at the configured host."""
    try:
        # Bounded so a silently-unreachable Milvus fails the import-time probe
        # fast instead of blocking pytest collection for pymilvus's ~30s default.
        connections.connect(
            alias="ac528_probe", host=MILVUS_HOST, port=MILVUS_PORT, timeout=5
        )
        connections.disconnect("ac528_probe")
        return True
    except Exception:
        return False


requires_milvus = pytest.mark.skipif(
    not _milvus_available(),
    reason=f"Milvus is not available on {MILVUS_HOST}:{MILVUS_PORT}",
)


@pytest.fixture
def upsert_collection_name(monkeypatch):
    """Register a unique throwaway collection for the ``Entity`` node type.

    Patches ``COLLECTION_NAMES`` so all of HCGMilvusSync's machinery
    (ensure_collection / upsert / get / health) targets a per-test collection,
    avoiding any clobber of the real ``hcg_*`` collections. Drops the
    collection on teardown.
    """
    name = f"hcg_test_upsert_{uuid_module.uuid4().hex[:12]}"
    patched = dict(sync_module.COLLECTION_NAMES)
    patched["Entity"] = name
    monkeypatch.setattr(sync_module, "COLLECTION_NAMES", patched)

    yield name

    # Teardown: drop the throwaway collection if it was created.
    try:
        connections.connect(alias="ac528_cleanup", host=MILVUS_HOST, port=MILVUS_PORT)
        if utility.has_collection(name, using="ac528_cleanup"):
            utility.drop_collection(name, using="ac528_cleanup")
        connections.disconnect("ac528_cleanup")
    except Exception:
        pass


@requires_milvus
def test_reingest_same_uuid_yields_single_row(upsert_collection_name):
    """Ingesting the same node twice must leave exactly ONE row for that uuid.

    This is the core AC for #528: the old insert()-only path appended a second
    row on re-ingest; a true upsert keyed on uuid replaces it.
    """
    dim = _TEST_EMBEDDING_DIM
    node_uuid = str(uuid_module.uuid4())

    with HCGMilvusSync(milvus_host=MILVUS_HOST, milvus_port=MILVUS_PORT) as sync:
        sync.ensure_collection("Entity", _TEST_EMBEDDING_DIM)

        # First ingest.
        sync.upsert_embedding(
            node_type="Entity",
            uuid=node_uuid,
            embedding=[0.10] * dim,
            model="model-v1",
        )

        # Re-ingest the SAME uuid with a different embedding + model.
        sync.upsert_embedding(
            node_type="Entity",
            uuid=node_uuid,
            embedding=[0.99] * dim,
            model="model-v2",
        )

        collection = sync._get_collection("Entity")
        collection.flush()

        rows = collection.query(
            expr=f'uuid == "{node_uuid}"',
            output_fields=["uuid", "embedding_model"],
        )

    # Exactly one row for the uuid (would be two before the fix).
    assert len(rows) == 1, f"expected exactly 1 row for uuid, got {len(rows)}"
    assert rows[0]["uuid"] == node_uuid
    # The surviving row reflects the most recent ingest (true replace, not append).
    assert rows[0]["embedding_model"] == "model-v2"


@requires_milvus
def test_batch_reingest_same_uuids_yields_single_rows(upsert_collection_name):
    """Batch re-ingest of the same uuids must not accumulate duplicate rows."""
    dim = _TEST_EMBEDDING_DIM
    uuid_a = str(uuid_module.uuid4())
    uuid_b = str(uuid_module.uuid4())

    with HCGMilvusSync(milvus_host=MILVUS_HOST, milvus_port=MILVUS_PORT) as sync:
        sync.ensure_collection("Entity", _TEST_EMBEDDING_DIM)

        batch_v1 = [
            {"uuid": uuid_a, "embedding": [0.1] * dim, "model": "m1"},
            {"uuid": uuid_b, "embedding": [0.2] * dim, "model": "m1"},
        ]
        sync.batch_upsert_embeddings(node_type="Entity", embeddings=batch_v1)

        batch_v2 = [
            {"uuid": uuid_a, "embedding": [0.3] * dim, "model": "m2"},
            {"uuid": uuid_b, "embedding": [0.4] * dim, "model": "m2"},
        ]
        sync.batch_upsert_embeddings(node_type="Entity", embeddings=batch_v2)

        collection = sync._get_collection("Entity")
        collection.flush()

        uuid_list = f'"{uuid_a}", "{uuid_b}"'
        rows = collection.query(
            expr=f"uuid in [{uuid_list}]",
            output_fields=["uuid", "embedding_model"],
        )

    # Two distinct uuids, one row each (four rows before the fix).
    assert len(rows) == 2, f"expected 2 rows (one per uuid), got {len(rows)}"
    by_uuid = {r["uuid"]: r["embedding_model"] for r in rows}
    assert by_uuid == {uuid_a: "m2", uuid_b: "m2"}


@requires_milvus
def test_ensure_collection_uses_uuid_primary_key(upsert_collection_name):
    """The created collection must key on ``uuid`` (no auto_id INT64 ``id`` PK).

    Guards against schema divergence: the writer's schema must match the
    read/health path's expected ``uuid``-keyed layout.
    """
    with HCGMilvusSync(milvus_host=MILVUS_HOST, milvus_port=MILVUS_PORT) as sync:
        sync.ensure_collection("Entity", _TEST_EMBEDDING_DIM)
        collection = sync._get_collection("Entity")

        schema = collection.schema
        field_names = {f.name for f in schema.fields}
        assert field_names == {"uuid", "embedding", "embedding_model", "last_sync"}
        assert "id" not in field_names

        primary = [f for f in schema.fields if f.is_primary]
        assert len(primary) == 1
        assert primary[0].name == "uuid"
        assert primary[0].auto_id is False
