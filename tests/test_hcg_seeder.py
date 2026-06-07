"""Tests for HCG seeder skeleton seeding and type centroid seeding."""

import re
from unittest.mock import Mock

from logos_hcg.seeder import TYPE_PARENTS, HCGSeeder

# uuid4 string form, e.g. "f47ac10b-58cc-4372-a567-0e02b2c3d479".
UUID4_RE = re.compile(
    r"^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$"
)

# The only names the seeder may ever create.
SEED_NAMES = {"root", "node", "entity", "concept", "process", "cognition"}

# Names that must never be seeded as vocabulary nodes (logos#515 design lock).
FORBIDDEN_SEED_NAMES = {
    "object",
    "location",
    "edge_type",
    "reserved_action",
    "reserved_agent",
    "reserved_execution",
    "reserved_goal",
    "reserved_media_sample",
    "reserved_node",
    "reserved_plan",
    "reserved_process",
    "reserved_simulation",
    "reserved_state",
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
        """TYPE_PARENTS is exactly the five reified IS_A edges of the skeleton."""
        assert TYPE_PARENTS == {
            "node": "root",
            "entity": "node",
            "concept": "node",
            "process": "node",
            "cognition": "node",
        }

    def test_seed_creates_six_nodes_and_five_edges(self):
        """An empty store yields exactly 6 nodes and 5 IS_A assertions."""
        mock_client = Mock()
        seeder = HCGSeeder(client=mock_client)

        count = seeder.seed_type_definitions()

        assert count == 6
        assert mock_client.add_node.call_count == 6
        assert mock_client.add_edge.call_count == 5

    def test_seed_names_are_exactly_the_skeleton(self):
        """Seeder names are exactly the skeleton and never a forbidden name."""
        mock_client = Mock()
        seeder = HCGSeeder(client=mock_client)

        seeder.seed_type_definitions()

        names = {call.kwargs["name"] for call in mock_client.add_node.call_args_list}
        assert names == SEED_NAMES
        assert not (names & FORBIDDEN_SEED_NAMES)

    def test_seed_uuids_are_uuid4_not_slugs(self):
        """Every seeded node uuid is a real uuid4, never a ``type_`` slug."""
        mock_client = Mock()
        seeder = HCGSeeder(client=mock_client)

        seeder.seed_type_definitions()

        uuids = [call.kwargs["uuid"] for call in mock_client.add_node.call_args_list]
        assert len(uuids) == 6
        for value in uuids:
            assert not value.startswith("type_")
            assert UUID4_RE.match(value), value


class TestSeedTypeCentroids:
    """Test suite for seed_type_centroids method."""

    def test_seed_type_centroids_calls_embed_and_update(self):
        """Test that seed_type_centroids embeds each type and updates centroids."""
        mock_client = Mock()
        seeder = HCGSeeder(client=mock_client)

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

        # type_uuid is now a real uuid4, never a fabricated ``type_`` slug.
        type_uuid = call_args.kwargs["type_uuid"]
        assert not type_uuid.startswith("type_")
        assert UUID4_RE.match(type_uuid), type_uuid
