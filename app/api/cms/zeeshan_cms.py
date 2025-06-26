from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
import json
from sqlalchemy.orm import Session
from app.db.db_setup import get_db
from app.db.schemas import *
from app.db.crud import *
import os
from fastapi.staticfiles import StaticFiles
from typing import List
from fastapi import Request
from urllib.parse import urljoin

router = APIRouter()


UPLOAD_DIR = "uploads"
CMS_BASE_DIR = os.path.join(UPLOAD_DIR, "cms")

async def save_upload_file_cms(file: UploadFile, subdir: str) -> str:
    """Save uploaded file and return relative URL path"""
    print("here 1")
    upload_dir = os.path.join(CMS_BASE_DIR, subdir)
    os.makedirs(upload_dir, exist_ok=True)
    
    # Sanitize filename
    filename = file.filename.replace(" ", "_")
    filepath = os.path.join(upload_dir, filename)
    
    # Save file
    with open(filepath, "wb") as buffer:
        buffer.write(await file.read())
    
    # Return relative URL path (without 'uploads' since we'll mount it)
    return f"cms/{subdir}/{filename}"

async def save_upload_file_aboutus(file: UploadFile, subdir: str) -> str:
    """Save uploaded file and return relative URL path"""
    print("here 1")
    upload_dir = os.path.join(CMS_BASE_DIR, subdir)
    os.makedirs(upload_dir, exist_ok=True)
    
    # Sanitize filename
    filename = file.filename.replace(" ", "_")
    filepath = os.path.join(upload_dir, filename)
    
    # Save file
    with open(filepath, "wb") as buffer:
        buffer.write(await file.read())
    
    # Return relative URL path (without 'uploads' since we'll mount it)
    return f"cms/{subdir}/{filename}"


async def save_upload_file_inventory(file: UploadFile, subdir: str) -> str:
    """Save uploaded file and return relative URL path"""
    print("here 1")
    upload_dir = os.path.join(CMS_BASE_DIR, subdir)
    os.makedirs(upload_dir, exist_ok=True)
    
    # Sanitize filename
    filename = file.filename.replace(" ", "_")
    filepath = os.path.join(upload_dir, filename)
    
    # Save file
    with open(filepath, "wb") as buffer:
        buffer.write(await file.read())
    
    # Return relative URL path (without 'uploads' since we'll mount it)
    return f"cms/{subdir}/{filename}"

async def save_upload_file_productdetails(file: UploadFile, subdir: str) -> str:
    """Save uploaded file and return relative URL path"""
    print("here 1")
    upload_dir = os.path.join(CMS_BASE_DIR, subdir)
    os.makedirs(upload_dir, exist_ok=True)
    
    # Sanitize filename
    filename = file.filename.replace(" ", "_")
    filepath = os.path.join(upload_dir, filename)
    
    # Save file
    with open(filepath, "wb") as buffer:
        buffer.write(await file.read())
    
    # Return relative URL path (without 'uploads' since we'll mount it)
    return f"cms/{subdir}/{filename}"


@router.put("/v1/cms")
async def update_home_cms(
    request: Request,  # Added for URL generation
    heroTitle: str = Form(...),
    mediaItems: str = Form(...),
    brands: str = Form(...),
    priceRanges: str = Form(...),
    bodyTypes: str = Form(...),
    categories: str = Form(...),
    fairTitle: str = Form(...),
    fairDescription: str = Form(...),
    fairImage: Optional[List[UploadFile]] = File(default=None),
    sliderText: str = Form(...),
    dealTitle: str = Form(...),
    dealDescription: str = Form(...),
    dealImage: Optional[List[UploadFile]] = File(default=None),
    db: Session = Depends(get_db)
):
    try:
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
        }

        # Handle fair image upload
        if fairImage and fairImage.size > 0:
            print(f"Processing fair image: {fairImage.filename}")
            try:
                fair_image_path = await save_upload_file_cms(fairImage, "home/fair")
                data["fairImage"] = fair_image_path
            except Exception as e:
                raise HTTPException(
                    status_code=500,
                    detail=f"Failed to save fair image: {str(e)}"
                )

        # Handle deal image upload
        if dealImage and dealImage.size > 0:
            print(f"Processing deal image: {dealImage.filename}")
            try:
                deal_image_path = await save_upload_file_cms(dealImage, "home/deal")
                data["dealImage"] = deal_image_path
            except Exception as e:
                raise HTTPException(
                    status_code=500,
                    detail=f"Failed to save deal image: {str(e)}"
                )

        return update_cms_home(db, data)
    
    except json.JSONDecodeError as e:
        raise HTTPException(status_code=400, detail=f"Invalid JSON data: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/v1/cms")
def read_home_cms(request: Request, db: Session = Depends(get_db)):
    cms_data = get_cms_home(db)
    if not cms_data:
        raise HTTPException(status_code=404, detail="CMS data not found")
    
    # Convert to dict
    result = cms_data.__dict__
    
    # Generate full URLs for images
    if result.get('fairImage'):
        result['fairImage'] = str(request.base_url) + f"uploads/{result['fairImage']}"
    
    if result.get('dealImage'):
        result['dealImage'] = str(request.base_url) + f"uploads/{result['dealImage']}"
    
    # Remove SQLAlchemy internal state
    result.pop('_sa_instance_state', None)
    
    return result


