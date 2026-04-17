from typing import List, Optional
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import or_
from pgvector.sqlalchemy import Vector
from app.models.music import Movement, Work, AudioSegment, AudioFile
from app.services.llm_service import llm_service

class SearchService:
    async def semantic_search(self, db: AsyncSession, query: str, limit: int = 10) -> List[Movement]:
        """Performs semantic search using pgvector."""
        query_embedding = await llm_service.get_embedding(query)
        
        # pgvector similarity search
        # <=> is cosine distance, <-> is Euclidean distance
        stmt = select(Movement).order_by(
            Movement.embedding.cosine_distance(query_embedding)
        ).limit(limit)
        
        result = await db.execute(stmt)
        return result.scalars().all()

    async def precise_search(
        self, 
        db: AsyncSession, 
        composer: Optional[str] = None,
        era: Optional[str] = None,
        work_type: Optional[str] = None,
        limit: int = 50
    ) -> List[Work]:
        """Filters works by specific fields."""
        stmt = select(Work)
        if composer:
            stmt = stmt.filter(Work.composer.ilike(f"%{composer}%"))
        if era:
            stmt = stmt.filter(Work.era == era)
        if work_type:
            stmt = stmt.filter(Work.work_type == work_type)
        
        stmt = stmt.limit(limit)
        result = await db.execute(stmt)
        return result.scalars().all()

    async def recommend_similar(self, db: AsyncSession, movement_id: str, limit: int = 5) -> List[Movement]:
        """Recommends similar movements based on embedding distance."""
        # 1. Get current movement embedding
        stmt = select(Movement).filter(Movement.id == movement_id)
        result = await db.execute(stmt)
        current_mov = result.scalars().first()
        
        if not current_mov:
            return []

        # 2. Find closest embeddings
        stmt = select(Movement).filter(Movement.id != movement_id).order_by(
            Movement.embedding.cosine_distance(current_mov.embedding)
        ).limit(limit)
        
        result = await db.execute(stmt)
        return result.scalars().all()

    async def get_work_details(self, db: AsyncSession, work_id: str):
        """Returns work with its movements and segments."""
        stmt = select(Work).filter(Work.id == work_id)
        result = await db.execute(stmt)
        work = result.scalars().first()
        return work

search_service = SearchService()
