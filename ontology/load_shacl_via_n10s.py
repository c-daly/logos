#!/usr/bin/env python3
"""
Load SHACL shapes into Neo4j via n10s and print the detailed response.

This script is meant for CI/use in GitHub Actions to surface the actual n10s
error message when a load fails (status: "KO"). It exits non-zero on failure.
"""

import argparse
import sys
from pathlib import Path

from neo4j import GraphDatabase


def main() -> int:
    parser = argparse.ArgumentParser(description="Load SHACL shapes via n10s and report status.")
    parser.add_argument("--uri", required=True, help="Neo4j Bolt URI, e.g., bolt://localhost:7687")
    parser.add_argument("--user", required=True, help="Neo4j username")
    parser.add_argument("--password", required=True, help="Neo4j password")
    parser.add_argument("--shapes", required=True, help="Path to SHACL shapes file, accessible to Neo4j (file:///...)")

    args = parser.parse_args()

    driver = GraphDatabase.driver(args.uri, auth=(args.user, args.password))

    # Read shapes file and import inline to avoid container file-path issues
    shapes_path = Path(args.shapes)
    if not shapes_path.exists():
        print(f"✗ SHACL shapes file not found: {shapes_path}", file=sys.stderr)
        return 1

    rdf_text = shapes_path.read_text(encoding="utf-8")

    with driver.session(database="neo4j") as session:
        print("Clearing existing SHACL shapes...")
        session.run("CALL n10s.validation.shacl.clear();")

        print(f"Loading SHACL shapes inline from {shapes_path} ...")
        result = session.run(
            """
            CALL n10s.validation.shacl.import.inline($rdf, "Turtle")
            YIELD status, extraInfo, triplesLoaded
            RETURN status, extraInfo, triplesLoaded
            """,
            rdf=rdf_text,
        ).single()

        status = result["status"] if result else None
        extra = result["extraInfo"] if result else None
        loaded = result["triplesLoaded"] if result else None

        print(f"status: {status}, triplesLoaded: {loaded}")
        if extra:
            print(f"extraInfo: {extra}")

        if status != "OK":
            print("✗ Failed to load SHACL shapes via n10s", file=sys.stderr)
            return 1

    print("✓ SHACL shapes loaded via n10s")
    return 0


if __name__ == "__main__":
    sys.exit(main())
