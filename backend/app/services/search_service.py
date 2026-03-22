from __future__ import annotations

from sqlalchemy import or_, select

from app.interfaces import ISearchService
from app.models import Claim, Concept, Context, Evidence, Term
from app.schemas import SearchQuery, SearchResult, SearchResultItem
from app.services._shared import SessionFactory


class SearchService(ISearchService):
    def __init__(self, session_factory: SessionFactory):
        self._session_factory = session_factory

    async def search(self, query: SearchQuery) -> SearchResult:
        pattern = f"%{query.q}%"
        scopes = {query.scope} if query.scope else {"claims", "concepts", "terms", "contexts", "evidence"}
        items: list[SearchResultItem] = []

        with self._session_factory() as session:
            if "claims" in scopes:
                records = session.scalars(select(Claim).where(Claim.statement.ilike(pattern)).limit(query.per_page)).all()
                items.extend(SearchResultItem(entity_type="claim", entity_id=str(record.id), title=record.statement[:80], snippet=record.statement, score=1.0) for record in records)
            if "concepts" in scopes:
                records = session.scalars(select(Concept).where(or_(Concept.label.ilike(pattern), Concept.description.ilike(pattern))).limit(query.per_page)).all()
                items.extend(SearchResultItem(entity_type="concept", entity_id=str(record.id), title=record.label, snippet=record.description, score=0.95) for record in records)
            if "terms" in scopes:
                records = session.scalars(select(Term).where(Term.surface_form.ilike(pattern)).limit(query.per_page)).all()
                items.extend(SearchResultItem(entity_type="term", entity_id=str(record.id), title=record.surface_form, snippet=record.field_hint, score=0.9) for record in records)
            if "contexts" in scopes:
                records = session.scalars(select(Context).where(or_(Context.name.ilike(pattern), Context.description.ilike(pattern))).limit(query.per_page)).all()
                items.extend(SearchResultItem(entity_type="context", entity_id=str(record.id), title=record.name, snippet=record.description, score=0.88) for record in records)
            if "evidence" in scopes:
                records = session.scalars(select(Evidence).where(or_(Evidence.title.ilike(pattern), Evidence.source.ilike(pattern), Evidence.excerpt.ilike(pattern))).limit(query.per_page)).all()
                items.extend(SearchResultItem(entity_type="evidence", entity_id=str(record.id), title=record.title, snippet=record.excerpt or record.source, score=0.86) for record in records)

        sorted_items = sorted(items, key=lambda item: item.score, reverse=True)
        start_index = (query.page - 1) * query.per_page
        end_index = start_index + query.per_page
        return SearchResult(total_count=len(sorted_items), items=sorted_items[start_index:end_index])
