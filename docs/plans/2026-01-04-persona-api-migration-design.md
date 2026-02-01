# Persona API Migration Design

## Overview

Add persona CRUD and sentiment endpoints to Sophia, then migrate Apollo from hcg-client.ts (which calls Apollo backend) to sophia-client.ts (which calls Sophia directly). Delete Apollo's direct Neo4j access for persona data.

## Approach

**Selected**: Add persona endpoints to Sophia's existing `app.py`, store as CWMState nodes with `type: "cwm_e"`, extend sophia-client.ts with HCG + persona methods, delete hcg-client.ts entirely.

**Why**: Follows established patterns (Sophia owns cognitive state, Apollo is UI layer). CWMPersistence already supports `cwm_e` type. No new module needed - just API endpoints and client methods.

---

## Part 1: Sophia Persona Endpoints

### 1.1 Request/Response Models

**File**: `sophia/src/sophia/api/models.py` (add to existing file)

```python
from typing import Literal, Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field

# --- Persona Entry Models ---

PersonaEntryType = Literal["belief", "decision", "observation", "reflection"]
PersonaSentiment = Literal["positive", "negative", "neutral", "mixed"]

class PersonaEntryCreate(BaseModel):
    """Request model for creating a persona entry."""
    entry_type: PersonaEntryType
    content: str = Field(..., min_length=1, max_length=10000)
    summary: Optional[str] = Field(None, max_length=200)
    trigger: Optional[str] = Field(None, max_length=200)
    sentiment: Optional[PersonaSentiment] = None
    confidence: Optional[float] = Field(None, ge=0.0, le=1.0)
    related_process_ids: List[str] = Field(default_factory=list)
    related_goal_ids: List[str] = Field(default_factory=list)
    emotion_tags: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class PersonaEntryResponse(BaseModel):
    """Response after creating a persona entry."""
    entry_id: str
    cwm_state_id: str
    timestamp: datetime


class PersonaEntryFull(BaseModel):
    """Complete persona entry with all fields."""
    entry_id: str
    timestamp: datetime
    entry_type: PersonaEntryType
    content: str
    summary: Optional[str] = None
    trigger: Optional[str] = None
    sentiment: Optional[PersonaSentiment] = None
    confidence: Optional[float] = None
    related_process_ids: List[str] = Field(default_factory=list)
    related_goal_ids: List[str] = Field(default_factory=list)
    emotion_tags: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class PersonaEntryUpdate(BaseModel):
    """Request model for partial update of persona entry."""
    summary: Optional[str] = Field(None, max_length=200)
    sentiment: Optional[PersonaSentiment] = None
    confidence: Optional[float] = Field(None, ge=0.0, le=1.0)
    emotion_tags: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None


class PersonaListResponse(BaseModel):
    """Response for listing persona entries."""
    entries: List[PersonaEntryFull]
    total: int
    limit: int
    offset: int


class SentimentResponse(BaseModel):
    """Aggregated sentiment from recent persona entries."""
    sentiment: Optional[str] = None  # Most common recent sentiment
    confidence_avg: Optional[float] = None  # Average confidence
    recent_sentiment_trend: Optional[Literal["rising", "falling", "stable"]] = None
    emotion_distribution: Dict[str, int] = Field(default_factory=dict)
    entry_count: int = 0
    last_updated: Optional[datetime] = None
```

### 1.2 Endpoint Specifications

**File**: `sophia/src/sophia/api/app.py` (add within `create_app()`)

#### POST /persona/entries

**Preconditions**:
- Valid Bearer token
- `_cwm_persistence` is initialized

**Input**:
```json
{
  "entry_type": "decision",
  "content": "Selected path A due to shorter time",
  "summary": "Path selection",
  "sentiment": "positive",
  "confidence": 0.87,
  "emotion_tags": ["decisive"]
}
```

**Processing**:
1. Generate UUID for entry: `entry_id = f"persona_{uuid4().hex[:12]}"`
2. Generate UUID for CWM state: `state_id = f"cwm_e_{uuid4().hex[:12]}"`
3. Build CWMState envelope:
   - `model_type = "CWM_E"`
   - `timestamp = datetime.now(timezone.utc)`
   - `data = {"entry": <input fields>, "source": "persona_api", "derivation": "observed"}`
4. Persist via `_cwm_persistence.persist(state)`
5. Return `PersonaEntryResponse(entry_id, state_id, timestamp)`

