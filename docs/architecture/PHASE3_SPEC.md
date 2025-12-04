# Phase 3 Specification — Learning & Memory Systems

Phase 3 builds on the Phase 2 foundation to deliver adaptive, learning-capable agent behavior through memory systems, event-driven reflection, and episodic learning. This phase transforms LOGOS from a reactive system into one that learns from experience and develops a persistent personality.

## Goals
1. **Hierarchical Memory** — Implement a three-tier memory system (ephemeral → short-term → long-term) with promotion policies
2. **Event-driven Reflection** — Create intelligent, selective diary entries based on significant events rather than every interaction
3. **Selective Diary Entries** — Replace per-turn observation logging with meaningful, curated persona history
4. **Episodic Memory** — Enable the agent to learn from execution history and improve plan quality over time
5. **Probabilistic Validation** — Layer Level 2 validation to complement SHACL constraints with uncertainty reasoning

---

## Hierarchical Memory Architecture

Sophia maintains knowledge across three memory tiers with distinct lifetimes, storage backends, and promotion criteria. Information flows upward from ephemeral observations to potentially permanent knowledge, but only when it demonstrates significance and truth.

### Memory Tiers

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           LONG-TERM MEMORY                                  │
│                          (HCG - Neo4j/Milvus)                               │
│  • Canonical facts, validated processes, stable relationships              │
│  • Lifetime: indefinite (decades+)                                         │
│  • Examples: ontology, proven capabilities, persistent user preferences    │
└─────────────────────────────────────────────────────────────────────────────┘
                                    ▲
                                    │ Promotion (significance + truth)
                                    │
┌─────────────────────────────────────────────────────────────────────────────┐
│                          SHORT-TERM MEMORY                                  │
│                             (Redis + TTL)                                   │
│  • Working context that spans multiple sessions                            │
│  • Lifetime: configurable (hours to weeks, default: 7 days)                │
│  • Examples: recent reflections, pending hypotheses, accumulated patterns  │
└─────────────────────────────────────────────────────────────────────────────┘
                                    ▲
                                    │ Promotion (session significance)
                                    │
┌─────────────────────────────────────────────────────────────────────────────┐
│                         EPHEMERAL MEMORY                                    │
│                      (In-memory / Session-scoped)                           │
│  • Single conversation/session working memory                              │
│  • Lifetime: session duration (minutes to hours)                           │
│  • Examples: current topic, pending clarifications, in-flight reasoning    │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Tier Comparison

| Aspect | Ephemeral | Short-term | Long-term |
|--------|-----------|------------|-----------|
| **Scope** | Single session | Multi-session | Permanent |
| **Lifetime** | Session end | Configurable TTL (default 7d) | Indefinite |
| **Storage** | In-memory | Redis with TTL | Neo4j + Milvus |
| **CWMState status** | `ephemeral` | `short_term` | `canonical` / `proposed` |
| **Validation** | None | Light (consistency) | Full (SHACL + probabilistic) |
| **Queryable by** | Current session only | Cross-session lookups | All subsystems |
| **Garbage collection** | Session cleanup | TTL expiration | Decay policies |

### Promotion Criteria

Information only moves up the hierarchy when it demonstrates both **significance** and **truth**. Trivia, transient details, and unverified claims remain at lower tiers.

#### Ephemeral → Short-term Promotion

Triggers at session boundary or significant event:

| Criterion | Description | Example |
|-----------|-------------|---------|
| **User signal** | User explicitly marked something important | "Remember this for next time" |
| **Behavioral impact** | Changed how agent should act | User correction that affected plan |
| **Recurrence** | Same pattern observed multiple times in session | Three similar questions suggest confusion |
| **Novel fact** | New information not in HCG | User's timezone, project name |
| **Unresolved question** | Open curiosity that warrants follow-up | "Why did the user reject the verbose plan?" |

**Automatic exclusions**:
- Individual chat messages (transient)
- Pending clarifications (resolved or abandoned)
- Intermediate reasoning steps (only conclusions matter)
- Temporary UI state (scroll position, collapsed sections)

#### Short-term → Long-term Promotion

Triggers on reflection, validation pass, or explicit approval:

| Criterion | Description | Example |
|-----------|-------------|---------|
| **Confidence threshold** | Belief confidence > 0.8 after multiple observations | "User prefers concise responses" confirmed 5x |
| **Cross-session consistency** | Same pattern observed across multiple sessions | Preference stable over weeks |
| **Causal verification** | Hypothesis validated by outcome | "Shorter plans succeed more" proven by execution |
| **Source reliability** | Trusted source (user statement, verified system) | User explicitly stated preference |
| **Human approval** | Critical facts reviewed by operator | Safety-critical knowledge |

