import traceback
from fastapi import APIRouter, HTTPException, Depends, Form
from sqlalchemy.orm import Session
from app.db.db_setup import get_db
from app.db.schemas import *
from app.db.models import *
from app.db.crud import *
from fastapi.responses import FileResponse
import random
import csv
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from sqlalchemy.sql import func
from sqlalchemy import and_
from fastapi.responses import FileResponse
import os
from app.helper.password_hashing import hashedpassword


UPLOAD_DIR = "uploads/profile/"  # Ensure this directory exists
EXPORT_DIR = "exports/"  # Directory to save the file

router = APIRouter()

@router.post("/v1/customers")
def create_customer(customer: CustomerCreate, db: Session = Depends(get_db)):
    try:
        db_customer = Customer(**customer.model_dump())
        db.add(db_customer)
        db.commit()
        db.refresh(db_customer)
        return db_customer
    except Exception as e:
        return str(e)


@router.put("/v1/customers/{customer_id}")
def create_customer(customer_id: int, customer: CustomerCreate, db: Session = Depends(get_db)):
    try:
        customer_data = db.query(Customer).filter(Customer.id == customer_id).first()
        if not customer_data:
            raise HTTPException(status_code=404, detail=f"Customer with ID {customer_id} not found")
        
        customer_data.name = customer_data.name
        customer_data.phone_number = customer_data.phone_number
        customer_data.email = customer_data.email

        # Commit changes to the database
        db.commit()

        return {"detail": f"Customer with ID {customer_id} updated successfully"}     
    except Exception as e:
        return str(e)

@router.delete("/v1/customers/{customer_id}")
def delete_customer(customer_id: int, db: Session = Depends(get_db)):
    try:
        existing_customer = db.query(Customer).filter(Customer.id == customer_id).first()

        if not existing_customer:
            raise HTTPException(status_code=404, detail=f"Customer with ID {customer_id} not found")

        # Delete the customer
        db.delete(existing_customer)
        db.commit()

        return {"detail": f"Customer with ID {customer_id} deleted successfully"}

    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/v1/customers")
def get_customer(db: Session = Depends(get_db)):
    try:
        customers = db.query(Customer).all()
        if not customers:
            raise HTTPException(status_code=404, detail="Customers not found")
        return customers
    except Exception as e:
        return str(e)
    

@router.get("/v1/customers/{customer_id}")
def create_customer(customer_id: int, db: Session = Depends(get_db)):
    try:
        customer_data = db.query(Customer).filter(Customer.id == customer_id).first()
        if not customer_data:
            raise HTTPException(status_code=404, detail=f"Customer with ID {customer_id} not found")
        
        return {"detail": customer_data}     
    except Exception as e:
        return str(e)
    


