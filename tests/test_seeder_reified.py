"""Tests for seeder with reified IS_A edges. Requires Neo4j."""
import pytest

from logos_hcg.client import HCGClient
from logos_hcg.seeder import HCGSeeder


@pytest.fixture
def client():
    c = HCGClient(uri="bolt://localhost:7687", user="neo4j", password="logosdev")
    c.clear_all()
    yield c
    c.clear_all()
    c.close()


def test_seed_creates_is_a_edge_nodes(client):
    """Type hierarchy should use IS_A edge nodes, not native relationships."""
    seeder = HCGSeeder(client)
    seeder.seed_type_definitions()

    # Verify IS_A edge node exists between entity and thing
    result = client._execute_read("""
        MATCH (child:Node {name: "entity"})<-[:FROM]-(e:Node {relation: "IS_A"})-[:TO]->(parent:Node {name: "thing"})
        RETURN e.uuid AS edge_uuid
    """, {})
    assert len(result) > 0


def test_seed_no_native_is_a_relationships(client):
    """No native [:IS_A] relationships should exist after seeding."""
    seeder = HCGSeeder(client)
    seeder.seed_type_definitions()

    result = client._execute_read(
        "MATCH ()-[r:IS_A]->() RETURN count(r) AS count", {}
    )
    assert result[0]["count"] == 0


def test_seed_no_ancestors_property(client):
    """Nodes should not have an 'ancestors' property after seeding."""
    seeder = HCGSeeder(client)
    seeder.seed_type_definitions()

    result = client._execute_read("""
        MATCH (n:Node)
        WHERE n.ancestors IS NOT NULL
        RETURN count(n) AS count
    """, {})
    assert result[0]["count"] == 0


def test_seed_demo_uses_add_edge(client):
    """Demo scenario edges should be reified edge nodes."""
    seeder = HCGSeeder(client)
    seeder.seed_type_definitions()
    seeder.seed_demo_scenario()

    # Check that a PART_OF relationship is an edge node
    result = client._execute_read("""
        MATCH (child:Node)<-[:FROM]-(e:Node {relation: "PART_OF"})-[:TO]->(parent:Node)
        RETURN count(e) AS count
    """, {})
    assert result[0]["count"] > 0
