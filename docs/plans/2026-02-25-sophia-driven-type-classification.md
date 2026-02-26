# Sophia-Driven Type Classification — Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Move HCG node type classification from Hermes to Sophia, using embedding space geometry (centroids for type assignment, k-NN for relationship discovery, variance-based split detection for type emergence).

**Architecture:** Hybrid centroid + k-NN. Type centroids live in a dedicated Milvus collection. On ingestion, Sophia classifies by nearest centroid, deduplicates within the assigned type's collection, then creates the node. Cross-cluster k-NN discovers relationship candidates; Hermes names them. Type emergence detects sub-clusters via variance monitoring and k-means splits.

**Tech Stack:** Python 3.12, pymilvus, neo4j, FastAPI, numpy (for centroid math), pytest

**Design doc:** `docs/plans/2026-02-25-sophia-driven-type-classification-design.md`

---

## Phase 1: Foundation (logos foundry)

### Task 1: Add TypeCentroid collection to HCGMilvusSync

**Files:**
- Modify: `logos/logos_hcg/sync.py:40-48` (COLLECTION_NAMES, NodeType)
- Test: `logos/tests/test_hcg_milvus_sync.py`

**Step 1: Write the failing test**

Add to `tests/test_hcg_milvus_sync.py`:

```python
def test_type_centroid_collection_in_names(self):
    """Test that TypeCentroid collection is registered."""
    assert "TypeCentroid" in COLLECTION_NAMES
    assert COLLECTION_NAMES["TypeCentroid"] == "hcg_type_centroids"
```

**Step 2: Run test to verify it fails**

Run: `cd logos && poetry run pytest tests/test_hcg_milvus_sync.py::TestHCGMilvusSync::test_type_centroid_collection_in_names -v`
Expected: FAIL with KeyError

**Step 3: Write minimal implementation**

In `logos_hcg/sync.py`, update `COLLECTION_NAMES` (line 40) and `NodeType` (line 48):

```python
COLLECTION_NAMES = {
    "Entity": "hcg_entity_embeddings",
    "Concept": "hcg_concept_embeddings",
    "State": "hcg_state_embeddings",
    "Process": "hcg_process_embeddings",
    "Edge": "hcg_edge_embeddings",
    "TypeCentroid": "hcg_type_centroids",
}

NodeType = Literal["Entity", "Concept", "State", "Process", "Edge", "TypeCentroid"]
```

**Step 4: Run test to verify it passes**

Run: `cd logos && poetry run pytest tests/test_hcg_milvus_sync.py -v`
Expected: All tests PASS

**Step 5: Commit**

```bash
git add logos_hcg/sync.py tests/test_hcg_milvus_sync.py
git commit -m "feat(hcg): add TypeCentroid Milvus collection for type centroids"
```

---

### Task 2: Add centroid-specific search and update methods to HCGMilvusSync

**Files:**
- Modify: `logos/logos_hcg/sync.py` (add methods after `search_similar`)
- Test: `logos/tests/test_hcg_milvus_sync.py`

**Step 1: Write the failing tests**

```python
@patch("logos_hcg.sync.connections")
@patch("logos_hcg.sync.utility")
@patch("logos_hcg.sync.Collection")
def test_update_centroid_new(self, mock_collection, mock_utility, mock_connections):
    """Test upserting a centroid embedding for a type."""
    mock_utility.has_collection.return_value = True
    mock_coll = Mock()
    mock_collection.return_value = mock_coll

    sync = HCGMilvusSync()
    sync.connect()
    result = sync.update_centroid(
        type_uuid="type_location",
        centroid=[0.1] * 384,
        model="all-MiniLM-L6-v2",
    )
    assert result["embedding_id"] == "type_location"

@patch("logos_hcg.sync.connections")
@patch("logos_hcg.sync.utility")
@patch("logos_hcg.sync.Collection")
def test_find_nearest_type(self, mock_collection, mock_utility, mock_connections):
    """Test searching for nearest type centroid."""
    mock_utility.has_collection.return_value = True
    mock_coll = Mock()
    mock_hit = Mock()
    mock_hit.entity.get.return_value = "type_location"
    mock_hit.distance = 0.15
    mock_coll.search.return_value = [[mock_hit]]
    mock_collection.return_value = mock_coll

    sync = HCGMilvusSync()
    sync.connect()
    results = sync.find_nearest_types(
        query_embedding=[0.1] * 384,
        top_k=3,
    )
    assert len(results) == 1
    assert results[0]["uuid"] == "type_location"
    assert results[0]["score"] == 0.15
```

