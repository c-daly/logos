# Multi-Modal Grounding Research — R3

**Task**: Research multi-modal grounding (sensor fusion, vision+proprioception) to inform Phase 2 CWM-G design.

**Author**: Project LOGOS Research Team  
**Date**: 2025-11-19  
**Status**: Complete  
**Related Specification Sections**: Section 3.3 (CWM-G), Section 3.5 (Talos), Section 7.2 (Phase 2)

---

## 1. Executive Summary

This research document provides a comprehensive analysis of multi-modal grounding techniques for Phase 2 CWM-G (Continuous World Model - Grounded) implementation. The recommended approach integrates vision, proprioception, and other sensor modalities through a hybrid symbolic-subsymbolic architecture that maintains alignment with LOGOS's non-linguistic cognitive principles.

**Key Recommendations**:
1. Implement a modular sensor fusion pipeline that converts raw Talos signals into HCG-compatible grounded entities and states
2. Use a bidirectional bridge between continuous sensor data and discrete symbolic representations
3. Adopt an attention-based fusion mechanism for handling multiple sensor modalities
4. Maintain temporal coherence through explicit causality tracking in the HCG
5. Leverage vector embeddings for perceptual similarity and grounding

---

## 2. Background and Context

### 2.1 CWM-G Role in LOGOS Architecture

From Section 3.3 of the specification, CWM-G serves as the grounded counterpart to CWM-A (Abstract World Model):
- **CWM-A**: Maintains abstract, symbolic state representations (e.g., "cup is on table")
- **CWM-G**: Maintains grounded physical/sensor state (e.g., 3D position, visual features, force feedback)

The integration between CWM-A and CWM-G enables:
- **Bottom-up grounding**: Raw sensor data → perceptual features → abstract concepts
- **Top-down prediction**: Abstract plans → expected sensor observations → validation against reality

### 2.2 Talos Integration Requirements

From Section 3.5, Talos provides:
- **Sensor abstractions**: Camera feeds, depth sensors, IMU (inertial measurement unit), force/torque sensors, tactile sensors
- **Actuator abstractions**: Motor controllers, gripper control, joint position/velocity commands
- **Simulation interfaces**: For Phase 1/2 testing before hardware deployment

### 2.3 Phase 2 Goals (Section 7.2)

Phase 2 primary deliverables include:
1. CWM-G implementation with sensor fusion
2. Talos integration with simulated hardware
3. Executor with real-time monitoring
4. Extended planning with uncertainty handling

---

## 3. Multi-Modal Grounding: State of the Art

### 3.1 Sensor Fusion Techniques

#### 3.1.1 Early Fusion
**Approach**: Combine raw sensor data at the input level before processing.
- **Pros**: Preserves maximum information, allows joint feature learning
- **Cons**: High computational cost, requires synchronized sensors, difficult to handle missing modalities

**Example**: Concatenate RGB image pixels with depth map values before feeding to neural network.

#### 3.1.2 Late Fusion
**Approach**: Process each modality independently, combine at decision/output level.
- **Pros**: Modular, handles asynchronous sensors, easier to debug per-modality
- **Cons**: May miss cross-modal correlations, requires careful weighting

**Example**: Separate visual object detector + proprioceptive position estimator → combine detections with spatial priors.

#### 3.1.3 Hybrid/Intermediate Fusion
**Approach**: Combine modalities at multiple intermediate processing stages.
- **Pros**: Balances early and late fusion benefits, flexible architecture
- **Cons**: More complex design, requires architectural decisions

**Example**: Vision CNN extracts features → fuse with IMU data at bottleneck → joint reasoning head.

#### 3.1.4 Attention-Based Fusion (Recommended)
**Approach**: Learn dynamic weighting of modalities based on context and reliability.
- **Pros**: Adaptive to sensor quality, handles uncertainty, interpretable attention weights
- **Cons**: Requires training data, can be computationally intensive

**Example**: Cross-attention mechanism between visual features and proprioceptive state, weighted by learned reliability scores.

### 3.2 Vision + Proprioception Integration

#### 3.2.1 Visual Grounding
Vision provides:
- **Object detection**: Bounding boxes, segmentation masks, 6D pose estimation
- **Scene understanding**: Spatial relationships, affordances, obstacles
- **Change detection**: Motion, manipulation outcomes, unexpected events

