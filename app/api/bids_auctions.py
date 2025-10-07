import traceback
from fastapi import APIRouter, HTTPException, Depends, Header, File, UploadFile, Form
from app.db.crud import *
from app.helper.authenticate_user import autheticate_user
from app.db.schemas import DeleteBid,ContactDetail,CustomerReports
from app.db.models import  Notification,BidWon,CustomerAuction,CustomerAuctionBids,User
from sqlalchemy.orm import Session
from app.db.db_setup import get_db
from app.helper.jwt_token import jwt_access_token
from app.helper.jwt_token_decode import decode_token
from app.helper.barcode_generator import generate_barcode_vehicle
from app.helper.jwt_token import is_token_blacklisted
import logging
import os
import shutil
import csv
from app.helper.emails import send_quote_to_email
from fastapi.responses import FileResponse
import json
import csv
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from sqlalchemy.sql import func
from sqlalchemy import and_
from fastapi.responses import FileResponse
import uuid


UPLOAD_DIR = "uploads/profile/"  # Ensure this directory exists
EXPORT_DIR = "exports/"  # Directory to save the file


router = APIRouter()

@router.post("/v1/add_to_cart")
def containers_creation(vehicles: str = Form(None), parts: str = Form(None), authorization: str = Header(None), db: Session = Depends(get_db)):
    try:
        bind = db.get_bind()
        if bind is None:
            raise HTTPException(status_code=500, detail="Database session is nout bound to an engine")
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

        """************************************vehicles******************************************"""
        # adding the container number to the vehicles
        if vehicles:
            vehicles_data = json.loads(vehicles)
        else:
            vehicles_data = []
        
        print("Vehicles data:", vehicles_data)

        # update the vehicles with the given chassis number with the respective container id
        for veh in vehicles_data:
            # Access each detail of the vehicle
            chassis_number = veh.get("chassis_number")
            bid_amount = veh.get("bid_amount")

            # Log the chassis number for debugging
            print(f"Processing vehicle with chassis number: {chassis_number}")

            # Example: Update the vehicle's container number based on chassis_number
            existing_vehicle = db.query(Vehicle).filter(Vehicle.chassis_number == chassis_number).first()
            if existing_vehicle:
                # Update container details or any other fields
                check_user_auction = db.query(AuctionBids).filter(AuctionBids.fk_user_id==user_id,AuctionBids.fk_vehicle_id == existing_vehicle.id).first()
                if check_user_auction:
                    check_user_auction.fk_vehicle_id = existing_vehicle.id
                    check_user_auction.amount = bid_amount
                    db.commit()
                    db.refresh(check_user_auction)
                else:
                    auction_data = AuctionBids(
                        fk_user_id=user_id,
                        fk_vehicle_id=existing_vehicle.id,
                        bid_amount=bid_amount
                    )
                    db.add(auction_data)
                    db.commit()
                    db.refresh(auction_data)

            else:
                print(f"No vehicle found with chassis number: {chassis_number}")


        """************************************sparepart******************************************"""
        # adding the container number to the Spareparts
        if parts:
            parts_data = json.loads(parts)
        else:
            parts_data = []
        
        print("Parts data:", parts_data)

        # update the vehicles with the given chassis number with the respective container id
        for part in parts_data:
            # Access each detail of the vehicle
            part_number = part.get("id")
            bid_amount = part.get("bid_amount")

            # Log the part number for debugging
            print(f"Processing sparepart with part number: {part_number}")

            # Example: Update the vehicle's container number based on chassis_number
            existing_part = db.query(Sparepart).filter(Sparepart.id == part_number).first()
            if existing_part:
                # Update container details or any other fields
                check_user_auction = db.query(AuctionBids).filter(AuctionBids.fk_user_id==user_id,AuctionBids.fk_part_id == existing_part.id).first()
                if check_user_auction:
                    check_user_auction.fk_part_id = existing_part.id
                    check_user_auction.amount = bid_amount
                    db.commit()
                    db.refresh(check_user_auction)
                else:
                    auction_data = AuctionBids(
                        fk_user_id=user_id,
                        fk_part_id=existing_part.id,
                        bid_amount=bid_amount
                    )
                    db.add(auction_data)
                    db.commit()
                    db.refresh(auction_data)

            else:
                print(f"No vehicle found with chassis number: {chassis_number}")

        return "Cart Data Added"
    except Exception as e:
        print(traceback.format_exc())
        logging.error(f'Error occured while registering vehicle: {str(e)}')
        raise HTTPException(status_code=409, detail=f' Error: {str(e)}')





