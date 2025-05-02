from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
import json
from sqlalchemy.orm import Session
from app.db.db_setup import get_db
from app.db.schemas import *
from app.db.crud import *
import os

router = APIRouter()


UPLOAD_DIR = "uploads/cms"

async def save_upload_file(file: UploadFile, upload_dir: str = UPLOAD_DIR):
    try:
        # Create directory if it doesn't exist
        os.makedirs(upload_dir, exist_ok=True)
        
        # Generate safe filename
        filename = file.filename.replace(" ", "_")  # Basic sanitization
        file_path = os.path.join(upload_dir, filename)
        
        # Save the file
        with open(file_path, "wb") as buffer:
            buffer.write(await file.read())
        
        return f"cms/{filename}"  # Return relative path
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"File upload failed: {str(e)}")


@router.put("/v1/cms", response_model=CMSHomeResponse)
async def update_home_cms(
    heroTitle: str = Form(...),
    mediaItems: str = Form(...),
    brands: str = Form(...),
    priceRanges: str = Form(...),
    bodyTypes: str = Form(...),
    categories: str = Form(...),
    fairTitle: str = Form(...),
    fairDescription: str = Form(...),
    fairImage: Optional[UploadFile] = File(None),
    sliderText: str = Form(...),
    dealTitle: str = Form(...),
    dealDescription: str = Form(...),
    dealImage: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db)
):
    try:
        # Parse JSON strings
        data = {
            "heroTitle": heroTitle,
            "mediaItems": json.loads(mediaItems),
            "brands": json.loads(brands),
            "priceRanges": json.loads(priceRanges),
            "bodyTypes": json.loads(bodyTypes),
            "categories": json.loads(categories),
            "fairTitle": fairTitle,
            "fairDescription": fairDescription,
            "sliderText": sliderText,
            "dealTitle": dealTitle,
            "dealDescription": dealDescription,
            "fairImage": fairImage.filename if fairImage else None,
            "dealImage": dealImage.filename if dealImage else None,
        }
        print("START OK")
        # Save files if provided (simplified example)
        if fairImage:
            data["fairImage"] = await save_upload_file(fairImage)
            print("OK")
        if dealImage:
            data["dealImage"] = await save_upload_file(dealImage)
            print("OK OK")

        return update_cms_home(db, CMSHomeCreate(**data))
    
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON data")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/v1/cms", response_model=CMSHomeResponse)
def read_home_cms(db: Session = Depends(get_db)):
    cms_data = get_cms_home(db)
    if not cms_data:
        raise HTTPException(status_code=404, detail="CMS data not found")
    return cms_data