**Automatic exclusions** (remain in short-term until TTL):
- Unverified hypotheses (confidence < 0.5)
- Session-specific context (project deadline that passed)
- Contradicted beliefs (conflicting evidence emerged)
- Trivia (true but not useful for future reasoning)

### Demotion & Decay

Information can also flow downward:

- **Long-term → Short-term**: Deprecated facts, superseded knowledge, detected inconsistencies
- **Short-term → Ephemeral**: Failed validation, user contradiction, low-confidence after timeout
- **Any tier → Garbage**: TTL expiration, explicit deletion, confidence < 0.1

### Example: Annotation-driven Fact Ingestion

This example illustrates the full lifecycle of a fact entering through Hermes annotation and either earning long-term status or decaying:

```
┌──────────────────────────────────────────────────────────────────────────────┐
│ 1. INGESTION                                                                 │
│    Hermes receives image for annotation. Sends to Sophia for semantic parse.│
│    Sophia detects: "There is a red mug on the desk" — novel fact.            │
│                                                                              │
│    → Created in SHORT-TERM memory:                                           │
│      { type: "State", label: "red_mug_on_desk",                              │
│        confidence: 0.6, source: "hermes_annotation",                         │
│        status: "short_term", ttl: "7d" }                                     │
└──────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│ 2. VALIDATION WINDOW (7 days)                                                │
│    The fact sits in short-term memory. Confidence can change:                │
│                                                                              │
│    ✓ Supported: Another observation confirms red mug → confidence += 0.15   │
│    ✓ Connected: User mentions "my red mug" → link to user preferences       │
│    ✓ Validated: Plan uses mug location successfully → causal verification   │
│    ✗ Contradicted: Later image shows no mug → confidence -= 0.3             │
│    ✗ Ignored: No reference to mug in any context → confidence decays slowly │
└──────────────────────────────────────────────────────────────────────────────┘
                                    │
                    ┌───────────────┴───────────────┐
                    ▼                               ▼
┌──────────────────────────────┐    ┌──────────────────────────────┐
│ 3a. PROMOTION (confidence    │    │ 3b. DECAY (confidence < 0.5  │
│     > 0.8 OR explicit        │    │     at TTL expiration)       │
│     validation)              │    │                              │
│                              │    │ → Fact expires, logged as    │
│ → Promoted to LONG-TERM:     │    │   "unverified/unsupported"   │
│   { status: "canonical",     │    │                              │
│     promoted_at: "...",      │    │ No pollution of long-term    │
│     promoted_reason:         │    │ knowledge with unconfirmed   │
│       "causal_verification"} │    │ observations.                │
└──────────────────────────────┘    └──────────────────────────────┘
```

**Key principle**: Facts don't earn permanence just by existing — they must demonstrate relevance through use, corroboration, or explicit validation. This prevents the HCG from accumulating noise.

### Implementation Notes

- All tiers use the `CWMState` envelope with `status` field indicating tier
- Promotion events are logged for auditability (who/what/when/why)
- Policies are configurable per deployment (stricter for safety-critical systems)
- Reflection system is the primary driver of upward promotion
- Curiosity budget (see below) can trigger investigation of short-term hypotheses

---

## Milestones

### P3-M1: Hierarchical Memory Infrastructure

**Objective**: Implement the three-tier memory system (ephemeral → short-term → long-term) with promotion pipelines between tiers.

**Deliverables**:
- **Ephemeral storage**: In-memory store for session-scoped `CWMState` entries
- **Short-term storage**: Redis with TTL support for multi-session persistence
- **API endpoints**: 
  - `POST /api/memory/{tier}` - Create entry at specified tier (ephemeral, short_term)
  - `GET /api/memory/{tier}` - Query entries (by type, time window, session, confidence)
  - `DELETE /api/memory/{tier}/{id}` - Explicit deletion
  - `POST /api/memory/promote/{id}` - Promote entry to next tier (ephemeral→short, short→long)
  - `POST /api/memory/demote/{id}` - Demote entry (with reason)
- **Session management**: Track session lifecycle, automatic ephemeral cleanup
- **CWMState envelope**: Entries use `status` field: `ephemeral`, `short_term`, `proposed`, `canonical`
- **Promotion policies**: Configurable rules per tier transition (logged for auditability)
- **Demotion handling**: Track why knowledge was demoted (contradiction, decay, superseded)

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

