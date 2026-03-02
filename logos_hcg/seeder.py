"""Shared HCG seeder for Project LOGOS.

Provides a complete type hierarchy, a rich demo scenario, and persona diary
entries that populate the graph for development, demos, and testing.

Can be used as a library (``HCGSeeder``) or from the command line::

    python -m logos_hcg.seeder --clear
    logos-seed-hcg --clear
"""

from __future__ import annotations

import argparse
import json
import logging
from collections.abc import Callable
from datetime import UTC, datetime, timedelta
from typing import TYPE_CHECKING, Any
from uuid import uuid4

from logos_hcg.client import HCGClient

if TYPE_CHECKING:
    from logos_hcg.sync import HCGMilvusSync

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Type hierarchy
# ---------------------------------------------------------------------------

# Hierarchy: node → {entity, concept, cognition, reserved_node}
# Domain types descend from entity; system-internal types from reserved_node.
#
# Types describe *what something IS*, not where it came from.  Provenance
# lives in ``source``/``derivation`` properties and graph connections.
TYPE_PARENTS: dict[str, str] = {
    # Intermediate types under node
    "entity": "node",
    "concept": "node",
    "cognition": "node",
    "reserved_node": "node",
    # Domain types under entity
    "object": "entity",
    "location": "entity",
    # System-internal types under reserved_node
    "reserved_agent": "reserved_node",  # Internal: Sophia as plan executor
    "reserved_process": "reserved_node",  # Internal: Sophia plan execution
    "reserved_action": "reserved_node",  # Internal: Sophia plan steps
    "reserved_goal": "reserved_node",  # Internal: Sophia planner goals
    "reserved_plan": "reserved_node",  # Internal: Sophia planner plans
    "reserved_simulation": "reserved_node",  # Internal: Sophia JEPA simulations
    "reserved_execution": "reserved_node",  # Internal: Sophia execution runs
    "reserved_state": "reserved_node",  # Internal: Sophia CWM states
    "reserved_media_sample": "reserved_node",  # Internal: Sophia media ingestion
}

# Edge type definitions to create as type-definition nodes.
EDGE_TYPES: list[str] = [
    "ENABLES",
    "ACHIEVES",
    "LOCATED_AT",
    "EXECUTES",
    "UPDATES",
    "REQUIRES",
    "CAUSES",
    "PRODUCES",
    "OBSERVES",
    "HAS_STATE",
    "PART_OF",
    "HAS_STEP",
    "GENERATES",
    "CONTAINS",
    "OCCUPIES",
]

# Types already created by core_ontology.cypher — skip to avoid duplicates.
BOOTSTRAP_TYPES: set[str] = {
    "type_definition",
    "node",
    "edge_type",
    "IS_A",
    "COMPONENT_OF",
}


# ---------------------------------------------------------------------------
# HCGSeeder
# ---------------------------------------------------------------------------


