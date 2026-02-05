from sqlalchemy import Column, Integer, String, DateTime
from .base import Base


class Video(Base):
    __tablename__ = 'videos'

    id = Column(String, primary_key=True)
    video_created_at = Column(DateTime)
    views_count = Column(Integer)
    likes_count = Column(Integer)
    reports_count = Column(Integer)
    comments_count = Column(Integer)
    creator_id = Column(String)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
