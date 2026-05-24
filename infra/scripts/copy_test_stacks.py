"""Copy rendered test-stack files from logos into each downstream repo.

Companion to ``render_test_stacks.py``. The renderer writes each repo's
generated stack into ``logos/infra/<repo>/`` (the canonical, generated
copies). This script distributes those into each downstream repo's
committed location — the step previously done by hand.

Layout / conventions:
- **Source** for a repo is the renderer's output dir, resolved exactly the
  way ``render_test_stacks.py`` resolves it (``TEST_STACK_DIR / path`` from
  ``repos.yaml``), so the two scripts never disagree.
- **Destination** is ``<repo>/containers/`` — the stated convention (docker +
  env files live in ``containers/``). Repos that currently keep them
  elsewhere (e.g. ``tests/e2e/stack/<repo>/``) are standardized here; this
  script only writes the canonical location, it does not delete old copies.
- ``logos`` is skipped: it *creates* these files, it does not consume them.

Files moved per repo: the compose file, the env file, and ``STACK_VERSION``
(whatever ``repos.yaml`` names them). It copies only what the renderer
produces; hand-maintained variants like ``docker-compose.test.<repo>.yml``
are left untouched.

Usage:
  poetry run python infra/scripts/copy_test_stacks.py            # all downstream repos
  poetry run python infra/scripts/copy_test_stacks.py --repo apollo --repo sophia
  poetry run python infra/scripts/copy_test_stacks.py --check    # verify, write nothing
"""

from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

# Reuse the renderer's own path/config resolution so source dirs, filenames,
# and the repo list stay in lockstep with what was rendered.
sys.path.insert(0, str(Path(__file__).resolve().parent))
from render_test_stacks import (  # noqa: E402
    REPOS_FILE,
    ROOT,
    TEST_STACK_DIR,
    RenderError,
    load_yaml,
    resolve_repo_configs,
)

# logos generates the stacks; it is not a downstream consumer of them.
SOURCE_ONLY = {"logos"}
# Stated convention: rendered docker/env files live in <repo>/containers/.
DEST_SUBDIR = "containers"
# Downstream repos are siblings of the logos repo (ROOT == logos repo root).
WORKSPACE_ROOT = ROOT.parent


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Copy rendered test-stack files from logos into each downstream repo.",
    )
    parser.add_argument(
        "--repo",
        action="append",
        dest="repos",
        help="Copy only the specified repo(s). Default: all downstream repos.",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Do not write; verify each destination already matches the rendered source.",
    )
    return parser.parse_args()


def files_match(src: Path, dst: Path) -> bool:
    return dst.exists() and dst.read_bytes() == src.read_bytes()


def copy_repo(name: str, repo_cfg: dict, *, check_only: bool) -> bool:
    """Copy/verify one repo's stack files. Returns True if dest is in sync."""
    src_dir = (TEST_STACK_DIR / repo_cfg["path"]).resolve()
    dest_dir = WORKSPACE_ROOT / name / DEST_SUBDIR
    artifacts = [repo_cfg["compose_filename"], repo_cfg["env_filename"], "STACK_VERSION"]

    missing = [f for f in artifacts if not (src_dir / f).exists()]
    if missing:
        raise RenderError(
            f"{name}: rendered source missing {missing} in {src_dir} "
            f"(run render_test_stacks.py first)"
        )

    in_sync = True
    for fname in artifacts:
        src = src_dir / fname
        dst = dest_dir / fname
        if check_only:
            in_sync = in_sync and files_match(src, dst)
        elif not files_match(src, dst):
            dest_dir.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)
    return in_sync


def main() -> int:
    args = parse_args()
    resolved = resolve_repo_configs(load_yaml(REPOS_FILE), args.repos)

    all_ok = True
    for name, repo_cfg in resolved.items():
        if name in SOURCE_ONLY:
            print(f"[skip ] {name}: source-only (creates configs, does not consume them)")
            continue
        try:
            ok = copy_repo(name, repo_cfg, check_only=args.check)
        except RenderError as exc:
            print(f"[error] {exc}", file=sys.stderr)
            return 1
        prefix = "CHECK" if args.check else "COPY "
        status = "in sync" if ok else ("stale" if args.check else "copied")
        print(f"[{prefix}] {name}: {status} -> {WORKSPACE_ROOT / name / DEST_SUBDIR}")
        all_ok = all_ok and ok

    if args.check and not all_ok:
        print("At least one destination is out of sync with the rendered source.", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
