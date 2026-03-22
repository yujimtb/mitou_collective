from __future__ import annotations

import json
from pathlib import Path

import httpx
from typer.testing import CliRunner

from cs.api_client import APIClient
from cs.config import CSConfig, save_config
from cs.main import app


runner = CliRunner()


def test_proposal_list_supports_json_filters(tmp_path: Path, monkeypatch) -> None:
    _write_config(tmp_path, monkeypatch)
    seen: dict[str, str] = {}

    def handler(request: httpx.Request) -> httpx.Response:
        seen["status"] = request.url.params.get("status", "")
        seen["proposal_type"] = request.url.params.get("proposal_type", "")
        return httpx.Response(
            200,
            json={
                "total_count": 1,
                "current_page": 1,
                "per_page": 20,
                "items": [
                    {
                        "id": "proposal-1",
                        "proposal_type": "create_claim",
                        "status": "pending",
                        "proposed_by": {"name": "Alice"},
                        "created_at": "2026-03-22T00:00:00Z",
                    }
                ],
            },
        )

    result = runner.invoke(
        app,
        ["proposal", "list", "--status", "pending", "--type", "create_claim", "--json"],
        obj={"client_factory": _factory(handler)},
    )

    assert result.exit_code == 0
    assert seen == {"status": "pending", "proposal_type": "create_claim"}
    payload = json.loads(result.stdout)
    assert payload["items"][0]["id"] == "proposal-1"


def test_proposal_review_requires_comment_for_reject() -> None:
    result = runner.invoke(app, ["proposal", "review", "proposal-1", "--reject"])

    assert result.exit_code == 1
    assert "--comment is required" in result.stderr


def test_proposal_review_posts_expected_payload(tmp_path: Path, monkeypatch) -> None:
    _write_config(tmp_path, monkeypatch)
    seen: dict[str, object] = {}

    def handler(request: httpx.Request) -> httpx.Response:
        seen["path"] = request.url.path
        seen["body"] = json.loads(request.content.decode("utf-8"))
        return httpx.Response(
            200,
            json={
                "id": "review-1",
                "proposal_id": "proposal-1",
                "reviewer": {
                    "id": "actor-1",
                    "name": "Reviewer",
                    "actor_type": "human",
                    "trust_level": "reviewer",
                    "agent_model": None,
                },
                "decision": "approve",
                "comment": "Looks good",
                "confidence": 0.9,
                "created_at": "2026-03-22T00:00:00Z",
            },
        )

    result = runner.invoke(
        app,
        [
            "proposal",
            "review",
            "proposal-1",
            "--approve",
            "--comment",
            "Looks good",
            "--confidence",
            "0.9",
            "--json",
        ],
        obj={"client_factory": _factory(handler)},
    )

    assert result.exit_code == 0
    assert seen["path"] == "/api/v1/proposals/proposal-1/review"
    assert seen["body"] == {
        "decision": "approve",
        "comment": "Looks good",
        "confidence": 0.9,
    }
    payload = json.loads(result.stdout)
    assert payload["decision"] == "approve"


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
