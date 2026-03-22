from __future__ import annotations

import json
from pathlib import Path

import httpx
from typer.testing import CliRunner

from cs.api_client import APIClient
from cs.config import CSConfig, save_config
from cs.main import app


runner = CliRunner()


def test_agent_suggest_posts_expected_payload(tmp_path: Path, monkeypatch) -> None:
    _write_config(tmp_path, monkeypatch)
    seen: dict[str, object] = {}

    def handler(request: httpx.Request) -> httpx.Response:
        seen["path"] = request.url.path
        seen["body"] = json.loads(request.content.decode("utf-8"))
        return httpx.Response(202, json={"job_id": "job-123", "status": "queued"})

    result = runner.invoke(
        app,
        [
            "agent",
            "suggest",
            "--concept",
            "concept-1",
            "--target-field",
            "physics",
            "--json",
        ],
        obj={"client_factory": _factory(handler)},
    )

    assert result.exit_code == 0
    assert seen["path"] == "/api/v1/agent/suggest-connections"
    assert seen["body"] == {
        "source_entity_type": "concept",
        "source_entity_id": "concept-1",
        "target_field": "physics",
    }
    payload = json.loads(result.stdout)
    assert payload["job_id"] == "job-123"


def test_agent_suggestions_support_json_filters(tmp_path: Path, monkeypatch) -> None:
    _write_config(tmp_path, monkeypatch)
    seen: dict[str, str] = {}

    def handler(request: httpx.Request) -> httpx.Response:
        seen["status"] = request.url.params.get("status", "")
        seen["min_confidence"] = request.url.params.get("min_confidence", "")
        return httpx.Response(
            200,
            json={
                "total_count": 1,
                "current_page": 1,
                "per_page": 20,
                "items": [
                    {
                        "id": "proposal-9",
                        "status": "pending",
                        "proposal_type": "connect_concepts",
                        "payload": {"confidence": 0.87},
                        "rationale": "High semantic overlap",
                    }
                ],
            },
        )

    result = runner.invoke(
        app,
        [
            "agent",
            "suggestions",
            "--status",
            "pending",
            "--min-confidence",
            "0.8",
            "--json",
        ],
        obj={"client_factory": _factory(handler)},
    )

    assert result.exit_code == 0
    assert seen == {"status": "pending", "min_confidence": "0.8"}
    payload = json.loads(result.stdout)
    assert payload["items"][0]["payload"]["confidence"] == 0.87


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
