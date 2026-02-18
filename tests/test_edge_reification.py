"""Integration tests for reified edge creation. Requires Neo4j."""
import inspect

import pytest

from logos_hcg.client import HCGClient


@pytest.fixture
def client():
    c = HCGClient(uri="bolt://localhost:7687", user="neo4j", password="logosdev")
    yield c
    c.clear_all()
    c.close()


class TestAddEdge:

    def test_creates_edge_node(self, client):
        src = client.add_node(name="Paris", node_type="entity")
        tgt = client.add_node(name="France", node_type="entity")
        edge_id = client.add_edge(
            source_uuid=src, target_uuid=tgt, relation="LOCATED_IN",
        )
        assert edge_id
        # Verify edge node exists
        result = client._execute_read(
            "MATCH (e:Node {uuid: $uuid}) RETURN e", {"uuid": edge_id},
        )
        assert len(result) == 1
        edge_props = dict(result[0]["e"])
        assert edge_props["relation"] == "LOCATED_IN"
        assert edge_props["source"] == src
        assert edge_props["target"] == tgt
        assert edge_props["bidirectional"] is False

    def test_creates_from_to_structural_rels(self, client):
        src = client.add_node(name="A", node_type="entity")
        tgt = client.add_node(name="B", node_type="entity")
        edge_id = client.add_edge(
            source_uuid=src, target_uuid=tgt, relation="CAUSES",
        )
        result = client._execute_read(
            """
            MATCH (source:Node)<-[:FROM]-(edge:Node {uuid: $edge_uuid})-[:TO]->(target:Node)
            RETURN source.uuid AS src, target.uuid AS tgt
            """,
            {"edge_uuid": edge_id},
        )
        assert len(result) == 1
        assert result[0]["src"] == src
        assert result[0]["tgt"] == tgt

    def test_edge_with_properties(self, client):
        src = client.add_node(name="A", node_type="entity")
        tgt = client.add_node(name="B", node_type="entity")
        edge_id = client.add_edge(
            source_uuid=src, target_uuid=tgt, relation="REQUIRES",
            properties={"confidence": 0.85},
        )
        result = client._execute_read(
            "MATCH (e:Node {uuid: $uuid}) RETURN e.confidence AS conf",
            {"uuid": edge_id},
        )
        assert result[0]["conf"] == 0.85

    def test_bidirectional_flag(self, client):
        src = client.add_node(name="A", node_type="entity")
        tgt = client.add_node(name="B", node_type="entity")
        edge_id = client.add_edge(
            source_uuid=src, target_uuid=tgt, relation="RELATED_TO",
            bidirectional=True,
        )
        result = client._execute_read(
            "MATCH (e:Node {uuid: $uuid}) RETURN e.bidirectional AS bidir",
            {"uuid": edge_id},
        )
        assert result[0]["bidir"] is True

    def test_add_edge_idempotent(self, client):
        """Same source+target+relation should not create duplicate edge nodes."""
        src = client.add_node(name="Paris", node_type="entity")
        tgt = client.add_node(name="France", node_type="entity")
        edge1 = client.add_edge(
            source_uuid=src, target_uuid=tgt, relation="LOCATED_IN",
        )
        edge2 = client.add_edge(
            source_uuid=src, target_uuid=tgt, relation="LOCATED_IN",
        )
        assert edge1 == edge2  # same edge node returned
        # Verify only one edge node exists
        result = client._execute_read(
            """MATCH (e:Node {source: $src, target: $tgt, relation: "LOCATED_IN"})
            RETURN count(e) AS count""",
            {"src": src, "tgt": tgt},
        )
        assert result[0]["count"] == 1

    def test_edge_name_is_descriptive(self, client):
        """Edge name should include source and target node names."""
        src = client.add_node(name="Paris", node_type="entity")
        tgt = client.add_node(name="France", node_type="entity")
        edge_id = client.add_edge(
            source_uuid=src, target_uuid=tgt, relation="LOCATED_IN",
        )
        result = client._execute_read(
            "MATCH (e:Node {uuid: $uuid}) RETURN e.name AS name",
            {"uuid": edge_id},
        )
        assert result[0]["name"] == "Paris_LOCATED_IN_France"

    def test_no_native_relationships_created(self, client):
        """add_edge() must NOT create native Neo4j relationships other than :FROM/:TO."""
        src = client.add_node(name="A", node_type="entity")
        tgt = client.add_node(name="B", node_type="entity")
        client.add_edge(
            source_uuid=src, target_uuid=tgt, relation="CAUSES",
        )
        # Check no native CAUSES relationship exists
        result = client._execute_read(
            "MATCH (a:Node {uuid: $src})-[r:CAUSES]->(b:Node {uuid: $tgt}) RETURN r",
            {"src": src, "tgt": tgt},
        )
        assert len(result) == 0


class TestAddNodeClean:

    def test_add_node_no_ancestors_param(self, client):
        """add_node() should not accept 'ancestors' — hierarchy is via IS_A edges."""
        sig = inspect.signature(client.add_node)
        assert "ancestors" not in sig.parameters

    def test_add_node_no_is_type_definition_param(self, client):
        """add_node() should not accept 'is_type_definition' — structure, not flags."""
        sig = inspect.signature(client.add_node)
        assert "is_type_definition" not in sig.parameters

    def test_add_node_basic(self, client):
        uuid = client.add_node(name="Paris", node_type="location")
        assert uuid
        result = client._execute_read(
            "MATCH (n:Node {uuid: $uuid}) RETURN n", {"uuid": uuid},
        )
        assert len(result) == 1
        node = dict(result[0]["n"])
        assert node["name"] == "Paris"
        assert node["type"] == "location"
        assert "ancestors" not in node
        assert "is_type_definition" not in node
