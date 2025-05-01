from fastapi import FastAPI, HTTPException, APIRouter
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Create the database engine
DATABASE_URL_SQL = os.getenv("DATABASE_URL_MYSQL")
engine = create_engine(DATABASE_URL_SQL)

# Create a session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

router = APIRouter()

# Test database connection endpoint
@router.get("/test-db-connection")
def test_db_connection():
    try:
        # Attempt to connect to the database
        connection = engine.connect()
        connection.close()
        return {"message": "Database connection successful!"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database connection failed: {str(e)}")