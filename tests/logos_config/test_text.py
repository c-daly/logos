"""Frozen golden-table tests for the shared canonicalize() normalizer.

ONE canonicalize() lives in the foundry (logos_config.text) and is imported by
Hermes, Sophia, and the offline naming-driven-typing harness (no drifting
copies -- R-integration-6). This golden table is FROZEN: every (input -> output)
pair below is a contract. If a change here is intentional, update all three
consumers in the same PR.

Behavior under test (SPEC s5.4):
NFKC -> strip -> collapse whitespace -> lowercase -> drop leading a/an/the ->
singularize HEAD NOUN ONLY via inflect (conservative; inflect.singular_noun
over-strips -ss/-is/-us and the realm roots, so those are kept verbatim via an
irregular keep-list + suffix guard) -> strip curated trailing fillers
{type, category, kind, class, group, entity} only when not the whole string.
canonicalize is idempotent: canonicalize(canonicalize(x)) == canonicalize(x).
"""

from __future__ import annotations

import pytest

from logos_config.text import canonicalize

# FROZEN golden table -- the contract. (raw_input, canonical_output)
GOLDEN: list[tuple[str, str]] = [
    # plural -> singular head noun
    ("vehicle", "vehicle"),
    ("vehicles", "vehicle"),
    ("mammal", "mammal"),
    ("mammals", "mammal"),
    ("process", "process"),
    ("processes", "process"),
    ("bus", "bus"),
    ("buses", "bus"),
    # inflect over-strips these -- keep-list / suffix guard must protect them
    ("species", "species"),
    ("analysis", "analysis"),
    ("class", "class"),
    # realm roots are stable fixed points
    ("entity", "entity"),
    ("concept", "concept"),
    ("node", "node"),
    # case / whitespace / unicode normalization
    ("  Vehicle  ", "vehicle"),
    ("VEHICLES", "vehicle"),
    ("vehicle\xa0\xa0type", "vehicle"),  # NBSP collapses; trailing "type" stripped
    # leading article stripping
    ("the vehicle", "vehicle"),
    ("a mammal", "mammal"),
    ("an analysis", "analysis"),
    # trailing filler stripping (only when not the whole string)
    ("vehicle type", "vehicle"),
    ("vehicle types", "vehicle"),
    ("mammal category", "mammal"),
    ("process group", "process"),
    # whole-string filler is NOT stripped (would empty the name)
    ("type", "type"),
    ("category", "category"),
    ("group", "group"),
]


@pytest.mark.parametrize("raw,expected", GOLDEN, ids=[g[0] for g in GOLDEN])
def test_canonicalize_golden_table(raw: str, expected: str) -> None:
    """Every frozen (input -> output) pair is a hard contract."""
    assert canonicalize(raw) == expected


@pytest.mark.parametrize("raw,expected", GOLDEN, ids=[g[0] for g in GOLDEN])
def test_canonicalize_is_idempotent(raw: str, expected: str) -> None:
    """canonicalize(canonicalize(x)) == canonicalize(x) for every golden input."""
    once = canonicalize(raw)
    assert canonicalize(once) == once
    assert once == expected


def test_vehicle_and_vehicles_collide() -> None:
    """The harness relies on this collision for semantic reuse_collapses."""
    assert canonicalize("vehicle") == canonicalize("vehicles")


def test_empty_and_whitespace_only_return_empty() -> None:
    """Degenerate inputs normalize to empty string, never raise."""
    assert canonicalize("") == ""
    assert canonicalize("   ") == ""
    assert canonicalize("\xa0") == ""
