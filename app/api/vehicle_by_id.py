from fastapi import APIRouter, HTTPException, Depends, Query, Request
from sqlalchemy.orm import Session
from typing import List, Optional
from app.db.db_setup import get_db
import os
import shutil
from app.db.models import *

router = APIRouter()

@router.get("/v1/user/vehicles_return/{veh_id}")
def return_data(veh_id:int, request: Request, db: Session = Depends(get_db)):
    try:
        veh = (
            db.query(Vehicle)
            .filter(Vehicle.id == veh_id)
            .first()
        )

        if veh:
            # Query to get associated images and videos
            images = db.query(Images).filter(Images.fk_vehicle_id == veh.id).all()
            videos = db.query(Videos).filter(Videos.fk_vehicle_id == veh.id).all()
            interior = db.query(VehicleInterior).filter(VehicleInterior.fk_vehicle_id == veh.id).first()
            safety = db.query(VehicleSafety).filter(VehicleSafety.fk_vehicle_id == veh.id).first()
            exterior = db.query(VehicleExterior).filter(VehicleExterior.fk_vehicle_id == veh.id).first()
            comfort = db.query(VehicleComfortConvenience).filter(VehicleComfortConvenience.fk_vehicle_id == veh.id).first()
            dimension = db.query(DimensionCapicity).filter(DimensionCapicity.fk_vehicle_id == veh.id).first()
            engine = db.query(EngineTransmisison).filter(EngineTransmisison.fk_vehicle_id == veh.id).first()

            image_urls = []
            video_urls = []

            # Retrieve image paths and convert to accessible URLs
            if images is not None:
                for img in images:
                    if img.image:
                        image_paths = img.image.split(",")  # Split comma-separated file paths
                        # Construct URLs to access the images
                        image_urls = [f"{request.base_url}uploads/vehicles/{os.path.basename(path)}" for path in image_paths]
                    else:
                        image_urls = []
            barcode_url = None
            if images and images[0].barcode:
                print("yes")
                print(images[0].barcode)
                barcode_url = f"{request.base_url}{images[0].barcode}"
                        
            if videos is not None:
                # Retrieve video paths and handle similarly if needed
                for vid in videos:
                    if vid.video:
                        video_paths = vid.video.split(",")
                        # Construct URLs to access the videos
                        video_urls = [f"{request.base_url}uploads/vehicles/{os.path.basename(path)}" for path in video_paths]
                    else:
                        video_urls = []
            vehicle_data = {
                "id": veh.id,
                "body_type": veh.body_type,
                "drive_type": veh.drive_type,
                "make": veh.make,
                "model":veh.model,
                "year": veh.year,
                "title": veh.title,
                "name": veh.name,
                "chassis_number":veh.chassis_number,
                "mileage":veh.mileage,
                "damage_details":veh.damage_details,
                "transmission":  veh.transmission,
                "clynder": veh.clynder,
                "location": veh.location,
                "color": veh.color,
                "fuel": veh.fuel,
                "engine":veh.engine,
                "status": veh.status,
                "description": veh.description,
                "grade": veh.grade,
                "score": veh.score,
                "steer":  veh.steer,
                "displacement": veh.displacement,
                "total_price": veh.total_price,
                "sold_price": veh.sold_price,
                "recieved_amount": veh.recieved_amount,
                "balance_amount": veh.balance_amount,
                "auction_result": veh.auction_result,
                "condition":veh.condition,
                "doors": veh.doors,
                "engine_name": veh.engine_name,
                "supplier": veh.supplier,
                "is_clear": veh.is_clear,
                "report_status": veh.report_status,
                "feature": veh.feature,
                "uploaded_by":veh.uploaded_by,
                "sold_by":veh.sold_by,
                "created_at": veh.created_at,
                "updated_at": veh.updated_at,
                "images": image_urls,  # Include constructed image URLs
                "videos": video_urls,  # Include constructed video URLs
                "interior":interior,
                "safety":safety,
                "exterior":exterior,
                "comfort":comfort,
                "dimension":dimension,
                "engine":engine,
                "barcode": barcode_url

            }

        return {'data': vehicle_data}

    except Exception as e:
        return str(e)
        