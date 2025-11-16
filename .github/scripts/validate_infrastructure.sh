#!/bin/bash
# Test script to validate GitHub infrastructure setup
# This script runs validation checks without creating actual GitHub resources

set -e

echo "🧪 Testing GitHub Infrastructure Configuration"
echo "=============================================="
echo ""

# Test 1: Validate labels.yml syntax
echo "✅ Test 1: Validating labels.yml syntax..."
if ! python3 -c "import yaml; yaml.safe_load(open('.github/labels.yml'))" 2>/dev/null; then
    echo "❌ FAILED: Invalid YAML syntax in labels.yml"
    exit 1
fi
echo "   ✓ labels.yml has valid YAML syntax"
echo ""

# Test 2: Check for required component labels
echo "✅ Test 2: Checking for required component labels..."
REQUIRED_COMPONENTS=("sophia" "hermes" "talos" "apollo" "logos" "infrastructure")
for component in "${REQUIRED_COMPONENTS[@]}"; do
    if grep -q "component:${component}" .github/labels.yml; then
        echo "   ✓ component:${component} found"
    else
        echo "   ❌ Missing required label: component:${component}"
        exit 1
    fi
done
echo ""

# Test 3: Validate project_config.yml syntax
echo "✅ Test 3: Validating project_config.yml syntax..."
if ! python3 -c "import yaml; yaml.safe_load(open('.github/project_config.yml'))" 2>/dev/null; then
    echo "❌ FAILED: Invalid YAML syntax in project_config.yml"
    exit 1
fi
echo "   ✓ project_config.yml has valid YAML syntax"
echo ""

# Test 4: Validate workflow files
echo "✅ Test 4: Validating workflow files..."
for workflow in .github/workflows/*.yml; do
    if ! python3 -c "import yaml; yaml.safe_load(open('$workflow'))" 2>/dev/null; then
        echo "   ❌ Invalid YAML syntax in $workflow"
        exit 1
    fi
    echo "   ✓ $(basename $workflow) has valid YAML syntax"
done
echo ""

# Test 5: Test Python scripts can run
echo "✅ Test 5: Testing Python scripts..."
if python3 .github/scripts/create_issues_by_epoch.py --format json > /dev/null 2>&1; then
    echo "   ✓ create_issues_by_epoch.py executes successfully"
else
    echo "   ❌ create_issues_by_epoch.py failed to execute"
    exit 1
fi

if python3 .github/scripts/generate_issues.py --format json > /dev/null 2>&1; then
    echo "   ✓ generate_issues.py executes successfully"
else
    echo "   ❌ generate_issues.py failed to execute"
    exit 1
fi
echo ""

# Test 6: Verify scripts generate valid output
echo "✅ Test 6: Validating generated output..."
ISSUE_COUNT=$(python3 .github/scripts/create_issues_by_epoch.py --format json 2>/dev/null | python3 -c "import sys, json; print(len(json.load(sys.stdin)))")
if [ "$ISSUE_COUNT" -gt 0 ]; then
    echo "   ✓ create_issues_by_epoch.py generated $ISSUE_COUNT issues"
else
    echo "   ❌ create_issues_by_epoch.py generated no issues"
    exit 1
fi

# Verify gh-cli format generates valid bash
if python3 .github/scripts/create_issues_by_epoch.py --format gh-cli 2>/dev/null | bash -n; then
    echo "   ✓ Generated gh-cli script has valid bash syntax"
else
    echo "   ❌ Generated gh-cli script has invalid bash syntax"
    exit 1
fi
echo ""

# Test 7: Check that all labels used in scripts exist in labels.yml
echo "✅ Test 7: Verifying label consistency..."
SCRIPT_LABELS=$(python3 .github/scripts/create_issues_by_epoch.py --format json 2>/dev/null | python3 -c "
import sys, json
issues = json.load(sys.stdin)
labels = set()
for issue in issues:
    labels.update(issue.get('labels', []))
for label in sorted(labels):
    print(label)
")

MISSING_LABELS=0
for label in $SCRIPT_LABELS; do
    if grep -q "\"${label}\"" .github/labels.yml; then
        echo "   ✓ $label"
    else
        echo "   ❌ Label referenced in script but not in labels.yml: $label"
        MISSING_LABELS=$((MISSING_LABELS + 1))
    fi
done

if [ $MISSING_LABELS -gt 0 ]; then
    echo ""
    echo "   ❌ Found $MISSING_LABELS missing labels!"
    exit 1
fi
echo ""

# Test 8: Verify all expected milestones are referenced
echo "✅ Test 8: Checking milestone references..."
EXPECTED_MILESTONES=("M1: HCG Store & Retrieve" "M2: SHACL Validation" "M3: Simple Planning" "M4: Pick and Place")
for milestone in "${EXPECTED_MILESTONES[@]}"; do
    if grep -q "$milestone" .github/workflows/create-phase1-issues.yml; then
        echo "   ✓ $milestone"
    else
        echo "   ❌ Missing milestone reference: $milestone"
        exit 1
    fi
done
echo ""

# Summary
echo "=============================================="
echo "✅ All tests passed!"
echo ""
echo "Infrastructure validation complete. The configuration is ready to use."
echo ""
echo "Next steps:"
echo "1. Run the 'Sync Labels' workflow from GitHub Actions"
echo "2. Run the 'Create Phase 1 Issues and Project Board' workflow"
echo "3. Verify labels and issues were created successfully"
