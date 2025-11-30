# Phase 3 Specification — Learning & Memory Systems

Phase 3 builds on the Phase 2 foundation to deliver adaptive, learning-capable agent behavior through memory systems, event-driven reflection, and episodic learning. This phase transforms LOGOS from a reactive system into one that learns from experience and develops a persistent personality.

## Goals
1. **Short-term Memory** — Implement session-scoped ephemeral memory for conversational context and transient reasoning
2. **Event-driven Reflection** — Create intelligent, selective diary entries based on significant events rather than every interaction
3. **Selective Diary Entries** — Replace per-turn observation logging with meaningful, curated persona history
4. **Episodic Memory** — Enable the agent to learn from execution history and improve plan quality over time
5. **Probabilistic Validation** — Layer Level 2 validation to complement SHACL constraints with uncertainty reasoning

## Milestones

### P3-M1: Short-term Memory Infrastructure

**Objective**: Implement session-scoped ephemeral memory that serves as working context for all agent subsystems.

**Deliverables**:
- **Storage backend**: Redis or in-memory store with TTL support for ephemeral `CWMState` entries
- **API endpoints**: 
  - `POST /api/memory/ephemeral` - Create ephemeral entry
  - `GET /api/memory/ephemeral` - Query recent entries (by type, time window, session)
  - `DELETE /api/memory/ephemeral/{id}` - Explicit deletion
  - `POST /api/memory/promote/{id}` - Promote ephemeral entry to persistent HCG
- **Session management**: Track session lifecycle, automatic expiration, cleanup
- **CWMState envelope**: All ephemeral entries use `status="ephemeral"` in unified contract
- **Promotion policies**: Configurable rules for what gets persisted (logged for auditability)

**Use cases**:
- Conversational context (current topic, pending clarifications, in-progress reasoning)
- Recent perceptual observations (last N frames, sensor readings)
- Error tracking (retry attempts, backoff state)
- User preferences (session-specific settings, temporary constraints)
- Capability execution state (multi-step operation progress)
- Curiosity flags (unknowns to investigate, ambiguities to resolve)

**Success criteria**:
- Short-term memory API functional and integrated
- At least 3 subsystems (planner, reflection, LLM chat) consume ephemeral memory
- Promotion policies demonstrated (manual and automatic)
- Session cleanup verified (no memory leaks)

---

### P3-M2: Event-driven Reflection System

**Objective**: Implement intelligent reflection triggers that create meaningful diary entries based on significant events, not time intervals.

**Deliverables**:
- **Reflection triggers** (event-based hooks):
  - `error` - Plan execution failures, validation errors, capability failures
  - `user_request` - Explicit instructions to change behavior, tone, or approach
  - `correction` - User corrects agent's understanding or actions
  - `session_boundary` - Conversation start (load context) / end (consolidate learnings)
  - `milestone` - Goal completion, significant progress, new capability
- **LLM-powered reflection prompts**: Analyze short-term memory and recent context to generate introspective reflections
- **Reflection entry creation**: Create `PersonaEntry` with `entry_type="reflection"` and appropriate `trigger` value
- **Context analysis**: Reflection system reads:
  - Short-term memory (recent conversation, errors, user signals)
  - Recent `PersonaEntry` nodes (prior reflections, observations)
  - Plan/process outcomes (success/failure patterns)
- **EmotionState generation**: Reflection output includes emotional assessment (confidence, caution, sentiment) stored as `EmotionState` nodes

**Reflection content examples**:
- "User corrected my assumption about X three times - need to ask clarifying questions earlier"
- "Navigation tasks succeeding consistently - increasing confidence in spatial reasoning"
- "Verbose explanations triggered frustration - adjusting default communication style"
- "Missed obvious validation step leading to error - adding to standard procedure"

