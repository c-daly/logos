"""
Tests for Milvus collection initialization

Verifies that the init_milvus_collections.py script correctly creates
and configures collections for HCG embeddings.

These tests require a running Milvus instance. The host and port can be
configured via MILVUS_HOST and MILVUS_PORT environment variables.
If Milvus is not available, tests will be skipped.
"""

import os

import pytest
from pymilvus import Collection, MilvusException, connections, utility

# Expected collections per Section 4.1 (Core Ontology)
EXPECTED_COLLECTIONS = [
    "hcg_entity_embeddings",
    "hcg_concept_embeddings",
    "hcg_state_embeddings",
    "hcg_process_embeddings",
]

# Expected schema fields
EXPECTED_FIELDS = ["uuid", "embedding", "embedding_model", "last_sync"]

# Test configuration - can be overridden with environment variables
MILVUS_HOST = os.getenv("MILVUS_HOST", "localhost")
MILVUS_PORT = os.getenv("MILVUS_PORT", "19530")


def _check_milvus_available():
    """Check if Milvus is available for testing."""
    try:
        connections.connect(
            alias="test_connection",
            host=MILVUS_HOST,
            port=MILVUS_PORT,
        )
        connections.disconnect("test_connection")
        return True
    except Exception:
        return False


# Skip all tests in this module if Milvus is not available
pytestmark = pytest.mark.skipif(
    not _check_milvus_available(),
    reason=f"Milvus is not available on {MILVUS_HOST}:{MILVUS_PORT}",
)


@pytest.fixture(scope="module")
def milvus_connection():
    """Connect to Milvus for testing."""
    try:
        connections.connect(
            alias="default",
            host=MILVUS_HOST,
            port=MILVUS_PORT,
        )
        yield
    except MilvusException as e:
        pytest.skip(f"Cannot connect to Milvus: {e}")
    finally:
        try:
            connections.disconnect("default")
        except Exception:
            pass


class TestMilvusCollections:
    """Test suite for Milvus collection configuration."""

    def test_all_collections_exist(self, milvus_connection):
        """Verify that all required HCG collections exist."""
        for collection_name in EXPECTED_COLLECTIONS:
            assert utility.has_collection(collection_name), (
                f"Collection {collection_name} does not exist. "
                "Run 'infra/init_milvus.sh' to initialize collections."
            )

    def test_collection_schemas(self, milvus_connection):
        """Verify that collections have the correct schema."""
        for collection_name in EXPECTED_COLLECTIONS:
            if not utility.has_collection(collection_name):
                pytest.skip(f"Collection {collection_name} not initialized")

            collection = Collection(name=collection_name)
            field_names = [field.name for field in collection.schema.fields]

            for expected_field in EXPECTED_FIELDS:
                assert (
                    expected_field in field_names
                ), f"Field {expected_field} missing from {collection_name}"

    def test_uuid_is_primary_key(self, milvus_connection):
        """Verify that uuid field is configured as primary key."""
        for collection_name in EXPECTED_COLLECTIONS:
            if not utility.has_collection(collection_name):
                pytest.skip(f"Collection {collection_name} not initialized")

            collection = Collection(name=collection_name)

            # Find the uuid field
            uuid_field = None
            for field in collection.schema.fields:
                if field.name == "uuid":
                    uuid_field = field
                    break

            assert uuid_field is not None, f"uuid field not found in {collection_name}"
            assert (
                uuid_field.is_primary
            ), f"uuid is not primary key in {collection_name}"

    def test_embedding_field_dimension(self, milvus_connection):
        """Verify that embedding field has correct dimension."""
        for collection_name in EXPECTED_COLLECTIONS:
            if not utility.has_collection(collection_name):
                pytest.skip(f"Collection {collection_name} not initialized")

            collection = Collection(name=collection_name)

            # Find the embedding field
            embedding_field = None
            for field in collection.schema.fields:
                if field.name == "embedding":
                    embedding_field = field
                    break

            assert (
                embedding_field is not None
            ), f"embedding field not found in {collection_name}"
            # Default dimension is 384, but allow other values
            assert (
                embedding_field.params["dim"] > 0
            ), f"Invalid embedding dimension in {collection_name}"

    def test_index_exists(self, milvus_connection):
        """Verify that an index exists on the embedding field."""
        for collection_name in EXPECTED_COLLECTIONS:
            if not utility.has_collection(collection_name):
                pytest.skip(f"Collection {collection_name} not initialized")

            collection = Collection(name=collection_name)

            # Get index information
            indexes = collection.indexes

            # Should have at least one index on the embedding field
            assert len(indexes) > 0, f"No indexes found on {collection_name}"

            # Verify index is on the embedding field
            embedding_indexed = False
            for index in indexes:
                if index.field_name == "embedding":
                    embedding_indexed = True
                    break

            assert (
                embedding_indexed
            ), f"No index on 'embedding' field in {collection_name}"

    def test_collection_descriptions(self, milvus_connection):
        """Verify that collections have appropriate descriptions."""
        for collection_name in EXPECTED_COLLECTIONS:
            if not utility.has_collection(collection_name):
                pytest.skip(f"Collection {collection_name} not initialized")

            collection = Collection(name=collection_name)

            # Schema should have a description
            assert (
                collection.schema.description
            ), f"Collection {collection_name} missing description"
            assert (
                "HCG" in collection.schema.description
                or "Embeddings" in collection.schema.description
            ), f"Collection {collection_name} description doesn't mention HCG or Embeddings"


class TestMilvusIntegration:
    """Integration tests for Milvus functionality."""

    def test_insert_and_search(self, milvus_connection):
        """Test basic insert and search operations."""
        import time

        collection_name = "hcg_entity_embeddings"
        if not utility.has_collection(collection_name):
            pytest.skip(f"Collection {collection_name} not initialized")

        collection = Collection(name=collection_name)

        # Get embedding dimension
        embedding_dim = None
        for field in collection.schema.fields:
            if field.name == "embedding":
                embedding_dim = field.params["dim"]
                break

        assert embedding_dim is not None, "Could not determine embedding dimension"

        # Insert a test entity
        test_uuid = f"test-entity-{int(time.time())}"
        test_embedding = [0.1] * embedding_dim
        test_model = "test-model"
        test_timestamp = int(time.time())

        data = [
            [test_uuid],
            [test_embedding],
            [test_model],
            [test_timestamp],
        ]

        collection.insert(data)
        collection.flush()

        # Verify insert succeeded
        assert collection.num_entities > 0, "No entities in collection after insert"

        # Search for similar vectors
        search_params = {"metric_type": "L2", "params": {"nprobe": 10}}
        results = collection.search(
            data=[test_embedding],
            anns_field="embedding",
            param=search_params,
            limit=1,
        )

        assert len(results) > 0, "Search returned no results"
        assert len(results[0]) > 0, "No matches found for test entity"

        # Clean up - delete the test entity
        collection.delete(f"uuid in ['{test_uuid}']")
        collection.flush()