**Output** (201 Created):
```json
{
  "entry_id": "persona_abc123def456",
  "cwm_state_id": "cwm_e_xyz789abc012",
  "timestamp": "2026-01-04T12:00:00Z"
}
```

**Error Cases**:
- 401: Invalid/missing token
- 422: Validation error (content empty, confidence out of range)
- 503: CWM persistence unavailable

---

#### GET /persona/entries

**Preconditions**: Valid Bearer token

**Input** (query params):
| Param | Type | Default | Description |
|-------|------|---------|-------------|
| entry_type | string | null | Filter: "belief", "decision", "observation", "reflection" |
| sentiment | string | null | Filter: "positive", "negative", "neutral", "mixed" |
| related_process_id | string | null | Filter by linked process |
| related_goal_id | string | null | Filter by linked goal |
| after_timestamp | string | null | ISO 8601 datetime, return entries after this |
| limit | int | 20 | Max entries (1-100) |
| offset | int | 0 | Pagination offset |

**Processing**:
1. Query CWM states where `type = "cwm_e"` via `_cwm_persistence.find_states(types=["cwm_e"], limit=limit*2)`
2. Parse each state's `data.entry` field into `PersonaEntryFull`
3. Apply filters in memory (entry_type, sentiment, related IDs)
4. Apply offset/limit
5. Return `PersonaListResponse`

**Output** (200 OK):
```json
{
  "entries": [
    {
      "entry_id": "persona_abc123",
      "timestamp": "2026-01-04T12:00:00Z",
      "entry_type": "decision",
      "content": "Selected path A...",
      ...
    }
  ],
  "total": 42,
  "limit": 20,
  "offset": 0
}
```

**Edge Cases**:
- No entries match filters: Return `{"entries": [], "total": 0, "limit": 20, "offset": 0}`
- Offset beyond total: Return empty entries array

---

#### GET /persona/entries/{entry_id}

**Input**: Path param `entry_id` (string)

**Processing**:
1. Query CWM states where `type = "cwm_e"`
2. Find state where `data.entry.entry_id == entry_id`
3. If found, return `PersonaEntryFull`
4. If not found, raise 404

**Output** (200 OK): `PersonaEntryFull` object

**Error Cases**:
- 404: Entry not found

---

#### PATCH /persona/entries/{entry_id}

**Input**: Path param + `PersonaEntryUpdate` body

**Processing**:
1. Find existing entry (same as GET)
2. If not found, raise 404
3. Merge updates into existing entry
4. Create new CWMState with updated data (append-only, not in-place update)
5. Persist new state
6. Return updated `PersonaEntryFull`

**Output** (200 OK): Updated `PersonaEntryFull`

**Note**: This creates a new CWMState node, preserving history. The latest state for an entry_id is determined by timestamp.

---

#### DELETE /persona/entries/{entry_id}

**Input**: Path param `entry_id`

**Processing**:
1. Find existing entry
2. If not found, raise 404
3. Create "tombstone" CWMState with `data.entry.deleted = true`
4. Subsequent GET/list operations filter out deleted entries

**Output**: 204 No Content

**Note**: Soft delete via tombstone. No physical deletion.

---

#### GET /persona/sentiment

**Input** (query params):
| Param | Type | Default | Description |
|-------|------|---------|-------------|
| limit | int | 20 | Number of recent entries to aggregate (1-100) |
| after_timestamp | string | null | Only aggregate entries after this time |

**Processing**:
1. Fetch recent persona entries (non-deleted) up to `limit`
2. Compute aggregates:
   - `sentiment`: Most frequent sentiment value
   - `confidence_avg`: Mean of non-null confidence values
   - `emotion_distribution`: Count of each emotion_tag
   - `recent_sentiment_trend`: Compare first half vs second half sentiment
3. Return `SentimentResponse`

**Output** (200 OK):
```json
{
  "sentiment": "positive",
  "confidence_avg": 0.78,
  "recent_sentiment_trend": "rising",
  "emotion_distribution": {"decisive": 5, "analytical": 3},
  "entry_count": 15,
  "last_updated": "2026-01-04T12:00:00Z"
}
```

**Edge Cases**:
- No entries: Return `{"sentiment": null, "confidence_avg": null, "entry_count": 0, ...}`
- All entries have null sentiment: `sentiment` field is null

---

## Part 2: Apollo sophia-client.ts Extensions

### 2.1 New Types

**File**: `apollo/webapp/src/lib/sophia-client.ts` (add to existing file)

