from fastapi import APIRouter, HTTPException, Depends, Header
from passlib.context import CryptContext
from app.db.schemas import *
import os
import shutil
from sqlalchemy.orm import Session
from app.db.db_setup import get_db
from app.helper.jwt_token_decode import decode_token
from app.helper.jwt_token import is_token_blacklisted
from app.db.crud import *
from app.helper.password_hashing import hashedpassword
import logging
from fastapi import APIRouter, Depends, HTTPException, Header, UploadFile, File, Request
from app.helper.emails import send_user_details_to_admin,send_user_details_to_client
import random
import csv
# from reportlab.lib.pagesizes import letter
# from reportlab.pdfgen import canvas
from sqlalchemy.sql import func
from sqlalchemy import and_
from fastapi.responses import FileResponse
import uuid
from app.db.models import User as ModelUser


UPLOAD_DIR = "uploads/profile/"  # Ensure this directory exists
EXPORT_DIR = "exports/"  # Directory to save the file


router = APIRouter()


@router.post("/v1/user/admin_signupuid")
def signup(user_data: UidUserAdmin, db: Session = Depends(get_db)):
        # make a random password for the user and a random user id


    # Generate a random 8-digit password
    def generate_password():
        return ''.join(random.choices('0123456789', k=6))
    # Generate a unique UID for each user
    def generate_uid():
        return ''.join(random.choices('0123456789', k=8))
    # Adjusted code
    original_password = generate_password()  # Generate random password
    hashed_password = hashedpassword(original_password)  # Hash the password
    uid = generate_uid()            # Generate unique UID
    logging.info('hashed password is called a seperate helper funtion to create hashed password')
    # password = hashedpassword(password)
    print("here 1")
    data_adding_DB = user_data.model_dump()
    print("here 2")
    data_adding_DB["side"] = "admin"
    data_adding_DB["terms_agreement"] = "Yes"
    data_adding_DB["original_password"] = original_password
    data_adding_DB["password"] = hashed_password
    data_adding_DB["uid"] = uid
    data_adding_DB["mfa_enabled"] = "no"
    data_adding_DB["mfa_secret"] = "none"
    print(data_adding_DB)
    print("data adding DB")
    
    new_user = create_user_admin(db, PublishDataUidAdmin(**data_adding_DB))
    print("user created")
    return {"Message": "Register Successful for User", "id": new_user}


"""***********register customer from admin portal"""
@router.post("/v1/user/admin_signupuid_customer")
def signup(user_data: UidCustomerAdmin, db: Session = Depends(get_db)):
    print(1)
    if not user_data.email:
        user_data.email = None 
        # make a random password for the user and a random user id
    print(f'Email is: {user_data.email}')
    print(2)

    # Generate a random 8-digit password
    def generate_password():
        return ''.join(random.choices('0123456789', k=6))
    # Generate a unique UID for each user
    print(3)
    
    def generate_uid():
        return ''.join(random.choices('0123456789', k=8))
    # Adjusted code
    print(4)

    original_password = generate_password()  # Generate random password
    hashed_password = hashedpassword(original_password)  # Hash the password
    uid = generate_uid()            # Generate unique UID
    # password = hashedpassword(password)
    print(5)
    data_adding_DB = user_data.model_dump()
    print(6)
    data_adding_DB["side"] = "client"
    data_adding_DB["terms_agreement"] = "Yes"
    data_adding_DB["original_password"] = original_password
    data_adding_DB["password"] = hashed_password
    data_adding_DB["uid"] = uid
    data_adding_DB["mfa_enabled"] = "no"
    data_adding_DB["mfa_secret"] = "none"
    print(data_adding_DB)
    print("7")
    
    new_user = create_user_admin_customer(db, PublishDataUidCustomerAdmin(**data_adding_DB))
    print(12)

    print("user created")
    return {"Message": "Register Successful for User", "id": new_user}

