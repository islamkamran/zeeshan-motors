from sqlalchemy.orm import Session
from app.db.models import *
from app.db.models import User as ModelUser
from app.db.schemas import *
from app.helper.emails import send_user_details_to_admin,send_user_details_to_client,send_user_details_to_user



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
        message=f"{new_user.firstname} has been added by Admin.",
        read = False
    )
    db.add(notification)
    db.commit()
    print("notification created in Notification Table")
    
    print("Sending Email IGNORING FOR NOW to User regarding registration")
    # send_user_details_to_client(new_user.firstname, new_user.lastname, new_user.email,new_user.uid,new_user.original_password, new_user.role)
    # send_user_details_to_admin(new_user.id,new_user.firstname, new_user.lastname, new_user.email, new_user.role)
    print("Email Sent")
    
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