"""*******************customer auction bids************************"""

@router.post("/v1/customer_data_to_cart")
def containers_creation(auction_id: int = Form(None), name: str = Form(None), contact: str = Form(None), vehicles: str = Form(None), parts: str = Form(None), db: Session = Depends(get_db)):
    try:
        """************************************vehicles******************************************"""
        print(name)
        print(contact)
        # checking customer data if the customer is already in the system or not
        customer_data = db.query(CustomerAuction).filter(CustomerAuction.phone_number==contact).first()
        if customer_data is None:
            adding_customer = CustomerAuction(
                name=name,
                phone_number=contact
            )
            db.add(adding_customer)
            db.commit()
            db.refresh(adding_customer)
        # adding the container number to the vehicles
            if vehicles:
                vehicles_data = json.loads(vehicles)
            else:
                vehicles_data = []

            print("Vehicles data:", vehicles_data)

            # update the vehicles with the given chassis number with the respective container id
            for veh in vehicles_data:
                # Access each detail of the vehicle
                chassis_number = veh.get("chassis_number")
                bid_amount = veh.get("bid_amount")
                print(f"the amount is: {bid_amount}")

                # Log the chassis number for debugging
                print(f"Processing vehicle with chassis number: {chassis_number}")

                # Example: Update the vehicle's container number based on chassis_number
                existing_vehicle = db.query(Vehicle).filter(Vehicle.chassis_number == chassis_number).first()
                if existing_vehicle:
                    # Update container details or any other fields
                    check_user_auction = db.query(CustomerAuctionBids).filter(CustomerAuctionBids.fk_customer_id==adding_customer.id,CustomerAuctionBids.fk_vehicle_id == existing_vehicle.id).first()
                    if check_user_auction:
                        check_user_auction.fk_vehicle_id = existing_vehicle.id
                        check_user_auction.bid_amount = bid_amount
                        db.commit()
                        db.refresh(check_user_auction)
                    else:
                        auction_data = CustomerAuctionBids(
                            fk_auctionbigstar_id = auction_id,
                            fk_customer_id=adding_customer.id,
                            fk_vehicle_id=existing_vehicle.id,
                            bid_amount=bid_amount
                        )
                        db.add(auction_data)
                        db.commit()
                        db.refresh(auction_data)

                else:
                    print(f"No vehicle found")

            # """************************************sparepart******************************************"""
            # adding the container number to the Spareparts
            if parts:
                parts_data = json.loads(parts)
            else:
                parts_data = []

            print("Parts data:", parts_data)

            # update the vehicles with the given chassis number with the respective container id
            for part in parts_data:
                # Access each detail of the vehicle
                part_number = part.get("id")
                bid_amount = part.get("bid_amount")

                # Log the part number for debugging
                print(f"Processing sparepart with part number: {part_number}")

                # Example: Update the vehicle's container number based on chassis_number
                existing_part = db.query(Sparepart).filter(Sparepart.id == part_number).first()
                if existing_part:
                    # Update container details or any other fields
                    check_user_auction = db.query(CustomerAuctionBids).filter(CustomerAuctionBids.fk_customer_id==adding_customer.id,CustomerAuctionBids.fk_part_id == existing_part.id).first()
                    if check_user_auction:
                        check_user_auction.fk_part_id = existing_part.id
                        check_user_auction.bid_amount = bid_amount
                        db.commit()
                        db.refresh(check_user_auction)
                    else:
                        auction_data = CustomerAuctionBids(
                            fk_auctionbigstar_id = auction_id,
                            fk_customer_id=adding_customer.id,
                            fk_part_id=existing_part.id,
                            bid_amount=bid_amount
                        )
                        db.add(auction_data)
                        db.commit()
                        db.refresh(auction_data)

                else:
                    print(f"No part found")
            return "Cart Data Added"

        else:
            print("customer already registered updating the data")
        # adding the container number to the vehicles
            if vehicles:
                vehicles_data = json.loads(vehicles)
            else:
                vehicles_data = []

            print("Vehicles data:", vehicles_data)

            # update the vehicles with the given chassis number with the respective container id
            for veh in vehicles_data:
                # Access each detail of the vehicle
                chassis_number = veh.get("chassis_number")
                bid_amount = veh.get("bid_amount")
                print(f"the amount is: {bid_amount}")

                # Log the chassis number for debugging
                print(f"Processing vehicle with chassis number: {chassis_number}")

                # Example: Update the vehicle's container number based on chassis_number
                existing_vehicle = db.query(Vehicle).filter(Vehicle.chassis_number == chassis_number).first()
                if existing_vehicle:
                    # Update container details or any other fields
                    check_user_auction = db.query(CustomerAuctionBids).filter(CustomerAuctionBids.fk_customer_id==customer_data.id,CustomerAuctionBids.fk_vehicle_id == existing_vehicle.id).first()
                    if check_user_auction:
                        print("I am already having this vehicle lets update")
                        # check_user_auction.fk_vehicle_id = existing_vehicle.id
                        check_user_auction.bid_amount = bid_amount
                        db.commit()
                        db.refresh(check_user_auction)
                    else:
                        print("I am not having this vehicle lets make one")
                        auction_data = CustomerAuctionBids(
                            fk_auctionbigstar_id = auction_id,
                            fk_customer_id=customer_data.id,
                            fk_vehicle_id=existing_vehicle.id,
                            bid_amount=bid_amount
                        )
                        db.add(auction_data)
                        db.commit()
                        db.refresh(auction_data)

                else:
                    print(f"No vehicle found")
            # """************************************sparepart******************************************"""
            # adding the container number to the Spareparts
            if parts:
                parts_data = json.loads(parts)
            else:
                parts_data = []

            print("Parts data:", parts_data)

            # update the vehicles with the given chassis number with the respective container id
            for part in parts_data:
                # Access each detail of the vehicle
                part_number = part.get("id")
                bid_amount = part.get("bid_amount")

                # Log the part number for debugging
                print(f"Processing sparepart with part number: {part_number}")

                # Example: Update the vehicle's container number based on chassis_number
                existing_part = db.query(Sparepart).filter(Sparepart.id == part_number).first()
                if existing_part:
                    # Update container details or any other fields
                    check_user_auction = db.query(CustomerAuctionBids).filter(CustomerAuctionBids.fk_customer_id==customer_data.id,CustomerAuctionBids.fk_part_id == existing_part.id).first()
                    if check_user_auction:
                        check_user_auction.fk_part_id = existing_part.id
                        check_user_auction.bid_amount = bid_amount
                        db.commit()
                        db.refresh(check_user_auction)
                    else:
                        auction_data = CustomerAuctionBids(
                            fk_auctionbigstar_id = auction_id,
                            fk_customer_id=customer_data.id,
                            fk_part_id=existing_part.id,
                            bid_amount=bid_amount
                        )
                        db.add(auction_data)
                        db.commit()
                        db.refresh(auction_data)

                else:
                    print(f"No part found")

            return "Cart Data updated"
    except Exception as e:
        print(traceback.format_exc())
        logging.error(f'Error occured while registering vehicle: {str(e)}')
        raise HTTPException(status_code=409, detail=f' Error: {str(e)}')



