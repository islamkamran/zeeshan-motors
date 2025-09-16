from fastapi import APIRouter, HTTPException, Depends
from app.db.crud import get_user_by_credentials
from app.helper.authenticate_user import autheticate_user
from app.db.schemas import User, Signin,MonthInput
from sqlalchemy.orm import Session
from app.db.db_setup import get_db
from app.helper.jwt_token import jwt_access_token
from app.db.models import Vehicle
from datetime import datetime
from sqlalchemy import func, and_
from sqlalchemy.sql import case

router = APIRouter()
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from datetime import datetime
from app.db.db_setup import get_db
from app.db.models import Vehicle

router = APIRouter()


@router.post("/v1/profit_loss_by_month")
def report_sales_revenue_by_month(input_data: MonthInput, db: Session = Depends(get_db)):
    veh_profit = 0
    veh_loss = 0

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

        # Total sales and revenue for vehicles
        vehicle_sales_data = db.query(
            func.count(Vehicle.id).label("total_sales"),
            func.sum(func.coalesce(Vehicle.total_price, 0)).label("total_price"),
            func.sum(func.coalesce(Vehicle.sold_price, 0)).label("total_revenue"),
            func.sum(func.coalesce(Vehicle.balance_amount, 0)).label("hold_revenue"),
            func.sum(
                case(
                    [(Vehicle.status == "Instock", func.coalesce(Vehicle.total_price, 0))],
                    else_=0
                )
            ).label("total_live_inventory_vehicle")
        ).filter(
            and_(
                Vehicle.updated_at >= start_date,
                Vehicle.updated_at < end_date
            )
        ).one()

        vehicle_total_price = vehicle_sales_data.total_price or 0.0
        vehicle_total_revenue = vehicle_sales_data.total_revenue or 0.0
        vehicle_total_hold_revenue = vehicle_sales_data.hold_revenue or 0.0
        vehicle_total_live_inventory = vehicle_sales_data.total_live_inventory_vehicle or 0.0
        print(vehicle_total_live_inventory)
        vehicle_profit = vehicle_total_revenue - vehicle_total_price
        if vehicle_profit >= 0:
            veh_profit = vehicle_profit
        else:
            veh_loss = vehicle_profit

# *********************overall**************************
        revenue_combine = vehicle_total_revenue 
        onhold_combine = vehicle_total_hold_revenue 
        profit_combine = veh_profit
        loss_combine = veh_loss
        combine_live_inventory_worth = vehicle_total_live_inventory
        
        revenue_combine = float(revenue_combine)
        revenue_combine = f"{revenue_combine:,.0f}"
        onhold_combine = float(onhold_combine)
        onhold_combine = f"{onhold_combine:,.0f}"
        profit_combine = float(profit_combine)
        profit_combine = f"{profit_combine:,.0f}"
        loss_combine = float(loss_combine)
        loss_combine = f"{loss_combine:,.0f}"
        combine_live_inventory_worth = float(combine_live_inventory_worth)
        combine_live_inventory_worth = f"{combine_live_inventory_worth:,.0f}"
        retval = {
            "total_revenue": revenue_combine,
            "total_on_hold": onhold_combine,
            "profit": profit_combine,
            "loss": loss_combine,
            "combine_live_inventory_worth": combine_live_inventory_worth
        }
        return {"data": retval}

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
