# Media Ingestion Service Dependencies

This document lists all required dependencies for the LOGOS media ingestion service.

## System Dependencies

### Required (Linux/Ubuntu)

```bash
sudo apt-get update
sudo apt-get install -y \
    ffmpeg \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1
```

### Optional (for WebRTC support)

```bash
sudo apt-get install -y \
    libavcodec-dev \
    libavformat-dev \
    libswscale-dev
```

### macOS

```bash
brew install ffmpeg
```

## Python Dependencies

### Core Dependencies (from pyproject.toml)

```toml
python = "^3.10"
fastapi = "^0.115.0"
uvicorn = {extras = ["standard"], version = "^0.32.0"}
pydantic = "^2.0.0"
neo4j = "^6.0.0"
pymilvus = "^2.3.0"
numpy = "^1.24.0"
slowapi = "^0.1.9"
python-multipart = "^0.0.6"
opentelemetry-api = "^1.20.0"
opentelemetry-sdk = "^1.20.0"
opentelemetry-instrumentation-fastapi = "^0.41b0"
```

### Installation

#### Using Poetry (Recommended)

```bash
poetry install
```

#### Using pip

```bash
pip install -e .
```

Or install from requirements:

```bash
pip install -r requirements.txt
```

## Database Dependencies

### Neo4j

**Version:** 5.13.0 or later

**Installation:**

Using Docker:
```bash
docker run -d \
  --name logos-neo4j \
  -p 7474:7474 -p 7687:7687 \
  -e NEO4J_AUTH=neo4j/logosdev \
  neo4j:5.13.0
```

**Plugins Required:**
- APOC (Awesome Procedures on Cypher)
- neosemantics (for RDF/SHACL support)

**Configuration:**
```properties
NEO4J_AUTH=neo4j/logosdev
NEO4JLABS_PLUGINS=["apoc"]
NEO4J_dbms_security_procedures_unrestricted=apoc.*,n10s.*
```

### Milvus

**Version:** 2.3.3 or later

**Installation:**

Using Docker:
```bash
docker run -d \
  --name logos-milvus \
  -p 19530:19530 -p 9091:9091 \
  -e ETCD_USE_EMBED=true \
  -e COMMON_STORAGETYPE=local \
  milvusdb/milvus:v2.3.3
```

**Python Client:**
```bash
pip install pymilvus>=2.3.0
```

## Infrastructure Dependencies

### Docker

**Version:** 20.10 or later

**Docker Compose Version:** 2.0 or later

**Installation:**
- Linux: https://docs.docker.com/engine/install/
- macOS: https://docs.docker.com/desktop/install/mac-install/
- Windows: https://docs.docker.com/desktop/install/windows-install/

### Storage

**Minimum:**
- 10 GB for media storage (`/tmp/logos_media` or configured path)
- 5 GB for Neo4j data
- 5 GB for Milvus vectors

**Recommended:**
- 100 GB+ for production deployments
- SSD for better I/O performance

## Optional Dependencies

### For Development

```toml
[tool.poetry.group.dev.dependencies]
pytest = "^7.4.0"
pytest-cov = "^4.1.0"
httpx = "^0.27.0"
ruff = "^0.1.0"
mypy = "^1.7.0"
```

### For WebRTC Streaming

```bash
pip install aiortc  # WebRTC for Python
pip install opencv-python  # For video frame processing
```

### For Advanced Image Processing

```bash
pip install pillow  # Image manipulation
pip install imageio  # Reading/writing image data
```

### For Audio Processing

```bash
pip install librosa  # Audio analysis
pip install soundfile  # Audio file I/O
```

## Environment Variables

### Required

```bash
# Neo4j connection
export NEO4J_URI="bolt://localhost:7687"
export NEO4J_USER="neo4j"
export NEO4J_PASSWORD="logosdev"

# Media storage
export MEDIA_STORAGE_PATH="/tmp/logos_media"
```

### Optional

```bash
# Milvus connection
export MILVUS_HOST="localhost"
export MILVUS_PORT="19530"

# Service configuration
export MEDIA_INGEST_HOST="0.0.0.0"
export MEDIA_INGEST_PORT="8002"

# Logging
export LOG_LEVEL="INFO"

# Rate limiting
export RATE_LIMIT_UPLOADS="10/minute"
export RATE_LIMIT_STREAMS="5/minute"
```

## Network Ports

