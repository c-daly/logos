"""Tests for seeder with reified IS_A edges. Requires Neo4j."""

import pytest

from logos_hcg.client import HCGClient
from logos_hcg.seeder import HCGSeeder
from logos_test_utils.neo4j import get_neo4j_config, is_neo4j_available

_neo4j_cfg = get_neo4j_config()
pytestmark = pytest.mark.skipif(
    not is_neo4j_available(_neo4j_cfg), reason="Neo4j not available"
)


@pytest.fixture
def client():
    c = HCGClient(
        uri=_neo4j_cfg.uri, user=_neo4j_cfg.user, password=_neo4j_cfg.password
    )
    c.clear_all()
    yield c
    c.clear_all()
    c.close()


def test_seed_creates_is_a_edge_nodes(client):
    """Type hierarchy should use IS_A edge nodes, not native relationships."""
    seeder = HCGSeeder(client)
    seeder.seed_type_definitions()

    # entity IS_A node (a kind under node)
    result = client._execute_read(
        """
        MATCH (child:Node {name: "entity"})<-[:FROM]-(e:Node {relation: "IS_A"})-[:TO]->(parent:Node {name: "node"})
        RETURN e.uuid AS edge_uuid
    """,
        {},
    )
    assert len(result) > 0

    # node IS_A root (node sits directly beneath the parentless terminus)
    result = client._execute_read(
        """
        MATCH (child:Node {name: "node"})<-[:FROM]-(e:Node {relation: "IS_A"})-[:TO]->(parent:Node {name: "root"})
        RETURN e.uuid AS edge_uuid
    """,
        {},
    )
    assert len(result) > 0


def test_seed_creates_exactly_the_six_node_skeleton(client):
    """Seeding an empty store yields exactly the sixteen-node skeleton."""
    seeder = HCGSeeder(client)
    count = seeder.seed_type_definitions()

    assert count == 16

    names = client._execute_read(
        """
        MATCH (n:Node {type: "type_definition"})
        RETURN n.name AS name
    """,
        {},
    )
    assert {row["name"] for row in names} == {
        "root",
        "node",
        "entity",
        "concept",
        "process",
        "_cognition",
        "_reserved_node",
        "_reserved_agent",
        "_reserved_process",
        "_reserved_action",
        "_reserved_goal",
        "_reserved_plan",
        "_reserved_simulation",
        "_reserved_execution",
        "_reserved_state",
        "_reserved_media_sample",
    }

    # root is the parentless terminus: it is never the child of an IS_A edge.
    root_parent = client._execute_read(
        """
        MATCH (root:Node {name: "root"})<-[:FROM]-(e:Node {relation: "IS_A"})
        RETURN count(e) AS count
    """,
        {},
    )
    assert root_parent[0]["count"] == 0

    # Exactly fifteen reified IS_A assertions wire the skeleton together.
    edges = client._execute_read(
        """
        MATCH (e:Node {relation: "IS_A"})
        RETURN count(e) AS count
    """,
        {},
    )
    assert edges[0]["count"] == 15

    # No seeded uuid may match the retired type_ slug pattern.
    slugs = client._execute_read(
        """
        MATCH (n:Node {type: "type_definition"})
        WHERE n.uuid STARTS WITH "type_"
        RETURN count(n) AS count
    """,
        {},
    )
    assert slugs[0]["count"] == 0


def test_seed_no_native_is_a_relationships(client):
    """No native [:IS_A] relationships should exist after seeding."""
    seeder = HCGSeeder(client)
    seeder.seed_type_definitions()

    result = client._execute_read("MATCH ()-[r:IS_A]->() RETURN count(r) AS count", {})
    assert result[0]["count"] == 0


def test_seed_no_ancestors_property(client):
    """Nodes should not have an 'ancestors' property after seeding."""
    seeder = HCGSeeder(client)
    seeder.seed_type_definitions()

    result = client._execute_read(
        """
        MATCH (n:Node)
        WHERE n.ancestors IS NOT NULL
        RETURN count(n) AS count
    """,
        {},
    )
    assert result[0]["count"] == 0


def test_seed_demo_uses_add_edge(client):
    """Demo scenario edges should be reified edge nodes."""
    seeder = HCGSeeder(client)
    seeder.seed_type_definitions()
    seeder.seed_demo_scenario()

    # Check that a PART_OF relationship is an edge node
    result = client._execute_read(
        """
        MATCH (child:Node)<-[:FROM]-(e:Node {relation: "PART_OF"})-[:TO]->(parent:Node)
        RETURN count(e) AS count
    """,
        {},
    )
    assert result[0]["count"] > 0
