from __future__ import annotations

import asyncio

from app.agent import (
    CandidateGenerator,
    CandidateRecord,
    ClaimContextSnapshot,
    LinkingAgentConfig,
    RetryPolicy,
)

from ._fakes import make_claim, make_concept


def test_candidate_generator_retries_and_parses_json() -> None:
    attempts: list[int] = []
    sleeps: list[float] = []

    async def llm_client(prompt: str):
        attempts.append(len(prompt))
        if len(attempts) < 3:
            raise TimeoutError("timeout")
        return '[{"target_claim_id": "claim-2", "connection_type": "analogous", "rationale": "Both claims use entropy as a state descriptor.", "confidence": 0.74, "caveats": ["Contexts differ."]}]'

    async def fake_sleep(delay: float) -> None:
        sleeps.append(delay)

    generator = CandidateGenerator(
        llm_client=llm_client,
        config=LinkingAgentConfig(
            retry_policy=RetryPolicy(max_attempts=3, base_delay_seconds=0.2, backoff_factor=2.0)
        ),
        sleep=fake_sleep,
    )
    snapshot = ClaimContextSnapshot(
        claim=make_claim(
            "claim-1", statement="Entropy increases in isolated systems.", concept_ids=["concept-1"]
        ),
        concepts=[
            make_concept(
                "concept-1",
                label="Entropy",
                description="Thermodynamic entropy.",
                field="thermodynamics",
            )
        ],
        contexts=[],
        evidence=[],
        adjacent_claims=[],
        source_field="thermodynamics",
    )
    candidates = [
        CandidateRecord(
            entity_type="claim",
            entity_id="claim-2",
            field="information_theory",
            score=0.88,
            summary="Information entropy measures uncertainty.",
            details={"statement": "Information entropy measures uncertainty."},
        )
    ]

    generated = asyncio.run(generator.generate_for_claim(snapshot, candidates))

    assert len(attempts) == 3
    assert sleeps == [0.2, 0.4]
    assert generated[0].target_entity_id == "claim-2"
    assert generated[0].confidence == 0.74