# About Us Endpoints
@router.put("/v1/about-us")
async def update_about_us_cms(
    sectionOneTitle: str = Form(...),
    sectionOneDescription: str = Form(...),
    sectionTwoTitle: str = Form(...),
    sectionTwoDescription: str = Form(...),
    sectionTwoImages: Optional[List[UploadFile]] = File(default=None),  # Now accepts multiple files
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


    print(f"Received files: {sectionTwoImages}")
    if sectionTwoImages is not None:  # Explicit None check
        print("Files detected, processing...")
        image_paths = []
        for image in sectionTwoImages:
            if image.size > 0:  # Check if file has content
                print(f"Processing file: {image.filename}")
                try:
                    path = await save_upload_file_aboutus(image, "about-us")
                    image_paths.append(path)
                except Exception as e:
                    raise HTTPException(
                        status_code=500,
                        detail=f"Failed to save image {image.filename}: {str(e)}"
                    )
        if image_paths:
            data["sectionTwoImage"] = json.dumps(image_paths)
    print(3)
    
    return update_about_us(db, data)


@router.get("/v1/about-us")
def get_about_us_cms(request: Request, db: Session = Depends(get_db)):
    about_us = get_about_us(db)
    if not about_us:
        raise HTTPException(status_code=404, detail="About Us content not found")
    
    # Convert to dict
    result = about_us.__dict__
    
    # Process images to direct-viewable URLs
    if result.get('sectionTwoImage'):
        try:
            # Parse stored image paths (could be JSON array or comma-separated)
            if result['sectionTwoImage'].startswith('['):
                image_paths = json.loads(result['sectionTwoImage'])
            else:
                image_paths = result['sectionTwoImage'].split(',')
            
            # Create direct-access URLs
            result['sectionTwoImage'] = [
                str(request.base_url) + f"uploads/{path.strip()}"
                for path in image_paths
            ]
        except Exception as e:
            # Fallback to original if parsing fails
            result['sectionTwoImage'] = [str(request.base_url) + f"uploads/{result['sectionTwoImage']}"]
    
    # Remove SQLAlchemy internal state if present
    result.pop('_sa_instance_state', None)
    
    return result


# Inventory Endpoints
@router.put("/v1/inventory")
async def update_inventory_cms(
    request: Request,
    title: str = Form(...),
    description: str = Form(...),
    images: Optional[List[UploadFile]] = File(default=None),  # Now accepts multiple files
    db: Session = Depends(get_db)
):
    data = {
        "title": title,
        "description": description,
    }

    print(f"Received {len(images)} image(s) for inventory")
    
    if images:  # Check if any files were uploaded
        image_paths = []
        for image in images:
            if image.size > 0:  # Check if file has content
                print(f"Processing file: {image.filename}")
                try:
                    path = await save_upload_file_inventory(image, "inventory")
                    image_paths.append(path)
                except Exception as e:
                    raise HTTPException(
                        status_code=500,
                        detail=f"Failed to save image {image.filename}: {str(e)}"
                    )
        if image_paths:
            data["image"] = json.dumps(image_paths)  # Store as JSON array
    
    return update_inventory(db, data)

@router.get("/v1/inventory")
def get_inventory_cms(request: Request, db: Session = Depends(get_db)):
    inventory = get_inventory(db)
    if not inventory:
        raise HTTPException(status_code=404, detail="Inventory content not found")
    
    # Convert to dict
    result = inventory.__dict__
    
    # Process images to direct-viewable URLs
    if result.get('image'):
        try:
            # Parse stored image paths (JSON array)
            image_paths = json.loads(result['image'])
            
            # Create direct-access URLs
            result['image'] = [
                str(request.base_url) + f"uploads/{path.strip()}"
                for path in image_paths
            ]
        except json.JSONDecodeError:
            # Fallback to single image if not JSON array
            result['image'] = [str(request.base_url) + f"uploads/{result['image']}"]
        except Exception as e:
            print(f"Error processing image URLs: {str(e)}")
            result['image'] = []
    
    # Remove SQLAlchemy internal state if present
    result.pop('_sa_instance_state', None)
    
    return result

# Product Detail Endpoints
@router.put("/v1/product-detail")
async def update_product_detail_cms(
    request: Request,
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
    images: Optional[List[UploadFile]] = File(default=None),  # Changed to multiple files
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

    print(f"Received {len(images)} image(s) for product detail")
    
    if images:
        image_paths = []
        for image in images:
            if image.size > 0:
                print(f"Processing file: {image.filename}")
                try:
                    path = await save_upload_file_productdetails(image, "product-detail")
                    image_paths.append(path)
                except Exception as e:
                    raise HTTPException(
                        status_code=500,
                        detail=f"Failed to save image {image.filename}: {str(e)}"
                    )
        if image_paths:
            data["image"] = json.dumps(image_paths)  # Store as JSON array
    
    return update_product_detail(db, data)

@router.get("/v1/product-detail")
def get_product_detail_cms(request: Request, db: Session = Depends(get_db)):
    product = get_product_detail(db)
    if not product:
        raise HTTPException(status_code=404, detail="Product detail content not found")
    
    # Convert to dict
    result = product.__dict__
    
    # Process images to direct-viewable URLs
    if result.get('image'):
        try:
            # Handle both JSON array and single path (backward compatibility)
            if result['image'].startswith('['):
                image_paths = json.loads(result['image'])
                result['image'] = [
                    str(request.base_url) + f"uploads/{path.strip()}"
                    for path in image_paths
                ]
            else:
                result['image'] = [str(request.base_url) + f"uploads/{result['image']}"]
        except Exception as e:
            print(f"Error processing image URLs: {str(e)}")
            result['image'] = []
    
    # Remove SQLAlchemy internal state
    result.pop('_sa_instance_state', None)
    
    return result

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