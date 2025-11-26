"""
HCG Client Library for Neo4j access.

Provides connection management, pooling, error handling, and query execution
for the Hybrid Causal Graph stored in Neo4j.

See Project LOGOS spec: Section 4.1 (Core Ontology and Data Model)
"""

import logging
from collections.abc import Iterator
from contextlib import contextmanager
from datetime import datetime
from typing import Any
from uuid import UUID

from neo4j import Driver, GraphDatabase, Session
from neo4j.exceptions import (
    Neo4jError,
    ServiceUnavailable,
    TransientError,
)

from logos_hcg.models import Concept, Entity, Process, State
from logos_hcg.queries import HCGQueries

logger = logging.getLogger(__name__)


class HCGConnectionError(Exception):
    """Raised when connection to Neo4j fails."""

    pass


class HCGQueryError(Exception):
    """Raised when a query execution fails."""

    pass


class HCGClient:
    """
    Client for accessing the Hybrid Causal Graph in Neo4j.

    Features:
    - Connection pooling (managed by Neo4j driver)
    - Automatic retry on transient errors
    - Type-safe result models
    - Comprehensive error handling

    Example:
        client = HCGClient(uri="bolt://localhost:7687", user="neo4j", password="password")
        entity = client.find_entity_by_uuid("uuid-here")
        client.close()

    Or use as context manager:
        with HCGClient(uri="bolt://localhost:7687", user="neo4j", password="password") as client:
            entity = client.find_entity_by_uuid("uuid-here")
    """

    def __init__(
        self,
        uri: str,
        user: str,
        password: str,
        database: str = "neo4j",
        max_connection_lifetime: int = 3600,
        max_connection_pool_size: int = 50,
        connection_acquisition_timeout: int = 60,
        max_retry_attempts: int = 3,
    ):
        """
        Initialize HCG client with connection pooling.

        Args:
            uri: Neo4j connection URI (e.g., "bolt://localhost:7687")
            user: Neo4j username
            password: Neo4j password
            database: Database name (default "neo4j")
            max_connection_lifetime: Max connection lifetime in seconds
            max_connection_pool_size: Max number of connections in pool
            connection_acquisition_timeout: Timeout for acquiring connection
            max_retry_attempts: Max retry attempts for transient errors
        """
        self.uri = uri
        self.user = user
        self.database = database
        self.max_retry_attempts = max_retry_attempts

        try:
            self.driver: Driver = GraphDatabase.driver(
                uri,
                auth=(user, password),
                max_connection_lifetime=max_connection_lifetime,
                max_connection_pool_size=max_connection_pool_size,
                connection_acquisition_timeout=connection_acquisition_timeout,
            )
            # Verify connectivity
            self.driver.verify_connectivity()
            logger.info(f"Connected to Neo4j at {uri}")
        except ServiceUnavailable as e:
            raise HCGConnectionError(f"Failed to connect to Neo4j at {uri}: {e}") from e
        except Exception as e:
            raise HCGConnectionError(
                f"Unexpected error connecting to Neo4j: {e}"
            ) from e

    def close(self):
        """Close the driver and release all connections."""
        if self.driver:
            self.driver.close()
            logger.info("Closed Neo4j connection")

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()

    @contextmanager
    def _session(self) -> Iterator[Session]:
        """
        Create a session with proper resource management.

        Yields:
            Neo4j session
        """
        session: Session | None = None
        try:
            session = self.driver.session(database=self.database)
            yield session
        finally:
            if session:
                session.close()

    def _execute_query(
        self,
        query: str,
        parameters: dict[str, Any] | None = None,
        retry_count: int = 0,
    ) -> list[Any]:
        """
        Execute a Cypher query with retry logic.

        Args:
            query: Cypher query string
            parameters: Query parameters
            retry_count: Current retry attempt

        Returns:
            List of records

        Raises:
            HCGQueryError: On query execution failure
        """
        parameters = parameters or {}

        try:
            with self._session() as session:
                result = session.run(query, parameters)
                # Consume the result within the session to avoid closure issues
                records = list(result)
                # Return the records directly instead of the Result object
                return records
        except TransientError as e:
            if retry_count < self.max_retry_attempts:
                logger.warning(
                    f"Transient error on query, retrying ({retry_count + 1}/{self.max_retry_attempts}): {e}"
                )
                return self._execute_query(query, parameters, retry_count + 1)
            else:
                raise HCGQueryError(
                    f"Query failed after {self.max_retry_attempts} retries: {e}"
                ) from e
        except Neo4jError as e:
            raise HCGQueryError(f"Neo4j error executing query: {e}") from e
        except Exception as e:
            raise HCGQueryError(f"Unexpected error executing query: {e}") from e

    def _execute_read(
        self,
        query: str,
        parameters: dict[str, Any] | None = None,
    ) -> list[dict[str, Any]]:
        """
        Execute a read query and return all records.

        Args:
            query: Cypher query string
            parameters: Query parameters

        Returns:
            List of record dictionaries
        """
        records = self._execute_query(query, parameters)
        return [dict(record) for record in records]

    def _parse_node_to_dict(self, node) -> dict[str, Any]:
        """
        Parse a Neo4j node to dictionary.

        Args:
            node: Neo4j node object

        Returns:
            Dictionary of node properties
        """
        if node is None:
            return {}

        # Convert Neo4j node to dict
        props = dict(node)

        # Convert datetime objects to ISO strings for consistency
        for key, value in props.items():
            if isinstance(value, datetime):
                props[key] = value

        return props

    @staticmethod
    def _normalize_uuid(value: str | UUID, param_name: str = "uuid") -> str:
        """
        Ensure UUID values are serialized as strings before sending them to Neo4j.

        Args:
            value: UUID as string or uuid.UUID
            param_name: Parameter name for clearer error messages

        Returns:
            String representation of the UUID
        """
        if value is None:
            raise ValueError(f"{param_name} cannot be None")
        if isinstance(value, UUID):
            return str(value)
        return str(value)

    @staticmethod
    def _sanitize_depth(max_depth: int | None, default: int = 10) -> int:
        """Ensure traversal depth is a safe positive integer."""
        depth = default if max_depth is None else int(max_depth)
        if depth < 1:
            depth = 1
        return depth

    # ========== Entity Operations ==========

    def find_entity_by_uuid(self, uuid: str | UUID) -> Entity | None:
        """
        Find an entity by UUID.

        Args:
            uuid: Entity UUID (string or uuid.UUID with 'entity-' prefix)

        Returns:
            Entity object or None if not found
        """
        query = HCGQueries.find_entity_by_uuid()
        uuid_str = self._normalize_uuid(uuid, "uuid")
        records = self._execute_read(query, {"uuid": uuid_str})

        if not records:
            return None

        node_props = self._parse_node_to_dict(records[0]["e"])
        return Entity(**node_props)

    def find_entities_by_name(self, name: str) -> list[Entity]:
        """
        Find entities by name (partial match).

        Args:
            name: Entity name pattern

        Returns:
            List of Entity objects
        """
        query = HCGQueries.find_entity_by_name()
        records = self._execute_read(query, {"name": name})

        entities = []
        for record in records:
            node_props = self._parse_node_to_dict(record["e"])
            entities.append(Entity(**node_props))

        return entities

    def find_all_entities(self, skip: int = 0, limit: int = 100) -> list[Entity]:
        """
        Find all entities with pagination.

        Args:
            skip: Number of records to skip
            limit: Maximum records to return

        Returns:
            List of Entity objects
        """
        query = HCGQueries.find_all_entities()
        records = self._execute_read(query, {"skip": skip, "limit": limit})

        entities = []
        for record in records:
            node_props = self._parse_node_to_dict(record["e"])
            entities.append(Entity(**node_props))

        return entities

    # ========== Concept Operations ==========

    def find_concept_by_uuid(self, uuid: str | UUID) -> Concept | None:
        """
        Find a concept by UUID.

        Args:
            uuid: Concept UUID (string or uuid.UUID)

        Returns:
            Concept object or None if not found
        """
        uuid_str = self._normalize_uuid(uuid, "uuid")
        query = HCGQueries.find_concept_by_uuid()
        records = self._execute_read(query, {"uuid": uuid_str})

        if not records:
            return None

        node_props = self._parse_node_to_dict(records[0]["c"])
        return Concept(**node_props)

    def find_concept_by_name(self, name: str) -> Concept | None:
        """
        Find a concept by exact name.

        Args:
            name: Concept name

        Returns:
            Concept object or None if not found
        """
        query = HCGQueries.find_concept_by_name()
        records = self._execute_read(query, {"name": name})

        if not records:
            return None

        node_props = self._parse_node_to_dict(records[0]["c"])
        return Concept(**node_props)

    def find_all_concepts(self) -> list[Concept]:
        """
        Find all concepts.

        Returns:
            List of Concept objects
        """
        query = HCGQueries.find_all_concepts()
        records = self._execute_read(query)

        concepts = []
        for record in records:
            node_props = self._parse_node_to_dict(record["c"])
            concepts.append(Concept(**node_props))

        return concepts

    # ========== State Operations ==========

    def find_state_by_uuid(self, uuid: str | UUID) -> State | None:
        """
        Find a state by UUID.

        Args:
            uuid: State UUID (string or uuid.UUID)

        Returns:
            State object or None if not found
        """
        uuid_str = self._normalize_uuid(uuid, "uuid")
        query = HCGQueries.find_state_by_uuid()
        records = self._execute_read(query, {"uuid": uuid_str})

        if not records:
            return None

        node_props = self._parse_node_to_dict(records[0]["s"])
        return State(**node_props)

    def find_states_by_timestamp_range(
        self,
        start_time: str | datetime,
        end_time: str | datetime,
    ) -> list[State]:
        """
        Find states within a timestamp range.

        Args:
            start_time: Start timestamp (ISO string or datetime)
            end_time: End timestamp (ISO string or datetime)

        Returns:
            List of State objects
        """
        # Convert datetime to ISO string if needed
        start_str = (
            start_time.isoformat() if isinstance(start_time, datetime) else start_time
        )
        end_str = end_time.isoformat() if isinstance(end_time, datetime) else end_time

        query = HCGQueries.find_states_by_timestamp_range()
        records = self._execute_read(
            query, {"start_time": start_str, "end_time": end_str}
        )

        states = []
        for record in records:
            node_props = self._parse_node_to_dict(record["s"])
            states.append(State(**node_props))

        return states

    # ========== Process Operations ==========

    def find_process_by_uuid(self, uuid: str | UUID) -> Process | None:
        """
        Find a process by UUID.

        Args:
            uuid: Process UUID (string or uuid.UUID)

        Returns:
            Process object or None if not found
        """
        uuid_str = self._normalize_uuid(uuid, "uuid")
        query = HCGQueries.find_process_by_uuid()
        records = self._execute_read(query, {"uuid": uuid_str})

        if not records:
            return None

        node_props = self._parse_node_to_dict(records[0]["p"])
        return Process(**node_props)

    def find_processes_by_time_range(
        self,
        start_time: str | datetime,
        end_time: str | datetime,
    ) -> list[Process]:
        """
        Find processes within a time range.

        Args:
            start_time: Start timestamp (ISO string or datetime)
            end_time: End timestamp (ISO string or datetime)

        Returns:
            List of Process objects
        """
        # Convert datetime to ISO string if needed
        start_str = (
            start_time.isoformat() if isinstance(start_time, datetime) else start_time
        )
        end_str = end_time.isoformat() if isinstance(end_time, datetime) else end_time

        query = HCGQueries.find_processes_by_time_range()
        records = self._execute_read(
            query, {"start_time": start_str, "end_time": end_str}
        )

        processes = []
        for record in records:
            node_props = self._parse_node_to_dict(record["p"])
            processes.append(Process(**node_props))

        return processes

    # ========== Relationship Operations ==========

    def get_entity_type(self, entity_uuid: str | UUID) -> Concept | None:
        """
        Get the concept/type of an entity.

        Args:
            entity_uuid: Entity UUID

        Returns:
            Concept object or None
        """
        entity_uuid_str = self._normalize_uuid(entity_uuid, "entity_uuid")
        query = HCGQueries.get_entity_type()
        records = self._execute_read(query, {"entity_uuid": entity_uuid_str})

        if not records:
            return None

        node_props = self._parse_node_to_dict(records[0]["c"])
        return Concept(**node_props)

    def get_entity_states(self, entity_uuid: str | UUID) -> list[State]:
        """
        Get all states of an entity.

        Args:
            entity_uuid: Entity UUID

        Returns:
            List of State objects (ordered by timestamp, most recent first)
        """
        entity_uuid_str = self._normalize_uuid(entity_uuid, "entity_uuid")
        query = HCGQueries.get_entity_states()
        records = self._execute_read(query, {"entity_uuid": entity_uuid_str})

        states = []
        for record in records:
            node_props = self._parse_node_to_dict(record["s"])
            states.append(State(**node_props))

        return states

    def get_entity_current_state(self, entity_uuid: str | UUID) -> State | None:
        """
        Get the most recent state of an entity.

        Args:
            entity_uuid: Entity UUID

        Returns:
            State object or None
        """
        entity_uuid_str = self._normalize_uuid(entity_uuid, "entity_uuid")
        query = HCGQueries.get_entity_current_state()
        records = self._execute_read(query, {"entity_uuid": entity_uuid_str})

        if not records:
            return None

        node_props = self._parse_node_to_dict(records[0]["s"])
        return State(**node_props)

    def get_entity_parts(self, entity_uuid: str | UUID) -> list[Entity]:
        """
        Get all parts of an entity.

        Args:
            entity_uuid: Entity UUID

        Returns:
            List of Entity objects
        """
        entity_uuid_str = self._normalize_uuid(entity_uuid, "entity_uuid")
        query = HCGQueries.get_entity_parts()
        records = self._execute_read(query, {"entity_uuid": entity_uuid_str})

        entities = []
        for record in records:
            node_props = self._parse_node_to_dict(record["part"])
            entities.append(Entity(**node_props))

        return entities

    def get_entity_parent(self, entity_uuid: str | UUID) -> Entity | None:
        """
        Get the parent entity.

        Args:
            entity_uuid: Entity UUID

        Returns:
            Entity object or None
        """
        entity_uuid_str = self._normalize_uuid(entity_uuid, "entity_uuid")
        query = HCGQueries.get_entity_parent()
        records = self._execute_read(query, {"entity_uuid": entity_uuid_str})

        if not records:
            return None

        node_props = self._parse_node_to_dict(records[0]["whole"])
        return Entity(**node_props)

    # ========== Causal Traversal Operations ==========

    def traverse_causality_forward(
        self,
        state_uuid: str | UUID,
        max_depth: int = 10,
    ) -> list[dict[str, Any]]:
        """
        Traverse causality chain forward from a state.

        Args:
            state_uuid: Starting State UUID
            max_depth: Maximum traversal depth

        Returns:
            List of dicts with 'process', 'state', and 'depth' keys
        """
        state_uuid_str = self._normalize_uuid(state_uuid, "state_uuid")
        depth = self._sanitize_depth(max_depth)
        query = HCGQueries.traverse_causality_forward(depth)
        records = self._execute_read(query, {"state_uuid": state_uuid_str})

        results = []
        for record in records:
            process_props = self._parse_node_to_dict(record["p"])
            state_props = self._parse_node_to_dict(record["result"])
            results.append(
                {
                    "process": Process(**process_props),
                    "state": State(**state_props),
                    "depth": record["depth"],
                }
            )

        return results

    def traverse_causality_backward(
        self,
        state_uuid: str | UUID,
        max_depth: int = 10,
    ) -> list[dict[str, Any]]:
        """
        Traverse causality chain backward from a state.

        Args:
            state_uuid: Target State UUID
            max_depth: Maximum traversal depth

        Returns:
            List of dicts with 'state', 'process', and 'depth' keys
        """
        state_uuid_str = self._normalize_uuid(state_uuid, "state_uuid")
        depth = self._sanitize_depth(max_depth)
        query = HCGQueries.traverse_causality_backward(depth)
        records = self._execute_read(query, {"state_uuid": state_uuid_str})

        results = []
        for record in records:
            state_props = self._parse_node_to_dict(record["cause"])
            process_props = self._parse_node_to_dict(record["p"])
            results.append(
                {
                    "state": State(**state_props),
                    "process": Process(**process_props),
                    "depth": record["depth"],
                }
            )

        return results

    def get_process_causes(self, process_uuid: str | UUID) -> list[State]:
        """
        Get all states caused by a process.

        Args:
            process_uuid: Process UUID

        Returns:
            List of State objects
        """
        process_uuid_str = self._normalize_uuid(process_uuid, "process_uuid")
        query = HCGQueries.get_process_causes()
        records = self._execute_read(query, {"process_uuid": process_uuid_str})

        states = []
        for record in records:
            node_props = self._parse_node_to_dict(record["s"])
            states.append(State(**node_props))

        return states

    def get_process_requirements(self, process_uuid: str | UUID) -> list[State]:
        """
        Get all states required by a process (preconditions).

        Args:
            process_uuid: Process UUID

        Returns:
            List of State objects
        """
        process_uuid_str = self._normalize_uuid(process_uuid, "process_uuid")
        query = HCGQueries.get_process_requirements()
        records = self._execute_read(query, {"process_uuid": process_uuid_str})

        states = []
        for record in records:
            node_props = self._parse_node_to_dict(record["s"])
            states.append(State(**node_props))

        return states

    # ========== Write Operations ==========

    def add_node(
        self,
        node_data: dict[str, Any],
        validate: bool = True,
    ) -> str:
        """Add a node to the graph with optional SHACL validation.

        Args:
            node_data: Node data with 'id', 'type', and optional 'properties'
            validate: Whether to validate against SHACL shapes (default True)

        Returns:
            Node ID

        Raises:
            HCGValidationError: If validation fails
            HCGQueryError: If query execution fails
        """
        from logos_hcg.shacl_validator import HCGValidationError, SHACLValidator

        if validate:
            validator = SHACLValidator()
            is_valid, errors = validator.validate_node(node_data)
            if not is_valid:
                raise HCGValidationError(
                    f"Node validation failed: {'; '.join(errors)}",
                    errors=errors,
                )

        node_id = node_data["id"]
        node_type = node_data["type"]
        properties = node_data.get("properties", {})

        query = """
        MERGE (n:Node {id: $id})
        SET n.type = $type
        SET n += $properties
        RETURN n.id as id
        """
        records = self._execute_read(
            query,
            {"id": node_id, "type": node_type, "properties": properties},
        )

        logger.info(f"Added node: {node_id}")
        return str(records[0]["id"]) if records else node_id

    def add_edge(
        self,
        edge_data: dict[str, Any],
        validate: bool = True,
    ) -> str:
        """Add an edge to the graph with optional SHACL validation.

        Args:
            edge_data: Edge data with 'id', 'source', 'target', 'relation',
                      and optional 'properties'
            validate: Whether to validate against SHACL shapes (default True)

        Returns:
            Edge ID

        Raises:
            HCGValidationError: If validation fails
            HCGQueryError: If query execution fails or nodes not found
        """
        from logos_hcg.shacl_validator import HCGValidationError, SHACLValidator

        if validate:
            validator = SHACLValidator()
            is_valid, errors = validator.validate_edge(edge_data)
            if not is_valid:
                raise HCGValidationError(
                    f"Edge validation failed: {'; '.join(errors)}",
                    errors=errors,
                )

        edge_id = edge_data["id"]
        source_id = edge_data["source"]
        target_id = edge_data["target"]
        relation = edge_data["relation"]
        properties = edge_data.get("properties", {})

        query = """
        MATCH (source:Node {id: $source_id})
        MATCH (target:Node {id: $target_id})
        MERGE (source)-[r:RELATION {id: $edge_id}]->(target)
        SET r.relation_type = $relation
        SET r += $properties
        RETURN r.id as id
        """
        records = self._execute_read(
            query,
            {
                "edge_id": edge_id,
                "source_id": source_id,
                "target_id": target_id,
                "relation": relation,
                "properties": properties,
            },
        )

        if not records:
            raise HCGQueryError(
                f"Failed to create edge: source ({source_id}) or target ({target_id}) not found"
            )

        logger.info(f"Added edge: {edge_id}")
        return str(records[0]["id"]) if records else edge_id

    def update_node(
        self,
        node_id: str,
        properties: dict[str, Any],
    ) -> bool:
        """Update a node's properties.

        Args:
            node_id: Node ID to update
            properties: Properties to update/add

        Returns:
            True if updated, False if not found
        """
        query = """
        MATCH (n:Node {id: $id})
        SET n += $properties
        RETURN count(n) as updated
        """
        records = self._execute_read(
            query,
            {"id": node_id, "properties": properties},
        )

        updated = records[0]["updated"] > 0 if records else False
        if updated:
            logger.info(f"Updated node: {node_id}")
        return updated

    def delete_node(self, node_id: str) -> bool:
        """Delete a node and all its relationships from the graph.

        Args:
            node_id: Node ID to delete

        Returns:
            True if deleted, False if not found
        """
        query = """
        MATCH (n:Node {id: $id})
        DETACH DELETE n
        RETURN count(n) as deleted
        """
        records = self._execute_read(query, {"id": node_id})

        deleted = records[0]["deleted"] > 0 if records else False
        if deleted:
            logger.info(f"Deleted node: {node_id}")
        return deleted

    def delete_edge(self, edge_id: str) -> bool:
        """Delete an edge from the graph.

        Args:
            edge_id: Edge ID to delete

        Returns:
            True if deleted, False if not found
        """
        query = """
        MATCH ()-[r:RELATION {id: $id}]->()
        DELETE r
        RETURN count(r) as deleted
        """
        records = self._execute_read(query, {"id": edge_id})

        deleted = records[0]["deleted"] > 0 if records else False
        if deleted:
            logger.info(f"Deleted edge: {edge_id}")
        return deleted

    def get_node(self, node_id: str) -> dict[str, Any] | None:
        """Get a node from the graph.

        Args:
            node_id: Node ID

        Returns:
            Node data or None if not found
        """
        query = """
        MATCH (n:Node {id: $id})
        RETURN n.id as id, n.type as type, properties(n) as props
        """
        records = self._execute_read(query, {"id": node_id})

        if not records:
            return None

        record = records[0]
        props = dict(record["props"])
        props.pop("id", None)
        props.pop("type", None)

        return {
            "id": record["id"],
            "type": record["type"],
            "properties": props,
        }

    def get_edge(self, edge_id: str) -> dict[str, Any] | None:
        """Get an edge from the graph.

        Args:
            edge_id: Edge ID

        Returns:
            Edge data or None if not found
        """
        query = """
        MATCH (source:Node)-[r:RELATION {id: $id}]->(target:Node)
        RETURN r.id as id, source.id as source, target.id as target,
               r.relation_type as relation, properties(r) as props
        """
        records = self._execute_read(query, {"id": edge_id})

        if not records:
            return None

        record = records[0]
        props = dict(record["props"])
        props.pop("id", None)
        props.pop("relation_type", None)

        return {
            "id": record["id"],
            "source": record["source"],
            "target": record["target"],
            "relation": record["relation"],
            "properties": props,
        }

    def query_neighbors(self, node_id: str) -> list[dict[str, Any]]:
        """Query neighbors of a node (both directions).

        Args:
            node_id: Node ID

        Returns:
            List of neighbor nodes
        """
        query = """
        MATCH (n:Node {id: $id})-[r]-(neighbor:Node)
        RETURN DISTINCT neighbor.id as id, neighbor.type as type,
               properties(neighbor) as props
        """
        records = self._execute_read(query, {"id": node_id})

        neighbors = []
        for record in records:
            props = dict(record["props"])
            props.pop("id", None)
            props.pop("type", None)

            neighbors.append({
                "id": record["id"],
                "type": record["type"],
                "properties": props,
            })

        return neighbors

    def query_edges_from(self, node_id: str) -> list[dict[str, Any]]:
        """Query outgoing edges from a node.

        Args:
            node_id: Node ID

        Returns:
            List of outgoing edges
        """
        query = """
        MATCH (source:Node {id: $id})-[r:RELATION]->(target:Node)
        RETURN r.id as id, source.id as source, target.id as target,
               r.relation_type as relation, properties(r) as props
        """
        records = self._execute_read(query, {"id": node_id})

        edges = []
        for record in records:
            props = dict(record["props"])
            props.pop("id", None)
            props.pop("relation_type", None)

            edges.append({
                "id": record["id"],
                "source": record["source"],
                "target": record["target"],
                "relation": record["relation"],
                "properties": props,
            })

        return edges

    def clear_all(self, confirm: bool = False) -> None:
        """Clear all nodes and edges from the graph.

        WARNING: This is destructive and cannot be undone!

        Args:
            confirm: Must be True to execute (safety check)

        Raises:
            ValueError: If confirm is not True
        """
        if not confirm:
            raise ValueError(
                "Must pass confirm=True to clear all data. "
                "This operation cannot be undone!"
            )

        query = "MATCH (n) DETACH DELETE n"
        self._execute_query(query)
        logger.warning("Cleared all nodes and edges from graph")

    # ========== Utility Operations ==========

    def count_nodes_by_type(self) -> dict[str, int]:
        """
        Count nodes by type.

        Returns:
            Dictionary with counts for each node type
        """
        query = HCGQueries.count_nodes_by_type()
        records = self._execute_read(query)

        if not records:
            return {
                "entity_count": 0,
                "concept_count": 0,
                "state_count": 0,
                "process_count": 0,
            }

        return dict(records[0])

    def verify_connection(self) -> bool:
        """
        Verify that the connection to Neo4j is working.

        Returns:
            True if connection is working, False otherwise
        """
        try:
            self.driver.verify_connectivity()
            return True
        except Exception as e:
            logger.error(f"Connection verification failed: {e}")
            return False
