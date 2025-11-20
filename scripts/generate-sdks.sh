#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
GEN="npx --yes @openapitools/openapi-generator-cli@2.25.2"

function generate_python() {
  local spec=$1
  local package_name=$2
  local project_name=$3
  local output_dir=$4

  rm -rf "$output_dir"
  $GEN generate \
    -i "$spec" \
    -g python \
    -o "$output_dir" \
    --additional-properties=packageName=$package_name,projectName=$project_name,packageVersion=0.1.0 \
    --skip-validate-spec
}

function generate_typescript() {
  local spec=$1
  local npm_name=$2
  local output_dir=$3

  rm -rf "$output_dir"
  $GEN generate \
    -i "$spec" \
    -g typescript-fetch \
    -o "$output_dir" \
    --additional-properties=npmName=$npm_name,npmVersion=0.1.0,supportsES6=true,typescriptThreePlus=true \
    --skip-validate-spec
}

mkdir -p "$ROOT_DIR/sdk/python" "$ROOT_DIR/sdk-web"

# Python SDKs
generate_python "$ROOT_DIR/contracts/sophia.openapi.yaml" logos_sophia_sdk logos-sophia-sdk "$ROOT_DIR/sdk/python/sophia"
generate_python "$ROOT_DIR/contracts/hermes.openapi.yaml" logos_hermes_sdk logos-hermes-sdk "$ROOT_DIR/sdk/python/hermes"

# TypeScript SDKs
generate_typescript "$ROOT_DIR/contracts/sophia.openapi.yaml" @logos/sophia-sdk "$ROOT_DIR/sdk-web/sophia"
generate_typescript "$ROOT_DIR/contracts/hermes.openapi.yaml" @logos/hermes-sdk "$ROOT_DIR/sdk-web/hermes"

echo "SDK generation complete. Outputs in sdk/ and sdk-web/."
