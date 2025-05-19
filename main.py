import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from app.api import db_testing, vehicles, vehicle_by_id, display_all_vehicles,vehicle_price
from app.api.users import signup, signin
from app.api.cms import zeeshan_cms
# from app.api.refresh_token import refresh_token
from app.db.db_setup import Base, engine
# from app.api.roles import role
import time
import logging


# Content Security Policy Middleware
class ContentSecurityPolicyMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        response = await call_next(request)
        response.headers['Content-Security-Policy'] = "default-src 'self'; script-src 'self'; style-src 'self'"
        return response


# Performance Monitoring Middleware
class PerformanceMonitoringMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time
        logging.info(f"Request {request.url.path} completed in {process_time:.4f} seconds")
        return response


app = FastAPI()


# # Initiallizing the logging file
# setup_logging()


# Directory to store the uploaded images
UPLOAD_DIR = "uploads"

"""Mounting the upload folder so that can be shown to the front end"""
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")


# These are used to remove the CORS error B/W different server in my case Python Back-end and flutter-dart front-end

origins = [
    "http://localhost.tiangolo.com",
    "https://localhost.tiangolo.com",
    "http://localhost",
    "http://localhost:5173",
    "http://localhost:5174",
    "http://localhost:8080",
    "http://ec2-54-252-183-45.ap-southeast-2.compute.amazonaws.com:3000",
]


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Just for checking if the application is working properly
@app.get("/")
async def main():
    return {"message": "Zeeshan Motors Application is Working (use: /docs to visit swagger documentation)"}


# Routers Here
# DB Testing
app.include_router(db_testing.router)
app.include_router(vehicles.router)
app.include_router(vehicle_by_id.router)
app.include_router(vehicle_price.router)
app.include_router(display_all_vehicles.router)
app.include_router(signup.router)
app.include_router(signin.router)
app.include_router(zeeshan_cms.router)




# # This function calls the ORM declerative base so that it may catch the difference and create DB by default if you want to handle all the DB manually by migrations comment this line
# Base.metadata.create_all(bind=engine)


# Application Starting
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=5004, reload=True)