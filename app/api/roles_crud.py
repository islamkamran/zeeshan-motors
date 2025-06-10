from fastapi import APIRouter, HTTPException, Depends, Header
from passlib.context import CryptContext
from app.db.schemas import Roles, RoleName
import os
import shutil
from sqlalchemy.orm import Session
from app.db.db_setup import get_db
from app.db.models import User as ModelUser,Role
from app.helper.jwt_token_decode import decode_token
from app.helper.jwt_token import is_token_blacklisted
from app.db.crud import create_role
from app.helper.password_hashing import hashedpassword
import logging
from app.db.models import PersonalDetails, Images
from fastapi import APIRouter, Depends, HTTPException, Header, UploadFile, File, Request


router = APIRouter()


@router.post("/v1/create_roles")
def roles_creating(data: Roles, authorization: str = Header(None), db: Session = Depends(get_db)):

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
    
    check_role = db.query(Role).filter(Role.name==data.name).first()
    if check_role is not None:
        raise HTTPException(status_code=409, detail="Role already Registered")
        
    user = db.query(ModelUser).filter(ModelUser.id==user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="The User registering Role is not Found in DB")
    created_by = user.firstname
    print(created_by)
    
    data = data.model_dump() 
    created_role = create_role(db,user_id, created_by, Roles(**data))
    retval = {
        'data': created_role
    }
    return retval

"""get role by name"""
@router.post("/v1/roles_by_name")
def roles_creating(data: RoleName, db: Session = Depends(get_db)):
    role_by_name = db.query(Role).filter(Role.name==data.name).first()
    if not role_by_name:
        raise HTTPException(status_code=404, detail="Roles not Found")
    
    retval = {
        'data': role_by_name
    }
    return retval

"""get role by id"""
@router.get("/v1/roles_by_id/{role_id}")
def roles_creating(role_id:int, db: Session = Depends(get_db)):
    role_by_id = db.query(Role).filter(Role.id==role_id).first()
    if not role_by_id:
        raise HTTPException(status_code=404, detail="Roles not Found")
    
    retval = {
        'data': role_by_id
    }
    return retval


"""get all role"""
@router.get("/v1/get_all_roles")
def roles_creating(db: Session = Depends(get_db)):
    roles = db.query(Role).all()
    if not roles:
        raise HTTPException(status_code=404, detail="Roles not Found")
    
    retval = [
        {
        "id":role.id,
        "name":role.name,
        "right_read":role.right_read,
        "right_write":role.right_write,
        "right_edit":role.right_edit,
        "right_delete":role.right_delete,
        "created_by":role.created_by,
        "created_at":role.created_at,
        "updated_at":role.updated_at
        }
        for role in roles
    ]
    return {"data":retval}



"""update role"""
@router.put("/v1/create_roles/{role_id}")
def roles_updating(role_id:int, data: Roles, authorization: str = Header(None), db: Session = Depends(get_db)):

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
    
    check_role = db.query(Role).filter(Role.id==role_id).first()

    if check_role is None:
        raise HTTPException(status_code=404, detail="Role Not Found")
        
    user = db.query(ModelUser).filter(ModelUser.id==user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="The User registering Role is not Found in DB")
    created_by = user.firstname
    print(created_by)
    

    for key, value in data.dict(exclude_unset=True).items():
        setattr(check_role, key, value)
    
    check_role.created_by = user.firstname
    db.commit()
    db.refresh(check_role)

    retval = {
        'data': check_role
    }
    return retval

"""delete role by id"""
@router.delete("/v1/roles_by_id/{role_id}")
def roles_creating(role_id:int, db: Session = Depends(get_db)):
    role_by_id = db.query(Role).filter(Role.id==role_id).first()
    if not role_by_id:
        raise HTTPException(status_code=404, detail="Roles not Found")
    
    db.delete(role_by_id)
    db.commit()
    retval = {
        'data': "Deleted successfully"
    }
    return retval
