"""
Example usage of the LOGOS Python SDKs (Hermes and Sophia clients).

This example demonstrates how to:
1. Connect to Hermes and Sophia services
2. Generate text embeddings with Hermes
3. Create a plan with Sophia
4. Query the current state
5. Run a simulation

Prerequisites:
- Hermes service running on http://localhost:8080
- Sophia service running on http://localhost:8000
- Both services connected to the HCG (Neo4j + Milvus)
"""

from hermes_client import ApiClient as HermesClient
from hermes_client import Configuration as HermesConfig
from hermes_client.api import default_api as hermes_api
from sophia_client import ApiClient as SophiaClient
from sophia_client import Configuration as SophiaConfig
from sophia_client.api import default_api as sophia_api


def hermes_example():
    """Example usage of Hermes SDK."""
    print("\n=== Hermes SDK Example ===\n")

    # Configure Hermes client
    hermes_config = HermesConfig(host="http://localhost:8080")
    hermes_client = HermesClient(configuration=hermes_config)
    api = hermes_api.DefaultApi(hermes_client)

    # 1. Generate text embeddings
    print("1. Generating text embeddings...")
    embed_request = {
        "text": "The red block is on the table",
        "model": "default"
    }
    try:
        embed_response = api.embed_text(embed_request)
        print(f"   ✓ Embedding generated: {embed_response.dimension} dimensions")
        print(f"   ✓ Model: {embed_response.model}")
        print(f"   ✓ First 5 values: {embed_response.embedding[:5]}")
    except Exception as e:
        print(f"   ✗ Error: {e}")

    # 2. Simple NLP processing
    print("\n2. Processing text with NLP...")
    nlp_request = {
        "text": "The quick brown fox jumps over the lazy dog",
        "operations": ["tokenize", "pos_tag"]
    }
    try:
        nlp_response = api.simple_nlp(nlp_request)
        print(f"   ✓ Tokens: {nlp_response.tokens}")
        if nlp_response.pos_tags:
            print(f"   ✓ POS tags: {[(t['token'], t['tag']) for t in nlp_response.pos_tags[:5]]}")
    except Exception as e:
        print(f"   ✗ Error: {e}")

    # 3. Text-to-Speech (note: returns binary data)
    print("\n3. Text-to-Speech conversion...")
    tts_request = {
        "text": "Hello from LOGOS",
        "language": "en-US"
    }
    try:
        tts_response = api.text_to_speech(tts_request)
        print(f"   ✓ Audio generated: {len(tts_response)} bytes")
    except Exception as e:
        print(f"   ✗ Error: {e}")


def sophia_example():
    """Example usage of Sophia SDK."""
    print("\n=== Sophia SDK Example ===\n")

    # Configure Sophia client
    sophia_config = SophiaConfig(host="http://localhost:8000")
    sophia_client = SophiaClient(configuration=sophia_config)
    api = sophia_api.DefaultApi(sophia_client)

    # 1. Check health status
    print("1. Checking Sophia health...")
    try:
        health = api.get_health()
        print(f"   ✓ Status: {health.status}")
        print(f"   ✓ Neo4j connected: {health.neo4j.connected}")
        print(f"   ✓ Milvus collections: {health.milvus.collections}")
    except Exception as e:
        print(f"   ✗ Error: {e}")

    # 2. Generate a plan
    print("\n2. Generating a plan...")
    plan_request = {
        "goal": "Pick up the red block and place it in the bin",
        "goal_state": {
            "entities": [
                {
                    "entity_id": "block_red_001",
                    "desired_state": "in_bin"
                }
            ]
        },
        "context": {
            "environment": "table_workspace",
            "available_capabilities": ["grasp_object", "move_arm", "release_object"]
        }
    }
    try:
        plan = api.generate_plan(plan_request)
        print(f"   ✓ Plan ID: {plan.plan_id}")
        print(f"   ✓ Number of processes: {len(plan.processes)}")
        print(f"   ✓ Confidence: {plan.confidence:.2f}")

        if plan.processes:
            print("\n   Processes:")
            for i, proc in enumerate(plan.processes, 1):
                print(f"     {i}. {proc.name} (capability: {proc.capability_id})")
    except Exception as e:
        print(f"   ✗ Error: {e}")

    # 3. Query current state
    print("\n3. Querying current state...")
    try:
        state = api.get_state(limit=5, model_type="CWM_A", status="observed")
        print(f"   ✓ Retrieved {len(state.states)} states")

        if state.states:
            print("\n   Recent states:")
            for s in state.states[:3]:
                print(f"     - {s.state_id}: {s.model_type} ({s.status})")
                print(f"       Confidence: {s.confidence:.2f}, Source: {s.source}")
    except Exception as e:
        print(f"   ✗ Error: {e}")

    # 4. Run simulation
    print("\n4. Running simulation...")
    sim_request = {
        "capability_id": "grasp_object",
        "context": {
            "entity_ids": ["block_red_001", "gripper_001"],
            "horizon_steps": 5,
            "talos_metadata": {
                "force_threshold": 5.0,
                "approach_velocity": 0.1
            }
        }
    }
    try:
        sim = api.run_simulation(sim_request)
        print(f"   ✓ Simulation ID: {sim.simulation_id}")
        print(f"   ✓ Imagined states: {len(sim.imagined_states)}")
        print(f"   ✓ Predicted outcomes: {len(sim.predicted_outcomes)}")

        if sim.metadata:
            print("\n   Metadata:")
            print(f"     Model version: {sim.metadata.model_version}")
            print(f"     Horizon: {sim.metadata.horizon} steps")
    except Exception as e:
        print(f"   ✗ Error: {e}")


def main():
    """Run all examples."""
    print("\n" + "="*60)
    print("LOGOS SDK Examples")
    print("="*60)

    print("\nNote: These examples require running Hermes and Sophia services.")
    print("If services are not available, you will see connection errors.\n")

    # Run Hermes examples
    hermes_example()

    # Run Sophia examples
    sophia_example()

    print("\n" + "="*60)
    print("Examples complete!")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()
