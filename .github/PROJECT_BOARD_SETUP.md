# Project LOGOS — Project Board & Tracking Guide

This guide replaces the old Phase 1–specific instructions. It reflects the flexible specification: Talos is optional, Apollo must support CLI + browser + LLM surfaces, and the board should cover every phase while still allowing phase-scoped views.

---

## 1. Labels

All labels live in `.github/labels.yml`.

- **Sync automatically**
  ```bash
  python .github/scripts/sync_labels.py --repo c-daly/logos
  ```

- **Manual fallback**: create/edit labels at <https://github.com/c-daly/logos/labels>.

**Label families**
- `component:*` — sophia, hermes, talos, apollo, infrastructure, logos.
- `surface:*` — cli, browser, llm.
- `capability:*` — perception, actuation, explainability.
- `domain:*` — hcg, planner, diagnostics.
- `phase:*` — 1, 2, 3, … (attach to issues instead of project name).
- Standard priority/type/status/workstream labels still apply.

Default rule: Any issue without `capability:actuation` should work without Talos.

---

## 2. Milestones (optional)

If you want a coarse-grained sense of progress, keep three open milestones—no due dates needed:
- **Phase 1 – HCG & Abstract Pipeline**: captures the remaining “phase 1 closers” (#200–#208) until that polish is merged.
- **Phase 2 – Perception & Apollo UX**: browser interface, Talos-free perception demo, multimodal LLM co-processor, planner/executor hardening, diagnostics.
- **Phase 3 – Learning & Embodiment Options**: episodic memory, probabilistic validation, alternative embodiments, multi-agent coordination.

Attach issues to the milestone that matches their label (`phase:1`, `phase:2`, etc.), or skip milestones entirely if labels + board views provide enough signal.

---

## 3. Project Board (“Project LOGOS”)

1. Go to **Projects** → **New project** → choose **Board**.
2. Name it **Project LOGOS** (covers all phases).
3. Set the Status workflow to **Backlog → In Progress → Ready for Demo → Done**. Everything else (HCG, Sophia, perception, Talos, Apollo, diagnostics, docs) should be handled via saved views/filters instead of columns. Recommended saved board views:
   - **Surfaced** – grouped by `surface:*` (CLI / browser / LLM).
   - **Capabilities** – grouped by `capability:*` (perception / actuation / explainability).
   - **Domains** – grouped by `domain:*` (HCG, planner, diagnostics, etc.).
   - **Phase 1 / Phase 2 / …** – filtered by each `phase:*` label so you can focus on one gate at a time.
   - **HCG & Validation**, **Sophia Planning & Execution**, **Perception / Talos-Free**, **Talos Capabilities**, **Apollo & UX**, **Diagnostics / Explainability**, **Docs / Governance** – create board views filtered on the appropriate label sets. This keeps the board uncluttered while still offering the swimlanes we care about.
   - **Demo Tracker** – filtered by Status = Ready for Demo or `capability:explainability`.

### Automation tips
- When an item doesn’t need Talos, drop it straight into Perception/Apollo columns.
- Move items into *Ready for Demo* only after CLI + browser (and soon LLM) paths + diagnostics are verified.
- Use `gh project` if you want to script column/view setup; the board layout above matches the flexible spec.

---

## 4. Issue Creation

Scripts remain available:
```bash
python .github/scripts/generate_issues.py --format gh-cli --output create_issues.sh
python .github/scripts/create_issues_by_epoch.py --help
```
Always review the generated labels and add `surface:*` / `capability:*` as needed.

---

## 5. Linking Issues to the Board

```bash
PROJECT_NUMBER=$(gh project list --owner c-daly --format json | jq -r '.projects[] | select(.title=="Project LOGOS").number')
gh project item-add $PROJECT_NUMBER --repo c-daly/logos --issue <ISSUE>
```

Or use the UI: open Project LOGOS → “+ Add item”.

---

## 6. Maintenance Rhythm

Weekly (or at least bi-weekly):
1. Review “Sophia Planning & Execution” and “Perception / Talos-Free” columns—ensure nothing is stale.
2. Verify each `surface:*` combination has current work; move gaps into Backlog.
3. Update phase labels so Phase views stay trustworthy.
4. Record demo artifacts (logs, videos) before moving cards to Done.

Optional: keep or discard the weekly progress GitHub Action. Many teams now rely on the board views + CLI reports instead.

---

With this setup, the board tracks the entire LOGOS program—from Phase 1 polish through Phase 2 browser/LLM work—without being locked to physical hardware or inaccurate due dates. Use labels + views to focus on whichever phase or surface matters right now, while keeping everything anchored to the flexible spec.
