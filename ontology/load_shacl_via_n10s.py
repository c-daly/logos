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
from neo4j.exceptions import Neo4jError


def configure_n10s(session, vocab_mode: str = "MAP") -> None:
    """Reset n10s graph config and set vocab handling/prefixes."""
    print(f"Configuring n10s graph (drop + init; handleVocabUris={vocab_mode})...")
    try:
        session.run("CALL n10s.graphconfig.drop()")
    except Neo4jError as exc:  # drop can fail if no config exists yet
        print(f"Graph config drop warning (ignored): {exc}")

    session.run(
        """
        CALL n10s.graphconfig.init({
          handleVocabUris: $vocab_mode,
          handleRDFTypes: 'LABELS',
          handleMultival: 'ARRAY',
          keepLangTag: true
        });
        """,
        vocab_mode=vocab_mode,
    )

    # Ensure prefix is registered so n10s keeps full IRIs instead of stripping them
    try:
        session.run("CALL n10s.nsprefixes.remove('logos')")
    except Neo4jError:
        pass
    session.run("CALL n10s.nsprefixes.add('logos', 'http://logos.ontology/')")

    cfg = {
        record["param"]: record["value"] for record in session.run("CALL n10s.graphconfig.show()")
    }
    print(f"n10s graph config now: {cfg}")


def import_shapes(session, rdf_text: str) -> None:
    session.run(
        """
        CALL n10s.validation.shacl.import.inline($rdf, "Turtle")
        """,
        rdf=rdf_text,
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Load SHACL shapes via n10s and report status.")
    parser.add_argument("--uri", required=True, help="Neo4j Bolt URI, e.g., bolt://localhost:7687")
    parser.add_argument("--user", required=True, help="Neo4j username")
    parser.add_argument("--password", required=True, help="Neo4j password")
    parser.add_argument(
        "--shapes",
        required=True,
        help="Path to SHACL shapes file, accessible to Neo4j (file:///...)",
    )

    args = parser.parse_args()

    driver = GraphDatabase.driver(args.uri, auth=(args.user, args.password))

    # Read shapes file and import inline to avoid container file-path issues
    shapes_path = Path(args.shapes)
    if not shapes_path.exists():
        print(f"✗ SHACL shapes file not found: {shapes_path}", file=sys.stderr)
        return 1

    rdf_text = shapes_path.read_text(encoding="utf-8")
    rdf_rewritten = rdf_text.replace("http://logos.ontology/", "neo4j://graph.schema#")

    try:
        with driver.session(database="neo4j") as session:
            # Verify n10s procedures are available
            procedures = [
                p[0]
                for p in session.run(
                    "SHOW PROCEDURES YIELD name WHERE name STARTS WITH 'n10s' RETURN name"
                ).values()
            ]

            if not procedures:
                print(
                    "✗ n10s procedures not found. Check plugin installation.",
                    file=sys.stderr,
                )
                return 1

            # Clear existing shapes if possible
            if "n10s.validation.shacl.clear" in procedures:
                print("Clearing existing SHACL shapes with n10s.validation.shacl.clear()...")
                session.run("CALL n10s.validation.shacl.clear();")
            elif "n10s.validation.shacl.dropShapes" in procedures:
                print(
                    "Clearing existing SHACL shapes with "
                    "n10s.validation.shacl.dropShapes()..."
                )
                session.run("CALL n10s.validation.shacl.dropShapes();")
            else:
                print(
                    "⚠️ No SHACL clear/drop procedure available; "
                    "continuing without clearing existing shapes."
                )

            configure_n10s(session, vocab_mode="MAP")

            print(f"Loading SHACL shapes inline from {shapes_path} ...")
            try:
                import_shapes(session, rdf_rewritten)
            except Neo4jError as exc:
                # Retry with SHORTEN if namespace-awareness still not honored
                if "UriNamespaceHasNoAssociatedPrefix" in str(exc):
                    print(
                        "Namespace error during import; "
                        "retrying after reconfiguring with SHORTEN..."
                    )
                    configure_n10s(session, vocab_mode="SHORTEN")
                    try:
                        import_shapes(session, rdf_rewritten)
                    except Neo4jError as exc2:
                        if "UriNamespaceHasNoAssociatedPrefix" in str(exc2):
                            print(
                                "Namespace error persists even after "
                                "rewrite/SHORTEN; aborting."
                            )
                            raise
                        else:
                            raise
                else:
                    raise

            # Verify shapes are present
            shapes_rows = session.run("CALL n10s.validation.shacl.listShapes()").data()
            shapes_count = len(shapes_rows)

            print(f"✓ SHACL shapes loaded via n10s; shapes listed: {shapes_count}")
            if shapes_count == 0:
                print("✗ No SHACL shapes found after import", file=sys.stderr)
                return 1
    except Neo4jError as exc:
        print(f"✗ Neo4j error during SHACL load: {exc}", file=sys.stderr)
        return 1

    print("✓ SHACL shapes loaded via n10s")
    return 0


if __name__ == "__main__":
    sys.exit(main())
