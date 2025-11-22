#!/usr/bin/env python3
"""
HCG Health Check Script

Verifies connectivity and consistency between Neo4j and Milvus.
Implements health checks for Section 4.2 (Vector Integration).

Usage:
    python check_hcg_health.py [--neo4j-uri URI] [--milvus-host HOST]
"""

import argparse
import sys
from typing import Any

from logos_hcg import HCGClient, HCGMilvusSync


def check_neo4j(uri: str, user: str, password: str) -> dict[str, Any]:
    """
    Check Neo4j connectivity and node counts.

    Args:
        uri: Neo4j connection URI
        user: Neo4j username
        password: Neo4j password

    Returns:
        Dictionary with Neo4j health status
    """
    status = {
        "connected": False,
        "node_counts": {},
        "error": None,
    }

    try:
        with HCGClient(uri=uri, user=user, password=password) as client:
            # Verify connection
            status["connected"] = client.verify_connection()

            if status["connected"]:
                # Get node counts
                counts = client.count_nodes_by_type()
                status["node_counts"] = counts

    except Exception as e:
        status["error"] = str(e)

    return status


def check_milvus(host: str, port: str) -> dict[str, Any]:
    """
    Check Milvus connectivity and collection status.

    Args:
        host: Milvus server host
        port: Milvus server port

    Returns:
        Dictionary with Milvus health status
    """
    status = {
        "connected": False,
        "collections": {},
        "error": None,
    }

    try:
        with HCGMilvusSync(milvus_host=host, milvus_port=port) as sync:
            health = sync.health_check()
            status["connected"] = health["connected"]
            status["collections"] = health["collections"]

    except Exception as e:
        status["error"] = str(e)

    return status


def check_sync_consistency(
    neo4j_uri: str,
    neo4j_user: str,
    neo4j_password: str,
    milvus_host: str,
    milvus_port: str,
) -> dict[str, Any]:
    """
    Check synchronization consistency between Neo4j and Milvus.

    Returns:
        Dictionary with sync reports for each node type
    """
    sync_reports = {}

    try:
        # Get UUIDs from Neo4j for each node type
        with HCGClient(
            uri=neo4j_uri, user=neo4j_user, password=neo4j_password
        ) as client:
            # Entity UUIDs
            entities = client.find_all_entities()
            entity_uuids = {str(e.uuid) for e in entities}

            # Concept UUIDs
            concepts = client.find_all_concepts()
            concept_uuids = {str(c.uuid) for c in concepts}

            # State and Process UUIDs would require custom queries or full scans
            # For now, we'll just check Entity and Concept

        # Verify sync with Milvus
        with HCGMilvusSync(milvus_host=milvus_host, milvus_port=milvus_port) as sync:
            sync_reports["Entity"] = sync.verify_sync(
                node_type="Entity",
                neo4j_uuids=entity_uuids,
            )
            sync_reports["Concept"] = sync.verify_sync(
                node_type="Concept",
                neo4j_uuids=concept_uuids,
            )

    except Exception as e:
        sync_reports["error"] = str(e)

    return sync_reports


def print_status(status: dict[str, Any], service_name: str) -> bool:
    """
    Print health status for a service.

    Args:
        status: Service health status
        service_name: Name of the service

    Returns:
        True if service is healthy, False otherwise
    """
    print(f"\n{'=' * 60}")
    print(f"{service_name} Health Check")
    print("=" * 60)

    if status.get("error"):
        print(f"❌ Error: {status['error']}")
        return False

    if not status.get("connected"):
        print("❌ Not connected")
        return False

    print("✅ Connected")
    return True


def print_neo4j_status(status: dict[str, Any]) -> bool:
    """Print Neo4j status details."""
    if not print_status(status, "Neo4j"):
        return False

    print("\nNode Counts:")
    for node_type, count in status["node_counts"].items():
        print(f"  {node_type}: {count}")

    return True


