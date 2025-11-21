# Testing Issue Backlog (Talos)

Purpose: track concrete testing/CI issues to close remaining gaps in the `talos` package (current coverage: ~96% from local run with `PYTHONPATH=src pytest --cov=talos --cov-report=term-missing`).

## Issue 1: Add GitHub Actions CI for Talos
- Problem: `talos` lacks CI; tests/format/type checks/coverage aren’t enforced on PRs.
- Proposal: Create `.github/workflows/ci.yml` mirroring apollo/hermes/sophia: setup Python 3.11/3.12, install with `pip install -e ".[dev]"` (or poetry `--with dev`), run `ruff`, `black --check`, `mypy`, `pytest --cov=talos --cov-report=xml --cov-report=term`, upload coverage to Codecov.
- Acceptance: Workflow runs on push+PR to main/develop, passes in a clean checkout, publishes coverage artifact and Codecov upload.

## Issue 2: Cover actuator metadata and telemetry branches
- Problem: `SimulatedMotor.get_info` and `SimulatedGripper.get_info` plus the `release` telemetry path remain uncovered (reported misses at `src/talos/actuators/motor.py:127-135`, `src/talos/actuators/gripper.py:132,181-187`).
- Proposal: Add tests that assert metadata fields (min/max/velocity/max_opening, enabled flag) and verify `release` records `OBJECT_RELEASED` and clears grasp state.
- Acceptance: New tests pass and coverage no longer reports misses in those lines.

## Issue 3: Cover pick-and-place failure paths and telemetry count
- Problem: Failure branches in `execute_pick_and_place` and telemetry count reporting are untested (`pick_and_place.py:155, 230, 235, 240, 245`).
- Proposal: Add tests that assert `telemetry_event_count` increments; failure flows for invalid object/location, failed grasp, failed release return expected flags/action logs without mutating state.
- Acceptance: Tests pass and coverage marks those lines as exercised.

## Issue 4: Package exports and abstract base safeguards
- Problem: Misses stem from re-export lines in `src/talos/__init__.py:45-47` and abstract `read`/`get_state` fall-throughs (`sensors/base.py:29`, `actuators/base.py:45`).
- Proposal: Add import smoke tests ensuring `from talos import Sensors, Actuators, TelemetryRecorder` (per exports) works; optionally mark abstract `pass` lines with `# pragma: no cover` if keeping the pattern.
- Acceptance: Either coverage ignores these lines via pragma or import tests cover them; no coverage warnings for these paths.

## Issue 5: Enforce coverage threshold in CI
- Problem: No guard prevents regressions below current coverage.
- Proposal: In CI, add `coverage xml` + `coverage report --fail-under=95` (or equivalent pytest `--cov-fail-under`) to fail builds when coverage drops.
- Acceptance: CI fails if coverage < threshold; documented in workflow.

## Issue 6: Harmonize local dev install docs
- Problem: Confusion between extras vs. poetry groups caused earlier install friction.
- Proposal: Update README to document talos dev setup (`pip install -e ".[dev]"` or `poetry install --with dev`) and remind to set `PYTHONPATH=src` when running pytest without editable install.
- Acceptance: README update merged; new contributors can run tests without import/coverage errors.
