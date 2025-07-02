from fastapi import APIRouter, Depends, Query, HTTPException, Request
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from app.db.db_setup import get_db
from app.db.models import Images, Videos, Vehicle, VehicleSafety, EngineTransmisison, DimensionCapicity, VehicleInterior, VehicleComfortConvenience, VehicleExterior
from app.db.schemas import SearchInventories
from app.db.crud import search_vehicles_inventory
import os
from app.db.models import *
from app.db.schemas import *
router = APIRouter()

@router.post("/v1/search_inventory")
def search_vehicles(request: Request,searching: SearchInventories, db: Session = Depends(get_db)):
    # Search vehicles by multiple fields (type, make, model, color, price, etc.)
    vehicles = db.query(Vehicle).filter(
        and_(
                Vehicle.status.in_(["Instock", "Outofstock", "New", "new", "Used", "used"]),  # Only include instock/sold vehicles
            or_(
                Vehicle.body_type.ilike(f"%{searching.search_query}%"),
                Vehicle.drive_type.ilike(f"%{searching.search_query}%"),
                Vehicle.make.ilike(f"%{searching.search_query}%"),
                Vehicle.model.ilike(f"%{searching.search_query}%"),
                Vehicle.year.ilike(f"%{searching.search_query}%"),
                Vehicle.name.ilike(f"%{searching.search_query}%"),
                Vehicle.chassis_number.ilike(f"%{searching.search_query}%"),
                Vehicle.transmission.ilike(f"%{searching.search_query}%"),
                Vehicle.color.ilike(f"%{searching.search_query}%"),
                Vehicle.engine.ilike(f"%{searching.search_query}%"),
                Vehicle.engine_name.ilike(f"%{searching.search_query}%"),
                Vehicle.status.ilike(f"%{searching.search_query}%"),
                Vehicle.doors.ilike(f"%{searching.search_query}%"),
                Vehicle.condition.ilike(f"%{searching.search_query}%"),
                Vehicle.grade.ilike(f"%{searching.search_query}%")
            )
        )
    ).all()
    
    vehicles_list = []

    """************************************************"""
    for veh in vehicles:
        # Query to get associated images and videos
        images = db.query(Images).filter(Images.fk_vehicle_id == veh.id).all()
        interior = db.query(VehicleInterior).filter(VehicleInterior.fk_vehicle_id == veh.id).first()
        safety = db.query(VehicleSafety).filter(VehicleSafety.fk_vehicle_id == veh.id).first()
        exterior = db.query(VehicleExterior).filter(VehicleExterior.fk_vehicle_id == veh.id).first()
        comfort = db.query(VehicleComfortConvenience).filter(VehicleComfortConvenience.fk_vehicle_id == veh.id).first()
        dimension = db.query(DimensionCapicity).filter(DimensionCapicity.fk_vehicle_id == veh.id).first()
        engine = db.query(EngineTransmisison).filter(EngineTransmisison.fk_vehicle_id == veh.id).first()
        bikeperformance = db.query(PerformanceFeature).filter(PerformanceFeature.fk_vehicle_id == veh.id).first()
        bikeusability = db.query(ComfortUsabilityFeatures).filter(ComfortUsabilityFeatures.fk_vehicle_id == veh.id).first()
        bikesafety = db.query(SafetyFeatures).filter(SafetyFeatures.fk_vehicle_id == veh.id).first()
        bikeconvenience = db.query(ConvenienceFeatures).filter(ConvenienceFeatures.fk_vehicle_id == veh.id).first()

        image_urls = []
        
        # Retrieve image paths and convert to accessible URLs
        if images is not None:
            for img in images:
                if img.image:
                    image_paths = img.image.split(",")  # Split comma-separated file paths
                    # Construct URLs to access the images
                    image_urls = [f"{request.base_url}uploads/vehicles/{os.path.basename(path)}" for path in image_paths]
                else:
                    image_urls = []

        vehicles_list.append({
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
                "interior":interior,
                "safety":safety,
                "exterior":exterior,
                "comfort":comfort,
                "dimension":dimension,
                "engine":engine,
                "bikeperformance": bikeperformance,
                "bikeusability": bikeusability,
                "bikesafety": bikesafety,
                "bikeconvenience": bikeconvenience
        })
    """************************************************"""
    retval = {
        "vehicle":vehicles_list
    }
    return retval



