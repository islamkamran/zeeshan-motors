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
            data["fairImage"] = await save_upload_file(fairImage, UPLOAD_DIR)
            print("OK")
        if dealImage:
            data["dealImage"] = await save_upload_file(dealImage, UPLOAD_DIR)
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



async def save_upload_file(file: UploadFile, subdir: str):
    os.makedirs(f"{UPLOAD_DIR}/{subdir}", exist_ok=True)
    filename = f"{subdir}/{file.filename}"
    filepath = f"{UPLOAD_DIR}/{filename}"
    with open(filepath, "wb") as buffer:
        buffer.write(await file.read())
    return filename


# About Us Endpoints
@router.put("/v1/about-us", response_model=CMSAboutUsResponse)
async def update_about_us_cms(
    sectionOneTitle: str = Form(...),
    sectionOneDescription: str = Form(...),
    sectionTwoTitle: str = Form(...),
    sectionTwoDescription: str = Form(...),
    sectionTwoImage: Optional[UploadFile] = File(None),
    sectionThreeTitle: str = Form(...),
    sectionThreeH1: str = Form(...),
    sectionThreeD1: str = Form(...),
    sectionThreeH2: str = Form(...),
    sectionThreeD2: str = Form(...),
    sectionThreeH3: str = Form(...),
    sectionThreeD3: str = Form(...),
    sectionFourTitle: str = Form(...),
    sectionFourDescription: str = Form(...),
    db: Session = Depends(get_db)
):
    data = {
        "sectionOneTitle": sectionOneTitle,
        "sectionOneDescription": sectionOneDescription,
        "sectionTwoTitle": sectionTwoTitle,
        "sectionTwoDescription": sectionTwoDescription,
        "sectionThreeTitle": sectionThreeTitle,
        "sectionThreeH1": sectionThreeH1,
        "sectionThreeD1": sectionThreeD1,
        "sectionThreeH2": sectionThreeH2,
        "sectionThreeD2": sectionThreeD2,
        "sectionThreeH3": sectionThreeH3,
        "sectionThreeD3": sectionThreeD3,
        "sectionFourTitle": sectionFourTitle,
        "sectionFourDescription": sectionFourDescription,
    }
    
    if sectionTwoImage:
        data["sectionTwoImage"] = await save_upload_file(sectionTwoImage, "about-us")
    
    return update_about_us(db, data)


@router.get("/v1/about-us", response_model=CMSAboutUsResponse)
def get_about_us_cms(db: Session = Depends(get_db)):
    about_us = get_about_us(db)
    if not about_us:
        raise HTTPException(status_code=404, detail="About Us content not found")
    return about_us



# Inventory Endpoints
@router.put("/v1/inventory", response_model=CMSInventoryResponse)
async def update_inventory_cms(
    title: str = Form(...),
    description: str = Form(...),
    image: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db)
):
    data = {
        "title": title,
        "description": description,
    }
    
    if image:
        data["image"] = await save_upload_file(image, "inventory")
    
    return update_inventory(db, data)

@router.get("/v1/inventory", response_model=CMSInventoryResponse)
def get_inventory_cms(db: Session = Depends(get_db)):
    inventory = get_inventory(db)
    if not inventory:
        raise HTTPException(status_code=404, detail="Inventory content not found")
    return inventory

# Product Detail Endpoints
@router.put("/v1/product-detail", response_model=CMSProductDetailResponse)
async def update_product_detail_cms(
    title: str = Form(...),
    description: str = Form(...),
    h1: str = Form(...),
    h1Description: str = Form(...),
    h2: str = Form(...),
    h2Description: str = Form(...),
    h3: str = Form(...),
    h3Description: str = Form(...),
    title2: str = Form(...),
    description2: str = Form(...),
    image: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db)
):
    data = {
        "title": title,
        "description": description,
        "h1": h1,
        "h1Description": h1Description,
        "h2": h2,
        "h2Description": h2Description,
        "h3": h3,
        "h3Description": h3Description,
        "title2": title2,
        "description2": description2,
    }
    
    if image:
        data["image"] = await save_upload_file(image, "product-detail")
    
    return update_product_detail(db, data)

@router.get("/v1/product-detail", response_model=CMSProductDetailResponse)
def get_product_detail_cms(db: Session = Depends(get_db)):
    product = get_product_detail(db)
    if not product:
        raise HTTPException(status_code=404, detail="Product detail content not found")
    return product

# Contact Endpoints
@router.put("/v1/contact", response_model=CMSContactResponse)
async def update_contact_cms(
    title: str = Form(...),
    description: str = Form(...),
    phone: str = Form(...),
    email: str = Form(...),
    location: str = Form(...),
    hours: str = Form(...),
    map_url: str = Form(...),
    db: Session = Depends(get_db)
):
    data = {
        "title": title,
        "description": description,
        "phone": phone,
        "email": email,
        "location": location,
        "hours": hours,
        "map_url": map_url,
    }
    return update_contact(db, data)

@router.get("/v1/contact", response_model=CMSContactResponse)
def get_contact_cms(db: Session = Depends(get_db)):
    contact = get_contact(db)
    if not contact:
        raise HTTPException(status_code=404, detail="Contact content not found")
    return contact