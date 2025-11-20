# LOGOS TypeScript SDKs

This directory contains auto-generated TypeScript client SDKs for the LOGOS services (Sophia and Hermes). These SDKs are generated from the OpenAPI contracts in `/contracts` and provide type-safe TypeScript/JavaScript interfaces for browser and Node.js applications.

## Available SDKs

- **`hermes-client/`** - TypeScript client for Hermes API (STT, TTS, NLP, embeddings)
- **`sophia-client/`** - TypeScript client for Sophia API (planning, state, simulation)

## Installation

### Local Development

For local development with the Apollo browser application:

```bash
# From the repository root
cd sdk-web/hermes-client && npm install
cd ../sophia-client && npm install
```

### From Source Repository

Install directly from the repository (when packages are available):

```bash
npm install @logos/hermes-client@file:../../logos/sdk-web/hermes-client
npm install @logos/sophia-client@file:../../logos/sdk-web/sophia-client
```

### NPM Package Registry (Optional)

If published to npm or internal registry:

```bash
npm install @logos/hermes-client@1.0.0
npm install @logos/sophia-client@1.0.0
```

## Usage

### Hermes Client

```typescript
import { Configuration, DefaultApi } from '@logos/hermes-client';

// Configure the client
const config = new Configuration({
  basePath: 'http://localhost:8080',
});
const hermesApi = new DefaultApi(config);

// Text-to-speech
const ttsResponse = await hermesApi.textToSpeech({
  text: 'Hello from LOGOS',
  language: 'en-US',
});
// ttsResponse is binary audio data

// Generate embeddings
const embedResponse = await hermesApi.embedText({
  text: 'The red block is on the table',
});
console.log(`Embedding dimension: ${embedResponse.dimension}`);
console.log(`Vector: ${embedResponse.embedding}`);

// Simple NLP processing
const nlpResponse = await hermesApi.simpleNlp({
  text: 'The quick brown fox jumps over the lazy dog',
  operations: ['tokenize', 'pos_tag'],
});
console.log(`Tokens: ${nlpResponse.tokens}`);
console.log(`POS tags: ${nlpResponse.pos_tags}`);
```

### Sophia Client

```typescript
import { Configuration, DefaultApi } from '@logos/sophia-client';

// Configure the client
const config = new Configuration({
  basePath: 'http://localhost:8000',
});
const sophiaApi = new DefaultApi(config);

// Generate a plan
const planResponse = await sophiaApi.generatePlan({
  goal: 'Pick up the red block and place it in the bin',
  goal_state: {
    entities: [
      {
        entity_id: 'block_red_001',
        desired_state: 'in_bin',
      },
    ],
  },
});
console.log(`Plan ID: ${planResponse.plan_id}`);
console.log(`Number of processes: ${planResponse.processes.length}`);

// Query current state
const stateResponse = await sophiaApi.getState({
  limit: 10,
  model_type: 'CWM_A',
});
console.log(`Retrieved ${stateResponse.states.length} states`);

// Run simulation
const simResponse = await sophiaApi.runSimulation({
  capability_id: 'grasp_object',
  context: {
    entity_ids: ['block_red_001', 'gripper_001'],
    horizon_steps: 5,
  },
});
console.log(`Simulation ID: ${simResponse.simulation_id}`);
console.log(`Imagined states: ${simResponse.imagined_states.length}`);

// Health check
const healthResponse = await sophiaApi.getHealth();
console.log(`Service status: ${healthResponse.status}`);
console.log(`Neo4j connected: ${healthResponse.neo4j.connected}`);
```

### React Example

```typescript
import React, { useState, useEffect } from 'react';
import { Configuration, DefaultApi as SophiaApi } from '@logos/sophia-client';

const PlanViewer: React.FC = () => {
  const [states, setStates] = useState([]);
  
  useEffect(() => {
    const config = new Configuration({
      basePath: 'http://localhost:8000',
    });
    const api = new SophiaApi(config);
    
    api.getState({ limit: 10, model_type: 'CWM_A' })
      .then(response => setStates(response.states))
      .catch(error => console.error('Failed to fetch states:', error));
  }, []);
  
  return (
    <div>
      <h2>Current States</h2>
      <ul>
        {states.map(state => (
          <li key={state.state_id}>
            {state.state_id} - {state.model_type} - {state.status}
          </li>
        ))}
      </ul>
    </div>
  );
};

export default PlanViewer;
```