**Relevant architectures**:
- **Object-centric representations**: Slot Attention, IODINE, MONet for decomposing scenes into entities
- **Transformers for vision**: ViT, DETR for spatial reasoning and attention
- **3D perception**: PointNet++, VoteNet for depth-based object detection

#### 3.2.2 Proprioceptive Grounding
Proprioception provides:
- **Joint states**: Positions, velocities, accelerations, torques
- **End-effector pose**: 6D position and orientation in robot frame
- **Contact detection**: Force/torque readings indicating grasps or collisions
- **Body schema**: Internal model of robot morphology

**Integration patterns**:
- **Forward kinematics**: Joint states → end-effector pose (analytical)
- **Inverse kinematics**: Desired pose → joint commands (optimization/learning)
- **Tactile feedback**: Contact sensors → grasp stability, slip detection

#### 3.2.3 Cross-Modal Association
Binding visual percepts with proprioceptive state:
- **Spatial registration**: Transform sensor frames to common coordinate system
- **Temporal synchronization**: Align sensor timestamps, handle latency
- **Causality tracking**: Actions → expected observations → confirmation/revision

---

## 4. Recommended Architecture for LOGOS CWM-G

### 4.1 High-Level Design

```
Talos Sensors → Perception Pipeline → Grounded Entities → HCG Integration
     ↓                  ↓                    ↓                 ↓
[Raw Data]      [Feature Extraction]   [Symbolic Binding]  [Graph Updates]
  - Vision          - Object detection    - Entity matching  - Create/update nodes
  - Depth           - Pose estimation     - State encoding   - Update embeddings
  - IMU             - Segmentation        - Temporal linking - Causal edges
  - Force/Torque    - Feature vectors     - Uncertainty      - SHACL validation
```

### 4.2 Component Breakdown

#### 4.2.1 Perception Layer (Talos → CWM-G)

**Vision Processing Module**:
- **Input**: RGB images, depth maps from Talos camera sensors
- **Processing**:
  - Object detection (e.g., YOLOv8, DINO, Grounding-DINO)
  - Semantic segmentation (e.g., Mask R-CNN, SAM)
  - 6D pose estimation (e.g., PoseCNN, CosyPose)
  - Feature extraction for embedding (e.g., CLIP, DINOv2 features)
- **Output**: Detected entities with bounding boxes, poses, visual embeddings

**Proprioceptive Processing Module**:
- **Input**: Joint positions, velocities, torques from Talos
- **Processing**:
  - Forward kinematics for end-effector pose
  - Velocity estimation for motion state
  - Contact detection from force/torque thresholds
- **Output**: Robot state representation (joint states, end-effector pose, contact flags)

**Fusion Module** (Attention-Based):
- **Input**: Visual features + proprioceptive state
- **Processing**:
  - Cross-attention between visual object features and robot pose
  - Uncertainty estimation (e.g., Bayesian fusion, confidence scores)
  - Temporal filtering (e.g., Kalman filter for smoothing)
- **Output**: Grounded entities with multimodal confidence scores

#### 4.2.2 Grounding Layer (Features → HCG Entities)

**Entity Matching**:
- **Challenge**: Associate detected visual objects with existing HCG entities
- **Approach**:
  1. Query HCG for entities in expected spatial region (using proprioceptive context)
  2. Compute similarity between visual embeddings and HCG entity embeddings (Milvus search)
  3. Use Hungarian algorithm or association heuristics for matching
  4. Create new entity nodes for unmatched detections

**State Encoding**:
- **Create grounded State nodes** in HCG with properties:
  - `position`: [x, y, z] in world frame
  - `orientation`: Quaternion [w, x, y, z] or rotation matrix
  - `velocity`: [vx, vy, vz] if tracked over time
  - `bounding_box`: [xmin, ymin, width, height] in image space
  - `visual_embedding_id`: Reference to Milvus vector
  - `confidence`: Detection confidence score
  - `timestamp`: Sensor timestamp for temporal coherence
  - `sensor_modality`: "vision", "proprioception", "fused"

**Temporal Linking**:
- Create `(:State)-[:NEXT_STATE]->(:State)` relationships for tracking entity evolution
- Use `(:Process)-[:CAUSES]->(:State)` to link actions to resulting states
- Maintain temporal consistency through timestamp validation

