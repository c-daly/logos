"""Tests for HCG seeder type centroid seeding."""

from unittest.mock import Mock

from logos_hcg.seeder import HCGSeeder, TYPE_PARENTS


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
        assert call_args.kwargs["type_uuid"].startswith("type_")
