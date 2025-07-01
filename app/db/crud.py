from sqlalchemy.orm import Session
from app.db.models import *
from app.db.models import User as ModelUser
from app.db.schemas import *
from app.helper.emails import send_user_details_to_admin,send_user_details_to_client,send_user_details_to_user
from sqlalchemy import text
from fastapi import APIRouter, HTTPException, Depends, Form, status
import os
import shutil

def format_image_name(filename: str) -> str:
    """Ensure the image name is formatted correctly."""
    base_name, ext = os.path.splitext(filename)
    if not base_name.startswith("cms"):
        return f"cms_{base_name}{ext}"
    return filename

def format_image_fair(filename: str) -> str:
    """Ensure the image name is formatted correctly."""
    base_name, ext = os.path.splitext(filename)
    if not base_name.startswith("fair"):
        return f"fair_{base_name}{ext}"
    return filename

def format_image_deal(filename: str) -> str:
    """Ensure the image name is formatted correctly."""
    base_name, ext = os.path.splitext(filename)
    if not base_name.startswith("deal"):
        return f"deal_{base_name}{ext}"
    return filename

def get_cms_home(db: Session):
    return db.query(CMSHome).first()

def create_cms_home(db: Session, cms_data: CMSHomeCreate):
    print("NOT OK CMS TO OK CMS")
    db_cms = CMSHome(**cms_data)
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


def get_cms_deal(db: Session):
    return db.query(CMSDeal).first()

def create_cms_deal(db: Session, cms_data: CMSDealCreate):
    print("NOT OK DEAL TO OK DEAL")
    db_cms = CMSDeal(**cms_data)
    db.add(db_cms)
    db.commit()
    db.refresh(db_cms)
    return db_cms

def update_cms_deal(db: Session, cms_data: CMSDealUpdate):
    db_cms = get_cms_deal(db)
    if not db_cms:
        print("NOT OK DEAL")
        return create_cms_deal(db, cms_data)
    
    print("OK CMS")
    for field, value in cms_data.dict().items():
        setattr(db_cms, field, value)
    
    db.commit()
    db.refresh(db_cms)
    return db_cms

"""******************SAME CREATE USER BUT FROM ADMINSIDE**************"""
def create_user_admin(db: Session, user_data):
    try:
        new_user =ModelUser(**user_data.dict())
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        print("user added")
    except Exception as e:
        db.rollback()  # Rollback in case of error
        raise
        

    """Create a notification and store in Notification Table"""
    notification = Notification(
        fk_user_id=new_user.id,
        message=f'New employee {new_user.firstname} has been created by Admin',
        read = False
    )
    db.add(notification)
    db.commit()
    print("notification created in Notification Table")
    
    print("Sending Email to User regarding registration")
    send_user_details_to_client(new_user.firstname, new_user.lastname, new_user.email,new_user.uid,new_user.original_password, new_user.role)
    # send_user_details_to_admin(new_user.id,new_user.firstname, new_user.lastname, new_user.email, new_user.role)
    print("Email Sent")
    
    return new_user.id


"""comprehensive vehicle search"""