## Building

To build the TypeScript SDKs for distribution:

```bash
cd sdk-web/hermes-client && npm run build
cd ../sophia-client && npm run build
```

This generates:
- **ES modules** in `dist/esm/`
- **CommonJS modules** in `dist/cjs/`
- **Type declarations** in `dist/types/`

## Versioning

The SDK versions follow semantic versioning and are tied to the OpenAPI contract versions:

- **Major version**: Breaking API changes
- **Minor version**: New features, backward compatible
- **Patch version**: Bug fixes, backward compatible

Current versions:
- Hermes SDK: `1.0.0` (matches `contracts/hermes.openapi.yaml` v1.0.0)
- Sophia SDK: `1.0.0` (matches `contracts/sophia.openapi.yaml` v1.0.0)

## Publishing

### NPM Registry (Public Release)

For public release to npm:

1. Update version numbers in OpenAPI contracts
2. Regenerate SDKs using `scripts/generate_sdks.sh`
3. Build packages:
   ```bash
   cd sdk-web/hermes-client && npm run build && npm pack
   cd ../sophia-client && npm run build && npm pack
   ```
4. Publish to npm:
   ```bash
   npm publish sdk-web/hermes-client/logos-hermes-client-1.0.0.tgz
   npm publish sdk-web/sophia-client/logos-sophia-client-1.0.0.tgz
   ```

### Internal Package Registry (Optional)

If your organization uses an internal package registry (e.g., Azure Artifacts, GitHub Packages, Verdaccio):

1. Configure `.npmrc` with registry URL and authentication
2. Build and publish:
   ```bash
   cd sdk-web/hermes-client && npm run build && npm publish
   cd ../sophia-client && npm run build && npm publish
   ```

### GitHub Packages

To publish to GitHub Packages:

1. Add to `package.json`:
   ```json
   {
     "publishConfig": {
       "registry": "https://npm.pkg.github.com/"
     }
   }
   ```
2. Authenticate with GitHub token
3. Publish:
   ```bash
   npm publish
   ```

## Regenerating SDKs

The SDKs are automatically regenerated in CI when OpenAPI contracts change. To regenerate manually:

```bash
./scripts/generate_sdks.sh
```

This script:
1. Validates the OpenAPI contracts
2. Generates fresh TypeScript SDKs using OpenAPI Generator
3. Generates fresh Python SDKs for CLI usage
4. Cleans up old generated files

**Note**: After regeneration, review the changes and ensure backward compatibility. Breaking changes require a major version bump.

## Development

### Type Checking

The generated SDKs are written in TypeScript. To check types:

```bash
cd sdk-web/hermes-client && npm run build
cd ../sophia-client && npm run build
```

### Testing with Apollo

To test the SDKs with the Apollo browser application:

1. Build the SDKs: `cd sdk-web/hermes-client && npm run build`
2. Link them locally: `npm link`
3. In Apollo project: `npm link @logos/hermes-client @logos/sophia-client`
4. Use the SDKs in your Apollo components

## Contributing

When updating the OpenAPI contracts:

1. Update the contract file in `/contracts`
2. Validate the contract: `swagger-cli validate contracts/<service>.openapi.yaml`
3. Regenerate SDKs: `./scripts/generate_sdks.sh`
4. Review generated changes
5. Update SDK version if necessary
6. Build and test the SDKs
7. Update this README if API usage has changed

## Browser Compatibility

The generated TypeScript SDKs use the Fetch API and are compatible with:

- **Chrome/Edge**: 42+
- **Firefox**: 39+
- **Safari**: 10.1+
- **Node.js**: 18+ (with native fetch support)

For older browsers, include a fetch polyfill:

```bash
npm install whatwg-fetch
```

```typescript
import 'whatwg-fetch';
import { DefaultApi } from '@logos/sophia-client';
```

## Support

- **Issues**: Report bugs and issues on the [LOGOS GitHub repository](https://github.com/c-daly/logos/issues)
- **Documentation**: See the [Phase 2 specification](../docs/phase2/PHASE2_SPEC.md)
- **API Reference**: See individual SDK READMEs and `docs/` directories

## License

These SDKs are part of Project LOGOS and are released under the MIT License.
