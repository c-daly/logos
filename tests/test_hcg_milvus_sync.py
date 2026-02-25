"""
Tests for HCG-Milvus synchronization utilities.

These tests verify the bidirectional sync between Neo4j and Milvus,
implementing Section 4.2 of the LOGOS specification.

Note: These are unit tests that mock Milvus interactions.
Integration tests require a running Milvus instance.
"""

from datetime import datetime
from unittest.mock import Mock, patch
from uuid import uuid4

import pytest

from logos_hcg.sync import (
    COLLECTION_NAMES,
    HCGMilvusSync,
    MilvusSyncError,
)


class TestHCGMilvusSync:
    """Test suite for HCGMilvusSync class."""

    def test_collection_names_mapping(self):
        """Test that collection name mapping is correct."""
        assert COLLECTION_NAMES["Entity"] == "hcg_entity_embeddings"
        assert COLLECTION_NAMES["Concept"] == "hcg_concept_embeddings"
        assert COLLECTION_NAMES["State"] == "hcg_state_embeddings"
        assert COLLECTION_NAMES["Process"] == "hcg_process_embeddings"

    def test_type_centroid_collection_in_names(self):
        """Test that TypeCentroid collection is registered."""
        assert "TypeCentroid" in COLLECTION_NAMES
        assert COLLECTION_NAMES["TypeCentroid"] == "hcg_type_centroids"

    @patch("logos_hcg.sync.connections")
    @patch("logos_hcg.sync.utility")
    @patch("logos_hcg.sync.Collection")
    def test_connect_success(self, mock_collection, mock_utility, mock_connections):
        """Test successful connection to Milvus."""
        # Setup mocks
        mock_utility.has_collection.return_value = True
        mock_coll_instance = Mock()
        mock_collection.return_value = mock_coll_instance

        sync = HCGMilvusSync(milvus_host="localhost", milvus_port="19530")
        sync.connect()

        # Verify connection was established
        mock_connections.connect.assert_called_once_with(
            alias="default",
            host="localhost",
            port="19530",
            timeout=30.0,
        )
        assert sync._connected is True
        assert len(sync._collections) == 6

    @patch("logos_hcg.sync.connections")
    def test_connect_failure(self, mock_connections):
        """Test connection failure handling."""
        mock_connections.connect.side_effect = Exception("Connection failed")

        sync = HCGMilvusSync()
        with pytest.raises(MilvusSyncError, match="Failed to connect to Milvus"):
            sync.connect()

    @patch("logos_hcg.sync.connections")
    def test_disconnect(self, mock_connections):
        """Test disconnection from Milvus."""
        sync = HCGMilvusSync()
        sync._connected = True
        sync._collections = {"Entity": Mock()}

        sync.disconnect()

        mock_connections.disconnect.assert_called_once_with("default")
        assert sync._connected is False
        assert len(sync._collections) == 0

    @patch("logos_hcg.sync.connections")
    @patch("logos_hcg.sync.utility")
    @patch("logos_hcg.sync.Collection")
    def test_context_manager(self, mock_collection, mock_utility, mock_connections):
        """Test using HCGMilvusSync as context manager."""
        mock_utility.has_collection.return_value = True

        with HCGMilvusSync() as sync:
            assert sync._connected is True

        # Verify disconnect was called
        mock_connections.disconnect.assert_called_once()

    @patch("logos_hcg.sync.connections")
    @patch("logos_hcg.sync.utility")
    @patch("logos_hcg.sync.Collection")
    def test_upsert_embedding_success(
        self, mock_collection, mock_utility, mock_connections
    ):
        """Test successful embedding upsert."""
        # Setup mocks
        mock_utility.has_collection.return_value = True
        mock_coll_instance = Mock()
        mock_collection.return_value = mock_coll_instance

        sync = HCGMilvusSync()
        sync.connect()

        # Upsert embedding
        test_uuid = str(uuid4())
        test_embedding = [0.1] * 384
        test_model = "test-model"

        metadata = sync.upsert_embedding(
            node_type="Entity",
            uuid=test_uuid,
            embedding=test_embedding,
            model=test_model,
        )

        # Verify collection operations
        mock_coll_instance.insert.assert_called_once()
        mock_coll_instance.flush.assert_called_once()

        # Verify returned metadata
        assert metadata["embedding_id"] == test_uuid
        assert metadata["embedding_model"] == test_model
        assert isinstance(metadata["last_sync"], datetime)

    def test_upsert_embedding_not_connected(self):
        """Test upsert fails when not connected."""
        sync = HCGMilvusSync()

        with pytest.raises(MilvusSyncError, match="Not connected to Milvus"):
            sync.upsert_embedding(
                node_type="Entity",
                uuid="test-uuid",
                embedding=[0.1] * 384,
                model="test-model",
            )

    @patch("logos_hcg.sync.connections")
    @patch("logos_hcg.sync.utility")
    @patch("logos_hcg.sync.Collection")
    def test_batch_upsert_embeddings(
        self, mock_collection, mock_utility, mock_connections
    ):
        """Test batch embedding upsert."""
        mock_utility.has_collection.return_value = True
        mock_coll_instance = Mock()
        mock_collection.return_value = mock_coll_instance

        sync = HCGMilvusSync()
        sync.connect()

        # Batch upsert
        embeddings = [
            {"uuid": str(uuid4()), "embedding": [0.1] * 384, "model": "model-1"},
            {"uuid": str(uuid4()), "embedding": [0.2] * 384, "model": "model-2"},
        ]

        metadata_list = sync.batch_upsert_embeddings(
            node_type="Entity",
            embeddings=embeddings,
        )

        # Verify batch operation
        mock_coll_instance.insert.assert_called_once()
        mock_coll_instance.flush.assert_called_once()

        # Verify metadata list
        assert len(metadata_list) == 2
        assert all(isinstance(m["last_sync"], datetime) for m in metadata_list)

    @patch("logos_hcg.sync.connections")
    @patch("logos_hcg.sync.utility")
    @patch("logos_hcg.sync.Collection")
    def test_batch_upsert_empty_list(
        self, mock_collection, mock_utility, mock_connections
    ):
        """Test batch upsert with empty list."""
        mock_utility.has_collection.return_value = True
        mock_collection.return_value = Mock()

        sync = HCGMilvusSync()
        sync.connect()

        metadata_list = sync.batch_upsert_embeddings(
            node_type="Entity",
            embeddings=[],
        )

        assert metadata_list == []

    @patch("logos_hcg.sync.connections")
    @patch("logos_hcg.sync.utility")
    @patch("logos_hcg.sync.Collection")
    def test_delete_embedding(self, mock_collection, mock_utility, mock_connections):
        """Test embedding deletion."""
        mock_utility.has_collection.return_value = True
        mock_coll_instance = Mock()
        mock_collection.return_value = mock_coll_instance

        sync = HCGMilvusSync()
        sync.connect()

        # Delete embedding
        test_uuid = str(uuid4())
        result = sync.delete_embedding(node_type="Entity", uuid=test_uuid)

        # Verify delete operation
        mock_coll_instance.delete.assert_called_once()
        mock_coll_instance.flush.assert_called_once()
        assert result is True

    @patch("logos_hcg.sync.connections")
    @patch("logos_hcg.sync.utility")
    @patch("logos_hcg.sync.Collection")
    def test_batch_delete_embeddings(
        self, mock_collection, mock_utility, mock_connections
    ):
        """Test batch embedding deletion."""
        mock_utility.has_collection.return_value = True
        mock_coll_instance = Mock()
        mock_collection.return_value = mock_coll_instance

        sync = HCGMilvusSync()
        sync.connect()

        # Batch delete
        uuids = [str(uuid4()), str(uuid4()), str(uuid4())]
        count = sync.batch_delete_embeddings(node_type="Entity", uuids=uuids)

        # Verify delete operation
        mock_coll_instance.delete.assert_called_once()
        mock_coll_instance.flush.assert_called_once()
        assert count == 3

    @patch("logos_hcg.sync.connections")
    @patch("logos_hcg.sync.utility")
    @patch("logos_hcg.sync.Collection")
    def test_batch_delete_empty_list(
        self, mock_collection, mock_utility, mock_connections
    ):
        """Test batch delete with empty list."""
        mock_utility.has_collection.return_value = True
        mock_collection.return_value = Mock()

        sync = HCGMilvusSync()
        sync.connect()

        count = sync.batch_delete_embeddings(node_type="Entity", uuids=[])
        assert count == 0

    @patch("logos_hcg.sync.connections")
    @patch("logos_hcg.sync.utility")
    @patch("logos_hcg.sync.Collection")
    def test_get_embedding_found(self, mock_collection, mock_utility, mock_connections):
        """Test retrieving an existing embedding."""
        mock_utility.has_collection.return_value = True
        mock_coll_instance = Mock()
        test_uuid = str(uuid4())
        mock_coll_instance.query.return_value = [
            {
                "uuid": test_uuid,
                "embedding": [0.1] * 384,
                "embedding_model": "test-model",
                "last_sync": 1234567890,
            }
        ]
        mock_collection.return_value = mock_coll_instance

        sync = HCGMilvusSync()
        sync.connect()

        # Get embedding
        result = sync.get_embedding(node_type="Entity", uuid=test_uuid)

        # Verify result
        assert result is not None
        assert result["uuid"] == test_uuid
        assert result["embedding_model"] == "test-model"

    @patch("logos_hcg.sync.connections")
    @patch("logos_hcg.sync.utility")
    @patch("logos_hcg.sync.Collection")
    def test_get_embedding_not_found(
        self, mock_collection, mock_utility, mock_connections
    ):
        """Test retrieving a non-existent embedding."""
        mock_utility.has_collection.return_value = True
        mock_coll_instance = Mock()
        mock_coll_instance.query.return_value = []
        mock_collection.return_value = mock_coll_instance

        sync = HCGMilvusSync()
        sync.connect()

        result = sync.get_embedding(node_type="Entity", uuid="nonexistent-uuid")
        assert result is None

    @patch("logos_hcg.sync.connections")
    @patch("logos_hcg.sync.utility")
    @patch("logos_hcg.sync.Collection")
    def test_verify_sync_in_sync(self, mock_collection, mock_utility, mock_connections):
        """Test sync verification when databases are in sync."""
        mock_utility.has_collection.return_value = True
        mock_coll_instance = Mock()

        # Milvus has same UUIDs as Neo4j
        neo4j_uuids = {"uuid-1", "uuid-2", "uuid-3"}
        mock_coll_instance.query.return_value = [
            {"uuid": "uuid-1"},
            {"uuid": "uuid-2"},
            {"uuid": "uuid-3"},
        ]
        mock_collection.return_value = mock_coll_instance

        sync = HCGMilvusSync()
        sync.connect()

        report = sync.verify_sync(node_type="Entity", neo4j_uuids=neo4j_uuids)

        assert report["in_sync"] is True
        assert report["neo4j_count"] == 3
        assert report["milvus_count"] == 3
        assert len(report["orphaned_embeddings"]) == 0
        assert len(report["missing_embeddings"]) == 0

    @patch("logos_hcg.sync.connections")
    @patch("logos_hcg.sync.utility")
    @patch("logos_hcg.sync.Collection")
    def test_verify_sync_orphaned_embeddings(
        self, mock_collection, mock_utility, mock_connections
    ):
        """Test sync verification with orphaned embeddings."""
        mock_utility.has_collection.return_value = True
        mock_coll_instance = Mock()

        # Milvus has extra UUIDs not in Neo4j
        neo4j_uuids = {"uuid-1", "uuid-2"}
        mock_coll_instance.query.return_value = [
            {"uuid": "uuid-1"},
            {"uuid": "uuid-2"},
            {"uuid": "uuid-orphaned"},
        ]
        mock_collection.return_value = mock_coll_instance

        sync = HCGMilvusSync()
        sync.connect()

        report = sync.verify_sync(node_type="Entity", neo4j_uuids=neo4j_uuids)

        assert report["in_sync"] is False
        assert report["neo4j_count"] == 2
        assert report["milvus_count"] == 3
        assert "uuid-orphaned" in report["orphaned_embeddings"]
        assert len(report["missing_embeddings"]) == 0

    @patch("logos_hcg.sync.connections")
    @patch("logos_hcg.sync.utility")
    @patch("logos_hcg.sync.Collection")
    def test_verify_sync_missing_embeddings(
        self, mock_collection, mock_utility, mock_connections
    ):
        """Test sync verification with missing embeddings."""
        mock_utility.has_collection.return_value = True
        mock_coll_instance = Mock()

        # Neo4j has UUIDs not in Milvus
        neo4j_uuids = {"uuid-1", "uuid-2", "uuid-missing"}
        mock_coll_instance.query.return_value = [
            {"uuid": "uuid-1"},
            {"uuid": "uuid-2"},
        ]
        mock_collection.return_value = mock_coll_instance

        sync = HCGMilvusSync()
        sync.connect()

        report = sync.verify_sync(node_type="Entity", neo4j_uuids=neo4j_uuids)

        assert report["in_sync"] is False
        assert report["neo4j_count"] == 3
        assert report["milvus_count"] == 2
        assert len(report["orphaned_embeddings"]) == 0
        assert "uuid-missing" in report["missing_embeddings"]

    @patch("logos_hcg.sync.connections")
    @patch("logos_hcg.sync.utility")
    @patch("logos_hcg.sync.Collection")
    def test_health_check_connected(
        self, mock_collection, mock_utility, mock_connections
    ):
        """Test health check when connected."""
        mock_utility.has_collection.return_value = True
        mock_coll_instance = Mock()
        mock_coll_instance.num_entities = 42
        mock_collection.return_value = mock_coll_instance

        sync = HCGMilvusSync()
        sync.connect()

        health = sync.health_check()

        assert health["connected"] is True
        assert len(health["collections"]) == 6
        # All collections should exist and be loaded
        for _node_type, status in health["collections"].items():
            assert status["exists"] is True
            assert status["loaded"] is True
            assert status["count"] == 42

    def test_health_check_not_connected(self):
        """Test health check when not connected."""
        sync = HCGMilvusSync()

        health = sync.health_check()

        assert health["connected"] is False
        assert len(health["collections"]) == 0

    @patch("logos_hcg.sync.connections")
    @patch("logos_hcg.sync.utility")
    @patch("logos_hcg.sync.Collection")
    def test_health_check_collection_not_loaded(
        self, mock_collection, mock_utility, mock_connections
    ):
        """Test health check with unloaded collection."""

        def has_collection_side_effect(name, using):
            return name == "hcg_entity_embeddings"

        mock_utility.has_collection.side_effect = has_collection_side_effect
        mock_coll_instance = Mock()
        # Simulate collection not loaded (accessing num_entities raises exception)
        type(mock_coll_instance).num_entities = property(
            lambda self: (_ for _ in ()).throw(Exception("Not loaded"))
        )
        mock_collection.return_value = mock_coll_instance

        sync = HCGMilvusSync()
        sync.connect()

        health = sync.health_check()

        assert health["connected"] is True
        # Entity collection exists but not loaded
        assert health["collections"]["Entity"]["exists"] is True
        assert health["collections"]["Entity"]["loaded"] is False
        # Other collections don't exist
        for node_type in ["Concept", "State", "Process"]:
            assert health["collections"][node_type]["exists"] is False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
