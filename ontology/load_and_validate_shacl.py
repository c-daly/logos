#!/usr/bin/env python3
"""
Load SHACL shapes into Neo4j via neosemantics (n10s) and run validation.

This script:
1. Initializes n10s in Neo4j
2. Loads SHACL shapes from shacl_shapes.ttl
3. Optionally loads test data (valid/invalid fixtures)
4. Runs SHACL validation and reports results
5. Exits with non-zero code on validation failures

Reference: docs/PHASE1_VERIFY.md, M2 section
"""

import argparse
import sys
from pathlib import Path

from neo4j import GraphDatabase
from rdflib import Graph


class Neo4jSHACLValidator:
    """Handles SHACL validation via Neo4j neosemantics."""

    def __init__(self, uri: str, user: str, password: str):
        """Initialize connection to Neo4j."""
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        """Close Neo4j connection."""
        self.driver.close()

    def initialize_n10s(self) -> bool:
        """
        Initialize neosemantics (n10s) in Neo4j.

        Creates the necessary graph configuration for RDF/SHACL support.
        Returns True on success, False on failure.
        """
        with self.driver.session() as session:
            try:
                # Check if n10s is available
                result = session.run(
                    "SHOW PROCEDURES YIELD name WHERE name STARTS WITH 'n10s' "
                    "RETURN count(name) AS count"
                )
                record = result.single()
                if not record:
                    print("✗ Failed to check n10s availability")
                    return False
                count = record["count"]
                if count == 0:
                    print("✗ n10s plugin not available in Neo4j")
                    print(
                        "  Please ensure NEO4J_PLUGINS includes 'n10s' in "
                        "docker-compose.hcg.dev.yml"
                    )
                    return False

                print(f"✓ n10s plugin available ({count} procedures)")

                # Initialize n10s graph configuration
                # First, check if config already exists
                result = session.run(
                    "CALL n10s.graphconfig.show() YIELD param, value RETURN count(*) AS count"
                )
                record = result.single()
                config_exists = record["count"] > 0 if record else False

                if config_exists:
                    print("✓ n10s graph configuration already exists")
                else:
                    # Create new configuration
                    session.run("""
                        CALL n10s.graphconfig.init({
                            handleVocabUris: 'IGNORE',
                            handleMultival: 'ARRAY',
                            handleRDFTypes: 'LABELS'
                        })
                        """)
                    print("✓ n10s graph configuration initialized")

                return True

            except Exception as e:
                print(f"✗ Failed to initialize n10s: {e}")
                return False

    def load_shacl_shapes(self, shapes_file: Path) -> bool:
        """
        Load SHACL shapes from TTL file into Neo4j via n10s.

        Args:
            shapes_file: Path to SHACL shapes TTL file

        Returns:
            True on success, False on failure
        """
        if not shapes_file.exists():
            print(f"✗ SHACL shapes file not found: {shapes_file}")
            return False

        # Read TTL file
        shapes_graph = Graph()
        try:
            shapes_graph.parse(shapes_file, format="turtle")
            print(f"✓ Loaded {len(shapes_graph)} SHACL triples from {shapes_file.name}")
        except Exception as e:
            print(f"✗ Failed to parse SHACL shapes: {e}")
            return False

        # Convert to N-Triples for n10s import
        shapes_ntriples = shapes_graph.serialize(format="nt")

        with self.driver.session() as session:
            try:
                # Import SHACL shapes using n10s
                result = session.run(
                    """
                    CALL n10s.rdf.import.inline($rdf, 'N-Triples')
                    YIELD terminationStatus, triplesLoaded
                    RETURN terminationStatus, triplesLoaded
                    """,
                    rdf=shapes_ntriples,
                )
                record = result.single()
                if not record:
                    print("✗ Failed to get import result")
                    return False

                status = record["terminationStatus"]
                triples = record["triplesLoaded"]

                if status == "OK":
                    print(f"✓ Loaded {triples} SHACL triples into Neo4j")
                    return True
                else:
                    print(f"✗ Failed to load SHACL shapes: {status}")
                    return False

            except Exception as e:
                print(f"✗ Failed to import SHACL shapes to Neo4j: {e}")
                return False

    def load_test_data(self, data_file: Path) -> bool:
        """
        Load test data from TTL file into Neo4j.

        Args:
            data_file: Path to test data TTL file

        Returns:
            True on success, False on failure
        """
        if not data_file.exists():
            print(f"✗ Test data file not found: {data_file}")
            return False

        # Read TTL file
        data_graph = Graph()
        try:
            data_graph.parse(data_file, format="turtle")
            print(f"✓ Loaded {len(data_graph)} data triples from {data_file.name}")
        except Exception as e:
            print(f"✗ Failed to parse test data: {e}")
            return False

        # Convert to N-Triples for n10s import
        data_ntriples = data_graph.serialize(format="nt")

        with self.driver.session() as session:
            try:
                result = session.run(
                    """
                    CALL n10s.rdf.import.inline($rdf, 'N-Triples')
                    YIELD terminationStatus, triplesLoaded
                    RETURN terminationStatus, triplesLoaded
                    """,
                    rdf=data_ntriples,
                )
                record = result.single()
                if not record:
                    print("✗ Failed to get import result")
                    return False

                status = record["terminationStatus"]
                triples = record["triplesLoaded"]

                if status == "OK":
                    print(f"✓ Loaded {triples} test data triples into Neo4j")
                    return True
                else:
                    print(f"✗ Failed to load test data: {status}")
                    return False

            except Exception as e:
                print(f"✗ Failed to import test data to Neo4j: {e}")
                return False

    def run_shacl_validation(self) -> tuple[bool, str]:
        """
        Run SHACL validation in Neo4j via n10s.

        Returns:
            Tuple of (conforms, validation_report)
        """
        with self.driver.session() as session:
            try:
                # Run SHACL validation
                result = session.run("""
                    CALL n10s.validation.shacl.validate()
                    YIELD focusNode, propertyShape, severity, resultMessage
                    RETURN focusNode, propertyShape, severity, resultMessage
                    """)

                violations = list(result)

                if not violations:
                    report = "✓ SHACL validation PASSED - no violations found"
                    return True, report
                else:
                    report_lines = [
                        "✗ SHACL validation FAILED - violations found:",
                        "",
                    ]
                    for i, violation in enumerate(violations, 1):
                        report_lines.append(f"Violation {i}:")
                        report_lines.append(f"  Focus Node: {violation['focusNode']}")
                        report_lines.append(
                            f"  Property Shape: {violation['propertyShape']}"
                        )
                        report_lines.append(f"  Severity: {violation['severity']}")
                        report_lines.append(f"  Message: {violation['resultMessage']}")
                        report_lines.append("")

                    report = "\n".join(report_lines)
                    return False, report

            except Exception as e:
                report = f"✗ Failed to run SHACL validation: {e}"
                return False, report

    def clear_graph(self) -> bool:
        """Clear all data from Neo4j graph."""
        with self.driver.session() as session:
            try:
                session.run("MATCH (n) DETACH DELETE n")
                print("✓ Cleared Neo4j graph")
                return True
            except Exception as e:
                print(f"✗ Failed to clear graph: {e}")
                return False


