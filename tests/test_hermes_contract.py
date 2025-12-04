"""Regression tests for the Hermes OpenAPI contract."""

from __future__ import annotations

from pathlib import Path
from typing import Any, cast

import yaml


def _load_hermes_contract() -> dict[str, Any]:
    contract_path = Path(__file__).resolve().parent.parent / "contracts" / "hermes.openapi.yaml"
    return cast(dict[str, Any], yaml.safe_load(contract_path.read_text(encoding="utf-8")))


def test_llm_endpoint_is_documented() -> None:
    spec = _load_hermes_contract()
    paths = spec.get("paths", {})

    assert "/llm" in paths, "Hermes contract must expose the /llm gateway"

    llm_post = paths["/llm"].get("post")
    assert llm_post, "POST /llm definition missing"

    request_schema = (
        llm_post.get("requestBody", {}).get("content", {}).get("application/json", {}).get("schema")
    )
    assert request_schema == {
        "$ref": "#/components/schemas/LLMRequest"
    }, "LLM request must reuse the canonical schema"

    success_response = (
        llm_post.get("responses", {})
        .get("200", {})
        .get("content", {})
        .get("application/json", {})
        .get("schema")
    )
    assert success_response == {
        "$ref": "#/components/schemas/LLMResponse"
    }, "LLM response must reuse the canonical schema"


def test_llm_components_exist() -> None:
    spec = _load_hermes_contract()
    schemas = spec.get("components", {}).get("schemas", {})
    for name in ("LLMRequest", "LLMResponse", "LLMMessage", "LLMChoice", "LLMUsage"):
        assert name in schemas, f"Missing {name} schema for Hermes LLM gateway"