#### 4.2.3 HCG Integration Layer

**Graph Updates**:
- **Create or update Entity nodes**:
  ```cypher
  MERGE (e:Entity {uuid: $entity_uuid})
  SET e.name = $detected_name,
      e.last_observed = timestamp()
  ```

- **Create grounded State nodes**:
  ```cypher
  CREATE (s:State {
    uuid: randomUUID(),
    entity_id: $entity_uuid,
    position: $position,
    orientation: $orientation,
    timestamp: $timestamp,
    confidence: $confidence,
    modality: $modality
  })
  ```

- **Link states to entities**:
  ```cypher
  MATCH (e:Entity {uuid: $entity_uuid})
  CREATE (e)-[:HAS_STATE]->(s)
  ```

**Vector Sync**:
- Store visual/multimodal embeddings in Milvus with metadata linking to HCG nodes
- Maintain bidirectional references:
  - HCG node → `embedding_id` property
  - Milvus vector → metadata fields with `entity_uuid`, `state_uuid`

**SHACL Validation**:
- Extend `shacl_shapes.ttl` to include grounded state constraints:
  - Position must be 3D float array
  - Orientation must be valid quaternion (normalized)
  - Timestamp must be within reasonable bounds
  - Confidence must be in [0, 1]

### 4.3 Handling Uncertainty and Temporal Dynamics

#### 4.3.1 Uncertainty Representation
- **Probabilistic properties**: Store confidence scores with each grounded state
- **Bounding representations**: Use bounding boxes/volumes instead of point estimates
- **Multi-hypothesis tracking**: Maintain multiple state hypotheses for ambiguous observations

#### 4.3.2 Temporal Coherence
- **Object persistence**: Track entities across frames using embedding similarity + spatial proximity
- **Prediction-correction loop**:
  1. Planner generates action plan
  2. Executor executes, CWM-G predicts expected sensor observations
  3. Compare predictions with actual Talos readings
  4. Update HCG with discrepancies (surprise signal for learning)

#### 4.3.3 Missing Modality Handling
- **Graceful degradation**: CWM-G should function with subset of sensors
- **Confidence weighting**: Reduce confidence scores when modalities are missing
- **Fallback strategies**: Use last-known state or CWM-A predictions when sensors fail

---

## 5. Integration with Talos

### 5.1 Talos API Requirements

Talos should expose the following sensor data streams:
1. **Vision**:
   - `GET /sensors/camera/rgb` → RGB image (JPEG/PNG)
   - `GET /sensors/camera/depth` → Depth map (float array or encoded image)
   - `GET /sensors/camera/intrinsics` → Camera calibration parameters
   
2. **Proprioception**:
   - `GET /sensors/joints` → Joint positions, velocities, torques (JSON array)
   - `GET /sensors/imu` → IMU readings: acceleration, gyroscope, orientation
   - `GET /sensors/end_effector` → End-effector pose (position + orientation)
   
3. **Tactile/Force**:
   - `GET /sensors/force_torque` → Force/torque sensor readings
   - `GET /sensors/tactile` → Tactile sensor array (if available)

4. **Actuator State**:
   - `GET /actuators/state` → Current actuator commands and feedback

### 5.2 Synchronization Strategy

**Timestamping**:
- All Talos sensor readings must include high-resolution timestamps
- Use common time reference (e.g., system monotonic clock or ROS time)

**Buffering**:
- CWM-G maintains short buffer (e.g., 1-2 seconds) of recent sensor data
- Allows retrospective fusion if sensors arrive at different rates

**Polling vs. Streaming**:
- **Phase 2**: Polling-based (CWM-G requests data at fixed rate, e.g., 10-30 Hz)
- **Phase 3**: Streaming-based (Talos pushes data via WebSocket or ROS topics)

### 5.3 Simulated Hardware for Phase 2

For testing without physical robot:
- **Simulated sensors**: Generate synthetic RGB, depth, joint states from simulated environment (e.g., PyBullet, Gazebo, Isaac Sim)
- **Noise injection**: Add realistic sensor noise to test robustness
- **Ground truth**: Provide perfect ground truth for validation

---

## 6. Phase 2 Implementation Roadmap

### 6.1 Milestone Breakdown

