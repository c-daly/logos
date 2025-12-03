# LOGOS SDKs

Shared client SDKs allow the CLI, browser, and automation jobs to consume the Sophia and Hermes APIs without hand-written HTTP glue. This directory documents how to install, regenerate, and publish the generated packages.

## Available Packages

### Python (sdk/)
- `sdk/python/sophia` → `logos_sophia_sdk`
- `sdk/python/hermes` → `logos_hermes_sdk`

### TypeScript (sdk-web/)
- `sdk-web/sophia` → `@logos/sophia-sdk`
- `sdk-web/hermes` → `@logos/hermes-sdk`

The packages are generated from the OpenAPI contracts in `contracts/`.

## Regenerating SDKs

Whenever `contracts/sophia.openapi.yaml` or `contracts/hermes.openapi.yaml` change, regenerate all SDKs:

```bash
./scripts/generate-sdks.sh
```

Requirements:
- Node.js/npm (script uses `npx @openapitools/openapi-generator-cli`)

The script overwrites everything under `sdk/` and `sdk-web/`. Always commit the regenerated files.

## Installing Locally

### Python

#### Option 1: Direct Install (Local Development)

From the desired SDK directory:

```bash
cd sdk/python/sophia
pip install .
```

or for development (editable mode):

```bash
pip install -e .
```

#### Option 2: Git Subdirectory (Recommended for Projects)

Install directly from the LOGOS repository using Poetry or pip:

**Poetry (pyproject.toml):**
```toml
[tool.poetry.dependencies]
logos-sophia-sdk = {git = "https://github.com/c-daly/logos.git", rev = "main", subdirectory = "sdk/python/sophia"}
logos-hermes-sdk = {git = "https://github.com/c-daly/logos.git", rev = "main", subdirectory = "sdk/python/hermes"}
```

**pip:**
```bash
pip install git+https://github.com/c-daly/logos.git@main#subdirectory=sdk/python/sophia
pip install git+https://github.com/c-daly/logos.git@main#subdirectory=sdk/python/hermes
```

#### Usage Examples

**Sophia SDK:**
```python
from logos_sophia_sdk import ApiClient, Configuration, DefaultApi
from logos_sophia_sdk.models import PlanRequest

# Configure client
config = Configuration(host="http://localhost:8000")
client = ApiClient(configuration=config)
api = DefaultApi(client)

# Create a plan
request = PlanRequest(
    goal="Mail a letter to the post office",
    context={"location": "home"}
)
response = api.plan(plan_request=request)
print(f"Plan ID: {response.plan_id}")
```

**Hermes SDK:**
```python
from logos_hermes_sdk import ApiClient, Configuration, DefaultApi
from logos_hermes_sdk.models import EmbedRequest, LLMRequest, LLMMessage

# Configure client
config = Configuration(host="http://localhost:8080")
client = ApiClient(configuration=config)
api = DefaultApi(client)

# Generate embeddings
embed_req = EmbedRequest(text="Hello, world!")
embed_resp = api.embed_text(embed_request=embed_req)

# Use LLM gateway
llm_req = LLMRequest(
    messages=[LLMMessage(role="user", content="Explain LOGOS in one sentence")]
)
llm_resp = api.llm_generate(llmrequest=llm_req)
print(llm_resp.choices[0].message.content)
```

### TypeScript / JavaScript

#### Option 1: Local Package (Vendored)

Copy the SDK package into your project:

```bash
# From your project root
mkdir -p vendor/@logos
cp -r /path/to/logos/sdk-web/sophia vendor/@logos/sophia-sdk
cp -r /path/to/logos/sdk-web/hermes vendor/@logos/hermes-sdk
cd vendor/@logos/sophia-sdk && npm install && npm run build
cd ../hermes-sdk && npm install && npm run build
```

**package.json:**
```json
{
  "dependencies": {
    "@logos/sophia-sdk": "file:vendor/@logos/sophia-sdk",
    "@logos/hermes-sdk": "file:vendor/@logos/hermes-sdk"
  }
}
```

#### Option 2: npm Link (Development)

```bash
cd sdk-web/sophia
npm install && npm run build
npm link

cd ../hermes
npm install && npm run build
npm link

# In your project
npm link @logos/sophia-sdk @logos/hermes-sdk
```

#### Usage Examples

