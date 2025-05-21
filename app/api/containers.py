import traceback
from fastapi import APIRouter, HTTPException, Depends, Header, File, UploadFile, Form, Request,status
from app.db.crud import *
from app.helper.authenticate_user import autheticate_user
from app.db.schemas import *
from app.db.models import  *
from sqlalchemy.orm import Session
from app.db.db_setup import get_db
from app.helper.jwt_token import jwt_access_token
from app.helper.jwt_token_decode import decode_token
from app.helper.barcode_generator import generate_barcode_vehicle
from app.helper.jwt_token import is_token_blacklisted
from app.helper.quarter import get_date_range
import os
import shutil
import csv
from app.helper.emails import send_quote_to_email
from fastapi.responses import FileResponse
import json
import requests
from datetime import datetime, timedelta
from sqlalchemy import func, and_
from sqlalchemy import text



REPORT_DIR = "container_reports/"  # Directory to save the report

# Ensure the report directory exists
os.makedirs(REPORT_DIR, exist_ok=True)

EXPORT_DIR = "exports/"  # Directory to save the file
UPLOAD_DIR = "uploads/containers/"  # Ensure this directory exists

router = APIRouter()

@router.post("/v1/container")
def containers_creation(shipper: str = Form(None), shipping_company: str = Form(None), bl_number: str = Form(None), container_number: str = Form(None), seal_number: str = Form(None), gross_weight: str = Form(None), port_of_discharge: str = Form(None), port_of_loading: str = Form(None), no_of_units: str = Form(None), status: str = Form(None), description: str = Form(None), eta: str = Form(None),  image: list[UploadFile] = File(None), vehicles: str = Form(None), authorization: str = Header(None), db: Session = Depends(get_db)):
    try:
        print(1)
        bind = db.get_bind()
        if bind is None:
            raise HTTPException(status_code=500, detail="Database session is nout bound to an engine")
        if authorization is None:
            raise HTTPException(status_code=401, detail="Unauthorized")
        print(2)
        token = authorization.split(" ")[1] if authorization.startswith("Bearer ") else authorization
        if is_token_blacklisted(token) == True:
            return {'Message': 'Session Expired please Login'}

        # we have return both the id and the complete data the only purpose is incase of refresh token we need all data in normal case we only need the id as foreign key
        user_id, retval = decode_token(token)  # Extracting the user_id as it would be used as foreign Key in the rollout table
        print(3)
        print(f"*********user id: {user_id}***********")

        user_data = db.query(User).filter(User.id == user_id).first()
        if user_data is None:
            raise HTTPException(status_code=404, detail="User Not Found")
        print(4)

        if bl_number is not None:
            check_container = db.query(Container).filter(Container.bl_number == bl_number).first()
            if check_container:
                raise HTTPException(status_code=409, detail="Container with this BL number is already registered")
        container_data = ContainerCreate(shipper=shipper, shipping_company=shipping_company, bl_number=bl_number, container_number=container_number,seal_number=seal_number,gross_weight=gross_weight,port_of_discharge=port_of_discharge, port_of_loading=port_of_loading, no_of_units = no_of_units, status=status, description=description, eta=eta)
        container_data = container_data.dict()
        container_id = create_ccontainer(db,user_id, user_data.firstname, ContainerCreate(**container_data))
        print(5)

        """storing images and videos"""
        image_paths = []
        print(6)

        # Save image files to the uploads directory
        if image is not None:
            for img in image:
                img.filename = str(container_id) + img.filename
                print(img.filename)
                file_location = os.path.join(UPLOAD_DIR, img.filename)
                with open(file_location, "wb") as buffer:
                    shutil.copyfileobj(img.file, buffer)
                print(file_location)
                image_paths.append(file_location)

            # Convert list of paths to a comma-separated string
            images_string = ",".join(image_paths)

            cont_images = Images(
                image = images_string,
                fk_container_id = container_id
            )
            db.add(cont_images)
            db.commit()
            db.refresh(cont_images)
        print(7)

        """************************************vehicles******************************************"""
        # adding the container number to the vehicles
        if vehicles:
            vehicles_data = json.loads(vehicles)
        else:
            vehicles_data = []
        
        print("Vehicles data:", vehicles_data)

        # update the vehicles with the given chassis number with the respective container id
        for veh in vehicles_data:
            # Access each detail of the vehicle
            chassis_number = veh.get("chassis_number")
            # make = veh.get("make")
            # model = veh.get("model")
            # year = veh.get("year")
            # color = veh.get("color")

            # Log the chassis number for debugging
            print(f"Processing vehicle with chassis number: {chassis_number}")

            # Example: Update the vehicle's container number based on chassis_number
            existing_vehicle = db.query(Vehicle).filter(Vehicle.chassis_number == chassis_number).first()
            if existing_vehicle is None:
                existing_vehicle = db.query(Truck).filter(Truck.chassis_number == chassis_number).first()
            if existing_vehicle:
                # Update container details or any other fields
                existing_vehicle.fk_container_id = container_id # assuming `container_number` is available
                db.commit()
                db.refresh(existing_vehicle)
                print(f"Updated container number for vehicle {chassis_number}")

            else:
                print(f"No vehicle/ Truck found with chassis number: {chassis_number}")

        print(9)

        retval = {
            "container_id": container_id
        }
        return {"data": retval}

    except Exception as e:
        print(10)
        print(traceback.format_exc())
        raise HTTPException(status_code=409, detail=f' Error: {str(e)}')


