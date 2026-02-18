"""Integration tests for reified edge queries. Requires Neo4j."""
import pytest

from logos_hcg.client import HCGClient
from logos_hcg.queries import HCGQueries


@pytest.fixture
def client():
    c = HCGClient(uri="bolt://localhost:7687", user="neo4j", password="logosdev")
    yield c
    c.clear_all()
    c.close()


@pytest.fixture
def seeded_graph(client):
    """Create a small type hierarchy + instances using reified edges."""
    # Type definitions
    thing = client.add_node(
        name="thing", node_type="type_definition", uuid="type_thing"
    )
    entity = client.add_node(
        name="entity", node_type="type_definition", uuid="type_entity"
    )
    location = client.add_node(
        name="location", node_type="type_definition", uuid="type_location"
    )

    # IS_A hierarchy: location -> entity -> thing
    client.add_edge(source_uuid=entity, target_uuid=thing, relation="IS_A")
    client.add_edge(source_uuid=location, target_uuid=entity, relation="IS_A")

    # Instances
    paris = client.add_node(name="Paris", node_type="location", uuid="paris")
    france = client.add_node(name="France", node_type="entity", uuid="france")
    client.add_edge(source_uuid=paris, target_uuid=location, relation="IS_A")
    client.add_edge(source_uuid=france, target_uuid=entity, relation="IS_A")

    # Knowledge edge
    client.add_edge(source_uuid=paris, target_uuid=france, relation="LOCATED_IN")

    return {
        "paris": paris,
        "france": france,
        "entity": entity,
        "location": location,
        "thing": thing,
    }


class TestRelationshipQueries:
    def test_get_outgoing_edges(self, client, seeded_graph):
        query = HCGQueries.get_outgoing_edges()
        result = client._execute_read(query, {"uuid": seeded_graph["paris"]})
        relations = [r["relation"] for r in result]
        assert "LOCATED_IN" in relations
        assert "IS_A" in relations

    def test_get_typed_edges(self, client, seeded_graph):
        query = HCGQueries.get_edges_by_relation()
        result = client._execute_read(
            query, {"uuid": seeded_graph["paris"], "relation": "LOCATED_IN"}
        )
        assert len(result) == 1
        assert result[0]["target_uuid"] == seeded_graph["france"]


class TestTypeHierarchy:
    def test_find_type_definitions(self, client, seeded_graph):
        query = HCGQueries.find_type_definitions()
        result = client._execute_read(query, {})
        names = {r["name"] for r in result}
        assert "thing" in names
        assert "entity" in names
        assert "location" in names

    def test_has_ancestor(self, client, seeded_graph):
        query = HCGQueries.has_ancestor()
        result = client._execute_read(
            query, {"uuid": seeded_graph["paris"], "ancestor_name": "thing"}
        )
        assert len(result) > 0

    def test_find_instances_of_type(self, client, seeded_graph):
        query = HCGQueries.find_instances_of_type()
        result = client._execute_read(query, {"type_name": "entity"})
        uuids = {r["uuid"] for r in result}
        assert seeded_graph["france"] in uuids