def search_vehicles_inventory(db: Session, search_criteria: dict):
    print(search_criteria)
    query = db.query(Vehicle).filter(Vehicle.status.in_(["Instock", "Outofstock"]))

    if 'make' in search_criteria and search_criteria['make'] and hasattr(Vehicle, "make"):
        query = query.filter(Vehicle.make.ilike(f"%{search_criteria['make']}%"))        
        # query = query.filter(Vehicle.maker == search_criteria['car_maker'])
    
    if 'model' in search_criteria and search_criteria['model'] and hasattr(Vehicle, "model"):
        query = query.filter(Vehicle.model.ilike(f"%{search_criteria['model']}%"))
        # query = query.filter(Vehicle.model == search_criteria['car_model'])
    
    if 'grade' in search_criteria and search_criteria['grade'] and hasattr(Vehicle, "grade"):
        query = query.filter(Vehicle.grade.ilike(f"%{search_criteria['grade']}%"))
        # query = query.filter(Vehicle.body == search_criteria['body'])

    # if 'year' in search_criteria and search_criteria['year'] and hasattr(Vehicle, "year"):
    #     query = query.filter(Vehicle.year.ilike(f"%{search_criteria['year']}%"))
    #     # query = query.filter(Vehicle.gearbox == search_criteria['gearbox'])

    if 'year' in search_criteria and search_criteria['year'] and hasattr(Vehicle, "year"):
        try:
            input_year = int(search_criteria['year'])
            # Filter the range from input_year - 4 to input_year
            query = query.filter(Vehicle.year.between(input_year - 4, input_year))
        except ValueError:
            # Handle cases where 'year' is not a valid integer
            raise ValueError("Invalid year provided in search criteria.")


    if 'chassis' in search_criteria and search_criteria['chassis'] and hasattr(Vehicle, "chassis"):
        query = query.filter(Vehicle.chassis.ilike(f"%{search_criteria['chassis']}%"))
        # query = query.filter(Vehicle.air_bags == search_criteria['air_bags'])
    
    # if 'mileage' in search_criteria and search_criteria['mileage'] and hasattr(Vehicle, "mileage"):
    #     query = query.filter(Vehicle.mileage.ilike(f"%{search_criteria['mileage']}%"))

    if 'mileage' in search_criteria and search_criteria['mileage'] and hasattr(Vehicle, "mileage"):
        try:
            input_mileage = int(search_criteria['mileage'])
            lower_bound = max(0, input_mileage - 50000)
            upper_bound = input_mileage
    
            # Use SQL functions to clean up the mileage string and filter by range
            query = query.filter(
                func.cast(
                    func.replace(
                        func.replace(func.replace(Vehicle.mileage, ' km', ''), ',', ''), ' ', ''
                    ), Integer
                ).between(lower_bound, upper_bound)
            )
        except ValueError:
            raise ValueError("Invalid mileage provided in search criteria.")


    if 'transmission' in search_criteria and search_criteria['transmission'] and hasattr(Vehicle, "transmission"):
        query = query.filter(Vehicle.transmission.ilike(f"%{search_criteria['transmission']}%"))
        # query = query.filter(Vehicle.color == ilike(search_criteria['color']))

    if 'displacement' in search_criteria and search_criteria['displacement'] and hasattr(Vehicle, "displacement"):
        query = query.filter(Vehicle.displacement.ilike(f"%{search_criteria['displacement']}%"))
        # query = query.filter(Vehicle.fuel == search_criteria['fuel'])

    if 'score' in search_criteria and search_criteria['score'] and hasattr(Vehicle, "score"):
        query = query.filter(Vehicle.score.ilike(f"%{search_criteria['score']}%"))
        # query = query.filter(Vehicle.emission == search_criteria['emission'])

    if 'steer' in search_criteria and search_criteria['steer'] and hasattr(Vehicle, "steer"):
        query = query.filter(Vehicle.steer.ilike(f"%{search_criteria['steer']}%"))
        # query = query.filter(Vehicle.parking_sensors == search_criteria['parking_sensors'])

    if 'color' in search_criteria and search_criteria['color'] and hasattr(Vehicle, "color"):
        query = query.filter(Vehicle.color.ilike(f"%{search_criteria['color']}%"))

    if 'fuel' in search_criteria and search_criteria['fuel'] and hasattr(Vehicle, "fuel"):
        query = query.filter(Vehicle.fuel.ilike(f"%{search_criteria['fuel']}%"))
    
    if 'bodytype' in search_criteria and search_criteria['bodytype'] and hasattr(Vehicle, "body_type"):
        query = query.filter(Vehicle.body_type.ilike(f"%{search_criteria['bodytype']}%"))

    return query.all()


