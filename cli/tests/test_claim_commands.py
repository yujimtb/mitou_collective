from __future__ import annotations

import json
from pathlib import Path

import httpx
from typer.testing import CliRunner

from cs.api_client import APIClient
from cs.config import CSConfig, load_config, save_config
from cs.main import app


runner = CliRunner()


def test_auth_login_persists_config(tmp_path: Path, monkeypatch) -> None:
    config_path = tmp_path / "config.toml"
    monkeypatch.setenv("CS_CONFIG_PATH", str(config_path))

    result = runner.invoke(
        app,
        [
            "auth",
            "login",
            "--token",
            "secret-token",
            "--api-url",
            "http://api.example.test",
        ],
    )

    assert result.exit_code == 0
    config = load_config(config_path)
    assert config.api_url == "http://api.example.test"
    assert config.token == "secret-token"


def test_claim_list_uses_filters_and_json_output(tmp_path: Path, monkeypatch) -> None:
    config_path = _write_config(tmp_path, monkeypatch)
    seen: dict[str, str] = {}

    def handler(request: httpx.Request) -> httpx.Response:
        seen["auth"] = request.headers.get("Authorization", "")
        seen["context"] = request.url.params.get("context", "")
        seen["field"] = request.url.params.get("field", "")
        return httpx.Response(
            200,
            json={
                "total_count": 1,
                "current_page": 1,
                "per_page": 20,
                "items": [
                    {
                        "id": "claim-1",
                        "statement": "Entropy increases.",
                        "claim_type": "theorem",
                        "trust_status": "established",
                        "context_ids": ["ctx-1"],
                    }
                ],
            },
        )

    result = runner.invoke(
        app,
        [
            "claim",
            "list",
            "--context",
            "Thermodynamics",
            "--field",
            "physics",
            "--json",
        ],
        obj={"client_factory": _factory(handler)},
    )

    assert result.exit_code == 0
    assert seen == {
        "auth": "Bearer test-token",
        "context": "Thermodynamics",
        "field": "physics",
    }
    payload = json.loads(result.stdout)
    assert payload["items"][0]["id"] == "claim-1"
    assert Path(config_path).exists()


def test_claim_create_posts_expected_payload(tmp_path: Path, monkeypatch) -> None:
    _write_config(tmp_path, monkeypatch)
    seen: dict[str, object] = {}

    def handler(request: httpx.Request) -> httpx.Response:
        seen["path"] = request.url.path
        seen["body"] = json.loads(request.content.decode("utf-8"))
        return httpx.Response(
            201,
            json={
                "id": "claim-9",
                "statement": "Entropy grows.",
                "claim_type": "theorem",
                "trust_status": "tentative",
                "context_ids": ["ctx-1"],
                "concept_ids": ["concept-1", "concept-2"],
                "evidence_ids": [],
                "cir": None,
                "created_at": "2026-03-22T00:00:00Z",
                "created_by": None,
                "version": 1,
            },
        )

    result = runner.invoke(
        app,
        [
            "claim",
            "create",
            "--statement",
            "Entropy grows.",
            "--type",
            "theorem",
            "--context",
            "ctx-1",
            "--concept",
            "concept-1",
            "--concept",
            "concept-2",
            "--json",
        ],
        obj={"client_factory": _factory(handler)},
    )

    assert result.exit_code == 0
    assert seen["path"] == "/api/v1/claims"
    assert seen["body"] == {
        "statement": "Entropy grows.",
        "claim_type": "theorem",
        "context_ids": ["ctx-1"],
        "concept_ids": ["concept-1", "concept-2"],
    }
    payload = json.loads(result.stdout)
    assert payload["id"] == "claim-9"


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
