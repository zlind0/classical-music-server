# Backend Implementation Plan - Classical Music Player

Implement the backend for the classical music player as specified in the `README.md`.

## Objective
Create a robust, LLM-powered music streaming and metadata management backend using FastAPI, Postgres (with pgvector), and FFmpeg.

## Key Files & Context
- `backend/`: Root directory for the backend.
- `backend/app/`: FastAPI application code.
- `backend/app/main.py`: Entry point.
- `backend/app/models/`: Database models.
- `backend/app/api/`: API endpoints.
- `backend/app/services/`: Business logic (LLM, Audio, Indexing).
- `backend/app/core/`: Configuration (env vars, constants).
- `backend/tools/`: Debugging and testing tools.
- `docker-compose.yml`: Orchestration.

## Implementation Steps

### Phase 1: Foundation
1.  **Dependencies & Config:**
    - Create `backend/requirements.txt` (FastAPI, SQLAlchemy, psycopg2-binary, pgvector, openai, pydantic-settings, mutagen, etc.).
    - Create `backend/app/core/config.py` for environment variables.
2.  **Docker Setup:**
    - Create `docker-compose.yml` with `db` (Postgres + pgvector) and `app` (FastAPI) services.
    - Create `backend/Dockerfile`.
3.  **Database Initial Setup:**
    - Create `backend/app/db/session.py` and base model.
    - Define models in `backend/app/models/` based on the schema in `README.md`.

### Phase 2: Audio Processing Service
1.  **FFmpeg Integration:**
    - Implement `backend/app/services/audio_service.py`.
    - Functions for streaming, format conversion (APE/ALAC to FLAC), and CUE splitting.
2.  **Metadata Extraction (Basic):**
    - Use `mutagen` to read ID3/Vorbis/MP4 tags.

### Phase 3: LLM Integration Service
1.  **OpenAI Client:**
    - Implement `backend/app/services/llm_service.py`.
    - Support OpenAI-compatible APIs.
2.  **Prompts & Canonical String:**
    - Develop prompts for advanced metadata extraction (era, work type, mood).
    - Implement logic to generate the `canonical_string`.
3.  **Testing Tool:**
    - Create `backend/tools/extract_metadata_debug.py` to test prompts on single files.

### Phase 4: Indexing & Search
1.  **Background Indexer:**
    - Implement `backend/app/services/indexer.py` to scan directories and update the DB.
2.  **Search Logic:**
    - Precise search (Postgres filters).
    - Semantic search (pgvector similarity).
3.  **Similarity Recommendation:**
    - Implement recommendation logic using embeddings.

### Phase 5: API Endpoints
1.  **Music API:** `/stream/{segment_id}`, `/search`, `/recommend`.
2.  **Management API:** `/scan` (trigger indexing).

## Verification & Testing
- **LLM Prompt Testing:** Use the tool in `backend/tools/` to verify LLM output quality.
- **Streaming Test:** Verify that various formats (FLAC, M4A, etc.) stream correctly via FFmpeg.
- **Search Test:** Verify that semantic search returns relevant results for natural language queries.
- **Database Schema:** Ensure `pgvector` is working and embeddings are stored/queried correctly.

## Migration & Rollback
- Use Alembic for database migrations (if needed, otherwise simple `create_all` for initial version).
- Ensure data volume for Postgres is persisted.
