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
        # Verify n10s procedures are available
        procedures = [
            p[0]
            for p in session.run(
                "SHOW PROCEDURES YIELD name WHERE name STARTS WITH 'n10s' RETURN name"
            ).values()
        ]

        if not procedures:
            print("✗ n10s procedures not found. Check plugin installation.", file=sys.stderr)
            return 1

        # Clear existing shapes if possible
        if "n10s.validation.shacl.clear" in procedures:
            print("Clearing existing SHACL shapes with n10s.validation.shacl.clear()...")
            session.run("CALL n10s.validation.shacl.clear();")
        elif "n10s.validation.shacl.dropShapes" in procedures:
            print("Clearing existing SHACL shapes with n10s.validation.shacl.dropShapes()...")
            session.run("CALL n10s.validation.shacl.dropShapes();")
        else:
            print("⚠️ No SHACL clear/drop procedure available; continuing without clearing existing shapes.")

        print(f"Loading SHACL shapes inline from {shapes_path} ...")
        rec = session.run(
            """
            CALL n10s.validation.shacl.import.inline($rdf, "Turtle")
            YIELD *
            RETURN *
            """,
            rdf=rdf_text,
        ).single()

        if not rec:
            print("✗ No response from n10s.import.inline", file=sys.stderr)
            return 1

        data = rec.data()
        print(f"Import response fields: {list(data.keys())}")
        print(f"Import response values: {data}")

        # Determine status
        status = data.get("status") or data.get("terminationStatus")
        extra = data.get("extraInfo")
        loaded = data.get("triplesLoaded") or data.get("triplesloaded") or data.get("loaded")

        if status:
            print(f"status: {status}")
        if loaded is not None:
            print(f"triplesLoaded: {loaded}")
        if extra:
            print(f"extraInfo: {extra}")

        # Fail if an explicit status is present and not OK
        if status and str(status).upper() != "OK":
            print("✗ Failed to load SHACL shapes via n10s", file=sys.stderr)
            return 1

    print("✓ SHACL shapes loaded via n10s")
    return 0


if __name__ == "__main__":
    sys.exit(main())
