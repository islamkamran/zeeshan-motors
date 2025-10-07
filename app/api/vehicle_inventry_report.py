from fastapi import APIRouter, HTTPException, Depends
from app.db.crud import get_user_by_credentials
from app.helper.authenticate_user import autheticate_user
from app.db.schemas import User, Signin,MonthInput, YearInput
from sqlalchemy.orm import Session
from app.db.db_setup import get_db
from app.helper.jwt_token import jwt_access_token
from app.db.models import Vehicle, VehicleSale, StatusHistory
from datetime import datetime
from sqlalchemy import func, and_
import json
from fastapi.responses import Response


router = APIRouter()
# Signin API for entering into the application


@router.get("/v1/vehicles_report")
def report_vehicles(start_date: str = None, end_date: str = None, db: Session = Depends(get_db)):
    try:
        start_date = datetime.strptime(start_date, "%Y-%m-%d") if start_date else None
        end_date = datetime.strptime(end_date, "%Y-%m-%d") if end_date else None

        # Query total vehicles in inventry count
        total_vehicles = db.query(func.count(Vehicle.id)).scalar()
        print(total_vehicles)

        # Query vehicles categorized by type (Car/Truck/Van etc)
        vehicles_by_type = db.query(Vehicle.type, func.count(Vehicle.id)).group_by(Vehicle.type).all()
        print(vehicles_by_type)

        # Query vehicles added in a specific time frame if both the time frames are avaliable in that case we can take out the data else None
        # added date will be taken out from  vehicle table
        if start_date and end_date:
            vehicles_added = db.query(func.count(Vehicle.id)).filter(
                and_(Vehicle.created_at >= start_date, Vehicle.created_at <= end_date)
            ).scalar()
        else:
            vehicles_added = 0
        print(vehicles_added)

        # Query vehicles sold in a specific time frame if both the time frames are avaliable
        # sold data will be taken out from sold table
        if start_date and end_date:
            vehicles_sold = db.query(func.count(VehicleSale.id)).filter(
                and_(VehicleSale.sold_date >= start_date, VehicleSale.sold_date <= end_date) 
            ).scalar()
        else:
            vehicles_sold = 0

        print(vehicles_sold)

        # Query status of each vehicle like in what status is the car now
        vehicles_status = db.query(Vehicle.status, func.count(Vehicle.id)).group_by(Vehicle.status).all()
        print(vehicles_status)

        # Query frequency of scans
        scan_frequency = db.query(
            StatusHistory.item_id, func.count(StatusHistory.id)
        ).group_by(StatusHistory.item_id).all()
        print(scan_frequency)

        # Query most scanned items
        most_scanned_items = db.query(
            StatusHistory.item_id, func.count(StatusHistory.id).label('scan_count')
        ).group_by(StatusHistory.item_id).order_by(func.count(StatusHistory.id).desc()).limit(10).all()
        print(most_scanned_items)

        # Query average time in inventory
        avg_time_in_inventory = db.query(
            func.avg(func.julianday(VehicleSale.sold_date) - func.julianday(Vehicle.created_at))
        ).filter(Vehicle.id == VehicleSale.fk_vehicle_id).scalar()
        print(avg_time_in_inventory)
        
        retval = {
            "total_vehicles": total_vehicles,
            "vehicles_by_type": dict(vehicles_by_type),
            "vehicles_added_in_time_frame": vehicles_added,
            "vehicles_sold_in_time_frame": vehicles_sold,
            "vehicles_status": dict(vehicles_status),
            "scan_frequency": dict(scan_frequency),
            "most_scanned_items": dict(most_scanned_items),
            "average_time_in_inventory": avg_time_in_inventory
        }
        # this data will be sent to front end developer in DICT format
        return retval

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))




"""******************INVENTORY LIVE AND SOLD COUNT PER MONTH*******************"""
@router.post("/v1/count_inventory_by_month")
def inventory_data_by_month(input_data: MonthInput, db: Session = Depends(get_db)):
    total_data = 0
    sold_data = 0
    live_data = 0

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
        vehicle_live_data = db.query(
            func.count(Vehicle.id).label("live_total")
        ).filter(Vehicle.status=="Instock",
            and_(
                Vehicle.created_at >= start_date,
                Vehicle.created_at < end_date
            )
        ).one()

        live_vehicle = vehicle_live_data.live_total
        print(live_vehicle)

        # Total sales and revenue for vehicles
        vehicle_sold_data = db.query(
            func.count(Vehicle.id).label("sold_total")
        ).filter(Vehicle.status=="Outofstock",
            and_(
                Vehicle.updated_at >= start_date,
                Vehicle.updated_at < end_date
            )
        ).one()

        sold_vehicle = vehicle_sold_data.sold_total
        print(sold_vehicle)
# *******************Total*********************
        live_data = live_vehicle 
        sold_data = sold_vehicle
        total_data = live_data + sold_data
        retval = {
            "total_live": live_data,
            "total_sold": sold_data,
            "total": total_data    
        }
        return {"data": retval}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



"""******************INVENTORY LIVE AND SOLD COUNT PER YEAR AND CATEGORY*******************"""
@router.post("/v1/count_inventory_by_year")
def inventory_data_by_month(input_data: YearInput, db: Session = Depends(get_db)):
    try:
        year = input_data.year
        live_total = []
        sold_total = []

        for month in range(1, 13):  # Loop over all months (1 to 12)
            start_date = datetime(year, month, 1)
            end_date = datetime(year, month + 1, 1) if month < 12 else datetime(year + 1, 1, 1)

            live = 0
            sold = 0

            if input_data.category == "Cars":
                live = db.query(func.count(Vehicle.id)).filter(
                    Vehicle.status == "Instock",
                    and_(Vehicle.created_at >= start_date, Vehicle.created_at < end_date)
                ).scalar()

                sold = db.query(func.count(Vehicle.id)).filter(
                    Vehicle.status == "Outofstock",
                    and_(Vehicle.updated_at >= start_date, Vehicle.updated_at < end_date)
                ).scalar()


            # Append the results to the respective lists
            live_total.append(live)
            sold_total.append(sold)

        retval = [{
                "label":"live",
                "data": live_total,
                "borderColor": "#2ECC71",
                "backgroundColor": "rgba(46, 204, 113, 0.2)",
                "tension": 0.4
            },
            {
                "label":"sold",
                "data": sold_total,
                "borderColor": "#F39C12",
                "backgroundColor": "rgba(243, 156, 18, 0.2)",
                "tension": 0.4,
            }]

        return {"datasets": retval}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