## Tentative: Graph Assist API (Hermes ↔ Sophia Integration)

> **Status**: Tentative proposal. Multiple approaches were considered; final design to be refined during implementation.

### Problem Statement

Sophia needs semantic assistance for graph operations without duplicating Hermes's linguistic processing capabilities. Key use cases include:

- **Entity resolution**: "America" → Is this the band, country, continent, or sailing vessel?
- **Knowledge extraction**: Parse media metadata into structured graph nodes/edges
- **Relationship inference**: Suggest connections between unlinked entities
- **Query assistance**: Help users express graph queries in natural language
- **Ontology extension**: Propose new node types for novel entity categories

The core question: **How should Sophia request semantic assistance from Hermes, and what should the response format be?**

### Approaches Considered

#### Option A: Structured JSON Responses

Sophia sends a natural language query; Hermes responds with structured JSON that Sophia interprets and acts upon.

```python
# Sophia request
{
    "action": "resolve_entity",
    "context": {
        "text": "America",
        "media_type": "audio",
        "surrounding_metadata": {"album": "Homecoming", "year": 1972}
    }
}

# Hermes response
{
    "candidates": [
        {"label": "America (band)", "confidence": 0.92, "uri": "musicbrainz:artist/..."},
        {"label": "United States", "confidence": 0.05, "uri": "wikidata:Q30"},
        {"label": "America (ship)", "confidence": 0.03, "uri": null}
    ],
    "recommended": "America (band)",
    "reasoning": "Audio context and album metadata strongly suggest the folk rock band"
}
```

**Pros**:
- Clean separation of concerns
- Sophia maintains full control over graph operations
- Responses are predictable and validated

**Cons**:
- Requires defining a comprehensive action/response schema
- May be limiting for novel use cases
- Sophia still needs logic to interpret responses

#### Option B: Hermes Returns Cypher Queries (Preferred)

Sophia sends context; Hermes responds with **executable Cypher** that Sophia runs against Neo4j. Hermes understands the ontology and generates valid graph operations.

```python
# Sophia request
{
    "operation": "ingest_knowledge",
    "context": {
        "source": "audio_metadata",
        "raw": {"artist": "America", "album": "Homecoming", "track": "A Horse with No Name"}
    }
}

# Hermes response
{
    "queries": [
        """
        MERGE (a:MusicArtist {name: 'America', musicbrainz_id: 'xxx'})
        MERGE (al:Album {title: 'Homecoming', year: 1972})
        MERGE (t:Track {title: 'A Horse with No Name'})
        MERGE (a)-[:RELEASED]->(al)
        MERGE (al)-[:CONTAINS]->(t)
        """,
        """
        MATCH (m:MediaSample {uuid: $sample_uuid})
        MATCH (t:Track {title: 'A Horse with No Name'})
        MERGE (m)-[:REPRESENTS]->(t)
        """
    ],
    "confidence": 0.89,
    "reasoning": "High confidence based on exact metadata match with MusicBrainz"
}
```

**Pros**:
- Sophia becomes a "dumb executor" for semantic operations (clear responsibility split)
- Hermes has full expressiveness of Cypher
- Easier to extend without changing Sophia's code
- Batch operations are natural (multiple queries)

**Cons**:
- Security: Hermes-generated queries run with full graph access
- Hermes must deeply understand the ontology schema
- Debugging harder (must trace through LLM-generated queries)
- Requires Cypher validation/sandboxing

**Mitigations**:
- Cypher query validation before execution
- Read-only mode for exploratory queries
- Audit logging of all Hermes-generated queries
- Schema awareness via ontology embedding in Hermes context

#### Option C: Dedicated `/graph-assist` Endpoint

A specialized Hermes endpoint with a fine-tuned prompt for graph operations, distinct from conversational chat.

```
POST /graph-assist
{
    "intent": "verify" | "resolve" | "query" | "link_nodes" | "ingest_knowledge",
    "payload": { ... context-specific ... }
}
```

**Pros**:
- Specialized prompts can be optimized for graph operations
- Clear API contract for Sophia
- Could use smaller, faster models for common operations

**Cons**:
- Separate codebase to maintain
- May diverge from main Hermes capabilities over time

### Recommended Approach

**Option B (Cypher responses)** with **Option C's endpoint structure** as implementation detail.

