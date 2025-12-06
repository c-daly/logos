"""Tests for logos_config.env module."""

from __future__ import annotations

import os
import tempfile
from pathlib import Path
from unittest import mock

from logos_config.env import get_env_value, get_repo_root, load_env_file


class TestGetEnvValue:
    """Tests for get_env_value function."""

    def test_returns_os_env_first(self) -> None:
        """OS environment takes priority over mapping and default."""
        with mock.patch.dict(os.environ, {"TEST_KEY": "from_os"}):
            result = get_env_value("TEST_KEY", {"TEST_KEY": "from_mapping"}, "default")
            assert result == "from_os"

    def test_returns_mapping_when_not_in_os(self) -> None:
        """Mapping is used when key not in OS environment."""
        # Ensure key is not in OS env
        os.environ.pop("TEST_KEY_2", None)
        result = get_env_value("TEST_KEY_2", {"TEST_KEY_2": "from_mapping"}, "default")
        assert result == "from_mapping"

    def test_returns_default_when_not_found(self) -> None:
        """Default is used when key not in OS env or mapping."""
        os.environ.pop("TEST_KEY_3", None)
        result = get_env_value("TEST_KEY_3", {"OTHER_KEY": "value"}, "default")
        assert result == "default"

    def test_returns_none_when_no_default(self) -> None:
        """None is returned when key not found and no default."""
        os.environ.pop("NONEXISTENT_KEY", None)
        result = get_env_value("NONEXISTENT_KEY")
        assert result is None

    def test_handles_none_mapping(self) -> None:
        """Works correctly when mapping is None."""
        os.environ.pop("TEST_KEY_4", None)
        result = get_env_value("TEST_KEY_4", None, "default")
        assert result == "default"


class TestGetRepoRoot:
    """Tests for get_repo_root function."""

    def test_uses_repo_specific_env_var(self) -> None:
        """Repo-specific env var takes priority."""
        with tempfile.TemporaryDirectory() as tmpdir:
            with mock.patch.dict(os.environ, {"HERMES_REPO_ROOT": tmpdir}):
                result = get_repo_root("hermes")
                assert result == Path(tmpdir).resolve()

    def test_uses_github_workspace(self) -> None:
        """GITHUB_WORKSPACE is used in CI when repo-specific var not set."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Clear any repo-specific var
            os.environ.pop("HERMES_REPO_ROOT", None)
            with mock.patch.dict(os.environ, {"GITHUB_WORKSPACE": tmpdir}):
                result = get_repo_root("hermes")
                assert result == Path(tmpdir).resolve()

    def test_walks_up_to_find_git(self) -> None:
        """Finds .git directory by walking up from cwd."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create a fake repo structure
            git_dir = Path(tmpdir) / ".git"
            git_dir.mkdir()
            subdir = Path(tmpdir) / "src" / "mypackage"
            subdir.mkdir(parents=True)

            # Clear env vars that would take priority
            os.environ.pop("MYREPO_REPO_ROOT", None)
            os.environ.pop("GITHUB_WORKSPACE", None)

            with mock.patch("os.getcwd", return_value=str(subdir)):
                result = get_repo_root("myrepo")
                assert result == Path(tmpdir).resolve()

    def test_falls_back_to_cwd(self) -> None:
        """Falls back to cwd when no .git found."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # No .git directory
            os.environ.pop("MYREPO_REPO_ROOT", None)
            os.environ.pop("GITHUB_WORKSPACE", None)

            with mock.patch("os.getcwd", return_value=tmpdir):
                result = get_repo_root("myrepo")
                assert result == Path(tmpdir).resolve()

    def test_no_repo_name_skips_repo_specific_var(self) -> None:
        """When repo_name is None, skips repo-specific env var check."""
        with tempfile.TemporaryDirectory() as tmpdir:
            with mock.patch.dict(os.environ, {"GITHUB_WORKSPACE": tmpdir}):
                result = get_repo_root()  # No repo name
                assert result == Path(tmpdir).resolve()


class TestLoadEnvFile:
    """Tests for load_env_file function."""

    def setup_method(self) -> None:
        """Clear cache before each test."""
        load_env_file.cache_clear()

    def test_loads_simple_env_file(self) -> None:
        """Parses simple KEY=value pairs."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".env", delete=False) as f:
            f.write("FOO=bar\n")
            f.write("BAZ=qux\n")
            f.flush()

            try:
                result = load_env_file(f.name)
                assert result == {"FOO": "bar", "BAZ": "qux"}
            finally:
                os.unlink(f.name)

    def test_strips_quotes(self) -> None:
        """Strips single and double quotes from values."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".env", delete=False) as f:
            f.write('DOUBLE="quoted value"\n')
            f.write("SINGLE='also quoted'\n")
            f.flush()

            try:
                load_env_file.cache_clear()
                result = load_env_file(f.name)
                assert result == {"DOUBLE": "quoted value", "SINGLE": "also quoted"}
            finally:
                os.unlink(f.name)

    def test_ignores_comments_and_blanks(self) -> None:
        """Skips comment lines and blank lines."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".env", delete=False) as f:
            f.write("# This is a comment\n")
            f.write("\n")
            f.write("VALID=value\n")
            f.write("   # Indented comment\n")
            f.flush()

            try:
                load_env_file.cache_clear()
                result = load_env_file(f.name)
                assert result == {"VALID": "value"}
            finally:
                os.unlink(f.name)

    def test_returns_empty_for_missing_file(self) -> None:
        """Returns empty dict when file doesn't exist."""
        result = load_env_file("/nonexistent/path/.env")
        assert result == {}

    def test_caches_result(self) -> None:
        """Subsequent calls with same path return cached result."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".env", delete=False) as f:
            f.write("KEY=value1\n")
            f.flush()

            try:
                load_env_file.cache_clear()
                result1 = load_env_file(f.name)

                # Modify the file
                with open(f.name, "w") as f2:
                    f2.write("KEY=value2\n")

                # Should still get cached value
                result2 = load_env_file(f.name)
                assert result1 == result2 == {"KEY": "value1"}
            finally:
                os.unlink(f.name)
