from sqlalchemy.orm import Session
from app.db.models import *
from app.db.schemas import *

def get_cms_home(db: Session):
    return db.query(CMSHome).first()

def create_cms_home(db: Session, cms_data: CMSHomeCreate):
    print("NOT OK CMS TO OK CMS")
    db_cms = CMSHome(**cms_data.dict())
    db.add(db_cms)
    db.commit()
    db.refresh(db_cms)
    return db_cms

def update_cms_home(db: Session, cms_data: CMSHomeUpdate):
    db_cms = get_cms_home(db)
    if not db_cms:
        print("NOT OK CMS")
        return create_cms_home(db, cms_data)
    
    print("OK CMS")
    for field, value in cms_data.dict().items():
        setattr(db_cms, field, value)
    
    db.commit()
    db.refresh(db_cms)
    return db_cms