# """***********UPDATE CONTAINER************************"""
@router.put("/v1/container/{container_id}")
def containers_updation(container_id:int, shipper: str = Form(None), shipping_company: str = Form(None), bl_number: str = Form(None), container_number: str = Form(None), seal_number: str = Form(None), gross_weight: str = Form(None), port_of_discharge: str = Form(None), port_of_loading: str = Form(None), no_of_units: str = Form(None), status: str = Form(None), description: str = Form(None), eta: str = Form(None),  image: list[UploadFile] = File(None), vehicles: str = Form(None), authorization: str = Header(None), db: Session = Depends(get_db)):
    try:
        bind = db.get_bind()
        if bind is None:
            raise HTTPException(status_code=500, detail="Database session is not bound to an engine")
        if authorization is None:
            raise HTTPException(status_code=401, detail="Unauthorized")
        token = authorization.split(" ")[1] if authorization.startswith("Bearer ") else authorization
        if is_token_blacklisted(token) == True:
            return {'Message': 'Session Expired please Login'}

        # we have return both the id and the complete data the only purpose is incase of refresh token we need all data in normal case we only need the id as foreign key
        user_id, retval = decode_token(token)  # Extracting the user_id as it would be used as foreign Key in the rollout table
        print(f"user id: {user_id}")

        check_container = db.query(Container).filter(Container.id == container_id).first()
        if check_container is None:
            raise HTTPException(status_code=404, detail="Container not found")
        
        previous_status = check_container.status
        print(previous_status)
        container_data = ContainerUpdate(shipper=shipper, shipping_company=shipping_company, bl_number=bl_number, container_number=container_number,seal_number=seal_number,gross_weight=gross_weight,port_of_discharge=port_of_discharge, port_of_loading=port_of_loading, no_of_units = no_of_units, status=status, description=description, eta=eta)
        for key, value in container_data.model_dump(exclude_unset=True).items():
            setattr(check_container, key, value)
        db.commit()
        db.refresh(check_container)
        new_status = check_container.status
        if previous_status != new_status and new_status == "arrived":
            print("inside if")
            """Create a notification and store in Notification Table"""
            notification = Notification(
                fk_user_id=None,
                message=f"Status of Container {check_container.id} has been changed to Arrived.",
                read = False
            )
            db.add(notification)
            db.commit()
            db.refresh(notification)


        """*********************images updating***********************"""
        image_paths = []

        # Save image files to the uploads directory
        if image is not None:
            print("I have an Image")
            for img in image:
                img.filename = str(container_id) + img.filename
                print(img.filename)
                file_location = os.path.join(UPLOAD_DIR, img.filename)
                with open(file_location, "wb") as buffer:
                    shutil.copyfileobj(img.file, buffer)
                print(file_location)
                image_paths.append(file_location)

            # Convert list of paths to a comma-separated string
            images_string = ",".join(image_paths)
            print(images_string)
            # Incase of new Image
            cont_images = Images(
                image = images_string,
                fk_container_id = container_id
            )
            # Incase of updating the images
            cont_images_update = ContImageSchema(
                image = images_string,
                fk_container_id = container_id
            )

            check_img = db.query(Images).filter(Images.fk_container_id == container_id).first()
            print(f"the container images: {check_img}")
            if check_img is None:
                print("INSIDE")
                db.add(cont_images)
                db.commit()
                db.refresh(cont_images)
            else:
                for key, value in cont_images_update.model_dump(exclude_unset=True).items():
                    setattr(check_img, key, value)

                db.commit()
                db.refresh(check_img) 
            print(2)
        elif image is None:
            print("I dont have an Image")
            print("Empty Images are passed")
            check_img = db.query(Images).filter(Images.fk_container_id == container_id).first()
            print(f"the images: {check_img}")
            if check_img is not None:
                print("old images are here we will delete them now")
                check_img.image = ""
                print(f'check image: {check_img.image}')
                db.commit()
                db.refresh(check_img)


        """Remove the old reference of vehicles and spareparts from this container later we will add them again"""
        print("removing reference from vehicle and spareparts")
        # Remove reference from vehicles
        old_ref_vehicle = db.query(Vehicle).filter(Vehicle.fk_container_id == container_id).all()
        if old_ref_vehicle:
            for veh in old_ref_vehicle:
                veh.fk_container_id = None

        # Commit the changes after updating all references
        db.commit()
        print("Removed reference from vehicle and spareparts")
        """************************************vehicles******************************************"""
        # adding the container number to the vehicles
        if vehicles:
            vehicles_data = json.loads(vehicles)
        else:
            vehicles_data = []
        
        print("Vehicles data:", vehicles_data)

        # update the vehicles with the given chassis number with the respective container id
        for veh in vehicles_data:
            # Access each detail of the vehicle
            chassis_number = veh.get("chassis_number")

            # Example: Update the vehicle's container number based on chassis_number
            existing_vehicle = db.query(Vehicle).filter(Vehicle.chassis_number == chassis_number).first()
            if existing_vehicle is None:
                print(f"No vehicle/ truck found with chassis number: {chassis_number}")
            if existing_vehicle:
                # Update container details or any other fields
                existing_vehicle.fk_container_id = container_id # assuming `container_number` is available
                db.commit()
                db.refresh(existing_vehicle)
                print(f"Updated container number for vehicle {chassis_number}")

        retval = {
            "message": "container updated successfully",
        }
        return {"data": retval}

    except Exception as e:
        print(traceback.format_exc())
        raise HTTPException(status_code=409, detail=f' Error: {str(e)}')

