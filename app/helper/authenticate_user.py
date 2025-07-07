from fastapi import HTTPException
from passlib.context import CryptContext
from app.helper.jwt_token import jwt_access_token, jwt_refresh_token
import json
from sqlalchemy.orm import Session
from app.db.models import Role
from sqlalchemy.orm import Session



pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def autheticate_user(db: Session,user_record, user_data):
    # I am fetching password directly check it out
    # print(f'user_record inside authenticate_user: {user_record.password}')
    # print(f'user_data inside authenticate_user: {user_data}')
    try:
        # remember the sequence of decrypting of matters !!!!!!!!
        if not verify_password(user_data.password, user_record.password):
            raise HTTPException(status_code=400, detail="Wrong password/ email")
        
        # The reason behind this is if a user dont have rights of rights are missing by anymean the if condition will not allow the retval json so that is why we need an empty condition
        right_read = ""
        right_write = ""
        right_edit = ""
        right_delete = ""
        right_dashboard = ""
        right_container = ""
        right_product = ""
        right_employee_management = ""
        right_reports = ""
        right_invoices = ""
        right_setting = ""
        right_help_center = ""
        right_feed_back = ""
        right_status_permission = ""
        right_generate = ""
        right_overseas_employee = ""
        right_customer_management = ""
        right_customer_management_read = ""
        right_customer_management_write = ""
        right_customer_management_edit = ""
        right_customer_management_delete = ""
        right_auction_management = ""
        right_auction_management_read = ""
        right_auction_management_write = ""
        right_auction_management_edit = ""
        right_auction_management_delete = ""
        right_cms = ""
        
        rights = db.query(Role).filter(Role.name==user_record.role).first()
        if rights is None:
            right_read = "default"
            right_write = "default"
            right_edit = "default"
            right_delete = "default"
            right_dashboard = "default"
            right_container = "default"
            right_product = "default"
            right_employee_management = "default"
            right_reports = "default"
            right_invoices = "default"
            right_setting = "default"
            right_help_center = "default"
            right_feed_back = "default"
            right_status_permission = "default"
            right_generate = "default"
            right_overseas_employee = "default"
            right_customer_management = "default"
            right_customer_management_read = "default"
            right_customer_management_write = "default"
            right_customer_management_edit = "default"
            right_customer_management_delete = "default"
            right_auction_management = "default"
            right_auction_management_read = "default"
            right_auction_management_write = "default"
            right_auction_management_edit = "default"
            right_auction_management_delete = "default"
            right_cms = "default"
            retval = json.dumps({
                "userid": user_record.id,
                "username": user_record.firstname,
                "phonenumber": user_record.phonenumber,
                "email": user_record.email,
                "role": user_record.role,
                "right_read": right_read,
                "right_write": right_write,
                "right_edit": right_edit,
                "right_delete": right_delete,
                "right_dashboard":right_dashboard,
                "right_container":right_container,
                "right_product":right_product,
                "right_employee_management":right_employee_management,
                "right_reports":right_reports,
                "right_invoices":right_invoices,
                "right_setting":right_setting,
                "right_help_center":right_help_center,
                "right_feed_back":right_feed_back,
                "right_status_permission": right_status_permission,
                "right_generate":right_generate,
                "right_overseas_employee":right_overseas_employee,
                "right_customer_management":right_customer_management,
                "right_customer_management_read":right_customer_management_read,
                "right_customer_management_write":right_customer_management_write,
                "right_customer_management_edit":right_customer_management_edit,
                "right_customer_management_delete":right_customer_management_delete,
                "right_auction_management":right_auction_management,
                "right_auction_management_read":right_auction_management_read,
                "right_auction_management_write":right_auction_management_write,
                "right_auction_management_edit":right_auction_management_edit,
                "right_auction_management_delete":right_auction_management_delete,
                "right_cms":right_cms
                })
        else:
        # print("I am here")
            retval = json.dumps({
                "userid": user_record.id,
                "username": user_record.firstname,
                "phonenumber": user_record.phonenumber,
                "email": user_record.email,
                "role": user_record.role,
                "right_read": rights.right_read,
                "right_write": rights.right_write,
                "right_edit": rights.right_edit,
                "right_delete": rights.right_delete,
                "right_dashboard":rights.right_dashboard,
                "right_container":rights.right_container,
                "right_product":rights.right_product,
                "right_employee_management":rights.right_employee_management,
                "right_reports":rights.right_reports,
                "right_invoices":rights.right_invoices,
                "right_setting":rights.right_setting,
                "right_help_center":rights.right_help_center,
                "right_feed_back":rights.right_feed_back,
                "right_status_permission": rights.right_status_permission,
                "right_generate":rights.right_generate,
                "right_overseas_employee":rights.right_overseas_employee,
                "right_customer_management":rights.right_customer_management,
                "right_customer_management_read":rights.right_customer_management_read,
                "right_customer_management_write":rights.right_customer_management_write,
                "right_customer_management_edit":rights.right_customer_management_edit,
                "right_customer_management_delete":rights.right_customer_management_delete,
                "right_auction_management":rights.right_auction_management,
                "right_auction_management_read":rights.right_auction_management_read,
                "right_auction_management_write":rights.right_auction_management_write,
                "right_auction_management_edit":rights.right_auction_management_edit,
                "right_auction_management_delete":rights.right_auction_management_delete,
                "right_cms":rights.right_cms
            })

        if user_record.mfa_enabled == "yes":
            # If MFA is enabled, return a response indicating that MFA verification is needed
            return {"mfa_required": True, "user_id": user_record.id}
        

        return {"access_token": jwt_access_token(retval), "token_type": "bearer", "refresh_token": jwt_refresh_token(retval)}
    except Exception as e:
        return {"error": str(e)}