@router.get("/v1/read_customers_data")
def read_container(db: Session = Depends(get_db)):
    customers = db.query(CustomerAuctionBids).all()
    if not customers:
        raise HTTPException(status_code=404, detail="customers not found")

    return {"data": customers}

@router.get("/v1/read_customers")
def read_container(db: Session = Depends(get_db)):
    customers = db.query(CustomerAuction).all()
    if not customers:
        raise HTTPException(status_code=404, detail="customers not found")

    return {"data": customers}

# name contact and the repective produect whch are added to cart will be in oine object



@router.get("/v1/read_customers_with_data")
def read_container(db: Session = Depends(get_db)):
    customers = db.query(CustomerAuction).all()
    if not customers:
        raise HTTPException(status_code=404, detail="customers not found")

    result = []
    for customer in customers:
        customer_data = {
            "id": customer.id,
            "name": customer.name,
            "phone_number": customer.phone_number,
            "bids": [
                {
                    "item_id": bid.id,
                    "auction_id":bid.fk_auctionbigstar_id,
                    "vehicle": db.query(Vehicle.name).filter(Vehicle.id == bid.fk_vehicle_id).scalar() if bid.fk_vehicle_id else None,
                    "vehicle_chassis": db.query(Vehicle.chassis_number).filter(Vehicle.id == bid.fk_vehicle_id).scalar() if bid.fk_vehicle_id else None,
                    "sparepart": db.query(Sparepart.name).filter(Sparepart.id == bid.fk_part_id).scalar() if bid.fk_part_id else None,
                    "sparepart_id": db.query(Sparepart.id).filter(Sparepart.id == bid.fk_part_id).scalar() if bid.fk_part_id else None,
                    "bid_amount": bid.bid_amount,
                    "created_at": bid.created_at
                }
                for bid in customer.bids
            ],
        }
        result.append(customer_data)

    return {"data": result}


