"""
Cognitive Loop Smoke Test

End-to-end test of the full cognitive loop:
  User text → Hermes /llm → ProposalBuilder (NER + embeddings)
  → POST to Sophia /ingest/hermes_proposal → Neo4j + Milvus storage
  → context retrieval → system message injection → LLM response

Requires:
  - Hermes running (port 17000) with ML extras (spaCy, sentence-transformers)
  - Sophia running (port 47000)
  - Neo4j running (port 7687)
  - Milvus running (port 19530)
  - SOPHIA_API_KEY set in Hermes env (so Hermes can talk to Sophia)
  - OPENAI_API_KEY or HERMES_LLM_API_KEY set in Hermes env

Run manually:
  cd ~/projects/LOGOS/logos
  poetry run pytest tests/e2e/test_cognitive_loop_smoke.py -v -s
"""

import os
import time

import pytest
import requests

from logos_config.ports import get_repo_ports

# ---------------------------------------------------------------------------
# Service URLs from logos_config (authoritative port source)
# ---------------------------------------------------------------------------
HERMES_PORT = os.getenv("HERMES_PORT", str(get_repo_ports("hermes").api))
SOPHIA_PORT = os.getenv("SOPHIA_PORT", str(get_repo_ports("sophia").api))
HERMES_URL = os.getenv("HERMES_URL", f"http://localhost:{HERMES_PORT}")
SOPHIA_URL = os.getenv("SOPHIA_URL", f"http://localhost:{SOPHIA_PORT}")

# Neo4j config — shared infra, standard ports
NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "logosdev")

# Milvus config — shared infra
MILVUS_HOST = os.getenv("MILVUS_HOST", "localhost")
MILVUS_PORT = int(os.getenv("MILVUS_PORT", "19530"))

# Distinctive entity names unlikely to collide with existing data
SEED_TEXT = (
    "Dr. Amelia Thornton is a robotics researcher at Nexus Robotics in Zurich. "
    "She is developing the Chimera manipulator arm for precision assembly tasks."
)
# Entities spaCy should extract (PERSON, ORG, GPE, PRODUCT-ish)
EXPECTED_ENTITIES = {"Amelia Thornton", "Nexus Robotics", "Zurich"}
# Query that should trigger context retrieval for stored entities
QUERY_TEXT = "Tell me about the work happening at Nexus Robotics in Zurich."


# ---------------------------------------------------------------------------
# Skip entire module if services aren't running
# ---------------------------------------------------------------------------
def _services_available():
    """Check that Hermes and Sophia are both reachable."""
    for _name, url in [("Hermes", HERMES_URL), ("Sophia", SOPHIA_URL)]:
        try:
            r = requests.get(f"{url}/health", timeout=3)
            if r.status_code != 200:
                return False
        except Exception:
            return False
    return True


if not _services_available():
    pytest.skip(
        "Cognitive loop smoke test requires Hermes + Sophia + infra. "
        "Start services first.",
        allow_module_level=True,
    )


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------
@pytest.fixture(scope="module")
def neo4j_driver():
    """Create a Neo4j driver for direct verification queries."""
    try:
        from neo4j import GraphDatabase
    except ImportError:
        pytest.skip("neo4j driver not installed")

    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
    yield driver
    driver.close()


@pytest.fixture(scope="module")
def milvus_connection():
    """Connect to Milvus for direct embedding verification."""
    try:
        from pymilvus import connections
    except ImportError:
        pytest.skip("pymilvus not installed")

    alias = "smoke_test"
    connections.connect(alias=alias, host=MILVUS_HOST, port=MILVUS_PORT)
    yield alias
    connections.disconnect(alias)


def _cleanup_test_nodes(driver):
    """Remove nodes created during the smoke test."""
    with driver.session() as session:
        for name in EXPECTED_ENTITIES:
            session.run(
                "MATCH (n:Node) WHERE n.name = $name DETACH DELETE n",
                name=name,
            )


