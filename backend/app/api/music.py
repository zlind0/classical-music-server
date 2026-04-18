from fastapi import APIRouter, Depends, HTTPException, Query, Header
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
import subprocess
from typing import List, Optional
from app.db.session import get_db
from app.services.search_service import search_service
from app.services.indexer import indexer_service
from app.services.audio_service import audio_service
from app.models.music import AudioSegment, AudioFile, Movement, Work
from sqlalchemy.future import select

router = APIRouter()

@router.get("/works")
async def list_works(
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db)
):
    """List all works"""
    stmt = select(Work).limit(limit).offset(offset)
    result = await db.execute(stmt)
    works = result.scalars().all()
    return works

@router.get("/search")
async def search(
    query: Optional[str] = None,
    composer: Optional[str] = None,
    era: Optional[str] = None,
    work_type: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    if query:
        movements = await search_service.semantic_search(db, query)
        return {"type": "semantic", "results": movements}
    else:
        works = await search_service.precise_search(db, composer, era, work_type)
        return {"type": "precise", "results": works}

@router.get("/works/{work_id}")
async def get_work(work_id: str, db: AsyncSession = Depends(get_db)):
    stmt = select(Work).filter(Work.id == work_id)
    result = await db.execute(stmt)
    work = result.scalars().first()
    if not work:
        raise HTTPException(status_code=404, detail="Work not found")

    return work

@router.get("/works/{work_id}/movements")
async def get_movements(work_id: str, db: AsyncSession = Depends(get_db)):
    """Get movements for a work"""
    stmt = select(Movement).filter(Movement.work_id == work_id).order_by(Movement.movement_number)
    result = await db.execute(stmt)
    movements = result.scalars().all()

    if not movements:
        raise HTTPException(status_code=404, detail="Work not found")

    return movements

@router.get("/works/{work_id}/recommendations")
async def get_recommendations(work_id: str, db: AsyncSession = Depends(get_db)):
    """Get recommended works similar to this one"""
    # For now, return random works
    stmt = select(Work).limit(5)
    result = await db.execute(stmt)
    works = result.scalars().all()
    return works

@router.get("/recommend/{movement_id}")
async def recommend(movement_id: str, db: AsyncSession = Depends(get_db)):
    movements = await search_service.recommend_similar(db, movement_id)
    return movements

@router.post("/scan")
async def scan_library():
    # In a real app, this should be a background task
    await indexer_service.scan_music()
    return {"message": "Scan started"}

@router.get("/audio/segments/{segment_id}")
async def stream_audio(
    segment_id: str,
    target_format: str = Query("flac"),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(AudioSegment).filter(AudioSegment.id == segment_id)
    result = await db.execute(stmt)
    segment = result.scalars().first()

    if not segment:
        raise HTTPException(status_code=404, detail="Segment not found")

    stmt = select(AudioFile).filter(AudioFile.id == segment.file_id)
    result = await db.execute(stmt)
    audio_file = result.scalars().first()

    cmd = audio_service.get_stream_command(
        audio_file.path,
        start_ms=segment.start_time_ms,
        end_ms=segment.end_time_ms,
        target_format=target_format
    )

    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)

    def generate():
        while True:
            chunk = process.stdout.read(4096)
            if not chunk:
                break
            yield chunk
        process.stdout.close()
        process.wait()

    media_type = "audio/flac" if target_format == "flac" else "audio/mpeg"
    return StreamingResponse(generate(), media_type=media_type)

