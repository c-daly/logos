"""
SHACL validation using pyshacl (connectionless).

These tests validate the ontology shapes against known-valid and known-invalid
fixtures without requiring Neo4j or n10s. They serve as a fast sanity check
for shape correctness and fixture coverage in CI.
"""

from pathlib import Path

import pytest
from pyshacl import validate
from rdflib import Graph


def _load_graph(path: Path) -> Graph:
    g = Graph()
    g.parse(path, format="turtle")
    return g


@pytest.fixture(scope="module")
def shapes_graph() -> Graph:
    shapes_path = Path(__file__).parent.parent.parent / "ontology" / "shacl_shapes.ttl"
    return _load_graph(shapes_path)


def _assert_validation(data_graph: Graph, shapes_graph: Graph, expect_conforms: bool) -> None:
    conforms, report, _ = validate(
        data_graph=data_graph,
        shacl_graph=shapes_graph,
        inference="rdfs",
        abort_on_first=False,
    )
    if expect_conforms:
        assert conforms, f"Expected conforming data, but got violations:\n{report}"
    else:
        assert not conforms, "Expected validation failures, but data conformed"


def test_valid_entities_conform(shapes_graph: Graph) -> None:
    data = _load_graph(Path(__file__).parent / "fixtures" / "valid_entities.ttl")
    _assert_validation(data, shapes_graph, expect_conforms=True)


def test_invalid_entities_fail(shapes_graph: Graph) -> None:
    data = _load_graph(Path(__file__).parent / "fixtures" / "invalid_entities.ttl")
    _assert_validation(data, shapes_graph, expect_conforms=False)


def test_bad_uuid_prefix_fails(shapes_graph: Graph) -> None:
    ttl = """
        @prefix logos: <http://logos.ontology/> .

        logos:entity-bad-prefix a logos:Entity ;
            logos:uuid "wrong-prefix-123" ;
            logos:name "BadEntity" .
    """
    g = Graph()
    g.parse(data=ttl, format="turtle")
    _assert_validation(g, shapes_graph, expect_conforms=False)


def test_missing_required_property_fails(shapes_graph: Graph) -> None:
    ttl = """
        @prefix logos: <http://logos.ontology/> .

        logos:concept-no-name a logos:Concept ;
            logos:uuid "concept-missing-name" .
    """
    g = Graph()
    g.parse(data=ttl, format="turtle")
    _assert_validation(g, shapes_graph, expect_conforms=False)


def test_missing_uuid_fails(shapes_graph: Graph) -> None:
    ttl = """
        @prefix logos: <http://logos.ontology/> .

        logos:entity-no-uuid a logos:Entity ;
            logos:name "EntityWithoutUUID" .
    """
    g = Graph()
    g.parse(data=ttl, format="turtle")
    _assert_validation(g, shapes_graph, expect_conforms=False)