**Step 2: Run tests to verify they fail**

Run: `cd logos && poetry run pytest tests/test_hcg_milvus_sync.py::TestHCGMilvusSync::test_update_centroid_new tests/test_hcg_milvus_sync.py::TestHCGMilvusSync::test_find_nearest_type -v`
Expected: FAIL — methods don't exist

**Step 3: Write minimal implementation**

Add to `logos_hcg/sync.py` after the `search_similar` method:

```python
def update_centroid(
    self,
    type_uuid: str,
    centroid: list[float],
    model: str,
) -> dict[str, Any]:
    """Upsert a type centroid embedding in the TypeCentroid collection."""
    return self.upsert_embedding(
        node_type="TypeCentroid",
        uuid=type_uuid,
        embedding=centroid,
        model=model,
    )

def find_nearest_types(
    self,
    query_embedding: list[float],
    top_k: int = 3,
) -> list[dict]:
    """Find the nearest type centroids for a query embedding."""
    return self.search_similar(
        node_type="TypeCentroid",
        query_embedding=query_embedding,
        top_k=top_k,
    )
```

**Step 4: Run full test suite**

Run: `cd logos && poetry run pytest tests/test_hcg_milvus_sync.py -v`
Expected: All PASS

**Step 5: Commit**

```bash
git add logos_hcg/sync.py tests/test_hcg_milvus_sync.py
git commit -m "feat(hcg): add centroid update and nearest-type search methods"
```

---

## Phase 2: Sophia Type Classifier

### Task 3: Create the TypeClassifier module

**Files:**
- Create: `sophia/src/sophia/ingestion/type_classifier.py`
- Test: `sophia/tests/unit/ingestion/test_type_classifier.py`

**Step 1: Write the failing tests**

Create `sophia/tests/unit/ingestion/test_type_classifier.py`:

```python
"""Tests for Sophia's embedding-based type classifier."""

import pytest
from unittest.mock import MagicMock

from sophia.ingestion.type_classifier import TypeClassifier


class TestTypeClassifier:
    """Test suite for TypeClassifier."""

    def _make_classifier(self, milvus=None, hcg=None):
        return TypeClassifier(
            milvus=milvus or MagicMock(),
            hcg=hcg or MagicMock(),
        )

    def test_classify_high_confidence(self):
        """Close to a centroid => high confidence assignment."""
        mock_milvus = MagicMock()
        mock_milvus.find_nearest_types.return_value = [
            {"uuid": "type_location", "score": 0.1},
            {"uuid": "type_concept", "score": 0.9},
        ]
        classifier = self._make_classifier(milvus=mock_milvus)

        result = classifier.classify([0.1] * 384)

        assert result.type_uuid == "type_location"
        assert result.type_name == "location"
        assert result.confidence > 0.8
        assert result.needs_reclassification is False

    def test_classify_low_confidence_ambiguous(self):
        """Between two centroids => low confidence, flagged."""
        mock_milvus = MagicMock()
        mock_milvus.find_nearest_types.return_value = [
            {"uuid": "type_location", "score": 0.45},
            {"uuid": "type_concept", "score": 0.50},
        ]
        classifier = self._make_classifier(milvus=mock_milvus)

        result = classifier.classify([0.1] * 384)

        assert result.type_uuid == "type_location"
        assert result.confidence < 0.5
        assert result.needs_reclassification is True

    def test_classify_no_centroids(self):
        """No centroids in Milvus => fallback to 'entity' with zero confidence."""
        mock_milvus = MagicMock()
        mock_milvus.find_nearest_types.return_value = []
        classifier = self._make_classifier(milvus=mock_milvus)

        result = classifier.classify([0.1] * 384)

        assert result.type_uuid == "type_entity"
        assert result.type_name == "entity"
        assert result.confidence == 0.0
        assert result.needs_reclassification is True

    def test_update_centroid_incremental(self):
        """Centroid updates incrementally after node assignment."""
        mock_milvus = MagicMock()
        mock_hcg = MagicMock()
        mock_hcg.get_node.return_value = {
            "uuid": "type_location",
            "properties": {"member_count": 10},
        }
        classifier = self._make_classifier(milvus=mock_milvus, hcg=mock_hcg)

        classifier.update_centroid_for_assignment(
            type_uuid="type_location",
            new_embedding=[1.0] * 384,
            current_centroid=[0.0] * 384,
            member_count=10,
            model="all-MiniLM-L6-v2",
        )

        mock_milvus.update_centroid.assert_called_once()
        call_args = mock_milvus.update_centroid.call_args
        new_centroid = call_args.kwargs.get("centroid") or call_args[1].get("centroid") or call_args[0][1]
        # (0.0 * 10 + 1.0) / 11 ≈ 0.0909
        assert abs(new_centroid[0] - (1.0 / 11)) < 0.001
```

