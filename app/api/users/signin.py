from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.middleware import SlowAPIMiddleware
from fastapi import APIRouter, HTTPException, Depends, Request
from app.db.crud import get_user_by_credentials, get_user_by_credentials_uid
from app.helper.authenticate_user import autheticate_user
from app.db.schemas import User, Signin, SigninUid
from sqlalchemy.orm import Session
from app.db.db_setup import get_db
from app.helper.jwt_token import jwt_access_token
# import logging


router = APIRouter()

"""*************login by UID*************************"""
# Initialize Limiter with the function to get the client's IP address
limiter = Limiter(key_func=get_remote_address)

# Signin API for entering into the application
@router.post("/v1/user/signinUid")
@limiter.limit("5/minute")
def signin(request: Request, user_data: SigninUid, db: Session = Depends(get_db)):
    print(user_data)
    user_record = get_user_by_credentials_uid(db, user_data.uid)
    print("back from credentails")
    logging.info('Finding if user record exist in DB')
    if user_record is None:
        print("user record is not found")
        logging.error(f'Error user not found: {user_record}')
        raise HTTPException(status_code=404, detail="User not found")
    if user_record.status == False:
        raise HTTPException(status_code=202, detail="Account is Waiting for Admin Approval")
    print("user exists lets check password")
    try:
        logging.info('checking the user credentials if correct than access will be given')
        response = autheticate_user(db,user_record, user_data)

        # Set the user_id in the session
        db.info['id'] = user_record.id  # for the purpose so that it is stored with us in the session later we can use it where ever we have the token of the user we can take out the session id

        return response
    except Exception as e:
        logging.error(f'Error occured in signin: {str(e)}')
        raise HTTPException(status_code=400, detail="Error occured while signing in")