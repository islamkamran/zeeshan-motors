from pydantic import BaseModel
from typing import Optional, List, Dict

class CMSHomeBase(BaseModel):
    heroTitle: str
    mediaItems: List[Dict]
    brands: List[Dict]
    priceRanges: List[Dict]
    bodyTypes: List[Dict]
    categories: List[Dict]
    fairTitle: str
    fairDescription: str
    fairImage: Optional[str] = None
    sliderText: str
    dealTitle: str
    dealDescription: str
    dealImage: Optional[str] = None

class CMSHomeCreate(CMSHomeBase):
    pass

class CMSHomeUpdate(CMSHomeBase):
    pass

class CMSHomeResponse(CMSHomeBase):
    id: int
    
    class Config:
        from_attributes = True