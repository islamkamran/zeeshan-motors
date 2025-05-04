from sqlalchemy.orm import Session
from app.db.models import *
from app.db.schemas import *
from app.helper.emails import send_user_details_to_admin,send_user_details_to_client,send_user_details_to_user
import logging



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
        new_user = User(**user_data.dict())
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        logging.info(f'new user registered in DB with the id: {new_user.id}')
        print("user added")
    except Exception as e:
        db.rollback()  # Rollback in case of error
        logging.error(f"Error during database operation: {e}")
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

"""******************SAME CREATE USER BUT FROM ADMINSIDE CREATING CUSTOMER**************"""
def create_user_admin_customer(db: Session, user_data):
    try:
        new_user = User(**user_data.dict())
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        logging.info(f'new user registered in DB with the id: {new_user.id}')
        print("user added")
    except Exception as e:
        db.rollback()  # Rollback in case of error
        logging.error(f"Error during database operation: {e}")
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
        logging.info(f'new user registered in DB with the id: {new_user.id}')
        print("user added")
    except Exception as e:
        db.rollback()  # Rollback in case of error
        logging.error(f"Error during database operation: {e}")
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