"""*********************** UID******************************"""
@router.post("/v1/user/signupuid")
def signup(user_data: UidUser, db: Session = Depends(get_db)):
    logging.info(f'Attempting to register user {user_data.email}')
    try:
        # make a random password for the user and a random user id


        # Generate a random 8-digit password
        def generate_password():
            return ''.join(random.choices('0123456789', k=6))

        # Generate a unique UID for each user
        def generate_uid():
            return ''.join(random.choices('0123456789', k=8))

        # Adjusted code
        original_password = generate_password()  # Generate random password
        hashed_password = hashedpassword(original_password)  # Hash the password
        uid = generate_uid()            # Generate unique UID

        logging.info('hashed password is called a seperate helper funtion to create hashed password')
        # password = hashedpassword(password)
        print("here 1")
        data_adding_DB = user_data.model_dump()
        print("here 2")

        data_adding_DB["original_password"] = original_password
        data_adding_DB["password"] = hashed_password
        data_adding_DB["uid"] = uid
        data_adding_DB["mfa_secret"] = "none"

        print(data_adding_DB)
        print("data adding DB")
        
        new_user = create_user(db, PublishDataUid(**data_adding_DB))
        print("user created")
        # when new user is created then check if user have opt for MFA or NOT
        if new_user:
            return {"Message": "Register Successful", "Message":"Account created successfully, waiting for Admin Approval"}
        else:
            raise HTTPException(status_code=400, detail="Registeration failed")

    except Exception as e:
        raise HTTPException(status_code=409, detail="Error occured while registering, please try again")
    
# ******************************************

"""Update signup"""
@router.put("/v1/user/signup/{userid}")
def signup(userid:int, user_data: SignupUpdateUid, authorization: str = Header(None), db: Session = Depends(get_db)):
    if authorization is None:
        logging.error('The token entered for the user is either wrong or expired')
        raise HTTPException(status_code=401, detail="Unauthorized")
    token = authorization.split(" ")[1] if authorization.startswith("Bearer ") else authorization
    if is_token_blacklisted(token) == True:
        return {'Message': 'Session Expired please Login'}
    user_id, retval = decode_token(token)  # Extracting the user_id as it would be used as foreign Key
    logging.info(f'the user id after decoding: {user_id}')
    print(user_id)

    check_condition = 0 # I will increase this value by 1 if the status is changed else it will stay 0
    new_role = ''
    previous_role = ''
    new_status = ''
    previous_status = ''

    user_profile = db.query(ModelUser).filter(ModelUser.id==userid).first()
    if user_profile is None:
        raise HTTPException(status_code=404, detail="User Not Found")
    previous_role = user_profile.role
    previous_status = user_profile.status
    print(previous_status)
    changer= db.query(ModelUser).filter(ModelUser.id == user_id).first()

    if user_profile is None:
        raise HTTPException(status_code=404, detail="User Not Found")

    for key, value in user_data.dict(exclude_unset=True).items():
        setattr(user_profile, key, value)
    new_role = user_profile.role
    new_status = user_profile.status
    print(new_status)
    if new_role != previous_role:
        if changer.role != "admin":
            raise HTTPException(status_code=400, detail="Only Admin is Allowed to Change Roles and Status")
        print("here")
        db.commit()
        db.refresh(user_profile)
        if new_status != previous_status and new_status == True:
            # db.commit()
            # db.refresh(user_profile)
            notification = Notification(
                fk_user_id=user_id,
                message=f"Status for {user_profile.firstname} has been changed to active by Admin",
                read = False
            )
            db.add(notification)
            db.commit()
            db.refresh(notification)
        elif new_status != previous_status and new_status == False:
            # db.commit()
            # db.refresh(user_profile)
            notification = Notification(
                fk_user_id=user_id,
                message=f"Status for {user_profile.firstname} has been changed to disable by Admin",
                read = False
            )
            db.add(notification)
            db.commit()
            db.refresh(notification)
        print("Sending Email to User Informing about Approval")
        send_user_details_to_client(user_profile.firstname, user_profile.lastname, user_profile.email,user_profile.uid,user_profile.original_password, user_profile.role)
        print("Email Sent to User")
    else:
        print("goes to else")
        db.commit()
        db.refresh(user_profile)
        if new_status != previous_status and new_status == True:
            # db.commit()
            # db.refresh(user_profile)
            notification = Notification(
                fk_user_id=user_id,
                message=f"Status for {user_profile.firstname} has been changed to active by Admin",
                read = False
            )
            db.add(notification)
            db.commit()
            db.refresh(notification)
        elif new_status != previous_status and new_status == False:
            # db.commit()
            # db.refresh(user_profile)
            notification = Notification(
                fk_user_id=user_id,
                message=f"Status for {user_profile.firstname} has been changed to disable by Admin",
                read = False
            )
            db.add(notification)
            db.commit()
            db.refresh(notification)
        # print("Sending Email to User Informing about Approval")
        # send_user_details_to_client(user_profile.firstname, user_profile.lastname, user_profile.email,user_profile.uid,user_profile.original_password, user_profile.role)
        # print("Email Sent to User")

    retval = {
        "data": user_profile
    }
    return retval


