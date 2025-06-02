import csv
from fastapi.responses import StreamingResponse
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.models import Prices, Vehicle
from app.db.schemas import PricingData
from app.db.db_setup import get_db
from app.db.crud import register_price
import io
import os
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch

router = APIRouter()


# *********************PRICE VEHICLE*********************

@router.post("/v1/add_price_vehicle/{veh_id}")
def adding_price_to_vehicle(veh_id:int, data: PricingData, db: Session = Depends(get_db)):
    vehicle_data = db.query(Vehicle).filter(Vehicle.id == veh_id).first()
    if vehicle_data is None:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    
    check_price_reg = db.query(Prices).filter(Prices.fk_vehicle_id == veh_id).first()
    if check_price_reg:
        return {"message": "Price already entered for the Vehicle, Please edit Price from the Vehicle view page"}
    
    price_data = data.dict()
    price_id = register_price(db, veh_id, PricingData(**price_data))

    total_price = (data.total_fob * data.conversion_rate) + data.cost_till_yard
    print(data.total_fob)

    if total_price <=0.0:
        if data.other_amount>0.0:
            total_price = data.other_amount
        else:
            total_price=0.0
    # Update the vehicle's total_price field
    vehicle_data.total_price = total_price
    db.commit()
    db.refresh(vehicle_data)
    retval = {
        "data": price_id,
        "total_price":total_price
    }
    return retval




@router.put("/v1/update_price_vehicle/{veh_id}")
def adding_price_to_vehicle(veh_id:int, data: PricingData, db: Session = Depends(get_db)):
    vehicle_data = db.query(Vehicle).filter(Vehicle.id == veh_id).first()
    if vehicle_data is None:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    
    check_price_reg = db.query(Prices).filter(Prices.fk_vehicle_id == veh_id).first()
    if check_price_reg is None:
        price_data = data.dict()
        price_id = register_price(db, veh_id, PricingData(**price_data))

        total_price = (data.total_fob * data.conversion_rate) + data.cost_till_yard
        print(data.total_fob)


        if total_price <=0.0:
            if data.other_amount>0.0:
                total_price = data.other_amount
            else:
                total_price=0.0
        
        # Update the vehicle's total_price field
        vehicle_data.total_price = total_price
        db.commit()
        db.refresh(vehicle_data)

        retval = {
            "data": price_id,
            "total_price":total_price
        }
        return retval
    else:

        for key, value in data.model_dump(exclude_unset=True).items():
            setattr(check_price_reg, key, value)
        
        db.commit()
        db.refresh(check_price_reg)

        total_price = (data.total_fob * data.conversion_rate) + data.cost_till_yard
        print(data.total_fob)
    

        if total_price <=0.0:
            if data.other_amount>0.0:
                total_price = data.other_amount
            else:
                total_price=0.0
        # Update the vehicle's total_price field
        vehicle_data.total_price = total_price
        db.commit()
        db.refresh(vehicle_data)
        retval = {
            "data": check_price_reg,
            "total_price": total_price
        }

        return retval
    

@router.get("/v1/prices_vehicle")
def adding_price_to_vehicle(db: Session = Depends(get_db)):
    check_price_reg = db.query(Prices).all()
    if check_price_reg is None:
        raise HTTPException(status_code=404, detail="prices not found")

    retval = {
        "data": check_price_reg
    }
    return retval

@router.get("/v1/prices_vehicle/{veh_id}")
def adding_price_to_vehicle(veh_id:int, db: Session = Depends(get_db)):
    vehicle_data = db.query(Vehicle).filter(Vehicle.id == veh_id).first()
    if vehicle_data is None:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    
    check_price_reg = db.query(Prices).filter(Prices.fk_vehicle_id == veh_id).first()
    if check_price_reg is None:
        raise HTTPException(status_code=404, detail="Vehicle price not found")

    retval = {
        "data": check_price_reg
    }
    return retval

@router.delete("/v1/delete_price_vehicle/{veh_id}")
def adding_price_to_vehicle(veh_id:int,db: Session = Depends(get_db)):
    vehicle_data = db.query(Vehicle).filter(Vehicle.id == veh_id).first()
    if vehicle_data is None:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    
    check_price_reg = db.query(Prices).filter(Prices.fk_vehicle_id == veh_id).first()
    if check_price_reg is None:
        raise HTTPException(status_code=404, detail="Vehicle price not found")
    db.delete(check_price_reg)
    db.commit()

    retval = {
        "data": "Price Deleted"
    }
    return retval



# *********************INVOICE*****************************
def create_invoice(veh_id: int, price_data, vehicle_data):
    # Define the PDF file path
    pdf_filename = f"invoice_{veh_id}.pdf"
    
    # Create a PDF file
    pdf = canvas.Canvas(pdf_filename, pagesize=letter)

    # Add company name and logo
    pdf.drawString(100, 750, "Big Star")
    pdf.drawImage("biag.png", 450, 730, width=2*inch, height=1*inch)

    # Add invoice details
    pdf.drawString(100, 720, f"Invoice Date: 2024-10-22")
    pdf.drawString(100, 700, f"Customer: JanJapan")
    pdf.drawString(100, 680, f"Invoice Number: 12345")

    # Add a table for items
    items = [("Item", "Quantity", "Price"),
             (vehicle_data.make, "1", str(price_data.cost_till_yard))]

    y = 650
    for item in items:
        pdf.drawString(100, y, item[0])
        pdf.drawString(250, y, item[1])
        pdf.drawString(400, y, item[2])
        y -= 20

    # Save the PDF
    pdf.save()

    return pdf_filename

# Endpoint to generate and download the invoice PDF
@router.get("/v1/generate_invoice/{veh_id}")
def generate_invoice(veh_id: int, db: Session = Depends(get_db)):
    # Fetch vehicle data from the database
    vehicle_data = db.query(Vehicle).filter(Vehicle.id == veh_id).first()

    if vehicle_data is None:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    
    price_data = db.query(Prices).filter(Prices.fk_vehicle_id==veh_id).first()
    if price_data is None:
        raise HTTPException(status_code=404, detail="Price not found")    

    # Create the invoice PDF
    pdf_filename = create_invoice(veh_id, price_data, vehicle_data)

    # Check if the PDF file was generated and exists
    if not os.path.exists(pdf_filename):
        raise HTTPException(status_code=500, detail="Failed to generate invoice PDF")

    # Return the PDF file as a downloadable response
    return FileResponse(path=pdf_filename, filename=pdf_filename, media_type='application/pdf')



