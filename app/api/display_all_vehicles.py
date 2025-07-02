from fastapi import APIRouter, HTTPException, Depends, Request,Header
from app.db.crud import get_user_by_credentials
from app.helper.authenticate_user import autheticate_user
from app.db.schemas import User, Signin
from sqlalchemy.orm import Session
from app.db.db_setup import get_db
from app.helper.jwt_token import jwt_access_token
from app.helper.jwt_token_decode import decode_token
from app.helper.jwt_token import is_token_blacklisted
import os
import shutil
from app.db.models import *
from app.db.models import User as ModelUser
from sqlalchemy import or_
router = APIRouter()
# Signin API for entering into the application


@router.get("/v1/user/display_vehicles")
def disp_vehicles( request: Request,authorization: str = Header(None),db: Session = Depends(get_db)):
    if authorization is None:
        logging.error('The token entered for the user is either wrong or expired')
        raise HTTPException(status_code=401, detail="Unauthorized")
    token = authorization.split(" ")[1] if authorization.startswith("Bearer ") else authorization
    if is_token_blacklisted(token) == True:
        return {'Message': 'Session Expired please Login'}
    # we have return both the id and the complete data the only purpose is incase of refresh token we need all data in normal case we only need the id as foreign key
    user_id, retval = decode_token(token)  # Extracting the user_id as it would be used as foreign Key in the rollout table
    print(user_id)
    user_details = db.query(ModelUser).filter(ModelUser.id==user_id).first()
    print(user_details.firstname)

    try:
        if user_details.role == "overseas employee":
            data = (
                db.query(Vehicle)
                .filter(Vehicle.uploaded_by == user_details.firstname)
                .outerjoin(Images, Vehicle.id == Images.fk_vehicle_id)  # Join images
                .outerjoin(Videos, Vehicle.id == Videos.fk_vehicle_id)  # Join videos
                .outerjoin(VehicleInterior, Vehicle.id == VehicleInterior.fk_vehicle_id) # Join interior
                .outerjoin(VehicleSafety, Vehicle.id == VehicleSafety.fk_vehicle_id) # Join interior
                .outerjoin(VehicleExterior, Vehicle.id == VehicleExterior.fk_vehicle_id) # Join interior
                .outerjoin(VehicleComfortConvenience, Vehicle.id == VehicleComfortConvenience.fk_vehicle_id) # Join interior
                .outerjoin(DimensionCapicity, Vehicle.id == DimensionCapicity.fk_vehicle_id) # Join interior
                .outerjoin(EngineTransmisison, Vehicle.id == EngineTransmisison.fk_vehicle_id) # Join interior
                .all()
            )
        else:
            data = (
                db.query(Vehicle)
                .outerjoin(Images, Vehicle.id == Images.fk_vehicle_id)  # Join images
                .outerjoin(Videos, Vehicle.id == Videos.fk_vehicle_id)  # Join videos
                .outerjoin(VehicleInterior, Vehicle.id == VehicleInterior.fk_vehicle_id) # Join interior
                .outerjoin(VehicleSafety, Vehicle.id == VehicleSafety.fk_vehicle_id) # Join interior
                .outerjoin(VehicleExterior, Vehicle.id == VehicleExterior.fk_vehicle_id) # Join interior
                .outerjoin(VehicleComfortConvenience, Vehicle.id == VehicleComfortConvenience.fk_vehicle_id) # Join interior
                .outerjoin(DimensionCapicity, Vehicle.id == DimensionCapicity.fk_vehicle_id) # Join interior
                .outerjoin(EngineTransmisison, Vehicle.id == EngineTransmisison.fk_vehicle_id) # Join interior
                .all()
            )

        vehicles = []
        for veh in data:

            images = db.query(Images).filter(
            Images.fk_vehicle_id == veh.id,
            or_(
                Images.image_interior.isnot(None),
                Images.image_exterior.isnot(None)
                )
            ).all()

            # Then you can separate them:
            interior_images = [img.image_interior for img in images if img.image_interior]
            exterior_images = [img.image_exterior for img in images if img.image_exterior]
            videos = db.query(Videos).filter(Videos.fk_vehicle_id == veh.id).all()
            interior = db.query(VehicleInterior).filter(VehicleInterior.fk_vehicle_id == veh.id).first()
            safety = db.query(VehicleSafety).filter(VehicleSafety.fk_vehicle_id == veh.id).first()
            exterior = db.query(VehicleExterior).filter(VehicleExterior.fk_vehicle_id == veh.id).first()
            comfort = db.query(VehicleComfortConvenience).filter(VehicleComfortConvenience.fk_vehicle_id == veh.id).first()
            dimension = db.query(DimensionCapicity).filter(DimensionCapicity.fk_vehicle_id == veh.id).first()
            engine = db.query(EngineTransmisison).filter(EngineTransmisison.fk_vehicle_id == veh.id).first()

            image_urls = []
            int_image_urls = []
            ext_image_urls = []
            video_urls = []
            
            # Retrieve image paths and convert to accessible URLs
            if interior_images is not None:
                # Process interior images
                for img_path in interior_images:
                    if img_path:  # Check if path exists
                        image_paths = img_path.split(",")  # Split comma-separated paths
                        int_image_urls.extend([
                            f"{request.base_url}uploads/vehicles/interior/{os.path.basename(path.strip())}" 
                            for path in image_paths if path.strip()
                        ])


            if exterior_images is not None:
                # Process exterior images
                for img_path in exterior_images:
                    if img_path:  # Check if path exists
                        image_paths = img_path.split(",")  # Split comma-separated paths
                        ext_image_urls.extend([
                            f"{request.base_url}uploads/vehicles/exterior/{os.path.basename(path.strip())}" 
                            for path in image_paths if path.strip()
                        ])        

            image_urls.extend(ext_image_urls)
            image_urls.extend(int_image_urls)

            vehicles.append({
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
                "created_at": veh.created_at,
                "updated_at": veh.updated_at,
                "images": image_urls,  # Include constructed image URLs
                "images_interior": int_image_urls,  # Include constructed image URLs
                "images_exterior": ext_image_urls,  # Include constructed image URLs
                "videos": video_urls,  # Include constructed video URLs
                "interior":interior,
                "safety":safety,
                "exterior":exterior,
                "comfort":comfort,
                "dimension":dimension,
                "engine":engine
            })

        return {'data': vehicles}

    except Exception as e:
        return str(e)
