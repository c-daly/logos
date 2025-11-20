# Media Ingestion CLI Instructions

This document provides instructions for submitting media samples and perception questions using the LOGOS media ingestion service.

## Prerequisites

- Media ingestion service running (see [Setup](#setup))
- Valid authentication token
- `curl` or similar HTTP client installed

## Setup

### Start the Media Ingestion Service

#### Option 1: Using Docker Compose

```bash
cd infra
docker compose -f docker-compose.hcg.dev.yml up -d media-ingest
```

#### Option 2: Running Locally with Poetry

```bash
cd /path/to/logos
poetry install
poetry run uvicorn logos_perception.app:app --host 0.0.0.0 --port 8002
```

### Verify Service is Running

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

## Authentication

All media ingestion endpoints require authentication. Set your token as an environment variable:

```bash
export LOGOS_TOKEN="your-token-here-minimum-8-chars"
```

## Uploading Media

### Upload an Image

```bash
curl -X POST http://localhost:8002/media/upload \
  -H "Authorization: Bearer $LOGOS_TOKEN" \
  -F "file=@path/to/image.jpg" \
  -F 'metadata={"source":"camera-1","scene":"robot_workspace"}'
```

Response:
```json
{
  "media_id": "uuid-abc-123",
  "timestamp": "2025-11-20T18:47:00Z",
  "format": "image/jpeg",
  "size_bytes": 245678,
  "status": "uploaded"
}
```

### Upload a Video Frame

```bash
curl -X POST http://localhost:8002/media/upload \
  -H "Authorization: Bearer $LOGOS_TOKEN" \
  -F "file=@frame_0001.png" \
  -F 'metadata={"source":"webcam","frame_number":1,"timestamp":"2025-11-20T18:47:00Z"}'
```

### Upload Audio

```bash
curl -X POST http://localhost:8002/media/upload \
  -H "Authorization: Bearer $LOGOS_TOKEN" \
  -F "file=@audio_sample.wav" \
  -F 'metadata={"source":"microphone","duration_sec":5.2}'
```

## Starting a Media Stream

For continuous frame ingestion (e.g., from a webcam or file watcher):

```bash
curl -X POST http://localhost:8002/media/stream/start \
  -H "Authorization: Bearer $LOGOS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "source": "webcam",
    "fps": 10,
    "format": "image/jpeg"
  }'
```

Response:
```json
{
  "stream_id": "uuid-stream-456",
  "source": "webcam",
  "status": "active"
}
```

### Stop a Stream

```bash
curl -X POST http://localhost:8002/media/stream/{stream_id}/stop \
  -H "Authorization: Bearer $LOGOS_TOKEN"
```

## Submitting Perception Questions

After uploading media, you can submit perception questions by triggering imagination simulations.

### 1. Upload the Perception Sample

```bash
MEDIA_ID=$(curl -X POST http://localhost:8002/media/upload \
  -H "Authorization: Bearer $LOGOS_TOKEN" \
  -F "file=@robot_jump_scene.jpg" \
  -F 'metadata={"scene":"robot_about_to_jump","question":"will_jump_clear"}' \
  | jq -r '.media_id')

echo "Uploaded media: $MEDIA_ID"
```

### 2. Trigger Imagination Simulation

```bash
curl -X POST http://localhost:8000/sophia/simulate \
  -H "Authorization: Bearer $LOGOS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "capability_id": "jump-prediction",
    "context": {
      "entity_id": "robot-01",
      "perception_sample_id": "'$MEDIA_ID'",
      "question": "will the jump clear the obstacle?"
    },
    "k_steps": 10
  }'
```

Response:
```json
{
  "process_uuid": "uuid-sim-789",
  "states_count": 10,
  "horizon": 10,
  "model_version": "jepa-v0.1"
}
```

### 3. Retrieve Simulation Results

```bash
curl http://localhost:8000/sophia/simulate/{process_uuid} \
  -H "Authorization: Bearer $LOGOS_TOKEN"
```

Response:
```json
{
  "process": {
    "uuid": "uuid-sim-789",
    "capability_id": "jump-prediction",
    "imagined": true,
    "horizon": 10
  },
  "states": [
    {
      "uuid": "state-1",
      "step": 0,
      "confidence": 1.0
    },
    {
      "uuid": "state-2",
      "step": 1,
      "confidence": 0.95
    }
  ]
}
```

## Querying Frame Metadata

To retrieve metadata for an uploaded frame:

```bash
curl http://localhost:8002/media/frames/{frame_id} \
  -H "Authorization: Bearer $LOGOS_TOKEN"
```

## Example Workflows

### Workflow 1: Predict Object Motion

```bash
# 1. Upload current scene
FRAME_ID=$(curl -X POST http://localhost:8002/media/upload \
  -H "Authorization: Bearer $LOGOS_TOKEN" \
  -F "file=@current_scene.jpg" \
  | jq -r '.media_id')

# 2. Ask: Where will the red block be in 5 steps?
curl -X POST http://localhost:8000/sophia/simulate \
  -H "Authorization: Bearer $LOGOS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "capability_id": "object-motion-prediction",
    "context": {
      "perception_sample_id": "'$FRAME_ID'",
      "target_object": "red_block",
      "question": "predict position after pick-and-place"
    },
    "k_steps": 5
  }'
```

### Workflow 2: Continuous Scene Monitoring

```bash
# 1. Start stream
STREAM_ID=$(curl -X POST http://localhost:8002/media/stream/start \
  -H "Authorization: Bearer $LOGOS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"source":"lab_camera","fps":5}' \
  | jq -r '.stream_id')

# 2. Stream processes frames automatically...
# (in production, frames trigger JEPA processing via queue)

# 3. Stop stream when done
curl -X POST http://localhost:8002/media/stream/$STREAM_ID/stop \
  -H "Authorization: Bearer $LOGOS_TOKEN"
```

## Rate Limits

The media ingestion service implements rate limiting:

- **Uploads**: 10 per minute per client
- **Stream start**: 5 per minute per client
- **Stream stop**: 10 per minute per client

If you exceed the rate limit, you'll receive a `429 Too Many Requests` response.

## Error Handling

### Common Error Responses

**401 Unauthorized** - Invalid or missing authentication token
```json
{
  "detail": "Invalid authentication token"
}
```

**400 Bad Request** - Invalid metadata JSON
```json
{
  "detail": "Invalid metadata JSON"
}
```

**404 Not Found** - Frame or stream not found
```json
{
  "detail": "Frame {frame_id} not found"
}
```

**429 Too Many Requests** - Rate limit exceeded
```json
{
  "detail": "Rate limit exceeded"
}
```

**500 Internal Server Error** - Server error
```json
{
  "detail": "Upload failed: [error message]"
}
```

## API Documentation

For full API documentation, visit:
```
http://localhost:8002/docs
```

This provides an interactive Swagger UI for testing endpoints.

## Troubleshooting

### Service Not Starting

Check Docker logs:
```bash
docker logs logos-media-ingest
```

### Neo4j Connection Issues

Verify Neo4j is running:
```bash
docker ps | grep neo4j
curl http://localhost:7474
```

### Uploads Failing

1. Check file size (large files may timeout)
2. Verify authentication token is valid
3. Check disk space in `/tmp/logos_media` or configured storage path
4. Review service logs for detailed error messages

## Next Steps

- See `docs/phase2/VERIFY.md` for verification instructions
- See `docs/phase2/PHASE2_SPEC.md` for full Phase 2 specification
- See `logos_perception/README.md` for API integration details
