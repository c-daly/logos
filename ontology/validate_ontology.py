#!/usr/bin/env python3
"""
Basic validation script for LOGOS ontology files.
Checks syntax and structure without requiring a running Neo4j instance.
"""

import re
from pathlib import Path


def validate_cypher_file(filepath: Path) -> tuple[bool, list[str]]:
    """
    Validates a Cypher file for basic syntax issues.

    Returns:
        (is_valid, list_of_issues)
    """
    issues = []

    try:
        content = filepath.read_text()
    except Exception as e:
        return False, [f"Failed to read file: {e}"]

    # Check for balanced braces
    if content.count('{') != content.count('}'):
        issues.append("Unbalanced curly braces")

    if content.count('(') != content.count(')'):
        issues.append("Unbalanced parentheses")

    if content.count('[') != content.count(']'):
        issues.append("Unbalanced square brackets")

    # Check for required statements
    if "CREATE CONSTRAINT" in content or "MERGE" in content or "CREATE" in content:
        # Looks like valid Cypher
        pass
    else:
        issues.append("No CREATE/MERGE/CONSTRAINT statements found")

    # Check UUID patterns in MERGE/CREATE statements
    uuid_patterns = [
        r"uuid:\s*['\"]entity-",
        r"uuid:\s*['\"]concept-",
        r"uuid:\s*['\"]state-",
        r"uuid:\s*['\"]process-",
    ]

    found_uuids = False
    for pattern in uuid_patterns:
        if re.search(pattern, content):
            found_uuids = True
            break

    if not found_uuids and "MERGE" in content:
        issues.append("Warning: No properly formatted UUIDs found (should start with entity-, concept-, state-, or process-)")

    return len(issues) == 0, issues


def validate_ttl_file(filepath: Path) -> tuple[bool, list[str]]:
    """
    Validates a Turtle/SHACL file for basic syntax issues.

    Returns:
        (is_valid, list_of_issues)
    """
    issues = []

    try:
        content = filepath.read_text()
    except Exception as e:
        return False, [f"Failed to read file: {e}"]

    # Check for required prefixes
    required_prefixes = ['@prefix sh:', '@prefix logos:']
    for prefix in required_prefixes:
        if prefix not in content:
            issues.append(f"Missing required prefix: {prefix}")

    # Check for balanced brackets
    if content.count('[') != content.count(']'):
        issues.append("Unbalanced square brackets")

    # Check for SHACL shapes
    if 'sh:NodeShape' not in content:
        issues.append("No SHACL shapes (sh:NodeShape) found")

    # Check for proper termination of statements
    lines = content.split('\n')
    in_shape = False
    for i, line in enumerate(lines, 1):
        stripped = line.strip()
        if 'sh:NodeShape' in stripped:
            in_shape = True
        if in_shape and stripped and not stripped.startswith('#'):
            # Shapes should end with . or ;
            if stripped[-1] not in ['.', ';', '[', ']', ','] and not stripped.startswith('@'):
                if i < len(lines):  # Not last line
                    issues.append(f"Line {i} may be missing proper termination: {stripped[:50]}")

    return len(issues) == 0, issues


def main():
    """Run validation on all ontology files."""
    ontology_dir = Path(__file__).parent.parent / "ontology"

    print("=" * 70)
    print("LOGOS Ontology Validation")
    print("=" * 70)

    all_valid = True

    # Validate Cypher files
    cypher_files = list(ontology_dir.glob("*.cypher"))
    print(f"\nFound {len(cypher_files)} Cypher file(s)")

    for cypher_file in cypher_files:
        print(f"\nValidating: {cypher_file.name}")
        is_valid, issues = validate_cypher_file(cypher_file)

        if is_valid:
            print("  ✓ Valid")
        else:
            print("  ✗ Issues found:")
            for issue in issues:
                print(f"    - {issue}")
            all_valid = False

    # Validate TTL files
    ttl_files = list(ontology_dir.glob("*.ttl"))
    print(f"\nFound {len(ttl_files)} Turtle/SHACL file(s)")

    for ttl_file in ttl_files:
        print(f"\nValidating: {ttl_file.name}")
        is_valid, issues = validate_ttl_file(ttl_file)

        if is_valid:
            print("  ✓ Valid")
        else:
            print("  ✗ Issues found:")
            for issue in issues:
                print(f"    - {issue}")
            all_valid = False

    print("\n" + "=" * 70)
    if all_valid:
        print("✓ All files passed basic validation")
        print("=" * 70)
        return 0
    else:
        print("✗ Some files have issues")
        print("=" * 70)
        return 1


if __name__ == "__main__":
    exit(main())