```typescript
// --- Persona Types ---

export type PersonaEntryType = 'belief' | 'decision' | 'observation' | 'reflection'
export type PersonaSentiment = 'positive' | 'negative' | 'neutral' | 'mixed'

export interface PersonaEntryCreate {
  entry_type: PersonaEntryType
  content: string
  summary?: string
  trigger?: string
  sentiment?: PersonaSentiment
  confidence?: number
  related_process_ids?: string[]
  related_goal_ids?: string[]
  emotion_tags?: string[]
  metadata?: Record<string, unknown>
}

export interface PersonaEntryResponse {
  entry_id: string
  cwm_state_id: string
  timestamp: string
}

export interface PersonaEntryFull {
  entry_id: string
  timestamp: string
  entry_type: PersonaEntryType
  content: string
  summary?: string
  trigger?: string
  sentiment?: PersonaSentiment
  confidence?: number
  related_process_ids: string[]
  related_goal_ids: string[]
  emotion_tags: string[]
  metadata: Record<string, unknown>
}

export interface PersonaListResponse {
  entries: PersonaEntryFull[]
  total: number
  limit: number
  offset: number
}

export interface PersonaListFilters {
  entry_type?: PersonaEntryType
  sentiment?: PersonaSentiment
  related_process_id?: string
  related_goal_id?: string
  after_timestamp?: string
  limit?: number
  offset?: number
}

export interface SentimentResponse {
  sentiment: string | null
  confidence_avg: number | null
  recent_sentiment_trend: 'rising' | 'falling' | 'stable' | null
  emotion_distribution: Record<string, number>
  entry_count: number
  last_updated: string | null
}

export interface SentimentFilters {
  limit?: number
  after_timestamp?: string
}

// --- HCG Types (moved from hcg-client.ts) ---

export interface HCGEntity {
  id: string
  type: string
  name: string
  properties: Record<string, unknown>
  labels: string[]
  created_at?: string
}

export interface HCGEdge {
  id: string
  source_id: string
  target_id: string
  edge_type: string
  properties: Record<string, unknown>
}

export interface HCGGraphSnapshot {
  entities: HCGEntity[]
  edges: HCGEdge[]
  entity_count: number
  edge_count: number
}
```

### 2.2 New Methods

**File**: `apollo/webapp/src/lib/sophia-client.ts` (add to SophiaClient class)