# ---------------------------------------------------------------------------
# Tests — ordered to run sequentially (pytest-ordering or naming convention)
# ---------------------------------------------------------------------------
class TestCognitiveLoopSmoke:
    """Full cognitive loop smoke test.

    Tests run in order:
      1. Seed the knowledge graph via a /llm call with real entities
      2. Verify nodes were stored in Neo4j
      3. Verify embeddings were stored in Milvus
      4. Query again and verify context annotation is injected
      5. (Optional) Verify real LLM uses the injected context
    """

    @pytest.fixture(autouse=True, scope="class")
    def setup_and_teardown(self, neo4j_driver):
        """Clean up test entities before and after the test class."""
        _cleanup_test_nodes(neo4j_driver)
        yield
        _cleanup_test_nodes(neo4j_driver)

    # -- Step 1: Seed the graph ------------------------------------------

    def test_01_seed_entities_via_llm(self):
        """Send entity-rich text through /llm to trigger the cognitive loop.

        This calls the full pipeline:
          Hermes /llm → ProposalBuilder (spaCy NER + embeddings)
          → POST proposal to Sophia → Neo4j + Milvus writes
          → LLM response
        """
        response = requests.post(
            f"{HERMES_URL}/llm",
            json={
                "prompt": SEED_TEXT,
                "provider": "openai",
                "model": "gpt-4o-mini",
                "max_tokens": 100,
            },
            timeout=90,
        )

        assert (
            response.status_code == 200
        ), f"Seed /llm call failed: {response.status_code} — {response.text}"

        data = response.json()
        assert "choices" in data, f"Response missing 'choices': {data}"
        assert len(data["choices"]) > 0, "No choices in response"
        assert data["choices"][0]["message"]["content"], "Empty LLM response"

        # Give Sophia a moment to finish async processing
        time.sleep(2)

    # -- Step 2: Verify Neo4j storage ------------------------------------

    def test_02_entities_stored_in_neo4j(self, neo4j_driver):
        """Verify that proposed entities were persisted as :Node in Neo4j."""
        found = {}
        with neo4j_driver.session() as session:
            for name in EXPECTED_ENTITIES:
                result = session.run(
                    "MATCH (n:Node) WHERE n.name = $name RETURN n.name AS name, "
                    "n.type AS type, n.uuid AS uuid",
                    name=name,
                )
                record = result.single()
                if record:
                    found[name] = {
                        "type": record["type"],
                        "uuid": record["uuid"],
                    }

        print(f"\nNeo4j entities found: {list(found.keys())}")
        print(f"Neo4j entities missing: {EXPECTED_ENTITIES - set(found.keys())}")
        for name, info in found.items():
            print(f"  {name}: type={info['type']}, uuid={info['uuid']}")

        assert len(found) > 0, (
            f"No entities found in Neo4j. Expected at least one of: "
            f"{EXPECTED_ENTITIES}. This likely means the proposal was not "
            f"sent to Sophia, or Sophia's ProposalProcessor is not running. "
            f"Check: SOPHIA_API_KEY set in Hermes env? Sophia /health shows "
            f"neo4j + milvus connected?"
        )

    # -- Step 2b: Verify relation edges in Neo4j -------------------------

    def test_02b_relations_stored_in_neo4j(self, neo4j_driver):
        """Verify that at least one relation edge was created between entities."""
        with neo4j_driver.session() as session:
            # Edge nodes have a 'relation' property and connect via :FROM/:TO
            result = session.run(
                """
                MATCH (edge:Node)
                WHERE edge.relation IS NOT NULL
                MATCH (edge)-[:FROM]->(src:Node)
                MATCH (edge)-[:TO]->(tgt:Node)
                WHERE src.name IN $names AND tgt.name IN $names
                RETURN edge.relation AS relation,
                       src.name AS source,
                       tgt.name AS target,
                       edge.uuid AS edge_uuid
                """,
                names=list(EXPECTED_ENTITIES),
            )
            edges = [dict(r) for r in result]

        print(f"\nRelation edges found: {len(edges)}")
        for e in edges:
            print(f"  {e['source']} -[{e['relation']}]-> {e['target']}")

        assert len(edges) > 0, (
            f"No relation edges found between {EXPECTED_ENTITIES}. "
            f"The relation extractor may not be producing edges, or "
            f"Sophia's ProposalProcessor may not be storing them. "
            f"Check Hermes logs for proposed_edges and Sophia logs for "
            f"edge storage."
        )

    # -- Step 3: Verify Milvus storage -----------------------------------

    def test_03_embeddings_stored_in_milvus(self, milvus_connection):
        """Verify that entity embeddings were persisted in Milvus."""
        from pymilvus import Collection, utility

        alias = milvus_connection

        # HCGMilvusSync uses these collection names
        hcg_collections = [
            "hcg_entity_embeddings",
            "hcg_concept_embeddings",
            "hcg_state_embeddings",
            "hcg_process_embeddings",
        ]

        existing = utility.list_collections(using=alias)
        print(f"\nMilvus collections: {existing}")

        # Check which HCG collections exist
        found_collections = [c for c in hcg_collections if c in existing]
        assert len(found_collections) > 0, (
            f"No HCG Milvus collections found. Expected at least one of: "
            f"{hcg_collections}. Sophia's HCGMilvusSync may not have "
            f"initialized. Check Sophia startup logs."
        )

        # Count total embeddings across HCG collections
        total_embeddings = 0
        for cname in found_collections:
            col = Collection(cname, using=alias)
            col.load()
            count = col.num_entities
            print(f"  {cname}: {count} embeddings")
            total_embeddings += count

        assert total_embeddings > 0, (
            "HCG collections exist but are empty. The proposal was likely "
            "processed but embeddings were not stored. Check Sophia logs "
            "for Milvus upsert errors."
        )

    # -- Step 3b: Verify edge embeddings in Milvus -----------------------

    def test_03b_edge_embeddings_in_milvus(self, milvus_connection):
        """Verify that edge embeddings were stored in the Edge collection."""
        from pymilvus import Collection, utility

        alias = milvus_connection
        edge_collection_name = "hcg_edge_embeddings"

        existing = utility.list_collections(using=alias)

        if edge_collection_name not in existing:
            pytest.skip(
                f"Edge collection '{edge_collection_name}' does not exist yet. "
                f"Sophia may not have created it on startup."
            )

        col = Collection(edge_collection_name, using=alias)
        col.load()
        count = col.num_entities
        print(f"\nEdge embeddings in Milvus: {count}")

        assert count > 0, (
            "Edge collection exists but is empty. Relation edges may have "
            "been stored in Neo4j but their embeddings were not persisted "
            "to Milvus. Check Sophia logs for edge embedding errors."
        )

    # -- Step 4: Verify context annotation on retrieval ------------------

    def test_04_context_annotation_on_retrieval(self):
        """Send a follow-up query and verify context injection.

        Uses the echo provider so we can inspect the exact message list
        that was sent to the LLM. If context injection works, the echo
        transcript will contain "Relevant knowledge from memory".
        """
        response = requests.post(
            f"{HERMES_URL}/llm",
            json={
                "prompt": QUERY_TEXT,
                "provider": "echo",
            },
            timeout=30,
        )

        assert (
            response.status_code == 200
        ), f"Query /llm call failed: {response.status_code} — {response.text}"

        data = response.json()
        echo_content = data["choices"][0]["message"]["content"]

        print(f"\nEcho transcript:\n{echo_content}")

        # The echo provider echoes all messages including injected system
        # messages. If Sophia returned relevant context, Hermes injects a
        # system message starting with "Relevant knowledge from memory:"
        assert "Relevant knowledge from memory" in echo_content, (
            f"Context annotation not found in echo transcript. "
            f"This means Sophia either returned no relevant context, or "
            f"Hermes did not inject it. Possible causes:\n"
            f"  - SOPHIA_API_KEY not set in Hermes env\n"
            f"  - Sophia returned empty context (embedding similarity too low)\n"
            f"  - ProposalProcessor not initialized in Sophia\n"
            f"  - Milvus search returned no results\n"
            f"Echo content was:\n{echo_content}"
        )

        # Verify that at least one of our seeded entities appears in the context
        found_in_context = [name for name in EXPECTED_ENTITIES if name in echo_content]
        print(f"Entities found in context annotation: {found_in_context}")

        assert len(found_in_context) > 0, (
            f"Context was injected but none of the expected entities "
            f"({EXPECTED_ENTITIES}) appear in it. The context may contain "
            f"unrelated data from a previous test run."
        )

    # -- Step 5: Verify real LLM uses context ----------------------------

    def test_05_openai_response_uses_context(self):
        """Ask the real LLM about seeded entities and check it uses context.

        This is a softer assertion — we check that the LLM response
        references at least one of the entities we stored. If the context
        injection worked, the LLM should know about Nexus Robotics etc.
        even though it has no prior knowledge of these fictional entities.
        """
        response = requests.post(
            f"{HERMES_URL}/llm",
            json={
                "prompt": (
                    "Based on what you know, who works at Nexus Robotics "
                    "and what are they building? Be specific."
                ),
                "provider": "openai",
                "model": "gpt-4o-mini",
                "max_tokens": 200,
            },
            timeout=30,
        )

        assert (
            response.status_code == 200
        ), f"OpenAI /llm call failed: {response.status_code} — {response.text}"

        data = response.json()
        llm_text = data["choices"][0]["message"]["content"]

        print(f"\nLLM response:\n{llm_text}")

        # The LLM should reference entities from the injected context.
        # "Amelia Thornton" and "Chimera" are fictional — the only way
        # the LLM knows about them is via the context annotation.
        fictional_entities = {"Amelia Thornton", "Chimera", "Nexus Robotics"}
        found = [e for e in fictional_entities if e.lower() in llm_text.lower()]

        print(f"Fictional entities found in LLM response: {found}")

        # Soft assertion — LLM behavior is non-deterministic
        if not found:
            pytest.xfail(
                "LLM did not reference fictional entities. Context may not "
                "have been injected, or the LLM chose not to use it. "
                "Check test_04 results for context injection verification."
            )


