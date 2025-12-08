# Getting Started with LOGOS

This guide gets you from zero to running tests in 10 minutes.

## Prerequisites

- **Docker** and **Docker Compose**
- **Python 3.11+** and **Poetry**
- **Node.js 18+** and **npm** (for Apollo webapp only)

```bash
# Verify prerequisites
docker --version && docker compose version
python3 --version && poetry --version
node --version && npm --version
```

## 1. Clone All Repos

```bash
mkdir -p ~/projects/LOGOS && cd ~/projects/LOGOS

for repo in logos hermes apollo sophia talos; do
  git clone https://github.com/c-daly/$repo.git
done
```

## 2. Install Dependencies

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

## 3. Run Tests

Each repo has scripts in `scripts/` for running tests. These handle starting containers, waiting for health, and running pytest:

```bash
cd ~/projects/LOGOS/sophia

# Unit tests (no containers needed)
./scripts/test_unit.sh
# or: poetry run pytest tests/unit/ -v

# Integration tests (starts containers automatically)
./scripts/run_integration_stack.sh
```

### Common Scripts

| Script | Purpose |
|--------|---------|
| `test_unit.sh` | Run unit tests (no containers) |
| `test_integration.sh` | Run integration tests |
| `run_integration_stack.sh` | Start containers + run integration tests |
| `test_all.sh` | Run all tests |

Each repo is containerized and manages its own infrastructure via Docker Compose. The scripts handle setup/teardown automatically.

## Port Allocation

Each repo uses unique ports to allow concurrent test runs:

| Repo | Prefix | Neo4j | Milvus |
|------|--------|-------|--------|
| hermes | 17xxx | 17474/17687 | 17530 |
| apollo | 27xxx | 27474/27687 | 27530 |
| logos | 37xxx | 37474/37687 | 37530 |
| sophia | 47xxx | 47474/47687 | 47530 |
| talos | 57xxx | 57474/57687 | 57530 |

## Next Steps

- [Architecture Overview](../architecture/ARCHITECTURE.md) - How the repos connect
- [Testing Guide](TESTING.md) - Test categories and CI parity
- [Infrastructure Guide](INFRASTRUCTURE.md) - Neo4j, Milvus details

Dev infrastructure uses default ports (7474, 7687, 19530).

## What's Next?

- [Architecture Overview](ARCHITECTURE.md) - How the repos connect
- [Testing Guide](TESTING.md) - Test categories, running integration tests
- [SDK Guide](SDK_GUIDE.md) - Using and regenerating the client SDKs
- [Infrastructure](INFRASTRUCTURE.md) - Neo4j, Milvus, observability setup