```typescript
// --- Persona Methods ---

async createPersonaEntry(
  entry: PersonaEntryCreate
): Promise<SophiaResponse<PersonaEntryResponse>> {
  return this.performRequest<PersonaEntryResponse>({
    action: 'creating persona entry',
    method: 'POST',
    path: '/persona/entries',
    body: entry,
  })
}

async getPersonaEntries(
  filters: PersonaListFilters = {}
): Promise<SophiaResponse<PersonaListResponse>> {
  const params: Record<string, string> = {}
  if (filters.entry_type) params.entry_type = filters.entry_type
  if (filters.sentiment) params.sentiment = filters.sentiment
  if (filters.related_process_id) params.related_process_id = filters.related_process_id
  if (filters.related_goal_id) params.related_goal_id = filters.related_goal_id
  if (filters.after_timestamp) params.after_timestamp = filters.after_timestamp
  if (filters.limit !== undefined) params.limit = String(filters.limit)
  if (filters.offset !== undefined) params.offset = String(filters.offset)

  return this.performRequest<PersonaListResponse>({
    action: 'listing persona entries',
    method: 'GET',
    path: '/persona/entries',
    params,
  })
}

async getPersonaEntry(
  entryId: string
): Promise<SophiaResponse<PersonaEntryFull | null>> {
  const response = await this.performRequest<PersonaEntryFull>({
    action: 'fetching persona entry',
    method: 'GET',
    path: `/persona/entries/${entryId}`,
  })

  if (!response.success && response.error?.includes('404')) {
    return { success: true, data: null }
  }
  return response
}

async updatePersonaEntry(
  entryId: string,
  update: Partial<Pick<PersonaEntryFull, 'summary' | 'sentiment' | 'confidence' | 'emotion_tags' | 'metadata'>>
): Promise<SophiaResponse<PersonaEntryFull>> {
  return this.performRequest<PersonaEntryFull>({
    action: 'updating persona entry',
    method: 'PATCH',
    path: `/persona/entries/${entryId}`,
    body: update,
  })
}

async deletePersonaEntry(entryId: string): Promise<SophiaResponse<void>> {
  return this.performRequest<void>({
    action: 'deleting persona entry',
    method: 'DELETE',
    path: `/persona/entries/${entryId}`,
  })
}

async getPersonaSentiment(
  filters: SentimentFilters = {}
): Promise<SophiaResponse<SentimentResponse>> {
  const params: Record<string, string> = {}
  if (filters.limit !== undefined) params.limit = String(filters.limit)
  if (filters.after_timestamp) params.after_timestamp = filters.after_timestamp

  return this.performRequest<SentimentResponse>({
    action: 'fetching persona sentiment',
    method: 'GET',
    path: '/persona/sentiment',
    params,
  })
}

// --- HCG Methods (migrated from hcg-client.ts) ---

async getHCGSnapshot(
  entityTypes?: string[],
  limit: number = 200
): Promise<SophiaResponse<HCGGraphSnapshot>> {
  const params: Record<string, string> = { limit: String(limit) }
  if (entityTypes && entityTypes.length > 0) {
    params.entity_types = entityTypes.join(',')
  }

  return this.performRequest<HCGGraphSnapshot>({
    action: 'fetching HCG snapshot',
    method: 'GET',
    path: '/hcg/snapshot',
    params,
  })
}

async getHCGEntities(
  entityType?: string,
  limit: number = 100,
  offset: number = 0
): Promise<SophiaResponse<HCGEntity[]>> {
  const params: Record<string, string> = {
    limit: String(limit),
    offset: String(offset),
  }
  if (entityType) params.type = entityType

  return this.performRequest<HCGEntity[]>({
    action: 'fetching HCG entities',
    method: 'GET',
    path: '/hcg/entities',
    params,
  })
}

async getHCGEntity(entityId: string): Promise<SophiaResponse<HCGEntity | null>> {
  const response = await this.performRequest<HCGEntity>({
    action: 'fetching HCG entity',
    method: 'GET',
    path: `/hcg/entities/${entityId}`,
  })

  if (!response.success && response.error?.includes('404')) {
    return { success: true, data: null }
  }
  return response
}

async getHCGEdges(
  entityId?: string,
  edgeType?: string,
  limit: number = 100
): Promise<SophiaResponse<HCGEdge[]>> {
  const params: Record<string, string> = { limit: String(limit) }
  if (entityId) params.entity_id = entityId
  if (edgeType) params.edge_type = edgeType

  return this.performRequest<HCGEdge[]>({
    action: 'fetching HCG edges',
    method: 'GET',
    path: '/hcg/edges',
    params,
  })
}

async hcgHealthCheck(): Promise<boolean> {
  try {
    const response = await this.performRequest<{ status: string }>({
      action: 'checking HCG health',
      method: 'GET',
      path: '/hcg/health',
    })
    return response.success
  } catch {
    return false
  }
}
```

### 2.3 Helper Method

Add a generic `performRequest` method (similar to existing `performLegacyRequest`):

```typescript
private async performRequest<T>({
  action,
  method,
  path,
  body,
  params,
}: {
  action: string
  method: 'GET' | 'POST' | 'PATCH' | 'DELETE'
  path: string
  body?: unknown
  params?: Record<string, string>
}): Promise<SophiaResponse<T>> {
  try {
    const url = new URL(path, this.baseUrl)
    if (params) {
      Object.entries(params).forEach(([key, value]) => {
        url.searchParams.set(key, value)
      })
    }

    const response = await this.fetchWithTimeout(url.toString(), {
      method,
      headers: {
        'Content-Type': 'application/json',
        ...this.authHeaders(),
      },
      body: body ? JSON.stringify(body) : undefined,
    })

    if (!response.ok) {
      const text = await response.text()
      return {
        success: false,
        error: text || `Sophia API error while ${action}: ${response.statusText}`,
      }
    }

    if (response.status === 204) {
      return { success: true } as SophiaResponse<T>
    }

    const data = (await response.json()) as T
    return { success: true, data }
  } catch (error) {
    return this.failure(action, error)
  }
}
```

---

## Part 3: Apollo Migration

### 3.1 Update useHCG.ts

**File**: `apollo/webapp/src/hooks/useHCG.ts`

**Changes**:
1. Replace import: `hcgClient` → `sophiaClient`
2. Update all query functions to use `sophiaClient` methods
3. Handle `SophiaResponse` wrapper (check `.success`, extract `.data`)

**Example transformation**:
```typescript
// Before
queryFn: () => hcgClient.getEntities(entityType, limit, offset)

// After
queryFn: async () => {
  const response = await sophiaClient.getHCGEntities(entityType, limit, offset)
  if (!response.success) throw new Error(response.error)
  return response.data ?? []
}
```