@router.get("/v1/export_to_excel")
def export_to_excel(db: Session = Depends(get_db)):
    try:
        items = db.query(Item).all()
        if not items:
            raise HTTPException(status_code=404, detail="No data to export")

        # Convert to pandas DataFrame
        df = pd.DataFrame([{
            'ID': item.id,
            'Item Name': item.item_name,
            'Chassis Number': item.chassis_number,
            'Offer Price': item.offer_price,
            'Status': item.status,
            'Created At': item.created_at,
            'Updated At': item.updated_at,
        } for item in items])

        # Save to Excel file
        file_path = 'exported_items_file.xlsx'
        df.to_excel(file_path, index=False)

        return FileResponse(file_path, media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', filename='exported_data.xlsx')

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Export failed: {str(e)}")


@router.put("/v1/finalize_sale/{item_id}")
def finalize_sale(item_id: int, status_update: StatusUpdate, db: Session = Depends(get_db)):
    try:
        # Fetch the item
        item = db.query(Item).filter(Item.id == item_id).first()
        if not item:
            raise HTTPException(status_code=404, detail="Item not found")
        
        # Update the item status to 'Sold'
        item.status = status_update.new_status
        db.commit()

        # Send a follow-up WhatsApp message BUT WE NEED SUBSCRIPTION FIRST
        # follow_up_message = f"Thank you for your purchase! The item '{item.item_name}' has been marked as Sold."
        # send_whatsapp_message(item.transaction.customer.phone_number, follow_up_message)

        return {"message": "Item status updated and follow-up message sent."}
    
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to finalize sale")



@router.get("/v1/items/{item_id}/status")
def update_item_status(item_id: int, db: Session = Depends(get_db)):
    try:

        item = db.query(Item).filter(Item.id == item_id).first()
        if not item:
            raise HTTPException(status_code=404, detail="Item not found")

        retval = {
            "item id": item.id,
            "item name": item.item_name,
            "item type": item.item_type,
            "item status": item.status
        }

        # Send initial WhatsApp reservation message
        # reservation_message = f"Your item '{item.item_name}' has a status '{item.status}'."
        # send_whatsapp_message(item.transaction.customer.phone_number, reservation_message)


        return retval
    except:
        raise HTTPException(status_code=500, detail="Failed to retrive status of the item")



@router.post("/v1/items")
def add_item(item: ItemCreate, db: Session = Depends(get_db)):
    try:
        db_item = Item(**item.model_dump())
        db.add(db_item)
        db.commit()
        db.refresh(db_item)
        return db_item
    except Exception as e:
        return str(e)


@router.get("/v1/items/{item_id}")
def get_item(item_id: int, db: Session = Depends(get_db)):
    try:
        item = db.query(Item).filter(Item.id == item_id).first()
        if not item:
            raise HTTPException(status_code=404, detail="Item not found")
        return item
    except Exception as e:
        return str(e)
    
@router.get("/v1/items")
def get_item(db: Session = Depends(get_db)):
    try:
        item = db.query(Item).all()
        if not item:
            raise HTTPException(status_code=404, detail="Item not found")
        return item
    except Exception as e:
        return str(e)
    
@router.put("/v1/items/{item_id}")
def get_item(item_id: int, item: ItemCreate, db: Session = Depends(get_db)):
    try:
        item_data = db.query(Item).filter(Item.id == item_id).first()
        if not item_data:
            raise HTTPException(status_code=404, detail="Item not found")
        
        item_data = Item(**item.model_dump())
        db.commit()
        
        return {"message":"Data updated for Item", "Item":item_data}
    except Exception as e:
        return str(e)
    

@router.delete("/v1/items/{item_id}")
def get_item(item_id: int, db: Session = Depends(get_db)):
    try:
        item_data = db.query(Item).filter(Item.id == item_id).first()
        if not item_data:
            raise HTTPException(status_code=404, detail="Item not found")
        
        db.delete(item_data)
        db.commit()
        
        return {f"Message":"deleted data for item with id {item_id}"}
    except Exception as e:
        return str(e)


@router.post("/v1/reserve_item")
def reserve_item(item_data: ItemCreate, db: Session = Depends(get_db)):
    try:
        # Create a new item with status "Reserved"
        item = Item(**item_data.model_dump())
        db.add(item)
        db.commit()

        # Send initial WhatsApp reservation message
        # reservation_message = f"Your item '{item.item_name}' has been reserved."
        # send_whatsapp_message(item.transaction.customer.phone_number, reservation_message)

        return {"message": "Item reserved and reservation message sent."}
    
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to reserve item")


@router.post("/v1/item/search")
def search_records(search_query: SearchQuery, db: Session = Depends(get_db)):
    """
    Search for customers, items, or transactions based on phone number,
    vehicle name (assuming 'item_name' represents vehicle names), or chassis number.

    Raises:
        HTTPException: 404 if no matching records are found.
    """
    try:
        query = search_query.query_to_search
        customer_results = db.query(Customer).filter(
            or_(
                Customer.phone_number.ilike(f"%{query}%"),  # Case-insensitive search for phone number
            )
        ).all()
        item_results = db.query(Item).filter(
            or_(
                Item.item_name.ilike(f"%{query}%"),
                Item.chassis_number.ilike(f"%{query}%"),
            )
        ).all()
        
        results = {
            "customers": customer_results,
            "items": item_results,
        }

        if not (customer_results or item_results):
            raise HTTPException(status_code=404, detail="No matching records found")

        return results

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")


@router.post("/v1/item/universal_search")
def universal_search(search_query: SearchQuery, db: Session = Depends(get_db)):
    """
    Perform a universal search across various fields in customers, items,
    and transactions (assuming you have a Transaction model).

    Raises:
        HTTPException: 404 if no matching records are found.
    """
    try:
        query = search_query.query_to_search
        
        customer_results = db.query(Customer).filter(
            or_(
                Customer.phone_number.ilike(f"%{query}%"),  # Case-insensitive search for phone number
                Customer.email.ilike(f"%{query}%"),  # Case-insensitive search for email
            )
        ).all()

        item_results = db.query(Item).filter(
            or_(
                Item.item_name.ilike(f"%{query}%"),
                Item.chassis_number.ilike(f"%{query}%"),
                Item.item_type.ilike(f"%{query}%"),
                Item.notes.ilike(f"%{query}%"),
                Item.status.ilike(f"%{query}%"),
                Item.category.ilike(f"%{query}%")
            )
        ).all()

        results = {
            "customers": customer_results,
            "items": item_results,
        }

        if not results:
            raise HTTPException(status_code=404, detail="No matching records found for your search")

        return results

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")


@router.post("/v1/item/filter_by_price")
def filter_by_price(search_query: SearchPrice, db: Session = Depends(get_db)):
    """
    Filter items by offer price range (low to high or high to low).

    Raises:
        HTTPException: 404 if no items are found within the specified price range.
    """
    try:
        results = db.query(Item).filter(
            Item.offer_price >= search_query.min_price,
            Item.offer_price <= search_query.max_price
        ).order_by(Item.offer_price).all()

        if not results:
            raise HTTPException(status_code=404, detail="No items found within the specified price range")

        return results

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Filtering failed: {str(e)}")
    



@router.put("/v1/items/{item_id}/status")
def update_item_status(item_id: int, status: StatusUpdate, db: Session = Depends(get_db)):
    item = db.query(Item).filter(Item.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    
    item.status = status.new_status
    db.commit()
    db.refresh(item)

    # Trigger any follow-up actions here, such as sending a confirmation message

    return {"Message": "Status updated successfully", "Item": item}



@router.post("/v1/transactions")
def save_transaction(transaction: TransactionCreate, db: Session = Depends(get_db)):
    try:
        db_transaction = Transaction(**transaction.model_dump())
        db.add(db_transaction)
        db.commit()
        db.refresh(db_transaction)
        return db_transaction
    except Exception as e:
        return str(e)


@router.get("/v1/transactions/{transaction_id}")
def get_transaction(transaction_id: int, db: Session = Depends(get_db)):
    try:
        transaction = db.query(Transaction).filter(Transaction.id == transaction_id).first()
        if not transaction:
            raise HTTPException(status_code=404, detail="Transaction not found")
        return transaction
    except Exception as e:
        return str(e)


@router.get("/v1/search_customer")
def search_items(data: CustomerSearch, db: Session = Depends(get_db)):
    # Search Query for User
    user_query = db.query(User)
    if data.username:
        user_query = user_query.filter(User.username.ilike(f"%{data.username}%"))
    if data.phonenumber:
        user_query = user_query.filter(User.phonenumber == data.phonenumber)
    if data.user_id:
        user_query = user_query.filter(User.id == data.user_id)

    users = user_query.all()
    print(f'the user data: {users.__dict__}')

    # Search Query for Vehicle
    vehicle_query = db.query(Vehicle)
    if data.vehicle_name:
        vehicle_query = vehicle_query.filter(Vehicle.name.ilike(f"%{data.vehicle_name}%"))
    if data.chassis_number:
        vehicle_query = vehicle_query.filter(Vehicle.chassis_number.ilike(f"%{data.chassis_number}%"))
    if data.vehicle_id:
        vehicle_query = vehicle_query.filter(Vehicle.id == data.vehicle_id)

    vehicles = vehicle_query.all()
    print(f'the user data: {vehicles.__dict__}')


    # Search Offers made by customers
    purchase_query = db.query(Purchase).join(User).join(Vehicle)
    if data.user_id:
        purchase_query = purchase_query.filter(Purchase.fk_user_id == data.user_id)
    
    offers = purchase_query.all()
    print(f'the user data: {offers.__dict__}')


    # Combine results
    search_results = {
        "users": users,
        "vehicles": vehicles,
        "offers": offers
    }
    return search_results


@router.get("/v1/all_signups_customer")
def vehicles(db: Session = Depends(get_db)):
    signups = db.query(User).filter(User.side=="client").all()
    if not signups:
        raise HTTPException(status_code=404, detail="No Signups Found")
    
    retval = [
        {
            "id": signup.id,
            "firstname": signup.firstname,
            "lastname": signup.lastname,
            "email": signup.email,
            "uid": signup.uid,
            "phonenumber": signup.phonenumber,
            "role": signup.role,
            "status": signup.status,
            "side": signup.side,
            "terms_agreement": signup.terms_agreement,
            "mfa_enabled": signup.mfa_enabled,
            "mfa_secret": signup.mfa_secret,
            "created_on": signup.created_at,
            "emirates_id":signup.emirates_id,
            "address":signup.address
        }
        for signup in signups
    ]
    
    retval = {
        "data": retval
    }
    return retval




"""************* DOWNLOAD CSV/PDF FILE OF THE INVENTORY RETAILS*****************"""

@router.post("/v1/admin/customers_report/export")
def export_vehicles_inventory_csv(data: CustomerReports, db: Session = Depends(get_db)):

        customers = db.query(User).filter(User.role == "customer")
        if not customers:
            raise HTTPException(status_code=404, detail="No customers found")
        # Ensure export directory exists
        if not os.path.exists(EXPORT_DIR):
            os.makedirs(EXPORT_DIR)

        if data.download_type == "csv":
            file_path = os.path.join(EXPORT_DIR, "customer_report.csv")

            # Create CSV file and write data to it
            with open(file_path, mode="w", newline="") as csv_file:
                writer = csv.writer(csv_file)

                writer.writerow(['id', 'firstname', 'lastname', 'email', 'uid','phone number', 'role','status','terms agreement','emirates_id','address'])  # CSV header


                for person in customers:
                    writer.writerow([person.id, person.firstname, person.lastname, person.email, person.uid, person.phonenumber,person.role,person.status,person.terms_agreement,person.emirates_id,person.address])

            # Return file as a download
            return FileResponse(file_path, filename="customer_report.csv", media_type="text/csv")
        
        elif data.download_type == "pdf":
            file_path = os.path.join(EXPORT_DIR, "customer_report.pdf")
            # Create PDF file and write data to it
            c = canvas.Canvas(file_path, pagesize=letter)
            c.setFont("Helvetica", 10)

            # Write header
            c.drawString(50, 750, "Customers Report")
            
            y_position = 710
            headers = ['ID', 'firstname', 'lastname', 'email', 'uid','phonenumber', 'role', 'status', 'terms agreement','emirates_id','address']
            c.drawString(50, y_position, " | ".join(headers))
            y_position -= 20

            for person in customers:
                line = f"{person.id} | {person.firstname} | {person.lastname} | {person.email} | {person.uid} | {person.phonenumber} | {person.role} | {person.status} | {person.terms_agreement} | {person.emirates_id} | {person.address}"
                c.drawString(50, y_position, line)
                y_position -= 20
                if y_position < 50:  # Create a new page if the content overflows
                    c.showPage()
                    c.setFont("Helvetica", 10)
                    y_position = 750

            c.save()
            # Return file as a download
            return FileResponse(file_path, filename="customer_report.pdf", media_type="application/pdf")


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

            return "Cart Data updated"
    except Exception as e:
        print(traceback.format_exc())
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
                    "bid_amount": bid.bid_amount,
                    "created_at": bid.created_at
                })

    return {"bids": bids}



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
                        "Unknown"
                    )
                    item_name = (
                        db.query(Vehicle.name).filter(Vehicle.id == bid.fk_vehicle_id).scalar() if bid.fk_vehicle_id else
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
                    "Unknown"
                )
                item_name = (
                    db.query(Vehicle.name).filter(Vehicle.id == bid.fk_vehicle_id).scalar() if bid.fk_vehicle_id else
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
                    "bid_amount": bid.bid_amount,
                    "created_at": bid.created_at
                })

    return {"bids": bids}