@router.get("/v1/read_customers_with_data/{auction_id}")
def read_container(auction_id: int, db: Session = Depends(get_db)):
    # Query customers who have placed bids in the given auction
    customers = (
        db.query(CustomerAuction)
        .join(CustomerAuctionBids, CustomerAuction.id == CustomerAuctionBids.fk_customer_id)
        .filter(CustomerAuctionBids.fk_auctionbigstar_id == auction_id)
        .all()
    )

    if not customers:
        raise HTTPException(status_code=200, detail="No customers found for this auction")

    bids = []
    for customer in customers:
        for bid in customer.bids:
            if bid.fk_auctionbigstar_id == auction_id:  # Ensure bids belong to the given auction
                bids.append({
                    "name": customer.name,
                    "phone_number": customer.phone_number,
                    "item_id": bid.id,
                    "auction_id": bid.fk_auctionbigstar_id,
                    "vehicle": db.query(Vehicle.name).filter(Vehicle.id == bid.fk_vehicle_id).scalar() if bid.fk_vehicle_id else None,
                    "vehicle_chassis": db.query(Vehicle.chassis_number).filter(Vehicle.id == bid.fk_vehicle_id).scalar() if bid.fk_vehicle_id else None,
                    "sparepart": db.query(Sparepart.name).filter(Sparepart.id == bid.fk_part_id).scalar() if bid.fk_part_id else None,
                    "sparepart_id": db.query(Sparepart.id).filter(Sparepart.id == bid.fk_part_id).scalar() if bid.fk_part_id else None,
                    "bid_amount": bid.bid_amount,
                    "created_at": bid.created_at
                })

    return {"bids": bids}


    
@router.get("/v1/count_bids")
def count_bids(db: Session = Depends(get_db)):
    total_bids = db.query(CustomerAuctionBids).count()
    return {"total_bids": total_bids}

@router.get("/v1/read_customer_data_by_contact")
def read_container(contact: str = Form(None), db: Session = Depends(get_db)):
    customer = db.query(CustomerAuction).filter(CustomerAuction.phone_number == contact).first()
    if not customer:
        raise HTTPException(status_code=404, detail="customer not found")

    result = []

    customer_data = {
        "id": customer.id,
        "name": customer.name,
        "phone_number": customer.phone_number,
        "bids": [
            {
                "item_id": bid.id,
                "auction_id":bid.fk_auctionbigstar_id,
                "vehicle": db.query(Vehicle.name).filter(Vehicle.id == bid.fk_vehicle_id).scalar() if bid.fk_vehicle_id else None,
                "vehicle_chassis": db.query(Vehicle.chassis_number).filter(Vehicle.id == bid.fk_vehicle_id).scalar() if bid.fk_vehicle_id else None,
                "sparepart": db.query(Sparepart.name).filter(Sparepart.id == bid.fk_part_id).scalar() if bid.fk_part_id else None,
                "sparepart_id": db.query(Sparepart.id).filter(Sparepart.id == bid.fk_part_id).scalar() if bid.fk_part_id else None,
                "bid_amount": bid.bid_amount,
            }
            for bid in customer.bids
        ],
    }
    result.append(customer_data)

    return {"data": result}


"""************* DOWNLOAD CSV/PDF FILE OF THE CUSTOMERS BIDS*****************"""