**Sophia SDK:**
```typescript
import { Configuration, DefaultApi } from '@logos/sophia-sdk';

const config = new Configuration({
  basePath: 'http://localhost:8000'
});
const api = new DefaultApi(config);

// Create a plan
const response = await api.plan({
  planRequest: {
    goal: 'Mail a letter to the post office',
    context: { location: 'home' }
  }
});
console.log(`Plan ID: ${response.plan_id}`);
```

**Hermes SDK:**
```typescript
import { Configuration, DefaultApi } from '@logos/hermes-sdk';

const config = new Configuration({
  basePath: 'http://localhost:8080'
});
const api = new DefaultApi(config);

// Generate embeddings
const embedResponse = await api.embedText({
  embedRequest: { text: 'Hello, world!' }
});

// Use LLM gateway
const llmResponse = await api.llmGenerate({
  lLMRequest: {
    messages: [
      { role: 'user', content: 'Explain LOGOS in one sentence' }
    ]
  }
});
console.log(llmResponse.choices[0].message.content);
```

## Practical Integration Patterns

### Python Projects (Apollo CLI Example)

The Apollo CLI demonstrates the recommended pattern:

1. **Add SDKs as git subdirectory dependencies** in `pyproject.toml`:
   ```toml
   logos-sophia-sdk = {git = "https://github.com/c-daly/logos.git", rev = "9549b089...", subdirectory = "sdk/python/sophia"}
   ```

2. **Create typed wrapper clients** that encapsulate SDK usage:
   ```python
   from logos_sophia_sdk import ApiClient, Configuration, DefaultApi
   
   def build_sophia_sdk(config: SophiaConfig) -> DefaultApi:
       """Build configured Sophia SDK client."""
       sdk_config = Configuration(
           host=config.base_url,
           access_token=config.api_key
       )
       client = ApiClient(configuration=sdk_config)
       return DefaultApi(client)
   ```

3. **Wrap SDK calls** for consistent error handling:
   ```python
   def execute_sophia_call(func, *args, **kwargs):
       """Execute SDK call with error handling."""
       try:
           return func(*args, **kwargs)
       except ApiException as e:
           raise SophiaAPIError(f"API call failed: {e}")
   ```

See `apollo/src/apollo/client/sophia_client.py` and `apollo/src/apollo/sdk.py` for complete examples.

### TypeScript Projects (Apollo Webapp Example)

The Apollo webapp demonstrates vendored SDK integration:

1. **Copy SDKs into vendor directory**:
   ```bash
   mkdir -p webapp/vendor/@logos
   cp -r ../logos/sdk-web/sophia webapp/vendor/@logos/sophia-sdk
   cp -r ../logos/sdk-web/hermes webapp/vendor/@logos/hermes-sdk
   ```

2. **Build and reference as local packages** in `package.json`:
   ```json
   {
     "dependencies": {
       "@logos/sophia-sdk": "file:vendor/@logos/sophia-sdk",
       "@logos/hermes-sdk": "file:vendor/@logos/hermes-sdk"
     }
   }
   ```

3. **Create React Query hooks** for type-safe data fetching:
   ```typescript
   import { DefaultApi, Configuration } from '@logos/sophia-sdk';
   import { useQuery } from '@tanstack/react-query';
   
   const sophiaApi = new DefaultApi(
     new Configuration({ basePath: import.meta.env.VITE_SOPHIA_URL })
   );
   
   export function usePlan(planId: string) {
     return useQuery({
       queryKey: ['plan', planId],
       queryFn: () => sophiaApi.getState({ stateId: planId })
     });
   }
   ```

See `apollo/webapp/src/services/` for complete examples.

## Versioning & Publishing

### Current Versioning Scheme

Generated packages default to version `0.1.0`. The version is controlled in `scripts/generate-sdks.sh`:

```bash
--additional-properties=packageVersion=0.1.0    # Python
--additional-properties=npmVersion=0.1.0        # TypeScript
```

### Pinning to Specific Commits

For production stability, pin SDK dependencies to specific git commits:

**Python:**
```toml
logos-sophia-sdk = {git = "https://github.com/c-daly/logos.git", rev = "a0399389a3e0...", subdirectory = "sdk/python/sophia"}
```

**TypeScript:**
Copy SDKs from a specific commit/tag and vendor them to avoid drift.

### Publishing to Registries (Future)

When ready to publish:

1. **Update version** in `scripts/generate-sdks.sh`
2. **Regenerate SDKs**: `./scripts/generate-sdks.sh`
3. **Commit changes**: Include all generated files
4. **Publish**:
   - **Python**: `cd sdk/python/<name> && python -m build && twine upload dist/*`
   - **TypeScript**: `cd sdk-web/<name> && npm publish`

