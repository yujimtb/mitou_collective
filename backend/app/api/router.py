from fastapi import APIRouter

from app.api.agent import router as agent_router
from app.api.claims import router as claims_router
from app.api.concepts import router as concepts_router
from app.api.contexts import router as contexts_router
from app.api.evidence import router as evidence_router
from app.api.proposals import router as proposals_router
from app.api.search import router as search_router
from app.api.terms import router as terms_router


api_router = APIRouter(prefix="/api/v1")
api_router.include_router(claims_router)
api_router.include_router(concepts_router)
api_router.include_router(contexts_router)
api_router.include_router(evidence_router)
api_router.include_router(terms_router)
api_router.include_router(proposals_router)
api_router.include_router(agent_router)
api_router.include_router(search_router)