def main():
    """Main entry point for SHACL validation script."""
    parser = argparse.ArgumentParser(
        description="Load SHACL shapes into Neo4j and run validation"
    )
    parser.add_argument(
        "--uri",
        default="bolt://localhost:7687",
        help="Neo4j connection URI (default: bolt://localhost:7687)",
    )
    parser.add_argument(
        "--user",
        default="neo4j",
        help="Neo4j username (default: neo4j)",
    )
    parser.add_argument(
        "--password",
        default="neo4jtest",
        help="Neo4j password (default: neo4jtest)",
    )
    parser.add_argument(
        "--shapes",
        type=Path,
        help="Path to SHACL shapes TTL file (default: ontology/shacl_shapes.ttl)",
    )
    parser.add_argument(
        "--test-data",
        type=Path,
        help="Path to test data TTL file to validate (optional)",
    )
    parser.add_argument(
        "--clear",
        action="store_true",
        help="Clear graph before loading data",
    )
    parser.add_argument(
        "--skip-validation",
        action="store_true",
        help="Load shapes but skip validation (useful for setup)",
    )

    args = parser.parse_args()

    # Default shapes file location
    if args.shapes is None:
        script_dir = Path(__file__).parent
        args.shapes = script_dir / "shacl_shapes.ttl"

    print("=" * 70)
    print("LOGOS SHACL Validation via Neo4j n10s")
    print("=" * 70)
    print()

    validator = Neo4jSHACLValidator(args.uri, args.user, args.password)

    try:
        # Clear graph if requested
        if args.clear:
            if not validator.clear_graph():
                return 1

        # Initialize n10s
        if not validator.initialize_n10s():
            return 1

        # Load SHACL shapes
        if not validator.load_shacl_shapes(args.shapes):
            return 1

        # Load test data if provided
        if args.test_data:
            if not validator.load_test_data(args.test_data):
                return 1

        # Run validation unless skipped
        if not args.skip_validation:
            print()
            print("Running SHACL validation...")
            print()
            conforms, report = validator.run_shacl_validation()
            print(report)
            print()
            print("=" * 70)

            if conforms:
                print("✓ VALIDATION PASSED")
                print("=" * 70)
                return 0
            else:
                print("✗ VALIDATION FAILED")
                print("=" * 70)
                return 1
        else:
            print()
            print("=" * 70)
            print("✓ SHAPES LOADED (validation skipped)")
            print("=" * 70)
            return 0

    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
        return 130
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        import traceback

        traceback.print_exc()
        return 1
    finally:
        validator.close()


if __name__ == "__main__":
    sys.exit(main())
