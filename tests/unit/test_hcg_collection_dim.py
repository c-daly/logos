"""Unit tests for HCGMilvusSync's embedding-dim helper (_collection_embedding_dim).

Pure unit tests — no Milvus required. The live-Milvus behaviour (collection
recreate / measured-dim sizing) lives in
``tests/integration/test_hcg_milvus_dim.py`` (logos#542, epic #535).
"""

from __future__ import annotations

from types import SimpleNamespace

from logos_hcg import sync


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


def test_collection_embedding_dim_handles_malformed_params() -> None:
    """Non-dict params or a non-numeric dim yield None, never an exception."""
    non_dict = SimpleNamespace(
        schema=SimpleNamespace(fields=[SimpleNamespace(name="embedding", params=None)])
    )
    assert sync._collection_embedding_dim(non_dict) is None
    bad_dim = SimpleNamespace(
        schema=SimpleNamespace(
            fields=[SimpleNamespace(name="embedding", params={"dim": "nope"})]
        )
    )
    assert sync._collection_embedding_dim(bad_dim) is None
