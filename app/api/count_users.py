from fastapi import APIRouter, HTTPException, Depends
from app.db.crud import get_user_by_credentials
from app.helper.authenticate_user import autheticate_user
from app.db.schemas import User, Signin,MonthInput
from sqlalchemy.orm import Session
from app.db.db_setup import get_db
from app.helper.jwt_token import jwt_access_token
from app.db.models import User as ModelUser
import logging
from datetime import datetime
from sqlalchemy import func, and_

router = APIRouter()


@router.get("/v1/count_user_employee")
def report_sales_revenue_by_month(db: Session = Depends(get_db)):
    registered_users = 0
    registered_employees = 0


    try:
        # Total employees
        employees_data = db.query(
            func.count(ModelUser.id).label("total_employee")
        ).filter(ModelUser.side=="admin",
        ).one()

        registered_employees = employees_data.total_employee
        print(registered_employees)

        # Total sales and revenue for spare parts
        customers_data = db.query(
            func.count(ModelUser.id).label("total_customer")
        ).filter(ModelUser.side=="client"
        ).one()

        registered_users = customers_data.total_customer
        print(registered_users)


        retval = {
            "total_employees": registered_employees,
            "total_customers": registered_users
        }
        return {"data": retval}

    except Exception as e:
        logging.error(f"Error counting registered users and employees: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
