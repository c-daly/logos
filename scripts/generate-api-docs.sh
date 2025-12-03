#!/usr/bin/env bash
# Generate API documentation from OpenAPI specifications
# Usage: ./scripts/generate-api-docs.sh

set -euo pipefail

# Script configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
CONTRACTS_DIR="${REPO_ROOT}/contracts"
OUTPUT_DIR="${REPO_ROOT}/docs/api"

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}===================================${NC}"
echo -e "${BLUE}LOGOS API Documentation Generator${NC}"
echo -e "${BLUE}===================================${NC}"
echo ""

# Ensure output directory exists
mkdir -p "${OUTPUT_DIR}"

# Check for OpenAPI specs
if [ ! -d "${CONTRACTS_DIR}" ]; then
    echo -e "${YELLOW}Warning: contracts directory not found${NC}"
    exit 1
fi

# Find all OpenAPI specification files in contracts/ and component directories
OPENAPI_FILES=$(find "${CONTRACTS_DIR}" "${REPO_ROOT}/logos_"* -name "*.openapi.yaml" -o -name "*.openapi.yml" 2>/dev/null || true)

if [ -z "${OPENAPI_FILES}" ]; then
    echo -e "${YELLOW}No OpenAPI specifications found in ${CONTRACTS_DIR}${NC}"
    exit 1
fi

# Generate documentation for each OpenAPI spec
for spec_file in ${OPENAPI_FILES}; do
    spec_basename=$(basename "${spec_file}" .openapi.yaml)
    spec_basename=$(basename "${spec_basename}" .openapi.yml)
    output_file="${OUTPUT_DIR}/${spec_basename}.html"
    
    echo -e "${BLUE}Processing:${NC} ${spec_basename}"
    echo -e "  Source: ${spec_file}"
    echo -e "  Output: ${output_file}"
    
    # Generate documentation using Redocly CLI
    if npx --yes @redocly/cli build-docs "${spec_file}" -o "${output_file}"; then
        echo -e "${GREEN}✓ Successfully generated documentation for ${spec_basename}${NC}"
    else
        echo -e "${YELLOW}✗ Failed to generate documentation for ${spec_basename}${NC}"
        exit 1
    fi
    
    echo ""
done

# Create index.html that redirects to or lists the API docs
echo -e "${BLUE}Creating API documentation index...${NC}"

cat > "${OUTPUT_DIR}/index.html" << 'EOF'
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>LOGOS API Documentation</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            line-height: 1.6;
            color: #333;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
        }
        
        .container {
            background: white;
            border-radius: 10px;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
            max-width: 800px;
            width: 100%;
            padding: 40px;
        }
        
        h1 {
            color: #333;
            margin-bottom: 10px;
            font-size: 2.5em;
        }
        
        .subtitle {
            color: #666;
            font-size: 1.1em;
            margin-bottom: 30px;
            padding-bottom: 20px;
            border-bottom: 2px solid #667eea;
        }
        
        .intro {
            margin-bottom: 30px;
            line-height: 1.8;
            color: #555;
        }
        
        .api-list {
            list-style: none;
        }
        
        .api-item {
            margin-bottom: 15px;
            background: #f8f9fa;
            border-radius: 8px;
            transition: all 0.3s ease;
        }
        
        .api-item:hover {
            background: #e9ecef;
            transform: translateX(5px);
        }
        
        .api-link {
            display: block;
            padding: 20px;
            color: #667eea;
            text-decoration: none;
            font-weight: 600;
            font-size: 1.2em;
        }
        
        .api-link:hover {
            color: #764ba2;
        }
        
        .api-description {
            color: #666;
            font-size: 0.9em;
            margin-top: 5px;
            font-weight: normal;
        }
        
        .footer {
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid #e0e0e0;
            color: #888;
            text-align: center;
            font-size: 0.9em;
        }
        
        .footer a {
            color: #667eea;
            text-decoration: none;
        }
        
        .footer a:hover {
            text-decoration: underline;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>LOGOS API Documentation</h1>
        <p class="subtitle">Non-Linguistic Cognitive Architecture for Autonomous Agents</p>
        
        <div class="intro">
            <p>Welcome to the LOGOS API documentation. This page provides comprehensive API references for all LOGOS ecosystem components.</p>
        </div>
        
        <h2 style="margin-bottom: 20px; color: #333;">Available APIs</h2>
        <ul class="api-list">
            <li class="api-item">
                <a href="hermes.html" class="api-link">
                    Hermes API
                    <div class="api-description">Stateless language & embedding utility (STT, TTS, NLP, text embeddings)</div>
                </a>
            </li>
            <li class="api-item">
                <a href="sophia.html" class="api-link">
                    Sophia API
                    <div class="api-description">Non-linguistic cognitive core with k-step imagination simulation</div>
                </a>
            </li>
            <li class="api-item">
                <a href="cwm-e.html" class="api-link">
                    CWM-E API
                    <div class="api-description">Emotional/social reflection layer for generating affective signals</div>
                </a>
            </li>
            <li class="api-item">
                <a href="persona.html" class="api-link">
                    Persona Diary API
                    <div class="api-description">Memory system for storing activity summaries and sentiments</div>
                </a>
            </li>
            <li class="api-item">
                <a href="apollo.html" class="api-link">
                    Apollo API
                    <div class="api-description">HCG graph querying, media upload, WebSocket diagnostics</div>
                </a>
            </li>
            <!-- Future APIs will be added here as they become available:
            <li class="api-item">
                <a href="talos.html" class="api-link">
                    Talos API
                    <div class="api-description">Hardware abstraction layer for sensors and actuators</div>
                </a>
            </li>
            -->
        </ul>
        
        <div class="footer">
            <p>Part of <a href="https://github.com/c-daly/logos" target="_blank">Project LOGOS</a> | 
            <a href="https://github.com/c-daly/logos/blob/main/LICENSE" target="_blank">MIT License</a></p>
        </div>
    </div>
</body>
</html>
EOF

echo -e "${GREEN}✓ Created index.html${NC}"
echo ""

echo -e "${GREEN}===================================${NC}"
echo -e "${GREEN}Documentation generation complete!${NC}"
echo -e "${GREEN}===================================${NC}"
echo ""
echo -e "Generated files in ${OUTPUT_DIR}:"
ls -lh "${OUTPUT_DIR}"
echo ""
echo -e "${BLUE}To view locally:${NC}"
echo -e "  Open ${OUTPUT_DIR}/index.html in your browser"
echo ""