**M2.1: Perception Pipeline Prototype** (Weeks 1-3)
- Implement vision processing module (object detection + pose estimation)
- Implement proprioceptive processing module (forward kinematics)
- Create simulated Talos sensor interface
- Unit tests for each module

**M2.2: Grounding Layer** (Weeks 4-6)
- Implement entity matching algorithm
- Extend HCG ontology with grounded state properties
- Implement temporal state linking
- Integration tests with Neo4j + Milvus

**M2.3: Sensor Fusion** (Weeks 7-9)
- Implement attention-based fusion module
- Add uncertainty estimation
- Temporal filtering and object tracking
- Fusion accuracy benchmarks

**M2.4: End-to-End Integration** (Weeks 10-12)
- Wire CWM-G into Sophia Orchestrator
- Implement prediction-correction loop with Executor
- Test with "pick and place" scenario
- Demonstrate grounded planning (e.g., avoid detected obstacles)

### 6.2 Testing Strategy

**Unit Tests**:
- Each perception module tested with synthetic data
- Grounding layer tested with mock HCG
- Fusion module tested with simulated sensor streams

**Integration Tests**:
- CWM-G updates HCG correctly for known scenarios
- SHACL validation catches malformed grounded states
- Temporal consistency maintained over time

**Performance Tests**:
- Perception pipeline latency (target: < 100ms per frame)
- HCG update throughput (target: > 10 updates/sec)
- Vector search latency (target: < 50ms for entity matching)

**Validation Tests**:
- Compare CWM-G state against ground truth from simulator
- Measure object detection accuracy, pose estimation error
- Evaluate entity association accuracy

---

## 7. Open Research Questions

### 7.1 Symbolic-Subsymbolic Divide
**Question**: How to balance symbolic HCG representation with continuous neural representations?

**Options**:
- **Option A**: Store only symbolic summaries in HCG, keep continuous features in separate neural memory
- **Option B**: Store full embeddings in Milvus, use HCG only for relationships and metadata
- **Option C**: Hybrid approach with both symbolic properties and embedding references

**Recommendation**: Option C (hybrid) — aligns with HCG design philosophy.

### 7.2 Perceptual Abstraction
**Question**: At what level should vision features be abstracted for HCG?

**Options**:
- **Low-level**: Raw pixels, point clouds
- **Mid-level**: Object bounding boxes, segmentation masks, feature vectors
- **High-level**: Semantic labels, spatial relationships, affordances

**Recommendation**: Mid-level + high-level — low-level is too verbose for HCG, but keep embeddings for similarity search.

### 7.3 Temporal Granularity
**Question**: How frequently should CWM-G update HCG?

**Considerations**:
- Sensor rates: 30-60 Hz for vision, 100+ Hz for proprioception
- HCG update cost: Neo4j write latency
- Relevance: Not all observations are significant

**Recommendation**: Event-driven updates — only create new State nodes when significant changes detected (e.g., object moved > threshold, new object appeared).

### 7.4 Learning and Adaptation
**Question**: Should CWM-G learn from experience?

**Phase 2 approach**: Hand-crafted perception and fusion (no learning)

**Phase 3 potential**:
- Learn visual embeddings that align with HCG entity concepts
- Learn fusion weights from task performance
- Learn predictive models for forward simulation

---

## 8. Related Work and References

### 8.1 Robotic Perception Systems
- **Robotics Transformer (RT-1, RT-2)**: End-to-end vision-language-action models
  - Insight: Large-scale pre-training on vision-language data improves grounding
  - Limitation: Purely subsymbolic, lacks explicit causal structure
  
- **Probabilistic Robotics (Thrun et al.)**: Bayesian sensor fusion, SLAM, filtering
  - Insight: Probabilistic methods handle uncertainty and temporal dynamics
  - Application: Can integrate into LOGOS for uncertainty representation

### 8.2 Object-Centric Representations
- **Slot Attention (Locatello et al., 2020)**: Unsupervised object discovery
  - Insight: Perceptual grouping without supervision, entity-level representations
  - Application: Could replace/augment traditional object detection in CWM-G

- **Neural Scene Representations**: NeRFs, 3D Gaussian Splatting for scene modeling
  - Insight: Continuous 3D representations enable viewpoint-invariant reasoning
  - Application: Phase 3 could integrate 3D scene models for richer grounding

