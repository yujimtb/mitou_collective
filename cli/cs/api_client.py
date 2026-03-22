from __future__ import annotations

from collections.abc import Callable, Mapping
from typing import Any, cast

import httpx

from cs.config import load_config, resolve_api_url


class APIClientError(RuntimeError):
    def __init__(
        self,
        message: str,
        *,
        status_code: int | None = None,
        code: str | None = None,
        details: dict[str, Any] | None = None,
    ):
        super().__init__(message)
        self.status_code = status_code
        self.code = code
        self.details = details or {}


class APIClient:
    def __init__(
        self,
        *,
        api_url: str,
        token: str | None = None,
        transport: httpx.BaseTransport | None = None,
        timeout: float = 10.0,
    ):
        headers = {"Accept": "application/json"}
        if token:
            headers["Authorization"] = f"Bearer {token}"
        self._client = httpx.Client(
            base_url=api_url.rstrip("/"),
            headers=headers,
            transport=transport,
            timeout=timeout,
        )

    def close(self) -> None:
        self._client.close()

    def request(
        self,
        method: str,
        path: str,
        *,
        params: Mapping[str, Any] | None = None,
        json_body: dict[str, Any] | None = None,
    ) -> Any:
        response = self._client.request(
            method,
            path,
            params={
                key: value for key, value in (params or {}).items() if value is not None
            },
            json=json_body,
        )
        if response.is_error:
            raise self._to_error(response)
        if response.status_code == 204 or not response.content:
            return None
        return response.json()

    def get(self, path: str, *, params: Mapping[str, Any] | None = None) -> Any:
        return self.request("GET", path, params=params)

    def post(self, path: str, *, json_body: dict[str, Any] | None = None) -> Any:
        return self.request("POST", path, json_body=json_body)

    @staticmethod
    def _to_error(response: httpx.Response) -> APIClientError:
        try:
            payload = response.json()
        except ValueError:
            return APIClientError(
                response.text or "API request failed", status_code=response.status_code
            )

        if isinstance(payload, dict) and isinstance(payload.get("error"), dict):
            error = payload["error"]
            return APIClientError(
                error.get("message", "API request failed"),
                status_code=response.status_code,
                code=error.get("code"),
                details=error.get("details")
                if isinstance(error.get("details"), dict)
                else {},
            )

        return APIClientError(str(payload), status_code=response.status_code)


ClientFactory = Callable[[str, str | None], APIClient]


def create_client_from_obj(obj: object | None) -> APIClient:
    config = load_config()
    context = obj if isinstance(obj, dict) else {}
    api_url = resolve_api_url(config, context.get("api_url_override"))
    client_factory = context.get("client_factory")
    if callable(client_factory):
        return cast(ClientFactory, client_factory)(api_url, config.token)
    return APIClient(api_url=api_url, token=config.token)
