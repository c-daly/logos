#!/bin/bash
# Create milestones for Project LOGOS Phase 1
# Organized by functional capability layers

set -e  # Exit on error

echo "Creating Phase 1 milestones for Project LOGOS..."
echo ""

# M1: Infrastructure & Knowledge Foundation
echo "Creating M1: HCG Store & Retrieve..."
gh milestone create "M1: HCG Store & Retrieve" \
  --repo c-daly/logos \
  --description "Knowledge graph operational. Neo4j + Milvus working, core ontology loaded, basic CRUD operations functional." \
  2>/dev/null || echo "  → M1 already exists"

# M2: Language & Perception Services  
echo "Creating M2: SHACL Validation..."
gh milestone create "M2: SHACL Validation" \
  --repo c-daly/logos \
  --description "Validation and language services operational. SHACL validation working, Hermes endpoints functional, embeddings integrated." \
  2>/dev/null || echo "  → M2 already exists"

# M3: Cognitive Core & Reasoning
echo "Creating M3: Simple Planning..."
gh milestone create "M3: Simple Planning" \
  --repo c-daly/logos \
  --description "Cognitive capabilities demonstrated. Sophia can generate valid plans using causal reasoning over the knowledge graph." \
  2>/dev/null || echo "  → M3 already exists"

# M4: Integration & Demonstration
echo "Creating M4: Pick and Place..."
gh milestone create "M4: Pick and Place" \
  --repo c-daly/logos \
  --description "End-to-end autonomous behavior. Full pipeline working from user command to execution with knowledge graph updates." \
  2>/dev/null || echo "  → M4 already exists"

echo ""
echo "✅ Milestones created successfully!"
echo ""
echo "Functional Epoch Organization:"
echo "  Epoch 1: Infrastructure & Knowledge Foundation → M1"
echo "  Epoch 2: Language & Perception Services → M2"
echo "  Epoch 3: Cognitive Core & Reasoning → M3"
echo "  Epoch 4: Integration & Demonstration → M4"
echo ""
echo "Next step: Run .github/scripts/create_issues.sh to create all issues"