"""*******************Update container status outside***************"""

@router.patch("/v1/container/update-status")
def update_container_status(update_data: UpdateContainerStatus, db: Session = Depends(get_db)):
    # Fetch the vehicle from the database
    if update_data.container_id:
        data = db.query(Container).filter(Container.id == update_data.container_id).first()
        if not data:
            raise HTTPException(status_code=404, detail="Container not found")
    # Update only the specified fields
    if update_data.status:
        data.status = update_data.status

    # Save the changes
    db.commit()
    db.refresh(data)
    return {
        "status": data.status,
    }



@router.get("/v1/containers")
def get_container_details(data: BLNumber, db: Session = Depends(get_db)):
    container = db.query(Container).filter(Container.bl_number == data.bl_number).first()
    if not container:
        raise HTTPException(status_code=404, detail="Container not found")

    vehicles = db.query(Vehicle).filter(Vehicle.fk_container_id == container.id).all()
    # spareparts = db.query(Sparepart).filter(Sparepart.fk_container_id == container_id).all()

    retval = {
        "id": container.id,
        "container_number": container.container_number,
        "bl_number": container.bl_number,
        "status": container.status,
        "expected_arrival": container.estimated_arrival_date,
        "vehicles": vehicles,
        # "spareparts": spareparts,
        "created_at": container.created_at,
        "updated_at": container.updated_at
    }

    return retval




@router.get("/v1/containers_dropdown")
def get_container_details(db: Session = Depends(get_db)):
    containers = db.query(Container).all()
    if not containers:
        raise HTTPException(status_code=404, detail="No containers found")

    retval = [
        {
            "id": container.id,
            "bl_number": container.bl_number,
            "created_at": container.created_at,
            "updated_at": container.updated_at
        }
        for container in containers
    ]
    
    return {"data": retval}

