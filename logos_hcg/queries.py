"""
Common Cypher queries for HCG graph operations.

This module provides parameterized Cypher queries for:
- Finding nodes by type
- Traversing type hierarchy via reified IS_A edge nodes
- Querying graph structure through :FROM/:TO structural relationships

All queries use parameters to prevent injection attacks.
See Project LOGOS spec: Section 4.1 for relationship types.

REIFIED EDGE MODEL:
All domain relationships are stored as edge nodes connected by
:FROM and :TO structural relationships (the ONLY native Neo4j rels):

    (source:Node)<-[:FROM]-(edge:Node {relation: "CAUSES"})-[:TO]->(target:Node)

Edge nodes carry: uuid, name, type="edge", relation, source, target,
bidirectional, created_at, updated_at.

Query patterns:
- Exact type: MATCH (n:Node {type: "my_type"})
- Type hierarchy: traverse IS_A edge nodes via :FROM/:TO
- Outgoing edges: MATCH (n)<-[:FROM]-(e:Node {type: "edge"})-[:TO]->(target)
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

    # ========== Edge Node Queries (new) ==========

    @staticmethod
    def get_outgoing_edges() -> str:
        """
        Get all outgoing edge nodes from a node via :FROM/:TO.

        Parameters:
        - uuid: Source node UUID

        Returns: edge relation, target_uuid, target_name, and edge node
        """
        return """
        MATCH (n:Node {uuid: $uuid})<-[:FROM]-(e:Node {type: "edge"})-[:TO]->(target:Node)
        RETURN e.relation AS relation, target.uuid AS target_uuid,
               target.name AS target_name, e
        """

    @staticmethod
    def get_incoming_edges() -> str:
        """
        Get all incoming edge nodes to a node via :FROM/:TO.

        Parameters:
        - uuid: Target node UUID

        Returns: edge relation, source_uuid, source_name, and edge node
        """
        return """
        MATCH (source:Node)<-[:FROM]-(e:Node {type: "edge"})-[:TO]->(n:Node {uuid: $uuid})
        RETURN e.relation AS relation, source.uuid AS source_uuid,
               source.name AS source_name, e
        """

    @staticmethod
    def get_edges_by_relation() -> str:
        """
        Get outgoing edges of a specific relation type from a node.

        Parameters:
        - uuid: Source node UUID
        - relation: Relation type (e.g. "IS_A", "CAUSES")

        Returns: target_uuid, target_name, and edge node
        """
        return """
        MATCH (n:Node {uuid: $uuid})<-[:FROM]-(e:Node {type: "edge", relation: $relation})-[:TO]->(target:Node)
        RETURN target.uuid AS target_uuid, target.name AS target_name, e
        """

    # ========== Entity Queries ==========

    # Known subtypes for each top-level category, derived from TYPE_PARENTS.
    ENTITY_TYPES = [
        "thing",
        "entity",
        "physical_entity",
        "agent",
        "object",
        "manipulator",
        "sensor",
        "spatial_entity",
        "location",
        "workspace",
        "zone",
        "process",
        "action",
        "step",
        "imagined_process",
        "proposed_plan_step",
        "proposed_tool_call",
        "intention",
        "goal",
        "plan",
        "hermes_proposal",
        "abstraction",
        "simulation",
        "execution",
        "data",
        "media_sample",
        "capability",
    ]
    STATE_TYPES = ["state", "imagined_state", "proposed_imagined_state"]
    PROCESS_TYPES = [
        "process",
        "action",
        "step",
        "imagined_process",
        "proposed_plan_step",
        "proposed_tool_call",
    ]

    @staticmethod
    def find_entity_by_uuid() -> str:
        """
        Find an entity by its UUID.
        Matches nodes whose type is in the entity hierarchy (descendants of
        'thing').

        Parameters:
        - uuid: Entity UUID (string format)

        Returns: Entity node properties
        """
        return """
        MATCH (e:Node {uuid: $uuid})
        WHERE e.type IN $entity_types
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
        WHERE e.type <> "edge"
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
        WHERE e.type <> "edge"
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
        WHERE c.type = "concept"
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
        WHERE c.type = "concept"
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
        WHERE c.type = "concept"
        RETURN c
        ORDER BY c.name
        """

    # ========== Type Definition Queries ==========

    @staticmethod
    def find_type_definitions() -> str:
        """
        Find all type definition nodes.
        Type definitions are nodes with type="type_definition".

        Returns: List of type definition nodes with name and uuid.
        """
        return """
        MATCH (t:Node {type: "type_definition"})
        RETURN t.name AS name, t.uuid AS uuid, t
        ORDER BY t.name
        """

    @staticmethod
    def find_type_definition() -> str:
        """
        Find a type definition by name.

        Parameters:
        - name: Type name

        Returns: Type definition node
        """
        return """
        MATCH (t:Node {type: "type_definition", name: $name})
        RETURN t
        """

    @staticmethod
    def get_type_hierarchy() -> str:
        """
        Get the type hierarchy for a type via reified IS_A edge nodes.
        Traverses up to 5 levels of IS_A.

        Parameters:
        - type_name: Name of the type

        Returns: Type node and its hierarchy
        """
        return """
        MATCH (t:Node {name: $type_name})
        OPTIONAL MATCH (t)<-[:FROM]-(e1:Node {type: "edge", relation: "IS_A"})-[:TO]->(p1:Node)
        OPTIONAL MATCH (p1)<-[:FROM]-(e2:Node {type: "edge", relation: "IS_A"})-[:TO]->(p2:Node)
        OPTIONAL MATCH (p2)<-[:FROM]-(e3:Node {type: "edge", relation: "IS_A"})-[:TO]->(p3:Node)
        OPTIONAL MATCH (p3)<-[:FROM]-(e4:Node {type: "edge", relation: "IS_A"})-[:TO]->(p4:Node)
        OPTIONAL MATCH (p4)<-[:FROM]-(e5:Node {type: "edge", relation: "IS_A"})-[:TO]->(p5:Node)
        RETURN t, [p1, p2, p3, p4, p5] AS hierarchy
        """

    # ========== Type Hierarchy Queries (new) ==========

    @staticmethod
    def has_ancestor() -> str:
        """
        Check if a node has a given ancestor in its IS_A chain.
        Checks up to 5 levels of IS_A traversal via reified edge nodes.

        Parameters:
        - uuid: Node UUID
        - ancestor_name: Name of the ancestor to check for

        Returns: Rows if ancestor found (empty if not)
        """
        return """
        MATCH (n:Node {uuid: $uuid})
        WHERE
          EXISTS {
            MATCH (n)<-[:FROM]-(e1:Node {type: "edge", relation: "IS_A"})-[:TO]->(a1:Node {name: $ancestor_name})
          }
          OR EXISTS {
            MATCH (n)<-[:FROM]-(:Node {type: "edge", relation: "IS_A"})-[:TO]->(m1:Node)
            MATCH (m1)<-[:FROM]-(e2:Node {type: "edge", relation: "IS_A"})-[:TO]->(a2:Node {name: $ancestor_name})
          }
          OR EXISTS {
            MATCH (n)<-[:FROM]-(:Node {type: "edge", relation: "IS_A"})-[:TO]->(m1:Node)
            MATCH (m1)<-[:FROM]-(:Node {type: "edge", relation: "IS_A"})-[:TO]->(m2:Node)
            MATCH (m2)<-[:FROM]-(e3:Node {type: "edge", relation: "IS_A"})-[:TO]->(a3:Node {name: $ancestor_name})
          }
          OR EXISTS {
            MATCH (n)<-[:FROM]-(:Node {type: "edge", relation: "IS_A"})-[:TO]->(m1:Node)
            MATCH (m1)<-[:FROM]-(:Node {type: "edge", relation: "IS_A"})-[:TO]->(m2:Node)
            MATCH (m2)<-[:FROM]-(:Node {type: "edge", relation: "IS_A"})-[:TO]->(m3:Node)
            MATCH (m3)<-[:FROM]-(e4:Node {type: "edge", relation: "IS_A"})-[:TO]->(a4:Node {name: $ancestor_name})
          }
          OR EXISTS {
            MATCH (n)<-[:FROM]-(:Node {type: "edge", relation: "IS_A"})-[:TO]->(m1:Node)
            MATCH (m1)<-[:FROM]-(:Node {type: "edge", relation: "IS_A"})-[:TO]->(m2:Node)
            MATCH (m2)<-[:FROM]-(:Node {type: "edge", relation: "IS_A"})-[:TO]->(m3:Node)
            MATCH (m3)<-[:FROM]-(:Node {type: "edge", relation: "IS_A"})-[:TO]->(m4:Node)
            MATCH (m4)<-[:FROM]-(e5:Node {type: "edge", relation: "IS_A"})-[:TO]->(a5:Node {name: $ancestor_name})
          }
        RETURN n
        """

    @staticmethod
    def find_instances_of_type() -> str:
        """
        Find instances whose IS_A chain reaches a named type.
        Searches up to 3 levels of IS_A depth using UNION.

        Parameters:
        - type_name: Name of the type to find instances of

        Returns: uuid and name of matching instances
        """
        return """
        MATCH (inst:Node)<-[:FROM]-(e:Node {type: "edge", relation: "IS_A"})-[:TO]->(t:Node {name: $type_name})
        WHERE inst.type <> "edge"
        RETURN inst.uuid AS uuid, inst.name AS name
        UNION
        MATCH (inst:Node)<-[:FROM]-(:Node {type: "edge", relation: "IS_A"})-[:TO]->(m1:Node)
        MATCH (m1)<-[:FROM]-(:Node {type: "edge", relation: "IS_A"})-[:TO]->(t:Node {name: $type_name})
        WHERE inst.type <> "edge"
        RETURN inst.uuid AS uuid, inst.name AS name
        UNION
        MATCH (inst:Node)<-[:FROM]-(:Node {type: "edge", relation: "IS_A"})-[:TO]->(m1:Node)
        MATCH (m1)<-[:FROM]-(:Node {type: "edge", relation: "IS_A"})-[:TO]->(m2:Node)
        MATCH (m2)<-[:FROM]-(:Node {type: "edge", relation: "IS_A"})-[:TO]->(t:Node {name: $type_name})
        WHERE inst.type <> "edge"
        RETURN inst.uuid AS uuid, inst.name AS name
        """

    @staticmethod
    def find_nodes_by_ancestor() -> str:
        """
        Find nodes that have a given type in their IS_A ancestry.
        Uses reified edge traversal up to 3 levels.

        Parameters:
        - ancestor: Ancestor type name to search for

        Returns: List of matching nodes
        """
        return """
        MATCH (n:Node)<-[:FROM]-(e:Node {type: "edge", relation: "IS_A"})-[:TO]->(t:Node {name: $ancestor})
        WHERE n.type <> "edge"
        RETURN n
        UNION
        MATCH (n:Node)<-[:FROM]-(:Node {type: "edge", relation: "IS_A"})-[:TO]->(m1:Node)
        MATCH (m1)<-[:FROM]-(:Node {type: "edge", relation: "IS_A"})-[:TO]->(t:Node {name: $ancestor})
        WHERE n.type <> "edge"
        RETURN n
        UNION
        MATCH (n:Node)<-[:FROM]-(:Node {type: "edge", relation: "IS_A"})-[:TO]->(m1:Node)
        MATCH (m1)<-[:FROM]-(:Node {type: "edge", relation: "IS_A"})-[:TO]->(m2:Node)
        MATCH (m2)<-[:FROM]-(:Node {type: "edge", relation: "IS_A"})-[:TO]->(t:Node {name: $ancestor})
        WHERE n.type <> "edge"
        RETURN n
        """

    # ========== State Queries ==========

    @staticmethod
    def find_state_by_uuid() -> str:
        """
        Find a state by its UUID.
        Matches nodes whose type is in the state hierarchy (state and its
        subtypes like imagined_state, proposed_imagined_state).

        Parameters:
        - uuid: State UUID (string format)

        Returns: State node properties
        """
        return """
        MATCH (s:Node {uuid: $uuid})
        WHERE s.type IN $state_types
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
        WHERE s.type = "state"
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
        WHERE s.type = "state"
        RETURN s
        ORDER BY s.timestamp DESC
        """

    # ========== Process Queries ==========

    @staticmethod
    def find_process_by_uuid() -> str:
        """
        Find a process by its UUID.
        Matches nodes whose type is in the process hierarchy (process and its
        subtypes like action, step, imagined_process, etc.).

        Parameters:
        - uuid: Process UUID (string format)

        Returns: Process node properties
        """
        return """
        MATCH (p:Node {uuid: $uuid})
        WHERE p.type IN $process_types
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
        WHERE p.type = "process"
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
        WHERE p.type = "process"
        RETURN p
        ORDER BY p.start_time DESC
        """

    # ========== Relationship Queries (reified edge traversal) ==========

    @staticmethod
    def get_node_type() -> str:
        """
        Get the type of a node via IS_A edge node traversal.

        Parameters:
        - uuid: Node UUID (string format)

        Returns: Type node that this node is an instance of
        """
        return """
        MATCH (n:Node {uuid: $uuid})<-[:FROM]-(e:Node {type: "edge", relation: "IS_A"})-[:TO]->(t:Node)
        RETURN t
        """

    @staticmethod
    def get_entity_type() -> str:
        """
        Get the concept type of an entity via IS_A edge node traversal.

        Parameters:
        - entity_uuid: Entity UUID (string format)

        Returns: Concept node (as 'c')
        """
        return """
        MATCH (e:Node {uuid: $entity_uuid})<-[:FROM]-(edge:Node {type: "edge", relation: "IS_A"})-[:TO]->(c:Node)
        RETURN c
        """

    @staticmethod
    def get_entity_parts() -> str:
        """
        Get all parts of an entity via PART_OF edge node traversal.
        Parts are nodes that have a PART_OF edge pointing TO this entity.

        Parameters:
        - entity_uuid: Entity UUID (string format)

        Returns: List of part Entity nodes
        """
        return """
        MATCH (part:Node)<-[:FROM]-(edge:Node {type: "edge", relation: "PART_OF"})-[:TO]->(e:Node {uuid: $entity_uuid})
        RETURN part
        """

    @staticmethod
    def get_entity_parent() -> str:
        """
        Get the parent entity via PART_OF edge node traversal.
        The parent is the target of the PART_OF edge from this entity.

        Parameters:
        - entity_uuid: Entity UUID (string format)

        Returns: Parent Entity node (as 'whole')
        """
        return """
        MATCH (e:Node {uuid: $entity_uuid})<-[:FROM]-(edge:Node {type: "edge", relation: "PART_OF"})-[:TO]->(whole:Node)
        RETURN whole
        """

    @staticmethod
    def get_entity_states() -> str:
        """
        Get all states of an entity via HAS_STATE edge node traversal.

        Parameters:
        - entity_uuid: Entity UUID (string format)

        Returns: List of State nodes ordered by timestamp
        """
        return """
        MATCH (e:Node {uuid: $entity_uuid})<-[:FROM]-(edge:Node {type: "edge", relation: "HAS_STATE"})-[:TO]->(s:Node)
        RETURN s
        ORDER BY s.timestamp DESC
        """

    @staticmethod
    def get_entity_current_state() -> str:
        """
        Get the most recent state of an entity via HAS_STATE edge node traversal.

        Parameters:
        - entity_uuid: Entity UUID (string format)

        Returns: Most recent State node
        """
        return """
        MATCH (e:Node {uuid: $entity_uuid})<-[:FROM]-(edge:Node {type: "edge", relation: "HAS_STATE"})-[:TO]->(s:Node)
        RETURN s
        ORDER BY s.timestamp DESC
        LIMIT 1
        """

    @staticmethod
    def get_process_preconditions() -> str:
        """
        Get states required by a process via REQUIRES edge node traversal.

        Parameters:
        - process_uuid: Process UUID (string format)

        Returns: List of State nodes that are preconditions
        """
        return """
        MATCH (p:Node {uuid: $process_uuid})<-[:FROM]-(edge:Node {type: "edge", relation: "REQUIRES"})-[:TO]->(s:Node)
        RETURN s
        """

    @staticmethod
    def get_process_effects() -> str:
        """
        Get states caused by a process via CAUSES edge node traversal.

        Parameters:
        - process_uuid: Process UUID (string format)

        Returns: List of State nodes that are effects
        """
        return """
        MATCH (p:Node {uuid: $process_uuid})<-[:FROM]-(edge:Node {type: "edge", relation: "CAUSES"})-[:TO]->(s:Node)
        RETURN s
        """

    # Aliases for backward compatibility with client.py
    @staticmethod
    def get_process_causes() -> str:
        """Alias for get_process_effects()."""
        return """
        MATCH (p:Node {uuid: $process_uuid})<-[:FROM]-(edge:Node {type: "edge", relation: "CAUSES"})-[:TO]->(s:Node)
        RETURN s
        """

    @staticmethod
    def get_process_requirements() -> str:
        """Alias for get_process_preconditions()."""
        return """
        MATCH (p:Node {uuid: $process_uuid})<-[:FROM]-(edge:Node {type: "edge", relation: "REQUIRES"})-[:TO]->(s:Node)
        RETURN s
        """

    @staticmethod
    def find_current_state_for_entity() -> str:
        """Alias for get_entity_current_state()."""
        return """
        MATCH (e:Node {uuid: $entity_uuid})<-[:FROM]-(edge:Node {type: "edge", relation: "HAS_STATE"})-[:TO]->(s:Node)
        RETURN s
        ORDER BY s.timestamp DESC
        LIMIT 1
        """

    # ========== Causality Traversal Queries ==========

    @staticmethod
    def traverse_causality_forward(max_depth: int = 10) -> str:
        """
        Traverse causality chain forward from a state via reified edge nodes.
        Finds processes that REQUIRE the given state and their CAUSES effects.

        Currently only single-hop traversal is implemented. Multi-hop
        traversal (max_depth > 1) is not yet supported.

        Parameters:
        - state_uuid: Starting State UUID
        - max_depth: Maximum traversal depth. Only ``1`` is currently
          supported; passing a value > 1 raises ``NotImplementedError``.

        Returns: Processes and resulting states with depth

        Raises:
            NotImplementedError: If *max_depth* > 1.
        """
        if max_depth > 1:
            raise NotImplementedError(
                f"Multi-hop causality traversal is not yet implemented (max_depth={max_depth}). "
                "Only single-step (max_depth=1) is supported."
            )
        # Single-step causality: state <-REQUIRES- process -CAUSES-> result
        # Each hop is through two edge nodes, so we do a single step for now.
        return """
        MATCH (start:Node {uuid: $state_uuid})
        MATCH (start)<-[:TO]-(req_edge:Node {type: "edge", relation: "REQUIRES"})-[:FROM]->(p:Node)
        MATCH (p)<-[:FROM]-(cause_edge:Node {type: "edge", relation: "CAUSES"})-[:TO]->(result:Node)
        RETURN p, result, 1 as depth
        ORDER BY depth
        """

    @staticmethod
    def traverse_causality_backward(max_depth: int = 10) -> str:
        """
        Traverse causality chain backward from a state via reified edge nodes.
        Finds processes that CAUSE the given state and their REQUIRES preconditions.

        Currently only single-hop traversal is implemented. Multi-hop
        traversal (max_depth > 1) is not yet supported.

        Parameters:
        - state_uuid: Target State UUID
        - max_depth: Maximum traversal depth. Only ``1`` is currently
          supported; passing a value > 1 raises ``NotImplementedError``.

        Returns: Causing states and processes with depth

        Raises:
            NotImplementedError: If *max_depth* > 1.
        """
        if max_depth > 1:
            raise NotImplementedError(
                f"Multi-hop causality traversal is not yet implemented (max_depth={max_depth}). "
                "Only single-step (max_depth=1) is supported."
            )
        return """
        MATCH (target:Node {uuid: $state_uuid})
        MATCH (target)<-[:TO]-(cause_edge:Node {type: "edge", relation: "CAUSES"})-[:FROM]->(p:Node)
        MATCH (p)<-[:FROM]-(req_edge:Node {type: "edge", relation: "REQUIRES"})-[:TO]->(cause:Node)
        RETURN cause, p, 1 as depth
        ORDER BY depth
        """

    # ========== Planning Queries ==========

    @staticmethod
    def find_processes_causing_state() -> str:
        """
        Find all processes that CAUSE a specific state via CAUSES edge nodes.

        Parameters:
        - state_uuid: Target State UUID

        Returns: List of Process nodes that cause this state
        """
        return """
        MATCH (p:Node)<-[:FROM]-(edge:Node {type: "edge", relation: "CAUSES"})-[:TO]->(s:Node {uuid: $state_uuid})
        WHERE p.type = "process"
        RETURN p
        """

    @staticmethod
    def find_processes_by_effect_properties() -> str:
        """
        Find processes that cause states matching property criteria via CAUSES edge nodes.

        Parameters:
        - property_key: Name of the state property to match
        - property_value: Value to match

        Returns: Process and State nodes
        """
        return """
        MATCH (p:Node)<-[:FROM]-(edge:Node {type: "edge", relation: "CAUSES"})-[:TO]->(s:Node)
        WHERE p.type = "process"
          AND s[$property_key] = $property_value
        RETURN p, s
        """

    @staticmethod
    def find_processes_for_entity_state() -> str:
        """
        Find processes that cause states for a specific entity via reified edges.

        Parameters:
        - entity_uuid: Entity UUID

        Returns: Process and State nodes
        """
        return """
        MATCH (e:Node {uuid: $entity_uuid})<-[:FROM]-(:Node {type: "edge", relation: "HAS_STATE"})-[:TO]->(s:Node)
        MATCH (p:Node)<-[:FROM]-(:Node {type: "edge", relation: "CAUSES"})-[:TO]->(s)
        WHERE p.type = "process"
        RETURN p, s
        """

    # ========== Capability Queries ==========

    @staticmethod
    def find_capability_by_uuid() -> str:
        """
        Find a capability by its UUID.

        Parameters:
        - uuid: Capability UUID

        Returns: Capability node (as 'c')
        """
        return """
        MATCH (c:Node {uuid: $uuid})
        WHERE c.type = "capability"
        RETURN c
        """

    @staticmethod
    def find_capability_for_process() -> str:
        """
        Find the capability that can execute a process via USES_CAPABILITY edge node.

        Parameters:
        - process_uuid: Process UUID

        Returns: Capability node
        """
        return """
        MATCH (p:Node {uuid: $process_uuid})
        OPTIONAL MATCH (p)<-[:FROM]-(edge:Node {type: "edge", relation: "USES_CAPABILITY"})-[:TO]->(capability:Node)
        RETURN capability
        """

    @staticmethod
    def check_state_satisfied() -> str:
        """
        Check if a state with given properties exists for an entity via HAS_STATE edge node.

        Parameters:
        - entity_uuid: Entity UUID
        - property_key: State property to check
        - property_value: Expected value

        Returns: Boolean 'satisfied' indicating if matching state exists
        """
        return """
        MATCH (e:Node {uuid: $entity_uuid})<-[:FROM]-(:Node {type: "edge", relation: "HAS_STATE"})-[:TO]->(s:Node)
        WHERE s[$property_key] = $property_value
        RETURN count(s) > 0 as satisfied
        """

    # ========== Create Queries ==========
    # Note: Type definitions and instances are now created via client.add_node()
    # and linked via client.add_edge(). The old create_type_definition(),
    # create_instance(), create_entity(), create_state(), create_process()
    # queries are kept for backward compatibility but no longer set
    # ancestors or is_type_definition properties.

    @staticmethod
    def create_type_definition() -> str:
        """
        Create a new type definition node.
        Type hierarchy is expressed via IS_A edge nodes, not stored properties.

        Parameters:
        - uuid: Node UUID
        - name: Type name
        - description: Optional description

        Returns: Created node
        """
        return """
        CREATE (t:Node {
            uuid: $uuid,
            name: $name,
            type: "type_definition",
            description: $description
        })
        RETURN t
        """

    @staticmethod
    def create_instance() -> str:
        """
        Create a new instance of a type.
        Type hierarchy is expressed via IS_A edge nodes, not stored properties.

        Parameters:
        - uuid: Node UUID
        - name: Instance name
        - type: Type name
        - description: Optional description

        Returns: Created node
        """
        return """
        CREATE (n:Node {
            uuid: $uuid,
            name: $name,
            type: $type,
            description: $description
        })
        RETURN n
        """

    @staticmethod
    def create_entity() -> str:
        """
        Create a new entity.

        Parameters:
        - uuid: Entity UUID
        - name: Entity name
        - type: Specific entity type (default "entity")
        - description: Optional description

        Returns: Created entity node
        """
        return """
        CREATE (e:Node {
            uuid: $uuid,
            name: $name,
            type: $type,
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
        - timestamp: Optional timestamp (defaults to now)

        Returns: Created state node
        """
        return """
        CREATE (s:Node {
            uuid: $uuid,
            name: $name,
            type: $type,
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
        - description: Optional description
        - duration_ms: Optional duration in milliseconds

        Returns: Created process node
        """
        return """
        CREATE (p:Node {
            uuid: $uuid,
            name: $name,
            type: $type,
            description: $description,
            start_time: datetime(),
            duration_ms: $duration_ms
        })
        RETURN p
        """

    @staticmethod
    def create_cwm_state() -> str:
        """
        Create a new CWM state entry.

        Parameters:
        - uuid: State UUID (state_id format: cwm_<type>_<uuid>)
        - name: State name (typically auto-generated)
        - type: CWM type ("cwm_a", "cwm_g", or "cwm_e")
        - timestamp: ISO timestamp
        - source: Origin subsystem (e.g., "planner", "jepa", "reflection")
        - confidence: Confidence score 0.0-1.0
        - status: Provenance status ("observed", "imagined", "reflected", "ephemeral")
        - payload: JSON string with type-specific data
        - links: JSON string with related entity references
        - tags: List of free-form labels for filtering
        - embedding_id: Optional reference to Milvus embedding
        - embedding_type: Optional embedding model type

        Returns: Created CWM state node
        """
        return """
        CREATE (s:Node {
            uuid: $uuid,
            name: $name,
            type: $type,
            timestamp: datetime($timestamp),
            source: $source,
            confidence: $confidence,
            status: $status,
            payload: $payload,
            links: $links,
            tags: $tags,
            embedding_id: $embedding_id,
            embedding_type: $embedding_type
        })
        RETURN s
        """

    @staticmethod
    def find_cwm_states() -> str:
        """
        Find CWM states with optional filters.

        Parameters:
        - types: List of CWM types to include (["cwm_a", "cwm_g", "cwm_e"])
        - after_timestamp: Optional ISO timestamp to filter after
        - limit: Max results to return

        Returns: List of CWM state nodes ordered by timestamp desc
        """
        return """
        MATCH (s:Node)
        WHERE s.type IN $types
          AND ($after_timestamp IS NULL OR s.timestamp > datetime($after_timestamp))
        RETURN s
        ORDER BY s.timestamp DESC
        LIMIT $limit
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
        Count type definitions (nodes with type="type_definition") vs other nodes.

        Returns: Counts by type category
        """
        return """
        MATCH (n:Node)
        RETURN CASE WHEN n.type = "type_definition" THEN true ELSE false END as is_type_def,
               count(n) as count
        """
