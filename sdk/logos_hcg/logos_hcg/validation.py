"""SHACL validator for HCG graph mutations."""

import logging
from typing import Any

from pyshacl import validate
from rdflib import Graph, Literal, Namespace
from rdflib.namespace import RDF, RDFS, SH

logger = logging.getLogger(__name__)


class SHACLValidator:
    """SHACL validator for knowledge graph mutations.

    Enforces constraints on graph mutations using SHACL shapes.
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

        # Node shape: All nodes must have a type
        node_shape = ex.NodeShape
        g.add((node_shape, RDF.type, SH.NodeShape))
        g.add((node_shape, SH.targetClass, ex.Node))
        g.add((node_shape, SH.property, ex.NodeTypeProperty))

        # Type property shape
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

        # Entity shape: Must have ID
        entity_shape = ex.EntityShape
        g.add((entity_shape, RDF.type, SH.NodeShape))
        g.add((entity_shape, SH.targetClass, ex.Entity))
        g.add((entity_shape, SH.property, ex.EntityIdProperty))

        id_prop = ex.EntityIdProperty
        g.add((id_prop, RDF.type, SH.PropertyShape))
        g.add((id_prop, SH.path, ex.entityId))
        g.add((id_prop, SH.minCount, Literal(1)))
        g.add((id_prop, SH.maxCount, Literal(1)))
        g.add((id_prop, SH.datatype, RDFS.Literal))

        return g

    def validate_node(self, node_data: dict[str, Any]) -> tuple[bool, list[str]]:
        """Validate a node against SHACL shapes.

        Args:
            node_data: Node data with 'id', 'type', and optional 'properties'

        Returns:
            Tuple of (is_valid, error_messages)
        """
        errors: list[str] = []

        # Basic validation
        if "id" not in node_data:
            errors.append("Node must have an 'id' field")
        if "type" not in node_data:
            errors.append("Node must have a 'type' field")

        if errors:
            return False, errors

        # Build data graph for SHACL validation
        data_graph = Graph()
        ex = Namespace("http://example.org/hcg/")

        node_uri = ex[f"node_{node_data['id']}"]
        data_graph.add((node_uri, RDF.type, ex.Node))
        data_graph.add((node_uri, ex.nodeType, Literal(node_data["type"])))
        data_graph.add((node_uri, ex.entityId, Literal(node_data["id"])))

        # Run SHACL validation
        try:
            conforms, _, results_text = validate(
                data_graph,
                shacl_graph=self._shapes,
                inference="none",
            )

            if not conforms:
                errors.append(f"SHACL validation failed: {results_text}")

            return conforms, errors

        except Exception as e:  # noqa: BLE001 - fail open if SHACL validation errors
            logger.warning(f"SHACL validation error: {e}")
            # Fail open - allow if validation itself fails
            return True, []

    def validate_edge(self, edge_data: dict[str, Any]) -> tuple[bool, list[str]]:
        """Validate an edge against SHACL shapes.

        Args:
            edge_data: Edge data with 'id', 'source', 'target', 'relation',
                      and optional 'properties'

        Returns:
            Tuple of (is_valid, error_messages)
        """
        errors: list[str] = []

        # Basic validation
        required_fields = ["id", "source", "target", "relation"]
        for field in required_fields:
            if field not in edge_data:
                errors.append(f"Edge must have a '{field}' field")

        if errors:
            return False, errors

        # Build data graph for SHACL validation
        data_graph = Graph()
        ex = Namespace("http://example.org/hcg/")

        edge_uri = ex[f"edge_{edge_data['id']}"]
        data_graph.add((edge_uri, RDF.type, ex.Edge))
        data_graph.add((edge_uri, ex.source, Literal(edge_data["source"])))
        data_graph.add((edge_uri, ex.target, Literal(edge_data["target"])))
        data_graph.add((edge_uri, ex.relation, Literal(edge_data["relation"])))

        # Run SHACL validation
        try:
            conforms, _, results_text = validate(
                data_graph,
                shacl_graph=self._shapes,
                inference="none",
            )

            if not conforms:
                errors.append(f"SHACL validation failed: {results_text}")

            return conforms, errors

        except Exception as e:  # noqa: BLE001 - fail open if SHACL validation errors
            logger.warning(f"SHACL validation error: {e}")
            # Fail open - allow if validation itself fails
            return True, []

    def load_shapes_from_file(self, path: str) -> None:
        """Load SHACL shapes from a file.

        Args:
            path: Path to SHACL shapes file (Turtle format)
        """
        self._shapes = Graph()
        self._shapes.parse(path, format="turtle")
        logger.info(f"Loaded SHACL shapes from {path}")
