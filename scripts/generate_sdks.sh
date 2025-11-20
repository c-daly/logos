#!/bin/bash
# Generate Python and TypeScript SDKs from OpenAPI contracts
# This script is used by CI and can be run locally

set -e

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CONTRACTS_DIR="${REPO_ROOT}/contracts"
SDK_DIR="${REPO_ROOT}/sdk"
SDK_WEB_DIR="${REPO_ROOT}/sdk-web"

echo "🔧 Generating SDKs from OpenAPI contracts..."

# Clean existing SDK directories
echo "🧹 Cleaning existing SDK directories..."
rm -rf "${SDK_DIR}/hermes_client" "${SDK_DIR}/sophia_client"
rm -rf "${SDK_WEB_DIR}/hermes-client" "${SDK_WEB_DIR}/sophia-client"

# Generate Python SDK for Hermes
echo "🐍 Generating Python SDK for Hermes..."
docker run --rm \
  -v "${CONTRACTS_DIR}:/contracts" \
  -v "${SDK_DIR}:/sdk" \
  openapitools/openapi-generator-cli:latest generate \
  -i /contracts/hermes.openapi.yaml \
  -g python \
  -o /sdk/hermes_client \
  --package-name hermes_client \
  --additional-properties=projectName=hermes-client,packageVersion=1.0.0

# Generate Python SDK for Sophia
echo "🐍 Generating Python SDK for Sophia..."
docker run --rm \
  -v "${CONTRACTS_DIR}:/contracts" \
  -v "${SDK_DIR}:/sdk" \
  openapitools/openapi-generator-cli:latest generate \
  -i /contracts/sophia.openapi.yaml \
  -g python \
  -o /sdk/sophia_client \
  --package-name sophia_client \
  --additional-properties=projectName=sophia-client,packageVersion=1.0.0

# Generate TypeScript SDK for Hermes
echo "📦 Generating TypeScript SDK for Hermes..."
docker run --rm \
  -v "${CONTRACTS_DIR}:/contracts" \
  -v "${SDK_WEB_DIR}:/sdk-web" \
  openapitools/openapi-generator-cli:latest generate \
  -i /contracts/hermes.openapi.yaml \
  -g typescript-fetch \
  -o /sdk-web/hermes-client \
  --additional-properties=npmName=@logos/hermes-client,npmVersion=1.0.0,supportsES6=true

# Generate TypeScript SDK for Sophia
echo "📦 Generating TypeScript SDK for Sophia..."
docker run --rm \
  -v "${CONTRACTS_DIR}:/contracts" \
  -v "${SDK_WEB_DIR}:/sdk-web" \
  openapitools/openapi-generator-cli:latest generate \
  -i /contracts/sophia.openapi.yaml \
  -g typescript-fetch \
  -o /sdk-web/sophia-client \
  --additional-properties=npmName=@logos/sophia-client,npmVersion=1.0.0,supportsES6=true

echo "✅ SDK generation complete!"
echo "📁 Python SDKs: ${SDK_DIR}/hermes_client, ${SDK_DIR}/sophia_client"
echo "📁 TypeScript SDKs: ${SDK_WEB_DIR}/hermes-client, ${SDK_WEB_DIR}/sophia-client"
