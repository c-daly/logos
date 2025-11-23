#!/usr/bin/env python3
"""
Example usage of the P2-M4 observability, persona, and CWM-E modules.

This demonstrates the integration of:
- OpenTelemetry structured logging
- Persona diary entries
- CWM-E emotion state generation

Run this after starting Neo4j:
    docker compose -f infra/docker-compose.hcg.dev.yml up -d
    python examples/p2_m4_demo.py
"""

from neo4j import GraphDatabase

from logos_cwm_e import CWMEReflector
from logos_observability import TelemetryExporter, get_logger, setup_telemetry
from logos_persona import PersonaDiary


def main():
    print("=" * 60)
    print("P2-M4 Demo: Observability, Persona, and CWM-E")
    print("=" * 60)
    print()

    # 1. Setup OpenTelemetry
    print("1. Setting up OpenTelemetry...")
    setup_telemetry(service_name="p2-m4-demo", export_to_console=False)
    logger = get_logger("p2-m4-demo")
    exporter = TelemetryExporter(output_dir="/tmp/logos_telemetry")
    print("   ✓ Telemetry configured")
    print()

    # 2. Connect to Neo4j (adjust credentials as needed)
    print("2. Connecting to Neo4j...")
    try:
        driver = GraphDatabase.driver(
            "bolt://localhost:7687", auth=("neo4j", "logosdev")
        )
        print("   ✓ Connected to Neo4j")
    except Exception as e:
        print(f"   ✗ Failed to connect to Neo4j: {e}")
        print("   Make sure Neo4j is running:")
        print("   docker compose -f infra/docker-compose.hcg.dev.yml up -d")
        return
    print()

    # 3. Create persona diary entries
    print("3. Creating persona diary entries...")
    diary = PersonaDiary(driver)

    entries = [
        {
            "summary": "Successfully completed pick-and-place task",
            "sentiment": "confident",
        },
        {
            "summary": "Encountered obstacle during path planning",
            "sentiment": "cautious",
        },
        {
            "summary": "Exploring new object manipulation strategies",
            "sentiment": "curious",
        },
    ]

    for entry_data in entries:
        entry = diary.create_entry(**entry_data)
        logger.log_persona_entry(
            entry_uuid=entry.uuid,
            summary=entry.summary,
            sentiment=entry.sentiment,
        )
        print(f"   ✓ Created entry: {entry.summary[:50]}...")

    print()

    # 4. Run CWM-E reflection
    print("4. Running CWM-E reflection...")
    reflector = CWMEReflector(driver)
    emotions = reflector.reflect_on_persona_entries(limit=10)

    for emotion in emotions:
        logger.log_emotion_state(
            emotion_uuid=emotion.uuid,
            emotion_type=emotion.emotion_type,
            intensity=emotion.intensity,
            context=emotion.context,
        )
        print(
            f"   ✓ Generated emotion: {emotion.emotion_type} (intensity: {emotion.intensity})"
        )

    print()

    # 5. Query recent persona entries
    print("5. Querying recent persona entries...")
    recent_entries = diary.get_recent_entries(limit=5)
    for entry in recent_entries:
        print(f"   - [{entry.sentiment}] {entry.summary[:60]}...")

    print()

    # 6. Get sentiment summary
    print("6. Sentiment distribution:")
    sentiment_summary = diary.get_sentiment_summary()
    for sentiment, count in sentiment_summary.items():
        print(f"   - {sentiment}: {count}")

    print()

    # 7. Show telemetry summary
    print("7. Telemetry summary:")
    telemetry_summary = exporter.get_summary()
    print(f"   Output directory: {telemetry_summary['output_dir']}")
    print(f"   Total files: {telemetry_summary['total_files']}")
    for event_type, count in telemetry_summary.get("event_types", {}).items():
        print(f"   - {event_type}: {count} events")

    print()

    # 8. Cleanup
    driver.close()

    print("=" * 60)
    print("Demo complete!")
    print()
    print("Next steps:")
    print("- View telemetry: ls -la /tmp/logos_telemetry/")
    print("- Query Neo4j: MATCH (pe:PersonaEntry) RETURN pe LIMIT 5")
    print("- Query emotions: MATCH (es:EmotionState) RETURN es LIMIT 5")
    print("=" * 60)


if __name__ == "__main__":
    main()