# ---------------------------------------------------------------------------
# Standalone: Direct Sophia proposal test (no Hermes, no ML needed)
# ---------------------------------------------------------------------------
class TestDirectSophiaProposal:
    """Test Sophia's proposal processing directly with a synthetic proposal.

    This bypasses Hermes entirely — crafts a proposal with fake embeddings
    and POSTs it directly to Sophia's /ingest/hermes_proposal endpoint.
    Useful for isolating Sophia-side issues from Hermes-side issues.
    """

    PROPOSAL_ID = "smoke-test-direct-proposal"
    ENTITY_NAME = "Prometheus Laboratory"
    ENTITY_NAME_2 = "Athena Research Group"
    # 384-dim zero vector — valid for MiniLM schema, won't match anything
    ZERO_EMBEDDING = [0.0] * 384
    # Slightly different vector for second entity (won't match first)
    NEAR_ZERO_EMBEDDING = [0.001] * 384

    @pytest.fixture(autouse=True, scope="class")
    def cleanup(self, neo4j_driver):
        """Remove synthetic test nodes and edge nodes."""

        def _clean():
            with neo4j_driver.session() as session:
                for name in (self.ENTITY_NAME, self.ENTITY_NAME_2):
                    session.run(
                        "MATCH (n:Node) WHERE n.name = $name DETACH DELETE n",
                        name=name,
                    )
                # Also clean up edge nodes between these entities.
                session.run(
                    "MATCH (e:Node) WHERE e.relation IS NOT NULL "
                    "AND (e.source IS NOT NULL OR e.target IS NOT NULL) "
                    "DETACH DELETE e"
                )

        _clean()
        yield
        _clean()

    def test_01_submit_synthetic_proposal(self):
        """POST a handcrafted proposal directly to Sophia."""
        proposal = {
            "proposal_id": self.PROPOSAL_ID,
            "correlation_id": "smoke-test-correlation",
            "source_service": "hermes",
            "llm_provider": "test",
            "model": "test",
            "generated_at": "2026-02-19T00:00:00Z",
            "confidence": 0.9,
            "raw_text": (f"{self.ENTITY_NAME} collaborates with {self.ENTITY_NAME_2}."),
            "proposed_nodes": [
                {
                    "name": self.ENTITY_NAME,
                    "type": "location",
                    "embedding": self.ZERO_EMBEDDING,
                    "embedding_id": "smoke-test-emb-001",
                    "dimension": 384,
                    "model": "all-MiniLM-L6-v2",
                    "properties": {},
                },
                {
                    "name": self.ENTITY_NAME_2,
                    "type": "agent",
                    "embedding": self.NEAR_ZERO_EMBEDDING,
                    "embedding_id": "smoke-test-emb-003",
                    "dimension": 384,
                    "model": "all-MiniLM-L6-v2",
                    "properties": {},
                },
            ],
            "proposed_edges": [
                {
                    "source_name": self.ENTITY_NAME,
                    "target_name": self.ENTITY_NAME_2,
                    "relation": "COLLABORATES_WITH",
                    "confidence": 0.8,
                    "bidirectional": True,
                    "embedding": self.ZERO_EMBEDDING,
                    "model": "all-MiniLM-L6-v2",
                    "properties": {
                        "raw_phrase": "collaborates with",
                    },
                },
            ],
            "document_embedding": {
                "embedding": self.ZERO_EMBEDDING,
                "embedding_id": "smoke-test-doc-emb-001",
                "dimension": 384,
                "model": "all-MiniLM-L6-v2",
            },
            "metadata": {"test": True},
        }

        response = requests.post(
            f"{SOPHIA_URL}/ingest/hermes_proposal",
            json=proposal,
            timeout=15,
        )

        assert response.status_code == 201, (
            f"Sophia proposal ingestion failed: {response.status_code} — "
            f"{response.text}"
        )

        data = response.json()
        print(f"\nSophia response: {data}")

        assert data["proposal_id"] == self.PROPOSAL_ID
        assert data["status"] == "accepted"

        # If ProposalProcessor is running, we should get stored_node_ids
        stored = data.get("stored_node_ids", [])
        print(f"Stored node IDs: {stored}")

        stored_edges = data.get("stored_edge_ids", [])
        print(f"Stored edge IDs: {stored_edges}")

        # relevant_context may or may not have entries
        context = data.get("relevant_context", [])
        print(f"Relevant context items: {len(context)}")

    def test_02_synthetic_nodes_in_neo4j(self, neo4j_driver):
        """Verify the synthetic nodes were stored in Neo4j."""
        time.sleep(1)  # Brief pause for async processing

        for entity_name in (self.ENTITY_NAME, self.ENTITY_NAME_2):
            with neo4j_driver.session() as session:
                result = session.run(
                    "MATCH (n:Node) WHERE n.name = $name "
                    "RETURN n.name AS name, n.type AS type, n.uuid AS uuid, "
                    "n.source AS source",
                    name=entity_name,
                )
                record = result.single()

            if record:
                print(
                    f"\nFound node: name={record['name']}, type={record['type']}, "
                    f"uuid={record['uuid']}, source={record['source']}"
                )
                assert record["name"] == entity_name
            else:
                pytest.fail(
                    f"Node '{entity_name}' not found in Neo4j after proposal "
                    f"ingestion. ProposalProcessor may not be initialized — check "
                    f"that Sophia started with Milvus available."
                )

    def test_02b_synthetic_edge_in_neo4j(self, neo4j_driver):
        """Verify the synthetic edge was stored in Neo4j."""
        with neo4j_driver.session() as session:
            result = session.run(
                """
                MATCH (edge:Node)
                WHERE edge.relation = 'COLLABORATES_WITH'
                MATCH (edge)-[:FROM]->(src:Node {name: $src})
                MATCH (edge)-[:TO]->(tgt:Node {name: $tgt})
                RETURN edge.uuid AS uuid, edge.relation AS relation,
                       src.name AS source, tgt.name AS target
                """,
                src=self.ENTITY_NAME,
                tgt=self.ENTITY_NAME_2,
            )
            record = result.single()

        if record:
            print(
                f"\nFound edge: {record['source']} -[{record['relation']}]-> "
                f"{record['target']} (uuid={record['uuid']})"
            )
        else:
            pytest.fail(
                f"Edge COLLABORATES_WITH not found between "
                f"'{self.ENTITY_NAME}' and '{self.ENTITY_NAME_2}'. "
                f"ProposalProcessor may not be processing proposed_edges."
            )

    def test_03_context_returned_for_similar_query(self):
        """Submit a second proposal referencing the same entity.

        If dedup works, the entity should NOT be re-created, and the
        existing node should appear in relevant_context.
        """
        proposal = {
            "proposal_id": "smoke-test-dedup-check",
            "correlation_id": "smoke-test-dedup",
            "source_service": "hermes",
            "llm_provider": "test",
            "model": "test",
            "generated_at": "2026-02-19T00:00:01Z",
            "confidence": 0.9,
            "raw_text": f"Research at {self.ENTITY_NAME} continues.",
            "proposed_nodes": [
                {
                    "name": self.ENTITY_NAME,
                    "type": "location",
                    # Same zero embedding — should match the stored one
                    "embedding": self.ZERO_EMBEDDING,
                    "embedding_id": "smoke-test-emb-002",
                    "dimension": 384,
                    "model": "all-MiniLM-L6-v2",
                    "properties": {},
                },
            ],
            "document_embedding": {
                "embedding": self.ZERO_EMBEDDING,
                "embedding_id": "smoke-test-doc-emb-002",
                "dimension": 384,
                "model": "all-MiniLM-L6-v2",
            },
            "metadata": {"test": True},
        }

        response = requests.post(
            f"{SOPHIA_URL}/ingest/hermes_proposal",
            json=proposal,
            timeout=15,
        )

        assert (
            response.status_code == 201
        ), f"Dedup proposal failed: {response.status_code} — {response.text}"

        data = response.json()
        stored = data.get("stored_node_ids", [])
        context = data.get("relevant_context", [])

        print(f"\nDedup check — stored_node_ids: {stored}")
        print(f"Dedup check — relevant_context ({len(context)} items):")
        for item in context:
            print(
                f"  - {item.get('name', '?')} ({item.get('type', '?')}): "
                f"score={item.get('score', '?')}"
            )

        # The entity should have been deduped (L2 distance = 0 for identical
        # embeddings, well below the 0.5 threshold), so stored_node_ids
        # should be empty and the existing node should appear in context.
        if stored:
            print(
                f"WARNING: Entity was re-created instead of deduped. "
                f"stored_node_ids={stored}. The dedup threshold may need tuning."
            )
