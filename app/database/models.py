import enum

from pgvector.sqlalchemy import Vector
from sqlalchemy import Enum, Integer, String, DateTime, ForeignKey
from sqlalchemy.sql.schema import Column
from app.database.connection import Base, engine

class VideoStatus(enum.Enum):
    PENDING = 'pending'
    INDEXING = 'indexing'
    COMPLETED = 'completed'
    FAILED = 'failed'


class Video(Base):
    __tablename__ = 'videos'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=False)
    path = Column(String, nullable=False)
    status = Column(Enum(VideoStatus, name='video_status'), nullable=False, default=VideoStatus.PENDING)
    created_at = Column(DateTime, nullable=False, default='now()')


class Embedding(Base):
    __tablename__ = 'embeddings'

    id = Column(Integer, primary_key=True, index=True)
    video_id = Column(Integer, ForeignKey('videos.id'), nullable=False)
    frame = Column(Integer, nullable=False)
    embedding = Column(Vector(1000), nullable=False)
    created_at = Column(DateTime, nullable=False, default='now()')


Base.metadata.create_all(bind=engine)
