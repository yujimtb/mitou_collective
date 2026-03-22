from __future__ import annotations

import asyncio
import json
import logging
from collections.abc import Awaitable, Callable, Sequence
from dataclasses import dataclass

from app.agent.candidate_search import CandidateRecord
from app.agent.config import LinkingAgentConfig
from app.agent.context_collector import ClaimContextSnapshot, ConceptContextSnapshot
from app.agent.llm_client import LLMResponse as ClientLLMResponse
from app.agent.prompts import build_claim_prompt, build_concept_prompt
from app.schemas import ConnectionType

LLMResponse = str | dict[str, object] | list[dict[str, object]] | ClientLLMResponse
LLMCallable = Callable[[str], Awaitable[LLMResponse]]
SleepCallable = Callable[[float], Awaitable[None]]


class LLMInvocationError(RuntimeError):
    pass


@dataclass(slots=True)
class GeneratedConnectionCandidate:
    source_entity_type: str
    source_entity_id: str
    target_entity_type: str
    target_entity_id: str
    connection_type: ConnectionType
    rationale: str
    confidence: float
    caveats: list[str]


class CandidateGenerator:
    def __init__(
        self,
        *,
        llm_client: LLMCallable,
        config: LinkingAgentConfig | None = None,
        sleep: SleepCallable = asyncio.sleep,
        logger: logging.Logger | None = None,
    ):
        self._llm_client = llm_client
        self._config = config or LinkingAgentConfig()
        self._sleep = sleep
        self._logger = logger or logging.getLogger(__name__)

    async def generate_for_claim(
        self,
        snapshot: ClaimContextSnapshot,
        candidates: Sequence[CandidateRecord],
    ) -> list[GeneratedConnectionCandidate]:
        if not candidates:
            return []
        response = await self._invoke_with_retries(build_claim_prompt(snapshot, list(candidates)))
        return self._parse_candidates(
            response,
            source_entity_type="claim",
            source_entity_id=snapshot.claim.id,
            target_entity_type="claim",
        )

    async def generate_for_concept(
        self,
        snapshot: ConceptContextSnapshot,
        candidates: Sequence[CandidateRecord],
    ) -> list[GeneratedConnectionCandidate]:
        if not candidates:
            return []
        response = await self._invoke_with_retries(build_concept_prompt(snapshot, list(candidates)))
        return self._parse_candidates(
            response,
            source_entity_type="concept",
            source_entity_id=snapshot.concept.id,
            target_entity_type="concept",
        )

    async def _invoke_with_retries(self, prompt: str) -> LLMResponse:
        attempts = self._config.retry_policy.max_attempts
        for attempt in range(1, attempts + 1):
            try:
                return await self._llm_client(prompt)
            except Exception as exc:
                self._logger.warning(
                    "linking-agent llm call failed on attempt %s/%s",
                    attempt,
                    attempts,
                    exc_info=exc,
                )
                if attempt == attempts:
                    raise LLMInvocationError("linking-agent llm call failed after retries") from exc
                delay = self._config.retry_policy.base_delay_seconds * (
                    self._config.retry_policy.backoff_factor ** (attempt - 1)
                )
                await self._sleep(delay)

        raise LLMInvocationError("linking-agent llm call failed")

    def _parse_candidates(
        self,
        response: LLMResponse,
        *,
        source_entity_type: str,
        source_entity_id: str,
        target_entity_type: str,
    ) -> list[GeneratedConnectionCandidate]:
        records = self._normalize_response(response)
        parsed: list[GeneratedConnectionCandidate] = []
        target_key = "target_claim_id" if target_entity_type == "claim" else "target_concept_id"
        fallback_key = "claim_id" if target_entity_type == "claim" else "concept_id"

        for record in records:
            raw_target_id = record.get(target_key) or record.get(fallback_key)
            if not raw_target_id:
                continue
            rationale = str(record.get("rationale", "")).strip()
            if not rationale:
                continue
            try:
                connection_type = ConnectionType(str(record["connection_type"]))
                confidence = min(1.0, max(0.0, float(record["confidence"])))
            except (KeyError, ValueError, TypeError):
                continue

            caveats = record.get("caveats", [])
            if isinstance(caveats, str):
                caveat_list = [caveats]
            elif isinstance(caveats, list):
                caveat_list = [str(item) for item in caveats]
            else:
                caveat_list = []

            parsed.append(
                GeneratedConnectionCandidate(
                    source_entity_type=source_entity_type,
                    source_entity_id=source_entity_id,
                    target_entity_type=target_entity_type,
                    target_entity_id=str(raw_target_id),
                    connection_type=connection_type,
                    rationale=rationale,
                    confidence=confidence,
                    caveats=caveat_list,
                )
            )
        return parsed

    @staticmethod
    def _normalize_response(response: LLMResponse) -> list[dict[str, object]]:
        if isinstance(response, ClientLLMResponse):
            parsed = json.loads(response.content)
        elif isinstance(response, str):
            parsed = json.loads(response)
        else:
            parsed = response

        if isinstance(parsed, dict):
            candidates = parsed.get("candidates", [])
        else:
            candidates = parsed

        if not isinstance(candidates, list):
            raise LLMInvocationError("linking-agent llm returned an unsupported payload")

        return [candidate for candidate in candidates if isinstance(candidate, dict)]