@router.get("/v1/get_all_containers")
def read_containers(db: Session = Depends(get_db)):
    containers = get_all_containers(db)
    retval = {
        "data": containers
        }
    return retval

@router.get("/containers/{container_id}/location", response_model=ContainerLocation)
def get_container_location(container_id: int, db: Session = Depends(get_db)):
    container = db.query(Container).filter(Container.id == container_id).first()
    if not container:
        raise HTTPException(status_code=404, detail="Container not found")
    
    return container



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






@router.get("/v1/containers/{container_id}")
def read_container(container_id: int, request: Request, db: Session = Depends(get_db)):
    db_containers = db.query(Container).filter(Container.id == container_id).all()
    
    if not db_containers:
        raise HTTPException(status_code=404, detail="Container not found")
    # get the images of the containers
    images = db.query(Images).filter(Images.fk_container_id == container_id).all()
    image_urls = []
    # Retrieve image paths and convert to accessible URLs
    if images is not None:
        for img in images:
            if img.image:
                image_paths = img.image.split(",")  # Split comma-separated file paths
                # Construct URLs to access the images
                image_urls = [f"{request.base_url}uploads/containers/{os.path.basename(path)}" for path in image_paths]
            else:
                image_urls = []

    if not db_containers:
        raise HTTPException(status_code=404, detail="Container not found")

    containers_data = []

    for cont in db_containers:
        # Retrieve vehicles and add a type identifier
        vehicles = db.query(Vehicle).filter(Vehicle.fk_container_id == cont.id).all()
        items_data = [
            {
                "type": "vehicle",
                "id": vehicle.id,
                "chassis_number": vehicle.chassis_number,
                "make": vehicle.make,
                "model": vehicle.model,
                "year": vehicle.year,
                "color": vehicle.color,
                "price": vehicle.total_price
            }
            for vehicle in vehicles
        ]

        # Add data for each container
        containers_data.append({
            "container": cont,
            "images": image_urls,
            "items": items_data
        })

    return {"data": containers_data}



@router.get("/v1/containers_arrived")
def read_container(db: Session = Depends(get_db)):
    # Query for all containers with status "arrived"
    db_containers = db.query(Container).filter(Container.status == "arrived").all()
    if not db_containers:
        raise HTTPException(status_code=404, detail="Container not found")

    containers_data = []

    for cont in db_containers:
        # Retrieve vehicles and add a type identifier
        vehicles = db.query(Vehicle).filter(Vehicle.fk_container_id == cont.id).all()
        items_data = [
            {
                "type": "vehicle",
                "id": vehicle.id,
                "chassis_number": vehicle.chassis_number,
                "make": vehicle.make,
                "model": vehicle.model,
                "year": vehicle.year,
                "color": vehicle.color,
            }
            for vehicle in vehicles
        ]


        # Add data for each container
        containers_data.append({
            "container": cont,
            "items": items_data
        })

    return {"data": containers_data}


@router.get("/v1/containers_upcoming")
def read_container(db: Session = Depends(get_db)):
    db_containers = db.query(Container).filter(Container.status == "upcoming").all()
    if not db_containers:
        raise HTTPException(status_code=404, detail="Container not found")

    containers_data = []

    for cont in db_containers:
        # Retrieve vehicles and add a type identifier
        vehicles = db.query(Vehicle).filter(Vehicle.fk_container_id == cont.id).all()
        items_data = [
            {
                "type": "vehicle",
                "id": vehicle.id,
                "chassis_number": vehicle.chassis_number,
                "make": vehicle.make,
                "model": vehicle.model,
                "year": vehicle.year,
                "color": vehicle.color,
            }
            for vehicle in vehicles
        ]
        # Add data for each container
        containers_data.append({
            "container": cont,
            "items": items_data
        })

    return {"data": containers_data}


