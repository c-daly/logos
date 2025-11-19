# Test Parameters Audit Report

**Date:** 2025-11-19  
**Issue:** [Infra] Verify no tests are using hardcoded parameters  
**Priority:** High  

## Executive Summary

This audit reviewed all test files in the repository to identify hardcoded parameters (connection strings, ports, credentials) and ensure they properly use environment variables with sensible defaults.

**Result:** ✅ All issues have been resolved. Tests now properly use environment variables.

## Findings and Resolutions

### 1. ✅ FIXED: `tests/phase1/test_m4_end_to_end.py`

**Issue:** Neo4j connection parameters were hardcoded without environment variable fallbacks.

**Lines 39-42 (Before):**
```python
NEO4J_URI = "bolt://localhost:7687"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "logosdev"
NEO4J_CONTAINER = "logos-hcg-neo4j"
```

**Resolution:** Added `os.getenv()` calls with defaults:
```python
NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "logosdev")
NEO4J_CONTAINER = os.getenv("NEO4J_CONTAINER", "logos-hcg-neo4j")
```

**Impact:** Tests can now be configured for different environments using environment variables while maintaining sensible defaults for local development.

---

### 2. ✅ FIXED: `tests/infra/test_milvus_collections.py`

**Issue:** Milvus connection parameters were hardcoded in multiple places.

**Lines 31-32 and 53-54 (Before):**
```python
connections.connect(
    alias="test_connection",
    host="localhost",
    port="19530",
)
```

**Resolution:** 
1. Added configuration constants at module level:
```python
import os
MILVUS_HOST = os.getenv("MILVUS_HOST", "localhost")
MILVUS_PORT = os.getenv("MILVUS_PORT", "19530")
```

2. Updated all connection calls to use these constants:
```python
connections.connect(
    alias="test_connection",
    host=MILVUS_HOST,
    port=MILVUS_PORT,
)
```

3. Updated skip message to include actual host/port being used

**Impact:** Milvus integration tests can now be configured for different environments, CI/CD pipelines, or remote Milvus instances.

---

### 3. ✅ ACCEPTABLE: `tests/test_hcg_milvus_sync.py`

**Status:** No changes needed - This is a unit test with proper mocking.

**Lines 44, 50-51:**
```python
sync = HCGMilvusSync(milvus_host="localhost", milvus_port="19530")
# ...
mock_connections.connect.assert_called_once_with(
    alias="default",
    host="localhost",
    port="19530",
)
```

**Rationale:** 
- These are unit tests that use `@patch` decorators to mock actual connections
- The hardcoded values are part of the test assertions to verify correct parameters are passed
- No real connections are made (all interactions are with mocks)
- This is standard practice for unit testing to ensure specific values are handled correctly

---

### 4. ✅ ACCEPTABLE: `tests/infra/test_hcg_client.py`

**Status:** No changes needed - This is a negative test case.

**Line 77:**
```python
HCGClient(uri="bolt://invalid:7687", user=NEO4J_USER, password=NEO4J_PASSWORD)
```

**Rationale:**
- This is testing connection failure with an intentionally invalid URI
- The hardcoded "invalid" hostname is part of the test's purpose
- The test verifies that the client properly handles connection errors
- Changing this to an environment variable would defeat the purpose of the negative test

---

### 5. ✅ VERIFIED: All Other Test Files

The following test files were reviewed and already properly use environment variables:

- `tests/phase1/test_m1_neo4j_crud.py` ✅
  - Lines 24-26: Uses `os.getenv()` for NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD
  
- `tests/phase1/test_shacl_neo4j_validation.py` ✅
  - Lines 30-32: Uses `os.getenv()` for connection parameters

- `tests/infra/test_hcg_client.py` ✅
  - Lines 22-24: Uses `os.getenv()` for NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD

## Configuration Reference

All integration tests now respect the following environment variables:

### Neo4j Configuration
| Variable | Default | Description |
|----------|---------|-------------|
| `NEO4J_URI` | `bolt://localhost:7687` | Neo4j connection URI |
| `NEO4J_USER` | `neo4j` | Neo4j username |
| `NEO4J_PASSWORD` | `logosdev` | Neo4j password |
| `NEO4J_CONTAINER` | `logos-hcg-neo4j` | Docker container name for Neo4j |

### Milvus Configuration
| Variable | Default | Description |
|----------|---------|-------------|
| `MILVUS_HOST` | `localhost` | Milvus server hostname |
| `MILVUS_PORT` | `19530` | Milvus server port |

## Usage Examples

### Local Development (defaults)
```bash
pytest tests/
```

### CI/CD Pipeline
```bash
export NEO4J_URI="bolt://neo4j-ci:7687"
export NEO4J_PASSWORD="secure-ci-password"
export MILVUS_HOST="milvus-ci"
export MILVUS_PORT="19530"
pytest tests/
```

### Custom Test Environment
```bash
NEO4J_URI=bolt://test-neo4j:7687 \
NEO4J_PASSWORD=testpass \
MILVUS_HOST=test-milvus \
pytest tests/infra/
```

## Best Practices Applied

1. **Environment Variables with Defaults**: All configuration uses `os.getenv(var, default)` pattern
2. **Sensible Defaults**: Default values work for standard docker-compose setup
3. **Documentation**: Connection requirements documented in test docstrings
4. **Skip Behavior**: Tests skip gracefully when services are unavailable
5. **Security**: Passwords and credentials can be overridden without code changes

## Testing Verification

All modified files have been syntax-checked:
```bash
python3 -m py_compile tests/phase1/test_m4_end_to_end.py
python3 -m py_compile tests/infra/test_milvus_collections.py
```

## Recommendations

1. **✅ Completed**: All hardcoded parameters have been addressed appropriately
2. **Future**: Consider adding `.env.example` file documenting all test environment variables
3. **Future**: Add to CI/CD documentation which environment variables should be set
4. **Future**: Consider using `pytest-env` plugin for cleaner environment variable management

## Conclusion

All tests in the repository now properly use environment variables for configuration parameters. The few cases where hardcoded values remain are either:
- Unit tests with mocks (where hardcoded values are part of test assertions)
- Negative test cases (where hardcoded invalid values are intentional)

The codebase follows best practices for test configuration and is ready for deployment in various environments.
