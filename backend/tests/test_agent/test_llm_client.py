from __future__ import annotations

import asyncio
import sys
import types
from types import SimpleNamespace

import pytest

from app.agent.config import LLMConfig
from app.agent.llm_client import (
    AnthropicAdapter,
    OpenAIAdapter,
    SYSTEM_PROMPT,
    create_llm_client,
)


def _install_module(monkeypatch: pytest.MonkeyPatch, name: str, module: types.ModuleType) -> None:
    monkeypatch.setitem(sys.modules, name, module)


def test_openai_adapter_returns_normalized_response(monkeypatch: pytest.MonkeyPatch) -> None:
    captured: dict[str, object] = {}

    class FakeCompletions:
        async def create(self, **kwargs):
            captured.update(kwargs)
            return SimpleNamespace(
                model="gpt-4o",
                choices=[SimpleNamespace(message=SimpleNamespace(content='{"candidates": []}'))],
                usage=SimpleNamespace(prompt_tokens=123, completion_tokens=45),
            )

    class FakeAsyncOpenAI:
        def __init__(self, *, api_key: str, timeout: float):
            captured["api_key"] = api_key
            captured["timeout"] = timeout
            self.chat = SimpleNamespace(completions=FakeCompletions())

    module = types.ModuleType("openai")
    module.AsyncOpenAI = FakeAsyncOpenAI
    _install_module(monkeypatch, "openai", module)

    adapter = OpenAIAdapter(
        LLMConfig(api_key="openai-key", model="gpt-4o-mini", temperature=0.1, max_tokens=256)
    )
    response = asyncio.run(adapter.generate('{"prompt": "value"}'))

    assert response.content == '{"candidates": []}'
    assert response.model == "gpt-4o"
    assert response.usage.prompt_tokens == 123
    assert response.usage.completion_tokens == 45
    assert captured["api_key"] == "openai-key"
    assert captured["timeout"] == 60.0
    assert captured["model"] == "gpt-4o-mini"
    assert captured["temperature"] == 0.1
    assert captured["max_tokens"] == 256
    assert captured["messages"] == [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": '{"prompt": "value"}'},
    ]


def test_openai_adapter_surfaces_timeout(monkeypatch: pytest.MonkeyPatch) -> None:
    class FakeCompletions:
        async def create(self, **kwargs):
            raise TimeoutError("request timed out")

    class FakeAsyncOpenAI:
        def __init__(self, *, api_key: str, timeout: float):
            self.chat = SimpleNamespace(completions=FakeCompletions())

    module = types.ModuleType("openai")
    module.AsyncOpenAI = FakeAsyncOpenAI
    _install_module(monkeypatch, "openai", module)

    adapter = OpenAIAdapter(LLMConfig(api_key="openai-key"))

    with pytest.raises(TimeoutError, match="request timed out"):
        asyncio.run(adapter.generate("prompt"))


def test_openai_adapter_surfaces_authentication_error(monkeypatch: pytest.MonkeyPatch) -> None:
    class OpenAIAuthenticationError(Exception):
        pass

    class FakeCompletions:
        async def create(self, **kwargs):
            raise OpenAIAuthenticationError("401 unauthorized")

    class FakeAsyncOpenAI:
        def __init__(self, *, api_key: str, timeout: float):
            self.chat = SimpleNamespace(completions=FakeCompletions())

    module = types.ModuleType("openai")
    module.AsyncOpenAI = FakeAsyncOpenAI
    module.AuthenticationError = OpenAIAuthenticationError
    _install_module(monkeypatch, "openai", module)

    adapter = OpenAIAdapter(LLMConfig(api_key="openai-key"))

    with pytest.raises(OpenAIAuthenticationError, match="401 unauthorized"):
        asyncio.run(adapter.generate("prompt"))