### 8.3 Symbolic-Subsymbolic Integration
- **Neuro-Symbolic AI**: Combining neural networks with symbolic reasoning
  - **NSIL (Neuro-Symbolic Integrated Learning)**: Learn symbolic rules from neural features
  - **Logical Neural Networks**: Differentiable logic for end-to-end training
  - Application: Potential approach for learning HCG structure from data

- **Concept Bottleneck Models**: Interpretable intermediate representations
  - Insight: Forces neural network to predict human-understandable concepts
  - Application: Could enforce alignment between visual features and HCG concepts

### 8.4 Grounding Language in Robotics
- **VLM-based Grounding**: CLIP, GLIP, Grounding DINO for open-vocabulary detection
  - Insight: Large vision-language models enable flexible semantic grounding
  - Application: Use for translating abstract commands (via CWM-A) to visual queries

- **Embodied AI**: Habitat, AI2-THOR, iGibson for simulated environments
  - Insight: Simulated grounding for testing before hardware deployment
  - Application: Phase 2 simulation infrastructure

---

## 9. Recommended Approach Summary

### 9.1 Core Design Principles
1. **Modularity**: Separate perception, grounding, and HCG integration layers
2. **Hybrid Fusion**: Use attention-based mechanisms for flexible multi-modal integration
3. **Symbolic Coherence**: Maintain HCG as primary knowledge representation, with embeddings for similarity
4. **Temporal Consistency**: Explicit causality tracking and temporal linking of states
5. **Uncertainty Awareness**: Represent and propagate confidence scores throughout pipeline

### 9.2 Minimal Viable CWM-G (Phase 2)
- **Vision**: Object detection + 6D pose estimation
- **Proprioception**: Joint states + end-effector pose
- **Fusion**: Late fusion with confidence weighting
- **HCG Integration**: Grounded State nodes with position, orientation, embeddings
- **Validation**: Extended SHACL shapes for grounded properties

### 9.3 Extensions for Phase 3
- **Advanced fusion**: Learned attention weights, multi-hypothesis tracking
- **Richer perception**: 3D scene representations, affordance prediction
- **Predictive models**: Forward simulation for planning, surprise detection
- **Learning**: Fine-tune perception models, learn entity embeddings

---

## 10. Next Steps

### 10.1 Immediate Actions (Post-R3)
1. **Update action_items.md**: Mark R3 as complete
2. **Create Phase 2 design document**: Expand this research into detailed technical specification
3. **Extend HCG ontology**: Add grounded state properties to `core_ontology.cypher`
4. **Extend SHACL shapes**: Add validation constraints for grounded states to `shacl_shapes.ttl`
5. **Define Talos sensor API contract**: Create `contracts/talos.openapi.yaml`

### 10.2 Phase 2 Kickoff Prerequisites
- [ ] Sophia repository with Orchestrator + CWM-A operational (from Phase 1)
- [ ] Talos repository initialized with simulated sensor interfaces
- [ ] HCG infrastructure running and validated (Neo4j + Milvus)
- [ ] Baseline perception models selected and tested

### 10.3 Team Assignments (TBD)
- **Perception Lead**: Vision and proprioceptive processing modules
- **Fusion Lead**: Multi-modal fusion and uncertainty handling
- **Integration Lead**: CWM-G ↔ HCG integration and temporal tracking
- **Simulation Lead**: Talos simulated environment and ground truth

---

## 11. Conclusion

Multi-modal grounding is essential for LOGOS to interact with the physical world. The recommended architecture integrates sensor fusion, entity matching, and HCG updates while maintaining the system's core philosophy of non-linguistic cognition. By treating sensory data as a grounding layer that populates the HCG with concrete states, LOGOS can bridge abstract reasoning with embodied action.

Phase 2 should focus on a minimal viable CWM-G that demonstrates:
- Reliable object detection and pose estimation from vision
- Accurate proprioceptive state tracking
- Effective fusion of modalities with uncertainty
- Seamless integration into the HCG for grounded planning

This foundation will enable Phase 3 learning and adaptation capabilities, ultimately realizing LOGOS's vision of causally coherent, non-linguistic autonomous agents.

---

**Document History**:
- 2025-11-19: Initial research document created (R3 completion)