"""Registering new performancebike"""
def register_performancebike(db: Session, user_id, vehicle_id, comfort_data):
    # print(sparepart_data.name)
    new_performancebike = PerformanceFeature(**comfort_data.dict())
    new_performancebike.fk_vehicle_id = vehicle_id

    db.add(new_performancebike)
    db.commit()
    db.refresh(new_performancebike)

    # """Create a notification and store in Notification Table"""
    # notification = Notification(
    #     fk_user_id=user_id, # in future remember this is user ID not sparepart but here is dummy example for now
    #     message=f"A new performance of Vehicle with ID: {vehicle_id} and new_performancebike: {new_performancebike.id} is registered",
    #     read = False
    # )
    # db.add(notification)
    # db.commit()
    # print("here 2 notification created in Notification Table")
    return new_performancebike.id

def register_price(db: Session, veh_id, price_data):
    new_price = Prices(**price_data.dict())
    new_price.fk_vehicle_id = veh_id
    db.add(new_price)
    db.commit()
    db.refresh(new_price)
    print(new_price.id)
    return new_price.id

"""******************SAME CREATE USER BUT FROM ADMINSIDE CREATING CUSTOMER**************"""
def create_user_admin_customer(db: Session, user_data):
    try:
        print(8)

        new_user = ModelUser(**user_data.dict())
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        print("user added")
        print(9)

    except Exception as e:
        db.rollback()  # Rollback in case of error
        raise
        

    """Create a notification and store in Notification Table"""
    notification = Notification(
        fk_user_id=new_user.id,
        message=f"{new_user.firstname} has been added by Admin.",
        read = False
    )
    db.add(notification)
    db.commit()
    print("notification created in Notification Table")
    print(10)

    
    print("Sending Email IGNORING FOR NOW to User regarding registration")
    # send_user_details_to_client(new_user.firstname, new_user.lastname, new_user.email,new_user.uid,new_user.original_password, new_user.role)
    # send_user_details_to_admin(new_user.id,new_user.firstname, new_user.lastname, new_user.email, new_user.role)
    print("Email Sent")
    print(11)
    
    return new_user.id


def create_user(db: Session, user_data):
    try:
        new_user = User(**user_data.dict())
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        print("user added")
    except Exception as e:
        db.rollback()  # Rollback in case of error
        raise
        

    """Create a notification and store in Notification Table"""
    notification = Notification(
        fk_user_id=new_user.id,
        message=f"Request for registration on Admin portal has been received",
        read = False
    )
    db.add(notification)
    db.commit()
    print("notification created in Notification Table")
    
    print("Sending Email to Admin Informing about new User")
    send_user_details_to_admin(new_user.id,new_user.firstname, new_user.lastname, new_user.email,new_user.phonenumber, new_user.role)
    print("Email Sent")

    print("Sending Email to Admin Informing about new User")
    send_user_details_to_user(new_user.firstname, new_user.lastname, new_user.email)
    print("Email Sent")
    
    return new_user

"""Registering a new vehicle"""
def register_vehicle(db: Session, user_id, vehicle_data):

    new_vehicle = Vehicle(**vehicle_data.dict())
    new_vehicle.fk_user_id = user_id
    # print(f'the data in CRUD: {new_vehicle.__dict__}')
    # # new_vehicle.fk_user_id = user_id
    db.add(new_vehicle)
    db.commit()
    db.refresh(new_vehicle)
    print(new_vehicle.id)

    """Create a notification and store in Notification Table"""
    notification = Notification(
        fk_user_id=user_id, # in future remember this is user ID not vehicle but here is dummy example for now
        message=f"{new_vehicle.name} has been added in Inventory by {new_vehicle.uploaded_by}",
        read = False
    )
    db.add(notification)
    db.commit()
    print("notification created in Notification Table")
    return new_vehicle.id

"""Registering new interior"""
def register_interior(db: Session, user_id, vehicle_id, interior_data):
    # print(sparepart_data.name)
    new_interior = VehicleInterior(**interior_data.dict())
    new_interior.fk_vehicle_id = vehicle_id

    db.add(new_interior)
    db.commit()
    db.refresh(new_interior)

    # """Create a notification and store in Notification Table"""
    # notification = Notification(
    #     fk_user_id=user_id, # in future remember this is user ID not sparepart but here is dummy example for now
    #     message=f"A new interior of Vehicle with ID: {vehicle_id} and Interior_id: {new_interior.id} is registered",
    #     read = False
    # )
    # db.add(notification)
    # db.commit()
    # print("here 2 notification created in Notification Table")
    return new_interior.id

