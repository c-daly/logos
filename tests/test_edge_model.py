"""Tests for the reified Edge model."""
from logos_hcg.edge import Edge


def test_edge_default_fields():
    edge = Edge(source="node-1", target="node-2", relation="IS_A")
    assert edge.id  # auto-generated UUID
    assert edge.source == "node-1"
    assert edge.target == "node-2"
    assert edge.relation == "IS_A"
    assert edge.bidirectional is False
    assert edge.properties == {}


def test_edge_with_all_fields():
    edge = Edge(
        id="edge-1",
        source="node-1",
        target="node-2",
        relation="CAUSES",
        bidirectional=False,
        properties={"confidence": 0.9, "source": "hermes"},
    )
    assert edge.id == "edge-1"
    assert edge.properties["confidence"] == 0.9


def test_edge_hashable():
    e = Edge(source="a", target="b", relation="X")
    s = {e}
    assert e in s
    assert hash(e) == hash(e.id)


def test_edge_equality_by_id():
    e1 = Edge(id="e1", source="a", target="b", relation="X")
    e2 = Edge(id="e1", source="c", target="d", relation="Y")
    assert e1 == e2