**Step 2: Run tests to verify they fail**

Run: `cd sophia && poetry run pytest tests/unit/ingestion/test_type_classifier.py -v`
Expected: FAIL — module doesn't exist

**Step 3: Write minimal implementation**

Create `sophia/src/sophia/ingestion/type_classifier.py`:

```python
"""Embedding-based type classifier for Sophia.

Uses centroid comparison in Milvus to assign HCG node types.
Sophia owns the type vocabulary — Hermes type hints are ignored.
"""

import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)

# If the gap between the top two centroid distances is less than this
# fraction of the top distance, the assignment is ambiguous.
AMBIGUITY_RATIO = 0.2

# Distances above this are considered too far from any type.
MAX_DISTANCE = 2.0

FALLBACK_TYPE_UUID = "type_entity"
FALLBACK_TYPE_NAME = "entity"


@dataclass
class TypeAssignment:
    """Result of type classification."""

    type_uuid: str
    type_name: str
    confidence: float
    needs_reclassification: bool


class TypeClassifier:
    """Assigns HCG node types using embedding-space centroid proximity."""

    def __init__(self, milvus, hcg):
        self._milvus = milvus
        self._hcg = hcg

    def classify(self, embedding: list[float], top_k: int = 3) -> TypeAssignment:
        """Classify an embedding by nearest type centroid.

        Args:
            embedding: The node's embedding vector.
            top_k: Number of candidate centroids to consider.

        Returns:
            TypeAssignment with type, confidence, and reclassification flag.
        """
        results = self._milvus.find_nearest_types(
            query_embedding=embedding,
            top_k=top_k,
        )

        if not results:
            return TypeAssignment(
                type_uuid=FALLBACK_TYPE_UUID,
                type_name=FALLBACK_TYPE_NAME,
                confidence=0.0,
                needs_reclassification=True,
            )

        best = results[0]
        best_distance = best["score"]
        best_uuid = best["uuid"]
        best_name = best_uuid.removeprefix("type_")

        # Confidence: inverse of distance, clamped to [0, 1]
        if best_distance <= 0:
            confidence = 1.0
        elif best_distance >= MAX_DISTANCE:
            confidence = 0.0
        else:
            confidence = 1.0 - (best_distance / MAX_DISTANCE)

        # Ambiguity check: if runner-up is close, lower confidence
        needs_reclass = False
        if len(results) >= 2:
            runner_up_distance = results[1]["score"]
            gap = runner_up_distance - best_distance
            if gap < AMBIGUITY_RATIO * best_distance:
                confidence *= 0.5
                needs_reclass = True

        if confidence < 0.5:
            needs_reclass = True

        return TypeAssignment(
            type_uuid=best_uuid,
            type_name=best_name,
            confidence=round(confidence, 4),
            needs_reclassification=needs_reclass,
        )

    def update_centroid_for_assignment(
        self,
        type_uuid: str,
        new_embedding: list[float],
        current_centroid: list[float],
        member_count: int,
        model: str,
    ) -> list[float]:
        """Incrementally update a type centroid after assigning a new node.

        new_centroid = (old_centroid * count + new_embedding) / (count + 1)

        Returns:
            The updated centroid vector.
        """
        new_count = member_count + 1
        updated = [
            (old * member_count + new) / new_count
            for old, new in zip(current_centroid, new_embedding)
        ]

        self._milvus.update_centroid(
            type_uuid=type_uuid,
            centroid=updated,
            model=model,
        )

        return updated
```

**Step 4: Run tests to verify they pass**

Run: `cd sophia && poetry run pytest tests/unit/ingestion/test_type_classifier.py -v`
Expected: All PASS

**Step 5: Commit**

