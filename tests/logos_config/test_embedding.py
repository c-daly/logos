"""Tests for logos_config embedding-dimension resolution.

The embedding dimension must come from the *measured* provider output, never a
hardcoded constant. An explicit override (LOGOS_EMBEDDING_DIM) is allowed but is
validated against the measured output and fails loud on disagreement, so a
provider/collection dimension mismatch can never silently drop embeddings.
"""

from __future__ import annotations

import pytest

from logos_config.embedding import (
    EmbeddingDimMismatch,
    get_embedding_dim_override,
    resolve_embedding_dim,
)


class TestResolveEmbeddingDim:
    def test_uses_measured_dim_when_no_override(self) -> None:
        """With no override, the provider's measured output is authoritative."""
        assert resolve_embedding_dim(measured_dim=1536, override=None) == 1536

    def test_rejects_override_that_disagrees_with_measured(self) -> None:
        """An explicit override the provider can't deliver fails loud, never silent.

        e.g. LOGOS_EMBEDDING_DIM=512 against a model hard-wired to 384.
        """
        with pytest.raises(EmbeddingDimMismatch):
            resolve_embedding_dim(measured_dim=384, override=512)

    def test_accepts_override_matching_measured(self) -> None:
        """An override that agrees with the measured dim is accepted as-is."""
        assert resolve_embedding_dim(measured_dim=1536, override=1536) == 1536

    @pytest.mark.parametrize("bad_dim", [0, -1])
    def test_rejects_non_positive_measured_dim(self, bad_dim: int) -> None:
        """A zero/empty measured dim must fail loud, never propagate to
        ensure_collection where it would drop a live collection it can't recreate
        (catastrophic data loss; gemini critical review on #545)."""
        with pytest.raises(ValueError):
            resolve_embedding_dim(measured_dim=bad_dim)


class TestEmbeddingDimOverride:
    def test_none_when_unset(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Unset LOGOS_EMBEDDING_DIM resolves to None — no hardcoded default."""
        monkeypatch.delenv("LOGOS_EMBEDDING_DIM", raising=False)
        assert get_embedding_dim_override() is None

    def test_int_when_explicitly_set(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """An explicit LOGOS_EMBEDDING_DIM is read as an int override."""
        monkeypatch.setenv("LOGOS_EMBEDDING_DIM", "1536")
        assert get_embedding_dim_override() == 1536

    def test_invalid_override_fails_loud(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """A non-integer LOGOS_EMBEDDING_DIM fails loud, never a silent fallback."""
        monkeypatch.setenv("LOGOS_EMBEDDING_DIM", "not-a-number")
        with pytest.raises(EmbeddingDimMismatch):
            get_embedding_dim_override()
