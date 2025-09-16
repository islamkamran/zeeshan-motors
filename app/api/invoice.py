import csv
from fastapi import APIRouter, HTTPException, Depends, Header, File, UploadFile, Form,status
from sqlalchemy.orm import Session
from app.db.models import *
from app.db.schemas import *
from sqlalchemy import text
from app.db.db_setup import get_db
from app.db.crud import *
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
import json
from reportlab.lib.units import inch
from app.db.crud import get_user_by_credentials
from app.helper.authenticate_user import autheticate_user
from app.helper.jwt_token import jwt_access_token
import logging
from datetime import datetime
from sqlalchemy import func, and_
import os

router = APIRouter()

"""*****************TOTAL INVOICES PER MONTH*******************"""
@router.post("/v1/count_invoices_by_month")
def invoices_data_by_month(input_data: MonthInput, db: Session = Depends(get_db)):
    invoices = 0

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
        invoice_data = db.query(
            func.count(Invoice.id).label("total_invoices")
        ).filter(
            and_(
                Invoice.created_at >= start_date,
                Invoice.created_at < end_date
            )
        ).one()

        invoices = invoice_data.total_invoices
        print(invoices)


        retval = {
            "total_invoices": invoices
        }
        return {"data": retval}

    except Exception as e:
        logging.error(f"Error calculating profit/loss: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Endpoint to generate and download the invoice PDF
@router.get("/v1/generate_invoice/{veh_id}")
def generate_invoice(veh_id: int, db: Session = Depends(get_db)):
    # Fetch vehicle data from the database
    vehicle_data = db.query(Vehicle).filter(Vehicle.id == veh_id).first()

    if vehicle_data is None:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    
    price_data = db.query(Prices).filter(Prices.fk_vehicle_id==veh_id).first()
    if price_data is None:
        print("No Price Found")
        raise HTTPException(status_code=404, detail="Price not found")    

    # Create the invoice PDF
    pdf_filename = create_invoice(veh_id, price_data, vehicle_data)

    # Check if the PDF file was generated and exists
    if not os.path.exists(pdf_filename):
        raise HTTPException(status_code=500, detail="Failed to generate invoice PDF")

    # Return the PDF file as a downloadable response
    return FileResponse(path=pdf_filename, filename=pdf_filename, media_type='application/pdf')


@router.post("/v1/pending_amount_adding")
def balanceamount(data: PendingAmountAdding, db: Session = Depends(get_db)):
    if data.type == "vehicle":
        check_veh = db.query(Vehicle).filter(Vehicle.chassis_number == data.chassis_no).first()
        if check_veh is None:
            raise HTTPException(status_code=404, detail="No Vehicle with this chassis is avaliable in inventory")
        
        check_veh.recieved_amount = check_veh.sold_price
        check_veh.balance_amount = 0.0
        db.commit()
        db.refresh(check_veh)
    
    return {"message":"Balance Amount Recieved"}