@router.post("/v1/admin/customers_data_report/export")
def export_customer_bids_report(data: CustomerReports, db: Session = Depends(get_db)):
    # Fetch customers with their bids and related names
    customers = db.query(CustomerAuction).all()
    if not customers:
        raise HTTPException(status_code=404, detail="No customers found")

    # Ensure export directory exists
    if not os.path.exists(EXPORT_DIR):
        os.makedirs(EXPORT_DIR)

    if data.download_type == "csv":
        file_path = os.path.join(EXPORT_DIR, "customer_bids_report.csv")

        # Create CSV file and write data to it
        with open(file_path, mode="w", newline="") as csv_file:
            writer = csv.writer(csv_file)

            # CSV header
            writer.writerow([
                "Customer ID", "Customer Name", "Phone Number", 
                "Bid Item Type", "Item Name", "Bid Amount"
            ])

            for customer in customers:
                for bid in customer.bids:
                    item_type = (
                        "Vehicle" if bid.fk_vehicle_id else
                        "Truck" if bid.fk_truck_id else
                        "Sparepart" if bid.fk_part_id else
                        "Unknown"
                    )
                    item_name = (
                        db.query(Vehicle.name).filter(Vehicle.id == bid.fk_vehicle_id).scalar() if bid.fk_vehicle_id else
                        db.query(Truck.name).filter(Truck.id == bid.fk_truck_id).scalar() if bid.fk_truck_id else
                        db.query(Sparepart.name).filter(Sparepart.id == bid.fk_part_id).scalar() if bid.fk_part_id else
                        None
                    )
                    writer.writerow([
                        customer.id, customer.name, customer.phone_number,
                        item_type, item_name, bid.bid_amount
                    ])

        # Return file as a download
        return FileResponse(file_path, filename="customer_bids_report.csv", media_type="text/csv")

    elif data.download_type == "pdf":
        file_path = os.path.join(EXPORT_DIR, "customer_bids_report.pdf")
        c = canvas.Canvas(file_path, pagesize=letter)
        c.setFont("Helvetica", 10)

        # Write header
        c.drawString(50, 750, "Customer Bids Report")

        y_position = 710
        headers = ["Customer ID", "Customer Name", "Phone Number", "Bid Item Type", "Item Name", "Bid Amount"]
        c.drawString(50, y_position, " | ".join(headers))
        y_position -= 20

        for customer in customers:
            for bid in customer.bids:
                item_type = (
                    "Vehicle" if bid.fk_vehicle_id else
                    "Truck" if bid.fk_truck_id else
                    "Sparepart" if bid.fk_part_id else
                    "Unknown"
                )
                item_name = (
                    db.query(Vehicle.name).filter(Vehicle.id == bid.fk_vehicle_id).scalar() if bid.fk_vehicle_id else
                    db.query(Truck.name).filter(Truck.id == bid.fk_truck_id).scalar() if bid.fk_truck_id else
                    db.query(Sparepart.name).filter(Sparepart.id == bid.fk_part_id).scalar() if bid.fk_part_id else
                    None
                )
                line = f"{customer.id} | {customer.name} | {customer.phone_number} | {item_type} | {item_name} | {bid.bid_amount}"
                c.drawString(50, y_position, line)
                y_position -= 20
                if y_position < 50:  # Create a new page if content overflows
                    c.showPage()
                    c.setFont("Helvetica", 10)
                    y_position = 750

        c.save()
        # Return file as a download
        return FileResponse(file_path, filename="customer_bids_report.pdf", media_type="application/pdf")



# *********************** contact list drop down *************************
@router.get("/v1/contact_list_dropdown")
def get_contact_list(db: Session = Depends(get_db)):
    customer_details = db.query(User).filter(User.side == "client", User.status == True).all()
    if not customer_details:
        raise HTTPException(status_code=404, detail="No customer found")

    retval = [
        {
            "id": customer.id,
            "phone_number": customer.phonenumber,
            "created_at": customer.created_at,
            "updated_at": customer.updated_at
        }
        for customer in customer_details
    ]
    
    return {"data": retval}


# *********************** Customer Contact Number Details *************************
@router.post("/v1/customer_contact_detail")
def get_chassis_details(data: ContactDetail, db: Session = Depends(get_db)):
    customer_detail = db.query(User).filter(User.phonenumber == data.contact).first()
    if not customer_detail or customer_detail.side == "admin":
        raise HTTPException(status_code=404, detail="No customer details found")
    retval = {
            "id": customer_detail.id,
            "phone_number": customer_detail.phonenumber,
            "name":customer_detail.firstname,
            "created_at": customer_detail.created_at,
            "updated_at": customer_detail.updated_at
        }

    return {"data": retval}



"""*******************Won Bids************************"""

