"""
Common Cypher queries for HCG graph operations.

This module provides parameterized Cypher queries for:
- Finding entities, concepts, states, and processes
- Traversing causal relationships
- Querying graph structure (IS_A, HAS_STATE, PART_OF, etc.)

All queries use parameters to prevent injection attacks.
See Project LOGOS spec: Section 4.1 for relationship types.
"""


class HCGQueries:
    """Collection of common Cypher queries for HCG operations."""

    # ========== Entity Queries ==========

    @staticmethod
    def find_entity_by_uuid() -> str:
        """
        Find an entity by its UUID.

        Parameters:
        - uuid: Entity UUID (string format)

        Returns: Entity node properties
        """
        return """
        MATCH (e:Entity {uuid: $uuid})
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
        MATCH (e:Entity)
        WHERE toLower(e.name) CONTAINS toLower($name)
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
        MATCH (e:Entity)
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
        MATCH (c:Concept {uuid: $uuid})
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
        MATCH (c:Concept {name: $name})
        RETURN c
        """

    @staticmethod
    def find_all_concepts() -> str:
        """
        Find all concepts.

        Returns: List of Concept nodes
        """
        return """
        MATCH (c:Concept)
        RETURN c
        ORDER BY c.name
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
        MATCH (s:State {uuid: $uuid})
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
        MATCH (s:State)
        WHERE s.timestamp >= datetime($start_time)
          AND s.timestamp <= datetime($end_time)
        RETURN s
        ORDER BY s.timestamp
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
        MATCH (p:Process {uuid: $uuid})
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
        MATCH (p:Process)
        WHERE p.start_time >= datetime($start_time)
          AND p.start_time <= datetime($end_time)
        RETURN p
        ORDER BY p.start_time
        """

    # ========== Relationship Queries ==========

    @staticmethod
    def get_entity_type() -> str:
        """
        Get the concept/type of an entity via IS_A relationship.

        Parameters:
        - entity_uuid: Entity UUID (string format)

        Returns: Concept node that the entity is an instance of
        """
        return """
        MATCH (e:Entity {uuid: $entity_uuid})-[:IS_A]->(c:Concept)
        RETURN c
        """

    @staticmethod
    def get_entity_states() -> str:
        """
        Get all states of an entity via HAS_STATE relationship.

        Parameters:
        - entity_uuid: Entity UUID (string format)

        Returns: List of State nodes ordered by timestamp (most recent first)
        """
        return """
        MATCH (e:Entity {uuid: $entity_uuid})-[:HAS_STATE]->(s:State)
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
        MATCH (e:Entity {uuid: $entity_uuid})-[:HAS_STATE]->(s:State)
        RETURN s
        ORDER BY s.timestamp DESC
        LIMIT 1
        """

    @staticmethod
    def get_entity_parts() -> str:
        """
        Get all parts of an entity via PART_OF relationship.

        Parameters:
        - entity_uuid: Entity UUID (string format)

        Returns: List of Entity nodes that are parts of the given entity
        """
        return """
        MATCH (part:Entity)-[:PART_OF]->(whole:Entity {uuid: $entity_uuid})
        RETURN part
        ORDER BY part.name
        """

    @staticmethod
    def get_entity_parent() -> str:
        """
        Get the parent entity via PART_OF relationship.

        Parameters:
        - entity_uuid: Entity UUID (string format)

        Returns: Parent Entity node
        """
        return """
        MATCH (part:Entity {uuid: $entity_uuid})-[:PART_OF]->(whole:Entity)
        RETURN whole
        """

    # ========== Causal Traversal Queries ==========

    @staticmethod
    def traverse_causality_forward(max_depth: int = 10) -> str:
        """
        Traverse causality chain forward from a state.
        Find all states that are caused (directly or indirectly) by processes
        that are caused by the given state.

        Parameters:
        - state_uuid: Starting State UUID (string format)
        - max_depth: Maximum traversal depth (default 10)

        Returns: List of (Process, State) pairs showing causal chain
        """
        return f"""
        MATCH path = (s:State {{uuid: $state_uuid}})<-[:REQUIRES*0..1]-
                     (p:Process)-[:CAUSES*1..{max_depth}]->(result:State)
        RETURN p, result, length(path) as depth
        ORDER BY depth, result.timestamp
        """

    @staticmethod
    def traverse_causality_backward(max_depth: int = 10) -> str:
        """
        Traverse causality chain backward from a state.
        Find all states that caused (directly or indirectly) the given state.

        Parameters:
        - state_uuid: Target State UUID (string format)
        - max_depth: Maximum traversal depth (default 10)

        Returns: List of (State, Process) pairs showing causal history
        """
        return f"""
        MATCH path = (cause:State)<-[:CAUSES*1..{max_depth}]-(p:Process)
                     -[:REQUIRES*0..1]->(s:State {{uuid: $state_uuid}})
        RETURN cause, p, length(path) as depth
        ORDER BY depth DESC, cause.timestamp DESC
        """

    @staticmethod
    def get_process_causes() -> str:
        """
        Get all states caused by a process.

        Parameters:
        - process_uuid: Process UUID (string format)

        Returns: List of State nodes caused by the process
        """
        return """
        MATCH (p:Process {uuid: $process_uuid})-[:CAUSES]->(s:State)
        RETURN s
        ORDER BY s.timestamp
        """

    @staticmethod
    def get_process_requirements() -> str:
        """
        Get all states required by a process (preconditions).

        Parameters:
        - process_uuid: Process UUID (string format)

        Returns: List of State nodes required by the process
        """
        return """
        MATCH (p:Process {uuid: $process_uuid})-[:REQUIRES]->(s:State)
        RETURN s
        ORDER BY s.timestamp
        """

    @staticmethod
    def get_state_effects() -> str:
        """
        Get all states that follow from this state via temporal ordering.

        Parameters:
        - state_uuid: State UUID (string format)

        Returns: List of State nodes that follow this state
        """
        return """
        MATCH (s:State {uuid: $state_uuid})-[:PRECEDES]->(next:State)
        RETURN next
        ORDER BY next.timestamp
        """

    # ========== Spatial/Physical Queries ==========

    @staticmethod
    def get_entity_location() -> str:
        """
        Get the location of an entity via LOCATED_AT relationship.

        Parameters:
        - entity_uuid: Entity UUID (string format)

        Returns: Entity node where the given entity is located
        """
        return """
        MATCH (e:Entity {uuid: $entity_uuid})-[:LOCATED_AT]->(loc:Entity)
        RETURN loc
        """

    @staticmethod
    def get_entities_at_location() -> str:
        """
        Get all entities at a specific location.

        Parameters:
        - location_uuid: Location Entity UUID (string format)

        Returns: List of Entity nodes at the location
        """
        return """
        MATCH (e:Entity)-[:LOCATED_AT]->(loc:Entity {uuid: $location_uuid})
        RETURN e
        ORDER BY e.name
        """

    @staticmethod
    def get_entity_attachments() -> str:
        """
        Get all entities attached to this entity.

        Parameters:
        - entity_uuid: Entity UUID (string format)

        Returns: List of Entity nodes attached to the given entity
        """
        return """
        MATCH (attached:Entity)-[:ATTACHED_TO]->(e:Entity {uuid: $entity_uuid})
        RETURN attached
        ORDER BY attached.name
        """

    # ========== Utility Queries ==========

    @staticmethod
    def get_node_relationships() -> str:
        """
        Get all relationships for a node (any type).

        Parameters:
        - uuid: Node UUID (string format)

        Returns: List of relationship types, target nodes, and directions
        """
        return """
        MATCH (n {uuid: $uuid})
        OPTIONAL MATCH (n)-[r]->(target)
        WITH n, collect({type: type(r), direction: 'outgoing', node: target}) as outgoing
        OPTIONAL MATCH (source)-[r2]->(n)
        WITH n, outgoing, collect({type: type(r2), direction: 'incoming', node: source}) as incoming
        RETURN n, outgoing + incoming as relationships
        """

    @staticmethod
    def count_nodes_by_type() -> str:
        """
        Count nodes by type.

        Returns: Counts for each node type
        """
        return """
        OPTIONAL MATCH (e:Entity)
        WITH count(e) as entity_count
        OPTIONAL MATCH (c:Concept)
        WITH entity_count, count(c) as concept_count
        OPTIONAL MATCH (s:State)
        WITH entity_count, concept_count, count(s) as state_count
        OPTIONAL MATCH (p:Process)
        WITH entity_count, concept_count, state_count, count(p) as process_count
        OPTIONAL MATCH (cap:Capability)
        RETURN entity_count, concept_count, state_count, process_count, count(cap) as capability_count
        """

    # ========== Capability Catalog Queries (logos#284) ==========

    @staticmethod
    def find_capability_by_uuid() -> str:
        """
        Find a capability by its UUID.

        Parameters:
        - uuid: Capability UUID (string format)

        Returns: Capability node properties
        """
        return """
        MATCH (cap:Capability {uuid: $uuid})
        RETURN cap
        """

    @staticmethod
    def find_capability_by_name() -> str:
        """
        Find a capability by exact name.

        Parameters:
        - name: Capability name (exact match)

        Returns: Capability node properties
        """
        return """
        MATCH (cap:Capability {name: $name})
        RETURN cap
        """

    @staticmethod
    def find_capabilities_by_executor_type() -> str:
        """
        Find capabilities by executor type.

        Parameters:
        - executor_type: Type of executor ('human', 'talos', 'service', 'llm')

        Returns: List of matching Capability nodes
        """
        return """
        MATCH (cap:Capability {executor_type: $executor_type})
        WHERE cap.deprecated IS NULL OR cap.deprecated = false
        RETURN cap
        ORDER BY cap.name
        """

    @staticmethod
    def find_capabilities_by_tag() -> str:
        """
        Find capabilities that have a specific tag.

        Parameters:
        - tag: Capability tag to search for

        Returns: List of matching Capability nodes
        """
        return """
        MATCH (cap:Capability)
        WHERE $tag IN cap.capability_tags
          AND (cap.deprecated IS NULL OR cap.deprecated = false)
        RETURN cap
        ORDER BY cap.name
        """

    @staticmethod
    def find_capabilities_by_tags() -> str:
        """
        Find capabilities that have ALL of the specified tags.

        Parameters:
        - tags: List of capability tags (all must match)

        Returns: List of matching Capability nodes
        """
        return """
        MATCH (cap:Capability)
        WHERE all(tag IN $tags WHERE tag IN cap.capability_tags)
          AND (cap.deprecated IS NULL OR cap.deprecated = false)
        RETURN cap
        ORDER BY cap.name
        """

    @staticmethod
    def find_capabilities_by_any_tag() -> str:
        """
        Find capabilities that have ANY of the specified tags.

        Parameters:
        - tags: List of capability tags (any can match)

        Returns: List of matching Capability nodes
        """
        return """
        MATCH (cap:Capability)
        WHERE any(tag IN $tags WHERE tag IN cap.capability_tags)
          AND (cap.deprecated IS NULL OR cap.deprecated = false)
        RETURN cap
        ORDER BY cap.name
        """

    @staticmethod
    def find_capabilities_implementing_concept() -> str:
        """
        Find capabilities that implement a specific action concept.

        Parameters:
        - concept_uuid: UUID of the action concept (e.g., 'concept-grasp')

        Returns: List of Capability nodes that implement the concept
        """
        return """
        MATCH (cap:Capability)-[:IMPLEMENTS]->(c:Concept {uuid: $concept_uuid})
        WHERE cap.deprecated IS NULL OR cap.deprecated = false
        RETURN cap
        ORDER BY cap.success_rate DESC, cap.estimated_cost ASC
        """

    @staticmethod
    def find_capabilities_for_entity() -> str:
        """
        Find capabilities that can be executed by a specific entity.

        Parameters:
        - entity_uuid: UUID of the entity

        Returns: List of Capability nodes executable by the entity
        """
        return """
        MATCH (cap:Capability)-[:EXECUTED_BY]->(e:Entity {uuid: $entity_uuid})
        WHERE cap.deprecated IS NULL OR cap.deprecated = false
        RETURN cap
        ORDER BY cap.name
        """

    @staticmethod
    def find_capabilities_with_inputs() -> str:
        """
        Find capabilities and their required input types.

        Parameters:
        - capability_uuid: UUID of the capability

        Returns: Capability with list of required input concepts
        """
        return """
        MATCH (cap:Capability {uuid: $capability_uuid})
        OPTIONAL MATCH (cap)-[:REQUIRES_INPUT]->(input:Concept)
        RETURN cap, collect(input) as required_inputs
        """

    @staticmethod
    def find_capabilities_with_outputs() -> str:
        """
        Find capabilities and their output types.

        Parameters:
        - capability_uuid: UUID of the capability

        Returns: Capability with list of output concepts
        """
        return """
        MATCH (cap:Capability {uuid: $capability_uuid})
        OPTIONAL MATCH (cap)-[:PRODUCES_OUTPUT]->(output:Concept)
        RETURN cap, collect(output) as produced_outputs
        """

    @staticmethod
    def find_all_capabilities() -> str:
        """
        Find all active capabilities with optional pagination.

        Parameters:
        - skip: Number of records to skip (default 0)
        - limit: Maximum records to return (default 100)
        - include_deprecated: Whether to include deprecated capabilities (default false)

        Returns: List of Capability nodes
        """
        return """
        MATCH (cap:Capability)
        WHERE $include_deprecated = true OR cap.deprecated IS NULL OR cap.deprecated = false
        RETURN cap
        ORDER BY cap.name
        SKIP $skip
        LIMIT $limit
        """

    @staticmethod
    def search_capabilities() -> str:
        """
        Search capabilities by name/description (case-insensitive partial match).

        Parameters:
        - query: Search query string

        Returns: List of matching Capability nodes
        """
        return """
        MATCH (cap:Capability)
        WHERE (toLower(cap.name) CONTAINS toLower($query)
               OR toLower(cap.description) CONTAINS toLower($query))
          AND (cap.deprecated IS NULL OR cap.deprecated = false)
        RETURN cap
        ORDER BY cap.name
        """

    @staticmethod
    def get_capability_with_full_context() -> str:
        """
        Get a capability with all its relationships (inputs, outputs, executors, implements).

        Parameters:
        - uuid: Capability UUID

        Returns: Capability with all related concepts and entities
        """
        return """
        MATCH (cap:Capability {uuid: $uuid})
        OPTIONAL MATCH (cap)-[:IMPLEMENTS]->(impl:Concept)
        OPTIONAL MATCH (cap)-[:REQUIRES_INPUT]->(input:Concept)
        OPTIONAL MATCH (cap)-[:PRODUCES_OUTPUT]->(output:Concept)
        OPTIONAL MATCH (cap)-[:EXECUTED_BY]->(executor:Entity)
        RETURN cap,
               collect(DISTINCT impl) as implements,
               collect(DISTINCT input) as required_inputs,
               collect(DISTINCT output) as produced_outputs,
               collect(DISTINCT executor) as executors
        """

    # ========== Capability Mutation Queries ==========

    @staticmethod
    def create_capability() -> str:
        """
        Create a new capability.

        Parameters:
        - uuid: Capability UUID (must start with 'capability-')
        - name: Unique capability name
        - executor_type: Type of executor ('human', 'talos', 'service', 'llm')
        - description: Optional description
        - capability_tags: Optional list of tags
        - version: Optional version string
        - estimated_duration_ms: Optional duration estimate
        - estimated_cost: Optional cost estimate

        Returns: Created Capability node
        """
        return """
        CREATE (cap:Capability {
            uuid: $uuid,
            name: $name,
            executor_type: $executor_type,
            description: $description,
            capability_tags: $capability_tags,
            version: $version,
            estimated_duration_ms: $estimated_duration_ms,
            estimated_cost: $estimated_cost,
            success_rate: 1.0,
            invocation_count: 0,
            deprecated: false,
            created_at: datetime(),
            updated_at: datetime()
        })
        RETURN cap
        """

    @staticmethod
    def update_capability() -> str:
        """
        Update an existing capability.

        Parameters:
        - uuid: Capability UUID
        - (other parameters as needed)

        Returns: Updated Capability node
        """
        return """
        MATCH (cap:Capability {uuid: $uuid})
        SET cap.name = COALESCE($name, cap.name),
            cap.description = COALESCE($description, cap.description),
            cap.capability_tags = COALESCE($capability_tags, cap.capability_tags),
            cap.version = COALESCE($version, cap.version),
            cap.estimated_duration_ms = COALESCE($estimated_duration_ms, cap.estimated_duration_ms),
            cap.estimated_cost = COALESCE($estimated_cost, cap.estimated_cost),
            cap.updated_at = datetime()
        RETURN cap
        """

    @staticmethod
    def deprecate_capability() -> str:
        """
        Mark a capability as deprecated.

        Parameters:
        - uuid: Capability UUID

        Returns: Deprecated Capability node
        """
        return """
        MATCH (cap:Capability {uuid: $uuid})
        SET cap.deprecated = true,
            cap.updated_at = datetime()
        RETURN cap
        """

    @staticmethod
    def record_capability_invocation() -> str:
        """
        Record a capability invocation and update success statistics.

        Parameters:
        - uuid: Capability UUID
        - success: Whether the invocation was successful (boolean)

        Returns: Updated Capability node with new statistics
        """
        return """
        MATCH (cap:Capability {uuid: $uuid})
        SET cap.invocation_count = COALESCE(cap.invocation_count, 0) + 1,
            cap.success_rate = CASE
                WHEN cap.invocation_count IS NULL OR cap.invocation_count = 0
                THEN CASE WHEN $success THEN 1.0 ELSE 0.0 END
                ELSE (cap.success_rate * cap.invocation_count + CASE WHEN $success THEN 1 ELSE 0 END) / (cap.invocation_count + 1)
            END,
            cap.updated_at = datetime()
        RETURN cap
        """

    @staticmethod
    def link_capability_to_concept() -> str:
        """
        Create an IMPLEMENTS relationship from capability to concept.

        Parameters:
        - capability_uuid: Capability UUID
        - concept_uuid: Concept UUID

        Returns: The created relationship
        """
        return """
        MATCH (cap:Capability {uuid: $capability_uuid})
        MATCH (c:Concept {uuid: $concept_uuid})
        MERGE (cap)-[r:IMPLEMENTS]->(c)
        RETURN cap, r, c
        """

    @staticmethod
    def link_capability_input() -> str:
        """
        Create a REQUIRES_INPUT relationship from capability to input type concept.

        Parameters:
        - capability_uuid: Capability UUID
        - concept_uuid: Input type Concept UUID

        Returns: The created relationship
        """
        return """
        MATCH (cap:Capability {uuid: $capability_uuid})
        MATCH (c:Concept {uuid: $concept_uuid})
        MERGE (cap)-[r:REQUIRES_INPUT]->(c)
        RETURN cap, r, c
        """

    @staticmethod
    def link_capability_output() -> str:
        """
        Create a PRODUCES_OUTPUT relationship from capability to output type concept.

        Parameters:
        - capability_uuid: Capability UUID
        - concept_uuid: Output type Concept UUID

        Returns: The created relationship
        """
        return """
        MATCH (cap:Capability {uuid: $capability_uuid})
        MATCH (c:Concept {uuid: $concept_uuid})
        MERGE (cap)-[r:PRODUCES_OUTPUT]->(c)
        RETURN cap, r, c
        """

    @staticmethod
    def link_capability_executor() -> str:
        """
        Create an EXECUTED_BY relationship from capability to executor entity.

        Parameters:
        - capability_uuid: Capability UUID
        - entity_uuid: Executor Entity UUID

        Returns: The created relationship
        """
        return """
        MATCH (cap:Capability {uuid: $capability_uuid})
        MATCH (e:Entity {uuid: $entity_uuid})
        MERGE (cap)-[r:EXECUTED_BY]->(e)
        RETURN cap, r, e
        """

    @staticmethod
    def link_process_to_capability() -> str:
        """
        Create a USES_CAPABILITY relationship from process to capability.

        Parameters:
        - process_uuid: Process UUID
        - capability_uuid: Capability UUID

        Returns: The created relationship
        """
        return """
        MATCH (p:Process {uuid: $process_uuid})
        MATCH (cap:Capability {uuid: $capability_uuid})
        MERGE (p)-[r:USES_CAPABILITY]->(cap)
        RETURN p, r, cap
        """
