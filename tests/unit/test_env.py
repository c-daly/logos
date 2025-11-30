from pathlib import Path

import pytest

import logos_test_utils.env as env_module
from logos_test_utils.env import _get_repo_root_from_items, get_repo_root


def clear_cache() -> None:
    _get_repo_root_from_items.cache_clear()


@pytest.fixture(autouse=True)
def reset_cache_and_env(monkeypatch):
    clear_cache()
    monkeypatch.delenv("LOGOS_REPO_ROOT", raising=False)
    monkeypatch.delenv("GITHUB_WORKSPACE", raising=False)
    yield
    clear_cache()


def test_repo_root_prefers_os_env(monkeypatch, tmp_path: Path):
    target = tmp_path / "repo"
    target.mkdir()
    monkeypatch.setenv("LOGOS_REPO_ROOT", str(target))

    assert get_repo_root() == target


def test_repo_root_uses_provided_env_mapping(tmp_path: Path):
    target = tmp_path / "mapped"
    target.mkdir()

    assert get_repo_root({"LOGOS_REPO_ROOT": str(target)}) == target


def test_repo_root_falls_back_to_github_workspace(monkeypatch, tmp_path: Path):
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    monkeypatch.setenv("GITHUB_WORKSPACE", str(workspace))
    monkeypatch.delenv("LOGOS_REPO_ROOT", raising=False)
    monkeypatch.delenv("LOGOS_STACK_ENV", raising=False)

    assert get_repo_root({}) == workspace


def test_repo_root_defaults_to_package_parent(monkeypatch):
    monkeypatch.delenv("LOGOS_REPO_ROOT", raising=False)
    monkeypatch.delenv("GITHUB_WORKSPACE", raising=False)

    expected = Path(env_module.__file__).resolve().parents[1]
    assert get_repo_root() == expected


def test_repo_root_cache_reuses_value(monkeypatch, tmp_path: Path):
    first = tmp_path / "first"
    first.mkdir()
    monkeypatch.setenv("LOGOS_REPO_ROOT", str(first))
    one = get_repo_root()

    second = tmp_path / "second"
    second.mkdir()
    monkeypatch.setenv("LOGOS_REPO_ROOT", str(second))
    two = get_repo_root()

    assert one is two
    assert two == first
