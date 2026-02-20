#!/usr/bin/env python3
"""
LOGOS Milvus Collection Initialization Script

This script initializes Milvus collections for the Hybrid Causal Graph (HCG) embeddings.
Reference: Section 4.2 (Vector Integration) and Section 5.2 (HCG Development Cluster)

Collections are created for each HCG node type:
- Entity embeddings
- Concept embeddings
- State embeddings
- Process embeddings

Each collection stores:
- uuid: Unique identifier matching the Neo4j node
- embedding: Vector representation for semantic search
- embedding_model: Model used to generate the embedding
- last_sync: Timestamp of last synchronization

Default embedding dimension: 384 (suitable for sentence-transformers models like all-MiniLM-L6-v2)
"""

import argparse
import sys

from pymilvus import (
    Collection,
    CollectionSchema,
    DataType,
    FieldSchema,
    connections,
    utility,
)

from logos_config import get_env_value

# Default configuration
DEFAULT_HOST = "localhost"
DEFAULT_PORT = "19530"
try:
    DEFAULT_EMBEDDING_DIM = int(
        get_env_value("LOGOS_EMBEDDING_DIM", default="384") or "384"
    )
except (ValueError, TypeError):
    DEFAULT_EMBEDDING_DIM = 384
DEFAULT_INDEX_TYPE = "IVF_FLAT"  # Simple and effective for development
DEFAULT_METRIC_TYPE = "L2"  # Euclidean distance for semantic similarity


def create_collection_schema(
    collection_name: str, embedding_dim: int = DEFAULT_EMBEDDING_DIM
) -> CollectionSchema:
    """
    Create a Milvus collection schema for HCG node embeddings.

    Args:
        collection_name: Name of the collection
        embedding_dim: Dimension of embedding vectors

    Returns:
        CollectionSchema configured for HCG embeddings
    """
    fields = [
        # Primary key - matches Neo4j node UUID
        FieldSchema(
            name="uuid",
            dtype=DataType.VARCHAR,
            max_length=256,
            is_primary=True,
            description=f"Unique identifier for {collection_name}",
        ),
        # Vector embedding
        FieldSchema(
            name="embedding",
            dtype=DataType.FLOAT_VECTOR,
            dim=embedding_dim,
            description="Vector embedding for semantic search",
        ),
        # Metadata fields
        FieldSchema(
            name="embedding_model",
            dtype=DataType.VARCHAR,
            max_length=128,
            description="Model used to generate the embedding",
        ),
        FieldSchema(
            name="last_sync",
            dtype=DataType.INT64,
            description="Unix timestamp of last synchronization with Neo4j",
        ),
    ]

    schema = CollectionSchema(
        fields=fields,
        description=f"Embeddings for HCG {collection_name} nodes",
    )

    return schema


def create_index(collection: Collection, index_type: str = DEFAULT_INDEX_TYPE) -> None:
    """
    Create an index on the embedding field for efficient similarity search.

    Args:
        collection: Milvus collection
        index_type: Type of index to create
    """
    index_params = {
        "index_type": index_type,
        "metric_type": DEFAULT_METRIC_TYPE,
        "params": {"nlist": 128},  # Number of cluster units
    }

    collection.create_index(
        field_name="embedding",
        index_params=index_params,
    )
    print(f"  ✓ Created index on 'embedding' field ({index_type})")