"""***********************get all containers**************************"""
@router.get("/v1/all_containers")
def read_container(db: Session = Depends(get_db)):
    db_containers = db.query(Container).all()
    if not db_containers:
        raise HTTPException(status_code=404, detail="Container not found")

    containers_data = []

    for cont in db_containers:
        # Retrieve vehicles and add a type identifier
        vehicles = db.query(Vehicle).filter(Vehicle.fk_container_id == cont.id).all()
        items_data = [
            {
                "type": "vehicle",
                "id": vehicle.id,
                "chassis_number": vehicle.chassis_number,
                "make": vehicle.make,
                "model": vehicle.model,
                "year": vehicle.year,
                "color": vehicle.color,
            }
            for vehicle in vehicles
        ]


        # Add data for each container
        containers_data.append({
            "container": cont,
            "items": items_data
        })

    return {"data": containers_data}
"""*****************SEARCH ON BL NUMBER******************"""

@router.get("/v1/containers_blnumber")
def read_container(data: Contblnumber, db: Session = Depends(get_db)):
    db_containers = db.query(Container).filter(Container.bl_number == data.bl_number).all()
    if not db_containers:
        raise HTTPException(status_code=404, detail="Container not found")

    containers_data = []

    for cont in db_containers:
        # Retrieve vehicles and add a type identifier
        vehicles = db.query(Vehicle).filter(Vehicle.fk_container_id == cont.id).all()
        items_data = [
            {
                "type": "vehicle",
                "id": vehicle.id,
                "chassis_number": vehicle.chassis_number,
                "make": vehicle.make,
                "model": vehicle.model,
                "year": vehicle.year,
                "color": vehicle.color,
            }
            for vehicle in vehicles
        ]


        # Add data for each container
        containers_data.append({
            "container": cont,
            "items": items_data
        })

    return {"data": containers_data}


"""*****************SEARCH ON MONTH******************"""
@router.get("/v1/search_by_month")
def search_container(data: MonthSearch, db: Session = Depends(get_db)):
    # Define the search pattern to match containers in the specified month
    search_pattern = f"%{data.month.lower()}%"
    
    # Count total containers for the specified month
    total_containers = db.query(Container).filter(
        func.lower(Container.estimated_arrival_date).like(search_pattern)
    ).count()
    
    # Count containers with status 'arrived' for the specified month
    arrived_count = db.query(Container).filter(
        func.lower(Container.estimated_arrival_date).like(search_pattern),
        Container.status == 'arrived'
    ).count()
    
    # Count containers with status 'upcoming' for the specified month
    upcoming_count = db.query(Container).filter(
        func.lower(Container.estimated_arrival_date).like(search_pattern),
        Container.status == 'upcoming'
    ).count()

    # If no containers found for the month
    if total_containers == 0:
        raise HTTPException(status_code=404, detail="No containers found for the specified month")
    
    return {
        f"total_containers in {data.month}": total_containers,
        f"arrived_count in {data.month}": arrived_count,
        f"upcoming_count in {data.month}": upcoming_count
    }


"""***************** GET CONTAINERS NAMES ONLY ********************"""
@router.get("/v1/read_containers_names")
def read_container_names(db: Session = Depends(get_db)):
    bl_numbers = db.query(Container.bl_number).all()
    return {"data": [bl_number[0] for bl_number in bl_numbers]}


"""*****************SEARCH ON CONTAINER NUMBER/BL NUMBER******************"""
@router.post("/v1/containers_blnum_contnum")
def read_container(data: Cont_blnumber, db: Session = Depends(get_db)):
    db_containers = db.query(Container).filter(Container.bl_number == data.item).all()
    if not db_containers:
        db_containers = db.query(Container).filter(Container.container_number == data.item).all()
        if not db_containers:
            raise HTTPException(status_code=404, detail="Container not found")

    containers_data = []

    for cont in db_containers:
        # Retrieve vehicles and add a type identifier
        vehicles = db.query(Vehicle).filter(Vehicle.fk_container_id == cont.id).all()

        items_data = [
            {
                "type": "vehicle",
                "id": vehicle.id,
                "chassis_number": vehicle.chassis_number,
                "make": vehicle.make,
                "model": vehicle.model,
                "year": vehicle.year,
                "color": vehicle.color,
            }
            for vehicle in vehicles
        ]

        # Add data for each container
        containers_data.append({
            "container": cont,
            "items": items_data
        })

    return {"data": containers_data}


