# LOGOS API Documentation

This directory contains generated API documentation for the LOGOS ecosystem components.

## Overview

The API documentation is automatically generated from OpenAPI specifications located in the `contracts/` directory. The documentation is built using [Redocly CLI](https://redocly.com/docs/cli/) and published to GitHub Pages.

## Available APIs

### Hermes API
**Status:** ✅ Available  
**Specification:** [`contracts/hermes.openapi.yaml`](../../contracts/hermes.openapi.yaml)  
**Documentation:** [View Online](https://c-daly.github.io/logos/api/hermes.html)

Hermes is the stateless language & embedding utility providing:
- Speech-to-text (STT)
- Text-to-speech (TTS)
- Simple NLP preprocessing
- Text embedding generation

### Sophia API
**Status:** 🚧 Coming Soon  
**Repository:** [c-daly/sophia](https://github.com/c-daly/sophia)

Non-linguistic cognitive core with Orchestrator, CWM-A, CWM-G, Planner, and Executor.

### Talos API
**Status:** 🚧 Coming Soon  
**Repository:** [c-daly/talos](https://github.com/c-daly/talos)

Hardware abstraction layer for sensors and actuators.

### Apollo API
**Status:** 🚧 Coming Soon  
**Repository:** [c-daly/apollo](https://github.com/c-daly/apollo)

Thin client UI and command layer.

## Building Documentation Locally

To generate the API documentation locally:

```bash
# From the repository root
./scripts/generate-api-docs.sh
```

This will:
1. Find all OpenAPI specifications in the `contracts/` directory
2. Generate HTML documentation for each API using Redocly
3. Create an index page listing all available APIs
4. Output files to `docs/api/`

### Requirements

- Node.js and npm (for Redocly CLI)
- The script uses `npx` to run Redocly without requiring a global installation

### Viewing Locally

After generation, open `docs/api/index.html` in your web browser to view the documentation.

## Automated Publishing

API documentation is automatically published to GitHub Pages via GitHub Actions:
- **Workflow:** `.github/workflows/publish-api-docs.yml`
- **Trigger:** On push to `main` branch when files in `contracts/` change
- **Deployment:** Automatically pushes to `gh-pages` branch, which GitHub Pages serves
- **URL:** https://c-daly.github.io/logos/api/

The workflow:
1. Generates documentation from OpenAPI specs
2. Deploys to the `gh-pages` branch
3. GitHub Pages automatically serves the content

**Setup**: See `GITHUB_PAGES_SETUP.md` for one-time configuration steps.

## Adding New API Documentation

To add documentation for a new API component (e.g., Sophia, Talos, Apollo):

1. Add the OpenAPI specification to `contracts/` with the naming pattern: `<component-name>.openapi.yaml`
2. Commit and push to `main`
3. The workflow automatically generates and publishes the documentation
4. The new API appears in the index page

Example:
```bash
# Add a new OpenAPI spec
cp sophia.openapi.yaml contracts/

# Commit and push
git add contracts/sophia.openapi.yaml
git commit -m "Add Sophia API specification"
git push

# Documentation is automatically generated and published
```

## File Structure

```
docs/api/
├── README.md           # This file
├── index.html          # Landing page listing all APIs
├── hermes.html         # Hermes API documentation
└── (future APIs...)    # sophia.html, talos.html, apollo.html
```

## Documentation Standards

All OpenAPI specifications should follow these guidelines:
- Use OpenAPI 3.1.0 specification
- Include comprehensive descriptions for all endpoints
- Document all request/response schemas
- Include examples where appropriate
- Follow the patterns established in `contracts/hermes.openapi.yaml`
- Reference relevant sections from the LOGOS specification documents

## Troubleshooting

### Documentation Not Generating

If documentation generation fails:
1. Validate your OpenAPI spec: `npx @apidevtools/swagger-cli validate contracts/<your-spec>.yaml`
2. Check for syntax errors in the YAML file
3. Ensure the file has the `.openapi.yaml` or `.openapi.yml` extension
4. Review the error messages from the generation script

### GitHub Pages Not Updating

If the published documentation is not updating:
1. Check the GitHub Actions workflow run for errors
2. Verify that GitHub Pages is enabled for the repository (Settings → Pages)
3. Ensure the Pages source is set to deploy from the `docs/` directory on the `main` branch
4. Allow a few minutes for GitHub Pages to rebuild and deploy

## Related Documentation

- [LOGOS Specification](../spec/project_logos_full.md) - Section 3.4 covers Hermes API endpoints
- [Contributing Guide](../../CONTRIBUTING.md) - General contribution guidelines
- [Development Guide](../../DEVELOPMENT.md) - Setting up the development environment

## License

The API documentation and specifications are part of Project LOGOS and are released under the [MIT License](../../LICENSE).
