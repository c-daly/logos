"""Authoritative embedding-dimension resolution for the LOGOS HCG.

The embedding vector dimension is taken from the *measured* output of the running
embedding provider — never a hardcoded constant. ``LOGOS_EMBEDDING_DIM`` is an
optional override that is validated against the measured output; if they disagree
the resolution fails loud rather than letting a provider/collection dimension
mismatch silently drop embeddings (see logos#535).
"""

from __future__ import annotations

from logos_config.env import get_env_value


class EmbeddingDimMismatch(ValueError):
    """Raised when an explicit override disagrees with the measured embedding output."""


def resolve_embedding_dim(measured_dim: int, override: int | None = None) -> int:
    """Resolve the authoritative embedding dimension.

    Args:
        measured_dim: the actual length of an embedding produced by the live
            provider (ground truth).
        override: optional explicit ``LOGOS_EMBEDDING_DIM``; must equal
            ``measured_dim`` or an :class:`EmbeddingDimMismatch` is raised.

    Returns:
        The authoritative dimension (always the measured value).

    Raises:
        EmbeddingDimMismatch: if ``override`` is set and disagrees with
            ``measured_dim`` (the provider did not deliver the requested size).
    """
    if override is not None and override != measured_dim:
        raise EmbeddingDimMismatch(
            f"LOGOS_EMBEDDING_DIM={override} but the embedding provider produced "
            f"{measured_dim}-dim vectors. The override cannot be honored — either "
            f"remove it (to use the provider's measured dimension) or fix the "
            f"provider/model so it actually emits {override} dimensions."
        )
    return measured_dim


def get_embedding_dim_override() -> int | None:
    """Read the optional ``LOGOS_EMBEDDING_DIM`` override.

    ``LOGOS_EMBEDDING_DIM`` — embedding vector dimension:

    * **Leave UNSET (``None``)** → derive the dimension from the running
      provider's *measured* output. This is the recommended default.
    * **Set an explicit int** → force a provider that supports it (e.g. OpenAI
      Matryoshka models) to a specific size. The override is validated against
      the measured output (see :func:`resolve_embedding_dim`) and fails loud if
      the provider can't deliver it.

    There is intentionally **no hardcoded numeric default** — a wrong constant
    silently drops embeddings (logos#535: a 1536-dim provider writing into a
    384-dim collection).
    """
    raw = get_env_value("LOGOS_EMBEDDING_DIM", default=None)
    if raw is None or raw.strip() == "":
        return None
    try:
        return int(raw)
    except (ValueError, TypeError) as exc:
        raise EmbeddingDimMismatch(
            f"LOGOS_EMBEDDING_DIM={raw!r} is not a valid integer — set it to an "
            f"integer dimension or leave it unset to derive from the provider."
        ) from exc