def print_milvus_status(status: dict[str, Any]) -> bool:
    """Print Milvus status details."""
    if not print_status(status, "Milvus"):
        return False

    print("\nCollections:")
    for node_type, coll_status in status["collections"].items():
        icon = "✅" if coll_status["exists"] and coll_status["loaded"] else "❌"
        print(f"  {icon} {node_type}")
        print(f"     - Exists: {coll_status['exists']}")
        print(f"     - Loaded: {coll_status['loaded']}")
        print(f"     - Count: {coll_status['count']}")

    return True


def print_sync_status(sync_reports: dict[str, Any]) -> bool:
    """Print sync consistency status."""
    print(f"\n{'=' * 60}")
    print("Synchronization Consistency")
    print("=" * 60)

    if "error" in sync_reports:
        print(f"❌ Error: {sync_reports['error']}")
        return False

    all_in_sync = True

    for node_type, report in sync_reports.items():
        if node_type == "error":
            continue

        icon = "✅" if report["in_sync"] else "⚠️"
        print(f"\n{icon} {node_type}")
        print(f"   Neo4j: {report['neo4j_count']} nodes")
        print(f"   Milvus: {report['milvus_count']} embeddings")

        if not report["in_sync"]:
            all_in_sync = False
            if report["orphaned_embeddings"]:
                print(
                    f"   ⚠ {len(report['orphaned_embeddings'])} orphaned embeddings in Milvus"
                )
            if report["missing_embeddings"]:
                print(f"   ⚠ {len(report['missing_embeddings'])} missing embeddings")

    return all_in_sync


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Check HCG health (Neo4j + Milvus connectivity and sync)",
    )
    parser.add_argument(
        "--neo4j-uri",
        default="bolt://localhost:7687",
        help="Neo4j connection URI (default: bolt://localhost:7687)",
    )
    parser.add_argument(
        "--neo4j-user",
        default="neo4j",
        help="Neo4j username (default: neo4j)",
    )
    parser.add_argument(
        "--neo4j-password",
        default="logosdev",
        help="Neo4j password (default: logosdev)",
    )
    parser.add_argument(
        "--milvus-host",
        default="localhost",
        help="Milvus host (default: localhost)",
    )
    parser.add_argument(
        "--milvus-port",
        default="19530",
        help="Milvus port (default: 19530)",
    )
    parser.add_argument(
        "--skip-sync-check",
        action="store_true",
        help="Skip synchronization consistency check",
    )

    args = parser.parse_args()

    print("=" * 60)
    print("HCG Health Check")
    print("Checking connectivity to Neo4j and Milvus...")
    print("=" * 60)

    # Check Neo4j
    neo4j_status = check_neo4j(
        uri=args.neo4j_uri,
        user=args.neo4j_user,
        password=args.neo4j_password,
    )
    neo4j_ok = print_neo4j_status(neo4j_status)

    # Check Milvus
    milvus_status = check_milvus(
        host=args.milvus_host,
        port=args.milvus_port,
    )
    milvus_ok = print_milvus_status(milvus_status)

    # Check sync consistency (if both services are up)
    sync_ok = True
    if neo4j_ok and milvus_ok and not args.skip_sync_check:
        sync_reports = check_sync_consistency(
            neo4j_uri=args.neo4j_uri,
            neo4j_user=args.neo4j_user,
            neo4j_password=args.neo4j_password,
            milvus_host=args.milvus_host,
            milvus_port=args.milvus_port,
        )
        sync_ok = print_sync_status(sync_reports)

    # Summary
    print(f"\n{'=' * 60}")
    print("Summary")
    print("=" * 60)

    overall_status = neo4j_ok and milvus_ok and sync_ok

    if overall_status:
        print("✅ All systems healthy")
        return 0
    else:
        print("❌ Issues detected")
        if not neo4j_ok:
            print("   - Neo4j not available or has errors")
        if not milvus_ok:
            print("   - Milvus not available or has errors")
        if not sync_ok:
            print("   - Synchronization inconsistencies detected")
        return 1


if __name__ == "__main__":
    sys.exit(main())