"""Comprehensive Search of Vehicles"""
@router.get("/v1/comprehensive_search_vehicle")
def search_comprehensive_vehicles(request: Request, make: str = Query(None), model: str = Query(None), grade: str = Query(None), year: str = Query(None), chassis: str = Query(None), mileage: str = Query(None), transmission: str = Query(None), displacement: str = Query(None), score: str = Query(None), steer: str = Query(None), color: str = Query(None), fuel: str = Query(None), db: Session = Depends(get_db)):
    try:
        search_criteria = {}

        if make:
            search_criteria['make'] = make

        if model:
            search_criteria['model'] = model

        # if min_price is not None or max_price is not None:
        #     search_criteria['price_range'] = (min_price, max_price)

        if grade:
            search_criteria['grade'] = grade

        if year:
            search_criteria['year'] = year

        if chassis:
            search_criteria['chassis'] = chassis

        if mileage:
            search_criteria['mileage'] = mileage

        if transmission:
            search_criteria['transmission'] = transmission

        if displacement:
            search_criteria['displacement'] = displacement

        if score:
            search_criteria['score'] = score

        if steer:
            search_criteria['steer'] = steer

        if color:
            search_criteria['color'] = color

        if fuel:
            search_criteria['fuel'] = fuel
            
        vehicle_search = search_vehicles_inventory(db, search_criteria)
        vehicle_list = []
        """************************************************"""
        for veh in vehicle_search:
            # Query to get associated images and videos
            images = db.query(Images).filter(Images.fk_vehicle_id == veh.id).all()
            videos = db.query(Videos).filter(Videos.fk_vehicle_id == veh.id).all()
            interior = db.query(VehicleInterior).filter(VehicleInterior.fk_vehicle_id == veh.id).first()
            safety = db.query(VehicleSafety).filter(VehicleSafety.fk_vehicle_id == veh.id).first()
            exterior = db.query(VehicleExterior).filter(VehicleExterior.fk_vehicle_id == veh.id).first()
            comfort = db.query(VehicleComfortConvenience).filter(VehicleComfortConvenience.fk_vehicle_id == veh.id).first()
            dimension = db.query(DimensionCapicity).filter(DimensionCapicity.fk_vehicle_id == veh.id).first()
            engine = db.query(EngineTransmisison).filter(EngineTransmisison.fk_vehicle_id == veh.id).first()
            bikeperformance = db.query(PerformanceFeature).filter(PerformanceFeature.fk_vehicle_id == veh.id).first()
            bikeusability = db.query(ComfortUsabilityFeatures).filter(ComfortUsabilityFeatures.fk_vehicle_id == veh.id).first()
            bikesafety = db.query(SafetyFeatures).filter(SafetyFeatures.fk_vehicle_id == veh.id).first()
            bikeconvenience = db.query(ConvenienceFeatures).filter(ConvenienceFeatures.fk_vehicle_id == veh.id).first()

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

            if videos is not None:
                # Retrieve video paths and handle similarly if needed
                for vid in videos:
                    if vid.video:
                        video_paths = vid.video.split(",")
                        # Construct URLs to access the videos
                        video_urls = [f"{request.base_url}uploads/vehicles/{os.path.basename(path)}" for path in video_paths]
                    else:
                        video_urls = []
            vehicle_list.append({
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
                "videos": video_urls,  # Include constructed video URLs
                "interior":interior,
                "safety":safety,
                "exterior":exterior,
                "comfort":comfort,
                "dimension":dimension,
                "engine":engine,
                "bikeperformance": bikeperformance,
                "bikeusability": bikeusability,
                "bikesafety": bikesafety,
                "bikeconvenience": bikeconvenience
            })
        """************************************************"""
       

        retval={
            "data": vehicle_list
        }
        return retval
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"{e}")


