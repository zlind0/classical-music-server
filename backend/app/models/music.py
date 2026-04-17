import uuid
from sqlalchemy import Column, String, Integer, Boolean, ForeignKey, Text, Table
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship, Mapped, mapped_column
from pgvector.sqlalchemy import Vector
from app.db.session import Base

class AudioFile(Base):
    __tablename__ = "audio_files"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    path: Mapped[str] = mapped_column(String, unique=True, index=True)
    format: Mapped[str] = mapped_column(String)
    size_bytes: Mapped[int] = mapped_column(Integer)
    duration_ms: Mapped[int] = mapped_column(Integer)
    
    segments = relationship("AudioSegment", back_populates="audio_file")

class AudioSegment(Base):
    __tablename__ = "audio_segments"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    file_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("audio_files.id"))
    movement_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("movements.id"), nullable=True)
    start_time_ms: Mapped[int] = mapped_column(Integer, default=0)
    end_time_ms: Mapped[int] = mapped_column(Integer, nullable=True)
    is_virtual: Mapped[bool] = mapped_column(Boolean, default=False)
    
    audio_file = relationship("AudioFile", back_populates="segments")
    movement = relationship("Movement", back_populates="audio_segments")

class Movement(Base):
    __tablename__ = "movements"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    work_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("works.id"))
    movement_number: Mapped[int] = mapped_column(Integer)
    title: Mapped[str] = mapped_column(Text)
    embedding = mapped_column(Vector(1536))
    
    work = relationship("Work", back_populates="movements")
    audio_segments = relationship("AudioSegment", back_populates="movement")

class Work(Base):
    __tablename__ = "works"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    composer: Mapped[str] = mapped_column(Text, index=True)
    era: Mapped[str] = mapped_column(Text)
    work_type: Mapped[str] = mapped_column(Text)
    catalog_number: Mapped[str] = mapped_column(Text)
    title: Mapped[str] = mapped_column(Text)
    movement_count: Mapped[int] = mapped_column(Integer)
    canonical_string: Mapped[str] = mapped_column(Text)
    summary: Mapped[str] = mapped_column(Text, nullable=True)
    
    movements = relationship("Movement", back_populates="work")
    versions = relationship("Version", back_populates="work")

class Version(Base):
    __tablename__ = "versions"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    work_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("works.id"))
    conductor: Mapped[str] = mapped_column(Text, nullable=True)
    ensemble: Mapped[str] = mapped_column(Text, nullable=True)
    year: Mapped[int] = mapped_column(Integer, nullable=True)
    label: Mapped[str] = mapped_column(Text, nullable=True)
    
    work = relationship("Work", back_populates="versions")
