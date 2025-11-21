# AI as Search: From Symbolic Trees to Neural Networks to Language Models

*This is the first post in a series exploring non-linguistic cognitive architectures. In this post, we examine the history of AI through the lens of search strategies—from symbolic tree search to neural weight optimization to language model token generation. The second post introduces Project LOGOS, a graph-based cognitive architecture that reasons causally rather than linguistically.*

---

At its core, artificial intelligence is about searching state spaces—exploring possible configurations to find solutions, make decisions, or generate outputs. Whether a chess program evaluating millions of positions per second or a language model predicting the next word in a sentence, every AI system navigates through a space of possibilities seeking optimal outcomes.

This historical survey traces how different AI paradigms approached this fundamental challenge, from early symbolic AI's explicit tree searches through neural networks' weight space optimization to large language models' probability distributions over token sequences. Understanding AI's history as evolving search strategies illuminates both the power and limitations of current approaches and points toward why structured causal graphs might offer an alternative path for machine cognition.

The key insight is this: the space you search determines what you can find. Symbolic logic can prove theorems but struggles with noisy perception. Neural networks excel at pattern recognition but can't explain their reasoning. Language models achieve remarkable fluency but can't guarantee causal correctness. Each paradigm's capabilities and limitations flow directly from the structure of its search space.

---

## The Central Insight: AI as Search

When Deep Blue defeated Garry Kasparov in 1997, it evaluated 200 million chess positions per second, searching a vast tree of possible moves to find the best path to victory. When ChatGPT writes an essay, it searches through probability distributions over trillions of possible token sequences to generate coherent text. Both are intelligent systems. Both solve problems by searching. But they search fundamentally different spaces, and that difference determines what they can and cannot do.

### State Spaces and Search

A **state space** is the set of all possible configurations of a system. In chess, each state is a board configuration; the state space contains approximately 10^43 legal positions. In robot navigation, each state might describe the robot's position, orientation, and the locations of obstacles. In image generation, each state could be a complete image with specific pixel values. The state space defines the universe of possibilities the AI must navigate.

A **search** is the process of exploring this space, moving from one state to another according to transition rules, to find states that satisfy goal conditions or optimize some objective function. The chess program searches for board positions leading to checkmate. The navigation system searches for collision-free paths to the destination. The image generator searches for pixel configurations matching a text description.

We can formalize a search problem as a tuple ⟨S, s₀, A, T, G⟩ where S is the set of all states, s₀ ∈ S is the initial state, A is the set of actions, T: S × A → S is the state transition function, and G ⊆ S is the set of goal states. This mathematical notation provides precision, but the intuition is simple: you start somewhere (s₀), you have actions available (A), those actions change your state (T), and you're trying to reach a goal (G).

Intelligence emerges from effective search strategies. The history of AI is the history of discovering new state spaces to search and developing better algorithms to explore them. Each paradigm shift in AI (symbolic to neural, neural to linguistic) fundamentally changed what we search and how we search it.

---

## The Symbolic Era: Searching Decision Trees (1950s-1980s)

### Early Foundations

The pioneers of AI approached intelligence as symbolic manipulation and logical inference. Allen Newell and Herbert Simon's **General Problem Solver** (1957) embodied this philosophy: problems are represented as states in a logical space, and intelligence is the process of navigating from initial state to goal state through **means-ends analysis**.

Their key insight was that many problems share common search structures. Whether proving mathematical theorems or solving the Tower of Hanoi puzzle, the underlying pattern is:
1. Represent current state symbolically
2. Identify difference between current and goal state
3. Select operators to reduce that difference
4. Recursively apply until goal reached

John McCarthy's **Lisp** (1958) provided the computational substrate for this vision. S-expressions naturally represented trees and graphs, enabling AI systems to manipulate symbolic structures as first-class objects. Logic programming languages like Prolog extended this, treating computation itself as theorem proving—a search through logical deductions.

### Search Algorithms: From Brute Force to Heuristics

Early chess programs demonstrated both the promise and peril of exhaustive search. Given a branching factor b (average moves per position) and search depth d, the number of nodes explored grows as O(b^d). For chess, b ≈ 35, making deep search intractable.

