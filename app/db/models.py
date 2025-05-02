from app.db.db_setup import Base
from sqlalchemy import (
    Float, Column, ForeignKey, Integer, String, DateTime, func, Boolean, Enum, JSON, Text
)


class TimestampMixin:
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

class CMSHome(TimestampMixin, Base):
    __tablename__ = "cms_home"
    
    id = Column(Integer, primary_key=True, index=True)
    heroTitle = Column(String(255))
    mediaItems = Column(JSON)
    brands = Column(JSON)
    priceRanges = Column(JSON)
    bodyTypes = Column(JSON)
    categories = Column(JSON)
    fairTitle = Column(String(255))
    fairDescription = Column(Text)
    fairImage = Column(String(255), nullable=True)
    sliderText = Column(Text)
    dealTitle = Column(String(255))
    dealDescription = Column(Text)
    dealImage = Column(String(255), nullable=True)