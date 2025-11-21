# Perception Pipeline - Talos/Gazebo Integration Guide

## Overview

The LOGOS perception pipeline supports two modes of operation:

1. **CPU-friendly mode** (Talos-free): For scenarios without hardware, using lightweight simulation
2. **Hardware simulator mode**: Integration with Talos/Gazebo for physics-based simulation

This guide describes how to connect hardware simulators to the perception pipeline.

## Architecture

```
┌─────────────────┐
│  Media Ingest   │  ← Frames from uploads/streams
│    Service      │
└────────┬────────┘
         │
         v
┌─────────────────┐
│  JEPA Runner    │  ← k-step imagination rollout
│                 │
│  ┌───────────┐  │
│  │ CPU Mode  │  │  (default: Phase 2)
│  └───────────┘  │
│                 │
│  ┌───────────┐  │
│  │ Hardware  │  │  (optional: Talos/Gazebo)
│  │ Sim Mode  │  │
│  └───────────┘  │
└────────┬────────┘
         │
         v
┌─────────────────┐
│  Neo4j/Milvus   │  ← ImaginedProcess/ImaginedState storage
│      HCG        │
└─────────────────┘
```

## CPU-Friendly Mode (Default)

The default JEPA runner operates without hardware dependencies.

## Hardware Simulator Mode (Talos/Gazebo)

For physics-based simulation, connect the JEPA runner to Talos/Gazebo.

See `logos_perception/jepa_runner.py` for implementation details.

## References

- Phase 2 Spec: `docs/phase2/PHASE2_SPEC.md` (Perception Workflows section)
- JEPA Runner: `logos_perception/jepa_runner.py`
- Simulation Service: `logos_sophia/simulation.py`
