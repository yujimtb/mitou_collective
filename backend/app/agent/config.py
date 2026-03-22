from __future__ import annotations

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
