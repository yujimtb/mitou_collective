from __future__ import annotations

import os
from dataclasses import dataclass, field


@dataclass(slots=True)
class RetryPolicy:
    max_attempts: int = 3
    base_delay_seconds: float = 0.1
    backoff_factor: float = 2.0


@dataclass(slots=True)
class LinkingAgentConfig:
    max_candidates: int = 20
    search_pool_size: int = 100
    suggestion_confidence_threshold: float = 0.3
    duplicate_check_page_size: int = 100
    retry_policy: RetryPolicy = field(default_factory=RetryPolicy)


@dataclass(slots=True)
class LLMConfig:
    provider: str = "openai"
    model: str = "gpt-4o"
    api_key: str = ""
    temperature: float = 0.3
    max_tokens: int = 4096
    timeout_seconds: float = 60.0

    @classmethod
    def from_env(cls) -> "LLMConfig":
        provider = os.getenv("LLM_PROVIDER", "openai").strip().lower() or "openai"
        model = os.getenv("LLM_MODEL", "").strip() or cls.default_model(provider)
        api_key = cls._resolve_api_key(provider)
        temperature = float(os.getenv("LLM_TEMPERATURE", "0.3"))
        max_tokens = int(os.getenv("LLM_MAX_TOKENS", "4096"))
        timeout_seconds = float(os.getenv("LLM_TIMEOUT_SECONDS", "60.0"))
        return cls(
            provider=provider,
            model=model,
            api_key=api_key,
            temperature=temperature,
            max_tokens=max_tokens,
            timeout_seconds=timeout_seconds,
        )

    @staticmethod
    def default_model(provider: str) -> str:
        normalized = provider.strip().lower()
        if normalized == "anthropic":
            return "claude-sonnet-4-20250514"
        return "gpt-4o"

    @staticmethod
    def _resolve_api_key(provider: str) -> str:
        normalized = provider.strip().lower()
        if normalized == "anthropic":
            return os.getenv("ANTHROPIC_API_KEY", "").strip()
        return os.getenv("OPENAI_API_KEY", "").strip()
