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

# *********************PRICE VEHICLE*********************

@router.post("/v1/generate_invoice")
def generating_invoices(first_name: str = Form(None),last_name: str = Form(None),cell_number: str = Form(None),whatsapp_number: str = Form(None),email_address: str = Form(None),address: str = Form(None),vehicles: str = Form(None), vat: str = Form(None), tax: float = Form(None), sub_total: float = Form(None),total: float = Form(None), db: Session = Depends(get_db)):
    invoice_data = InvoiceData(first_name=first_name,last_name=last_name,cell_number=cell_number,whatsapp_number=whatsapp_number,email_address=email_address,address=address,vat=vat, tax=tax, sub_total=sub_total,total=total)
    invoice_data = invoice_data.dict()
    invoice_id = create_invoice(db, InvoiceData(**invoice_data))
    print("invoice created")
    """************************************vehicles/bikes/trucks******************************************"""

    if vehicles:
        print("in vehicle json")
        vehicles_data = json.loads(vehicles)
        print("json loaded")
    else:
        vehicles_data = []
    
    print("Vehicles data:", vehicles_data)
    for veh in vehicles_data:
        # Access each detail of the vehicle
        chassis_number = veh.get("chassis_number")
 
        # Log the chassis number for debugging
        print(f"Processing chassis number: {chassis_number}")
        existing_vehicle = db.query(Vehicle).filter(Vehicle.chassis_number == chassis_number).first()
        if existing_vehicle:
            # Update container details or any other fields
            existing_vehicle.fk_invoice_id = invoice_id # assuming `invoice id` is available
            db.commit()
            db.refresh(existing_vehicle)
            print(f"Updated invoice for vehicle {chassis_number}")
        else:
            print(f"No vehicle found with chassis number: {chassis_number}")

    """*******data stored in the post of invoice and the repective data is linked now lets take the data backout******"""
    print("returning data to screen")
    customer_invoice_data = db.query(Invoice).filter(Invoice.id == invoice_id).first()

    # Initialize retval as an empty list
    retval = []

    # Taking the data linked to this invoice number
    vehicle_invoice = db.query(Vehicle).filter(Vehicle.fk_invoice_id == invoice_id).all()

    if vehicle_invoice:
        retval.extend([{
            "product_name": veh.name,
            "sold_price": veh.sold_price,
            "chassis_no":veh.chassis_number
        } for veh in vehicle_invoice])

    # Add invoice data to retval
    retval.append({
        "invoice_data": {
            "id":customer_invoice_data.id,
            "first_name": customer_invoice_data.first_name,
            "last_name": customer_invoice_data.last_name,
            "email_address": customer_invoice_data.email_address,
            "address": customer_invoice_data.address,
            "cell_number": customer_invoice_data.cell_number,
            "whatsapp_number": customer_invoice_data.whatsapp_number,
            "tax": customer_invoice_data.tax,
            "sub_total": customer_invoice_data.sub_total,
            "total": customer_invoice_data.total,
            "date":customer_invoice_data.created_at
        }
    })

    return retval


"""********************GET API for listing all the invoices*********************"""
@router.get("/v1/get_generated_invoices")
def getting_invoices(db: Session = Depends(get_db)):    
    invoices = db.query(Invoice).all()

    # Add invoice data to retval
    retval = [{
            "id":invoice.id,
            "first_name": invoice.first_name,
            "last_name": invoice.last_name,
            "email_address": invoice.email_address,
            "address": invoice.address,
            "cell_number": invoice.cell_number,
            "whatsapp_number": invoice.whatsapp_number,
            "tax": invoice.tax,
            "sub_total": invoice.sub_total,
            "total": invoice.total,
            "date":invoice.created_at
        } for invoice in invoices]

    return retval

"""********************GET by id API the invoices*********************"""
@router.get("/v1/generate_invoices/{invoice_id}")
def generating_invoices(invoice_id:int, db: Session = Depends(get_db)):
    customer_invoice_data = db.query(Invoice).filter(Invoice.id == invoice_id).first()

    # Initialize retval as an empty list
    retval = []

    # Taking the data linked to this invoice number
    vehicle_invoice = db.query(Vehicle).filter(Vehicle.fk_invoice_id == invoice_id).all()

    if vehicle_invoice:
        print("vehicle yes")
        retval.extend([{
            "product_name": veh.name,
            "sold_price": veh.sold_price
        } for veh in vehicle_invoice])
    # Add invoice data to retval
    retval.append({
        "invoice_data": {
            "id":customer_invoice_data.id,
            "first_name": customer_invoice_data.first_name,
            "last_name": customer_invoice_data.last_name,
            "email_address": customer_invoice_data.email_address,
            "address": customer_invoice_data.address,
            "cell_number": customer_invoice_data.cell_number,
            "whatsapp_number": customer_invoice_data.whatsapp_number,
            "tax": customer_invoice_data.tax,
            "sub_total": customer_invoice_data.sub_total,
            "total": customer_invoice_data.total,
            "date":customer_invoice_data.created_at
        }
    })

    return retval

"""********************Delete by id API*********************"""
@router.delete("/v1/delete_invoice/{invoice_id}")
def deleting_invoices(invoice_id:int, db: Session = Depends(get_db)):
    customer_invoice_data = db.query(Invoice).filter(Invoice.id == invoice_id).first()
    if customer_invoice_data is None:
        raise HTTPException(status_code=404, detail="Invoice Not Found")
    # Initialize retval as an empty list
    retval = []

    # Taking the data linked to this invoice number
    vehicle_invoice = db.query(Vehicle).filter(Vehicle.fk_invoice_id == invoice_id).all()
    # Disable foreign key checks
    db.execute(text("SET FOREIGN_KEY_CHECKS = 0"))
    print("foreign key disabled")

    if vehicle_invoice:
        for veh in vehicle_invoice:
            veh.fk_invoice_id=None
        db.commit()


    result = db.query(Invoice).filter(Invoice.id == invoice_id).delete()
    if result == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"invoice with id {invoice_id} not found"
        )
    # Re-enable foreign key checks
    db.execute(text("SET FOREIGN_KEY_CHECKS = 1"))
    print("foreign key enabled")
    db.commit()
    return {"message": "deleted successfully"}


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