```bash
git add src/sophia/ingestion/type_classifier.py tests/unit/ingestion/test_type_classifier.py
git commit -m "feat(sophia): add TypeClassifier for centroid-based type assignment"
```

---

## Phase 3: Integrate Classifier into Proposal Processing

### Task 4: Modify ProposalProcessor to use TypeClassifier

**Files:**
- Modify: `sophia/src/sophia/ingestion/proposal_processor.py:29-52,135-242`
- Modify: `sophia/tests/unit/ingestion/test_proposal_processor.py`

**Step 1: Write the failing test**

Add to the existing test file `sophia/tests/unit/ingestion/test_proposal_processor.py`:

```python
def test_process_uses_type_classifier(self):
    """Sophia classifies node type via centroid, ignoring Hermes type hint."""
    mock_hcg = MagicMock()
    mock_hcg.add_node.return_value = "uuid-1"
    mock_hcg.get_node.return_value = None

    mock_milvus = MagicMock()
    mock_milvus.search_similar.return_value = []  # no dedup match
    mock_milvus.find_nearest_types.return_value = [
        {"uuid": "type_location", "score": 0.1},
    ]

    processor = ProposalProcessor(hcg_client=mock_hcg, milvus_sync=mock_milvus)
    proposal = {
        "proposal_id": "test-1",
        "source_service": "hermes",
        "confidence": 0.8,
        "raw_text": "Dublin is a city",
        "proposed_nodes": [
            {
                "name": "Dublin",
                "type": "state",  # Hermes says state — should be ignored
                "embedding": [0.1] * 384,
                "embedding_id": "emb-1",
                "dimension": 384,
                "model": "all-MiniLM-L6-v2",
                "properties": {"start": 0, "end": 6},
            }
        ],
        "proposed_edges": [],
        "document_embedding": {
            "embedding": [0.2] * 384,
            "embedding_id": "doc-1",
            "dimension": 384,
            "model": "all-MiniLM-L6-v2",
        },
    }

    result = processor.process(proposal)

    # Verify add_node was called with Sophia's classification, not Hermes's
    add_node_call = mock_hcg.add_node.call_args_list[0]
    assert add_node_call.kwargs.get("node_type") == "location"  # NOT "state"
```

**Step 2: Run test to verify it fails**

Run: `cd sophia && poetry run pytest tests/unit/ingestion/test_proposal_processor.py::test_process_uses_type_classifier -v`
Expected: FAIL — processor still uses Hermes type

**Step 3: Modify proposal_processor.py**

Key changes to `sophia/src/sophia/ingestion/proposal_processor.py`:

1. Import TypeClassifier (top of file)
2. Instantiate TypeClassifier in `__init__` using the existing `milvus_sync` and `hcg_client`
3. In the node processing loop (lines ~135-242), replace:
   - `node_type = proposed.get("type", "entity")` with `classification = self._classifier.classify(embedding)`
   - `collection = _collection_for(node_type)` with `collection = _collection_for(classification.type_name)`
   - Pass `classification.confidence` as `type_confidence` property
   - Pass `classification.needs_reclassification` as property
   - After successful creation, call `self._classifier.update_centroid_for_assignment()`

The `_NODE_TYPE_TO_COLLECTION` dict and `_collection_for()` function stay — they just receive Sophia's classification instead of Hermes's.

See design doc Section "Component 2: Ingestion-Time Classification" for the full flow.

**Step 4: Run full processor test suite**

Run: `cd sophia && poetry run pytest tests/unit/ingestion/test_proposal_processor.py -v`
Expected: All PASS (existing tests need updates for the new classifier dependency)

**Step 5: Commit**

```bash
git add src/sophia/ingestion/proposal_processor.py tests/unit/ingestion/test_proposal_processor.py
git commit -m "feat(sophia): replace Hermes type hints with centroid-based classification"
```

---

### Task 5: Seed type centroids at startup

**Files:**
- Modify: `logos/logos_hcg/seeder.py:101-170` (add centroid seeding)
- Modify: `sophia/src/sophia/api/app.py:383-404` (call seeder during lifespan)
- Test: `logos/tests/test_hcg_seeder.py` (or create if missing)

**Step 1: Write the failing test**