"""Read Signup data"""
@router.get("/v1/user/signup")
def signup(authorization: str = Header(None), db: Session = Depends(get_db)):
    if authorization is None:
        logging.error('The token entered for the user is either wrong or expired')
        raise HTTPException(status_code=401, detail="Unauthorized")
    token = authorization.split(" ")[1] if authorization.startswith("Bearer ") else authorization
    if is_token_blacklisted(token) == True:
        return {'Message': 'Session Expired please Login'}
    user_id, retval = decode_token(token)  # Extracting the user_id as it would be used as foreign Key
    logging.info(f'the user id after decoding: {user_id}')
    print(user_id)

    user_profile = db.query(ModelUser).filter(ModelUser.id==user_id).first()
    print(user_profile.firstname)
    if user_profile is None:
        raise HTTPException(status_code=404, detail="User Not Found")

    retval = {
        "data": user_profile
    }
    return retval



"""Profile Image Details"""
# add profile image
@router.post("/v1/profile_image")
def upload_profile_images(files: list[UploadFile] = File(...), authorization: str = Header(None), db: Session = Depends(get_db)):
    if authorization is None:
        logging.error('The token entered for the user is either wrong or expired')
        raise HTTPException(status_code=401, detail="Unauthorized")
    token = authorization.split(" ")[1] if authorization.startswith("Bearer ") else authorization
    logging.info('token have two parts some time writen as token "value of token" or directly "token"')
    user_id, retval = decode_token(token)  # Extracting the user_id as it would be used as foreign Key in the rollout table
    logging.info(f'the user id after decoding: {user_id}')
    print(user_id)
    check_user = db.query(ModelUser).filter(ModelUser.id == user_id).first()
    if not check_user:
        raise HTTPException(status_code=404, detail="User not found")

    # check profile image if already there
    check_profile_image = db.query(Images).filter(Images.fk_user_id==check_user.id).first()
    if check_profile_image:
        raise HTTPException(status_code=409, detail="Profile Image already uploaded go to Edit")

    print(check_user.firstname)
    
    image_paths = []
    # Save files to the uploads directory
    for file in files:
        file.filename = str(check_user.id) + file.filename
        print(file.filename)
        file_location = os.path.join(UPLOAD_DIR, file.filename)
        with open(file_location, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            print(file_location)
        image_paths.append(file_location)
    # Convert list of paths to a comma-separated string
    images_string = ",".join(image_paths)
    print(images_string)
    id_card_images = Images(
        image = images_string,
        fk_user_id = check_user.id
    )
    db.add(id_card_images)
    db.commit()
    db.refresh(id_card_images)
    return {"data": "Profile image uploaded successfully", "image_paths": image_paths}


# get profile image
@router.get("/v1/profile_image")
def personal_details_view_profile(request: Request, authorization: str = Header(None), db: Session = Depends(get_db)):
    if authorization is None:
        logging.error('The token entered for the user is either wrong or expired')
        raise HTTPException(status_code=401, detail="Unauthorized")
    token = authorization.split(" ")[1] if authorization.startswith("Bearer ") else authorization
    logging.info('token have two parts some time writen as token "value of token" or directly "token"')
    user_id, retval = decode_token(token)  # Extracting the user_id as it would be used as foreign Key in the rollout table
    logging.info(f'the user id after decoding: {user_id}')
    print(user_id)
    check_user = db.query(ModelUser).filter(ModelUser.id == user_id).first()
    if not check_user:
        raise HTTPException(status_code=404, detail="User not found")

    # Split the comma-separated string into a list of paths
    files_check = db.query(Images).filter(Images.fk_user_id == check_user.id).first()
    if files_check:
        if files_check.image:
            image_paths = files_check.image.split(",")
            # Construct URLs to access the images
            image_urls = [f"{request.base_url}uploads/profile/{os.path.basename(path)}" for path in image_paths]
        else:
            image_urls = []
        return {"data": image_urls}
    else:
        return "No Profile Image Found"


# edit profile image
@router.put("/v1/profile_image")
def update_profile_image(image: list[UploadFile] = File(None), authorization: str = Header(None), db: Session = Depends(get_db)):
    if authorization is None:
        logging.error('The token entered for the user is either wrong or expired')
        raise HTTPException(status_code=401, detail="Unauthorized")
    token = authorization.split(" ")[1] if authorization.startswith("Bearer ") else authorization
    
    if is_token_blacklisted(token) == True:
        return {'Message': 'Session Expired please Login'}
    
    logging.info('token have two parts some time writen as token "value of token" or directly "token"')
    user_id, retval = decode_token(token)

    logging.info(f'the user id after decoding: {user_id}')
    print(f"user id: {user_id}")

    check_user = db.query(ModelUser).filter(ModelUser.id == user_id).first()
    if not check_user:
        raise HTTPException(status_code=404, detail="User not found")

    image_paths = []

        # Save image files to the uploads directory
    if image is not None:
        for img in image:
            img.filename = str(check_user.id) + img.filename
            print(img.filename)
            file_location = os.path.join(UPLOAD_DIR, img.filename)
            with open(file_location, "wb") as buffer:
                shutil.copyfileobj(img.file, buffer)
            print(file_location)
            image_paths.append(file_location)
        # Convert list of paths to a comma-separated string
    images_string = ",".join(image_paths)   
        
    """check if there are images in the folder already"""
    checkUserImage = db.query(Images).filter(Images.fk_user_id == check_user.id).first()

    if checkUserImage:
        # if checkPartImages.image:            
            # images_string = images_string + "," + checkPartImages.image
        checkUserImage.image = images_string
    else:  
        new_image_record = Images(fk_user_id=check_user.id, image=images_string)
        db.add(new_image_record)
    
    db.commit()
    db.refresh(checkUserImage if checkUserImage else new_image_record)
    return {"Message": "Image/s added successfully", "user_id": check_user.id,"updated_profile": images_string}



# delete profile image
@router.delete("/v1/profile_image")
def vehicles(authorization: str = Header(None), db: Session = Depends(get_db)):
    if authorization is None:
        logging.error('The token entered for the user is either wrong or expired')
        raise HTTPException(status_code=401, detail="Unauthorized")
    token = authorization.split(" ")[1] if authorization.startswith("Bearer ") else authorization
    if is_token_blacklisted(token) == True:
        return {'Message': 'Session Expired please Login'}
    logging.info('token have two parts some time writen as token "value of token" or directly "token"')
    # we have return both the id and the complete data the only purpose is incase of refresh token we need all data in normal case we only need the id as foreign key
    user_id, retval = decode_token(token)  # Extracting the user_id as it would be used as foreign Key in the rollout table
    logging.info(f'the user id after decoding: {user_id}')
    print(f"user id: {user_id}")

    check_user = db.query(ModelUser).filter(ModelUser.id == user_id).first()
    if check_user is None:
        raise HTTPException(status_code=404, detail="User not found")

    checkUserImage = db.query(Images).filter(Images.fk_user_id == check_user.id).first()
    if checkUserImage is None:
        logging.error(f'The user profile image is not found in DB')
        raise HTTPException(status_code=404, detail="Profile Image not found")
    
    # Delete the image files from the filesystem
    image_paths = checkUserImage.image.split(",")
    for image_path in image_paths:
        try:
            if os.path.exists(image_path):
                os.remove(image_path)
                logging.info(f"Deleted image file: {image_path}")
                print(f'deleting image: {image_path}')
            else:
                logging.warning(f"File not found, could not delete: {image_path}")
        except Exception as e:
            logging.error(f"Error deleting file {image_path}: {e}")
    
    db.delete(checkUserImage)
    db.commit()
    
    retval = {
        "data": "Profile Image Deleted Successfully"
    }
    return retval


"""*****All Signup list Crud**************"""
@router.get("/v1/all_signups")
def vehicles(db: Session = Depends(get_db)):
    signups = db.query(ModelUser).filter(ModelUser.side=="admin").all()
    if not signups:
        raise HTTPException(status_code=404, detail="No Signups Found")
    
    retval = [
        {
            "id": signup.id,
            "firstname": signup.firstname,
            "lastname": signup.lastname,
            "email": signup.email,
            "uid": signup.uid,
            "phonenumber": signup.phonenumber,
            "role": signup.role,
            "status": signup.status,
            "side": signup.side,
            "terms_agreement": signup.terms_agreement,
            "mfa_enabled": signup.mfa_enabled,
            "mfa_secret": signup.mfa_secret,
            "created_on": signup.created_at,
            "emirates_id":signup.emirates_id,
            "address":signup.address
        }
        for signup in signups
    ]
    
    retval = {
        "data": retval
    }
    return retval

@router.get("/v1/all_signups_customer")
def vehicles(db: Session = Depends(get_db)):
    signups = db.query(ModelUser).filter(ModelUser.side=="client").all()
    if not signups:
        raise HTTPException(status_code=404, detail="No Signups Found")
    
    retval = [
        {
            "id": signup.id,
            "firstname": signup.firstname,
            "lastname": signup.lastname,
            "email": signup.email,
            "uid": signup.uid,
            "phonenumber": signup.phonenumber,
            "role": signup.role,
            "status": signup.status,
            "side": signup.side,
            "terms_agreement": signup.terms_agreement,
            "mfa_enabled": signup.mfa_enabled,
            "mfa_secret": signup.mfa_secret,
            "created_on": signup.created_at,
            "emirates_id":signup.emirates_id,
            "address":signup.address
        }
        for signup in signups
    ]
    
    retval = {
        "data": retval
    }
    return retval

"""*****Signup by ID**************"""
@router.get("/v1/all_signups/{signup_id}")
def vehicles(signup_id:int, db: Session = Depends(get_db)):
    signup = db.query(ModelUser).filter(ModelUser.id==signup_id).first()
    if not signup:
        raise HTTPException(status_code=404, detail="No Signup Found")
    
    retval = {
            "id": signup.id,
            "firstname": signup.firstname,
            "lastname": signup.lastname,
            "email": signup.email,
            "uid": signup.uid,
            "phonenumber": signup.phonenumber,
            "role": signup.role,
            "status": signup.status,
            "side": signup.side,
            "terms_agreement": signup.terms_agreement,
            "mfa_enabled": signup.mfa_enabled,
            "mfa_secret": signup.mfa_secret,
            "emirates_id":signup.emirates_id,
            "address":signup.address
        }
    
    retval = {
        "data": retval
    }
    return retval


"""************* DOWNLOAD CSV/PDF FILE OF THE INVENTORY RETAILS*****************"""

@router.post("/v1/admin/customers_report/export")
def export_vehicles_inventory_csv(data: CustomerReports, db: Session = Depends(get_db)):

        customers = db.query(ModelUser).filter(ModelUser.role == "customer")
        if not customers:
            raise HTTPException(status_code=404, detail="No customers found")
        # Ensure export directory exists
        if not os.path.exists(EXPORT_DIR):
            os.makedirs(EXPORT_DIR)

        if data.download_type == "csv":
            file_path = os.path.join(EXPORT_DIR, "customer_report.csv")

            # Create CSV file and write data to it
            with open(file_path, mode="w", newline="") as csv_file:
                writer = csv.writer(csv_file)

                writer.writerow(['id', 'firstname', 'lastname', 'email', 'uid','phone number', 'role','status','terms agreement','emirates_id','address'])  # CSV header


                for person in customers:
                    writer.writerow([person.id, person.firstname, person.lastname, person.email, person.uid, person.phonenumber,person.role,person.status,person.terms_agreement,person.emirates_id,person.address])

            # Return file as a download
            return FileResponse(file_path, filename="customer_report.csv", media_type="text/csv")
        
        elif data.download_type == "pdf":
            file_path = os.path.join(EXPORT_DIR, "customer_report.pdf")
            # Create PDF file and write data to it
            c = canvas.Canvas(file_path, pagesize=letter)
            c.setFont("Helvetica", 10)

            # Write header
            c.drawString(50, 750, "Customers Report")
            
            y_position = 710
            headers = ['ID', 'firstname', 'lastname', 'email', 'uid','phonenumber', 'role', 'status', 'terms agreement','emirates_id','address']
            c.drawString(50, y_position, " | ".join(headers))
            y_position -= 20

            for person in customers:
                line = f"{person.id} | {person.firstname} | {person.lastname} | {person.email} | {person.uid} | {person.phonenumber} | {person.role} | {person.status} | {person.terms_agreement} | {person.emirates_id} | {person.address}"
                c.drawString(50, y_position, line)
                y_position -= 20
                if y_position < 50:  # Create a new page if the content overflows
                    c.showPage()
                    c.setFont("Helvetica", 10)
                    y_position = 750

            c.save()
            # Return file as a download
            return FileResponse(file_path, filename="customer_report.pdf", media_type="application/pdf")