"""************TOTAL COUNT**********************"""
@router.get("/v1/containers_count")
def read_container(db: Session = Depends(get_db)):
    # Count arrived containers (case-insensitive)
    arrived_count = db.query(Container).filter(func.lower(Container.status).ilike("%arrived%")).count()
    
    # Count upcoming containers (case-insensitive)
    upcoming_count = db.query(Container).filter(func.lower(Container.status).ilike("%upcoming%")).count()
    
    # Total containers
    total_count = arrived_count + upcoming_count

    retval = {
             "arrived": arrived_count,
             "upcoming": upcoming_count,
             "total": total_count
    }
    return retval



"""************Quaters data in CSV**********************"""
@router.post("/v1/container/report")
def generate_container_report(data: ContQuarter, db: Session = Depends(get_db)):
    try:
        # Get date range based on quarter
        start_date, end_date = get_date_range(data.quarter)
        
        # Query containers within the date range
        containers = db.query(Container).filter(
            Container.created_at >= start_date,
            Container.created_at <= end_date
        ).all()
        
        # CSV file path
        report_file = os.path.join(REPORT_DIR, f"{data.quarter}_container_report.csv")
        
        # Generate CSV
        with open(report_file, mode="w", newline="") as file:
            writer = csv.writer(file)
            # Write headers
            writer.writerow([
                "ID", "Shipper", "Shipping Company", "BL Number",
                "Container Number", "Seal Number", "Gross Weight",
                "Port of Discharge", "Port of Loading", "No of Units", "Status","description",
                "Created At", "Updated At"
            ])
            # Write data rows
            for container in containers:
                writer.writerow([
                    container.id, container.shipper, container.shipping_company,
                    container.bl_number, container.container_number,
                    container.seal_number, container.gross_weight,
                    container.port_of_discharge, container.port_of_loading,
                    container.no_of_units, container.status,container.description,
                    container.created_at, container.updated_at
                ])
        
        # Return download link
        
        # return {"download_link": f"/v1/container/download-report/{data.quarter}"}
        return FileResponse(report_file, filename=f"{data.quarter}_container_report.csv", media_type="text/csv")
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



"""*************UPCOMING AND ARRIVED CONTAINER REPORTS"""

# Helper function to generate CSV
def generate_csv(containers, report_file):
    with open(report_file, mode="w", newline="") as file:
        writer = csv.writer(file)
        # Write headers
        writer.writerow([
            "ID", "Shipper", "Shipping Company", "BL Number",
            "Container Number", "Seal Number", "Gross Weight",
            "Port of Discharge", "Port of Loading", "No of Units", "Status","description",
            "Created At", "Updated At"
        ])
        # Write data rows
        for container in containers:
            writer.writerow([
                container.id, container.shipper, container.shipping_company,
                container.bl_number, container.container_number,
                container.seal_number, container.gross_weight,
                container.port_of_discharge, container.port_of_loading,
                container.no_of_units, container.status,container.description,
                container.created_at, container.updated_at
            ])

# Endpoint for arrived containers report
@router.get("/v1/container/report/arrived")
def generate_arrived_container_report(db: Session = Depends(get_db)):
    try:
        
        # Query for arrived containers
        containers = db.query(Container).filter(func.lower(Container.status).ilike("%arrived%")).all()
        
        report_file = os.path.join(REPORT_DIR, f"arrived_container_report.csv")
        generate_csv(containers, report_file)
        
        return FileResponse(report_file, filename=f"arrived_container_report.csv", media_type="text/csv")
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Endpoint for upcoming containers report
@router.get("/v1/container/report/upcoming")
def generate_upcoming_container_report(db: Session = Depends(get_db)):
    try:
        
        # Query for upcoming containers
        containers = db.query(Container).filter(func.lower(Container.status).ilike("%upcoming%")).all()
        
        report_file = os.path.join(REPORT_DIR, f"upcoming_container_report.csv")
        generate_csv(containers, report_file)
        
        return FileResponse(report_file, filename=f"upcoming_container_report.csv", media_type="text/csv")
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Endpoint for upcoming containers report
@router.get("/v1/container/report/all_containers_report")
def generate_upcoming_container_report(db: Session = Depends(get_db)):
    try:
        
        # Query for upcoming containers
        containers = db.query(Container).all()
        
        report_file = os.path.join(REPORT_DIR, f"all_container_report.csv")
        generate_csv(containers, report_file)
        
        return FileResponse(report_file, filename=f"all_container_report.csv", media_type="text/csv")
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