```python
def test_seed_type_centroids(self):
    """Seeder generates and stores centroid embeddings for each type."""
    mock_client = MagicMock()
    mock_milvus = MagicMock()
    mock_embed = AsyncMock(return_value={"embedding": [0.1] * 384})

    seeder = HCGSeeder(client=mock_client, milvus_sync=mock_milvus)
    count = seeder.seed_type_centroids(embed_fn=mock_embed)

    assert count == len(TYPE_PARENTS)
    assert mock_milvus.update_centroid.call_count == len(TYPE_PARENTS)
```

**Step 2: Run test to verify it fails**

Expected: FAIL — `seed_type_centroids` method doesn't exist

**Step 3: Write implementation**

Add `seed_type_centroids` method to `HCGSeeder` in `logos/logos_hcg/seeder.py`. For each type in `TYPE_PARENTS`:
1. Use the type description from a descriptions dict (mirroring the old `ONTOLOGY_TYPES` descriptions)
2. Call `embed_fn(description)` to get an embedding
3. Call `milvus_sync.update_centroid(type_uuid, centroid, model)`
4. Set `member_count=0`, `centroid_variance=0.0` on the type_definition node

The `embed_fn` is injected so the seeder doesn't depend on Hermes directly — Sophia's lifespan passes Hermes's embed endpoint as a callable.

**Step 4: Run tests**

Run: `cd logos && poetry run pytest tests/test_hcg_seeder.py -v`
Expected: All PASS

**Step 5: Commit**

```bash
git add logos_hcg/seeder.py tests/test_hcg_seeder.py
git commit -m "feat(hcg): seed type centroid embeddings from type descriptions"
```

---

## Phase 4: Cross-Cluster Relationship Discovery

### Task 6: Add RelationshipDiscoverer module

**Files:**
- Create: `sophia/src/sophia/ingestion/relationship_discoverer.py`
- Test: `sophia/tests/unit/ingestion/test_relationship_discoverer.py`

**Step 1: Write the failing tests**

```python
class TestRelationshipDiscoverer:

    def test_find_cross_cluster_candidates(self):
        """Nodes close to a node but in different type clusters are candidates."""
        mock_milvus = MagicMock()
        # Searching non-own collections returns a close node
        mock_milvus.search_similar.return_value = [
            {"uuid": "node-in-other-cluster", "score": 0.3},
        ]
        mock_milvus.find_nearest_types.return_value = [
            {"uuid": "type_process", "score": 0.8},  # far from own centroid
        ]

        discoverer = RelationshipDiscoverer(milvus=mock_milvus)
        candidates = discoverer.find_candidates(
            embedding=[0.1] * 384,
            own_type="Entity",
            top_k=5,
        )

        assert len(candidates) >= 1
        assert candidates[0]["uuid"] == "node-in-other-cluster"

    def test_filter_boundary_nodes(self):
        """Nodes closer to their own centroid than to query are filtered out."""
        mock_milvus = MagicMock()
        # Node is close to query but also very close to its own centroid
        mock_milvus.search_similar.return_value = [
            {"uuid": "boundary-node", "score": 0.4},
        ]
        mock_milvus.find_nearest_types.return_value = [
            {"uuid": "type_concept", "score": 0.1},  # very close to own centroid
        ]

        discoverer = RelationshipDiscoverer(milvus=mock_milvus)
        candidates = discoverer.find_candidates(
            embedding=[0.1] * 384,
            own_type="Entity",
            top_k=5,
        )

        assert len(candidates) == 0  # filtered out
```

**Step 2: Run tests to verify they fail**

Expected: FAIL — module doesn't exist

**Step 3: Write implementation**

Create `sophia/src/sophia/ingestion/relationship_discoverer.py`:

The `find_candidates` method:
1. Gets the list of all collection types except `own_type` and `TypeCentroid` and `Edge`
2. For each collection, calls `milvus.search_similar(node_type=coll, query_embedding=embedding, top_k=top_k)`
3. For each hit, checks if the hit is closer to the query than to its own type centroid (via `find_nearest_types` with the hit's embedding — requires fetching the hit's embedding, or storing the centroid distance as metadata)
4. Returns filtered candidates sorted by score

**Step 4: Run tests**

Run: `cd sophia && poetry run pytest tests/unit/ingestion/test_relationship_discoverer.py -v`
Expected: All PASS

**Step 5: Commit**

```bash
git add src/sophia/ingestion/relationship_discoverer.py tests/unit/ingestion/test_relationship_discoverer.py
git commit -m "feat(sophia): add cross-cluster relationship discovery via k-NN"
```

---

## Phase 5: Hermes Naming Endpoints