class TestEdgeNodeTraversal:
    """Tests for methods that were rewritten from native rels to edge node traversal."""

    def test_get_entity_type(self, client, seeded_graph):
        """get_entity_type should traverse IS_A via edge nodes."""
        query = HCGQueries.get_entity_type()
        result = client._execute_read(query, {"entity_uuid": seeded_graph["paris"]})
        assert len(result) >= 1
        # Paris IS_A location
        target_names = [dict(r["c"])["name"] for r in result]
        assert "location" in target_names

    def test_get_entity_parts(self, client, seeded_graph):
        """get_entity_parts should traverse PART_OF via edge nodes."""
        # Create part relationship
        wheel = client.add_node(name="wheel", node_type="entity", uuid="wheel_1")
        car = client.add_node(name="car", node_type="entity", uuid="car_1")
        client.add_edge(source_uuid=wheel, target_uuid=car, relation="PART_OF")

        query = HCGQueries.get_entity_parts()
        result = client._execute_read(query, {"entity_uuid": "car_1"})
        assert len(result) == 1
        part_name = dict(result[0]["part"])["name"]
        assert part_name == "wheel"

    def test_get_entity_parent(self, client, seeded_graph):
        """get_entity_parent should traverse PART_OF via edge nodes."""
        wheel = client.add_node(name="wheel", node_type="entity", uuid="wheel_2")
        car = client.add_node(name="car", node_type="entity", uuid="car_2")
        client.add_edge(source_uuid=wheel, target_uuid=car, relation="PART_OF")

        query = HCGQueries.get_entity_parent()
        result = client._execute_read(query, {"entity_uuid": "wheel_2"})
        assert len(result) == 1
        parent_name = dict(result[0]["whole"])["name"]
        assert parent_name == "car"

    def test_get_entity_states(self, client, seeded_graph):
        """get_entity_states should traverse HAS_STATE via edge nodes."""
        state1 = client.add_node(name="hot", node_type="state", uuid="state_hot")
        client.add_edge(
            source_uuid=seeded_graph["paris"],
            target_uuid=state1,
            relation="HAS_STATE",
        )

        query = HCGQueries.get_entity_states()
        result = client._execute_read(query, {"entity_uuid": seeded_graph["paris"]})
        assert len(result) == 1
        state_name = dict(result[0]["s"])["name"]
        assert state_name == "hot"

    def test_get_process_effects(self, client, seeded_graph):
        """get_process_effects should traverse CAUSES via edge nodes."""
        proc = client.add_node(name="heat_up", node_type="process", uuid="proc_heat")
        state = client.add_node(name="heated", node_type="state", uuid="state_heated")
        client.add_edge(source_uuid=proc, target_uuid=state, relation="CAUSES")

        query = HCGQueries.get_process_effects()
        result = client._execute_read(query, {"process_uuid": "proc_heat"})
        assert len(result) == 1
        assert dict(result[0]["s"])["name"] == "heated"

    def test_get_process_preconditions(self, client, seeded_graph):
        """get_process_preconditions should traverse REQUIRES via edge nodes."""
        proc = client.add_node(name="heat_up", node_type="process", uuid="proc_heat2")
        state = client.add_node(name="cold", node_type="state", uuid="state_cold")
        client.add_edge(source_uuid=proc, target_uuid=state, relation="REQUIRES")

        query = HCGQueries.get_process_preconditions()
        result = client._execute_read(query, {"process_uuid": "proc_heat2"})
        assert len(result) == 1
        assert dict(result[0]["s"])["name"] == "cold"

    def test_find_capability_for_process(self, client, seeded_graph):
        """find_capability_for_process should traverse USES_CAPABILITY via edge nodes."""
        proc = client.add_node(name="pick_up", node_type="process", uuid="proc_pick")
        cap = client.add_node(
            name="gripper",
            node_type="capability",
            uuid="cap_grip",
            properties={"executor_type": "talos"},
        )
        client.add_edge(source_uuid=proc, target_uuid=cap, relation="USES_CAPABILITY")

        query = HCGQueries.find_capability_for_process()
        result = client._execute_read(query, {"process_uuid": "proc_pick"})
        assert len(result) == 1
        assert dict(result[0]["capability"])["name"] == "gripper"

    def test_check_state_satisfied(self, client, seeded_graph):
        """check_state_satisfied should traverse HAS_STATE via edge nodes."""
        entity = client.add_node(name="cup", node_type="entity", uuid="cup_1")
        state = client.add_node(
            name="full",
            node_type="state",
            uuid="state_full",
            properties={"is_empty": False},
        )
        client.add_edge(source_uuid=entity, target_uuid=state, relation="HAS_STATE")

        query = HCGQueries.check_state_satisfied()
        result = client._execute_read(
            query,
            {
                "entity_uuid": "cup_1",
                "property_key": "is_empty",
                "property_value": False,
            },
        )
        assert len(result) == 1
        assert result[0]["satisfied"] is True


class TestLinkMethodsRemoved:
    """Verify that old link_* query methods have been removed."""

    def test_no_link_is_a(self):
        assert not hasattr(HCGQueries, "link_is_a")

    def test_no_link_has_state(self):
        assert not hasattr(HCGQueries, "link_has_state")

    def test_no_link_requires(self):
        assert not hasattr(HCGQueries, "link_requires")

    def test_no_link_causes(self):
        assert not hasattr(HCGQueries, "link_causes")


class TestAncestorPropertyRemoved:
    """Verify that queries no longer reference n.ancestors or n.is_type_definition."""

    def _get_all_query_strings(self):
        """Collect all query strings from HCGQueries static methods."""
        queries = []
        for name in dir(HCGQueries):
            if name.startswith("_"):
                continue
            method = getattr(HCGQueries, name)
            if callable(method):
                try:
                    q = method()
                    if isinstance(q, str):
                        queries.append((name, q))
                except TypeError:
                    # Methods that take arguments — skip
                    pass
        return queries

    def test_no_ancestors_property(self):
        for name, q in self._get_all_query_strings():
            assert "n.ancestors" not in q, f"{name} still references n.ancestors"
            assert "e.ancestors" not in q, f"{name} still references e.ancestors"
            assert "s.ancestors" not in q, f"{name} still references s.ancestors"
            assert "p.ancestors" not in q, f"{name} still references p.ancestors"
            assert "c.ancestors" not in q, f"{name} still references c.ancestors"
            assert "IN n.ancestors" not in q, f"{name} still uses IN n.ancestors"

    def test_no_is_type_definition_property(self):
        for name, q in self._get_all_query_strings():
            assert (
                "is_type_definition" not in q
            ), f"{name} still references is_type_definition"
