# Getting Started with LOGOS

This guide gets you from zero to running tests in 10 minutes.

## Prerequisites

- **Docker** and **Docker Compose** (for Neo4j, Milvus)
- **Python 3.11+** and **Poetry** (for all Python repos)
- **Node.js 18+** and **npm** (for Apollo webapp)

```bash
# Verify prerequisites
docker --version && docker compose version
python3 --version && poetry --version
node --version && npm --version
```

## 1. Clone All Repos

```bash
mkdir -p ~/projects/LOGOS && cd ~/projects/LOGOS

# Clone all repos
for repo in logos hermes apollo sophia talos; do
  git clone https://github.com/c-daly/$repo.git
done
```

## 2. Start Infrastructure

The shared dev infrastructure (Neo4j + Milvus) runs from the logos repo:

```bash
cd logos
docker compose -f infra/docker-compose.hcg.dev.yml up -d

# Verify services are running
docker compose -f infra/docker-compose.hcg.dev.yml ps
```

Expected services:
- `logos-hcg-neo4j` → http://localhost:7474 (neo4j/neo4jtest)
- `logos-hcg-milvus` → localhost:19530

## 3. Install Dependencies

```bash
# Install each Python repo
for repo in logos hermes sophia talos; do
  cd ~/projects/LOGOS/$repo
  poetry install
done

# Install Apollo webapp
cd ~/projects/LOGOS/apollo/webapp
npm install
```

## 4. Run Tests

Each repo can run tests independently:

```bash
# Unit tests (no infrastructure needed)
cd ~/projects/LOGOS/sophia
poetry run pytest tests/unit/ -v

# Integration tests (requires infrastructure)
cd ~/projects/LOGOS/talos
./scripts/run_integration_stack.sh
```

## 5. Run Services

```bash
# Start Hermes (language/embedding service)
cd ~/projects/LOGOS/hermes
poetry run uvicorn hermes.api:app --host 0.0.0.0 --port 8080

# Start Sophia (cognitive core)
cd ~/projects/LOGOS/sophia
poetry run uvicorn sophia.api.app:app --host 0.0.0.0 --port 8000

# Start Apollo webapp
cd ~/projects/LOGOS/apollo/webapp
npm run dev
```

## Port Reference

Each repo uses a unique port prefix for test isolation:

| Repo | Prefix | Neo4j | Milvus | API |
|------|--------|-------|--------|-----|
| hermes | 17xxx | 17474/17687 | 17530 | 17000 |
| apollo | 27xxx | 27474/27687 | 27530 | 27000 |
| logos | 37xxx | 37474/37687 | 37530 | 37000 |
| sophia | 47xxx | 47474/47687 | 47530 | 47000 |
| talos | 57xxx | 57474/57687 | 57530 | 57000 |

Dev infrastructure uses default ports (7474, 7687, 19530).

## What's Next?

- [Architecture Overview](ARCHITECTURE.md) - How the repos connect
- [Testing Guide](TESTING.md) - Test categories, running integration tests
- [SDK Guide](SDK_GUIDE.md) - Using and regenerating the client SDKs
- [Infrastructure](INFRASTRUCTURE.md) - Neo4j, Milvus, observability setup
