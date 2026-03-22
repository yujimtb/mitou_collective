from __future__ import annotations

import json
from pathlib import Path

import httpx
import pytest
from typer.testing import CliRunner

from cs.api_client import APIClient
from cs.config import CSConfig, save_config
from cs.main import app


runner = CliRunner()


@pytest.mark.parametrize(
    ("args", "expected_path", "expected_body", "response_json"),
    [
        pytest.param(
            [
                "context",
                "create",
                "--name",
                "Thermodynamics",
                "--field",
                "physics",
                "--description",
                "Study of heat and energy transfer.",
                "--assumptions",
                "Closed system",
                "--assumptions",
                "Near equilibrium",
                "--parent",
                "ctx-root",
                "--json",
            ],
            "/api/v1/contexts",
            {
                "name": "Thermodynamics",
                "field": "physics",
                "description": "Study of heat and energy transfer.",
                "assumptions": ["Closed system", "Near equilibrium"],
                "parent_context_id": "ctx-root",
            },
            {"id": "ctx-1", "name": "Thermodynamics"},
            id="context-create",
        ),
        pytest.param(
            [
                "term",
                "create",
                "--surface-form",
                "entropy",
                "--language",
                "en",
                "--field-hint",
                "physics",
                "--concept",
                "concept-1",
                "--concept",
                "concept-2",
                "--json",
            ],
            "/api/v1/terms",
            {
                "surface_form": "entropy",
                "language": "en",
                "field_hint": "physics",
                "concept_ids": ["concept-1", "concept-2"],
            },
            {"id": "term-1", "surface_form": "entropy"},
            id="term-create",
        ),
        pytest.param(
            [
                "evidence",
                "create",
                "--title",
                "Entropy paper",
                "--type",
                "paper",
                "--source",
                "https://example.test/papers/entropy",
                "--excerpt",
                "Entropy increases in isolated systems.",
                "--reliability",
                "peer_reviewed",
                "--claim",
                "claim-1",
                "--claim",
                "claim-2",
                "--json",
            ],
            "/api/v1/evidence",
            {
                "title": "Entropy paper",
                "evidence_type": "paper",
                "source": "https://example.test/papers/entropy",
                "excerpt": "Entropy increases in isolated systems.",
                "reliability": "peer_reviewed",
                "claim_links": [{"claim_id": "claim-1"}, {"claim_id": "claim-2"}],
            },
            {"id": "evidence-1", "title": "Entropy paper"},
            id="evidence-create",
        ),
        pytest.param(
            [
                "concept",
                "create",
                "--label",
                "Entropy",
                "--field",
                "physics",
                "--description",
                "A measure of disorder.",
                "--term",
                "term-1",
                "--term",
                "term-2",
                "--referent",
                "concept-root",
                "--json",
            ],
            "/api/v1/concepts",
            {
                "label": "Entropy",
                "field": "physics",
                "description": "A measure of disorder.",
                "term_ids": ["term-1", "term-2"],
                "referent_id": "concept-root",
            },
            {"id": "concept-1", "label": "Entropy"},
            id="concept-create",
        ),
    ],
)
def test_resource_create_commands_post_expected_payload(
    tmp_path: Path,
    monkeypatch,
    args: list[str],
    expected_path: str,
    expected_body: dict[str, object],
    response_json: dict[str, object],
) -> None:
    _write_config(tmp_path, monkeypatch)
    seen: dict[str, object] = {}

    def handler(request: httpx.Request) -> httpx.Response:
        seen["auth"] = request.headers.get("Authorization", "")
        seen["path"] = request.url.path
        seen["body"] = json.loads(request.content.decode("utf-8"))
        return httpx.Response(201, json=response_json)

    result = runner.invoke(app, args, obj={"client_factory": _factory(handler)})

    assert result.exit_code == 0
    assert seen["auth"] == "Bearer test-token"
    assert seen["path"] == expected_path
    assert seen["body"] == expected_body
    assert json.loads(result.stdout) == response_json


@pytest.mark.parametrize(
    ("args", "expected_path", "error_message"),
    [
        pytest.param(
            [
                "context",
                "create",
                "--name",
                "Thermodynamics",
                "--field",
                "physics",
                "--description",
                "Study of heat.",
            ],
            "/api/v1/contexts",
            "Context validation failed",
            id="context-create-error",
        ),
        pytest.param(
            [
                "term",
                "create",
                "--surface-form",
                "entropy",
                "--language",
                "en",
            ],
            "/api/v1/terms",
            "Term already exists",
            id="term-create-error",
        ),
        pytest.param(
            [
                "evidence",
                "create",
                "--title",
                "Entropy paper",
                "--type",
                "paper",
                "--source",
                "https://example.test/papers/entropy",
            ],
            "/api/v1/evidence",
            "Evidence validation failed",
            id="evidence-create-error",
        ),
        pytest.param(
            [
                "concept",
                "create",
                "--label",
                "Entropy",
                "--field",
                "physics",
                "--description",
                "A measure of disorder.",
            ],
            "/api/v1/concepts",
            "Concept validation failed",
            id="concept-create-error",
        ),
    ],
)
def test_resource_create_commands_surface_api_errors(
    tmp_path: Path,
    monkeypatch,
    args: list[str],
    expected_path: str,
    error_message: str,
) -> None:
    _write_config(tmp_path, monkeypatch)
    seen: dict[str, str] = {}

    def handler(request: httpx.Request) -> httpx.Response:
        seen["path"] = request.url.path
        return httpx.Response(
            422,
            json={
                "error": {
                    "message": error_message,
                    "code": "validation_error",
                    "details": {"field": "invalid"},
                }
            },
        )

    result = runner.invoke(app, args, obj={"client_factory": _factory(handler)})

    assert result.exit_code == 1
    assert seen["path"] == expected_path
    assert error_message in result.stderr


def _write_config(tmp_path: Path, monkeypatch) -> Path:
    config_path = tmp_path / "config.toml"
    monkeypatch.setenv("CS_CONFIG_PATH", str(config_path))
    save_config(CSConfig(api_url="http://api.test", token="test-token"), config_path)
    return config_path


def _factory(handler):
    def make_client(api_url: str, token: str | None) -> APIClient:
        return APIClient(
            api_url=api_url, token=token, transport=httpx.MockTransport(handler)
        )

    return make_client