The `/graph-assist` endpoint would:
1. Accept structured requests with intent classification
2. Use ontology-aware system prompts
3. Return validated Cypher queries
4. Include confidence scores and reasoning
5. Support read-only mode for queries vs. write mode for ingestion

### Use Cases

| Intent | Description | Example |
|--------|-------------|---------|
| `verify` | Check if entity interpretation is correct | "Is 'America' the band in this audio context?" |
| `resolve` | Disambiguate entity from candidates | Given context, which America is meant? |
| `query` | Natural language → Cypher for user queries | "What albums did America release in the 1970s?" |
| `link_nodes` | Propose relationships between existing nodes | MediaSample X seems related to Track Y |
| `ingest_knowledge` | Parse unstructured data into graph operations | Audio metadata → Artist/Album/Track nodes |

### Security Considerations

- **Query sandboxing**: Validate Cypher before execution; reject DELETE/REMOVE in non-admin mode
- **Rate limiting**: Prevent runaway graph modifications
- **Audit trail**: Log all Hermes-generated queries with provenance
- **Human-in-the-loop**: Optionally require approval for write operations
- **Schema pinning**: Hermes can only reference node/relationship types in ontology

### Integration with Curiosity System (Phase 4)

When the Curiosity Budget allows autonomous exploration, Sophia can:
1. Identify a knowledge gap (e.g., "Who produced this album?")
2. Call `/graph-assist` with `ingest_knowledge` intent
3. Hermes generates lookup + Cypher
4. Sophia executes, expanding the knowledge graph

This creates a **Hermes ↔ Sophia symbiosis**: Hermes provides semantic intelligence, Sophia provides structural memory.

### Graph Maintenance & Hygiene

Sophia requires periodic graph maintenance operations, potentially assisted by Hermes for semantic understanding. These operations maintain graph quality as knowledge accumulates.

#### Maintenance Operations

| Operation | Description | Trigger |
|-----------|-------------|---------|
| **Pruning** | Remove low-confidence or stale edges | Scheduled / budget-driven |
| **Deduplication** | Merge nodes representing the same entity | On ingest / periodic scan |
| **Inference** | Create implicit relationships from patterns | Reflection / curiosity |
| **Consolidation** | Summarize dense subgraphs into higher-level nodes | Threshold-based |
| **Orphan cleanup** | Remove disconnected nodes with no value | Scheduled |
| **Confidence decay** | Reduce certainty of unverified old facts | Time-based |

#### Deduplication Strategy

Entity deduplication is non-trivial—two nodes may represent the same entity with different labels or partial information.

```
Node A: {name: "America", type: "MusicArtist"}
Node B: {name: "America (band)", type: "MusicArtist", formed: 1970}
```

**Approach**:
1. **Candidate detection**: Embedding similarity + label fuzzy matching
2. **Hermes verification**: "Are these the same entity?" with full context
3. **Merge proposal**: Hermes generates `MERGE` Cypher combining properties
4. **Conflict resolution**: Prefer newer data, higher confidence, or prompt user

#### Inference Patterns

Sophia can infer relationships that aren't explicitly stated:

| Pattern | Inference |
|---------|-----------|
| A authored Track T, T is on Album B | A contributed to Album B |
| MediaSample M represents Track T, T mentions Location L | M is associated with L |
| User uploaded M1, M2, M3 all featuring Artist A | User has interest in A |

**Implementation**: Hermes generates inference Cypher based on graph patterns:

```python
# Sophia request
{
    "operation": "infer_relationships",
    "focus_node": "uuid:artist-america-xxx",
    "max_depth": 2
}

# Hermes response
{
    "inferences": [
        {
            "query": "MATCH (a:MusicArtist {uuid: $uuid})-[:RELEASED]->(:Album)<-[:UPLOADED]->(u:User) MERGE (u)-[:INTERESTED_IN {confidence: 0.7, inferred: true}]->(a)",
            "reasoning": "User uploaded multiple tracks from this artist",
            "confidence": 0.7
        }
    ]
}
```

#### Pruning Criteria

Edges/nodes may be pruned based on:

- **Age**: No access or update in N days
- **Confidence**: Below threshold and unverified
- **Redundancy**: Superseded by stronger relationship
- **Isolation**: No connections to active subgraph

**Safeguards**:
- Never prune user-created content without confirmation
- Archive before delete (soft delete with recovery window)
- Pruning proposals reviewed if above threshold count

#### Scheduling