Document published versions in release notes so downstream clients can pin known-good builds.

## Continuous Integration

The `sdk-regen` GitHub Actions workflow runs `./scripts/generate-sdks.sh` on every PR/push that touches the contracts or generator inputs. If regenerated files differ from what is committed, the job fails with instructions to rerun the script locally and add the changes.

**Workflow triggers:**
- Changes to `contracts/*.openapi.yaml`
- Changes to `scripts/generate-sdks.sh`
- Changes to `openapitools.json`

**What it checks:**
- Runs SDK generation
- Fails if `git status --porcelain` shows uncommitted changes
- Ensures SDKs stay in sync with contracts

## Troubleshooting

### SDK Missing New Endpoint

**Problem:** New endpoint added to service (e.g., `/llm` in Hermes) but SDK doesn't have the method.

**Solution:**
1. Check if contract is up to date: `cat contracts/hermes.openapi.yaml | grep /llm`
2. If missing, copy updated contract from service repo:
   ```bash
   cp ../hermes/src/hermes/api/hermes.openapi.yaml contracts/hermes.openapi.yaml
   ```
3. Regenerate SDKs: `./scripts/generate-sdks.sh`
4. Commit both contract and generated SDK files
5. Update downstream projects to use new commit SHA

### Import Errors in Python

**Problem:** `ModuleNotFoundError: No module named 'logos_sophia_sdk'`

**Solutions:**
- Ensure SDK is installed: `pip list | grep logos-sophia-sdk`
- If using Poetry, run: `poetry install` (not `pip install`)
- Check `pyproject.toml` has correct git rev and subdirectory path
- Try: `poetry lock --no-update && poetry install`

### Type Errors in TypeScript

**Problem:** TypeScript complains about missing types or incorrect API signatures.

**Solutions:**
- Rebuild SDK: `cd vendor/@logos/sophia-sdk && npm install && npm run build`
- Clear node_modules: `rm -rf node_modules && npm install`
- Check SDK version matches: Verify vendor copy is from same commit as Python SDK
- Ensure `tsconfig.json` includes vendor path in module resolution

### Git Subdirectory Dependency Issues

**Problem:** `pip install` fails with "does not appear to be a Python project"

**Solutions:**
- Verify the subdirectory path is correct: `subdirectory = "sdk/python/sophia"` (not `sdk/sophia`)
- Ensure the commit SHA exists: Check GitHub or `git ls-remote`
- Try specific commit instead of branch: Use full SHA instead of `main`
- Clear Poetry cache: `poetry cache clear pypi --all && poetry install`

### CI Fails on SDK Regeneration

**Problem:** CI fails with "SDK outputs are stale"

**Solution:**
1. Run locally: `./scripts/generate-sdks.sh`
2. Commit all changes: `git add sdk/ sdk-web/ && git commit -m "chore: regenerate SDKs"`
3. Push again

**Prevention:** Always regenerate SDKs before pushing contract changes.

## Keeping Contracts in Sync

Service repositories (Hermes, Sophia) maintain their own OpenAPI contracts. The LOGOS repo holds **canonical copies** for SDK generation.

### Sync Workflow

When a service adds/changes endpoints:

1. **Update service contract** in service repo (e.g., `hermes/src/hermes/api/hermes.openapi.yaml`)
2. **Copy to LOGOS**: 
   ```bash
   cp hermes/src/hermes/api/hermes.openapi.yaml logos/contracts/hermes.openapi.yaml
   ```
3. **Regenerate SDKs** in LOGOS repo:
   ```bash
   cd logos
   ./scripts/generate-sdks.sh
   git add contracts/ sdk/ sdk-web/
   git commit -m "sync: update Hermes contract and regenerate SDKs"
   ```
4. **Update downstream** projects (Apollo, etc.) to use new commit

### Contract Drift Detection

If Apollo webapp shows `api.newMethod is not a function`:
- Service has new endpoint but LOGOS contract is stale
- Follow sync workflow above
- Consider automating with cross-repo CI hooks

## Related Documentation

- **Architecture**: `docs/architecture/PHASE2_SPEC.md` - API specifications
- **Services**: 
  - `hermes/README.md` - Hermes API details
  - `sophia/README.md` - Sophia API details
- **Apollo Integration**:
  - `apollo/src/apollo/sdk.py` - Python SDK wrapper
  - `apollo/webapp/src/services/` - TypeScript SDK usage