"""**********************READ CONTAINER BY ID AND ALSO REPORT OF THE ASSOCIATED VEHICLES AND SPAREPARTS WITH IT"""
@router.get("/v1/containers/{container_id}/report")
def generate_single_container_report(container_id: int, request: Request, db: Session = Depends(get_db)):
    # Query the container by ID
    total_price_container = 0
    print(f'price:{total_price_container}')
    container = db.query(Container).filter(Container.id == container_id).first()
    if not container:
        raise HTTPException(status_code=404, detail="Container not found")

    # Retrieve associated images
    images = db.query(Images).filter(Images.fk_container_id == container_id).all()
    image_urls = []
    if images:
        for img in images:
            if img.image:
                image_paths = img.image.split(",")  # Split comma-separated file paths
                image_urls += [f"{request.base_url}uploads/containers/{os.path.basename(path)}" for path in image_paths]

    # Retrieve associated vehicles
    vehicles = db.query(Vehicle).filter(Vehicle.fk_container_id == container_id).all()

    # Retrieve associated spare parts

    if vehicles is not None:
        for veh in vehicles:
            total_price_container = total_price_container + veh.total_price
    # CSV file path
    report_file = os.path.join(REPORT_DIR, f"container_{container_id}_report.csv")

    try:
        # Generate CSV report
        with open(report_file, mode="w", newline="") as file:
            writer = csv.writer(file)

            # Write container details
            writer.writerow(["Container Details"])
            writer.writerow(["ID", "Shipper", "Shipping Company", "BL Number", "Container Number", "Seal Number",
                             "Gross Weight", "Port of Discharge", "Port of Loading", "No of Units", "Status","description","Total Container Cost",
                             "Created At", "Updated At"])
            writer.writerow([
                container.id, container.shipper, container.shipping_company, container.bl_number,
                container.container_number, container.seal_number, container.gross_weight,
                container.port_of_discharge, container.port_of_loading, container.no_of_units,
                container.status,container.description,total_price_container, container.created_at, container.updated_at
            ])

            # Write images section
            writer.writerow([])
            writer.writerow(["Container Images"])
            writer.writerow(["Image URLs"])
            for url in image_urls:
                writer.writerow([url])

            # Write vehicles section
            writer.writerow([])
            # Write vehicles section only if vehicles exist
            if vehicles:
                writer.writerow([])
                writer.writerow(["Vehicles"])
                writer.writerow(["ID", "Chassis Number", "Make", "Model", "Year", "Color"])
                for vehicle in vehicles:
                    writer.writerow([
                        vehicle.id, vehicle.chassis_number, vehicle.make, vehicle.model,
                        vehicle.year, vehicle.color
                    ])
            
        # Return the generated report
        return FileResponse(report_file, filename=f"container_{container_id}_report.csv", media_type="text/csv")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating report: {str(e)}")



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


@router.post("/v1/report/confirm")
def confirm_report(vehicle_id: int, db: Session = Depends(get_db)):
    try:
        if vehicle_id:
            vehicle = db.query(Vehicle).filter(Vehicle.id == vehicle_id).first()
            if vehicle:
                vehicle.report_status = 'confirmed'
                db.commit()

        return {"message": "Report confirmed and ready to be sent"}
    
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to confirm report")

@router.put("/v1/containers/{container_id}")
def update_container_endpoint(container_id: int, container: ContainerUpdate, db: Session = Depends(get_db), authorization: str = Header(None)):
    if authorization is None:
        raise HTTPException(status_code=401, detail="Unauthorized")
    token = authorization.split(" ")[1] if authorization.startswith("Bearer ") else authorization
    # we have return both the id and the complete data the only purpose is incase of refresh token we need all data in normal case we only need the id as foreign key
    user_id, retval = decode_token(token)  # Extracting the user_id as it would be used as foreign Key in the rollout table
    # print(f'retval: {retval}')
    check = db.query(User).filter(User.id == user_id).first()

    db_container = get_container(db, container_id=container_id)
    if not db_container:
        raise HTTPException(status_code=404, detail="Container not found")
    if check:
        if check.role not in ["admin", "employee", "Customer", "customer"]:
            raise HTTPException(status_code=403, detail="Not authorized")
    
    return update_container(db, container_id, ContainerUpdate(**container.model_dump()))



