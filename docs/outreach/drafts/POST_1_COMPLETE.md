# Non-Linguistic Cognition: Why Graphs Matter

*This is the second post in a series on building non-linguistic cognitive architectures. The first post examined AI history through the lens of search strategies—symbolic trees, neural weight spaces, and language model token sequences. This post introduces Project LOGOS, which explores graph-based knowledge representation as an alternative to language-based reasoning.*

---

Large language models have achieved remarkable capabilities, from writing code to conducting conversations to solving complex reasoning tasks. Yet they share a fundamental constraint: they think in words. Every problem must be compressed into token sequences, every relationship expressed linguistically, every concept encoded as patterns in text.

Human cognition, by contrast, operates in non-linguistic structures (**mental models**, spatial reasoning, causal intuition) before language ever emerges. When you navigate around furniture, catch a ball, or understand that pushing causes movement, your brain builds structured representations of space, physics, and causality. Language comes later, as an interface for communication, not as the substrate for thought itself.

This post introduces Project LOGOS, an open-source cognitive architecture that uses graph-based knowledge representation instead of token sequences. By building what we call a **Hybrid Causal Graph** (**HCG**) using **Neo4j** (a graph database) and **Milvus** (a vector database), LOGOS enables autonomous agents to reason causally about actions and consequences, validate plans formally using logical constraints, and explain their decisions transparently by tracing through explicit graph structures.

We'll demonstrate these capabilities through a robotics pick-and-place scenario and explore why graphs (not words) might be the natural substrate for machine cognition.

---

## The Language Bottleneck

Ask GPT-4 to plan how a robot should pick up a red block and place it in a target bin. You'll get beautiful, fluent prose:

> *"First, the robot should move its gripper above the red block, ensuring proper alignment. Then, it should descend carefully to grasp the block without disturbing neighboring objects. Once grasped securely, the robot should lift the block and transport it to the target location, where it will gently release..."*

Now ask:

<div align="center">
<i>What are the precise spatial coordinates at each step?</i><br>
<i>What are the causal dependencies between actions?</i><br>
<i>Which constraints must be validated before executing each motion?</i><br>
<i>How do we verify the plan is physically feasible?</i><br>
</div>

The language model's response conflates description with specification. It generates tokens that sound correct without representing the geometric, causal, and temporal structure required for actual execution. This isn't a failure of scale or training; it's a fundamental limitation of the search space. Token sequences encode linguistic patterns, not **world models**.

### The Hallucination Problem is Structural

The issue runs deeper than training data or model size. It's inherent to what language models optimize for. Consider the probability distribution LLMs learn:

$$P(x_{t+1} | x_1, \ldots, x_t) = \text{softmax}(W \cdot h_t)$$

This mathematical notation describes the core operation: given all previous tokens ($x_1$ through $x_t$), predict the probability distribution over what token comes next ($x_{t+1}$). The model maximizes the probability of the next token given previous tokens; it learns **correlations** in text, patterns of which words tend to follow which other words.

But **correlation** is not **causation**, and linguistic plausibility is not physical validity. The model learns that "above" often follows "move gripper" in robot instruction manuals, not because it understands spatial relationships, but because this word sequence appears frequently in its training data.

When GPT-4 generates "the robot moves its gripper above the block," it's sampling from the probability distribution $P(\text{"above"} | \text{context})$, not from a spatial model that actually computes geometric relationships. A true spatial model would calculate something like:

$$\text{gripper\_position} = \text{block\_position} + [0, 0, \text{hover\_height}]$$

This formula specifies exact 3D coordinates. It would also check **preconditions**: is the computed position reachable by the robot's joints (avoiding impossible configurations)? Is there a **collision-free path** from the current position to the target? These are geometric computations, not linguistic patterns.

The LLM has never performed **inverse kinematics** calculations, never checked collision constraints against 3D models, never validated that preconditions hold before actions execute. It generates text that describes what should happen without specifying how to make it happen. The output sounds correct because it matches linguistic patterns from training data, but may be physically impossible or causally incoherent.

### The Deeper Issue: Language as Lossy Compression

