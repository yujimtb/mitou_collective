from __future__ import annotations

import importlib
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Any, Protocol

from app.agent.config import LLMConfig


SYSTEM_PROMPT = """You are an interdisciplinary scientific knowledge expert.
Analyze the source entity and candidate entities, then respond with JSON only.
Return an object with a "candidates" array or a bare array of candidate objects.
Each candidate must include:
- target_claim_id or target_concept_id
- connection_type
- rationale
- confidence
- caveats

Allowed connection_type values:
- equivalent
- analogous
- generalizes
- contradicts
- complements
"""


@dataclass(slots=True)
class TokenUsage:
    prompt_tokens: int
    completion_tokens: int


@dataclass(slots=True)
class LLMResponse:
    content: str
    model: str
    usage: TokenUsage


class LLMClient(Protocol):
    async def generate(self, prompt: str) -> LLMResponse: ...


class OpenAIAdapter:
    def __init__(self, config: LLMConfig):
        self._config = config
        openai = importlib.import_module("openai")
        self._client = openai.AsyncOpenAI(
            api_key=config.api_key,
            timeout=config.timeout_seconds,
        )

    async def generate(self, prompt: str) -> LLMResponse:
        response = await self._client.chat.completions.create(
            model=self._config.model,
            temperature=self._config.temperature,
            max_tokens=self._config.max_tokens,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
        )
        return LLMResponse(
            content=_extract_openai_content(response),
            model=str(getattr(response, "model", self._config.model)),
            usage=TokenUsage(
                prompt_tokens=int(
                    getattr(getattr(response, "usage", None), "prompt_tokens", 0) or 0
                ),
                completion_tokens=int(
                    getattr(getattr(response, "usage", None), "completion_tokens", 0) or 0
                ),
            ),
        )


class AnthropicAdapter:
    def __init__(self, config: LLMConfig):
        self._config = config
        anthropic = importlib.import_module("anthropic")
        self._client = anthropic.AsyncAnthropic(
            api_key=config.api_key,
            timeout=config.timeout_seconds,
        )

    async def generate(self, prompt: str) -> LLMResponse:
        response = await self._client.messages.create(
            model=self._config.model,
            system=SYSTEM_PROMPT,
            temperature=self._config.temperature,
            max_tokens=self._config.max_tokens,
            messages=[{"role": "user", "content": prompt}],
        )
        return LLMResponse(
            content=_extract_anthropic_content(getattr(response, "content", [])),
            model=str(getattr(response, "model", self._config.model)),
            usage=TokenUsage(
                prompt_tokens=int(
                    getattr(getattr(response, "usage", None), "input_tokens", 0) or 0
                ),
                completion_tokens=int(
                    getattr(getattr(response, "usage", None), "output_tokens", 0) or 0
                ),
            ),
        )


def create_llm_client(config: LLMConfig) -> LLMClient:
    provider = config.provider.strip().lower()
    if provider == "openai":
        return OpenAIAdapter(config)
    if provider == "anthropic":
        return AnthropicAdapter(config)
    raise ValueError(f"Unsupported LLM provider: {config.provider}")


def _extract_openai_content(response: Any) -> str:
    choices = getattr(response, "choices", None)
    if not choices:
        return ""
    message = getattr(choices[0], "message", None)
    content = getattr(message, "content", "")
    return _coerce_content(content)


def _extract_anthropic_content(content_blocks: Sequence[Any]) -> str:
    parts: list[str] = []
    for block in content_blocks:
        if isinstance(block, Mapping):
            if block.get("type") == "text":
                parts.append(str(block.get("text", "")))
            continue
        if getattr(block, "type", None) == "text":
            parts.append(str(getattr(block, "text", "")))
    return "".join(parts)


def _coerce_content(content: Any) -> str:
    if isinstance(content, str):
        return content
    if isinstance(content, Sequence):
        parts: list[str] = []
        for item in content:
            if isinstance(item, Mapping):
                if item.get("type") == "text":
                    parts.append(str(item.get("text", "")))
                else:
                    text = item.get("text")
                    if text is not None:
                        parts.append(str(text))
                continue
            text = getattr(item, "text", None)
            if text is not None:
                parts.append(str(text))
        return "".join(parts)
    return str(content)
