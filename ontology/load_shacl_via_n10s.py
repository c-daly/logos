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

        # Initialize graph config to be namespace aware
        print("Initializing n10s graph configuration (MAP vocab URIs)...")
        session.run(
            """
            CALL n10s.graphconfig.init({
              handleVocabUris: 'MAP',
              handleMultival: 'ARRAY',
              keepLangTag: true,
              handleRDFTypes: 'LABELS'
            })
            """
        )

        # Register prefix for logos ontology to satisfy namespace requirement
        session.run(
            "CALL n10s.nsprefixes.add('logos', 'http://logos.ontology/')"
        )

        print(f"Loading SHACL shapes inline from {shapes_path} ...")
        # Import shapes; n10s returns no rows if called without YIELD
        session.run(
            """
            CALL n10s.validation.shacl.import.inline($rdf, "Turtle")
            """,
            rdf=rdf_text,
        )

        # Verify shapes are present
        shapes_count = session.run(
            "CALL n10s.validation.shacl.listShapes() YIELD name RETURN count(*) AS count"
        ).single()["count"]

        print(f"✓ SHACL shapes loaded via n10s; shapes listed: {shapes_count}")
        if shapes_count == 0:
            print("✗ No SHACL shapes found after import", file=sys.stderr)
            return 1

    print("✓ SHACL shapes loaded via n10s")
    return 0


if __name__ == "__main__":
    sys.exit(main())