"""Updating interior"""
def upd_interior(db: Session, user_id, vehicle_id, interior_data):
    # print(sparepart_data.name)
    new_interior = VehicleInterior(**interior_data.dict())
    new_interior.fk_vehicle_id = vehicle_id

    db.commit()
    db.refresh(new_interior)

    # """Create a notification and store in Notification Table"""
    # notification = Notification(
    #     fk_user_id=user_id, # in future remember this is user ID not sparepart but here is dummy example for now
    #     message=f"A new interior of Vehicle with ID: {vehicle_id} and Interior_id: {new_interior.id} is registered",
    #     read = False
    # )
    # db.add(notification)
    # db.commit()
    # print("here 2 notification created in Notification Table")
    return new_interior.id

"""Registering new safety"""
def register_safety(db: Session, user_id, vehicle_id, safety_data):
    # print(sparepart_data.name)
    new_safety = VehicleSafety(**safety_data.dict())
    new_safety.fk_vehicle_id = vehicle_id

    db.add(new_safety)
    db.commit()
    db.refresh(new_safety)

    # """Create a notification and store in Notification Table"""
    # notification = Notification(
    #     fk_user_id=user_id, # in future remember this is user ID not sparepart but here is dummy example for now
    #     message=f"A new safety of Vehicle with ID: {vehicle_id} and Interior_id: {new_safety.id} is registered",
    #     read = False
    # )
    # db.add(notification)
    # db.commit()
    # print("here 2 notification created in Notification Table")
    return new_safety.id

"""updating safety"""
def upd_safety(db: Session, user_id, vehicle_id, safety_data):
    # print(sparepart_data.name)
    new_safety = VehicleSafety(**safety_data.dict())
    new_safety.fk_vehicle_id = vehicle_id

    db.commit()
    db.refresh(new_safety)

    # """Create a notification and store in Notification Table"""
    # notification = Notification(
    #     fk_user_id=user_id, # in future remember this is user ID not sparepart but here is dummy example for now
    #     message=f"A new safety of Vehicle with ID: {vehicle_id} and Interior_id: {new_safety.id} is registered",
    #     read = False
    # )
    # db.add(notification)
    # db.commit()
    # print("here 2 notification created in Notification Table")
    return new_safety.id


"""Registering new exterior"""
def register_exterior(db: Session, user_id, vehicle_id, exterior_data):
    # print(sparepart_data.name)
    new_exterior = VehicleExterior(**exterior_data.dict())
    new_exterior.fk_vehicle_id = vehicle_id

    db.add(new_exterior)
    db.commit()
    db.refresh(new_exterior)

    # """Create a notification and store in Notification Table"""
    # notification = Notification(
    #     fk_user_id=user_id, # in future remember this is user ID not sparepart but here is dummy example for now
    #     message=f"A new exterior of Vehicle with ID: {vehicle_id} and exterior_id: {new_exterior.id} is registered",
    #     read = False
    # )
    # db.add(notification)
    # db.commit()
    # print("here 2 notification created in Notification Table")
    return new_exterior.id


"""updating exterior"""
def upd_exterior(db: Session, user_id, vehicle_id, exterior_data):
    # print(sparepart_data.name)
    new_exterior = VehicleExterior(**exterior_data.dict())
    new_exterior.fk_vehicle_id = vehicle_id

    db.commit()
    db.refresh(new_exterior)

    # """Create a notification and store in Notification Table"""
    # notification = Notification(
    #     fk_user_id=user_id, # in future remember this is user ID not sparepart but here is dummy example for now
    #     message=f"A new exterior of Vehicle with ID: {vehicle_id} and exterior_id: {new_exterior.id} is registered",
    #     read = False
    # )
    # db.add(notification)
    # db.commit()
    # print("here 2 notification created in Notification Table")
    return new_exterior.id

