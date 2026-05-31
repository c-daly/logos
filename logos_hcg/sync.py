"""
HCG-Milvus Synchronization Utility

This module provides bidirectional synchronization between Neo4j graph nodes
and Milvus vector embeddings, implementing Section 4.2 of the LOGOS specification.

Key features:
- Upsert embeddings to Milvus with metadata tracking
- Sync metadata back to Neo4j nodes
- Batch operations for efficiency
- Delete synchronization (cascade deletes)
- Health checks for consistency verification

See Project LOGOS spec: Section 4.2 (Vector Integration)
"""

import logging
from datetime import UTC, datetime
from typing import Any, Literal, cast
from uuid import UUID

from pymilvus import Collection, connections, utility

logger = logging.getLogger(__name__)


def _collection_embedding_dim(collection: Any) -> int | None:
    """Return the dim of a collection's ``embedding`` FLOAT_VECTOR field, or None."""
    for field in collection.schema.fields:
        if field.name == "embedding":
            params = getattr(field, "params", None) or {}
            return params.get("dim")
    return None


# Collection name mapping for HCG node types
COLLECTION_NAMES = {
    "Entity": "hcg_entity_embeddings",
    "Concept": "hcg_concept_embeddings",
    "State": "hcg_state_embeddings",
    "Process": "hcg_process_embeddings",
    "Edge": "hcg_edge_embeddings",
    "TypeCentroid": "hcg_type_centroids",
}

NodeType = Literal["Entity", "Concept", "State", "Process", "Edge", "TypeCentroid"]


class MilvusSyncError(Exception):
    """Raised when synchronization with Milvus fails."""

    pass


