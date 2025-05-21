from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.db.db_setup import get_db
from app.db.schemas import *
from app.db.models import *
from app.db.crud import *
from fastapi.responses import FileResponse

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