**Success criteria**:
- Reflections triggered by events, not periodic timers
- Reflection quality assessed by stakeholders (meaningful insights)
- Planner demonstrates behavior adjustment based on reflection content
- EmotionState nodes influence persona tone in LLM responses

---

### P3-M3: Selective Diary Entry Creation

**Objective**: Replace automatic per-turn observations with selective, meaningful diary entries based on impact criteria.

**Deliverables**:
- **Entry creation criteria**:
  - **Impact**: Does this change how agent should behave going forward?
  - **Reusability**: Will this context matter in future sessions?
  - **Learning value**: Is there a lesson or pattern to extract?
  - **User signal**: Did user explicitly indicate importance?
- **Automatic triggers for observations**:
  - Context shift (topic/domain change, new user information, environment change)
  - Novel information (user preferences, constraints, facts not in HCG)
  - Ambiguity resolution (clarifications that change understanding)
  - Significant interactions (exchanges that materially advance goals)
- **Short-term memory promotion**: Criteria for elevating ephemeral entries to persistent diary
- **Diary query optimization**: Index and query patterns for retrieving relevant historical context
- **Backward compatibility**: Existing observation-heavy workflows can opt into new selective behavior

**What does NOT create diary entries**:
- Individual chat messages (stay in short-term memory)
- Temporary state (current discussion topic)
- Pending clarifications
- In-progress reasoning chains

**Success criteria**:
- Diary entry volume reduced significantly (measured against Phase 2 baseline)
- Diary query relevance improved (stakeholder assessment)
- Short-term memory serves as working context without diary pollution
- Critical information still captured (no loss of important context)

---

### P3-M4: Episodic Memory & Learning

**Objective**: Enable the agent to learn from execution history and improve plan quality over time.

**Deliverables**:
- **Episodic storage**: HCG schema for recording execution episodes (plan → actions → outcomes)
- **Episode indexing**: Link episodes to goals, capabilities, contexts for retrieval
- **Learning from outcomes**: Analyze success/failure patterns across episodes
- **Plan quality improvement**: Planner queries relevant episodes before generating new plans
- **Probabilistic validation (Level 2)**: Augment SHACL with uncertainty-based validation using learned patterns
- **Capability confidence**: Track per-capability success rates, adjust planning accordingly
- **Context-sensitive learning**: Different strategies for different domains/users

**Episode structure**:
```
Episode {
  id, timestamp, goal, plan_id,
  actions: [{ capability, params, result, confidence }],
  outcome: { success, failure_reason, duration },
  context: { user, environment, constraints },
  reflections: [related PersonaEntry IDs],
  learned: { patterns, adjustments, recommendations }
}
```

**Success criteria**:
- Plan quality measurably improves over repeated similar goals
- Probabilistic validation catches issues SHACL misses
- Capability selection adapts based on historical success rates
- Agent demonstrates learning without explicit retraining

---

## Implementation Notes

### Short-term Memory Architecture
- **Storage**: Redis with session-scoped keyspaces (`session:{id}:memory:*`)
- **TTL**: Configurable per entry type (default: 1 hour for conversation, 15 minutes for perception)
- **Promotion**: Manual API calls or automatic policy engine (rule-based or LLM-assisted)
- **Integration**: All Phase 2 services (Sophia, Hermes, Apollo) consume memory API

### Reflection System Architecture
- **Trigger detection**: Event handlers in Sophia (plan execution), Apollo (user interaction), CWM-E (error monitoring)
- **Reflection LLM**: Separate prompt template for introspection, distinct from chat/planning prompts
- **Context window**: Last N ephemeral entries + recent diary entries + current plan state
- **Output format**: Structured reflection (trigger, insight, recommendation, confidence) → PersonaEntry

### Diary Entry Decision Logic
- **Decision point**: Before creating any PersonaEntry, evaluate impact criteria
- **LLM-assisted**: Use small classifier or prompt to determine "meaningful Y/N"
- **Override**: Manual diary commands always create entries (stakeholder discretion)
- **Audit trail**: Log all "rejected" entry attempts for tuning criteria