The breakthrough came with heuristic search algorithms that use domain knowledge to guide exploration toward promising areas of the state space. Rather than blindly trying every possibility, these algorithms incorporate estimates of how close each state is to the goal.

The **A* algorithm** (Hart, Nilsson, Raphael, 1968) remains one of AI's most elegant results. Its key idea is beautifully simple: at each step, expand the node that appears most promising based on both how far you've come and how far you estimate you have left to go.

More precisely, A* uses three values for each node n in the search tree:
- g(n) = actual cost from start to node n (known exactly from the path taken)
- h(n) = estimated cost from n to goal (the **heuristic**, a guess based on domain knowledge)
- f(n) = g(n) + h(n) = estimated total cost of the path through n

A* maintains a priority queue of nodes ordered by f(n), always expanding the node with the lowest estimated total cost. The remarkable property: if h(n) is **admissible** (meaning it never overestimates the true cost to reach the goal), A* is guaranteed to find the optimal path while exploring far fewer nodes than brute-force search. In GPS navigation with straight-line distance as the heuristic, A* might explore thousands of intersections instead of millions.

Minimax and alpha-beta pruning brought game-theoretic rigor to adversarial search. In a two-player zero-sum game, minimax computes:

$$V(n) = \begin{cases}
\max_{a \in A(n)} \min_{n' \in \text{children}(n,a)} V(n') & \text{if MAX's turn} \\
\min_{a \in A(n)} \max_{n' \in \text{children}(n,a)} V(n') & \text{if MIN's turn}
\end{cases}$$

Alpha-beta pruning reduces the branching factor from $b$ to approximately $\sqrt{b}$ by eliminating subtrees guaranteed to be worse than already-explored alternatives.

### STRIPS and Classical Planning

The **Stanford Research Institute Problem Solver** (**STRIPS**, 1971) formalized planning as search through state space where:
- States are conjunctions of predicates
- Actions have **preconditions** (must be true to apply) and **effects** (predicates added/deleted)
- Goal is a partial state specification

For example, moving a block:
```
Move(x, y, z):
  Preconditions: On(x,y) ∧ Clear(x) ∧ Clear(z)
  Effects: On(x,z) ∧ Clear(y) ∧ ¬On(x,y) ∧ ¬Clear(z)
```

STRIPS planning is **PSPACE-complete** in general, but practical heuristics (like GraphPlan and FF planner) made it tractable for robotics and logistics applications.

### Expert Systems and the AI Winter

The 1970s-80s saw **expert systems** encode human knowledge as rule bases. MYCIN diagnosed blood infections with ~600 rules, achieving expert-level performance. DENDRAL inferred molecular structures. The paradigm: capture expert knowledge, search rule space, produce diagnoses.

But **combinatorial explosion** remained intractable. The **qualification problem** (enumerating all preconditions) and **frame problem** (tracking what changes vs. what persists) proved fundamental obstacles. By the late 1980s, limitations of purely symbolic approaches had triggered the second AI winter.

Key limitation: Symbolic search operates in discrete, hand-crafted state spaces. It handles crisp logic poorly suited to noisy perception, requires extensive knowledge engineering, and scales badly as state space grows.

---

## The Neural Revolution: Searching Weight Spaces (1980s-2010s)

### Connectionism: Search as Optimization

The **connectionist revolution** reframed AI as optimization rather than logical inference. Instead of searching discrete states, neural networks search **continuous weight spaces** to minimize error functions.

A feedforward neural network with weights $w$ computes its output through layers of transformations. In mathematical notation:

$$\hat{y} = f(x; w) = \sigma(W_L \sigma(W_{L-1} \cdots \sigma(W_1 x)))$$

where $\sigma$ are activation functions (like ReLU or sigmoid) and $W_i$ are weight matrices at each layer. If you're not comfortable with this notation, the intuition is: data flows through the network layer by layer, each layer applying weights and nonlinear transformations, until producing a final output.

The learning problem is to find weights $w^*$ that minimize the error (loss) between predictions and true labels:

$$w^* = \arg\min_w \mathbb{E}_{(x,y)\sim D}[L(f(x;w), y)]$$

In plain language: find the weights that make the network's predictions as accurate as possible on average across the training data.

**Backpropagation** (Rumelhart et al., 1986) made this tractable by computing gradients via the **chain rule** from calculus. The gradient $\frac{\partial L}{\partial w_i}$ tells us how to adjust each weight to reduce the loss:

$$\frac{\partial L}{\partial w_i} = \frac{\partial L}{\partial \hat{y}} \cdot \frac{\partial \hat{y}}{\partial z_L} \cdot \frac{\partial z_L}{\partial z_{L-1}} \cdots \frac{\partial z_i}{\partial w_i}$$

This chains together the effects of each weight on the final error, propagating the error signal backward through the network.

This enables **gradient descent**, which iteratively updates the weights by taking small steps in the direction that reduces loss:

$$w_{t+1} = w_t - \eta \nabla_w L(w_t)$$

where $\eta$ is the **learning rate** (step size). Think of this as rolling a ball downhill on the loss surface: the gradient tells you which direction is downward, and you take small steps in that direction. The search traverses the weight space's **loss landscape**, seeking valleys (**local minima**) where the error is low.

### The Deep Learning Breakthrough

For decades, training deep networks (L > 3 layers) proved unstable. Gradients either **vanished** (approached 0) or **exploded** (approached infinity) as they propagated through layers. The 2010s saw several key innovations:

1. **ReLU activations**: σ(x) = max(0,x) preserve gradients better than sigmoids
2. **Batch normalization**: normalize layer inputs to stabilize training
3. **Residual connections**: skip connections enable training networks with L > 100
4. **GPU acceleration**: matrix operations parallelize perfectly

**AlexNet** (Krizhevsky et al., 2012) demonstrated the paradigm shift. With 60M parameters trained on ImageNet (1.2M images), it achieved 15.3% top-5 error, a 10% improvement over previous methods. This proved neural networks could learn **hierarchical features** automatically:
- Layer 1: edge detectors
- Layer 2-3: textures and patterns  
- Layer 4-5: object parts
- Layer 6-8: complete objects

The search space had fundamentally changed. Instead of searching trees of symbolic states, we now search high-dimensional continuous weight spaces with billions of parameters.

### Weight Space Geometry

What does this weight space look like? For a network with n parameters, the loss landscape is a function L: ℝⁿ → ℝ. Empirical studies reveal:

- **High-dimensional saddle points** are more common than local minima
- **Mode connectivity**: different minima often connect via low-loss paths
- **Loss landscape smoothness** correlates with generalization
- **Over-parameterization** (n >> dataset size) surprisingly helps (the **lottery ticket hypothesis** suggests good sub-networks exist)

Training dynamics can be understood through the **neural tangent kernel** (NTK) in the infinite-width limit, where training approximates kernel regression in function space.

### Hybrid Symbolic-Neural Systems

The era's most impressive achievements combined discrete symbolic search with neural approximation:

**Deep Blue** (1997) evaluated 200M positions/second using:
- Hand-crafted evaluation functions
- Specialized chess hardware
- **Minimax search** to depth 6-8 (with extensions up to 40 plies)

**AlphaGo** (2016) blended **Monte Carlo Tree Search** with neural networks:
- **Policy network** $p_\pi(a|s)$: predicts expert moves
- **Value network** $v_\theta(s)$: estimates position value
- **MCTS** explores tree, using networks to guide search and evaluate leaves

The search formula combines tree statistics with neural predictions:

$$\text{UCT}(s,a) = Q(s,a) + c \cdot p_\pi(a|s) \cdot \frac{\sqrt{\sum_b N(s,b)}}{1 + N(s,a)}$$

This balances exploitation ($Q$ value) with exploration (visit count).

Key insight: Neural networks learned from data reduce the symbolic search space, while symbolic search provides reliability and interpretability that pure neural approaches lack.

---

## The Language Model Era: Searching Token Sequences (2010s-2020s)

### Attention and the Transformer Architecture

Recurrent neural networks processed sequences one token at a time, creating **information bottlenecks**: information from early tokens had to squeeze through a fixed-size hidden state to reach later processing stages. The **Transformer** (Vaswani et al., 2017) revolutionized this with **self-attention**, allowing every token to directly access every other token in the sequence.

The attention mechanism computes:

$$\text{Attention}(Q,K,V) = \text{softmax}\left(\frac{QK^T}{\sqrt{d_k}}\right)V$$

If you're not familiar with this notation, here's the intuition: each token creates three vectors: a **Query** ("what am I looking for?"), a **Key** ("what do I contain?"), and a **Value** ("what information should I pass forward?"). The mechanism computes similarity scores between each token's Query and every other token's Key, then uses these scores as weights to combine the Values.

More concretely:
- $Q = XW_Q$ creates queries by multiplying input tokens by learned weights
- $K = XW_K$ creates keys similarly
- $V = XW_V$ creates values
- $QK^T$ computes all pairwise similarity scores
- Dividing by $\sqrt{d_k}$ (the square root of the key dimension) prevents the scores from getting too large
- $\text{softmax}$ converts scores to probabilities that sum to 1
- Multiplying by $V$ weights each token's value by its attention score

The result: each token's output is a weighted combination of all tokens' values, where the weights reflect learned relationships. In "The cat sat on the mat," the token "sat" might attend strongly to "cat" (the subject) and "mat" (the location), automatically learning grammatical structure.

**Multi-head attention** runs h parallel attention mechanisms with different learned weights, allowing the model to capture multiple types of relationships simultaneously. One head might learn syntactic dependencies while another learns semantic similarity.

The full Transformer architecture interleaves:
1. Multi-head self-attention (parallelizable)
2. Position-wise feedforward networks
3. Residual connections and layer normalization

This enables efficient training on sequences of length n with O(n²) attention complexity, recently reduced to O(n) or O(n log n) in variants like Linformer and Performer.

### The Scaling Hypothesis

The **scaling laws** for language models (Kaplan et al., 2020) reveal power-law relationships:

$$L(N) \propto N^{-\alpha}$$

where $L$ is test loss, $N$ is parameter count, and $\alpha \approx 0.076$. Performance improves predictably with scale:

- GPT-1 (2018): 117M parameters
- GPT-2 (2019): 1.5B parameters  
- GPT-3 (2020): 175B parameters
- GPT-4 (2023): ~1.8T parameters (estimated)

**Emergent abilities** appear at scale:
- **Few-shot learning** (GPT-3)
- **Chain-of-thought reasoning** (>100B parameters)
- Tool use and planning (largest models)

### Autoregressive Language Modeling

LLMs perform **next-token prediction**. Given sequence $x_1, \ldots, x_t$, model the distribution:

$$P(x_{t+1} | x_1, \ldots, x_t) = \text{softmax}(W_{\text{out}} h_t)$$

where $h_t$ is the final hidden state after processing $x_1, \ldots, x_t$ through transformer layers.

Generation samples from this distribution:

$$x_{t+1} \sim P(\cdot | x_1, \ldots, x_t)$$

**Sampling strategies** control the search through token sequence space:

1. **Greedy decoding**: $x_{t+1} = \arg\max P(x | \text{context})$
   - Deterministic but repetitive

2. **Temperature sampling**: $P'(x) = P(x)^{1/T} / Z$
   - $T < 1$: sharper (more conservative)
   - $T > 1$: flatter (more random)

3. **Top-k sampling**: sample from $k$ most likely tokens
   
4. **Nucleus (top-p) sampling**: sample from smallest set with cumulative probability $\geq p$
   - Adapts to distribution shape

5. **Beam search**: maintain $k$ highest-probability sequences
   - Probability of sequence: $P(x_1, \ldots, x_n) = \prod_{i=1}^n P(x_i | x_1, \ldots, x_{i-1})$

### The Search Space: Token Sequences

LLMs search a discrete space of token sequences. With vocabulary size V ≈ 50,000 and context length n ≈ 4,000-128,000, the space has V^n possible sequences (astronomically large).

The **attention mechanism** performs a learned, soft search over the context window. For each output position, **attention weights** determine which input tokens to focus on. This is fundamentally different from symbolic tree search or neural weight optimization: it's a **probabilistic search** over discrete sequences guided by learned continuous representations.

---

## Patterns, Limitations, and the Path Forward

### Universal Patterns

Across paradigms, several patterns emerge:

1. Scale enables capability: 10^43 chess positions, 10^9 image parameters, 10^11 LLM parameters
2. Search strategy matters: A* beats breadth-first, SGD with momentum beats vanilla gradient descent, nucleus sampling beats greedy
3. The space determines the possible: Symbolic logic can't handle noise; neural networks can't prove theorems; LLMs can't guarantee causality

### Fundamental Limitations by Search Space

**Symbolic AI:**
- Provably correct, explainable, compositional
- **Combinatorial explosion** (O(b^d) growth)
- Brittle knowledge engineering
- Cannot handle perceptual uncertainty

**Neural Networks:**
- Learn from data, handle noise, scale to billions of parameters
- **Adversarial brittleness** (small input perturbations lead to wrong outputs)
- **Black-box reasoning** (gradient-based explanations do not equal understanding)
- Data hunger (typically need 10³-10⁶ examples)
- **Catastrophic forgetting** in continual learning

**Large Language Models:**
- Natural language fluency, broad knowledge, few-shot learning
- **Hallucination**: P(likely token) ≠ P(true statement)
- No causal grounding: learns P(word|context), not causal mechanisms
- Temporal confusion: all tokens exist "simultaneously" in context window
- No world model: purely linguistic, no physics or geometry

The LLM limitations are particularly revealing. Token sequence space fundamentally cannot encode:
- 3D spatial relationships (beyond linguistic description)
- Causal mechanisms (beyond correlational co-occurrence)
- Temporal dynamics (beyond sequential ordering of tokens)
- Physical constraints (beyond learned statistical patterns)

### The Next Search Space: Causal Graphs

Human cognition operates on **structured mental models** before language:
- Spatial reasoning (navigating rooms)
- Causal intuition (predicting outcomes)
- Motor planning (reaching and grasping)
- Physical understanding (object permanence, collision dynamics)

These capabilities emerge from searching **graph-structured representations** where:
- **Nodes** represent entities, states, concepts, processes
- **Edges** encode relationships: causal (CAUSES), temporal (PRECEDES), taxonomic (IS_A), compositional (PART_OF)
- **Constraints** enforce consistency: SHACL shapes, temporal ordering, causal coherence

**Project LOGOS** explores this alternative search space through the **Hybrid Causal Graph** (**HCG**):

```cypher
// Symbolic structure (Neo4j)
CREATE (e:Entity {uuid: '...', name: 'RedBlock'})
CREATE (s:State {uuid: '...', location: [0.5, 0.2, 0.0]})
CREATE (p:Process {uuid: '...', action: 'Grasp'})
CREATE (e)-[:HAS_STATE]->(s)
CREATE (p)-[:CAUSES]->(s')
CREATE (p1)-[:PRECEDES]->(p2)

// Semantic search (Milvus)
embedding = embed("manipulate red object")
similar_concepts = search_milvus(embedding, k=10)
```

Search in this space means:
- **Planning**: backward-chaining from goal states through CAUSES relationships
- **Reasoning**: traversing IS_A hierarchies and PART_OF compositions  
- **Validation**: SHACL constraints ensure graph integrity
- **Semantic search**: vector embeddings find analogous structures

This combines symbolic search's explainability with neural search's pattern matching, while representing causal structure that token sequences cannot capture.

---

## Conclusion: Converging Search Strategies

AI's trajectory shows **progressive expansion of search spaces**, not replacement:
- Symbolic logic, then continuous optimization, then discrete sequences, then structured causality

The future likely involves **multiple search spaces** working synergistically:
- **Symbolic graphs** for causal reasoning and planning
- **Neural networks** for perception and dynamics prediction
- **Language models** for natural language interface
- **Hybrid architectures** that search across all three

The question isn't "which search space is best?" but rather "which combination enables robust, explainable, and capable AI?"

Project LOGOS represents one answer: let language models handle language, neural networks handle perception, and causal graphs handle reasoning. Search the right space for each task.

---

## Further Reading

- Pearl, J. (2009). *Causality: Models, Reasoning, and Inference*
- Russell, S. & Norvig, P. (2020). *Artificial Intelligence: A Modern Approach*, 4th ed.
- Vaswani et al. (2017). "Attention Is All You Need"
- Kaplan et al. (2020). "Scaling Laws for Neural Language Models"
- Silver et al. (2016). "Mastering the game of Go with deep neural networks and tree search"
