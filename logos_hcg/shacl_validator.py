"""SHACL validator for HCG graph mutations.

Provides validation of graph nodes and edges against SHACL shapes
to ensure data integrity and constraint enforcement.

Based on sophia/src/sophia/hcg_client/shacl_validator.py
"""

import logging
from typing import Any

from pyshacl import validate
from rdflib import Graph, Literal, Namespace
from rdflib.namespace import RDF, RDFS, SH

logger = logging.getLogger(__name__)


class HCGValidationError(Exception):
    """Raised when SHACL validation fails."""

    def __init__(self, message: str, errors: list[str] | None = None) -> None:
        super().__init__(message)
        self.errors = errors or []


class SHACLValidator:
    """SHACL validator for knowledge graph mutations.

    Enforces constraints on graph mutations using SHACL shapes.
    Supports both default HCG shapes and custom shapes.

    Example:
        validator = SHACLValidator()
        is_valid, errors = validator.validate_node({"id": "n1", "type": "Entity"})

        # With custom shapes
        custom_shapes = '''
        @prefix sh: <http://www.w3.org/ns/shacl#> .
        # ... custom shapes ...
        '''
        validator = SHACLValidator(shapes_graph=custom_shapes)
    """

    def __init__(self, shapes_graph: str | None = None) -> None:
        """Initialize SHACL validator.

        Args:
            shapes_graph: Optional SHACL shapes graph in Turtle format.
                        If None, uses default HCG shapes.
        """
        if shapes_graph:
            self._shapes = Graph()
            self._shapes.parse(data=shapes_graph, format="turtle")
        else:
            self._shapes = self._create_default_shapes()

    def _create_default_shapes(self) -> Graph:
        """Create default SHACL shapes for HCG validation.

        Returns:
            RDF graph with default SHACL shapes
        """
        g = Graph()
        ex = Namespace("http://example.org/hcg/")

        # Node shape: All nodes must have id and type
        node_shape = ex.NodeShape
        g.add((node_shape, RDF.type, SH.NodeShape))
        g.add((node_shape, SH.targetClass, ex.Node))

        # ID property shape
        g.add((node_shape, SH.property, ex.NodeIdProperty))
        id_prop = ex.NodeIdProperty
        g.add((id_prop, RDF.type, SH.PropertyShape))
        g.add((id_prop, SH.path, ex.entityId))
        g.add((id_prop, SH.minCount, Literal(1)))
        g.add((id_prop, SH.maxCount, Literal(1)))
        g.add((id_prop, SH.datatype, RDFS.Literal))

        # Type property shape
        g.add((node_shape, SH.property, ex.NodeTypeProperty))
        type_prop = ex.NodeTypeProperty
        g.add((type_prop, RDF.type, SH.PropertyShape))
        g.add((type_prop, SH.path, ex.nodeType))
        g.add((type_prop, SH.minCount, Literal(1)))
        g.add((type_prop, SH.maxCount, Literal(1)))
        g.add((type_prop, SH.datatype, RDFS.Literal))

        # Edge shape: All edges must have source, target, and relation
        edge_shape = ex.EdgeShape
        g.add((edge_shape, RDF.type, SH.NodeShape))
        g.add((edge_shape, SH.targetClass, ex.Edge))

        # Source property
        g.add((edge_shape, SH.property, ex.EdgeSourceProperty))
        source_prop = ex.EdgeSourceProperty
        g.add((source_prop, RDF.type, SH.PropertyShape))
        g.add((source_prop, SH.path, ex.source))
        g.add((source_prop, SH.minCount, Literal(1)))
        g.add((source_prop, SH.maxCount, Literal(1)))

        # Target property
        g.add((edge_shape, SH.property, ex.EdgeTargetProperty))
        target_prop = ex.EdgeTargetProperty
        g.add((target_prop, RDF.type, SH.PropertyShape))
        g.add((target_prop, SH.path, ex.target))
        g.add((target_prop, SH.minCount, Literal(1)))
        g.add((target_prop, SH.maxCount, Literal(1)))

        # Relation property
        g.add((edge_shape, SH.property, ex.EdgeRelationProperty))
        relation_prop = ex.EdgeRelationProperty
        g.add((relation_prop, RDF.type, SH.PropertyShape))
        g.add((relation_prop, SH.path, ex.relation))
        g.add((relation_prop, SH.minCount, Literal(1)))
        g.add((relation_prop, SH.maxCount, Literal(1)))

        # Hermes Proposal shape: Must have required provenance fields
        proposal_shape = ex.HermesProposalShape
        g.add((proposal_shape, RDF.type, SH.NodeShape))
        g.add((proposal_shape, SH.targetClass, ex.HermesProposal))

        # Source service property
        g.add((proposal_shape, SH.property, ex.ProposalSourceProperty))
        source_service_prop = ex.ProposalSourceProperty
        g.add((source_service_prop, RDF.type, SH.PropertyShape))
        g.add((source_service_prop, SH.path, ex.source_service))
        g.add((source_service_prop, SH.minCount, Literal(1)))
        g.add((source_service_prop, SH.datatype, RDFS.Literal))

        # LLM provider property
        g.add((proposal_shape, SH.property, ex.ProposalLLMProviderProperty))
        llm_provider_prop = ex.ProposalLLMProviderProperty
        g.add((llm_provider_prop, RDF.type, SH.PropertyShape))
        g.add((llm_provider_prop, SH.path, ex.llm_provider))
        g.add((llm_provider_prop, SH.minCount, Literal(1)))
        g.add((llm_provider_prop, SH.datatype, RDFS.Literal))

        # Model property
        g.add((proposal_shape, SH.property, ex.ProposalModelProperty))
        model_prop = ex.ProposalModelProperty
        g.add((model_prop, RDF.type, SH.PropertyShape))
        g.add((model_prop, SH.path, ex.model))
        g.add((model_prop, SH.minCount, Literal(1)))
        g.add((model_prop, SH.datatype, RDFS.Literal))

        # Generated timestamp property
        g.add((proposal_shape, SH.property, ex.ProposalGeneratedAtProperty))
        generated_at_prop = ex.ProposalGeneratedAtProperty
        g.add((generated_at_prop, RDF.type, SH.PropertyShape))
        g.add((generated_at_prop, SH.path, ex.generated_at))
        g.add((generated_at_prop, SH.minCount, Literal(1)))
        g.add((generated_at_prop, SH.datatype, RDFS.Literal))

        # Confidence property (0.0 to 1.0)
        g.add((proposal_shape, SH.property, ex.ProposalConfidenceProperty))
        confidence_prop = ex.ProposalConfidenceProperty
        g.add((confidence_prop, RDF.type, SH.PropertyShape))
        g.add((confidence_prop, SH.path, ex.confidence))
        g.add((confidence_prop, SH.minCount, Literal(1)))
        g.add((confidence_prop, SH.datatype, RDFS.Literal))
        g.add((confidence_prop, SH.minInclusive, Literal(0.0)))
        g.add((confidence_prop, SH.maxInclusive, Literal(1.0)))

        # Proposed Plan Step shape
        plan_step_shape = ex.ProposedPlanStepShape
        g.add((plan_step_shape, RDF.type, SH.NodeShape))
        g.add((plan_step_shape, SH.targetClass, ex.ProposedPlanStep))
        g.add((plan_step_shape, SH.property, ex.PlanStepSourceProperty))

        step_source_prop = ex.PlanStepSourceProperty
        g.add((step_source_prop, RDF.type, SH.PropertyShape))
        g.add((step_source_prop, SH.path, ex.source_proposal))
        g.add((step_source_prop, SH.minCount, Literal(1)))

        # Proposed Imagined State shape
        imagined_state_shape = ex.ProposedImaginedStateShape
        g.add((imagined_state_shape, RDF.type, SH.NodeShape))
        g.add((imagined_state_shape, SH.targetClass, ex.ProposedImaginedState))
        g.add((imagined_state_shape, SH.property, ex.ImaginedStateSourceProperty))

        state_source_prop = ex.ImaginedStateSourceProperty
        g.add((state_source_prop, RDF.type, SH.PropertyShape))
        g.add((state_source_prop, SH.path, ex.source_proposal))
        g.add((state_source_prop, SH.minCount, Literal(1)))

        # Proposed Tool Call shape
        tool_call_shape = ex.ProposedToolCallShape
        g.add((tool_call_shape, RDF.type, SH.NodeShape))
        g.add((tool_call_shape, SH.targetClass, ex.ProposedToolCall))
        g.add((tool_call_shape, SH.property, ex.ToolCallSourceProperty))

        tool_source_prop = ex.ToolCallSourceProperty
        g.add((tool_source_prop, RDF.type, SH.PropertyShape))
        g.add((tool_source_prop, SH.path, ex.source_proposal))
        g.add((tool_source_prop, SH.minCount, Literal(1)))

        return g

    def validate_node(self, node_data: dict[str, Any]) -> tuple[bool, list[str]]:
        """Validate a node against SHACL shapes.

        Performs basic validation (required fields) first, then runs
        SHACL validation if basic checks pass.

        Args:
            node_data: Node data with 'id', 'type', and optional 'properties'

        Returns:
            Tuple of (is_valid, list of error messages)
        """
        errors: list[str] = []

        # Basic validation - required fields
        if "id" not in node_data:
            errors.append("Node must have an 'id' field")
        if "type" not in node_data:
            errors.append("Node must have a 'type' field")

        if errors:
            return False, errors

        # Build RDF graph for SHACL validation
        data_graph = self._node_to_graph(node_data)

        try:
            conforms, _, results_text = validate(
                data_graph,
                shacl_graph=self._shapes,
                inference="none",
            )

            if not conforms:
                errors.extend(self._extract_validation_errors(results_text))
                return False, errors

            return True, []

        except Exception as e:  # noqa: BLE001 - fail open if SHACL validation errors
            logger.warning(f"SHACL validation error: {e}")
            # Fail open - allow if validation itself fails
            return True, []

    def validate_edge(self, edge_data: dict[str, Any]) -> tuple[bool, list[str]]:
        """Validate an edge against SHACL shapes.

        Performs basic validation (required fields) first, then runs
        SHACL validation if basic checks pass.

        Args:
            edge_data: Edge data with 'id', 'source', 'target', 'relation',
                      and optional 'properties'

        Returns:
            Tuple of (is_valid, list of error messages)
        """
        errors: list[str] = []

        # Basic validation - required fields
        required_fields = ["id", "source", "target", "relation"]
        for field in required_fields:
            if field not in edge_data:
                errors.append(f"Edge must have a '{field}' field")

        if errors:
            return False, errors

        # Build RDF graph for SHACL validation
        data_graph = self._edge_to_graph(edge_data)

        try:
            conforms, _, results_text = validate(
                data_graph,
                shacl_graph=self._shapes,
                inference="none",
            )

            if not conforms:
                errors.extend(self._extract_validation_errors(results_text))
                return False, errors

            return True, []

        except Exception as e:  # noqa: BLE001 - fail open if SHACL validation errors
            logger.warning(f"SHACL validation error: {e}")
            # Fail open - allow if validation itself fails
            return True, []

    def validate_mutation(self, mutation_type: str, data: dict[str, Any]) -> tuple[bool, list[str]]:
        """Validate a graph mutation (node or edge operation).

        Args:
            mutation_type: Type of mutation ('add_node', 'add_edge', 'update_node', etc.)
            data: Data for the mutation

        Returns:
            Tuple of (is_valid, list of error messages)
        """
        if mutation_type in ["add_node", "update_node"]:
            return self.validate_node(data)
        elif mutation_type in ["add_edge", "update_edge"]:
            return self.validate_edge(data)
        else:
            return False, [f"Unknown mutation type: {mutation_type}"]

    def _node_to_graph(self, node_data: dict[str, Any]) -> Graph:
        """Convert node data to RDF graph for validation.

        Args:
            node_data: Node data dictionary

        Returns:
            RDF graph representation
        """
        g = Graph()
        ex = Namespace("http://example.org/hcg/")

        node_id = node_data.get("id", "unknown")
        node_uri = ex[f"node_{node_id}"]

        g.add((node_uri, RDF.type, ex.Node))
        g.add((node_uri, ex.entityId, Literal(node_id)))

        if "type" in node_data:
            node_type = node_data["type"]
            g.add((node_uri, ex.nodeType, Literal(node_type)))

            # Add specific type class for SHACL validation
            type_class_map = {
                "hermes_proposal": ex.HermesProposal,
                "proposed_plan_step": ex.ProposedPlanStep,
                "proposed_imagined_state": ex.ProposedImaginedState,
                "proposed_tool_call": ex.ProposedToolCall,
            }
            if node_type in type_class_map:
                g.add((node_uri, RDF.type, type_class_map[node_type]))

        # Add properties
        properties = node_data.get("properties", {})
        for key, value in properties.items():
            g.add((node_uri, ex[key], Literal(str(value))))

        return g

    def _edge_to_graph(self, edge_data: dict[str, Any]) -> Graph:
        """Convert edge data to RDF graph for validation.

        Args:
            edge_data: Edge data dictionary

        Returns:
            RDF graph representation
        """
        g = Graph()
        ex = Namespace("http://example.org/hcg/")

        edge_id = edge_data.get("id", "unknown")
        edge_uri = ex[f"edge_{edge_id}"]

        g.add((edge_uri, RDF.type, ex.Edge))

        if "source" in edge_data:
            g.add((edge_uri, ex.source, Literal(edge_data["source"])))

        if "target" in edge_data:
            g.add((edge_uri, ex.target, Literal(edge_data["target"])))

        if "relation" in edge_data:
            g.add((edge_uri, ex.relation, Literal(edge_data["relation"])))

        # Add properties
        properties = edge_data.get("properties", {})
        for key, value in properties.items():
            g.add((edge_uri, ex[key], Literal(str(value))))

        return g

    def _extract_validation_errors(self, results_text: str) -> list[str]:
        """Extract error messages from SHACL validation results.

        Args:
            results_text: SHACL validation results text

        Returns:
            List of error messages
        """
        errors = []
        if results_text:
            lines = results_text.split("\n")
            for line in lines:
                if "Validation Result" in line or "Message:" in line:
                    errors.append(line.strip())

        if not errors:
            errors.append("Validation failed but no specific errors found")

        return errors

    def load_shapes_from_file(self, path: str) -> None:
        """Load SHACL shapes from a file.

        Args:
            path: Path to SHACL shapes file (Turtle format)
        """
        self._shapes = Graph()
        self._shapes.parse(path, format="turtle")
        logger.info(f"Loaded SHACL shapes from {path}")
