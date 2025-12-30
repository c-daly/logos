"""
Common Cypher queries for HCG graph operations.

This module provides parameterized Cypher queries for:
- Finding nodes by type or ancestry
- Traversing type hierarchy via IS_A edges
- Querying graph structure

All queries use parameters to prevent injection attacks.
See Project LOGOS spec: Section 4.1 for relationship types.

FLEXIBLE ONTOLOGY:
All nodes use the :Node label with these properties:
- uuid: unique identifier
- name: human-readable name
- is_type_definition: boolean (true for types, false for instances)
- type: immediate type name
- ancestors: list of ancestor types up to bootstrap root

Query patterns:
- Exact type: MATCH (n:Node {type: "my_type"})
- Type definitions: MATCH (n:Node {is_type_definition: true})
- All states: MATCH (n:Node) WHERE n.type = "state" OR "state" IN n.ancestors
- Type hierarchy: MATCH (n)-[:IS_A*]->(t {name: "concept"})
"""


class HCGQueries:
    """Collection of common Cypher queries for HCG operations."""

    # ========== Generic Node Queries ==========

    @staticmethod
    def find_node_by_uuid() -> str:
        """
        Find any node by its UUID.

        Parameters:
        - uuid: Node UUID (string format)

        Returns: Node properties
        """
        return """
        MATCH (n:Node {uuid: $uuid})
        RETURN n
        """

    @staticmethod
    def find_nodes_by_type() -> str:
        """
        Find nodes by exact type.

        Parameters:
        - type: Node type (exact match)

        Returns: List of matching nodes
        """
        return """
        MATCH (n:Node {type: $type})
        RETURN n
        ORDER BY n.name
        """

    @staticmethod
    def find_nodes_by_ancestor() -> str:
        """
        Find nodes that have a given type in their ancestry.

        Parameters:
        - ancestor: Ancestor type name to search for

        Returns: List of matching nodes
        """
        return """
        MATCH (n:Node)
        WHERE n.type = $ancestor OR $ancestor IN n.ancestors
        RETURN n
        ORDER BY n.name
        """

    @staticmethod
    def find_node_by_name() -> str:
        """
        Find nodes by name (case-insensitive partial match).

        Parameters:
        - name: Node name pattern

        Returns: List of matching nodes
        """
        return """
        MATCH (n:Node)
        WHERE toLower(n.name) CONTAINS toLower($name)
        RETURN n
        ORDER BY n.name
        """

    @staticmethod
    def find_node_by_type_and_name() -> str:
        """
        Find a node by type and exact name.

        Parameters:
        - type: Node type
        - name: Exact name

        Returns: Node properties
        """
        return """
        MATCH (n:Node {type: $type, name: $name})
        RETURN n
        """

    # ========== Entity Queries (things) ==========

    @staticmethod
    def find_entity_by_uuid() -> str:
        """
        Find an entity by its UUID.

        Parameters:
        - uuid: Entity UUID (string format)

        Returns: Entity node properties
        """
        return """
        MATCH (e:Node {uuid: $uuid})
        WHERE "thing" IN e.ancestors
        RETURN e
        """

    @staticmethod
    def find_entity_by_name() -> str:
        """
        Find entities by name (case-insensitive partial match).

        Parameters:
        - name: Entity name pattern

        Returns: List of matching Entity nodes
        """
        return """
        MATCH (e:Node)
        WHERE "thing" IN e.ancestors
          AND toLower(e.name) CONTAINS toLower($name)
        RETURN e
        ORDER BY e.name
        """

    @staticmethod
    def find_all_entities() -> str:
        """
        Find all entities with optional pagination.

        Parameters:
        - skip: Number of records to skip (default 0)
        - limit: Maximum records to return (default 100)

        Returns: List of Entity nodes
        """
        return """
        MATCH (e:Node)
        WHERE "thing" IN e.ancestors
        RETURN e
        ORDER BY e.name
        SKIP $skip
        LIMIT $limit
        """

    # ========== Concept Queries ==========

    @staticmethod
    def find_concept_by_uuid() -> str:
        """
        Find a concept by its UUID.

        Parameters:
        - uuid: Concept UUID (string format)

        Returns: Concept node properties
        """
        return """
        MATCH (c:Node {uuid: $uuid})
        WHERE c.type = "concept" OR "concept" IN c.ancestors
        RETURN c
        """

    @staticmethod
    def find_concept_by_name() -> str:
        """
        Find a concept by exact name.

        Parameters:
        - name: Concept name (exact match)

        Returns: Concept node properties
        """
        return """
        MATCH (c:Node {name: $name})
        WHERE c.type = "concept" OR "concept" IN c.ancestors
        RETURN c
        """

    @staticmethod
    def find_all_concepts() -> str:
        """
        Find all concepts.

        Returns: List of Concept nodes
        """
        return """
        MATCH (c:Node)
        WHERE c.type = "concept" OR "concept" IN c.ancestors
        RETURN c
        ORDER BY c.name
        """

    # ========== Type Definition Queries ==========

    @staticmethod
    def find_type_definition() -> str:
        """
        Find a type definition by name.

        Parameters:
        - name: Type name

        Returns: Type definition node
        """
        return """
        MATCH (t:Node {is_type_definition: true, name: $name})
        RETURN t
        """

    @staticmethod
    def find_all_type_definitions() -> str:
        """
        Find all type definitions.

        Returns: List of type definition nodes
        """
        return """
        MATCH (t:Node {is_type_definition: true})
        RETURN t
        ORDER BY t.name
        """

    @staticmethod
    def get_type_hierarchy() -> str:
        """
        Get the type hierarchy for a type.

        Parameters:
        - type_name: Name of the type

        Returns: Path through type hierarchy
        """
        return """
        MATCH (t:Node {name: $type_name})
        OPTIONAL MATCH path = (t)-[:IS_A*]->(parent:Node)
        RETURN t, collect(nodes(path)) as hierarchy
        """

    # ========== State Queries ==========

    @staticmethod
    def find_state_by_uuid() -> str:
        """
        Find a state by its UUID.

        Parameters:
        - uuid: State UUID (string format)

        Returns: State node properties
        """
        return """
        MATCH (s:Node {uuid: $uuid})
        WHERE s.type = "state" OR "state" IN s.ancestors
        RETURN s
        """

    @staticmethod
    def find_states_by_timestamp_range() -> str:
        """
        Find states within a timestamp range.

        Parameters:
        - start_time: Start timestamp (ISO format string)
        - end_time: End timestamp (ISO format string)

        Returns: List of State nodes ordered by timestamp
        """
        return """
        MATCH (s:Node)
        WHERE (s.type = "state" OR "state" IN s.ancestors)
          AND s.timestamp >= datetime($start_time)
          AND s.timestamp <= datetime($end_time)
        RETURN s
        ORDER BY s.timestamp
        """

    @staticmethod
    def find_all_states() -> str:
        """
        Find all states.

        Returns: List of State nodes
        """
        return """
        MATCH (s:Node)
        WHERE s.type = "state" OR "state" IN s.ancestors
        RETURN s
        ORDER BY s.timestamp DESC
        """

    # ========== Process Queries ==========

    @staticmethod
    def find_process_by_uuid() -> str:
        """
        Find a process by its UUID.

        Parameters:
        - uuid: Process UUID (string format)

        Returns: Process node properties
        """
        return """
        MATCH (p:Node {uuid: $uuid})
        WHERE p.type = "process" OR "process" IN p.ancestors
        RETURN p
        """

    @staticmethod
    def find_processes_by_time_range() -> str:
        """
        Find processes within a time range.

        Parameters:
        - start_time: Start timestamp (ISO format string)
        - end_time: End timestamp (ISO format string)

        Returns: List of Process nodes ordered by start_time
        """
        return """
        MATCH (p:Node)
        WHERE (p.type = "process" OR "process" IN p.ancestors)
          AND p.start_time >= datetime($start_time)
          AND p.start_time <= datetime($end_time)
        RETURN p
        ORDER BY p.start_time
        """

    @staticmethod
    def find_all_processes() -> str:
        """
        Find all processes.

        Returns: List of Process nodes
        """
        return """
        MATCH (p:Node)
        WHERE p.type = "process" OR "process" IN p.ancestors
        RETURN p
        ORDER BY p.start_time DESC
        """

    # ========== Relationship Queries ==========

    @staticmethod
    def get_node_type() -> str:
        """
        Get the type of a node via IS_A relationship.

        Parameters:
        - uuid: Node UUID (string format)

        Returns: Type node that this node is an instance of
        """
        return """
        MATCH (n:Node {uuid: $uuid})-[:IS_A]->(t:Node)
        RETURN t
        """

    @staticmethod
    def get_entity_states() -> str:
        """
        Get all states of an entity via HAS_STATE relationship.

        Parameters:
        - entity_uuid: Entity UUID (string format)

        Returns: List of State nodes ordered by timestamp
        """
        return """
        MATCH (e:Node {uuid: $entity_uuid})-[:HAS_STATE]->(s:Node)
        RETURN s
        ORDER BY s.timestamp DESC
        """

    @staticmethod
    def get_entity_current_state() -> str:
        """
        Get the most recent state of an entity.

        Parameters:
        - entity_uuid: Entity UUID (string format)

        Returns: Most recent State node
        """
        return """
        MATCH (e:Node {uuid: $entity_uuid})-[:HAS_STATE]->(s:Node)
        RETURN s
        ORDER BY s.timestamp DESC
        LIMIT 1
        """

    @staticmethod
    def get_process_preconditions() -> str:
        """
        Get states required by a process (REQUIRES relationship).

        Parameters:
        - process_uuid: Process UUID (string format)

        Returns: List of State nodes that are preconditions
        """
        return """
        MATCH (p:Node {uuid: $process_uuid})-[:REQUIRES]->(s:Node)
        RETURN s
        """

    @staticmethod
    def get_process_effects() -> str:
        """
        Get states caused by a process (CAUSES relationship).

        Parameters:
        - process_uuid: Process UUID (string format)

        Returns: List of State nodes that are effects
        """
        return """
        MATCH (p:Node {uuid: $process_uuid})-[:CAUSES]->(s:Node)
        RETURN s
        """

    # ========== Create Queries ==========

    @staticmethod
    def create_type_definition() -> str:
        """
        Create a new type definition.

        Parameters:
        - uuid: Node UUID
        - name: Type name
        - ancestors: List of ancestor type names
        - description: Optional description

        Returns: Created node
        """
        return """
        CREATE (t:Node {
            uuid: $uuid,
            name: $name,
            is_type_definition: true,
            type: $name,
            ancestors: $ancestors,
            description: $description
        })
        RETURN t
        """

    @staticmethod
    def create_instance() -> str:
        """
        Create a new instance of a type.

        Parameters:
        - uuid: Node UUID
        - name: Instance name
        - type: Type name
        - ancestors: List of ancestor type names
        - description: Optional description

        Returns: Created node
        """
        return """
        CREATE (n:Node {
            uuid: $uuid,
            name: $name,
            is_type_definition: false,
            type: $type,
            ancestors: $ancestors,
            description: $description
        })
        RETURN n
        """

    @staticmethod
    def create_entity() -> str:
        """
        Create a new entity (instance of thing).

        Parameters:
        - uuid: Entity UUID
        - name: Entity name
        - type: Specific entity type (default "entity")
        - ancestors: List of ancestor types
        - description: Optional description

        Returns: Created entity node
        """
        return """
        CREATE (e:Node {
            uuid: $uuid,
            name: $name,
            is_type_definition: false,
            type: $type,
            ancestors: $ancestors,
            description: $description,
            created_at: datetime()
        })
        RETURN e
        """

    @staticmethod
    def create_state() -> str:
        """
        Create a new state.

        Parameters:
        - uuid: State UUID
        - name: State name
        - type: Specific state type (default "state")
        - ancestors: List of ancestor types
        - timestamp: Optional timestamp (defaults to now)

        Returns: Created state node
        """
        return """
        CREATE (s:Node {
            uuid: $uuid,
            name: $name,
            is_type_definition: false,
            type: $type,
            ancestors: $ancestors,
            timestamp: COALESCE($timestamp, datetime())
        })
        RETURN s
        """

    @staticmethod
    def create_process() -> str:
        """
        Create a new process.

        Parameters:
        - uuid: Process UUID
        - name: Process name
        - type: Specific process type (default "process")
        - ancestors: List of ancestor types
        - description: Optional description
        - duration_ms: Optional duration in milliseconds

        Returns: Created process node
        """
        return """
        CREATE (p:Node {
            uuid: $uuid,
            name: $name,
            is_type_definition: false,
            type: $type,
            ancestors: $ancestors,
            description: $description,
            start_time: datetime(),
            duration_ms: $duration_ms
        })
        RETURN p
        """

    # ========== Link Queries ==========

    @staticmethod
    def link_is_a() -> str:
        """
        Create IS_A relationship between nodes.

        Parameters:
        - from_uuid: Source node UUID
        - to_uuid: Target node UUID

        Returns: Created relationship
        """
        return """
        MATCH (from:Node {uuid: $from_uuid})
        MATCH (to:Node {uuid: $to_uuid})
        CREATE (from)-[r:IS_A]->(to)
        RETURN r
        """

    @staticmethod
    def link_has_state() -> str:
        """
        Create HAS_STATE relationship between entity and state.

        Parameters:
        - entity_uuid: Entity node UUID
        - state_uuid: State node UUID

        Returns: Created relationship
        """
        return """
        MATCH (e:Node {uuid: $entity_uuid})
        MATCH (s:Node {uuid: $state_uuid})
        CREATE (e)-[r:HAS_STATE]->(s)
        RETURN r
        """

    @staticmethod
    def link_requires() -> str:
        """
        Create REQUIRES relationship between process and state.

        Parameters:
        - process_uuid: Process node UUID
        - state_uuid: State node UUID

        Returns: Created relationship
        """
        return """
        MATCH (p:Node {uuid: $process_uuid})
        MATCH (s:Node {uuid: $state_uuid})
        CREATE (p)-[r:REQUIRES]->(s)
        RETURN r
        """

    @staticmethod
    def link_causes() -> str:
        """
        Create CAUSES relationship between process and state.

        Parameters:
        - process_uuid: Process node UUID
        - state_uuid: State node UUID

        Returns: Created relationship
        """
        return """
        MATCH (p:Node {uuid: $process_uuid})
        MATCH (s:Node {uuid: $state_uuid})
        CREATE (p)-[r:CAUSES]->(s)
        RETURN r
        """

    # ========== Update Queries ==========

    @staticmethod
    def update_node_properties() -> str:
        """
        Update properties on a node.

        Parameters:
        - uuid: Node UUID
        - properties: Map of properties to set

        Returns: Updated node
        """
        return """
        MATCH (n:Node {uuid: $uuid})
        SET n += $properties
        RETURN n
        """

    # ========== Delete Queries ==========

    @staticmethod
    def delete_node() -> str:
        """
        Delete a node and its relationships.

        Parameters:
        - uuid: Node UUID

        Returns: Count of deleted nodes
        """
        return """
        MATCH (n:Node {uuid: $uuid})
        DETACH DELETE n
        RETURN count(n) as deleted
        """

    # ========== Validation Queries ==========

    @staticmethod
    def verify_constraints() -> str:
        """
        Show all constraints in the database.

        Returns: List of constraints
        """
        return "SHOW CONSTRAINTS"

    @staticmethod
    def verify_indexes() -> str:
        """
        Show all indexes in the database.

        Returns: List of indexes
        """
        return "SHOW INDEXES"

    @staticmethod
    def count_nodes_by_type() -> str:
        """
        Count nodes grouped by type.

        Returns: Type counts
        """
        return """
        MATCH (n:Node)
        RETURN n.type as type, count(n) as count
        ORDER BY count DESC
        """

    @staticmethod
    def count_type_definitions() -> str:
        """
        Count type definitions vs instances.

        Returns: Counts by is_type_definition
        """
        return """
        MATCH (n:Node)
        RETURN n.is_type_definition as is_type_def, count(n) as count
        """
