"""
HCG Data Loader - Loads ontology and seed entities into Neo4j.

This script provides a deterministic way to bootstrap the HCG with:
1. Core ontology (constraints, indexes, bootstrap types)
2. Optional seed data

Usage:
    python -m logos_hcg.load_hcg --uri bolt://localhost:7687 --user neo4j --password neo4jtest

    Or with environment variables:
    NEO4J_URI=bolt://localhost:7687 python -m logos_hcg.load_hcg

See Project LOGOS spec: Section 4.1 (Core Ontology and Data Model)
Reference: docs/plans/2025-12-30-flexible-ontology-design.md
"""

import argparse
import logging
import os
import sys
from pathlib import Path

from neo4j import GraphDatabase
from neo4j.exceptions import Neo4jError, ServiceUnavailable

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class HCGLoader:
    """Loads HCG ontology and seed data into Neo4j."""

    def __init__(self, uri: str, user: str, password: str):
        """
        Initialize loader with Neo4j connection.

        Args:
            uri: Neo4j connection URI (e.g., "bolt://localhost:7687")
            user: Neo4j username
            password: Neo4j password
        """
        self.uri = uri
        self.user = user
        try:
            self.driver = GraphDatabase.driver(uri, auth=(user, password))
            self.driver.verify_connectivity()
            logger.info(f"Connected to Neo4j at {uri}")
        except ServiceUnavailable as e:
            logger.error(f"Failed to connect to Neo4j at {uri}: {e}")
            raise

    def close(self):
        """Close the driver connection."""
        if self.driver:
            self.driver.close()
            logger.info("Closed Neo4j connection")

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()

    def load_cypher_file(self, file_path: Path, description: str) -> bool:
        """
        Load a Cypher script file into Neo4j.

        Args:
            file_path: Path to the .cypher file
            description: Human-readable description of what's being loaded

        Returns:
            True if successful, False otherwise
        """
        if not file_path.exists():
            logger.error(f"File not found: {file_path}")
            return False

        logger.info(f"Loading {description} from {file_path.name}...")

        try:
            with open(file_path) as f:
                script_content = f.read()

            # Parse Cypher statements more carefully
            # Remove single-line comments
            lines = []
            for line in script_content.split("\n"):
                # Remove inline comments
                if "//" in line:
                    line = line[: line.index("//")]
                line = line.strip()
                if line:
                    lines.append(line)

            # Join lines and split by semicolons
            cleaned_script = " ".join(lines)
            statements = [s.strip() for s in cleaned_script.split(";") if s.strip()]

            with self.driver.session() as session:
                for i, statement in enumerate(statements):
                    # Skip empty statements
                    if not statement:
                        continue

                    try:
                        result = session.run(statement)
                        # Consume result to ensure execution
                        summary = result.consume()

                        # Log meaningful operations
                        counters = summary.counters
                        if counters.constraints_added > 0:
                            logger.info(f"  Added {counters.constraints_added} constraint(s)")
                        if counters.indexes_added > 0:
                            logger.info(f"  Added {counters.indexes_added} index(es)")
                        if counters.nodes_created > 0:
                            logger.info(f"  Created {counters.nodes_created} node(s)")
                        if counters.relationships_created > 0:
                            logger.info(
                                f"  Created {counters.relationships_created} relationship(s)"
                            )

                    except Neo4jError as e:
                        # Some errors are expected (e.g., constraint already exists)
                        if "already exists" in str(e).lower() or "equivalent" in str(e).lower():
                            logger.debug("  (skipped - already exists)")
                        else:
                            logger.warning(f"  Warning on statement {i+1}: {e}")
                            # Continue with other statements

            logger.info(f"Loaded {description}")
            return True

        except Exception as e:
            logger.error(f"Failed to load {description}: {e}")
            return False

    def verify_constraints(self) -> dict:
        """
        Verify that required constraints exist.

        Returns:
            Dictionary with constraint counts
        """
        logger.info("Verifying constraints...")

        with self.driver.session() as session:
            result = session.run("SHOW CONSTRAINTS")
            constraints = [record["name"] for record in result]

        # Flexible ontology has one constraint
        required_constraints = [
            "logos_node_uuid",
        ]

        found = {}
        for constraint in required_constraints:
            exists = any(constraint in c for c in constraints)
            found[constraint] = exists
            status = "found" if exists else "MISSING"
            logger.info(f"  {constraint}: {status}")

        return found

    def verify_indexes(self) -> dict:
        """
        Verify that required indexes exist.

        Returns:
            Dictionary with index counts
        """
        logger.info("Verifying indexes...")

        with self.driver.session() as session:
            result = session.run("SHOW INDEXES")
            indexes = [record["name"] for record in result]

        required_indexes = [
            "logos_node_type",
            "logos_node_name",
            "logos_node_is_type_def",
        ]

        found = {}
        for index in required_indexes:
            exists = any(index in i for i in indexes)
            found[index] = exists
            status = "found" if exists else "MISSING"
            logger.info(f"  {index}: {status}")

        return found

    def verify_bootstrap_types(self) -> int:
        """
        Verify that bootstrap type definitions are loaded.

        Returns:
            Number of type definitions found
        """
        logger.info("Verifying bootstrap types...")

        with self.driver.session() as session:
            result = session.run("MATCH (t:Node {is_type_definition: true}) RETURN t.name as name")
            types = [record["name"] for record in result]

        expected = ["type_definition", "edge_type", "thing", "concept"]
        for t in expected:
            status = "found" if t in types else "MISSING"
            logger.info(f"  {t}: {status}")

        return len(types)

    def verify_nodes(self) -> dict:
        """
        Verify node counts by type.

        Returns:
            Dictionary with counts by type
        """
        logger.info("Verifying nodes...")

        with self.driver.session() as session:
            result = session.run(
                """
                MATCH (n:Node)
                RETURN n.type as type, n.is_type_definition as is_type_def, count(n) as count
                ORDER BY type
            """
            )
            counts = {}
            for record in result:
                type_name = record["type"]
                is_type_def = record["is_type_def"]
                count = record["count"]
                label = f"{type_name} ({'type' if is_type_def else 'instance'})"
                counts[label] = count

        for type_label, count in counts.items():
            logger.info(f"  {type_label}: {count}")

        return counts

    def create_seed_entities(self) -> bool:
        """
        Create canonical seed entities using the flexible ontology.

        These are minimal entities for verification purposes.

        Returns:
            True if successful, False otherwise
        """
        logger.info("Creating seed entities...")

        # Create type definitions and instances using the new schema
        seed_queries = [
            # Create manipulator type (subtype of thing)
            """
            MATCH (thing:Node {name: 'thing'})
            MERGE (m:Node {uuid: '3bed753e-51ad-5f8f-bb3a-1f7dc39ae01c'})
            SET m.name = 'manipulator',
                m.is_type_definition = true,
                m.type = 'manipulator',
                m.ancestors = ['thing'],
                m.description = 'A robotic manipulator or arm capable of movement and grasping'
            MERGE (m)-[:IS_A]->(thing)
            """,
            # Create RobotArm entity (instance of manipulator)
            """
            MATCH (m:Node {name: 'manipulator'})
            MERGE (e:Node {uuid: 'entity-robot-arm-01'})
            SET e.name = 'RobotArm01',
                e.is_type_definition = false,
                e.type = 'manipulator',
                e.ancestors = ['manipulator', 'thing'],
                e.description = 'Canonical six-axis robotic manipulator'
            MERGE (e)-[:IS_A]->(m)
            """,
            # Create 'state' type under concept
            """
            MATCH (concept:Node {name: 'concept'})
            MERGE (s:Node {uuid: '2dd3d0d8-569f-5132-b4a1-7ec30dc2d92b'})
            SET s.name = 'state',
                s.is_type_definition = true,
                s.type = 'state',
                s.ancestors = ['concept'],
                s.description = 'A temporal snapshot of entity properties'
            MERGE (s)-[:IS_A]->(concept)
            """,
            # Create initial state for RobotArm
            """
            MATCH (state_type:Node {name: 'state'})
            MERGE (s:Node {uuid: 'state-robot-arm-01-idle'})
            SET s.name = 'RobotArm01-Idle',
                s.is_type_definition = false,
                s.type = 'state',
                s.ancestors = ['state', 'concept'],
                s.description = 'Robot arm in idle state',
                s.timestamp = datetime()
            MERGE (s)-[:IS_A]->(state_type)
            """,
            # Link state to entity
            """
            MATCH (e:Node {uuid: 'entity-robot-arm-01'})
            MATCH (s:Node {uuid: 'state-robot-arm-01-idle'})
            MERGE (e)-[:HAS_STATE]->(s)
            """,
        ]

        try:
            with self.driver.session() as session:
                for query in seed_queries:
                    result = session.run(query)
                    result.consume()

            logger.info("Seed entities created")
            return True

        except Neo4jError as e:
            logger.error(f"Failed to create seed entities: {e}")
            return False

    def load_all(self, repo_root: Path) -> bool:
        """
        Load all ontology and seed data.

        Args:
            repo_root: Root path of the repository

        Returns:
            True if successful, False otherwise
        """
        logger.info("=" * 60)
        logger.info("HCG Data Loader - Loading Ontology and Seed Data")
        logger.info("=" * 60)

        # Step 1: Load core ontology
        ontology_path = repo_root / "ontology" / "core_ontology.cypher"
        if not self.load_cypher_file(ontology_path, "core ontology"):
            return False

        # Step 2: Verify ontology loaded correctly
        logger.info("")
        constraints = self.verify_constraints()
        self.verify_indexes()
        bootstrap_count = self.verify_bootstrap_types()

        # Check if basic requirements are met
        if not all(constraints.values()):
            logger.warning("Some constraints are missing - they may have been created previously")

        if bootstrap_count < 4:
            logger.warning("Some bootstrap types are missing")

        # Step 3: Create seed entities
        logger.info("")
        if not self.create_seed_entities():
            return False

        # Step 4: Final verification
        logger.info("")
        counts = self.verify_nodes()

        logger.info("")
        logger.info("=" * 60)
        logger.info("HCG Loading Complete")
        logger.info("=" * 60)
        logger.info(f"  Total nodes: {sum(counts.values())}")
        logger.info("")
        logger.info("Access Neo4j Browser at: http://localhost:7474")
        logger.info(f"  Username: {self.user}")
        logger.info("")
        logger.info("Try running queries like:")
        logger.info("  MATCH (n:Node) RETURN n.type, n.name, n.is_type_definition LIMIT 20;")
        logger.info("  MATCH (n:Node {is_type_definition: true}) RETURN n.name, n.ancestors;")
        logger.info("  MATCH (n:Node)-[:IS_A]->(t:Node) RETURN n.name, t.name;")
        logger.info("")

        return True


def main():
    """Main entry point for the HCG loader."""
    parser = argparse.ArgumentParser(description="Load LOGOS HCG ontology and seed data into Neo4j")
    parser.add_argument(
        "--uri",
        default=os.getenv("NEO4J_URI", "bolt://localhost:7687"),
        help="Neo4j connection URI (default: bolt://localhost:7687)",
    )
    parser.add_argument(
        "--user",
        default=os.getenv("NEO4J_USER", "neo4j"),
        help="Neo4j username (default: neo4j)",
    )
    parser.add_argument(
        "--password",
        default=os.getenv("NEO4J_PASSWORD", "neo4jtest"),
        help="Neo4j password (default: neo4jtest)",
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path(__file__).parent.parent,
        help="Repository root path (default: auto-detected)",
    )

    args = parser.parse_args()

    try:
        with HCGLoader(args.uri, args.user, args.password) as loader:
            success = loader.load_all(args.repo_root)
            sys.exit(0 if success else 1)
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
