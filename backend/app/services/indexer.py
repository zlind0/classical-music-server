import os
import asyncio
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.music import AudioFile, AudioSegment, Movement, Work, Version
from app.services.audio_service import audio_service
from app.services.llm_service import llm_service
from app.core.config import settings
from app.db.session import SessionLocal

class IndexerService:
    async def scan_music(self):
        """Scans the music directory and indexes all files."""
        async with SessionLocal() as db:
            for root, _, files in os.walk(settings.MUSIC_PATH):
                for file in files:
                    if file.lower().endswith(('.mp3', '.flac', '.m4a', '.ape', '.wav')):
                        file_path = os.path.join(root, file)
                        await self.index_file(db, file_path)
            await db.commit()

    async def index_file(self, db: AsyncSession, file_path: str):
        # 1. Check if file already indexed
        result = await db.execute(select(AudioFile).filter(AudioFile.path == file_path))
        if result.scalars().first():
            return

        print(f"Indexing: {file_path}")
        
        # 2. Extract basic metadata
        basic_meta = audio_service.extract_metadata(file_path)
        
        # 3. Extract advanced metadata using LLM
        adv_meta = await llm_service.extract_metadata(basic_meta, file_path)
        
        # 4. Find or Create Work
        work_query = await db.execute(
            select(Work).filter(
                Work.composer == adv_meta.get("composer"),
                Work.title == adv_meta.get("work_title")
            )
        )
        work = work_query.scalars().first()
        if not work:
            work = Work(
                composer=adv_meta.get("composer"),
                era=adv_meta.get("era"),
                work_type=adv_meta.get("work_type"),
                catalog_number=adv_meta.get("catalog"),
                title=adv_meta.get("work_title"),
                movement_count=1, # Default to 1, can be updated
                canonical_string=adv_meta.get("canonical_string"),
                summary=adv_meta.get("summary")
            )
            db.add(work)
            await db.flush()

        # 5. Create AudioFile
        audio_file = AudioFile(
            path=file_path,
            format=basic_meta.get("format"),
            size_bytes=basic_meta.get("size_bytes"),
            duration_ms=basic_meta.get("duration_ms")
        )
        db.add(audio_file)
        await db.flush()

        # 6. Create Movement
        # Try to find existing movement in this work with same number
        mov_num = adv_meta.get("movement_number", 1)
        mov_query = await db.execute(
            select(Movement).filter(
                Movement.work_id == work.id,
                Movement.movement_number == mov_num
            )
        )
        movement = mov_query.scalars().first()
        if not movement:
            # Generate embedding for the movement based on canonical string and title
            embed_text = f"{adv_meta.get('canonical_string')} {adv_meta.get('movement_title')} {adv_meta.get('summary', '')}"
            embedding = await llm_service.get_embedding(embed_text)
            
            movement = Movement(
                work_id=work.id,
                movement_number=mov_num,
                title=adv_meta.get("movement_title") or f"Movement {mov_num}",
                embedding=embedding
            )
            db.add(movement)
            await db.flush()

        # 7. Create AudioSegment
        segment = AudioSegment(
            file_id=audio_file.id,
            movement_id=movement.id,
            start_time_ms=0,
            end_time_ms=basic_meta.get("duration_ms")
        )
        db.add(segment)
        
        print(f"Finished indexing: {adv_meta.get('canonical_string')}")

indexer_service = IndexerService()
