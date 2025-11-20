# LOGOS Utility Scripts

This directory collects helper scripts that wrap the repetitive steps for
standing up the local infrastructure (Milvus/etcd/MinIO), seeding data, and
running the canonical test suites.

## Available scripts

| Script | Description |
| --- | --- |
| `test_logos.sh` | Starts the LOGOS HCG stack (Milvus/etcd/MinIO) via `infra/docker-compose.hcg.dev.yml`, initializes the Milvus collections, and runs `poetry run pytest`. Pass additional arguments to forward them to pytest. |
| `test_hermes.sh` | Spins up Hermes' test-only stack (`docker-compose.test.yml`), installs dev/ML dependencies, and executes the Hermes pytest suite. |

### Usage

From the `logos/` repository root:

```bash
./utils/test_logos.sh                    # run the full LOGOS pytest suite
./utils/test_logos.sh tests/infra -k milvus  # run a subset

./utils/test_hermes.sh                   # run hermes tests (expects ../hermes)
./utils/test_hermes.sh tests/test_api.py # pass through pytest args
```

Both scripts accept the environment variable `KEEP_LOGOS_INFRA=1` (or
`KEEP_HERMES_INFRA=1`) to skip shutting down the docker-compose services after
tests complete. This is handy if you want to leave the services running for
additional manual debugging.

> Note: The Hermes script assumes the `hermes/` repository lives next to
> `logos/` (i.e., `../hermes`). Adjust `HERMES_REPO` if it is elsewhere.