### 3.2 Update ChatPanel.tsx

**File**: `apollo/webapp/src/components/ChatPanel.tsx`

**Changes**:
1. Replace import: `hcgClient` → `sophiaClient`
2. Update persona entry creation to use `sophiaClient.createPersonaEntry()`

### 3.3 Update lib/index.ts

**File**: `apollo/webapp/src/lib/index.ts`

**Changes**:
1. Remove exports of `HCGAPIClient`, `hcgClient`, `HCGClientConfig`
2. Add exports of new persona/HCG types from `sophia-client.ts`

### 3.4 Delete Files

| File | Action |
|------|--------|
| `apollo/webapp/src/lib/hcg-client.ts` | DELETE |
| `apollo/src/apollo/data/persona_store.py` | DELETE |

### 3.5 Types to Move

Move from `apollo/webapp/src/types/hcg.ts` to `sophia-client.ts` or delete if duplicated:
- `PersonaEntry`, `CreatePersonaEntryRequest` → Use new types in sophia-client.ts

---

## Part 4: Testing Strategy

### 4.1 Sophia Unit Tests

**File**: `sophia/tests/unit/api/test_persona_endpoints.py`

| Test | Input | Expected |
|------|-------|----------|
| `test_create_persona_entry` | Valid PersonaEntryCreate | 201, entry_id returned |
| `test_create_entry_empty_content` | `{"content": ""}` | 422 validation error |
| `test_list_entries_empty` | No entries exist | `{"entries": [], "total": 0}` |
| `test_list_entries_with_filter` | `?entry_type=decision` | Only decision entries |
| `test_get_entry_not_found` | Invalid entry_id | 404 |
| `test_update_entry` | PATCH with sentiment change | 200, updated entry |
| `test_delete_entry` | DELETE valid entry | 204, subsequent GET returns 404 |
| `test_sentiment_aggregation` | 10 entries with mixed sentiment | Correct distribution |

### 4.2 Sophia Integration Tests

**File**: `sophia/tests/integration/api/test_persona_api_integration.py`

- Test full flow: create → list → get → update → delete
- Test Neo4j persistence via CWMPersistence
- Test auth required on all endpoints

### 4.3 Apollo Tests

- Update existing persona hook tests to use mocked sophiaClient
- Verify useHCG hooks work with new client

---

## Files Affected

### Sophia (Create/Modify)

| File | Action | Description |
|------|--------|-------------|
| `src/sophia/api/models.py` | MODIFY | Add persona request/response models |
| `src/sophia/api/app.py` | MODIFY | Add 6 persona endpoints |
| `tests/unit/api/test_persona_endpoints.py` | CREATE | Unit tests |
| `tests/integration/api/test_persona_api_integration.py` | CREATE | Integration tests |

### Apollo (Modify/Delete)

| File | Action | Description |
|------|--------|-------------|
| `webapp/src/lib/sophia-client.ts` | MODIFY | Add persona + HCG methods, types |
| `webapp/src/hooks/useHCG.ts` | MODIFY | Switch from hcgClient to sophiaClient |
| `webapp/src/components/ChatPanel.tsx` | MODIFY | Switch from hcgClient to sophiaClient |
| `webapp/src/lib/index.ts` | MODIFY | Update exports |
| `webapp/src/lib/hcg-client.ts` | DELETE | No longer needed |
| `src/apollo/data/persona_store.py` | DELETE | No longer needed |

---

## Out of Scope

1. Apollo backend `/api/hcg/*` and `/api/persona/*` endpoints - these become unused but not deleted in this PR
2. WebSocket/real-time persona updates
3. Persona entry versioning/history UI
4. Hermes integration with persona (Hermes creating entries)
5. Migration of existing PersonaEntry nodes to CWMState nodes

---

## Implementation Order

1. **Sophia models** - Add Pydantic models to models.py
2. **Sophia endpoints** - Add 6 endpoints to app.py
3. **Sophia tests** - Unit + integration tests, verify passing
4. **Apollo sophia-client.ts** - Add persona + HCG methods
5. **Apollo useHCG.ts** - Migrate to sophiaClient
6. **Apollo ChatPanel.tsx** - Migrate to sophiaClient
7. **Apollo index.ts** - Update exports
8. **Delete hcg-client.ts**
9. **Delete PersonaDiaryStore.py**
10. **Final verification** - All tests pass, lint/type checks pass