### Episodic Learning Flow
1. Plan execution completes (success or failure)
2. Create Episode record with full trace
3. Link to related PersonaEntry reflections
4. Index by goal type, capabilities, context
5. Future plans query similar episodes
6. Adjust confidence, strategy, capability selection

---

## Dependencies

- **Phase 2 completion**: Sophia/Hermes services, Apollo surfaces, PersonaEntry with `trigger` field, basic CWM-E
- **Redis instance**: For ephemeral memory (or alternative key-value store)
- **LLM access**: For reflection prompts and decision logic
- **Neo4j schema updates**: Episode storage, memory indexing
- **Observability**: Track memory usage, promotion rates, reflection quality

---

## Verification & Success Criteria

### M1 - Short-term Memory
- [ ] Redis backend operational with TTL
- [ ] API endpoints functional (create, query, promote, delete)
- [ ] Session management with automatic cleanup
- [ ] 3+ subsystems consuming memory API
- [ ] Promotion policies demonstrated
- [ ] Load test: 100 concurrent sessions, no memory leaks

### M2 - Event-driven Reflection
- [ ] 5+ trigger types implemented (error, user_request, correction, session_boundary, milestone)
- [ ] LLM reflection prompts generate meaningful insights (stakeholder review)
- [ ] Reflections create PersonaEntry nodes correctly
- [ ] EmotionState nodes linked to reflections
- [ ] Planner demonstrates behavior change from reflection content
- [ ] No periodic reflection jobs (all event-driven)

### M3 - Selective Diary Entries
- [ ] Impact criteria documented and implemented
- [ ] Per-turn observation creation disabled by default
- [ ] Diary entry volume reduced >70% vs Phase 2
- [ ] Stakeholder assessment: diary relevance improved
- [ ] Short-term memory serves working context
- [ ] Critical information capture validated (no regressions)

### M4 - Episodic Learning
- [ ] Episode schema in HCG, CRUD operations functional
- [ ] Episode indexing by goal/capability/context
- [ ] Planner queries episodes before plan generation
- [ ] Demonstrated improvement: 2nd attempt at repeated goal succeeds faster
- [ ] Probabilistic validation catches uncertain plans
- [ ] Capability confidence scores adjust based on outcomes

---

## Phase 3 Roadmap

**Timeline**: Estimated 8-12 weeks

| Milestone | Duration | Dependencies |
|-----------|----------|--------------|
| P3-M1 (Short-term memory) | 2-3 weeks | Phase 2 complete |
| P3-M2 (Event-driven reflection) | 3-4 weeks | P3-M1 complete |
| P3-M3 (Selective diary) | 2-3 weeks | P3-M1, P3-M2 complete |
| P3-M4 (Episodic learning) | 3-4 weeks | P3-M3 complete |

**Parallel work opportunities**:
- Redis setup and API can proceed independently
- LLM reflection prompt development can start early
- Episode schema design can overlap with M3

---

## Future Considerations (Phase 4+)

Phase 3 provides the foundation. Advanced features for later phases:

- **Meta-reflection**: Periodic aggregate analysis across many diary entries (pattern detection at scale)
- **Personality evolution tracking**: Long-term changes in agent behavior, tone, preferences
- **Deep planner integration**: Reflection-driven strategy adjustment, dynamic capability weighting
- **Multi-agent memory sharing**: Selective knowledge transfer between LOGOS instances
- **Memory compression**: Summarize/consolidate old episodes to manage growth

---

## References

- `PHASE2_SPEC.md` - PersonaEntry schema, CWM-E foundations
- `LOGOS_SPEC.md` - Short-term memory conceptual architecture
- `apollo/docs/PERSONA_DIARY.md` - Diary API and usage patterns
- `docs/operations/PHASE2_VERIFY.md` - Phase 2 completion criteria