Human language evolved for communication, not computation. We compress rich 3D spatial understanding into 1D token sequences, losing:

1. **Geometric precision**: "above the block" is ambiguous (how far above? What orientation?)
2. **Causal structure**: "then move" implies temporal ordering but doesn't encode causal dependencies
3. **Constraint satisfaction**: "grasp the block" doesn't specify force limits, contact points, or stability conditions
4. **Validation criteria**: "carefully" and "securely" are qualitative, not quantifiable

Natural language is a lossy encoding of thought. When LLMs learn P(text), they learn the compressed representation, not the underlying world model.

---

## How Humans Actually Think

Neurological evidence reveals that cognition precedes language:

### Spatial Reasoning Without Words

When you navigate around furniture to reach the kitchen, your brain constructs a spatial map, an internal representation of locations, obstacles, and possible paths. Neuroscience research reveals this happens in the hippocampus through specialized neurons called **place cells** and **grid cells** that fire in geometric patterns corresponding to your location and movement through space.

**Place cells** activate when you're in specific locations ("kitchen doorway," "beside the couch"). **Grid cells** fire in regular hexagonal patterns as you move, creating a coordinate system for tracking position. Importantly, this neural activity represents space directly as geometric relationships, not as verbal descriptions. You don't internally narrate "walk three steps forward, turn 30 degrees right, proceed four steps." The navigation system operates in spatial coordinates (actual geometric representations of position and direction).

We can describe this mathematically as graph search on a spatial representation $G = (V, E)$, where $V$ is a set of discrete locations in space and $E$ represents connections between locations where a path exists. Each edge has a weight representing distance or movement cost. Path planning then becomes finding the minimum-cost path through this graph:

$$\pi^* = \arg\min_\pi \sum_{(u,v) \in \pi} \text{cost}(u,v)$$

The key insight: your brain searches this spatial graph structure, not a sequence of linguistic instructions. The computation is geometric, not linguistic. Language only emerges if you need to communicate your navigation to someone else ("I went past the couch toward the kitchen"), but the underlying reasoning happens in spatial representations.

### Motor Planning and Forward Models