### Task 7: Add POST /name-type endpoint

**Files:**
- Modify: `hermes/src/hermes/main.py` (add endpoint near line ~888)
- Test: `hermes/tests/test_naming.py` (create)

**Step 1: Write the failing test**

Create `hermes/tests/test_naming.py`:

```python
import pytest
from unittest.mock import AsyncMock, patch
from httpx import AsyncClient, ASGITransport

from hermes.main import app


@pytest.mark.asyncio
async def test_name_type_returns_name():
    """POST /name-type returns a type name for a cluster of node names."""
    with patch("hermes.main.generate_completion", new_callable=AsyncMock) as mock_llm:
        mock_llm.return_value = {
            "choices": [{"message": {"content": '{"type_name": "temporal_reference"}'}}]
        }
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.post("/name-type", json={
                "node_names": ["13th century", "the 1200s", "medieval period"],
                "parent_type": "state",
            })
        assert resp.status_code == 200
        assert resp.json()["type_name"] == "temporal_reference"
```

**Step 2: Run test to verify it fails**

Run: `cd hermes && poetry run pytest tests/test_naming.py -v`
Expected: FAIL — 404, endpoint doesn't exist

**Step 3: Write implementation**

Add to `hermes/src/hermes/main.py`:

```python
class NameTypeRequest(BaseModel):
    node_names: list[str]
    parent_type: str | None = None

class NameTypeResponse(BaseModel):
    type_name: str

@app.post("/name-type", response_model=NameTypeResponse)
async def name_type(request: NameTypeRequest) -> NameTypeResponse:
    """Given a cluster of node names, suggest a type name."""
    from hermes.llm import generate_completion

    prompt = (
        "You are naming a category for a knowledge graph. "
        "The following nodes form a distinct group"
    )
    if request.parent_type:
        prompt += f" within the '{request.parent_type}' category"
    prompt += (
        ":\n\n"
        + "\n".join(f"- {name}" for name in request.node_names)
        + "\n\nWhat single, concise name (1-3 words, lowercase, underscores) "
        "best describes this group? Return JSON: {\"type_name\": \"...\"}"
    )

    result = await generate_completion(
        messages=[{"role": "user", "content": prompt}],
        temperature=0.0,
        max_tokens=64,
        metadata={"scenario": "name_type"},
    )

    content = result["choices"][0]["message"]["content"]
    import json
    data = json.loads(content)
    return NameTypeResponse(type_name=data["type_name"])
```

**Step 4: Run tests**

Run: `cd hermes && poetry run pytest tests/test_naming.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add src/hermes/main.py tests/test_naming.py
git commit -m "feat(hermes): add POST /name-type endpoint for cluster naming"
```

---

### Task 8: Add POST /name-relationship endpoint

**Files:**
- Modify: `hermes/src/hermes/main.py`
- Test: `hermes/tests/test_naming.py` (extend)

**Step 1: Write the failing test**

Add to `hermes/tests/test_naming.py`:

```python
@pytest.mark.asyncio
async def test_name_relationship_returns_label():
    """POST /name-relationship returns an edge label for a node pair."""
    with patch("hermes.main.generate_completion", new_callable=AsyncMock) as mock_llm:
        mock_llm.return_value = {
            "choices": [{"message": {"content": '{"relationship": "LOCATED_IN", "bidirectional": false}'}}]
        }
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.post("/name-relationship", json={
                "source_name": "Dublin",
                "target_name": "Ireland",
                "context": "Dublin is the capital of Ireland",
            })
        assert resp.status_code == 200
        assert resp.json()["relationship"] == "LOCATED_IN"
```

**Step 2: Run test to verify it fails**

Expected: FAIL — 404

**Step 3: Write implementation**

Add to `hermes/src/hermes/main.py`:

```python
class NameRelationshipRequest(BaseModel):
    source_name: str
    target_name: str
    context: str | None = None

class NameRelationshipResponse(BaseModel):
    relationship: str
    bidirectional: bool = False

@app.post("/name-relationship", response_model=NameRelationshipResponse)
async def name_relationship(request: NameRelationshipRequest) -> NameRelationshipResponse:
    """Given two node names, suggest a relationship label."""
    from hermes.llm import generate_completion

    prompt = (
        f"What is the relationship between '{request.source_name}' "
        f"and '{request.target_name}' in a knowledge graph?"
    )
    if request.context:
        prompt += f"\n\nContext: {request.context}"
    prompt += (
        "\n\nReturn a JSON object with:\n"
        '- "relationship": an UPPER_SNAKE_CASE edge label (e.g., LOCATED_IN, CAUSES, PART_OF)\n'
        '- "bidirectional": true if the relationship goes both ways, false otherwise\n'
        "Return ONLY valid JSON."
    )

    result = await generate_completion(
        messages=[{"role": "user", "content": prompt}],
        temperature=0.0,
        max_tokens=64,
        metadata={"scenario": "name_relationship"},
    )

    content = result["choices"][0]["message"]["content"]
    import json
    data = json.loads(content)
    return NameRelationshipResponse(
        relationship=data["relationship"],
        bidirectional=data.get("bidirectional", False),
    )
```

**Step 4: Run tests**

Run: `cd hermes && poetry run pytest tests/test_naming.py -v`
Expected: All PASS

**Step 5: Commit**

```bash
git add src/hermes/main.py tests/test_naming.py
git commit -m "feat(hermes): add POST /name-relationship endpoint for edge labeling"
```

---

## Phase 6: Type Emergence

### Task 9: Add TypeEmergenceDetector module

**Files:**
- Create: `sophia/src/sophia/ingestion/type_emergence.py`
- Test: `sophia/tests/unit/ingestion/test_type_emergence.py`

**Step 1: Write the failing tests**

```python
class TestTypeEmergenceDetector:

    def test_no_split_when_variance_low(self):
        """Low variance type should not trigger a split."""
        mock_milvus = MagicMock()
        mock_hcg = MagicMock()
        mock_hcg.get_node.return_value = {
            "uuid": "type_location",
            "properties": {"member_count": 20, "centroid_variance": 0.1},
        }

        detector = TypeEmergenceDetector(
            milvus=mock_milvus,
            hcg=mock_hcg,
            variance_threshold=0.5,
        )
        result = detector.check_type("type_location")
        assert result is None  # no split needed

    def test_split_detected_when_variance_high(self):
        """High variance with two clear sub-clusters triggers a split."""
        mock_milvus = MagicMock()
        mock_hcg = MagicMock()
        mock_hcg.get_node.return_value = {
            "uuid": "type_state",
            "properties": {"member_count": 30, "centroid_variance": 0.8},
        }

        # Return embeddings for k-means to split
        cluster_a = [[0.0] * 384] * 15
        cluster_b = [[1.0] * 384] * 15
        mock_milvus.get_all_embeddings.return_value = cluster_a + cluster_b

        detector = TypeEmergenceDetector(
            milvus=mock_milvus,
            hcg=mock_hcg,
            variance_threshold=0.5,
        )
        result = detector.check_type("type_state")

        assert result is not None
        assert len(result.sub_clusters) == 2
        assert result.should_split is True
```

**Step 2: Run tests to verify they fail**

Expected: FAIL — module doesn't exist

**Step 3: Write implementation**

Create `sophia/src/sophia/ingestion/type_emergence.py`:

The `TypeEmergenceDetector`:
1. `check_type(type_uuid)` — checks if a type's variance exceeds threshold
2. If so, fetches all member embeddings from Milvus
3. Runs k-means (k=2) using numpy
4. Computes internal variance of each sub-cluster
5. If both sub-clusters have significantly lower variance than parent, returns a `SplitCandidate` with the two sub-cluster centroids and member lists
6. `execute_split(candidate, type_name_fn)` — calls `type_name_fn` (Hermes `/name-type`) with each sub-cluster's node names, creates new type_definitions, reassigns nodes

**Step 4: Run tests**

Run: `cd sophia && poetry run pytest tests/unit/ingestion/test_type_emergence.py -v`
Expected: All PASS

**Step 5: Commit**

```bash
git add src/sophia/ingestion/type_emergence.py tests/unit/ingestion/test_type_emergence.py
git commit -m "feat(sophia): add type emergence detection via variance monitoring and k-means"
```

---

## Phase 7: Hermes Deprecations

### Task 10: Mark Hermes type classification as deprecated

**Files:**
- Modify: `hermes/src/hermes/ner_provider.py:23-38,108-122`
- Test: existing tests should still pass (backward compat)

**Step 1: Add deprecation markers**

In `hermes/src/hermes/ner_provider.py`:

1. Add deprecation comment to `ONTOLOGY_TYPES` (line 21):
```python
# DEPRECATED: Sophia now owns type classification. These definitions are
# retained for backward compatibility — Sophia ignores the `type` field
# in proposals and classifies using embedding-space centroids.
# See: docs/plans/2026-02-25-sophia-driven-type-classification-design.md
ONTOLOGY_TYPES: dict[str, str] = { ... }
```

2. Add deprecation comment to `_SYSTEM_PROMPT` (line 108):
```python
# DEPRECATED: Type classification instructions are retained for backward
# compatibility but Sophia ignores the type field. Future: simplify this
# prompt to extract entity names and spans only.
_SYSTEM_PROMPT = ( ... )
```

3. Add deprecation comment to `SPACY_TO_ONTOLOGY` (line 41):
```python
# DEPRECATED: See ONTOLOGY_TYPES deprecation note above.
SPACY_TO_ONTOLOGY: dict[str, str] = { ... }
```

**Step 2: Run existing tests to verify backward compat**

Run: `cd hermes && poetry run pytest tests/ -v -k "ner or proposal"`
Expected: All PASS — no functional changes

**Step 3: Commit**

```bash
git add src/hermes/ner_provider.py
git commit -m "chore(hermes): deprecate type classification in favor of Sophia"
```

---

## Phase 8: Integration Testing

### Task 11: End-to-end integration test

**Files:**
- Create: `sophia/tests/integration/test_type_classification_e2e.py`

**Step 1: Write integration test**

```python
"""End-to-end test for Sophia-driven type classification.

Requires: Neo4j, Milvus, Hermes running.
"""

import pytest

from sophia.ingestion.proposal_processor import ProposalProcessor
from sophia.ingestion.type_classifier import TypeClassifier


@pytest.mark.integration
class TestTypeClassificationE2E:

    def test_entity_classified_by_sophia_not_hermes(
        self, hcg_client, milvus_sync
    ):
        """A proposed node with wrong Hermes type gets correctly classified."""
        processor = ProposalProcessor(
            hcg_client=hcg_client,
            milvus_sync=milvus_sync,
        )

        # Hermes says "state" but embedding is location-like
        proposal = {
            "proposal_id": "e2e-test-1",
            "source_service": "hermes",
            "confidence": 0.8,
            "raw_text": "Dublin is a city in Ireland",
            "proposed_nodes": [
                {
                    "name": "Dublin",
                    "type": "state",  # Wrong Hermes classification
                    "embedding": None,  # Will need real embedding from Hermes
                    "embedding_id": "emb-1",
                    "dimension": 384,
                    "model": "all-MiniLM-L6-v2",
                    "properties": {"start": 0, "end": 6},
                }
            ],
            "proposed_edges": [],
            "document_embedding": {
                "embedding": None,  # Will need real embedding
                "embedding_id": "doc-1",
                "dimension": 384,
                "model": "all-MiniLM-L6-v2",
            },
        }

        # TODO: Generate real embeddings via Hermes /embed_text
        # then verify the node gets classified as location, not state

    def test_type_emergence_after_many_insertions(
        self, hcg_client, milvus_sync
    ):
        """After inserting many temporal entities as 'state', emergence splits them."""
        # TODO: Insert ~20 temporal reference nodes and ~20 CWM state nodes,
        # verify variance threshold triggers split detection
        pass
```

**Step 2: Run (expects infrastructure)**

Run: `cd sophia && poetry run pytest tests/integration/test_type_classification_e2e.py -v -m integration`
Expected: Skip if infra not running, pass if it is

**Step 3: Commit**

```bash
git add tests/integration/test_type_classification_e2e.py
git commit -m "test(sophia): add e2e integration tests for type classification"
```

---

## Task Dependency Summary

```
Task 1 (TypeCentroid collection)
  └─> Task 2 (centroid methods)
        └─> Task 3 (TypeClassifier)
              └─> Task 4 (integrate into ProposalProcessor)
        └─> Task 5 (seed centroids)
  └─> Task 6 (RelationshipDiscoverer)
        └─> Task 8 (/name-relationship endpoint)
  └─> Task 9 (TypeEmergenceDetector)
        └─> Task 7 (/name-type endpoint)

Task 10 (deprecations) — independent, can run anytime
Task 11 (e2e tests) — after tasks 1-9
```

Tasks 6, 7, 8, 9 can proceed in parallel once Tasks 1-2 are done.