@router.post("/v1/user/admin_signupuid_bidadding_customer")
def signup(user_data: UidCustomerBidAdmin, db: Session = Depends(get_db)):
    # logging.info(f'Attempting to register user {user_data.email}')
    check_user_data = db.query(User).filter(User.phonenumber==user_data.phonenumber).first()
    if check_user_data is None:

        print(f'Email is: {user_data.auction_id}')
        print(f'Email is: {user_data.email}')
        print(f'Email is: {user_data.emirates_id}')
        print(f'Email is: {user_data.address}')
        if not user_data.auction_id:
            user_data.auction_id = None 
        if not user_data.email:
            user_data.email = None 
        if not user_data.emirates_id:
            user_data.emirates_id = None 
        if not user_data.address:
            user_data.address = None 
        if not user_data.role:
            user_data.role = "customer" 
            # make a random password for the user and a random user id
        print(f'Email is: {user_data.auction_id}')
        print(f'Email is: {user_data.email}')
        print(f'Email is: {user_data.emirates_id}')
        print(f'Email is: {user_data.address}')
        print(f'Email is: {user_data.role}')

        # Generate a random 8-digit password
        def generate_password():
            return ''.join(random.choices('0123456789', k=6))
        # Generate a unique UID for each user
        def generate_uid():
            return ''.join(random.choices('0123456789', k=8))
        # Adjusted code
        original_password = generate_password()  # Generate random password
        hashed_password = hashedpassword(original_password)  # Hash the password
        uid = generate_uid()            # Generate unique UID
        # password = hashedpassword(password)
        data_adding_DB = user_data.model_dump()
        data_adding_DB["side"] = "client"
        data_adding_DB["terms_agreement"] = "Yes"
        data_adding_DB["original_password"] = original_password
        data_adding_DB["password"] = hashed_password
        data_adding_DB["uid"] = uid
        data_adding_DB["mfa_enabled"] = "no"
        data_adding_DB["mfa_secret"] = "none"

        new_user = create_user_admin_customer(db, PublishDataUidCustomerAdmin(**data_adding_DB))
        if new_user is None:
            raise HTTPException(status_code=400, detail="New User is not Created")

        print("User Created Working on Bid Putting")


        # return {"Message": "Register Successful and Bid Placed", "id": new_user, "bid": new_bid}


    try:
        """************************************vehicles******************************************"""
        print(user_data.firstname)
        print(user_data.phonenumber)
        # checking customer data if the customer is already in the system or not
        customer_data = db.query(CustomerAuction).filter(CustomerAuction.phone_number==user_data.phonenumber).first()
        if customer_data is None:
            adding_customer = CustomerAuction(
                name=user_data.firstname,
                phone_number=user_data.phonenumber
            )
            db.add(adding_customer)
            db.commit()
            db.refresh(adding_customer)
            # adding the container number to the vehicles
            if user_data.vehicles:
                # vehicles_data = json.loads(user_data.vehicles)
                vehicles_data = user_data.vehicles
            else:
                vehicles_data = []

            print("Vehicles data:", vehicles_data)

            # update the vehicles with the given chassis number with the respective container id
            for veh in vehicles_data:
                # Access each detail of the vehicle
                # chassis_number = veh.get("chassis_number")
                # bid_amount = veh.get("bid_amount")
                chassis_number = veh.chassis_number
                bid_amount = veh.bid_amount
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
                            fk_auctionbigstar_id=user_data.auction_id,
                            fk_customer_id=adding_customer.id,
                            fk_vehicle_id=existing_vehicle.id,
                            bid_amount=bid_amount
                        )
                        db.add(auction_data)
                        db.commit()
                        db.refresh(auction_data)

                else:
                    print(f"No vehicle found")

            return "Cart Data Added"

        else:
            print("customer already registered updating the data")
        # adding the container number to the vehicles
            if user_data.vehicles:
                # vehicles_data = json.loads(user_data.vehicles)
                vehicles_data = user_data.vehicles
            else:
                vehicles_data = []

            print("Vehicles data:", vehicles_data)

            # update the vehicles with the given chassis number with the respective container id
            for veh in vehicles_data:
                # Access each detail of the vehicle
                # chassis_number = veh.get("chassis_number")
                # bid_amount = veh.get("bid_amount")
                chassis_number = veh.chassis_number
                bid_amount = veh.bid_amount
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
                            fk_auctionbigstar_id=user_data.auction_id,
                            fk_customer_id=customer_data.id,
                            fk_vehicle_id=existing_vehicle.id,
                            bid_amount=bid_amount
                        )
                        db.add(auction_data)
                        db.commit()
                        db.refresh(auction_data)

                else:
                    print(f"No vehicle found")

            return "Cart Data updated"
    except Exception as e:
        print(traceback.format_exc())
        raise HTTPException(status_code=409, detail=f' Error: {str(e)}')