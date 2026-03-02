# Developer Tooling

Tools built to support LOGOS development workflow. Each addresses a specific friction point in building a multi-repo cognitive architecture with AI agents.

## Workflow Orchestration

| Tool | Repo | Contribution to LOGOS |
|------|------|----------------------|
| **agent-swarm** | [c-daly/agent-swarm](https://github.com/c-daly/agent-swarm) | Enforces disciplined agent workflows in Claude Code — phase gates (intake → design → implement → verify → review), tool blocking during implementation to force subagent delegation, script routing for batch operations. The `develop` workflow simulates a full SE team (PM → Researcher → Architect → Implementer → Reviewer → Git-agent) with TDD loops and kickback paths for test failures and review issues |
| **parallel-orchestration** | [c-daly/parallel-orchestration](https://github.com/c-daly/parallel-orchestration) | Parallel TDD subagent orchestration plugin. Enables running multiple isolated implementation agents in git worktrees simultaneously — critical for LOGOS where a single feature often touches logos, sophia, and hermes in parallel |
| **chiron** | [c-daly/chiron](https://github.com/c-daly/chiron) | Model-agnostic agent orchestration via cascading intent discovery. Provides explicit mode management (Explore/Propose/Execute/Critique/Reevaluate), session state persistence, and automatic reevaluation triggers. Earlier iteration of the workflow discipline now in agent-swarm |

## Knowledge & Session Management

| Tool | Repo | Contribution to LOGOS |
|------|------|----------------------|
| **vault-cli** | [c-daly/vault-cli](https://github.com/c-daly/vault-cli) | Terminal CLI for Obsidian vaults — quick capture, search, sync, and Claude Code session harvesting. Bridges the gap between LOGOS development sessions and the Obsidian knowledge base where research notes, paper tracking, and design reasoning live |
| **PM agent** | `logos/.claude/agents/project-manager.md` | Project management agent for status/vision/ticket workflows. Maintains VISION.md and STATUS.md, captures ideas as tickets, detects documentation drift |

## Hardware & Embodiment

| Tool | Repo | Contribution to LOGOS |
|------|------|----------------------|
| **pyBittle** | [c-daly/pyBittle](https://github.com/c-daly/pyBittle) | Python library for controlling the Petoi Bittle robot via Bluetooth/WiFi/Serial. First hardware target for Talos — provides a real embodiment platform for testing Sophia's plans against physical actuation |
