# Media Ingestion Service - Quick Start

This guide provides step-by-step instructions to get the LOGOS media ingestion service running.

## Prerequisites

- Python 3.10+
- Docker and Docker Compose
- Neo4j (via Docker)

## Quick Start (Development)

### 1. Install Dependencies

```bash
cd /path/to/logos
pip install -e .
```

### 2. Start Neo4j

```bash
docker compose -f infra/docker-compose.hcg.dev.yml up -d neo4j
```

Wait for Neo4j to be ready (~30 seconds):
```bash
curl http://localhost:7474
```

### 3. Run Media Ingestion Service

```bash
uvicorn logos_perception.app:app --host 0.0.0.0 --port 8002
```

Or with reload for development:
```bash
uvicorn logos_perception.app:app --host 0.0.0.0 --port 8002 --reload
```

### 4. Verify Service is Running

```bash
curl http://localhost:8002/health
```

Expected response:
```json
{
  "status": "healthy",
  "service": "media-ingest",
  "neo4j_connected": true,
  "milvus_connected": false
}
```

### 5. View API Documentation

Open in browser: http://localhost:8002/docs

## Quick Start (Docker)

### 1. Build Docker Image

```bash
cd infra
docker build -f Dockerfile.media-ingest -t logos-media-ingest:latest ..
```

### 2. Start All Services

```bash
docker compose -f docker-compose.hcg.dev.yml up -d
```

This starts:
- Neo4j (ports 7474, 7687)
- Milvus (ports 19530, 9091)
- Media Ingest Service (port 8002)

### 3. Check Service Health

```bash
docker compose -f docker-compose.hcg.dev.yml ps
curl http://localhost:8002/health
```

## Usage Examples

### Upload an Image

```bash
# Set authentication token
export TOKEN="test-token-12345678"

# Upload image
curl -X POST http://localhost:8002/media/upload \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@path/to/image.jpg" \
  -F 'metadata={"source":"camera-1","scene":"workspace"}'
```

Response:
```json
{
  "media_id": "abc-123-def-456",
  "timestamp": "2025-11-20T18:47:00Z",
  "format": "image/jpeg",
  "size_bytes": 245678,
  "status": "uploaded"
}
```

### Start a Stream

```bash
curl -X POST http://localhost:8002/media/stream/start \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "source": "webcam",
    "fps": 10,
    "format": "image/jpeg"
  }'
```

### Trigger Simulation (via Sophia)

```bash
# Assuming Sophia service is running on port 8000
curl -X POST http://localhost:8000/sophia/simulate \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "capability_id": "perception-question",
    "context": {
      "perception_sample_id": "'$MEDIA_ID'",
      "question": "Will the jump clear the obstacle?"
    },
    "k_steps": 5
  }'
```

## Configuration

### Environment Variables

```bash
# Neo4j connection
export NEO4J_URI="bolt://localhost:7687"
export NEO4J_USER="neo4j"
export NEO4J_PASSWORD="logosdev"

# Media storage
export MEDIA_STORAGE_PATH="/tmp/logos_media"

# Optional: Milvus
export MILVUS_HOST="localhost"
export MILVUS_PORT="19530"
```

### Storage Location

By default, uploaded media is stored in `/tmp/logos_media`.

To change:
```bash
export MEDIA_STORAGE_PATH="/your/custom/path"
mkdir -p $MEDIA_STORAGE_PATH
```

## Testing

### Run All Tests

```bash
pytest tests/phase2/perception/ -v
```

### Run Media API Tests Only

```bash
pytest tests/phase2/perception/test_media_api.py -v
```

### Run Verification Script

```bash
python scripts/verify_media_ingestion.py
```

## Troubleshooting

### Service Won't Start

**Check Python version:**
```bash
python --version  # Should be 3.10+
```

**Install missing dependencies:**
```bash
pip install -e .
```

### Neo4j Connection Failed

**Check if Neo4j is running:**
```bash
docker ps | grep neo4j
```

**Test Neo4j connection:**
```bash
curl http://localhost:7474
```

**Check credentials:**
```bash
# Default credentials for dev environment
# Username: neo4j
# Password: logosdev
```

### Upload Fails with 401 Unauthorized

**Token must be at least 8 characters:**
```bash
# ❌ Too short
export TOKEN="short"

# ✅ Valid
export TOKEN="test-token-12345678"
```

### Port Already in Use

**Check what's using port 8002:**
```bash
lsof -i :8002
```

**Use a different port:**
```bash
uvicorn logos_perception.app:app --port 8003
```

## Documentation

- **CLI Usage:** `docs/phase2/perception/MEDIA_INGESTION_CLI.md`
- **Browser Integration:** `docs/phase2/perception/MEDIA_INGESTION_BROWSER.md`
- **Dependencies:** `docs/phase2/perception/DEPENDENCIES.md`
- **Phase 2 Spec:** `docs/phase2/PHASE2_SPEC.md`
- **Verification:** `docs/phase2/VERIFY.md`

## API Reference

### Endpoints

| Endpoint | Method | Auth | Description |
|----------|--------|------|-------------|
| `/` | GET | No | Service info |
| `/health` | GET | No | Health check |
| `/media/health` | GET | No | Detailed health |
| `/media/upload` | POST | Yes | Upload file |
| `/media/stream/start` | POST | Yes | Start stream |
| `/media/stream/{id}/stop` | POST | Yes | Stop stream |
| `/media/frames/{id}` | GET | Yes | Get metadata |
| `/docs` | GET | No | Swagger UI |

### Authentication

All `/media/*` endpoints (except `/media/health`) require authentication:

```bash
Authorization: Bearer <your-token>
```

Token requirements:
- Minimum 8 characters
- No special format required for Phase 2
- Production should use JWT or OAuth2

## Development

### Project Structure

```
logos_perception/
├── __init__.py          # Module exports
├── app.py               # FastAPI application
├── media_api.py         # API endpoints
├── ingest.py            # Media ingestion logic
├── jepa_runner.py       # JEPA simulation runner
└── models.py            # Pydantic models
```

### Running with Hot Reload

```bash
uvicorn logos_perception.app:app --reload --port 8002
```

### Viewing Logs

```bash
# Service logs
docker logs logos-media-ingest -f

# Neo4j logs
docker logs logos-hcg-neo4j -f
```

## Next Steps

1. **Production Deployment**
   - Set up proper authentication (JWT/OAuth2)
   - Configure object storage (S3/MinIO)
   - Add rate limiting
   - Set up monitoring

2. **Integration**
   - Connect Sophia service for simulation
   - Add Milvus for embedding search
   - Integrate with Apollo browser UI

3. **Features**
   - WebRTC streaming implementation
   - File watcher for directory monitoring
   - Advanced frame processing
   - Batch upload support

## Support

- **Issues:** https://github.com/c-daly/logos/issues
- **Spec:** `docs/phase2/PHASE2_SPEC.md`
- **Verification:** `logs/p2-m3-verification/VERIFICATION_SUMMARY.md`