"""Registering new Comfort"""
def register_comfort(db: Session, user_id, vehicle_id, comfort_data):
    # print(sparepart_data.name)
    new_comfort = VehicleComfortConvenience(**comfort_data.dict())
    new_comfort.fk_vehicle_id = vehicle_id

    db.add(new_comfort)
    db.commit()
    db.refresh(new_comfort)

    # """Create a notification and store in Notification Table"""
    # notification = Notification(
    #     fk_user_id=user_id, # in future remember this is user ID not sparepart but here is dummy example for now
    #     message=f"A new comfort and convenience of Vehicle with ID: {vehicle_id} and comfort_id: {new_comfort.id} is registered",
    #     read = False
    # )
    # db.add(notification)
    # db.commit()
    # print("here 2 notification created in Notification Table")
    return new_comfort.id

"""Registering new safetyfeatures"""
def register_safetyfeatures(db: Session, user_id, vehicle_id, comfort_data):
    # print(sparepart_data.name)
    new_safetyfeatures = SafetyFeatures(**comfort_data.dict())
    new_safetyfeatures.fk_vehicle_id = vehicle_id
 
    db.add(new_safetyfeatures)
    db.commit()
    db.refresh(new_safetyfeatures)

    # """Create a notification and store in Notification Table"""
    # notification = Notification(
    #     fk_user_id=user_id, # in future remember this is user ID not sparepart but here is dummy example for now
    #     message=f"A new performance of Vehicle with ID: {vehicle_id} and new_safetyfeatures: {new_safetyfeatures.id} is registered",
    #     read = False
    # )
    # db.add(notification)
    # db.commit()
    # print("here 2 notification created in Notification Table")
    return new_safetyfeatures.id


"""Registering new comfortusabilitybike"""
def register_comfortusability(db: Session, user_id, vehicle_id, comfort_data):
    # print(sparepart_data.name)
    new_comfortusability = ComfortUsabilityFeatures(**comfort_data.dict())
    new_comfortusability.fk_vehicle_id = vehicle_id
 
    db.add(new_comfortusability)
    db.commit()
    db.refresh(new_comfortusability)

    # """Create a notification and store in Notification Table"""
    # notification = Notification(
    #     fk_user_id=user_id, # in future remember this is user ID not sparepart but here is dummy example for now
    #     message=f"A new performance of Vehicle with ID: {vehicle_id} and new_comfortusability: {new_comfortusability.id} is registered",
    #     read = False
    # )
    # db.add(notification)
    # db.commit()
    # print("here 2 notification created in Notification Table")
    return new_comfortusability.id


"""Registering new safetyfeatures"""
def register_safetyfeatures(db: Session, user_id, vehicle_id, comfort_data):
    # print(sparepart_data.name)
    new_safetyfeatures = SafetyFeatures(**comfort_data.dict())
    new_safetyfeatures.fk_vehicle_id = vehicle_id
 
    db.add(new_safetyfeatures)
    db.commit()
    db.refresh(new_safetyfeatures)

    # """Create a notification and store in Notification Table"""
    # notification = Notification(
    #     fk_user_id=user_id, # in future remember this is user ID not sparepart but here is dummy example for now
    #     message=f"A new performance of Vehicle with ID: {vehicle_id} and new_safetyfeatures: {new_safetyfeatures.id} is registered",
    #     read = False
    # )
    # db.add(notification)
    # db.commit()
    # print("here 2 notification created in Notification Table")
    return new_safetyfeatures.id



def create_make(db: Session, data):
    new_make = VehicleMake(**data.dict())
    db.add(new_make)
    db.commit()
    db.refresh(new_make)
    return new_make.id

def create_model(db: Session, data):
    new_model = VehicleModel(**data.dict())
    db.add(new_model)
    db.commit()
    db.refresh(new_model)
    return new_model.id

