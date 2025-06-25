from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from app.db.db_setup import get_db
from app.db.models import FeedBack, Message, FeedBackClient, Notification, Subscription
from app.db.schemas import FeedbackCreate, MessageData, FeedbackClientSchema, SubscriptionData
from app.helper.jwt_token_decode import decode_token
from sqlalchemy.orm import Session
from app.helper.emails import send_user_feedback_to_admin

router = APIRouter()

@router.post("/v1/user/feedback")
def create_feedback(feedback: FeedbackCreate, authorization: str = Header(None), db: Session = Depends(get_db)):

    if authorization is None:
            logging.error('The token entered for the user is either wrong or expired')
            raise HTTPException(status_code=401, detail="Unauthorized")
    token = authorization.split(" ")[1] if authorization.startswith("Bearer ") else authorization
    # we have return both the id and the complete data the only purpose is incase of refresh token we need all data in normal case we only need the id as foreign key
    user_id, retval = decode_token(token)  # Extracting the user_id as it would be used as foreign Key in the rollout table
    print(user_id)
    
    """create feed back"""
    feed_back = FeedBack(fk_user_id = user_id, rating = feedback.rating, comment = feedback.comment)
    db.add(feed_back)
    db.commit()
    db.refresh(feed_back)
    retval = {
         "id": feed_back.id,
         "Rating": feed_back.rating,
         "comment": feed_back.comment
    }
    return retval



@router.get("/v1/user/feedback")
def read_feedback(db: Session = Depends(get_db)):
    try:
        data = db.query(FeedBack).all()
        if data:
            return {'list': data}
        else:
            print("Feedback is None")
    
    except Exception as e:
        return str(e)



"""Leave a message"""

@router.post("/v1/user/leave_a_message")
def create_feedback(message: MessageData, db: Session = Depends(get_db)):
    
    """create Message"""
    message_create = Message(**message.model_dump())
    db.add(message_create)
    db.commit()
    db.refresh(message_create)

    return message_create



@router.get("/v1/messages")
def read_feedback(db: Session = Depends(get_db)):
    try:
        data = db.query(Message).all()
        if data:
            return {'list': data}
        else:
            print("Message is None")
    
    except Exception as e:
        return str(e)


@router.post("/v1/user/feedback_client")
def create_feedback_client(feedback: FeedbackClientSchema, db: Session = Depends(get_db)):
    """create feed back for client"""
    feed_back = FeedBackClient(title = feedback.title, description = feedback.description)
    db.add(feed_back)
    db.commit()
    db.refresh(feed_back)
    retval = {
         "id": feed_back.id,
         "Rating": feed_back.title,
         "comment": feed_back.description
    }

    """Create a notification and store in Notification Table"""
    notification = Notification(
        fk_user_id=None,
        message=f"You have received a feedback from an Employee",
        read = False
    )
    db.add(notification)
    db.commit()
    db.refresh(notification)

    print("Sending Email to Admin Informing about  User Feedback")
    send_user_feedback_to_admin(feed_back.title, feed_back.description)
    print("Email Sent")

    return retval


@router.get("/v1/user/feedback_client")
def read_feedback_client(db: Session = Depends(get_db)):
    try:
        data = db.query(FeedBackClient).all()
        if data:
            return {'data': data}
        else:
            print("Feedback is None")
    
    except Exception as e:
        return str(e)



@router.post("/v1/subscribe")
def create_feedback(subs: SubscriptionData, db: Session = Depends(get_db)):
    user_subs = Subscription(**subs.model_dump())
    db.add(user_subs)
    db.commit()
    db.refresh(user_subs)

    return {"Subscription Done": user_subs}