def test_anthropic_adapter_returns_normalized_response(monkeypatch: pytest.MonkeyPatch) -> None:
    captured: dict[str, object] = {}

    class FakeMessages:
        async def create(self, **kwargs):
            captured.update(kwargs)
            return SimpleNamespace(
                model="claude-sonnet",
                content=[SimpleNamespace(type="text", text='{"candidates": []}')],
                usage=SimpleNamespace(input_tokens=88, output_tokens=21),
            )

    class FakeAsyncAnthropic:
        def __init__(self, *, api_key: str, timeout: float):
            captured["api_key"] = api_key
            captured["timeout"] = timeout
            self.messages = FakeMessages()

    module = types.ModuleType("anthropic")
    module.AsyncAnthropic = FakeAsyncAnthropic
    _install_module(monkeypatch, "anthropic", module)

    adapter = AnthropicAdapter(
        LLMConfig(
            provider="anthropic",
            api_key="anthropic-key",
            model="claude-sonnet-4-20250514",
            temperature=0.2,
            max_tokens=512,
            timeout_seconds=12.5,
        )
    )
    response = asyncio.run(adapter.generate('{"prompt": "value"}'))

    assert response.content == '{"candidates": []}'
    assert response.model == "claude-sonnet"
    assert response.usage.prompt_tokens == 88
    assert response.usage.completion_tokens == 21
    assert captured["api_key"] == "anthropic-key"
    assert captured["timeout"] == 12.5
    assert captured["model"] == "claude-sonnet-4-20250514"
    assert captured["system"] == SYSTEM_PROMPT
    assert captured["messages"] == [{"role": "user", "content": '{"prompt": "value"}'}]


def test_create_llm_client_selects_provider(monkeypatch: pytest.MonkeyPatch) -> None:
    openai_module = types.ModuleType("openai")
    anthropic_module = types.ModuleType("anthropic")

    class FakeAsyncOpenAI:
        def __init__(self, *, api_key: str, timeout: float):
            self.chat = SimpleNamespace(completions=SimpleNamespace(create=None))

    class FakeAsyncAnthropic:
        def __init__(self, *, api_key: str, timeout: float):
            self.messages = SimpleNamespace(create=None)

    openai_module.AsyncOpenAI = FakeAsyncOpenAI
    anthropic_module.AsyncAnthropic = FakeAsyncAnthropic
    _install_module(monkeypatch, "openai", openai_module)
    _install_module(monkeypatch, "anthropic", anthropic_module)

    assert isinstance(create_llm_client(LLMConfig(provider="openai", api_key="key")), OpenAIAdapter)
    assert isinstance(
        create_llm_client(LLMConfig(provider="anthropic", api_key="key")),
        AnthropicAdapter,
    )
    with pytest.raises(ValueError, match="Unsupported LLM provider"):
        create_llm_client(LLMConfig(provider="unknown", api_key="key"))


def test_llm_config_from_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("LLM_PROVIDER", "anthropic")
    monkeypatch.setenv("LLM_MODEL", "claude-3.7")
    monkeypatch.setenv("ANTHROPIC_API_KEY", "anthropic-key")
    monkeypatch.setenv("LLM_TEMPERATURE", "0.15")
    monkeypatch.setenv("LLM_MAX_TOKENS", "2048")
    monkeypatch.setenv("LLM_TIMEOUT_SECONDS", "42.5")

    config = LLMConfig.from_env()

    assert config.provider == "anthropic"
    assert config.model == "claude-3.7"
    assert config.api_key == "anthropic-key"
    assert config.temperature == 0.15
    assert config.max_tokens == 2048
    assert config.timeout_seconds == 42.5


def test_llm_config_from_env_defaults(monkeypatch: pytest.MonkeyPatch) -> None:
    for name in (
        "LLM_PROVIDER",
        "LLM_MODEL",
        "OPENAI_API_KEY",
        "ANTHROPIC_API_KEY",
        "LLM_TEMPERATURE",
        "LLM_MAX_TOKENS",
        "LLM_TIMEOUT_SECONDS",
    ):
        monkeypatch.delenv(name, raising=False)

    config = LLMConfig.from_env()

    assert config.provider == "openai"
    assert config.model == "gpt-4o"
    assert config.api_key == ""
    assert config.temperature == 0.3
    assert config.max_tokens == 4096
    assert config.timeout_seconds == 60.0