@router.post("/v1/bid_won")
def containers_creation(contact: str = Form(None), chassis: str = Form(None), part_id: str = Form(None), bid_amount: str = Form(None), db: Session = Depends(get_db)):
    try:
        """************************************checking data******************************************"""
        print(contact)
        print(chassis)
        print(bid_amount)
        user_data = db.query(User).filter(User.phonenumber == contact).first()
        if user_data is None:
            raise HTTPException(status_code=404, detail="User not found")
        
        if chassis:
            veh_data = db.query(Vehicle).filter(Vehicle.chassis_number==chassis).first()
            if veh_data is None:
                raise HTTPException(status_code=404, detail="vehicle not found")
            # checking customer data if the customer is already in the system or not

            customer_data = db.query(BidWon).filter(BidWon.fk_user_id==user_data.id,BidWon.fk_vehicle_id==veh_data.id).first()
            if customer_data:
                if customer_data.bid_amount != bid_amount:
                    for_notify = customer_data.bid_amount
                    customer_data.bid_amount=bid_amount
                    db.commit()
                    db.refresh(customer_data)
                    notification = Notification(
                        fk_user_id=None,
                        message=f"{user_data.firstname} has changed the won bid price for {veh_data.name} from {for_notify} to {customer_data.bid_amount}",
                        read = False
                    )
                    db.add(notification)
                    db.commit()
                    db.refresh(notification)
                    return "Bid is Won by this customer for this vehicle and is already registered, the new Price is updated"
                
                return "Bid is Won by this customer for this vehicle and is already registered"
            if customer_data is None:
                adding_customer_won = BidWon(
                    fk_user_id=user_data.id,
                    fk_vehicle_id=veh_data.id,
                    bid_amount = bid_amount
                )
                db.add(adding_customer_won)
                db.commit()
                db.refresh(adding_customer_won)
                """Create a notification and store in Notification Table"""
                notification = Notification(
                    fk_user_id=None,
                    message=f"{user_data.firstname} has won the bid for {veh_data.name}",
                    read = False
                )
                db.add(notification)
                db.commit()
                db.refresh(notification)

        if part_id:
            part_data = db.query(Sparepart).filter(Sparepart.id==part_id).first()
            if part_data is None:
                raise HTTPException(status_code=404, detail="part not found")
            # checking customer data if the customer is already in the system or not
            
            customer_data = db.query(BidWon).filter(BidWon.fk_user_id==user_data.id,BidWon.fk_part_id==part_data.id).first()
            if customer_data:
                if customer_data.bid_amount != bid_amount:
                    for_notify = customer_data.bid_amount
                    customer_data.bid_amount=bid_amount
                    db.commit()
                    db.refresh(customer_data)
                    notification = Notification(
                        fk_user_id=None,
                        message=f"{user_data.firstname} has changed the won bid price for {part_data.name} from {for_notify} to {customer_data.bid_amount}",
                        read = False
                    )
                    db.add(notification)
                    db.commit()
                    db.refresh(notification)
                    return "Bid is Won by this customer for this vehicle and is already registered, the new Price is updated"

                return "Bid is Won by this customer for this Sparepart and is already registered"
            if customer_data is None:
                adding_customer_won = BidWon(
                    fk_user_id=user_data.id,
                    fk_part_id=part_data.id,
                    bid_amount = bid_amount
                )
                db.add(adding_customer_won)
                db.commit()
                db.refresh(adding_customer_won)
                """Create a notification and store in Notification Table"""
                notification = Notification(
                    fk_user_id=None,
                    message=f"{user_data.firstname} has won the bid for {part_data.name}",
                    read = False
                )
                db.add(notification)
                db.commit()
                db.refresh(notification)


        return f"Bid Won Registered for {user_data.firstname}"
    except Exception as e:
        print(traceback.format_exc())
        logging.error(f'Error occured while registering Bid Won: {str(e)}')
        raise HTTPException(status_code=409, detail=f' Error: {str(e)}')