Consider catching a ball: you see it arcing through the air, predict where it will be, and coordinate your hand movement to intercept it. This entire process happens in approximately 400 milliseconds, far too fast for linguistic processing (try internally narrating instructions for catching and you'll drop the ball). 

The cerebellum, a brain structure dedicated to motor control, implements what neuroscientists call a **forward model**: an internal simulation that predicts the consequences of actions. We can write this as:

$$x_{t+1} = f(x_t, a_t, \theta)$$

where $x_t$ represents the current state (ball position, velocity, hand position), $a_t$ represents motor commands (muscle activations), and $\theta$ represents learned parameters of how the world works (gravity, ball dynamics, limb mechanics).

This is **model-based prediction** in continuous state space. The brain maintains representations of positions and velocities as real numbers (or neural approximations thereof), not as words in a vocabulary. The computation searches through trajectories in multidimensional space (potential paths the ball and hand might take), selecting motor commands that bring them to the same location at the same time.

Compare this to token sequence generation, where an LLM would need to describe each moment linguistically ("the ball is now 2 meters away, moving at 5 m/s, my hand should move upward..."). The serial nature of language generation, the discretization into vocabulary items, and the indirection through linguistic description would make real-time motor control impossible. The brain solves this by reasoning directly in spatial-temporal coordinates.

### Causal Intuition in Infants

By 6 months, pre-linguistic infants demonstrate:
- **Object permanence**: understanding objects persist when occluded
- **Physical causality**: surprise when objects pass through solid barriers
- **Agent intentionality**: distinguishing goal-directed vs. random motion

These capabilities emerge from **core knowledge systems** (Spelke, 1990) that represent:
- Objects and their properties
- Agents and their goals  
- Numbers and quantities
- Spatial relationships

None require language. Cognition operates on structured representations: graphs of objects, properties, and relationships.

### Animal Cognition: Intelligence Without Language

Examples abound of sophisticated reasoning without linguistic capability:

**Crows** (corvids):
- Use tools to solve multi-step problems
- Plan sequences: "if I drop rock in tube, water rises, I can reach food"
- Demonstrates **causal reasoning**: action/outcome chains

**Octopuses** (cephalopods):
- Navigate mazes by memory
- Open jars through trial-and-error learning
- Independently evolved intelligence without shared ancestry with vertebrates

**Bees** (insects):
- Communicate spatial information via waggle dance (non-linguistic encoding!)
- Optimize foraging routes (**traveling salesman problem**)
- Understand abstract concepts (same/different, above/below)

Key insight: These species build mental models of their environments and reason causally about actions and outcomes, all without linguistic tokens. Intelligence operates on structured representations, and language is an optional interface layer.

---

## The Graph Alternative: Explicit Structure

What if we represented knowledge the way brains do, as **nodes** and **edges** encoding entities, relationships, and causal structure?

### Knowledge Graphs: Formal Definition

A knowledge graph represents information as a network of interconnected concepts. Formally, a **knowledge graph** $K = (V, E, L)$ consists of:
- **Vertices** $V$ (the "nodes": things like objects, concepts, states, and processes)
- **Edges** $E \subseteq V \times R \times V$ (the "relationships" connecting nodes, where each edge has a type from a set $R$)
- **Labels** $L: V \cup E \to \text{attributes}$ that attach properties and metadata to both nodes and edges

The power comes from making relationships **explicit** and **typed**. Rather than learning that "block" and "red" tend to appear near each other in text (a statistical correlation), we explicitly represent (RedBlock) -[:HAS_PROPERTY]-> (ColorRed). Rather than learning that "grasp" tends to follow "move to" in robot commands, we explicitly encode (MoveToBlock) -[:PRECEDES]-> (GraspBlock) with a temporal relationship.

Let's build up a concrete example for our pick-and-place robotics domain. We'll start with entities (the physical objects involved):

```
Entities:
  RedBlock: Entity {uuid: e1, type: Block, color: red}
  TargetBin: Entity {uuid: e2, type: Container}
  Gripper: Entity {uuid: e3, type: EndEffector}

States:
  BlockAtOrigin: State {entity: e1, location: [0.5, 0.2, 0.0]}
  BlockInBin: State {entity: e1, location: [0.8, 0.5, 0.1]}

Processes (Actions):
  MoveToBlock: Process {action: MoveToPreGrasp, target: e1}
  GraspBlock: Process {action: Grasp, target: e1}
  MoveToTarget: Process {action: MoveToPlace, target: e2}
  ReleaseBlock: Process {action: Release, target: e1}

Relationships:
  (RedBlock) -[:HAS_STATE]-> (BlockAtOrigin)
  (MoveToBlock) -[:PRECONDITION]-> (Clear(e1))
  (GraspBlock) -[:PRECEDES]-> (MoveToTarget)
  (MoveToTarget) -[:CAUSES]-> (BlockInBin)
```

### Why Graphs Beat Token Sequences

1. Explicit Relationships

Graphs represent relationships directly as typed edges between nodes. When we write (action) -[:CAUSES]-> (state_change), we're creating an explicit, queryable link that says "this action causes this state change." The relationship exists as a first-class object in the database—we can traverse it, query for all actions that cause a particular state, or find all effects of a given action.

Consider these relationship types that naturally arise in robotic planning:
- **Causal**: (GraspBlock) -[:CAUSES]-> (BlockGrasped) expresses that executing the grasp action brings about the grasped state
- **Temporal**: (MoveToBlock) -[:PRECEDES]-> (GraspBlock) encodes that moving must happen before grasping
- **Spatial**: (RedBlock) -[:LOCATED_AT]-> ([0.5, 0.2, 0.0]) specifies exact 3D coordinates
- **Hierarchical**: (RedBlock) -[:IS_A]-> (Block) indicates taxonomic relationships

In token sequences, these relationships are implicit, buried in statistical patterns learned from text. When an LLM generates "then grasp the block," the word "then" suggests temporal ordering, but there's no explicit data structure encoding the PRECEDES relationship. The model learns P("then" | context) from seeing "then" follow certain patterns in training data, without ever creating an explicit representation that "action A must precede action B."

This distinction matters enormously for reliability. With explicit relationships, we can query "what are all the preconditions for this action?" and get a definitive answer by following edges in the graph. With implicit relationships learned statistically, we can only sample likely continuations and hope the statistical patterns align with logical necessity.

2. Validation and Consistency

One of the most powerful features of graph-based knowledge representation is the ability to define formal constraints that the graph must satisfy. **SHACL** (**Shapes Constraint Language**) is a W3C standard that lets us specify logical rules about graph structure.

Here's an example constraint in SHACL (the notation is Turtle/RDF, but the idea is straightforward):

```turtle
:ProcessShape a sh:NodeShape ;
  sh:targetClass :Process ;
  sh:property [
    sh:path :hasPrecondition ;
    sh:minCount 1 ;
    sh:message "Every process must have at least one precondition"
  ] ;
  sh:property [
    sh:path :causes ;
    sh:class :State ;
    sh:message "Process effects must reference State nodes"
  ] .
```

This defines a "shape" that all Process nodes must conform to. In plain English: every process (action) must have at least one precondition (a state that must be true before the action can execute), and every process must cause at least one state (specify what changes when the action executes). The "sh:class :State" constraint ensures that the target of a CAUSES edge is actually a State node, not some other type.

Now, when we try to add or modify processes in our graph, we can validate against these constraints. If someone tries to create a robot action without specifying preconditions, the validator rejects it:

```cypher
// This violates our constraints - rejected by SHACL validator
CREATE (p:Process {action: 'Grasp'})
  -[:CAUSES]->(s:State {entity: 'Block', grasped: true})
// Problem: Missing precondition stating the block must be clear and reachable
```

The validator checks the proposed graph modification against all defined shapes and reports violations before the invalid data gets committed. This provides formal correctness guarantees—we can prove the knowledge graph satisfies our constraints.

Language models have no equivalent mechanism. They generate token sequences that sound plausible based on training data patterns, but there's no formal validation that the generated plan satisfies physical constraints, respects temporal ordering, or maintains causal coherence. A language model might confidently generate "grasp the block" without first establishing that the gripper is positioned correctly or that the block is reachable.

3. Causal Reasoning

Graphs enable backward chaining from goals:

```
Goal: BlockInBin
Question: What causes BlockInBin?
Answer: ReleaseBlock process

Question: What are preconditions for ReleaseBlock?
Answer: (Gripper)-[:HAS_STATE]->(GripperAtTarget), 
        (Gripper)-[:HOLDING]->(RedBlock)

Question: What causes these preconditions?
Answer: MoveToTarget process (for location),
        GraspBlock process (for holding)

// Recursively build plan: MoveToBlock, Grasp, MoveToTarget, Release
```

This is **means-ends analysis** operating on explicit causal structure. Compare to LLM approach:

```
Prompt: "Plan to put block in bin"
LLM: "1. Move to block [P=0.85] 2. Grasp block [P=0.92] 3. Move to bin [P=0.88]..."
```

The probabilities reflect linguistic co-occurrence patterns, not causal necessity. There's no guarantee the plan is valid or that steps satisfy each other's preconditions.

4. Explainability

Graph-based plans are inherently transparent:

```
Why did you choose GraspBlock before MoveToTarget?

Answer (with proof):
1. Goal: BlockInBin (desired state)
2. Cause: ReleaseBlock process
3. Precondition: Gripper must be holding block
4. Cause: GraspBlock process  
5. Temporal constraint: GraspBlock -[:PRECEDES]-> ReleaseBlock
∴ GraspBlock must occur before MoveToTarget which precedes ReleaseBlock
```

Each step references explicit graph structure. For LLMs, "explainability" means:

```
Why did you generate "grasp" next?
Answer: attention weights over context [0.3, 0.15, 0.8, ...], maximizing P("grasp"|context)
```

This explains what tokens had high attention, not why the plan is correct.

---

## Introducing LOGOS: Hybrid Causal Graphs in Practice

Project LOGOS implements these ideas in an open-source cognitive architecture combining:
- **Neo4j** (graph database): explicit causal/temporal/spatial relationships
- **Milvus** (vector database): semantic similarity search over embeddings
- **SHACL** validation: formal constraints ensuring graph integrity

### Architecture: Sophia + HCG

**Sophia** (cognitive core) maintains the **Hybrid Causal Graph** with:
- **CWM-A** (Abstract World Model): symbolic commonsense reasoning
- **CWM-G** (Grounded World Model): learned physics/dynamics [Phase 2+]
- **Planner**: backward-chaining through CAUSES relationships
- **Executor**: monitors plan execution, updates state

HCG Structure:

```cypher
// Node types
(:Entity)      // Objects in the world
(:Concept)     // Abstract categories  
(:State)       // Configurations of entities
(:Process)     // Actions/events that cause state changes

// Relationship types
-[:IS_A]->         // Taxonomy (RedBlock IS_A Block)
-[:HAS_STATE]->    // Current configuration
-[:CAUSES]->       // Causal links (Process causes State)
-[:PRECEDES]->     // Temporal ordering
-[:PART_OF]->      // Compositional structure
```

**Example HCG for Pick-and-Place:**

```cypher
// Entities
CREATE (rb:Entity {uuid: '...', name: 'RedBlock', type: 'Block'})
CREATE (tb:Entity {uuid: '...', name: 'TargetBin', type: 'Container'})

// Initial state
CREATE (s0:State {
  uuid: '...', 
  timestamp: '2025-01-15T10:00:00Z',
  entity_id: '...',
  location: [0.5, 0.2, 0.0],
  grasped: false
})
CREATE (rb)-[:HAS_STATE {current: true}]->(s0)

// Goal state
CREATE (sg:State {
  uuid: '...',
  entity_id: '...',
  location: [0.8, 0.5, 0.1],  // inside bin
  grasped: false
})
CREATE (tb)-[:CONTAINS]->(sg)

// Generated plan (processes)
CREATE (p1:Process {uuid: '...', action: 'MoveToPreGrasp', target: '...'})
CREATE (p2:Process {uuid: '...', action: 'Grasp', target: '...'})
CREATE (p3:Process {uuid: '...', action: 'MoveToPlace', target: '...'})
CREATE (p4:Process {uuid: '...', action: 'Release', target: '...'})

// Temporal ordering
CREATE (p1)-[:PRECEDES]->(p2)-[:PRECEDES]->(p3)-[:PRECEDES]->(p4)

// Causal relationships
CREATE (p2)-[:CAUSES]->(s1:State {grasped: true})
CREATE (p4)-[:CAUSES]->(sg)

// Preconditions
CREATE (p2)-[:PRECONDITION]->(:State {clear: true})
CREATE (p4)-[:PRECONDITION]->(s1)
```

### Planning Algorithm: Backward Chaining

```python
def plan(goal_state, current_state, hcg):
    """
    Generate plan by backward-chaining through causal graph.
    
    Args:
        goal_state: desired State node
        current_state: initial State node
        hcg: Hybrid Causal Graph (Neo4j connection)
    
    Returns:
        List[Process] ordered by PRECEDES relationships
    """
    plan = []
    frontier = [goal_state]
    
    while frontier:
        state = frontier.pop()
        
        # Check if already achieved
        if state == current_state or is_satisfied(state, hcg):
            continue
        
        # Find process that causes this state
        causing_process = hcg.query("""
            MATCH (p:Process)-[:CAUSES]->(s:State {uuid: $state_uuid})
            RETURN p
        """, state_uuid=state.uuid)
        
        if not causing_process:
            raise PlanningError(f"No process causes {state}")
        
        # Add to plan
        plan.insert(0, causing_process)
        
        # Add preconditions to frontier
        preconditions = hcg.query("""
            MATCH (p:Process {uuid: $proc_uuid})-[:PRECONDITION]->(pre:State)
            RETURN pre
        """, proc_uuid=causing_process.uuid)
        
        frontier.extend(preconditions)
    
    # Verify temporal ordering via PRECEDES relationships
    validate_temporal_order(plan, hcg)
    
    return plan


def validate_temporal_order(plan, hcg):
    """Ensure plan respects PRECEDES constraints."""
    for i, proc in enumerate(plan[:-1]):
        next_proc = plan[i+1]
        
        # Check if explicit PRECEDES relationship exists
        must_precede = hcg.query("""
            MATCH (p1:Process {uuid: $uuid1})
                  -[:PRECEDES*1..5]->(p2:Process {uuid: $uuid2})
            RETURN count(*) > 0 as connected
        """, uuid1=proc.uuid, uuid2=next_proc.uuid)
        
        if not must_precede:
            raise ValidationError(
                f"Process {proc} must precede {next_proc} but no path exists"
            )
```

### SHACL Validation Example

```turtle
@prefix sh: <http://www.w3.org/ns/shacl#> .
@prefix logos: <http://logos.ai/ontology#> .

logos:ProcessShape
  a sh:NodeShape ;
  sh:targetClass logos:Process ;
  
  # Every process must have exactly one action type
  sh:property [
    sh:path logos:action ;
    sh:minCount 1 ;
    sh:maxCount 1 ;
    sh:datatype xsd:string ;
  ] ;
  
  # Every process must have at least one precondition
  sh:property [
    sh:path logos:precondition ;
    sh:minCount 1 ;
    sh:class logos:State ;
    sh:message "Process requires precondition states"
  ] ;
  
  # Every process must cause at least one state change
  sh:property [
    sh:path logos:causes ;
    sh:minCount 1 ;
    sh:class logos:State ;
    sh:message "Process must have causal effects"
  ] ;
  
  # Temporal constraints: if A PRECEDES B, then A.timestamp < B.timestamp
  sh:sparql [
    sh:message "Process temporal ordering violated" ;
    sh:select """
      SELECT $this ?later
      WHERE {
        $this logos:precedes ?later .
        $this logos:timestamp ?t1 .
        ?later logos:timestamp ?t2 .
        FILTER (?t1 >= ?t2)
      }
    """ ;
  ] .
```

When Sophia attempts to update the HCG, SHACL validation runs:

```python
from pyshacl import validate

# Proposed graph update
proposed_graph = construct_update(new_process)

# Validate against SHACL shapes
conforms, results_graph, results_text = validate(
    data_graph=proposed_graph,
    shacl_graph=shacl_shapes,
    inference='rdfs',
    abort_on_first=False
)

if not conforms:
    raise ValidationError(f"Invalid HCG update:\n{results_text}")
else:
    commit_to_neo4j(proposed_graph)
```

This provides **formal correctness guarantees** that LLM text generation cannot offer.

### Demonstration: Pick-and-Place Execution

From the M4 milestone verification:

```bash
$ python scripts/m4_demo.py

[Sophia] Goal received: place RedBlock in TargetBin
[Sophia] Querying HCG for current state...
[HCG] Entity RedBlock at [0.5, 0.2, 0.0], grasped=false, clear=true
[HCG] Entity TargetBin at [0.8, 0.5, 0.0]

[Planner] Backward chaining from goal state...
[Planner] Goal: RedBlock at [0.8, 0.5, 0.1] (inside bin)
[Planner] Cause: Release process
[Planner] Precondition: Gripper holding RedBlock
[Planner] Cause: Grasp process  
[Planner] Precondition: Gripper at RedBlock, RedBlock clear
[Planner] Cause: MoveToPreGrasp process
[Planner] Generated plan: [MoveToPreGrasp, Grasp, MoveToPlace, Release]

[SHACL] Validating plan...
[SHACL] All processes have preconditions
[SHACL] Temporal ordering consistent
[SHACL] Causal chains valid

[Executor] Executing step 1: MoveToPreGrasp
[Talos] Simulated: gripper moved to [0.5, 0.2, 0.15]
[HCG] State updated: Gripper at [0.5, 0.2, 0.15]

[Executor] Executing step 2: Grasp
[Talos] Simulated: gripper closed, contact detected
[HCG] State updated: RedBlock grasped=true

[Executor] Executing step 3: MoveToPlace
[Talos] Simulated: gripper moved to [0.8, 0.5, 0.15]
[HCG] State updated: Gripper at [0.8, 0.5, 0.15]

[Executor] Executing step 4: Release
[Talos] Simulated: gripper opened, block released
[HCG] State updated: RedBlock at [0.8, 0.5, 0.1], grasped=false

[Sophia] Goal achieved: BlockInBin
[Sophia] Verification: all CAUSES relationships confirmed
```

Key observations:

1. **Explainable reasoning**: each step traced through causal graph
2. **Formal validation**: SHACL checked correctness before execution
3. **State tracking**: HCG maintained consistent world state
4. **Zero hallucination**: plan derived from explicit structure, not probability distributions

Compare to an LLM-based planner where outputs must be parsed, validated post-hoc, and may generate plausible-sounding but invalid plans.

---

## What This Enables (and What It Doesn't Replace)

### Graph-Based Cognitive Architecture Advantages

1. Reliability
- Formal validation prevents invalid states
- Causal reasoning guarantees preconditions met
- No hallucination: outputs derived from structure

2. Explainability
- Every decision traces to explicit graph relationships
- "Why?" queries return causal chains with proof
- Human-inspectable reasoning paths

3. Integration
- Graphs compose: merge domain ontologies
- Semantic search (Milvus) finds analogous structures
- Extends to new domains without retraining

4. Efficiency for Structured Tasks
- Graph traversal: O(|V| + |E|), not O(V^|sequence_length|)
- Pruning via constraints reduces search space
- Incremental updates cheap (add edges, don't retrain)

### When to Use LLMs vs. Graphs

Use LLMs for:
- Natural language interface (Apollo CLI)
- Parsing high-level goals into formal representations
- Generating human-readable explanations
- Creativity and open-ended generation

Use graphs for:
- Causal reasoning and planning
- Constraint satisfaction
- Structured world model maintenance  
- Formal verification of correctness

LOGOS philosophy: complementary, not competitive.

**Apollo** (interface) uses LLMs, parses to formal goal state. **Sophia** (reasoning) searches HCG. **Talos** (embodiment) executes. **Hermes** (language) explains in natural language.

---

## Hybrid Architectures: The Path Forward

The history of AI shows that combining paradigms often works better than any single approach:
- Deep Blue: symbolic search + neural evaluation
- AlphaGo: MCTS + policy/value networks
- LOGOS: causal graphs + vector embeddings + optional LLM interface

Future systems will likely integrate:
- Symbolic knowledge graphs: explicit causal/temporal structure
- Learned dynamics models: neural networks for physics prediction (CWM-G)
- Language models: fluent communication interface
- Embodied perception: vision, proprioception, touch

Each component searches its appropriate space:
- Graphs search causal relationships
- Neural nets search weight spaces for pattern recognition
- LLMs search token distributions for language
- Together: reliable, explainable, and capable AI

---

## Try It Yourself

LOGOS is fully open-source:

```bash
# Clone the repository
git clone https://github.com/c-daly/logos.git
cd logos

# Start HCG infrastructure (Neo4j + Milvus)
docker compose -f infra/docker-compose.hcg.dev.yml up -d

# Load core ontology
./infra/load_ontology.sh

# Run the pick-and-place demo
python scripts/m4_demo.py
```

Explore the HCG:
- Neo4j Browser: http://localhost:7474
- Run Cypher queries to traverse the causal graph
- Visualize plans, inspect state transitions

Contribute:
- Extend the ontology for new domains
- Implement planning algorithms
- Build perception pipelines (Phase 2)
- Integrate with your robotics stack

---

## References

- Pearl, J. (2009). *Causality: Models, Reasoning and Inference*
- Spelke, E. S. (1990). "Principles of object perception." *Cognitive Science*, 14(1)
- Newell, A. & Simon, H. A. (1961). "GPS: A Program that Simulates Human Thought"
- SHACL specification: https://www.w3.org/TR/shacl/
- Neo4j graph database: https://neo4j.com/docs/
- Milvus vector database: https://milvus.io/docs/
