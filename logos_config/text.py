"""Shared name-normalization utility for the LOGOS ontology.

ONE canonicalize() lives here in the foundry and is imported by Hermes,
Sophia, and the offline naming-driven-typing harness -- never three drifting
copies (R-integration-6).

canonicalize() maps a raw type / cluster name to its canonical lowercase
singular form so that semantically equal names collide (vehicle == vehicles)
while inflect's known over-stripping of the realm roots and -ss/-is/-us nouns
is suppressed (analysis stays analysis, process stays process, bus stays bus).

Steps (SPEC s5.4):
  NFKC -> strip -> collapse whitespace -> lowercase -> drop leading a/an/the
  -> singularize HEAD NOUN ONLY (conservative; no Porter stemming)
  -> strip curated trailing fillers, only when not the whole string.

The function is idempotent: canonicalize(canonicalize(x)) == canonicalize(x).
"""

from __future__ import annotations

import re
import unicodedata

import inflect

# Single shared inflect engine (thread-safe for read-only singular_noun calls).
_INFLECT = inflect.engine()

# Leading articles dropped before head-noun singularization.
_LEADING_ARTICLES = {"a", "an", "the"}

# Curated trailing fillers stripped only when they are NOT the whole name.
_TRAILING_FILLERS = {"type", "category", "kind", "class", "group", "entity"}

# Words inflect mis-singularizes (over-strips); kept verbatim. Includes the
# realm roots, structural keywords, and the SPEC golden cases.
_SINGULAR_KEEP = {
    "entity",
    "concept",
    "process",
    "node",
    "species",
    "class",
    "bus",
    "analysis",
}

# Any word ending in one of these is already singular for our purposes;
# inflect would wrongly strip the trailing s (e.g. -ss class/glass,
# -is analysis/crisis, -us bus/corpus/status).
_SINGULAR_SUFFIX_GUARD = ("ss", "is", "us")

_WHITESPACE_RE = re.compile(r"\s+")


def _singularize_word(word: str) -> str:
    """Singularize a single already-lowercased token, conservatively.

    inflect.singular_noun returns False when the word is already singular; in
    that case (and for guarded words) we keep the input unchanged.
    """
    if word in _SINGULAR_KEEP or word.endswith(_SINGULAR_SUFFIX_GUARD):
        return word
    singular = _INFLECT.singular_noun(word)
    return singular if isinstance(singular, str) else word


def canonicalize(name: str) -> str:
    """Return the canonical lowercase singular form of *name*.

    Idempotent. Empty / whitespace-only input returns the empty string.
    """
    # NFKC -> strip -> collapse whitespace -> lowercase.
    text = unicodedata.normalize("NFKC", name)
    text = _WHITESPACE_RE.sub(" ", text).strip().lower()
    if not text:
        return ""

    tokens = text.split(" ")

    # Drop a single leading article (keep it if it is the whole string).
    if len(tokens) > 1 and tokens[0] in _LEADING_ARTICLES:
        tokens = tokens[1:]

    # Singularize the HEAD NOUN ONLY (the last token). Modifiers are untouched.
    tokens[-1] = _singularize_word(tokens[-1])

    # Strip a single trailing curated filler, but never empty the name.
    if len(tokens) > 1 and tokens[-1] in _TRAILING_FILLERS:
        tokens = tokens[:-1]

    return " ".join(tokens)
