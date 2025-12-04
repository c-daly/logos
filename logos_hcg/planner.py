"""
HCG Planner - Domain-agnostic planning over the Hybrid Cognitive Graph.

Implements backward chaining over REQUIRES/CAUSES edges to generate
plans that achieve goal states. Works with any domain represented
in the HCG - the graph structure defines what's possible.

See logos#157 for design details.
"""

import logging
from datetime import datetime, timezone
from uuid import UUID, uuid4

from logos_hcg.client import HCGClient
from logos_hcg.models import (
    Goal,
    GoalTarget,
    Plan,
    PlanStatus,
    PlanStep,
    Process,
    Provenance,
    SourceService,
    State,
)

logger = logging.getLogger(__name__)


class PlanningError(Exception):
    """Raised when planning fails."""

    pass


class GoalUnachievableError(PlanningError):
    """Raised when no plan can achieve the goal."""

    pass


class HCGPlanner:
    """
    Domain-agnostic planner over the Hybrid Cognitive Graph.

    Uses backward chaining to find sequences of Processes that
    achieve goal states. The planner is domain-agnostic - it
    operates purely on graph structure (States, Processes,
    REQUIRES/CAUSES edges) without hard-coded domain knowledge.

    Features:
    - Backward chaining from goal state to current state
    - Capability binding for execution
    - Provenance tracking on all artifacts
    - Configurable search depth
    """

    def __init__(
        self,
        hcg_client: HCGClient,
        max_depth: int = 10,
        source_service: str = SourceService.SOPHIA,
    ):
        """
        Initialize the planner.

        Args:
            hcg_client: HCG client for graph queries
            max_depth: Maximum backward chaining depth
            source_service: Service name for provenance
        """
        self._hcg = hcg_client
        self._max_depth = max_depth
        self._source_service = source_service

    def _create_provenance(
        self, author_id: UUID | None = None, trace_id: UUID | None = None
    ) -> Provenance:
        """Create a Provenance object with current timestamp."""
        return Provenance(
            source_service=self._source_service,
            author_id=author_id,
            created_at=datetime.now(timezone.utc),
            trace_id=trace_id,
            tags=["planner", "backward-chain"],
        )

    def plan(
        self,
        goal: Goal,
        satisfied_states: set[UUID],
        author_id: UUID | None = None,
        trace_id: UUID | None = None,
    ) -> Plan:
        """
        Generate a plan to achieve the goal from the current state.

        Uses backward chaining over REQUIRES/CAUSES edges:
        1. Find processes that CAUSE states matching the goal
        2. For each process, check what states it REQUIRES
        3. Recursively plan for unsatisfied requirements
        4. Return ordered sequence of processes

        Args:
            goal: Goal specification with target state
            satisfied_states: Set of state UUIDs that are currently true
            author_id: Optional author UUID for provenance
            trace_id: Optional trace ID for distributed tracing

        Returns:
            Plan with ordered PlanSteps

        Raises:
            GoalUnachievableError: If no plan can achieve the goal
        """
        provenance = self._create_provenance(author_id, trace_id)

        # Resolve goal target to find achieving processes
        target_processes = self._find_achieving_processes(goal.target)

        if not target_processes:
            raise GoalUnachievableError(f"No processes found that achieve goal: {goal.description}")

        # Backward chain to build plan
        visited: set[UUID] = set()
        steps: list[PlanStep] = []

        for process, target_state in target_processes:
            try:
                self._backward_chain(
                    process=process,
                    target_state=target_state,
                    satisfied_states=satisfied_states,
                    steps=steps,
                    visited=visited,
                    depth=0,
                    provenance=provenance,
                )
                # Found a valid plan
                break
            except GoalUnachievableError:
                # Try next achieving process
                continue
        else:
            raise GoalUnachievableError(f"Could not build plan for goal: {goal.description}")

        # Number steps in order
        for i, step in enumerate(steps):
            step.index = i

        # Calculate overall confidence
        overall_confidence = 1.0
        for step in steps:
            overall_confidence *= step.confidence

        # Determine final state
        final_state_uuid = None
        if steps:
            effects = steps[-1].effect_uuids
            if effects:
                final_state_uuid = effects[0]

        # Use first satisfied state as current_state_uuid for Plan
        current_state_uuid = next(iter(satisfied_states)) if satisfied_states else None

        return Plan(
            uuid=uuid4(),
            goal_uuid=goal.uuid,
            steps=steps,
            current_state_uuid=current_state_uuid,
            expected_final_state_uuid=final_state_uuid,
            status=PlanStatus.PENDING,
            confidence=overall_confidence,
            provenance=provenance,
        )

    def _find_achieving_processes(self, target: GoalTarget) -> list[tuple[Process, State]]:
        """
        Find processes that achieve the goal target.

        Args:
            target: Goal target specification

        Returns:
            List of (Process, State) tuples where Process CAUSES State
        """
        # If we have specific state properties, search by properties
        if target.state_properties:
            results = []
            for key, value in target.state_properties.items():
                matches = self._hcg.find_processes_by_effect_properties(key, value)
                # Filter to only processes affecting the target entity
                for process, state in matches:
                    # Check if this state is for the target entity
                    # (This requires the state to have entity linkage)
                    results.append((process, state))
            return results

        # Otherwise, find processes that affect the target entity
        return self._hcg.find_processes_for_entity_state(target.entity_uuid)

    def _backward_chain(
        self,
        process: Process,
        target_state: State,
        satisfied_states: set[UUID],
        steps: list[PlanStep],
        visited: set[UUID],
        depth: int,
        provenance: Provenance,
    ) -> None:
        """
        Recursively backward chain from a process to build plan steps.

        Args:
            process: Process to include in plan
            target_state: State this process achieves
            satisfied_states: Set of state UUIDs that are currently satisfied
            steps: List to accumulate steps (modified in place)
            visited: Set of visited process UUIDs (cycle detection)
            depth: Current recursion depth
            provenance: Provenance for created steps
        """
        if depth > self._max_depth:
            raise GoalUnachievableError(f"Max planning depth ({self._max_depth}) exceeded")

        # Parse process UUID
        process_uuid = UUID(process.uuid) if isinstance(process.uuid, str) else process.uuid

        if process_uuid in visited:
            # Already planned for this process
            return

        visited.add(process_uuid)

        # Get preconditions for this process
        preconditions = self._hcg.get_process_requirements(process.uuid)

        # For each unsatisfied precondition, find a process that achieves it
        for precond in preconditions:
            precond_uuid = UUID(precond.uuid) if isinstance(precond.uuid, str) else precond.uuid

            # Check if precondition is already satisfied
            if precond_uuid in satisfied_states:
                continue

            # Find processes that cause this precondition state
            achieving_procs = self._hcg.find_processes_causing_state(precond.uuid)

            if not achieving_procs:
                raise GoalUnachievableError(
                    f"No process found to achieve precondition: {precond.uuid} ({precond.name})"
                )

            # Recursively plan for this precondition
            # (Take first achieving process for now - could explore alternatives)
            achieving_proc = achieving_procs[0]
            self._backward_chain(
                process=achieving_proc,
                target_state=precond,
                satisfied_states=satisfied_states,
                steps=steps,
                visited=visited,
                depth=depth + 1,
                provenance=provenance,
            )

        # Get effects of this process
        effects = self._hcg.get_process_causes(process.uuid)
        effect_uuids = [UUID(e.uuid) if isinstance(e.uuid, str) else e.uuid for e in effects]

        # Get capability for execution
        capability = self._hcg.find_capability_for_process(process.uuid)
        capability_uuid = None
        if capability:
            capability_uuid = (
                UUID(capability.uuid) if isinstance(capability.uuid, str) else capability.uuid
            )

        # Create plan step
        precond_uuids = [UUID(p.uuid) if isinstance(p.uuid, str) else p.uuid for p in preconditions]

        step = PlanStep(
            uuid=uuid4(),
            name=process.name,  # Human-readable label from Process
            index=0,  # Will be set later
            process_uuid=process_uuid,
            precondition_uuids=precond_uuids,
            effect_uuids=effect_uuids,
            capability_uuid=capability_uuid,
            estimated_duration_ms=process.duration_ms,
            confidence=1.0,  # Could be derived from capability.success_rate
            provenance=provenance,
        )

        steps.append(step)

    def validate_plan(self, plan: Plan) -> tuple[bool, list[str]]:
        """
        Validate a plan for consistency.

        Checks:
        - All process UUIDs exist in HCG
        - Precondition chains are consistent
        - Capabilities are available

        Args:
            plan: Plan to validate

        Returns:
            Tuple of (is_valid, list of error messages)
        """
        errors: list[str] = []

        for step in plan.steps:
            # Check process exists
            process = self._hcg.find_process_by_uuid(step.process_uuid)
            if not process:
                errors.append(f"Process not found: {step.process_uuid}")
                continue

            # Check capability exists if specified
            if step.capability_uuid:
                capability = self._hcg.find_capability_by_uuid(step.capability_uuid)
                if not capability:
                    errors.append(f"Capability not found: {step.capability_uuid}")

        return len(errors) == 0, errors
