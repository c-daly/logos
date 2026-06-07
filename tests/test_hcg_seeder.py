"""Tests for HCG seeder skeleton seeding and type centroid seeding."""

import re
from unittest.mock import Mock

from logos_hcg.seeder import TYPE_PARENTS, HCGSeeder

# Version-agnostic UUID string form, e.g.
# "f47ac10b-58cc-4372-a567-0e02b2c3d479". The seeder mints deterministic
# ``uuid5`` ids for the skeleton; the assertion only enforces "real UUID,
# never a ``type_`` slug", which uuid5 satisfies.
UUID_RE = re.compile(r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$")

# The only names the seeder may ever create.
SEED_NAMES = {
    "root",
    "node",
    "entity",
    "concept",
    "process",
    "cognition",
    # System-reserved scaffolding -- seeded, untouched by the content engine.
    "reserved_node",
    "reserved_agent",
    "reserved_process",
    "reserved_action",
    "reserved_goal",
    "reserved_plan",
    "reserved_simulation",
    "reserved_execution",
    "reserved_state",
    "reserved_media_sample",
}

# Names that must never be seeded (logos#515 design lock). object/location
# EMERGE as content types; the relation-vocabulary nodes are not seeded
# (only IS_A is used for now); reserved_* are SEEDED scaffolding, not cruft.
FORBIDDEN_SEED_NAMES = {
    "object",
    "location",
    "edge_type",
    "ENABLES",
    "ACHIEVES",
    "LOCATED_AT",
    "EXECUTES",
    "UPDATES",
    "REQUIRES",
    "CAUSES",
    "PRODUCES",
    "OBSERVES",
    "HAS_STATE",
    "PART_OF",
    "HAS_STEP",
    "GENERATES",
    "CONTAINS",
    "OCCUPIES",
}


class TestSeedTypeDefinitions:
    """Test suite for the seeded skeleton produced by seed_type_definitions."""

    def test_type_parents_is_the_locked_skeleton(self):
        """TYPE_PARENTS is exactly the fifteen reified IS_A edges of the skeleton."""
        assert TYPE_PARENTS == {
            "node": "root",
            "entity": "node",
            "concept": "node",
            "process": "node",
            "cognition": "node",
            "reserved_node": "node",
            "reserved_agent": "reserved_node",
            "reserved_process": "reserved_node",
            "reserved_action": "reserved_node",
            "reserved_goal": "reserved_node",
            "reserved_plan": "reserved_node",
            "reserved_simulation": "reserved_node",
            "reserved_execution": "reserved_node",
            "reserved_state": "reserved_node",
            "reserved_media_sample": "reserved_node",
        }

    def test_seed_creates_sixteen_nodes_and_fifteen_edges(self):
        """An empty store yields exactly 16 nodes and 15 IS_A assertions."""
        mock_client = Mock()
        seeder = HCGSeeder(client=mock_client)

        count = seeder.seed_type_definitions()

        assert count == 16
        assert mock_client.add_node.call_count == 16
        assert mock_client.add_edge.call_count == 15

    def test_seed_names_are_exactly_the_skeleton(self):
        """Seeder names are exactly the skeleton and never a forbidden name."""
        mock_client = Mock()
        seeder = HCGSeeder(client=mock_client)

        seeder.seed_type_definitions()

        names = {call.kwargs["name"] for call in mock_client.add_node.call_args_list}
        assert names == SEED_NAMES
        assert not (names & FORBIDDEN_SEED_NAMES)

    def test_seed_uuids_are_real_uuids_not_slugs(self):
        """Every seeded node uuid is a real UUID, never a ``type_`` slug."""
        mock_client = Mock()
        seeder = HCGSeeder(client=mock_client)

        seeder.seed_type_definitions()

        uuids = [call.kwargs["uuid"] for call in mock_client.add_node.call_args_list]
        assert len(uuids) == 16
        for value in uuids:
            assert not value.startswith("type_")
            assert UUID_RE.match(value), value

    def test_seed_is_idempotent_deterministic_uuid5(self):
        """Re-seeding mints the same sixteen uuid5 ids (MERGE no-ops, no growth)."""
        mock_client = Mock()
        # Echo the uuid back so type_uuids holds the real ids (mirrors the
        # real client, whose add_node MERGEs on uuid and returns it).
        mock_client.add_node.side_effect = lambda **kwargs: kwargs["uuid"]
        seeder = HCGSeeder(client=mock_client)

        seeder.seed_type_definitions()
        first = {
            call.kwargs["name"]: call.kwargs["uuid"]
            for call in mock_client.add_node.call_args_list
        }

        mock_client.add_node.reset_mock()
        seeder.seed_type_definitions()
        second = {
            call.kwargs["name"]: call.kwargs["uuid"]
            for call in mock_client.add_node.call_args_list
        }

        # uuid5 is deterministic: each name yields the identical uuid both runs.
        assert first == second
        assert set(first) == SEED_NAMES
        # The MERGE key (uuid) is stable, so the union across both runs is
        # exactly the sixteen skeleton ids -- a second seed adds no new nodes.
        assert set(first.values()) | set(second.values()) == set(first.values())
        assert len(set(first.values())) == 16


class TestSeedTypeCentroids:
    """Test suite for seed_type_centroids method."""

    def test_seed_type_centroids_calls_embed_and_update(self):
        """Test that seed_type_centroids embeds each type and updates centroids."""
        mock_client = Mock()
        # Echo uuids back so type_uuids holds real skeleton ids after seeding.
        mock_client.add_node.side_effect = lambda **kwargs: kwargs["uuid"]
        seeder = HCGSeeder(client=mock_client)

        # Centroids reference the skeleton node uuids, so the type definitions
        # must be seeded first; otherwise every centroid is skipped.
        seeder.seed_type_definitions()

        mock_embed_fn = Mock(return_value=[0.1] * 384)
        mock_milvus_sync = Mock()
        mock_milvus_sync.update_centroid.return_value = {"embedding_id": "test"}

        count = seeder.seed_type_centroids(
            embed_fn=mock_embed_fn,
            milvus_sync=mock_milvus_sync,
            model="all-MiniLM-L6-v2",
        )

        assert count == len(TYPE_PARENTS)
        assert mock_embed_fn.call_count == len(TYPE_PARENTS)
        assert mock_milvus_sync.update_centroid.call_count == len(TYPE_PARENTS)

        # Verify at least one call has the correct shape
        call_args = mock_milvus_sync.update_centroid.call_args_list[0]
        assert call_args.kwargs["centroid"] == [0.1] * 384
        assert call_args.kwargs["model"] == "all-MiniLM-L6-v2"

        # type_uuid is a real skeleton uuid, never a fabricated ``type_`` slug.
        type_uuid = call_args.kwargs["type_uuid"]
        assert not type_uuid.startswith("type_")
        assert UUID_RE.match(type_uuid), type_uuid

    def test_seed_type_centroids_skips_when_definitions_missing(self):
        """Without seeded definitions, centroids are skipped, not orphaned."""
        mock_client = Mock()
        seeder = HCGSeeder(client=mock_client)

        mock_embed_fn = Mock(return_value=[0.1] * 384)
        mock_milvus_sync = Mock()

        count = seeder.seed_type_centroids(
            embed_fn=mock_embed_fn,
            milvus_sync=mock_milvus_sync,
            model="all-MiniLM-L6-v2",
        )

        # No type_uuids on hand -> every centroid skipped, none written.
        assert count == 0
        assert mock_milvus_sync.update_centroid.call_count == 0