| Service | Port | Protocol | Purpose |
|---------|------|----------|---------|
| Media Ingest API | 8002 | HTTP | REST API endpoints |
| Neo4j Browser | 7474 | HTTP | Web interface |
| Neo4j Bolt | 7687 | TCP | Database connection |
| Milvus | 19530 | gRPC | Vector database |
| Milvus Metrics | 9091 | HTTP | Prometheus metrics |

## Health Check Dependencies

The service health check requires:

1. Neo4j connection (for metadata storage)
2. Disk space in storage path (for media files)
3. Optional: Milvus connection (for embeddings)

**Health Check Endpoint:**
```bash
curl http://localhost:8002/health
```

**Expected Response:**
```json
{
  "status": "healthy",
  "service": "media-ingest",
  "neo4j_connected": true,
  "milvus_connected": false
}
```

## Performance Requirements

### Minimum Hardware

- **CPU:** 2 cores
- **RAM:** 4 GB
- **Storage:** 20 GB
- **Network:** 10 Mbps

### Recommended Hardware

- **CPU:** 4+ cores
- **RAM:** 8+ GB
- **Storage:** 100+ GB SSD
- **Network:** 100+ Mbps

### For GPU Acceleration (Optional)

If using GPU-accelerated JEPA models:

- **GPU:** CUDA-capable (NVIDIA)
- **CUDA:** 11.8 or later
- **cuDNN:** 8.x

```bash
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

## Verification

### Check All Dependencies

```bash
# Python version
python --version  # Should be 3.10+

# Docker
docker --version
docker compose version

# FFmpeg
ffmpeg -version

# Neo4j connectivity
curl http://localhost:7474

# Milvus connectivity
python -c "from pymilvus import connections; connections.connect('default', host='localhost', port='19530'); print('Milvus OK')"

# Storage path
ls -la /tmp/logos_media || echo "Storage path not created yet"
```

### Run Dependency Check Script

```python
#!/usr/bin/env python3
"""Check all media ingestion service dependencies."""

import sys
import subprocess
from pathlib import Path

def check_python_version():
    if sys.version_info < (3, 10):
        print("❌ Python 3.10+ required")
        return False
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor}")
    return True

def check_command(cmd):
    try:
        subprocess.run([cmd, "--version"], capture_output=True, check=True)
        print(f"✅ {cmd}")
        return True
    except:
        print(f"❌ {cmd} not found")
        return False

def check_port(port):
    import socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        result = s.connect_ex(('localhost', port))
        if result == 0:
            print(f"✅ Port {port} is open")
            return True
        else:
            print(f"❌ Port {port} is closed")
            return False

def main():
    print("Checking media ingestion service dependencies...\n")
    
    checks = [
        check_python_version(),
        check_command("docker"),
        check_command("ffmpeg"),
    ]
    
    print("\nChecking services...")
    checks.extend([
        check_port(7687),  # Neo4j
        check_port(19530),  # Milvus
    ])
    
    print("\n" + "="*50)
    if all(checks):
        print("✅ All dependencies satisfied")
        sys.exit(0)
    else:
        print("❌ Some dependencies missing")
        sys.exit(1)

if __name__ == "__main__":
    main()
```

Save as `check_dependencies.py` and run:
```bash
python check_dependencies.py
```

## Troubleshooting

### FFmpeg Not Found

**Linux:**
```bash
sudo apt-get update && sudo apt-get install -y ffmpeg
```

**macOS:**
```bash
brew install ffmpeg
```

### Neo4j Connection Failed

Check if Neo4j is running:
```bash
docker ps | grep neo4j
```

Test connection:
```bash
cypher-shell -a bolt://localhost:7687 -u neo4j -p logosdev "RETURN 1"
```

### Milvus Connection Failed

Check if Milvus is running:
```bash
docker ps | grep milvus
```

Test connection:
```bash
python -c "from pymilvus import connections; connections.connect('default', host='localhost', port='19530')"
```

### Storage Path Permission Denied

```bash
sudo mkdir -p /tmp/logos_media
sudo chmod 777 /tmp/logos_media
```

Or use a user-writable path:
```bash
export MEDIA_STORAGE_PATH="$HOME/.logos/media"
mkdir -p $MEDIA_STORAGE_PATH
```

## References

- FFmpeg: https://ffmpeg.org/
- Neo4j: https://neo4j.com/docs/
- Milvus: https://milvus.io/docs/
- FastAPI: https://fastapi.tiangolo.com/
- Docker: https://docs.docker.com/