class HCGSeeder:
    """Seeds the HCG with type definitions, demo data, and persona entries."""

    def __init__(self, client: HCGClient) -> None:
        self.client = client

    # ------------------------------------------------------------------
    # clear
    # ------------------------------------------------------------------

    def clear(self) -> None:
        """Remove all data from the graph."""
        self.client.clear_all()

    # ------------------------------------------------------------------
    # type definitions
    # ------------------------------------------------------------------

    def seed_type_definitions(self) -> int:
        """Create type-definition nodes and IS_A edge nodes for the hierarchy.

        Each type gets a node and an IS_A reified edge to its immediate
        parent.  Bootstrap types (already in ``core_ontology.cypher``) are
        skipped for node creation but still get IS_A edges if the parent
        exists.

        Returns:
            Number of type-definition nodes created.
        """
        self.client.ensure_indexes()

        count = 0

        # Ensure the node parent exists so IS_A edges can reference it.
        # Normally created by core_ontology.cypher; in tests we create a stub.
        self.client.add_node(
            uuid="type_node",
            name="node",
            node_type="type_definition",
        )

        for type_name, parent_name in TYPE_PARENTS.items():
            if type_name in BOOTSTRAP_TYPES:
                continue

            # Create the type-definition node
            node_uuid = self.client.add_node(
                uuid=f"type_{type_name}",
                name=type_name,
                node_type="type_definition",
            )

            # Create IS_A edge to the immediate parent
            parent_uuid = f"type_{parent_name}"
            self.client.add_edge(
                source_uuid=node_uuid,
                target_uuid=parent_uuid,
                relation="IS_A",
            )
            count += 1

        # Ensure the edge_type bootstrap node exists (once, before the loop)
        self.client.add_node(
            uuid="type_edge_type",
            name="edge_type",
            node_type="type_definition",
        )

        for edge_name in EDGE_TYPES:
            if edge_name in BOOTSTRAP_TYPES:
                continue

            node_uuid = self.client.add_node(
                uuid=f"type_edge_{edge_name.lower()}",
                name=edge_name,
                node_type="edge_type",
            )

            # IS_A -> edge_type
            self.client.add_edge(
                source_uuid=node_uuid,
                target_uuid="type_edge_type",
                relation="IS_A",
            )
            count += 1

        logger.info("Seeded %d type definitions", count)
        return count

    # ------------------------------------------------------------------
    # type centroid embeddings
    # ------------------------------------------------------------------

    def seed_type_centroids(
        self,
        embed_fn: Callable[[str], list[float]],
        milvus_sync: HCGMilvusSync,
        model: str = "all-MiniLM-L6-v2",
    ) -> int:
        """Seed type centroid embeddings from type descriptions.

        For each type in ``TYPE_PARENTS``, creates a description string,
        embeds it via *embed_fn*, and upserts the centroid to Milvus.

        Args:
            embed_fn: Callable that takes a description string and returns
                an embedding vector.
            milvus_sync: An ``HCGMilvusSync`` instance (or compatible object)
                with an ``update_centroid`` method.
            model: Name of the embedding model used by *embed_fn*.

        Returns:
            Number of centroids seeded.
        """
        # Semantically distinct descriptions so centroids occupy different
        # regions of embedding space.  Each description captures *what the
        # type represents* rather than just its name.
        type_descriptions: dict[str, str] = {
            "object": (
                "A physical thing that can be grasped, moved, or manipulated. "
                "Examples: bolt, gear, cup, tool, box, sensor, bracket."
            ),
            "location": (
                "A named place, workspace, or spatial region where objects "
                "reside. Examples: table, shelf, bin, assembly station, tray."
            ),
            "reserved_agent": (
                "An autonomous actor that perceives, decides, and acts. "
                "The robot arm, a planner module, or Sophia itself."
            ),
            "reserved_process": (
                "An ongoing activity or workflow with a lifecycle. "
                "Assembly sequence, inspection routine, calibration procedure."
            ),
            "reserved_action": (
                "A single discrete step: pick, place, move, grasp, release, "
                "rotate, or inspect."
            ),
            "reserved_goal": (
                "A desired future state the planner tries to achieve. "
                "Object at target location, assembly complete, error resolved."
            ),
            "reserved_plan": (
                "An ordered sequence of actions chosen to reach a goal. "
                "Contains steps, preconditions, and expected outcomes."
            ),
            "reserved_simulation": (
                "A mental rehearsal predicting what will happen if a plan "
                "is executed. JEPA forward model evaluation."
            ),
            "reserved_execution": (
                "A concrete run of a plan on real or simulated hardware. "
                "Tracks progress, success, failure, and timing."
            ),
            "reserved_state": (
                "A snapshot of the world model at a point in time. "
                "Current positions, relationships, and beliefs."
            ),
            "reserved_media_sample": (
                "A media artifact ingested for processing: image, audio "
                "clip, video frame, or document."
            ),
        }

        count = 0
        for type_name in TYPE_PARENTS:
            description = type_descriptions.get(
                type_name, f"type definition for {type_name}"
            )
            embedding = embed_fn(description)
            milvus_sync.update_centroid(
                type_uuid=f"type_{type_name}",
                centroid=embedding,
                model=model,
            )
            count += 1

        logger.info("Seeded %d type centroid embeddings", count)
        return count

    # ------------------------------------------------------------------
    # demo scenario
    # ------------------------------------------------------------------

    def seed_demo_scenario(self) -> dict[str, str]:
        """Populate the graph with a rich Assembly Lab demo scenario.

        Creates ~30 nodes and ~40 edges covering workspaces, agents,
        objects, goals at different lifecycle stages, plans with steps,
        causal chains, and simulations.

        Returns:
            Mapping of logical name -> uuid for every created node.
        """
        ids: dict[str, str] = {}

        def _n(
            key: str,
            name: str,
            node_type: str,
            *,
            props: dict[str, Any] | None = None,
        ) -> str:
            """Helper -- create a node, record its uuid, add IS_A edge to type."""
            uuid = str(uuid4())
            self.client.add_node(
                uuid=uuid,
                name=name,
                node_type=node_type,
                properties=props,
            )
            # Create IS_A edge from instance to its type definition
            type_def_uuid = f"type_{node_type}"
            self.client.add_edge(
                source_uuid=uuid,
                target_uuid=type_def_uuid,
                relation="IS_A",
            )
            ids[key] = uuid
            return uuid

        def _e(src: str, tgt: str, rel: str, **kw: Any) -> None:
            self.client.add_edge(
                source_uuid=ids[src],
                target_uuid=ids[tgt],
                relation=rel,
                properties=kw or None,
            )

        # --- Workspace & zones (modelled as locations) ---
        _n(
            "ws",
            "Assembly Lab",
            "location",
            props={
                "description": "Main assembly workspace",
                "location_type": "workspace",
            },
        )
        _n(
            "zone_staging",
            "Staging Area",
            "location",
            props={"location_type": "zone", "zone_type": "staging"},
        )
        _n(
            "zone_assembly",
            "Assembly Station",
            "location",
            props={"location_type": "zone", "zone_type": "assembly"},
        )
        _n(
            "zone_inspection",
            "Inspection Bay",
            "location",
            props={"location_type": "zone", "zone_type": "inspection"},
        )
        _e("zone_staging", "ws", "PART_OF")
        _e("zone_assembly", "ws", "PART_OF")
        _e("zone_inspection", "ws", "PART_OF")

        # --- Agent + components ---
        _n(
            "agent",
            "LOGOS-01",
            "reserved_agent",
            props={"description": "Primary robotic agent"},
        )
        _n(
            "arm",
            "Panda Arm",
            "object",
            props={"model": "Franka Panda", "dof": 7, "object_type": "manipulator"},
        )
        _n(
            "cam",
            "Depth Camera",
            "object",
            props={
                "model": "Intel RealSense D435",
                "sensor_type": "rgbd",
                "object_type": "sensor",
            },
        )
        _e("arm", "agent", "PART_OF")
        _e("cam", "agent", "PART_OF")
        _e("agent", "zone_assembly", "LOCATED_AT")

        # --- Objects ---
        obj_defs = [
            ("red_cube", "Red Cube", "zone_staging", "red", "cube"),
            ("blue_cylinder", "Blue Cylinder", "zone_staging", "blue", "cylinder"),
            ("green_cube", "Green Cube", "zone_staging", "green", "cube"),
            ("yellow_sphere", "Yellow Sphere", "zone_assembly", "yellow", "sphere"),
            ("white_cube", "White Cube", "zone_assembly", "white", "cube"),
            ("black_prism", "Black Prism", "zone_inspection", "black", "prism"),
        ]
        for key, name, zone, color, shape in obj_defs:
            _n(key, name, "object", props={"color": color, "shape": shape})
            _e(key, zone, "LOCATED_AT")

        # =================================================================
        # Goal 1 — Sort by Color (completed)
        # =================================================================
        _n(
            "goal_sort",
            "Sort Objects by Color",
            "reserved_goal",
            props={
                "status": "completed",
                "priority": 1,
                "description": "Move all red and green cubes to staging area",
            },
        )

        _n(
            "plan_sort",
            "Color Sort Plan",
            "reserved_plan",
            props={"status": "completed", "goal_id": ids["goal_sort"]},
        )
        _e("plan_sort", "goal_sort", "ACHIEVES")

        sort_steps = [
            ("sort_s1", "Scan staging area", "completed"),
            ("sort_s2", "Pick red cube", "completed"),
            ("sort_s3", "Place red cube in staging", "completed"),
            ("sort_s4", "Pick green cube", "completed"),
            ("sort_s5", "Place green cube in staging", "completed"),
        ]
        prev_step = None
        for key, name, status in sort_steps:
            _n(
                key,
                name,
                "reserved_action",
                props={"status": status, "order": int(key[-1])},
            )
            _e("plan_sort", key, "HAS_STEP")
            if prev_step:
                _e(prev_step, key, "ENABLES")
            prev_step = key

        # =================================================================
        # Goal 2 — Assemble Stack (active, with a prior failed plan)
        # =================================================================
        _n(
            "goal_stack",
            "Assemble Cube Stack",
            "reserved_goal",
            props={
                "status": "active",
                "priority": 2,
                "description": "Stack white, red, and green cubes at assembly station",
            },
        )

        # Failed plan attempt
        _n(
            "plan_stack_v1",
            "Stack Plan v1 (failed)",
            "reserved_plan",
            props={
                "status": "failed",
                "goal_id": ids["goal_stack"],
                "failure_reason": "Grasp slip on white cube",
            },
        )
        _e("plan_stack_v1", "goal_stack", "ACHIEVES")

        # Active plan
        _n(
            "plan_stack_v2",
            "Stack Plan v2",
            "reserved_plan",
            props={"status": "executing", "goal_id": ids["goal_stack"]},
        )
        _e("plan_stack_v2", "goal_stack", "ACHIEVES")

        stack_steps = [
            ("stack_s1", "Move to white cube", "completed"),
            ("stack_s2", "Place white cube base", "completed"),
            ("stack_s3", "Pick red cube", "in_progress"),
            ("stack_s4", "Stack red on white", "pending"),
            ("stack_s5", "Stack green on red", "pending"),
        ]
        prev_step = None
        for key, name, status in stack_steps:
            _n(
                key,
                name,
                "reserved_action",
                props={"status": status, "order": int(key[-1])},
            )
            _e("plan_stack_v2", key, "HAS_STEP")
            if prev_step:
                _e(prev_step, key, "ENABLES")
            prev_step = key

        # Causal chain for active execution
        _e("agent", "stack_s3", "EXECUTES")
        _e("stack_s3", "red_cube", "UPDATES")

        # =================================================================
        # Goal 3 — Clear Workspace (pending, with simulation)
        # =================================================================
        _n(
            "goal_clear",
            "Clear Workspace",
            "reserved_goal",
            props={
                "status": "pending",
                "priority": 3,
                "description": "Move all objects to inspection bay",
            },
        )

        _n(
            "sim_clear",
            "Clearance Simulation",
            "reserved_simulation",
            props={"description": "Simulated workspace clearance", "confidence": 0.78},
        )
        _e("sim_clear", "goal_clear", "GENERATES")

        # Imagined states / processes within the simulation
        _n(
            "ip_move_all",
            "Move all to inspection",
            "reserved_process",
            props={"description": "Simulated batch move", "derivation": "imagined"},
        )
        _n(
            "is_empty_ws",
            "Empty workspace state",
            "reserved_state",
            props={
                "description": "All objects in inspection bay",
                "derivation": "imagined",
            },
        )
        _e("sim_clear", "ip_move_all", "HAS_STEP")
        _e("ip_move_all", "is_empty_ws", "CAUSES")

        # =================================================================
        # Cross-cutting edges
        # =================================================================
        _e("agent", "arm", "EXECUTES")
        _e("cam", "zone_assembly", "OBSERVES")
        _e("cam", "zone_staging", "OBSERVES")

        # Capability (modelled as a process the agent can execute)
        _n(
            "cap_pick",
            "Pick-and-Place",
            "reserved_process",
            props={
                "description": "Grasping and placing objects",
                "executor_type": "manipulator",
                "process_type": "capability",
            },
        )
        _e("arm", "cap_pick", "HAS_STATE")

        logger.info(
            "Seeded demo scenario: %d nodes, workspace=%s",
            len(ids),
            ids["ws"],
        )
        return ids

    # ------------------------------------------------------------------
    # Apollo-compatible Plan nodes (:Plan label)
    # ------------------------------------------------------------------

    def seed_plan_nodes(self, scenario_ids: dict[str, str]) -> list[str]:
        """Create :Plan labelled nodes that Apollo's /api/hcg/plans reads.

        Apollo queries ``MATCH (p:Plan)`` so we need the :Plan label
        in addition to (or instead of) :Node.

        Returns:
            List of plan node IDs.
        """
        now = datetime.now(UTC)
        plan_ids: list[str] = []

        plans = [
            {
                "id": f"plan-sort-{uuid4().hex[:8]}",
                "goal_id": scenario_ids.get("goal_sort", "goal_sort"),
                "status": "completed",
                "steps": json.dumps(
                    [
                        {"id": "1", "name": "Scan staging area", "status": "completed"},
                        {"id": "2", "name": "Pick red cube", "status": "completed"},
                        {
                            "id": "3",
                            "name": "Place red cube in staging",
                            "status": "completed",
                        },
                        {"id": "4", "name": "Pick green cube", "status": "completed"},
                        {
                            "id": "5",
                            "name": "Place green cube in staging",
                            "status": "completed",
                        },
                    ]
                ),
                "created_at": (now - timedelta(hours=2)).isoformat(),
                "completed_at": (now - timedelta(hours=1, minutes=30)).isoformat(),
            },
            {
                "id": f"plan-stack-v1-{uuid4().hex[:8]}",
                "goal_id": scenario_ids.get("goal_stack", "goal_stack"),
                "status": "failed",
                "steps": json.dumps(
                    [
                        {
                            "id": "1",
                            "name": "Move to white cube",
                            "status": "completed",
                        },
                        {
                            "id": "2",
                            "name": "Place white cube base",
                            "status": "failed",
                        },
                    ]
                ),
                "created_at": (now - timedelta(hours=1)).isoformat(),
                "completed_at": (now - timedelta(minutes=50)).isoformat(),
                "result": json.dumps({"error": "Grasp slip on white cube"}),
            },
            {
                "id": f"plan-stack-v2-{uuid4().hex[:8]}",
                "goal_id": scenario_ids.get("goal_stack", "goal_stack"),
                "status": "executing",
                "steps": json.dumps(
                    [
                        {
                            "id": "1",
                            "name": "Move to white cube",
                            "status": "completed",
                        },
                        {
                            "id": "2",
                            "name": "Place white cube base",
                            "status": "completed",
                        },
                        {"id": "3", "name": "Pick red cube", "status": "in_progress"},
                        {"id": "4", "name": "Stack red on white", "status": "pending"},
                        {"id": "5", "name": "Stack green on red", "status": "pending"},
                    ]
                ),
                "created_at": (now - timedelta(minutes=30)).isoformat(),
                "started_at": (now - timedelta(minutes=25)).isoformat(),
            },
        ]

        for plan in plans:
            query = """
            CREATE (p:Plan {
                id: $id,
                goal_id: $goal_id,
                status: $status,
                steps: $steps,
                created_at: $created_at,
                started_at: $started_at,
                completed_at: $completed_at,
                result: $result
            })
            RETURN p
            """
            self.client._execute_query(
                query,
                {
                    "id": plan["id"],
                    "goal_id": plan["goal_id"],
                    "status": plan["status"],
                    "steps": plan["steps"],
                    "created_at": plan.get("created_at", now.isoformat()),
                    "started_at": plan.get("started_at"),
                    "completed_at": plan.get("completed_at"),
                    "result": plan.get("result"),
                },
            )
            plan_ids.append(plan["id"])

        logger.info("Seeded %d Apollo Plan nodes", len(plan_ids))
        return plan_ids

    # ------------------------------------------------------------------
    # persona diary
    # ------------------------------------------------------------------

    def seed_persona_diary(self) -> list[str]:
        """Create persona diary entries as CWM-E state nodes.

        Persona entries are stored as :Node with type="reserved_state" and
        tags ["cwm", "subsystem:cwm_e"].  The entry data lives in the
        JSON ``payload`` field under the ``entry`` key, which is the format
        Sophia's ``_cwmstate_to_persona_entry`` expects.

        Returns:
            List of entry IDs created.
        """
        now = datetime.now(UTC)
        entry_ids: list[str] = []

        entries: list[dict[str, Any]] = [
            {
                "entry_type": "observation",
                "content": (
                    "I notice the Assembly Lab workspace has six objects "
                    "distributed across three zones. The staging area holds "
                    "a red cube, blue cylinder, and green cube. The assembly "
                    "station has a yellow sphere and white cube. A black prism "
                    "sits alone in the inspection bay."
                ),
                "summary": "Surveyed workspace \u2014 6 objects across 3 zones",
                "sentiment": "neutral",
                "confidence": 0.92,
                "emotion_tags": ["curiosity", "readiness"],
                "related_process_ids": [],
                "related_goal_ids": [],
            },
            {
                "entry_type": "belief",
                "content": (
                    "Based on the object layout, the color-sorting goal should "
                    "be straightforward. Red and green cubes are already in the "
                    "staging area. I am confident the pick-and-place primitives "
                    "are sufficient for this task."
                ),
                "summary": "Colour-sort task looks achievable",
                "sentiment": "positive",
                "confidence": 0.88,
                "emotion_tags": ["confidence", "analysis"],
                "related_process_ids": [],
                "related_goal_ids": [],
            },
            {
                "entry_type": "decision",
                "content": (
                    "I will prioritise the colour-sort goal first because it "
                    "requires the fewest moves and will free staging-area space "
                    "for later stacking operations."
                ),
                "summary": "Prioritised colour-sort as first goal",
                "sentiment": "positive",
                "confidence": 0.80,
                "emotion_tags": ["determination", "planning"],
                "related_process_ids": [],
                "related_goal_ids": [],
            },
            {
                "entry_type": "reflection",
                "content": (
                    "Colour-sort plan completed successfully \u2014 all five steps "
                    "executed without error. Execution was 15%% faster than the "
                    "simulated estimate. My grasp accuracy seems to be improving."
                ),
                "summary": "Colour-sort plan completed ahead of estimate",
                "sentiment": "positive",
                "confidence": 0.90,
                "emotion_tags": ["satisfaction", "confidence"],
                "related_process_ids": [],
                "related_goal_ids": [],
            },
            {
                "entry_type": "observation",
                "content": (
                    "The white cube surface is smoother than expected. During "
                    "the first stacking attempt the gripper slipped after lift. "
                    "Force-torque readings spiked 40%% above baseline."
                ),
                "summary": "Detected grasp-slip on white cube",
                "sentiment": "negative",
                "confidence": 0.95,
                "emotion_tags": ["surprise", "caution"],
                "related_process_ids": [],
                "related_goal_ids": [],
            },
            {
                "entry_type": "decision",
                "content": (
                    "Switching to a tighter grasp profile for the white cube. "
                    "I will increase gripper force by 20%% and reduce approach "
                    "velocity to compensate for the smooth surface."
                ),
                "summary": "Adjusted grasp parameters for white cube",
                "sentiment": "neutral",
                "confidence": 0.75,
                "emotion_tags": ["adaptation", "caution"],
                "related_process_ids": [],
                "related_goal_ids": [],
            },
            {
                "entry_type": "belief",
                "content": (
                    "With the adjusted parameters, stacking success probability "
                    "is now approximately 0.85. The workspace clearance goal "
                    "should remain feasible once stacking completes."
                ),
                "summary": "Revised stacking success probability to 0.85",
                "sentiment": "positive",
                "confidence": 0.82,
                "emotion_tags": ["analysis", "hope"],
                "related_process_ids": [],
                "related_goal_ids": [],
            },
            {
                "entry_type": "reflection",
                "content": (
                    "Overall I feel more capable than at the start of this "
                    "session. Handling the grasp failure gracefully reinforced "
                    "my ability to adapt. I should log surface-texture data "
                    "for future reference."
                ),
                "summary": "Grew more confident through adaptive recovery",
                "sentiment": "positive",
                "confidence": 0.87,
                "emotion_tags": ["growth", "confidence", "reflection"],
                "related_process_ids": [],
                "related_goal_ids": [],
            },
        ]

        from logos_hcg.queries import HCGQueries

        query = HCGQueries.create_cwm_state()

        for i, entry_data in enumerate(entries):
            entry_id = f"persona-{uuid4().hex[:12]}"
            ts = now - timedelta(minutes=len(entries) - i)

            payload = json.dumps(
                {
                    "entry": {
                        "entry_id": entry_id,
                        "entry_type": entry_data["entry_type"],
                        "content": entry_data["content"],
                        "summary": entry_data["summary"],
                        "sentiment": entry_data["sentiment"],
                        "confidence": entry_data["confidence"],
                        "emotion_tags": entry_data["emotion_tags"],
                        "related_process_ids": entry_data["related_process_ids"],
                        "related_goal_ids": entry_data["related_goal_ids"],
                        "metadata": {},
                    }
                }
            )

            self.client._execute_query(
                query,
                {
                    "uuid": entry_id,
                    "name": f"cwm_e_{ts.strftime('%Y%m%d_%H%M%S')}",
                    "type": "reserved_state",
                    "timestamp": ts.isoformat(),
                    "source": "seeder",
                    "confidence": entry_data["confidence"],
                    "status": "observed",
                    "payload": payload,
                    "links": "{}",
                    "tags": ["cwm", "subsystem:cwm_e"],
                    "embedding_id": None,
                    "embedding_type": None,
                },
            )
            entry_ids.append(entry_id)

        logger.info("Seeded %d persona diary entries", len(entry_ids))
        return entry_ids

    # ------------------------------------------------------------------
    # convenience
    # ------------------------------------------------------------------

    def seed_all(self) -> dict[str, Any]:
        """Run the full seed sequence: clear + ontology + demo + plans + persona.

        Returns:
            Dict with keys ``type_count``, ``scenario_ids``, ``plan_ids``,
            ``persona_entry_ids``.
        """
        self.clear()
        type_count = self.seed_type_definitions()
        scenario_ids = self.seed_demo_scenario()
        plan_ids = self.seed_plan_nodes(scenario_ids)
        persona_ids = self.seed_persona_diary()
        logger.info(
            "Full seed complete: %d types, %d scenario nodes, "
            "%d plans, %d persona entries",
            type_count,
            len(scenario_ids),
            len(plan_ids),
            len(persona_ids),
        )
        return {
            "type_count": type_count,
            "scenario_ids": scenario_ids,
            "plan_ids": plan_ids,
            "persona_entry_ids": persona_ids,
        }


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main(argv: list[str] | None = None) -> None:
    """Command-line entry point for seeding the HCG."""
    parser = argparse.ArgumentParser(
        description="Seed the LOGOS HCG with type definitions and demo data.",
    )
    parser.add_argument(
        "--uri",
        default="bolt://localhost:7687",
        help="Neo4j bolt URI (default: bolt://localhost:7687)",
    )
    parser.add_argument("--user", default="neo4j", help="Neo4j user")
    parser.add_argument("--password", default="logosdev", help="Neo4j password")
    parser.add_argument(
        "--clear",
        action="store_true",
        help="Clear existing data before seeding",
    )
    parser.add_argument(
        "--ontology-only",
        action="store_true",
        help="Only seed type definitions (no demo data or persona entries)",
    )
    args = parser.parse_args(argv)

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )

    client = HCGClient(uri=args.uri, user=args.user, password=args.password)
    try:
        seeder = HCGSeeder(client)
        if args.clear:
            seeder.clear()
        if args.ontology_only:
            seeder.seed_type_definitions()
        else:
            seeder.seed_type_definitions()
            scenario_ids = seeder.seed_demo_scenario()
            seeder.seed_plan_nodes(scenario_ids)
            seeder.seed_persona_diary()
        logger.info("Done.")
    finally:
        client.close()


if __name__ == "__main__":
    main()
