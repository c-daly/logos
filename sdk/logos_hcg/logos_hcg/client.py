"""Neo4j client for HCG graph operations."""

import json
import logging
import uuid
from datetime import datetime
from typing import Any

from neo4j import Driver, GraphDatabase
from neo4j.exceptions import ServiceUnavailable, TransientError
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from logos_hcg.config import HCGConfig
from logos_hcg.exceptions import (
    HCGConnectionError,
    HCGNotFoundError,
    HCGQueryError,
    HCGValidationError,
)
from logos_hcg.models import (
    CausalEdge,
    Entity,
    GraphSnapshot,
    PlanHistory,
    Process,
    State,
    StateHistory,
)
from logos_hcg.validation import SHACLValidator

logger = logging.getLogger(__name__)


class HCGClient:
    """Client for interacting with HCG (Hybrid Causal Graph) in Neo4j.

    Provides both read and write operations with optional SHACL validation,
    retry logic for transient failures, and connection pooling.

    Example:
        >>> config = HCGConfig()
        >>> with HCGClient(config) as client:
        ...     entities = client.get_entities(entity_type="manipulator")
        ...     entity_id = client.create_entity("gripper", {"status": "ready"})
    """

    def __init__(
        self,
        config: HCGConfig | None = None,
        validator: SHACLValidator | None = None,
    ) -> None:
        """Initialize HCG client.

        Args:
            config: HCG configuration. If None, loads from environment.
            validator: Optional custom SHACL validator. If None and validation
                      is enabled, uses default validator.
        """
        self.config = config or HCGConfig()
        self._driver: Driver | None = None
        self._validator: SHACLValidator | None = None

        # Set up validator
        if self.config.shacl_enabled:
            if validator:
                self._validator = validator
            elif self.config.shacl_shapes_path:
                self._validator = SHACLValidator()
                self._validator.load_shapes_from_file(self.config.shacl_shapes_path)
            else:
                self._validator = SHACLValidator()

    def connect(self) -> None:
        """Establish connection to Neo4j database.

        Raises:
            HCGConnectionError: If connection fails
        """
        if self._driver is not None:
            return

        try:
            self._driver = GraphDatabase.driver(
                self.config.neo4j_uri,
                auth=(self.config.neo4j_user, self.config.neo4j_password),
                max_connection_pool_size=self.config.max_connection_pool_size,
            )
            # Verify connectivity
            self._driver.verify_connectivity()
            logger.info(f"Connected to Neo4j at {self.config.neo4j_uri}")
        except Exception as e:
            raise HCGConnectionError(f"Failed to connect to Neo4j: {e}") from e

    def close(self) -> None:
        """Close connection to Neo4j database."""
        if self._driver:
            self._driver.close()
            self._driver = None
            logger.info("Disconnected from Neo4j")

    def __enter__(self) -> "HCGClient":
        """Context manager entry."""
        self.connect()
        return self

    def __exit__(
        self,
        exc_type: type | None,
        exc_val: Exception | None,
        exc_tb: Any,  # noqa: ANN401 - traceback type is complex, Any is idiomatic
    ) -> None:
        """Context manager exit."""
        self.close()

    def _ensure_connected(self) -> None:
        """Ensure connection is established."""
        if self._driver is None:
            self.connect()

    def _get_retry_decorator(self) -> Any:  # noqa: ANN401 - tenacity decorator has complex return type
        """Get retry decorator with current config settings."""
        return retry(
            stop=stop_after_attempt(self.config.retry_attempts),
            wait=wait_exponential(
                multiplier=1,
                min=self.config.retry_min_wait,
                max=self.config.retry_max_wait,
            ),
            retry=retry_if_exception_type((ServiceUnavailable, TransientError)),
        )

    # -------------------------------------------------------------------------
    # Type conversion utilities
    # -------------------------------------------------------------------------

    def _convert_value(self, value: Any) -> Any:  # noqa: ANN401 - Neo4j driver returns dynamic types
        """Convert Neo4j types to Python native types."""
        if value is None:
            return None
        if hasattr(value, "to_native"):
            return value.to_native()
        if isinstance(value, bytes):
            try:
                return value.decode("utf-8")
            except UnicodeDecodeError:
                return f"<bytes len={len(value)}>"
        if isinstance(value, str):
            try:
                return datetime.fromisoformat(value)
            except ValueError:
                pass
        return value

    def _parse_json_field(self, value: Any, default: Any = None) -> Any:  # noqa: ANN401 - JSON values are dynamic
        """Parse JSON string field if necessary."""
        if isinstance(value, str):
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                return default
        return value if value is not None else default

    def _sanitize_props(self, props: dict[str, Any]) -> dict[str, Any]:
        """Recursively convert Neo4j types to Python native types."""
        sanitized: dict[str, Any] = {}
        for key, value in props.items():
            if isinstance(value, dict):
                sanitized[key] = self._sanitize_props(value)
            elif isinstance(value, list):
                sanitized[key] = [
                    (
                        self._sanitize_props(item)
                        if isinstance(item, dict)
                        else self._convert_value(item)
                    )
                    for item in value
                ]
            else:
                sanitized[key] = self._convert_value(value)
        return sanitized

    def _parse_node(self, node: Any) -> Entity:  # noqa: ANN401 - Neo4j Node type is not exported
        """Parse Neo4j node into Entity model."""
        properties = dict(node)
        return Entity(
            id=properties.get("id", str(node.id)),
            type=properties.get("type", "unknown"),
            properties=self._sanitize_props(properties),
            labels=list(node.labels),
            created_at=self._convert_value(properties.get("created_at")),
            updated_at=self._convert_value(properties.get("updated_at")),
        )

    def _parse_relationship(self, rel: Any, source: Any, target: Any) -> CausalEdge:  # noqa: ANN401 - Neo4j types
        """Parse Neo4j relationship into CausalEdge model."""
        properties = dict(rel)
        return CausalEdge(
            id=properties.get("id", str(rel.id)),
            source_id=dict(source).get("id", str(source.id)),
            target_id=dict(target).get("id", str(target.id)),
            edge_type=rel.type,
            properties=self._sanitize_props(properties),
            weight=properties.get("weight", 1.0),
            created_at=self._convert_value(properties.get("created_at"))
            or datetime.now(),
        )

    # -------------------------------------------------------------------------
    # Read operations (from Apollo)
    # -------------------------------------------------------------------------

    def get_entities(
        self,
        entity_type: str | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[Entity]:
        """Get entities from HCG graph.

        Args:
            entity_type: Optional filter by entity type
            limit: Maximum number of entities to return
            offset: Number of entities to skip

        Returns:
            List of entities
        """
        self._ensure_connected()

        query = """
        MATCH (n)
        WHERE $entity_type IS NULL OR n.type = $entity_type
        RETURN n
        ORDER BY n.created_at DESC
        SKIP $offset
        LIMIT $limit
        """

        with self._driver.session(database=self.config.neo4j_database) as session:  # type: ignore
            result = session.run(
                query,
                entity_type=entity_type,
                limit=limit,
                offset=offset,
            )
            return [self._parse_node(record["n"]) for record in result]

    def get_entity_by_id(self, entity_id: str) -> Entity | None:
        """Get a specific entity by ID.

        Args:
            entity_id: Entity identifier

        Returns:
            Entity or None if not found
        """
        self._ensure_connected()

        query = """
        MATCH (n)
        WHERE n.id = $entity_id OR id(n) = $node_id
        RETURN n
        """

        with self._driver.session(database=self.config.neo4j_database) as session:  # type: ignore
            result = session.run(
                query,
                entity_id=entity_id,
                node_id=int(entity_id) if entity_id.isdigit() else -1,
            )
            record = result.single()
            return self._parse_node(record["n"]) if record else None

    def get_states(
        self,
        limit: int = 100,
        offset: int = 0,
    ) -> list[State]:
        """Get state entities from HCG graph.

        Args:
            limit: Maximum number of states to return
            offset: Number of states to skip

        Returns:
            List of states
        """
        self._ensure_connected()

        query = """
        MATCH (s:State)
        RETURN s
        ORDER BY s.timestamp DESC
        SKIP $offset
        LIMIT $limit
        """

        with self._driver.session(database=self.config.neo4j_database) as session:  # type: ignore
            result = session.run(query, limit=limit, offset=offset)
            states = []
            for record in result:
                node = record["s"]
                props = dict(node)
                states.append(
                    State(
                        id=props.get("id", str(node.id)),
                        description=props.get("description", ""),
                        variables=self._parse_json_field(props.get("variables"), {}),
                        timestamp=self._convert_value(props.get("timestamp"))
                        or datetime.now(),
                        properties=self._sanitize_props(props),
                    )
                )
            return states

    def get_processes(
        self,
        status: str | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[Process]:
        """Get process entities from HCG graph.

        Args:
            status: Optional filter by process status
            limit: Maximum number of processes to return
            offset: Number of processes to skip

        Returns:
            List of processes
        """
        self._ensure_connected()

        query = """
        MATCH (p:Process)
        WHERE $status IS NULL OR p.status = $status
        RETURN p
        ORDER BY p.created_at DESC
        SKIP $offset
        LIMIT $limit
        """

        with self._driver.session(database=self.config.neo4j_database) as session:  # type: ignore
            result = session.run(
                query,
                status=status,
                limit=limit,
                offset=offset,
            )
            processes = []
            for record in result:
                node = record["p"]
                props = dict(node)
                processes.append(
                    Process(
                        id=props.get("id", str(node.id)),
                        name=props.get("name", ""),
                        description=props.get("description"),
                        status=props.get("status", "pending"),
                        inputs=self._parse_json_field(props.get("inputs"), []),
                        outputs=self._parse_json_field(props.get("outputs"), []),
                        properties=self._sanitize_props(props),
                        created_at=self._convert_value(props.get("created_at"))
                        or datetime.now(),
                        completed_at=self._convert_value(props.get("completed_at")),
                    )
                )
            return processes

    def get_causal_edges(
        self,
        entity_id: str | None = None,
        edge_type: str | None = None,
        limit: int = 100,
    ) -> list[CausalEdge]:
        """Get causal edges from HCG graph.

        Args:
            entity_id: Optional filter by source or target entity
            edge_type: Optional filter by edge type
            limit: Maximum number of edges to return

        Returns:
            List of causal edges
        """
        self._ensure_connected()

        if entity_id:
            query = """
            MATCH (n)-[r]->(m)
            WHERE (n.id = $entity_id OR m.id = $entity_id)
              AND ($edge_type IS NULL OR type(r) = $edge_type)
            RETURN n, r, m
            LIMIT $limit
            """
        else:
            query = """
            MATCH (n)-[r]->(m)
            WHERE $edge_type IS NULL OR type(r) = $edge_type
            RETURN n, r, m
            LIMIT $limit
            """

        with self._driver.session(database=self.config.neo4j_database) as session:  # type: ignore
            result = session.run(
                query,
                entity_id=entity_id,
                edge_type=edge_type,
                limit=limit,
            )
            return [
                self._parse_relationship(record["r"], record["n"], record["m"])
                for record in result
            ]

    def get_plan_history(
        self,
        goal_id: str | None = None,
        limit: int = 10,
    ) -> list[PlanHistory]:
        """Get plan history from HCG graph.

        Args:
            goal_id: Optional filter by goal ID
            limit: Maximum number of plans to return

        Returns:
            List of plan history records
        """
        self._ensure_connected()

        query = """
        MATCH (p:Plan)
        WHERE $goal_id IS NULL OR p.goal_id = $goal_id
        RETURN p
        ORDER BY p.created_at DESC
        LIMIT $limit
        """

        with self._driver.session(database=self.config.neo4j_database) as session:  # type: ignore
            result = session.run(query, goal_id=goal_id, limit=limit)
            plans = []
            for record in result:
                node = record["p"]
                props = dict(node)

                steps_raw = self._parse_json_field(props.get("steps"), [])
                steps = [
                    self._sanitize_props(s) if isinstance(s, dict) else s
                    for s in steps_raw
                ]

                result_raw = self._parse_json_field(props.get("result"))
                plan_result = (
                    self._sanitize_props(result_raw)
                    if isinstance(result_raw, dict)
                    else result_raw
                )

                plans.append(
                    PlanHistory(
                        id=props.get("id", str(node.id)),
                        goal_id=props.get("goal_id", ""),
                        status=props.get("status", "pending"),
                        steps=steps,
                        created_at=self._convert_value(props.get("created_at"))
                        or datetime.now(),
                        started_at=self._convert_value(props.get("started_at")),
                        completed_at=self._convert_value(props.get("completed_at")),
                        result=plan_result,
                    )
                )
            return plans

    def get_state_history(
        self,
        state_id: str | None = None,
        limit: int = 50,
    ) -> list[StateHistory]:
        """Get state change history from HCG graph.

        Args:
            state_id: Optional filter by state ID
            limit: Maximum number of history records to return

        Returns:
            List of state history records
        """
        self._ensure_connected()

        query = """
        MATCH (h:StateHistory)
        WHERE $state_id IS NULL OR h.state_id = $state_id
        RETURN h
        ORDER BY h.timestamp DESC
        LIMIT $limit
        """

        with self._driver.session(database=self.config.neo4j_database) as session:  # type: ignore
            result = session.run(query, state_id=state_id, limit=limit)
            history = []
            for record in result:
                node = record["h"]
                props = dict(node)

                changes_raw = self._parse_json_field(props.get("changes"), {})
                changes = (
                    self._sanitize_props(changes_raw)
                    if isinstance(changes_raw, dict)
                    else changes_raw
                )

                prev_raw = self._parse_json_field(props.get("previous_values"))
                previous_values = (
                    self._sanitize_props(prev_raw)
                    if isinstance(prev_raw, dict)
                    else prev_raw
                )

                history.append(
                    StateHistory(
                        id=props.get("id", str(node.id)),
                        state_id=props.get("state_id", ""),
                        timestamp=self._convert_value(props.get("timestamp"))
                        or datetime.now(),
                        changes=changes,
                        previous_values=previous_values,
                        trigger=props.get("trigger"),
                    )
                )
            return history

    def get_graph_snapshot(
        self,
        entity_types: list[str] | None = None,
        limit: int = 200,
    ) -> GraphSnapshot:
        """Get a snapshot of the HCG graph.

        Args:
            entity_types: Optional filter by entity types
            limit: Maximum number of entities to include

        Returns:
            Graph snapshot with entities and edges
        """
        self._ensure_connected()

        # Get entities
        if entity_types:
            node_query = """
            MATCH (n)
            WHERE n.type IN $entity_types
            RETURN n, id(n) as internal_id
            LIMIT $limit
            """
        else:
            node_query = """
            MATCH (n)
            RETURN n, id(n) as internal_id
            LIMIT $limit
            """

        # Get edges between selected nodes
        edge_query = """
        MATCH (n)-[r]->(m)
        WHERE id(n) IN $node_ids AND id(m) IN $node_ids
        RETURN n, r, m
        """

        with self._driver.session(database=self.config.neo4j_database) as session:  # type: ignore
            # Get nodes
            node_result = session.run(
                node_query,
                entity_types=entity_types,
                limit=limit,
            )

            entities = []
            node_ids = []
            for record in node_result:
                entities.append(self._parse_node(record["n"]))
                node_ids.append(record["internal_id"])

            # Get edges
            edge_result = session.run(edge_query, node_ids=node_ids)
            edges = [
                self._parse_relationship(record["r"], record["n"], record["m"])
                for record in edge_result
            ]

            return GraphSnapshot(
                entities=entities,
                edges=edges,
                timestamp=datetime.now(),
                metadata={
                    "entity_count": len(entities),
                    "edge_count": len(edges),
                    "entity_types": entity_types or [],
                },
            )

    def query_neighbors(self, node_id: str) -> list[dict[str, Any]]:
        """Query neighbors of a node.

        Args:
            node_id: Node ID

        Returns:
            List of neighbor nodes
        """
        self._ensure_connected()

        with self._driver.session(database=self.config.neo4j_database) as session:  # type: ignore
            query = """
            MATCH (n {id: $id})-[r]-(neighbor)
            RETURN DISTINCT neighbor.id as id, neighbor.type as type,
                   properties(neighbor) as props
            """
            result = session.run(query, id=node_id)

            neighbors = []
            for record in result:
                props = dict(record["props"])
                props.pop("id", None)
                props.pop("type", None)

                neighbors.append(
                    {
                        "id": record["id"],
                        "type": record["type"],
                        "properties": props,
                    }
                )

            return neighbors

    def query_edges_from(self, node_id: str) -> list[dict[str, Any]]:
        """Query edges from a node.

        Args:
            node_id: Node ID

        Returns:
            List of outgoing edges
        """
        self._ensure_connected()

        with self._driver.session(database=self.config.neo4j_database) as session:  # type: ignore
            query = """
            MATCH (source {id: $id})-[r]->(target)
            RETURN r.id as id, source.id as source, target.id as target,
                   type(r) as relation, properties(r) as props
            """
            result = session.run(query, id=node_id)

            edges = []
            for record in result:
                props = dict(record["props"]) if record["props"] else {}
                props.pop("id", None)

                edges.append(
                    {
                        "id": record["id"],
                        "source": record["source"],
                        "target": record["target"],
                        "relation": record["relation"],
                        "properties": props,
                    }
                )

            return edges

    # -------------------------------------------------------------------------
    # Write operations (from Sophia with retry logic)
    # -------------------------------------------------------------------------

    def create_entity(
        self,
        entity_type: str,
        properties: dict[str, Any] | None = None,
        entity_id: str | None = None,
    ) -> str:
        """Create a new entity in the graph.

        Args:
            entity_type: Entity type
            properties: Optional entity properties
            entity_id: Optional custom ID (generated if not provided)

        Returns:
            Entity ID

        Raises:
            HCGValidationError: If SHACL validation fails
            HCGQueryError: If the query fails
        """
        self._ensure_connected()

        node_id = entity_id or f"entity_{uuid.uuid4().hex[:12]}"
        props = properties or {}

        # SHACL validation
        if self._validator:
            node_data = {"id": node_id, "type": entity_type, "properties": props}
            is_valid, errors = self._validator.validate_node(node_data)
            if not is_valid:
                raise HCGValidationError(
                    f"Entity validation failed: {'; '.join(errors)}",
                    errors=errors,
                )

        # Add timestamps
        now = datetime.now().isoformat()
        props["created_at"] = now
        props["updated_at"] = now

        @self._get_retry_decorator()
        def _create() -> str:
            with self._driver.session(database=self.config.neo4j_database) as session:  # type: ignore
                query = """
                CREATE (n:Entity {id: $id, type: $type})
                SET n += $properties
                RETURN n.id as id
                """
                result = session.run(
                    query,
                    id=node_id,
                    type=entity_type,
                    properties=props,
                )
                record = result.single()
                return str(record["id"]) if record else node_id

        try:
            created_id = _create()
            logger.info(f"Created entity: {created_id}")
            return created_id
        except (ServiceUnavailable, TransientError) as e:
            raise HCGConnectionError(f"Failed to create entity: {e}") from e
        except Exception as e:
            raise HCGQueryError(f"Failed to create entity: {e}") from e

    def update_entity(
        self,
        entity_id: str,
        properties: dict[str, Any],
    ) -> bool:
        """Update an entity's properties.

        Args:
            entity_id: Entity ID to update
            properties: Properties to update

        Returns:
            True if updated, False if not found

        Raises:
            HCGQueryError: If the query fails
        """
        self._ensure_connected()

        # Add updated timestamp
        properties["updated_at"] = datetime.now().isoformat()

        @self._get_retry_decorator()
        def _update() -> bool:
            with self._driver.session(database=self.config.neo4j_database) as session:  # type: ignore
                query = """
                MATCH (n {id: $id})
                SET n += $properties
                RETURN count(n) as updated
                """
                result = session.run(
                    query,
                    id=entity_id,
                    properties=properties,
                )
                record = result.single()
                return bool(record["updated"] > 0) if record else False

        try:
            updated = _update()
            if updated:
                logger.info(f"Updated entity: {entity_id}")
            return updated
        except Exception as e:
            raise HCGQueryError(f"Failed to update entity: {e}") from e

    def delete_entity(self, entity_id: str) -> bool:
        """Delete an entity from the graph.

        Args:
            entity_id: Entity ID to delete

        Returns:
            True if deleted, False if not found
        """
        self._ensure_connected()

        @self._get_retry_decorator()
        def _delete() -> bool:
            with self._driver.session(database=self.config.neo4j_database) as session:  # type: ignore
                query = """
                MATCH (n {id: $id})
                DETACH DELETE n
                RETURN count(n) as deleted
                """
                result = session.run(query, id=entity_id)
                record = result.single()
                return bool(record["deleted"] > 0) if record else False

        deleted = _delete()
        if deleted:
            logger.info(f"Deleted entity: {entity_id}")
        return deleted

    def add_relationship(
        self,
        source_id: str,
        target_id: str,
        relation_type: str,
        properties: dict[str, Any] | None = None,
        edge_id: str | None = None,
    ) -> str:
        """Add a relationship between two entities.

        Args:
            source_id: Source entity ID
            target_id: Target entity ID
            relation_type: Relationship type
            properties: Optional relationship properties
            edge_id: Optional custom edge ID

        Returns:
            Edge ID

        Raises:
            HCGValidationError: If SHACL validation fails
            HCGNotFoundError: If source or target not found
        """
        self._ensure_connected()

        rel_id = edge_id or f"edge_{uuid.uuid4().hex[:12]}"
        props = properties or {}

        # SHACL validation
        if self._validator:
            edge_data = {
                "id": rel_id,
                "source": source_id,
                "target": target_id,
                "relation": relation_type,
                "properties": props,
            }
            is_valid, errors = self._validator.validate_edge(edge_data)
            if not is_valid:
                raise HCGValidationError(
                    f"Edge validation failed: {'; '.join(errors)}",
                    errors=errors,
                )

        props["created_at"] = datetime.now().isoformat()

        @self._get_retry_decorator()
        def _add_rel() -> str:
            with self._driver.session(database=self.config.neo4j_database) as session:  # type: ignore
                # Use APOC if available, otherwise dynamic relationship
                query = f"""
                MATCH (source {{id: $source_id}})
                MATCH (target {{id: $target_id}})
                CREATE (source)-[r:{relation_type} {{id: $edge_id}}]->(target)
                SET r += $properties
                RETURN r.id as id
                """
                result = session.run(
                    query,
                    source_id=source_id,
                    target_id=target_id,
                    edge_id=rel_id,
                    properties=props,
                )
                record = result.single()
                if not record:
                    raise HCGNotFoundError(
                        f"Source or target not found: {source_id}, {target_id}"
                    )
                return str(record["id"])

        created_id = _add_rel()
        logger.info(f"Added relationship: {created_id}")
        return created_id

    def delete_relationship(self, edge_id: str) -> bool:
        """Delete a relationship by ID.

        Args:
            edge_id: Edge ID to delete

        Returns:
            True if deleted, False if not found
        """
        self._ensure_connected()

        @self._get_retry_decorator()
        def _delete() -> bool:
            with self._driver.session(database=self.config.neo4j_database) as session:  # type: ignore
                query = """
                MATCH ()-[r {id: $id}]->()
                DELETE r
                RETURN count(r) as deleted
                """
                result = session.run(query, id=edge_id)
                record = result.single()
                return bool(record["deleted"] > 0) if record else False

        deleted = _delete()
        if deleted:
            logger.info(f"Deleted relationship: {edge_id}")
        return deleted

    def clear_all(self) -> None:
        """Clear all nodes and edges from the graph.

        Warning: This is destructive and cannot be undone!
        """
        self._ensure_connected()

        @self._get_retry_decorator()
        def _clear() -> None:
            with self._driver.session(database=self.config.neo4j_database) as session:  # type: ignore
                session.run("MATCH (n) DETACH DELETE n")

        _clear()
        logger.warning("Cleared all nodes and edges from graph")

    # -------------------------------------------------------------------------
    # Health and utilities
    # -------------------------------------------------------------------------

    def health_check(self) -> bool:
        """Check if Neo4j connection is healthy.

        Returns:
            True if connected and healthy, False otherwise
        """
        try:
            self._ensure_connected()
            with self._driver.session(database=self.config.neo4j_database) as session:  # type: ignore
                result = session.run("RETURN 1 as health")
                record = result.single()
                return record is not None and record["health"] == 1
        except Exception as e:  # noqa: BLE001 - health check should return False for any failure
            logger.error(f"Health check failed: {e}")
            return False

    def get_stats(self) -> dict[str, Any]:
        """Get database statistics.

        Returns:
            Dictionary with node count, relationship count, etc.
        """
        self._ensure_connected()

        with self._driver.session(database=self.config.neo4j_database) as session:  # type: ignore
            result = session.run("""
                MATCH (n)
                WITH count(n) as node_count
                MATCH ()-[r]->()
                WITH node_count, count(r) as rel_count
                RETURN node_count, rel_count
            """)
            record = result.single()

            if record:
                return {
                    "node_count": record["node_count"],
                    "relationship_count": record["rel_count"],
                    "database": self.config.neo4j_database,
                    "uri": self.config.neo4j_uri,
                }
            return {
                "node_count": 0,
                "relationship_count": 0,
                "database": self.config.neo4j_database,
                "uri": self.config.neo4j_uri,
            }