def create_body(db: Session, data):
    new_body = VehicleBodyType(**data.dict())
    db.add(new_body)
    db.commit()
    db.refresh(new_body)
    return new_body.id


def create_trans(db: Session, data):
    new_trans = VehicleTransmission(**data.dict())
    db.add(new_trans)
    db.commit()
    db.refresh(new_trans)
    return new_trans.id

def create_clr(db: Session, data):
    new_color = VehicleColor(**data.dict())
    db.add(new_color)
    db.commit()
    db.refresh(new_color)
    return new_color.id

def create_drtype(db: Session, data):
    new_drtype = VehicleDriveType(**data.dict())
    db.add(new_drtype)
    db.commit()
    db.refresh(new_drtype)
    return new_drtype.id

def create_disp(db: Session, data):
    new_displacement = VehicleDisplacement(**data.dict())
    db.add(new_displacement)
    db.commit()
    db.refresh(new_displacement)
    return new_displacement.id


def create_scr(db: Session, data):
    new_score = VehicleScore(**data.dict())
    db.add(new_score)
    db.commit()
    db.refresh(new_score)
    return new_score.id

"""Registering new conveniencefeatures"""
def register_conveniencefeatures(db: Session, user_id, vehicle_id, comfort_data):
    # print(sparepart_data.name)
    new_conveniencefeatures = ConvenienceFeatures(**comfort_data.dict())
    new_conveniencefeatures.fk_vehicle_id = vehicle_id
 
    db.add(new_conveniencefeatures)
    db.commit()
    db.refresh(new_conveniencefeatures)

    # """Create a notification and store in Notification Table"""
    # notification = Notification(
    #     fk_user_id=user_id, # in future remember this is user ID not sparepart but here is dummy example for now
    #     message=f"A new performance of Vehicle with ID: {vehicle_id} and new_conveniencefeatures: {new_conveniencefeatures.id} is registered",
    #     read = False
    # )
    # db.add(notification)
    # db.commit()
    # print("here 2 notification created in Notification Table")
    return new_conveniencefeatures.id


"""Registering new conveniencefeatures"""
def register_conveniencefeatures(db: Session, user_id, vehicle_id, comfort_data):
    # print(sparepart_data.name)
    new_conveniencefeatures = ConvenienceFeatures(**comfort_data.dict())
    new_conveniencefeatures.fk_vehicle_id = vehicle_id
 
    db.add(new_conveniencefeatures)
    db.commit()
    db.refresh(new_conveniencefeatures)

    # """Create a notification and store in Notification Table"""
    # notification = Notification(
    #     fk_user_id=user_id, # in future remember this is user ID not sparepart but here is dummy example for now
    #     message=f"A new performance of Vehicle with ID: {vehicle_id} and new_conveniencefeatures: {new_conveniencefeatures.id} is registered",
    #     read = False
    # )
    # db.add(notification)
    # db.commit()
    # print("here 2 notification created in Notification Table")
    return new_conveniencefeatures.id


"""updating Comfort"""
def upd_comfort(db: Session, user_id, vehicle_id, comfort_data):
    # print(sparepart_data.name)
    new_comfort = VehicleComfortConvenience(**comfort_data.dict())
    new_comfort.fk_vehicle_id = vehicle_id

    db.commit()
    db.refresh(new_comfort)

    # """Create a notification and store in Notification Table"""
    # notification = Notification(
    #     fk_user_id=user_id, # in future remember this is user ID not sparepart but here is dummy example for now
    #     message=f"A new comfort and convenience of Vehicle with ID: {vehicle_id} and comfort_id: {new_comfort.id} is registered",
    #     read = False
    # )
    # db.add(notification)
    # db.commit()
    # print("here 2 notification created in Notification Table")
    return new_comfort.id

