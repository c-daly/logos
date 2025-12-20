"""Tests for logos_test_utils env helpers."""

from __future__ import annotations

from logos_test_utils.env import load_stack_env


def test_load_stack_env_strips_quotes(tmp_path) -> None:
    env_file = tmp_path / ".env.test"
    env_file.write_text(
        "\n".join(
            [
                "FOO=\"bar\"",
                "BAZ='qux'",
                "RAW=value",
                "# comment",
            ]
        )
        + "\n"
    )
    values = load_stack_env(env_file)
    assert values["FOO"] == "bar"
    assert values["BAZ"] == "qux"
    assert values["RAW"] == "value"