class HCGMilvusSync:
    """
    Synchronization manager for HCG-Milvus bidirectional sync.

    Handles:
    - Upserting embeddings to Milvus
    - Tracking metadata in Neo4j
    - Batch operations
    - Delete synchronization
    - Consistency verification

    Example:
        sync = HCGMilvusSync(milvus_host="localhost", milvus_port="19530")
        sync.upsert_embedding(
            node_type="Entity",
            uuid="entity-uuid",
            embedding=[0.1, 0.2, ...],
            model="sentence-transformers/all-MiniLM-L6-v2"
        )
    """

    DEFAULT_TIMEOUT: float = 30.0

    def __init__(
        self,
        milvus_host: str = "localhost",
        milvus_port: str = "19530",
        alias: str = "default",
        timeout: float | None = None,
    ):
        """
        Initialize sync manager with Milvus connection.

        Args:
            milvus_host: Milvus server host
            milvus_port: Milvus server port
            alias: Connection alias for Milvus
            timeout: Timeout in seconds for Milvus operations (default: 30s)
        """
        self.host = milvus_host
        self.port = milvus_port
        self.alias = alias
        self.timeout = timeout if timeout is not None else self.DEFAULT_TIMEOUT
        self._connected = False
        self._collections: dict[str, Collection] = {}

    def connect(self) -> None:
        """
        Establish connection to Milvus and load collections.

        Raises:
            MilvusSyncError: If connection fails
        """
        try:
            connections.connect(
                alias=self.alias,
                host=self.host,
                port=self.port,
                timeout=self.timeout,
            )
            self._connected = True
            logger.info(f"Connected to Milvus at {self.host}:{self.port}")

            # Load collections into memory
            for node_type, collection_name in COLLECTION_NAMES.items():
                if utility.has_collection(collection_name, using=self.alias):
                    collection = Collection(name=collection_name, using=self.alias)
                    try:
                        collection.load(timeout=self.timeout)
                    except Exception as load_err:
                        logger.warning(
                            f"Failed to load collection {collection_name} "
                            f"(timeout={self.timeout}s): {load_err}"
                        )
                        continue
                    self._collections[node_type] = collection
                    logger.debug(f"Loaded collection: {collection_name}")
                else:
                    logger.warning(f"Collection not found: {collection_name}")

        except MilvusSyncError:
            raise
        except Exception as e:
            raise MilvusSyncError(f"Failed to connect to Milvus: {e}") from e

    def ensure_collection(self, node_type: NodeType, dim: int) -> None:
        """Create/load the collection for ``node_type`` sized to ``dim``.

        If a collection already exists with a *different* embedding dimension it
        is dropped and recreated, so a stale-dim collection never silently
        rejects writes (logos#542). ``dim`` is the measured embedding length,
        resolved via ``logos_config.resolve_embedding_dim`` at the call site.
        """
        if not self._connected:
            raise MilvusSyncError("Not connected to Milvus. Call connect() first.")

        from pymilvus import CollectionSchema, DataType, FieldSchema

        # Fast path: already cached at the right dim — skip the Milvus round-trips
        # (has_collection + Collection introspection) that would otherwise run on
        # every upsert (gemini review on #543).
        cached = self._collections.get(node_type)
        if cached is not None and _collection_embedding_dim(cached) == dim:
            return

        name = COLLECTION_NAMES[node_type]
        if utility.has_collection(name, using=self.alias):
            existing = Collection(name=name, using=self.alias)
            primary = [
                f for f in existing.schema.fields if getattr(f, "is_primary", False)
            ]
            pk_ok = bool(primary) and primary[0].name == "uuid"
            existing_dim = _collection_embedding_dim(existing)
            if pk_ok and existing_dim == dim:
                existing.load(timeout=self.timeout)
                self._collections[node_type] = existing
                return
            # Recreate on a schema mismatch -- either the old auto_id INT64 'id'
            # primary key (which Milvus refuses to upsert by uuid, logos#533) or a
            # stale embedding dim (logos#542). The drop is intentional, not a
            # data-loss bug: a wrong-PK or wrong-dim collection's vectors are
            # unusable (384-dim rows can't be queried by a 1536-dim provider) and
            # embeddings regenerate from Neo4j down to the type baseline, so a
            # self-healing recreate is the desired behaviour.
            logger.warning(
                "Collection %s schema mismatch (pk=%r, dim=%s; want uuid/%s) -- "
                "dropping and recreating.",
                name,
                primary[0].name if primary else None,
                existing_dim,
                dim,
            )
            utility.drop_collection(name, using=self.alias)

        # uuid is the primary key (auto_id=False) so that upsert() replaces an
        # existing row keyed on the node UUID instead of appending a duplicate.
        # Schema mirrors infra/init_milvus_collections.py so the write path and
        # the read/classify/health paths agree on the collection layout.
        fields = [
            FieldSchema(
                name="uuid",
                dtype=DataType.VARCHAR,
                max_length=256,
                is_primary=True,
                auto_id=False,
            ),
            FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=dim),
            FieldSchema(name="embedding_model", dtype=DataType.VARCHAR, max_length=128),
            FieldSchema(name="last_sync", dtype=DataType.INT64),
        ]
        schema = CollectionSchema(fields, description=f"Embeddings for {node_type}")
        collection = Collection(name=name, schema=schema, using=self.alias)

        index_params = {
            "index_type": "IVF_FLAT",
            "metric_type": "L2",
            "params": {"nlist": 128},
        }
        collection.create_index("embedding", index_params)
        collection.load(timeout=self.timeout)
        self._collections[node_type] = collection
        logger.info(f"Created collection {name} with L2 IVF_FLAT index")

    def search_similar(
        self,
        node_type: NodeType,
        query_embedding: list[float],
        top_k: int = 10,
    ) -> list[dict]:
        """Search for similar embeddings in a node type collection.

        Args:
            node_type: Which collection to search
            query_embedding: Query vector (dimension must match collection schema)
            top_k: Number of results

        Returns:
            List of dicts with keys: uuid, score (L2 distance — lower is more similar)
        """
        collection = self._collections.get(node_type)
        if not collection:
            logger.warning(f"Collection for {node_type} not available")
            return []

        try:
            results = collection.search(
                data=[query_embedding],
                anns_field="embedding",
                param={"metric_type": "L2", "params": {"nprobe": 10}},
                limit=top_k,
                output_fields=["uuid"],
            )
            return [
                {"uuid": hit.entity.get("uuid"), "score": hit.distance}
                for hit in results[0]
            ]
        except Exception as e:
            logger.error(f"Embedding search failed for {node_type}: {e}")
            return []

    def update_centroid(
        self, type_uuid: str, centroid: list[float], model: str
    ) -> dict[str, Any]:
        """Upsert a type centroid embedding in the TypeCentroid collection."""
        return self.upsert_embedding(
            node_type="TypeCentroid", uuid=type_uuid, embedding=centroid, model=model
        )

    def find_nearest_types(
        self, query_embedding: list[float], top_k: int = 3
    ) -> list[dict]:
        """Find the nearest type centroids for a query embedding."""
        return self.search_similar(
            node_type="TypeCentroid", query_embedding=query_embedding, top_k=top_k
        )

    def disconnect(self) -> None:
        """Disconnect from Milvus."""
        if self._connected:
            connections.disconnect(self.alias)
            self._connected = False
            self._collections.clear()
            logger.info("Disconnected from Milvus")

    def __enter__(self):
        """Context manager entry."""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.disconnect()

    def _get_collection(self, node_type: NodeType) -> Collection:
        """
        Get Milvus collection for a node type.

        Args:
            node_type: Type of HCG node

        Returns:
            Milvus Collection object

        Raises:
            MilvusSyncError: If collection not available
        """
        if not self._connected:
            raise MilvusSyncError("Not connected to Milvus. Call connect() first.")

        if node_type not in self._collections:
            raise MilvusSyncError(
                f"Collection for {node_type} not loaded. "
                f"Run init_milvus_collections.py to create collections."
            )

        return self._collections[node_type]

    def upsert_embedding(
        self,
        node_type: NodeType,
        uuid: str | UUID,
        embedding: list[float],
        model: str,
    ) -> dict[str, Any]:
        """
        Upsert an embedding to Milvus with metadata.

        This creates or updates the embedding in Milvus and returns metadata
        that should be stored in the Neo4j node.

        Args:
            node_type: Type of HCG node (Entity, Concept, State, Process)
            uuid: Node UUID
            embedding: Vector embedding (dimensionality must match collection schema)
            model: Model name used to generate the embedding

        Returns:
            Dictionary with embedding metadata:
            {
                "embedding_id": str,
                "embedding_model": str,
                "last_sync": datetime
            }

        Raises:
            MilvusSyncError: If upsert fails
        """
        uuid_str = str(uuid)

        from logos_config import get_embedding_dim_override, resolve_embedding_dim

        self.ensure_collection(
            node_type,
            resolve_embedding_dim(len(embedding), get_embedding_dim_override()),
        )
        collection = self._get_collection(node_type)

        try:
            # uuid is the primary key (auto_id=False), so upsert() replaces the
            # existing row for this uuid rather than appending a duplicate.
            timestamp = int(datetime.now(UTC).timestamp())
            data = [
                [uuid_str],  # uuid (primary key)
                [embedding],  # embedding
                [model],  # embedding_model
                [timestamp],  # last_sync
            ]

            collection.upsert(data)
            collection.flush()

            logger.info(f"Upserted embedding for {node_type} {uuid_str}")

            return {
                "embedding_id": uuid_str,
                "embedding_model": model,
                "last_sync": datetime.now(UTC),
            }

        except Exception as e:
            raise MilvusSyncError(
                f"Failed to upsert embedding for {node_type} {uuid_str}: {e}"
            ) from e

    def batch_upsert_embeddings(
        self,
        node_type: NodeType,
        embeddings: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        """
        Batch upsert embeddings to Milvus.

        Args:
            node_type: Type of HCG node
            embeddings: List of dicts with keys: uuid, embedding, model

        Returns:
            List of embedding metadata dicts (one per input)

        Raises:
            MilvusSyncError: If batch upsert fails
        """
        if not embeddings:
            return []

        from logos_config import get_embedding_dim_override, resolve_embedding_dim

        # Size the collection to the *measured* embedding dim, recreating it if a
        # stale-dim collection exists (logos#542) instead of failing the insert.
        measured_dim = len(embeddings[0]["embedding"])
        self.ensure_collection(
            node_type,
            resolve_embedding_dim(measured_dim, get_embedding_dim_override()),
        )
        collection = self._get_collection(node_type)

        try:
            # Prepare batch data
            timestamp = int(datetime.now(UTC).timestamp())
            uuids = [str(e["uuid"]) for e in embeddings]
            vectors = [e["embedding"] for e in embeddings]
            models = [e["model"] for e in embeddings]
            timestamps = [timestamp] * len(embeddings)

            data = [uuids, vectors, models, timestamps]

            # uuid is the primary key, so upsert() replaces any existing rows for
            # these uuids rather than appending duplicates.
            collection.upsert(data)
            collection.flush()

            logger.info(f"Batch upserted {len(embeddings)} embeddings for {node_type}")

            # Return metadata for each embedding
            sync_time = datetime.now(UTC)
            return [
                {
                    "embedding_id": uuid,
                    "embedding_model": model,
                    "last_sync": sync_time,
                }
                for uuid, model in zip(uuids, models, strict=True)
            ]

        except Exception as e:
            raise MilvusSyncError(
                f"Failed to batch upsert embeddings for {node_type}: {e}"
            ) from e

    def delete_embedding(
        self,
        node_type: NodeType,
        uuid: str | UUID,
    ) -> bool:
        """
        Delete an embedding from Milvus.

        This should be called when a node is deleted from Neo4j to maintain sync.

        Args:
            node_type: Type of HCG node
            uuid: Node UUID

        Returns:
            True if deletion was successful

        Raises:
            MilvusSyncError: If deletion fails
        """
        uuid_str = str(uuid)
        collection = self._get_collection(node_type)

        try:
            # Delete by primary key
            expr = f'uuid == "{uuid_str}"'
            collection.delete(expr)
            collection.flush()

            logger.info(f"Deleted embedding for {node_type} {uuid_str}")
            return True

        except Exception as e:
            raise MilvusSyncError(
                f"Failed to delete embedding for {node_type} {uuid_str}: {e}"
            ) from e

    def batch_delete_embeddings(
        self,
        node_type: NodeType,
        uuids: list[str | UUID],
    ) -> int:
        """
        Batch delete embeddings from Milvus.

        Args:
            node_type: Type of HCG node
            uuids: List of node UUIDs to delete

        Returns:
            Number of embeddings deleted

        Raises:
            MilvusSyncError: If batch deletion fails
        """
        if not uuids:
            return 0

        collection = self._get_collection(node_type)
        uuid_strs = [str(u) for u in uuids]

        try:
            # Build delete expression (OR of all UUIDs)
            uuid_list = ", ".join([f'"{u}"' for u in uuid_strs])
            expr = f"uuid in [{uuid_list}]"
            collection.delete(expr)
            collection.flush()

            logger.info(f"Batch deleted {len(uuids)} embeddings for {node_type}")
            return len(uuids)

        except Exception as e:
            raise MilvusSyncError(
                f"Failed to batch delete embeddings for {node_type}: {e}"
            ) from e

    def get_embedding(
        self,
        node_type: NodeType,
        uuid: str | UUID,
    ) -> dict[str, Any] | None:
        """
        Retrieve an embedding and its metadata from Milvus.

        Args:
            node_type: Type of HCG node
            uuid: Node UUID

        Returns:
            Dictionary with embedding data or None if not found:
            {
                "uuid": str,
                "embedding": list[float],
                "embedding_model": str,
                "last_sync": int (unix timestamp)
            }

        Raises:
            MilvusSyncError: If query fails
        """
        uuid_str = str(uuid)
        collection = self._get_collection(node_type)

        try:
            # Query by primary key
            expr = f'uuid == "{uuid_str}"'
            results = collection.query(
                expr=expr,
                output_fields=["uuid", "embedding", "embedding_model", "last_sync"],
            )

            if not results:
                return None

            return cast(dict[str, Any], results[0])

        except Exception as e:
            raise MilvusSyncError(
                f"Failed to get embedding for {node_type} {uuid_str}: {e}"
            ) from e

    def verify_sync(
        self,
        node_type: NodeType,
        neo4j_uuids: set[str],
    ) -> dict[str, Any]:
        """
        Verify synchronization consistency between Neo4j and Milvus.

        Compares the set of UUIDs in Neo4j with those in Milvus to detect:
        - Orphaned embeddings (in Milvus but not in Neo4j)
        - Missing embeddings (in Neo4j but not in Milvus)

        Args:
            node_type: Type of HCG node
            neo4j_uuids: Set of UUIDs from Neo4j for this node type

        Returns:
            Dictionary with consistency report:
            {
                "in_sync": bool,
                "neo4j_count": int,
                "milvus_count": int,
                "orphaned_embeddings": list[str],  # In Milvus but not Neo4j
                "missing_embeddings": list[str],   # In Neo4j but not Milvus
            }

        Raises:
            MilvusSyncError: If verification fails
        """
        collection = self._get_collection(node_type)

        try:
            # Get all UUIDs from Milvus
            results = collection.query(
                expr="uuid != ''",  # Match all
                output_fields=["uuid"],
            )
            milvus_uuids = {r["uuid"] for r in results}

            # Find discrepancies
            orphaned = milvus_uuids - neo4j_uuids
            missing = neo4j_uuids - milvus_uuids

            report = {
                "in_sync": len(orphaned) == 0 and len(missing) == 0,
                "neo4j_count": len(neo4j_uuids),
                "milvus_count": len(milvus_uuids),
                "orphaned_embeddings": sorted(orphaned),
                "missing_embeddings": sorted(missing),
            }

            if not report["in_sync"]:
                logger.warning(
                    f"Sync inconsistency detected for {node_type}: "
                    f"{len(orphaned)} orphaned, {len(missing)} missing"
                )

            return report

        except Exception as e:
            raise MilvusSyncError(f"Failed to verify sync for {node_type}: {e}") from e

    def health_check(self) -> dict[str, Any]:
        """
        Perform health check on Milvus collections.

        Returns:
            Dictionary with health status:
            {
                "connected": bool,
                "collections": {
                    "Entity": {"exists": bool, "loaded": bool, "count": int},
                    ...
                }
            }
        """
        status: dict[str, Any] = {
            "connected": self._connected,
            "collections": {},
        }

        if not self._connected:
            return status

        for node_type, collection_name in COLLECTION_NAMES.items():
            collection_status = {
                "exists": False,
                "loaded": False,
                "count": 0,
            }

            try:
                if utility.has_collection(collection_name, using=self.alias):
                    collection_status["exists"] = True
                    collection = Collection(name=collection_name, using=self.alias)

                    # Check if loaded
                    try:
                        collection_status["count"] = collection.num_entities
                        collection_status["loaded"] = True
                    except Exception:
                        # Collection exists but not loaded
                        collection_status["loaded"] = False

            except Exception as e:
                logger.error(f"Error checking collection {collection_name}: {e}")

            status["collections"][node_type] = collection_status

        return status