def init_collection(
    collection_name: str,
    embedding_dim: int = DEFAULT_EMBEDDING_DIM,
    force: bool = False,
) -> Collection:
    """
    Initialize a Milvus collection for HCG embeddings.

    Args:
        collection_name: Name of the collection to create
        embedding_dim: Dimension of embedding vectors
        force: If True, drop existing collection before creating

    Returns:
        Created or existing Collection
    """
    print(f"\nInitializing collection: {collection_name}")

    # Check if collection already exists
    if utility.has_collection(collection_name):
        if force:
            print(f"  ⚠ Dropping existing collection: {collection_name}")
            utility.drop_collection(collection_name)
        else:
            print(f"  ℹ Collection already exists: {collection_name}")
            collection = Collection(name=collection_name)
            print("  ✓ Loaded existing collection")
            return collection

    # Create new collection
    schema = create_collection_schema(collection_name, embedding_dim)
    collection = Collection(
        name=collection_name,
        schema=schema,
        using="default",
    )
    print(f"  ✓ Created collection with {embedding_dim}-dimensional vectors")

    # Create index
    create_index(collection)

    # Load collection into memory
    collection.load()
    print("  ✓ Collection loaded into memory")

    return collection


def init_all_collections(
    embedding_dim: int = DEFAULT_EMBEDDING_DIM,
    force: bool = False,
) -> dict[str, Collection]:
    """
    Initialize all HCG collections (Entity, Concept, State, Process).

    Args:
        embedding_dim: Dimension of embedding vectors
        force: If True, drop existing collections before creating

    Returns:
        Dictionary mapping collection names to Collection objects
    """
    # HCG node types from Section 4.1
    collection_names = [
        "hcg_entity_embeddings",
        "hcg_concept_embeddings",
        "hcg_state_embeddings",
        "hcg_process_embeddings",
    ]

    collections = {}
    for name in collection_names:
        collections[name] = init_collection(name, embedding_dim, force)

    return collections


def verify_collections() -> bool:
    """
    Verify that all HCG collections exist and are properly configured.

    Returns:
        True if all collections are valid, False otherwise
    """
    print("\n=== Verifying Collections ===")

    expected_collections = [
        "hcg_entity_embeddings",
        "hcg_concept_embeddings",
        "hcg_state_embeddings",
        "hcg_process_embeddings",
    ]

    all_valid = True
    for name in expected_collections:
        if not utility.has_collection(name):
            print(f"✗ Collection missing: {name}")
            all_valid = False
        else:
            collection = Collection(name=name)
            print(f"✓ Collection exists: {name}")
            print(f"  - Entities: {collection.num_entities}")
            print(f"  - Schema: {len(collection.schema.fields)} fields")

    return all_valid


def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(
        description="Initialize Milvus collections for LOGOS HCG embeddings"
    )
    parser.add_argument(
        "--host",
        default=DEFAULT_HOST,
        help=f"Milvus server host (default: {DEFAULT_HOST})",
    )
    parser.add_argument(
        "--port",
        default=DEFAULT_PORT,
        help=f"Milvus server port (default: {DEFAULT_PORT})",
    )
    parser.add_argument(
        "--embedding-dim",
        type=int,
        default=DEFAULT_EMBEDDING_DIM,
        help=f"Embedding dimension (default: {DEFAULT_EMBEDDING_DIM})",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Drop and recreate collections if they exist",
    )
    parser.add_argument(
        "--verify-only",
        action="store_true",
        help="Only verify collections, don't create them",
    )

    args = parser.parse_args()

    print("=== LOGOS Milvus Collection Initialization ===")
    print(f"Connecting to Milvus at {args.host}:{args.port}...")

    try:
        # Connect to Milvus
        connections.connect(
            alias="default",
            host=args.host,
            port=args.port,
        )
        print("✓ Connected to Milvus")

        if args.verify_only:
            # Just verify collections
            success = verify_collections()
        else:
            # Initialize collections
            collections = init_all_collections(
                embedding_dim=args.embedding_dim,
                force=args.force,
            )
            print(f"\n✓ Successfully initialized {len(collections)} collections")

            # Verify
            success = verify_collections()

        if success:
            print("\n=== Initialization Complete ===")
            return 0
        else:
            print("\n⚠ Some collections are invalid")
            return 1

    except Exception as e:
        print(f"\n✗ Error: {e}", file=sys.stderr)
        return 1
    finally:
        connections.disconnect("default")


if __name__ == "__main__":
    sys.exit(main())