Graph maintenance can be:
- **Scheduled**: Cron-style jobs during low-activity periods
- **Budget-driven**: Use Curiosity Budget for autonomous maintenance
- **Threshold-triggered**: When node/edge count exceeds limits
- **On-demand**: User or system requests cleanup

### Open Questions

- Should Hermes cache ontology schema, or query it dynamically?
- How to handle conflicting interpretations (multiple high-confidence candidates)?
- Transaction semantics: rollback if multi-query batch partially fails?
- How to measure and improve Cypher generation accuracy?
- What's the retention policy for pruned/archived nodes?
- How to balance inference aggressiveness vs. graph noise?

### Milestone Integration

This feature spans milestones if implemented in Phase 3:

- **P3-M1**: Schema awareness (Hermes can query ontology)
- **P3-M2**: Reflection can trigger resolution requests
- **P3-M4**: Episodic learning includes Graph Assist interactions

Alternatively, defer to **Phase 4** alongside Curiosity Budget for cohesive autonomous exploration.

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
- **Curiosity-driven exploration**: Autonomous investigation with resource budgets (see below)

### Curiosity Budget & Autonomous Exploration

Sophia maintains a **curiosity budget**—a constrained resource allocation for self-directed exploration. When Sophia is not responding to user requests, she can use this budget to investigate gaps in her knowledge.

#### Curiosity Triggers

Curiosity flags are raised when Sophia encounters:

| Trigger | Description | Example |
|---------|-------------|---------|
| **Novel fact** | Information that doesn't fit existing patterns or categories | Encountering an entity type with no ontology match |
| **Apparent contradiction** | Two beliefs or observations that seem incompatible | State A says object is at Location X, but Process B implies it moved to Y |
| **Perplexing diary entry** | Reflection that generates confusion, surprise, or high uncertainty | "I don't understand why the user rejected my plan" |
| **Interesting pattern** | Recurring structure that suggests an underlying connection | Multiple unconnected nodes share similar properties |
| **Disconnected subgraphs** | Nodes that seem related but lack explicit causal links | Draft → ??? → Published (missing intermediate processes) |

#### Budget Mechanics

The curiosity budget is a scalar value (0.0–1.0) that constrains exploration:

```python
class CuriosityBudget:
    value: float           # Current budget (0.0–1.0)
    min_threshold: float   # Below this, no autonomous exploration
    recharge_rate: float   # Budget recovery per time unit
    max_spend_per_action: float  # Cap on single exploration cost
```

**Budget increases when:**
- User confirms a hypothesis was useful
- Exploration discovers a valuable connection (judged by graph coherence improvement)
- Time passes without exploration (passive recharge)
- User explicitly grants exploration permission

**Budget decreases when:**
- Exploration yields no useful results
- User ignores or rejects findings
- External API calls are made (Hermes lookups have cost)
- Exploration time exceeds threshold

#### Exploration Actions

When budget > threshold, Sophia can:

1. **Graph gap analysis**: Identify nodes that *should* be connected but aren't
2. **Hermes lookup**: Use embedding search or web queries to find missing information
3. **Hypothesis generation**: Propose new nodes/edges that would resolve contradictions
4. **Simulation testing**: Use CWM-G to imagine whether proposed changes are plausible

#### Resource Limits

To prevent runaway consumption:

| Resource | Limit | Rationale |
|----------|-------|-----------|
| API calls per hour | Configurable (default: 10) | Prevent excessive external queries |
| Exploration time per session | Configurable (default: 5 min) | Bound compute usage |
| Concurrent explorations | 1 | Focus attention |
| Max graph modifications | Proposals only (no auto-commit) | Human-in-the-loop for changes |

#### Integration with Reflection (P3-M2)

Curiosity triggers often emerge from reflection:

```
Reflection → "This outcome was unexpected"
           → Curiosity flag: "Why did the user reject the plan?"
           → If budget allows: Search for similar rejected plans in diary
           → Propose hypothesis: "Plans with >5 steps are often rejected"
```

This forms a feedback loop: **Experience → Reflection → Curiosity → Exploration → New Knowledge → Better Plans**

---

## References

- `PHASE2_SPEC.md` - PersonaEntry schema, CWM-E foundations
- `LOGOS_SPEC.md` - Short-term memory conceptual architecture
- `apollo/docs/PERSONA_DIARY.md` - Diary API and usage patterns
- `docs/operations/PHASE2_VERIFY.md` - Phase 2 completion criteria
