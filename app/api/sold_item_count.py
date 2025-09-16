from fastapi import APIRouter, HTTPException, Depends
from app.db.crud import get_user_by_credentials
from app.helper.authenticate_user import autheticate_user
from app.db.schemas import MonthInput
from sqlalchemy.orm import Session
from app.db.db_setup import get_db
from app.helper.jwt_token import jwt_access_token
from app.db.models import Vehicle
from datetime import datetime
from sqlalchemy import func, and_

router = APIRouter()


@router.post("/v1/count_item_by_month")
def report_sales_revenue_by_month(input_data: MonthInput, db: Session = Depends(get_db)):
    try:
        # Parse the input month and year
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

        # Debug the date range
        print(f"Start Date: {start_date}, End Date: {end_date}")

        # Query for vehicles with 'Outofstock' status in the specified month and year
        vehicle_sales_data = db.query(
            func.count(Vehicle.id).label("total_sales")
        ).filter(
            Vehicle.status == "Outofstock",
            Vehicle.updated_at >= start_date,
            Vehicle.updated_at < end_date
        ).one()

        vehicle_total = vehicle_sales_data.total_sales
        print(f"Total out-of-stock vehicles for {input_data.month} {input_data.year}: {vehicle_total}")
       


        retval = {
            "sold_vehicles": vehicle_total
        }
        return {"data": retval}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
