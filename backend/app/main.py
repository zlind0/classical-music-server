from fastapi import FastAPI
from app.core.config import settings
from app.api.music import router as music_router
from app.db.session import engine, Base
from sqlalchemy import text

app = FastAPI(title=settings.PROJECT_NAME)

@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        # Enable pgvector extension if not exists
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        # Create tables
        await conn.run_sync(Base.metadata.create_all)

app.include_router(music_router, prefix="/api/music", tags=["music"])

@app.get("/")
async def root():
    return {"message": "Welcome to Classical Music Player API"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