"""*********************get bid data ************************"""
@router.get("/v1/bid_won/{user_id}")
def get_bids_won(user_id: int, db: Session = Depends(get_db)):
    try:
        # Query BidWon table to fetch all bids won by the user, including vehicles and spare parts
        customer_data = (
            db.query(BidWon, Vehicle, Sparepart)
            .join(Vehicle, Vehicle.id == BidWon.fk_vehicle_id, isouter=True)
            .join(Sparepart, Sparepart.id == BidWon.fk_part_id, isouter=True)
            .filter(BidWon.fk_user_id == user_id)
            .all()
        )

        if not customer_data:
            raise HTTPException(status_code=404, detail="No Bids Won Found For this User")
        result = []
        for bid, vehicle, sparepart in customer_data:
            bid.bid_amount = float(bid.bid_amount)

            bid_data = {
                "bid_id": bid.id,
                "bid_amount": bid.bid_amount,
                "date": bid.created_at,
            }
        
            if vehicle and vehicle.chassis_number and vehicle.name:
                bid_data.update({
                    "product_id": bid.fk_vehicle_id,
                    "vehicle_id": bid.fk_vehicle_id,
                    "chassis_no": vehicle.chassis_number,
                    "vehicle_name": vehicle.name,
                    "sold_price":vehicle.sold_price,
                    "recieved_amount":vehicle.recieved_amount,
                    "balance_amount":vehicle.balance_amount

                })
        
            if sparepart and sparepart.name:
                bid_data.update({
                    "product_id": bid.fk_part_id,
                    "part_id": bid.fk_part_id,
                    "part_name": sparepart.name,
                    "sold_price":sparepart.sold_price,
                    "recieved_amount":sparepart.recieved_amount,
                    "balance_amount":sparepart.balance_amount
                })
        
            result.append(bid_data)

        return {"user_id": user_id, "bids_won": result}
    except Exception as e:
        logging.error(f"Error occurred while fetching bids won: {str(e)}")
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")


"""*********************Delete bid data ************************"""
@router.delete("/v1/delete_bid_won/{user_id}")
def get_bids_won(user_id:int, data: DeleteBid, db: Session = Depends(get_db)):
    try:
        print(user_id)
        print(data.chassis_no)
        print(data.part_id)

        check_user = db.query(User).filter(User.id == user_id).first()
        if check_user is None:
            raise HTTPException(status_code=404, detail="User not Found")

        # Chassis Number
        if data.chassis_no:
            veh_data = db.query(Vehicle).filter(Vehicle.chassis_number == data.chassis_no).first()
            if veh_data is None:
                raise HTTPException(status_code=404, detail="Vehicle Not Found")
            
            # Deleting the Bid Won by the user 
            check_bid_won = db.query(BidWon).filter(BidWon.fk_vehicle_id == veh_data.id).first()
            if check_bid_won is None:
                raise HTTPException(status_code=404, detail="No such vehicle for bidwon found")
            db.delete(check_bid_won)
            db.commit()

            # Deleting the Auciton entry for the user but before take out the auction entry of customer
            auction_entry = db.query(CustomerAuction).filter(CustomerAuction.phone_number==check_user.phonenumber).first()
            if auction_entry is None:
                raise HTTPException(status_code=404, detail="No Auction Entry for this User")
            check_auction_bid = db.query(CustomerAuctionBids).filter(CustomerAuctionBids.fk_customer_id == auction_entry.id, CustomerAuctionBids.fk_vehicle_id == veh_data.id).first()
            if check_auction_bid is None:
                raise HTTPException(status_code=404, detail="No bid found for this vehicle")
            db.delete(check_auction_bid)
            db.commit()

        # Part Number
        if data.part_id:
            part_data = db.query(Sparepart).filter(Sparepart.id == data.part_id).first()
            if part_data is None:
                raise HTTPException(status_code=404, detail="Sparepart Not Found")
            
            # Deleting the Bid Won by the user 
            check_bid_won = db.query(BidWon).filter(BidWon.fk_part_id == part_data.id).first()
            if check_bid_won is None:
                raise HTTPException(status_code=404, detail="No such Sparepart for bidwon found")
            db.delete(check_bid_won)
            db.commit()

            # Deleting the Auciton entry for the user but before take out the auction entry of customer
            auction_entry = db.query(CustomerAuction).filter(CustomerAuction.phone_number==check_user.phonenumber).first()
            if auction_entry is None:
                raise HTTPException(status_code=404, detail="No Auction Entry for this User")
            check_auction_bid = db.query(CustomerAuctionBids).filter(CustomerAuctionBids.fk_customer_id == auction_entry.id, CustomerAuctionBids.fk_part_id == part_data.id).first()
            if check_auction_bid is None:
                raise HTTPException(status_code=404, detail="No bid found for this Sparepart")
            db.delete(check_auction_bid)
            db.commit()

        return "Bid Won and Auction Entry Deleted for the User" 
    except Exception as e:
        logging.error(f"Error occurred while bid delete: {str(e)}")
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
