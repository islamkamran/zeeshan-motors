from fastapi import HTTPException, APIRouter, Depends
from app.db.schemas import BLRequest
from sqlalchemy.orm import Session
from app.db.db_setup import get_db
from app.db.models import Container
import requests
from fastapi import APIRouter, Depends, HTTPException,Request
from sqlalchemy.orm import Session
from app.db.db_setup import get_db
from app.db.schemas import MonthInput,MonthSearch,ContainerCreate, ContainerUpdate, Contblnumber, Cont_blnumber,ContQuarter
from app.db.crud import get_container, create_container, update_container
from app.helper.quarter import get_date_range
from app.db.models import User, Container, Vehicle, Sparepart, Images, Invoice,Truck
import os
import shutil
import logging
import csv
from datetime import datetime, timedelta
from fastapi.responses import FileResponse
from app.db.crud import get_user_by_credentials
from app.helper.authenticate_user import autheticate_user
from app.helper.jwt_token import jwt_access_token
import logging
from sqlalchemy import func, and_
from sqlalchemy import text

router = APIRouter()

# Replace with your third-party API base URL and API key
THIRD_PARTY_API_URL = "https://tracking.searates.com/tracking"
API_KEY = "K-7484622E-03C9-4C55-BC01-BEAF2E9271DB"


@router.get("/v1/get-container-tracking")
async def get_container_tracking(db: Session = Depends(get_db)):
    
    """************logic for the get API****************"""
    bl_num = db.query(Container.bl_number).filter(Container.status == 'upcoming').all()
    bl_num_values = [item[0] for item in bl_num if item[0] not in (None, '')]
    print(bl_num_values)
    bl_num_values = ["TYO0641826","TYO0645144"]
    print(bl_num_values)
    """************logic for the get API****************"""

    results = []

    headers = {
        "Content-Type": "application/json",  # Explicitly specify JSON content type
    }

    for bl_number in bl_num_values:
        # Prepare request parameters
        params = {
            "api_key": API_KEY,
            "number": bl_number,
            "type": "BL",  # Since it's a Bill of Lading
            "sealine": "auto",  # Optional, auto-detect the shipping line
        }

        try:
            # Make a request to the third-party API
            response = requests.get(THIRD_PARTY_API_URL, params=params, headers=headers)
            response.raise_for_status()  # Raise error for HTTP status codes 4xx/5xx
            results.append({
                "bl_number": bl_number,
                "data": response.json()  # Append the JSON response
            })
        except requests.exceptions.RequestException as e:
            results.append({
                "bl_number": bl_number,
                "error": str(e)
            })
    extracted_data = []
    for result in results:
        data = result.get("data", {}).get("data", {})
        metadata = data.get("metadata", {})
        locations = data.get("locations", [])
        extracted_data.append({
            "metadata": metadata,
            "locations": locations
        })
    
    return {"data": extracted_data}




"""****************Google Reviews****************"""
# Your Google API key
GOOGLE_API_KEY = "AIzaSyB7snqxODPiRVEvFChFwdTOGTbh_j_AWpI"

@router.get("/v1/get_google_reviews")
def get_business_reviews(db: Session = Depends(get_db)):
    """
    Fetch reviews for the given Place ID.
    """
    place_id = "ChIJ80V8O7JeXz4RRW7ktzmPv7I"
    url = "https://maps.googleapis.com/maps/api/place/details/json"
    params = {
        "place_id": place_id,
        "fields": "name,rating,review",
        "key": GOOGLE_API_KEY
    }

    headers = {
        "Content-Type": "application/json",  # Explicitly specify JSON content type
    }

    response = requests.get(url, params=params, headers=headers)
    if response.status_code == 200:
        data = response.json()
        # print("hello")
        # print(data)
        if "result" in data and "reviews" in data["result"]:
            reviews = data["result"]["reviews"]
            return {"business_name": data["result"]["name"], "reviews": reviews}
        else:
            raise HTTPException(status_code=404, detail="No reviews found for this Place ID.")
    else:
        raise HTTPException(status_code=response.status_code, detail="Failed to fetch reviews from Google.")



"""************TOTAL COUNT BY MONTH FILTER FOR DASHBOARD**********************"""
@router.post("/v1/containers_count_dashboard")
def read_container(input_data: MonthInput, db: Session = Depends(get_db)):
    all_containers = 0
    upcoming_containers = 0
    arrived_containers = 0

    try:
        month_num = datetime.strptime(input_data.month, "%B").month
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid month name provided.")
    year = input_data.year
    start_date = datetime(year, month_num, 1)
    if month_num == 12:
        end_date = datetime(year + 1, 1, 1)
    else:
        end_date = datetime(year, month_num + 1, 1)

    # Total sales and revenue for vehicles
    upcoming_container_data = db.query(
        func.count(Container.id).label("total_upcoming")
    ).filter(func.lower(Container.status).ilike("%upcoming%"),
        and_(
            Container.created_at >= start_date,
            Container.created_at < end_date
        )
    ).one()

    upcoming_containers = upcoming_container_data.total_upcoming
    print(upcoming_containers)

    arrived_container_data = db.query(
        func.count(Container.id).label("total_arrived")
    ).filter(func.lower(Container.status).ilike("%arrived%"),
        and_(
            Container.created_at >= start_date,
            Container.created_at < end_date
        )
    ).one()

    arrived_containers = arrived_container_data.total_arrived
    print(arrived_containers)

    retval = {
        "arrived": arrived_containers,
        "upcoming": upcoming_containers,
        "total": arrived_containers+upcoming_containers
    }
    return {"data":retval}