"""Registering new dimension"""
def register_dimension(db: Session, user_id, vehicle_id, dimension_data):
    # print(sparepart_data.name)
    new_dimension = DimensionCapicity(**dimension_data.dict())
    new_dimension.fk_vehicle_id = vehicle_id

    db.add(new_dimension)
    db.commit()
    db.refresh(new_dimension)

    # """Create a notification and store in Notification Table"""
    # notification = Notification(
    #     fk_user_id=user_id, # in future remember this is user ID not sparepart but here is dummy example for now
    #     message=f"A new dimension of Vehicle with ID: {vehicle_id} and comfort_id: {new_dimension.id} is registered",
    #     read = False
    # )
    # db.add(notification)
    # db.commit()
    # print("here 2 notification created in Notification Table")
    return new_dimension.id

"""updating dimension"""
def upd_dimension(db: Session, user_id, vehicle_id, dimension_data):
    # print(sparepart_data.name)
    new_dimension = DimensionCapicity(**dimension_data.dict())
    new_dimension.fk_vehicle_id = vehicle_id

    db.commit()
    db.refresh(new_dimension)

    # """Create a notification and store in Notification Table"""
    # notification = Notification(
    #     fk_user_id=user_id, # in future remember this is user ID not sparepart but here is dummy example for now
    #     message=f"A new dimension of Vehicle with ID: {vehicle_id} and comfort_id: {new_dimension.id} is registered",
    #     read = False
    # )
    # db.add(notification)
    # db.commit()
    # print("here 2 notification created in Notification Table")
    return new_dimension.id

"""Registering new engine"""
def register_engine(db: Session, user_id, vehicle_id, engine_data):
    # print(sparepart_data.name)
    new_engine = EngineTransmisison(**engine_data.dict())
    new_engine.fk_vehicle_id = vehicle_id

    db.add(new_engine)
    db.commit()
    db.refresh(new_engine)

    # """Create a notification and store in Notification Table"""
    # notification = Notification(
    #     fk_user_id=user_id, # in future remember this is user ID not sparepart but here is dummy example for now
    #     message=f"A new engine of Vehicle with ID: {vehicle_id} and comfort_id: {new_engine.id} is registered",
    #     read = False
    # )
    # db.add(notification)
    # db.commit()
    # print("here 2 notification created in Notification Table")
    return new_engine.id


"""updating engine"""
def upd_engine(db: Session, user_id, vehicle_id, engine_data):
    # print(sparepart_data.name)
    new_engine = EngineTransmisison(**engine_data.dict())
    new_engine.fk_vehicle_id = vehicle_id

    db.commit()
    db.refresh(new_engine)

    # """Create a notification and store in Notification Table"""
    # notification = Notification(
    #     fk_user_id=user_id, # in future remember this is user ID not sparepart but here is dummy example for now
    #     message=f"A new engine of Vehicle with ID: {vehicle_id} and comfort_id: {new_engine.id} is registered",
    #     read = False
    # )
    # db.add(notification)
    # db.commit()
    # print("here 2 notification created in Notification Table")
    return new_engine.id


# About Us CRUD
def get_about_us(db: Session):
    return db.query(CMSAboutUs).first()

def update_about_us(db: Session, data: dict):
    about_us = get_about_us(db)
    if not about_us:
        about_us = CMSAboutUs(**data)
        db.add(about_us)
    else:
        for key, value in data.items():
            setattr(about_us, key, value)
    db.commit()
    db.refresh(about_us)
    return about_us

# Inventory CRUD 
def get_inventory(db: Session):
    return db.query(CMSInventory).first()

def update_inventory(db: Session, data: dict):
    inventory = get_inventory(db)
    if not inventory:
        inventory = CMSInventory(**data)
        db.add(inventory)
    else:
        for key, value in data.items():
            setattr(inventory, key, value)
    db.commit()
    db.refresh(inventory)
    return inventory

# Product Detail CRUD
def get_product_detail(db: Session):
    return db.query(CMSProductDetail).first()

def update_product_detail(db: Session, data: dict):
    product = get_product_detail(db)
    if not product:
        product = CMSProductDetail(**data)
        db.add(product)
    else:
        for key, value in data.items():
            setattr(product, key, value)
    db.commit()
    db.refresh(product)
    return product