@router.put("/v1/container/{container_id}/status-at-yard")
def update_container_status(container_id: int, stat: ContainerStatus, db: Session = Depends(get_db), authorization: str = Header(None)):
    try:
        # if the status: str do not work we have to work it out using pydentic classes make a pydentic for the str
        token = authorization.split(" ")[1] if authorization.startswith("Bearer ") else authorization
        user_id, _ = decode_token(token)

        container = db.query(Container).filter(Container.id == container_id).first()
        if not container:
            raise HTTPException(status_code=404, detail="Container not found")
        
        container.status = stat.status
        db.commit()
        db.refresh(container)

        return {"Message": "Container status updated successfully", "container": container}
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to update container status")

@router.delete("/v1/container/{container_id}")
def delete_maintenance(container_id: int, db: Session = Depends(get_db)):
    db_container = db.query(Container).filter(Container.id == container_id).first()

    if db_container is None:
        raise HTTPException(status_code=404, detail="Container not found")
    try:
        # Disable foreign key checks
        db.execute(text("SET FOREIGN_KEY_CHECKS = 0"))
        print("foreign key disabled")
        
        # Unlink related records
        db.query(Vehicle).filter(Vehicle.fk_container_id == container_id).update({Vehicle.fk_container_id: None})
        db.commit()

        result = db.query(Container).filter(Container.id == container_id).delete()
        if result == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"container with id {container_id} not found"
            )
        db.commit()
        # Re-enable foreign key checks
        db.execute(text("SET FOREIGN_KEY_CHECKS = 1"))
        print("foreign key enabled")
        db.commit()
        return {"detail": "Container event deleted successfully"}
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error truncating tables: {str(e)}"
        )

@router.post("/v1/upload-status-overseas")
def update_loading_status(qr_code, container_id,  db: Session = Depends(get_db)):
        vehicle = db.query(Vehicle).filter_by(qrcode=qr_code).first()
        if vehicle:
            vehicle.status = "loaded"
            vehicle.fk_container_id = container_id
            db.commit()
            db.refresh(vehicle)
        else:
            sparepart = db.query(Sparepart).filter_by(qrcode=qr_code).first()
            if sparepart:
                sparepart.status = "loaded"
                sparepart.fk_container_id = container_id
                db.commit()
                db.refresh(sparepart)


@router.put("/v1/containers/{container_id}/location")
def update_container_location(container_id: int, location: ContainerLocationUpdate, db: Session = Depends(get_db)):
    container = db.query(Container).filter(Container.id == container_id).first()
    if not container:
        raise HTTPException(status_code=404, detail="Container not found")
    
    container.current_latitude = location.current_latitude
    container.current_longitude = location.current_longitude
    container.tracking_status = location.tracking_status
    db.commit()
    db.refresh(container)
    
    return container



@router.patch("/v1/vehicles_parts_container/update-status")
def update_vehicle_status(update_data: UpdateVehiclePartsStatusContainer, db: Session = Depends(get_db)):
    # Fetch the vehicle from the database
    if update_data.chassis_no:
        data = db.query(Vehicle).filter(Vehicle.chassis_number == update_data.chassis_no).first()
        if not data:
            raise HTTPException(status_code=404, detail="Vehicle not found")

    # Update only the specified fields
    if update_data.status:
        data.status = update_data.status

    # Save the changes
    db.commit()
    db.refresh(data)
    return {
        "status": data.status
    }


@router.patch("/v1/vehicle_container/{veh_id}")
def maintenance(veh_id: int, db: Session = Depends(get_db)):
    db_container = db.query(Vehicle).filter(Vehicle.id == veh_id).first()

    if db_container is None:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    try:
        # Disable foreign key checks
        db.execute(text("SET FOREIGN_KEY_CHECKS = 0"))
        print("foreign key disabled")

        db_container.fk_container_id == ""
        db.commit()
        db.refresh(db_container)

        # Re-enable foreign key checks
        db.execute(text("SET FOREIGN_KEY_CHECKS = 1"))
        print("foreign key enabled")
        db.commit()
        return {"detail": "Vehicle done successfully"}
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error truncating tables: {str(e)}"
        )