"""Overall Comprehensive Search of Vehicles and Spareparts"""
@router.get("/v1/overall_search_vehicle_sparepart_truck")
def search_comprehensive_vehicles(request: Request, category_type: str = Query(None), make: str = Query(None), model: str = Query(None), grade: str = Query(None), year: str = Query(None), chassis: str = Query(None), mileage: str = Query(None), transmission: str = Query(None), displacement: str = Query(None), score: str = Query(None), steer: str = Query(None), color: str = Query(None), fuel: str = Query(None), bodytype: str = Query(None), category: str = Query(None), keyword: str = Query(None), db: Session = Depends(get_db)):
    print(f"requested item:{category_type}")
    if category_type.lower() == "vehicle":
        print("In Vehicle")
        try:
            search_criteria = {}

            if make:
                search_criteria['make'] = make

            if model:
                search_criteria['model'] = model

            # if min_price is not None or max_price is not None:
            #     search_criteria['price_range'] = (min_price, max_price)

            if grade:
                search_criteria['grade'] = grade

            if year:
                search_criteria['year'] = year
                print(search_criteria['year'])

            if chassis:
                search_criteria['chassis'] = chassis

            if mileage:
                search_criteria['mileage'] = mileage
                print(search_criteria['mileage'])

            if transmission:
                search_criteria['transmission'] = transmission

            if displacement:
                search_criteria['displacement'] = displacement

            if score:
                search_criteria['score'] = score

            if steer:
                search_criteria['steer'] = steer

            if color:
                search_criteria['color'] = color

            if fuel:
                search_criteria['fuel'] = fuel
            
            if bodytype:
                search_criteria['bodytype'] = bodytype

            vehicle_search = search_vehicles_inventory(db, search_criteria)
            vehicle_list = []
            """************************************************"""
            for veh in vehicle_search:
                # Query to get associated images and videos
                images = db.query(Images).filter(Images.fk_vehicle_id == veh.id).all()
                videos = db.query(Videos).filter(Videos.fk_vehicle_id == veh.id).all()
                interior = db.query(VehicleInterior).filter(VehicleInterior.fk_vehicle_id == veh.id).first()
                safety = db.query(VehicleSafety).filter(VehicleSafety.fk_vehicle_id == veh.id).first()
                exterior = db.query(VehicleExterior).filter(VehicleExterior.fk_vehicle_id == veh.id).first()
                comfort = db.query(VehicleComfortConvenience).filter(VehicleComfortConvenience.fk_vehicle_id == veh.id).first()
                dimension = db.query(DimensionCapicity).filter(DimensionCapicity.fk_vehicle_id == veh.id).first()
                engine = db.query(EngineTransmisison).filter(EngineTransmisison.fk_vehicle_id == veh.id).first()
                bikeperformance = db.query(PerformanceFeature).filter(PerformanceFeature.fk_vehicle_id == veh.id).first()
                bikeusability = db.query(ComfortUsabilityFeatures).filter(ComfortUsabilityFeatures.fk_vehicle_id == veh.id).first()
                bikesafety = db.query(SafetyFeatures).filter(SafetyFeatures.fk_vehicle_id == veh.id).first()
                bikeconvenience = db.query(ConvenienceFeatures).filter(ConvenienceFeatures.fk_vehicle_id == veh.id).first()

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

                if videos is not None:
                    # Retrieve video paths and handle similarly if needed
                    for vid in videos:
                        if vid.video:
                            video_paths = vid.video.split(",")
                            # Construct URLs to access the videos
                            video_urls = [f"{request.base_url}uploads/vehicles/{os.path.basename(path)}" for path in video_paths]
                        else:
                            video_urls = []
                vehicle_list.append({
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
                    "videos": video_urls,  # Include constructed video URLs
                    "interior":interior,
                    "safety":safety,
                    "exterior":exterior,
                    "comfort":comfort,
                    "dimension":dimension,
                    "engine":engine,
                    "bikeperformance": bikeperformance,
                    "bikeusability": bikeusability,
                    "bikesafety": bikesafety,
                    "bikeconvenience": bikeconvenience
                })
            """************************************************"""


            retval={
                "data": vehicle_list
            }
            return retval
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"{e}")

    else:
        raise HTTPException(status_code=404, detail="No Data Found for this Type")
    
