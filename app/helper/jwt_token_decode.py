from fastapi import HTTPException
from jose import jwt, JWTError
import json
from dotenv import load_dotenv
import os
import logging
load_dotenv()  # Load environment variables from .env file

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")


def decode_token(token: str):
    try:
        logging.info('trying to decode token and extract the ID from it so it will be used in foreign key')
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        # print(payload)
        sub = payload.get("sub")
        retval = json.loads(sub.replace("'", '"'))
        # print(f'data in decode: {sub_dict}')
        user_id = retval.get("userid")
        # print(f'the user id in new token by refresh: {user_id}')
        logging.info(f'the user ID extracted from token in decode: {user_id}')
        if user_id is None:
            raise HTTPException(status_code=401, detail="Token missing user ID")
        return user_id, retval
    except Exception as e:
        print("In Error Decode")
        print(str(e))
        logging.error('Error occured in jwt_token_decode helper function')
        raise HTTPException(status_code=409, detail=f"Invalid token: {e}")