# Contact CRUD
def get_contact(db: Session):
    return db.query(CMSContact).first()

def update_contact(db: Session, data: dict):
    contact = get_contact(db)
    if not contact:
        contact = CMSContact(**data)
        db.add(contact)
    else:
        for key, value in data.items():
            setattr(contact, key, value)
    db.commit()
    db.refresh(contact)
    return contact


def get_user_by_credentials(db: Session, email: str):
    user_record = db.query(ModelUser).filter(ModelUser.email == email).first()
    print(user_record)
    print("in get user by credentail function")
    return user_record

def get_user_by_credentials_uid(db: Session, uid: str):
    user_record = db.query(ModelUser).filter(ModelUser.uid == uid).first()
    print(user_record)
    print("in get user by credentail function")
    return user_record


def create_ccontainer(db: Session, user_id: int, firstname: str, container: ContainerCreate) -> int:
    try:
        print("Creating container with data:", container.dict())
        
        # Create SQLAlchemy model instance
        db_container = Container(
            shipper=container.shipper,
            shipping_company=container.shipping_company,
            bl_number=container.bl_number,
            container_number=container.container_number,
            seal_number=container.seal_number,
            gross_weight=container.gross_weight,
            port_of_discharge=container.port_of_discharge,
            port_of_loading=container.port_of_loading,
            no_of_units=container.no_of_units,
            status=container.status,
            description=container.description,
            eta=container.eta
        )

        db.add(db_container)
        db.commit()
        db.refresh(db_container)

        # Create notification
        notification = Notification(
            fk_user_id=user_id,
            message=f"New Container added: ID {db_container.id} by {firstname}",
            read=False
        )
        db.add(notification)
        db.commit()

        return db_container.id

    except Exception as e:
        db.rollback()
        print(f"Error creating container: {str(e)}")
        raise


def get_all_containers(db: Session):
    return db.query(Container).all()



"""**************************DELETING DATA OF USER*********************"""
def delete_a_user_record(item_id, db: Session):
    try:
        # Disable foreign key checks
        print(1)
        db.execute(text("SET FOREIGN_KEY_CHECKS = 0"))
        print("foreign key disabled")
        print(2)

        employee = db.query(ModelUser).filter(ModelUser.id == item_id).first()
        print(employee)
        if employee is None:
            raise HTTPException(status_code=404, detail="User Not Found")
        store_name = employee.firstname
        print(3)
        print(item_id)
        result = db.query(ModelUser).filter(ModelUser.id == item_id).delete()
        print(result)
        if result == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"item with id {item_id} not found"
            )
        print(4)
        
        notification = Notification(
        fk_user_id=None,
        message=f'{store_name} has been deleted by Admin.',
        read = False
        )
        db.add(notification)
        db.commit()
        db.refresh(notification)
        # db.commit()
        print(5)

        # Re-enable foreign key checks
        db.execute(text("SET FOREIGN_KEY_CHECKS = 1"))
        print("foreign key enabled")
        db.commit()
        return
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting data: {str(e)}"
        )
    

def create_role(db: Session,user_id, created_by, data):
    new_role = Role(**data.dict())
    new_role.created_by = created_by
    db.add(new_role)
    db.commit()
    db.refresh(new_role)

    """Create a notification and store in Notification Table"""
    notification = Notification(
        fk_user_id=user_id,
        message=f'A new role "{new_role.name}" has been created by {created_by}',
        read = False
    )
    db.add(notification)
    db.commit()
    db.refresh(notification)
    print(f'the id: {new_role.name}')
    return new_role.name

def create_invoice(db: Session, invoice):
    db_invoice = Invoice(**invoice.dict())
    db.add(db_invoice)
    db.commit()
    db.refresh(db_invoice)
    """Create a notification and store in Notification Table"""
    notification = Notification(
        fk_user_id=None,
        message=f"Invoice for Products has been generated by Admin",
        read = False
    )
    db.add(notification)
    db.commit()
    return db_invoice.id
