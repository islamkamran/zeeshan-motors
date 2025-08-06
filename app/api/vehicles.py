import traceback
from fastapi import APIRouter, HTTPException, Depends, Header, File, UploadFile, Form, Request
from app.helper.authenticate_user import autheticate_user
from sqlalchemy.orm import Session
from app.db.db_setup import get_db
from app.helper.jwt_token import jwt_access_token
from app.helper.jwt_token_decode import decode_token
from app.helper.barcode_generator import generate_barcode_vehicle
from app.helper.jwt_token import is_token_blacklisted
from app.helper.image_name_maker import *
import logging
import os
import shutil
import csv
from app.helper.emails import send_quote_to_email
from fastapi.responses import FileResponse
from app.db.schemas import *
from app.db.models import *
from app.db.models import User as ModelUser
from app.db.crud import *
from fastapi.responses import FileResponse
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from sqlalchemy.sql import func
from sqlalchemy import and_
import requests
from datetime import datetime

EXPORT_DIR = "exports/"  # Directory to save the file
UPLOAD_DIR = "uploads/vehicles"
UPLOAD_DIR_INT = "uploads/vehicles/interior"  # Ensure this directory exists
UPLOAD_DIR_EXT = "uploads/vehicles/exterior"  # Ensure this directory exists

router = APIRouter()

@router.post("/v1/user/vehicles")
def vehicles(fk_bl_number: str = Form(None), body_type: str = Form(None), make: str = Form(None), model: str = Form(None), year: str = Form(None), title: str = Form(None), name: str = Form(None),chassis_number: str = Form(None),mileage: str = Form(None),damage_details: str = Form(None),transmission: str = Form(None), clynder: str = Form(None), location: str = Form(None), intcolor: str = Form(None),extcolor: str = Form(None),fuel: str = Form(None),engine: str = Form(None), status: str = Form(None),description: str = Form(None),grade: str = Form(None),score: str = Form(None),steer: str = Form(None),displacement: str = Form(None),total_price: float = Form(None),sold_price: float = Form(None),recieved_amount: float = Form(None),balance_amount: float = Form(None),auction_result: str = Form(None), condition: str = Form(None), image_interior: list[UploadFile] = File(None), image_exterior: list[UploadFile] = File(None), video: list[UploadFile] = File(None), drive_type: str = Form(None),doors: str = Form(None),engine_name: str = Form(None),supplier: str = Form(None),is_clear: bool = Form(None), report_status: str = Form(None),feature: str = Form(None), motor: str = Form(None), air_conditioner: str = Form(None), digital_odometer: str = Form(None), heater: str = Form(None),sunroof: str = Form(None),power_windows: str = Form(None),tv_led: str = Form(None), leather_seats: str = Form(None), tachometer: str = Form(None), headlight_leveler: str = Form(None), am_fm_radio: str = Form(None),armrest_console: str = Form(None),rear_seat_armrest_centre_console: str = Form(None),abs_antilock_braking: str = Form(None),child_safety_lock: str = Form(None),driver_air_bag: str = Form(None),passanger_air_bag: str = Form(None),rear_seat_air_bag: str = Form(None),curtain_air_bag: str = Form(None),power_door_lock: str = Form(None),traction_control: str = Form(None),oil_brakes: str = Form(None), air_brakes: str = Form(None),tool_kit: str = Form(None),stepney_tyre: str = Form(None),foot_parking_brake: str = Form(None),fog_lights_front: str = Form(None),alloy_rims: str = Form(None),high_deck: str = Form(None),electric_pump: str = Form(None),justlow: str = Form(None),crane_step: str = Form(None),HID_headlights: str = Form(None),rear_wiper: str = Form(None),sun_visor: str = Form(None), power_streeing: str = Form(None),push_start_smartkey: str = Form(None),keyless_entry: str = Form(None),key_start: str = Form(None),navigation: str = Form(None),remote_controller: str = Form(None),android_led: str = Form(None),bluetooth: str = Form(None),front_door_speaker: str = Form(None),rear_door_speaker: str = Form(None),rear_deck_speaker: str = Form(None),ECO_mode: str = Form(None),heated_seats: str = Form(None),power_seats: str = Form(None),power_side_mirrors: str = Form(None),electric_rearview_mirror: str = Form(None),dashboard_speakers: str = Form(None),max_length: str = Form(None),height: str = Form(None),wheel_base: str = Form(None),height_including_roof_rails: str = Form(None),luggage_capacity_seatsup: str = Form(None),luggage_capacity_seatsdown: str = Form(None),width: str = Form(None),width_including_mirrors: str = Form(None),gross_vehicle_weight: str = Form(None),max_loading_weight: str = Form(None),max_roof_load: str = Form(None),number_of_seats: str = Form(None), fuel_tank_capacity: str = Form(None),max_towing_weight_braked: str = Form(None),max_towing_weight_unbraked: str = Form(None),minimum_kerbweight: str = Form(None),turning_circle_kerb_to_kerb: str = Form(None),desmodromic_engine_technology: str = Form(None), fuel_injection: str = Form(None), lightweight_design: str = Form(None), high_performance_suspension: str = Form(None), riding_ergonomics: str = Form(None), seat: str = Form(None), instrumentation: str = Form(None), fuel_capacity: str = Form(None), high_performance_brakes: str = Form(None), high_quality_tires: str = Form(None), lighting: str = Form(None), storage: str = Form(None), security: str = Form(None), adjustable_suspension: str = Form(None), ambient_lighting_mood_lighting: str = Form(None), digital_instrument_cluster: str = Form(None), head_up_display: str = Form(None), wireless_charging_pad: str = Form(None), multi_zone_climate_control: str = Form(None), premium_sound_system: str = Form(None), wood_interior: str = Form(None), aluminum_tri_interior: str = Form(None), ventilated_seats: str = Form(None), panoramic_sunroof: str = Form(None), rear_entertainment_screens: str = Form(None), power_adjustable_steering_column: str = Form(None), memory_seats: str = Form(None), alcantara_carbon_fiber_trim: str = Form(None), alarm: str = Form(None), cooled_rear_seat: str = Form(None), wireless_smartphone_charger: str = Form(None),usb_type_c_port : str = Form(None), usb_20_port: str = Form(None), v12_power_outlet: str = Form(None), rear_charging_ports: str = Form(None), adaptive_cruise_control: str = Form(None), blind_spot_monitoring: str = Form(None), lane_keep_assist: str = Form(None), lane_departure_warning: str = Form(None), degree_360_camera: str = Form(None),front_rear_parking_sensors : str = Form(None), automatic_emergency_braking: str = Form(None), pedestrian_detection: str = Form(None), cross_traffic_alert_rear: str = Form(None), driver_attention_warning: str = Form(None), night_vision_assist: str = Form(None),tire_pressure_monitoring_system : str = Form(None),collision_mitigation_system : str = Form(None),isofix_child_seat_mounts : str = Form(None),adaptive_lighting : str = Form(None), performance_kit_tuned: str = Form(None),parking_button : str = Form(None),manual_handbrake : str = Form(None),electronic_parking_brake_auto_hold : str = Form(None),matrix_led_laser_headlights : str = Form(None),automatic_headlight_on_off: str = Form(None),power_tailgate : str = Form(None), roof_rails_roof_rack: str = Form(None), dual_exhaust_pipes: str = Form(None), sport_exhaust: str = Form(None),rear_spoiler : str = Form(None), led_dlrs_daytime_running_lights: str = Form(None),auto_folding_side_mirrors: str = Form(None), frameless_doors: str = Form(None),charging_port : str = Form(None), soft_close_doors: str = Form(None),illuminated_logo_welcome_lights : str = Form(None),rain_sensing_wipers : str = Form(None),Performance_tyres : str = Form(None), side_mirrors_indicators: str = Form(None), sports_suspension: str = Form(None), premium_paint: str = Form(None), air_deflector: str = Form(None), wireless_apple_carplay_android_auto: str = Form(None), voice_control_system: str = Form(None), gesture_control: str = Form(None), remote_engine_start: str = Form(None), auto_dimming_rearview_mirror: str = Form(None), driver_seat_massager: str = Form(None), rear_window_sunshade_manual: str = Form(None), rear_window_sunshade_electric: str = Form(None),air_purifier_ionizer : str = Form(None), cabin_noise_cancellation: str = Form(None), smart_climate_control_ai_sensing: str = Form(None),ota_updates_over_the_air_software : str = Form(None),sports_drive_mode: str = Form(None), comfort_drive_mode: str = Form(None),snow_drive_mode : str = Form(None),intelligent_parking_assist_auto_park : str = Form(None),digital_key_smartphone : str = Form(None),electric_rear_seat_recline : str = Form(None), navigation_system: str = Form(None), power_locks: str = Form(None), tinted_windows: str = Form(None), rear_tv_screens: str = Form(None),cd_dvd_player : str = Form(None), mp3_interface: str = Form(None), authorization: str = Header(None), db: Session = Depends(get_db)):
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
        user_details = db.query(ModelUser).filter(ModelUser.id==user_id).first()
        check_veh_data  = db.query(Vehicle).filter(Vehicle.chassis_number == chassis_number).first()
        if check_veh_data:
            raise HTTPException(status_code=409, detail="Vehicle with this Chassis already Exist")
        if mileage is not None:
            # the commas Logic
            mileage = float(mileage)
            mileage = f"{mileage:,.0f}"
            mileage = str(mileage) + " " + "km"
        print(f'engine name is: {engine_name}')
        if fk_bl_number:
            print("In if condition")
            container_data = db.query(Container).filter(Container.bl_number == fk_bl_number).first()
            if container_data is None:
                raise HTTPException(status_code=404, detail="Container not found")
            # print(container_data.id)
            vehicle_data = Vehicles(fk_container_id=container_data.id, body_type=body_type,make=make,model=model, year=year, title=title, name=name, chassis_number=chassis_number, mileage=mileage, damage_details=damage_details, transmission=transmission, clynder=clynder, location=location, intcolor=intcolor, extcolor=extcolor, fuel=fuel, engine=engine, status=status, description=description, grade=grade, score=score, steer=steer, displacement=displacement, total_price=total_price, sold_price=sold_price,recieved_amount=recieved_amount, balance_amount=balance_amount, auction_result=auction_result, condition=condition, drive_type=drive_type,doors=doors,engine_name=engine_name,supplier=supplier, is_clear=is_clear, report_status=report_status, feature=feature, motor=motor)
            vehicle_data = vehicle_data.dict()
            vehicle_data["uploaded_by"] = user_details.firstname
            if status == "Outofstock":
                vehicle_data["sold_by"] = user_details.firstname
            else:
                vehicle_data["sold_by"] = None
            vehicle_id = register_vehicle(db, user_id, PublishVehicle(**vehicle_data))
        elif fk_bl_number is None:
            print("In else condition")
            vehicle_data = Vehicles(body_type=body_type,make=make,model=model, year=year, title=title, name=name, chassis_number=chassis_number, mileage=mileage, damage_details=damage_details, transmission=transmission, clynder=clynder, location=location, intcolor=intcolor,extcolor=extcolor, fuel=fuel, engine=engine, status=status, description=description, grade=grade, score=score, steer=steer, displacement=displacement, total_price=total_price, sold_price=sold_price,recieved_amount=recieved_amount, balance_amount=balance_amount, auction_result=auction_result, condition=condition, drive_type=drive_type,doors=doors,engine_name=engine_name,supplier=supplier, is_clear=is_clear, report_status=report_status, feature=feature, motor=motor)
            vehicle_data = vehicle_data.dict()
            vehicle_data["uploaded_by"] = user_details.firstname
            if status == "Outofstock":
                vehicle_data["sold_by"] = user_details.firstname
            else:
                vehicle_data["sold_by"] = None
            vehicle_id = register_vehicle(db, user_id, PublishVehicle(**vehicle_data))
        
        """THE FUNCTION NAME IS BARCODE BUT IT HAVE QRCODE AS THE PROJECT REQUIREMENT WAS CHANGED AT THE END AND I DONOT WANT TO MISS UP ALL THE CODE :) PARDONS IN ADVANCE ONLY 3 FUNCTIONS TOTAL FOR BARCODES WHICH ARE QRCODES NOW"""
        # Generate the barcode data as a string
        barcode_data = f"id: {id}, name: {name}, chassis_number:{chassis_number}, make:{make}, model:{model}, year:{year}, intcolor:{extcolor},extcolor:{extcolor}, fuel: {fuel}, transmission:{transmission}, condition:{condition}, total_price:{total_price}, mileage:{mileage}, sold_price:{sold_price}, status:{status}"
        # Generate and save barcode image
        barcode_path = generate_barcode_vehicle(barcode_data, vehicle_id)
        logging.info(f'Barcode generated and saved at: {barcode_path}')
        print(f"The path of barcode: {barcode_path}")

        """storing images and videos"""
        # Initialize paths
        image_paths_int = []  # for interior images
        image_paths_ext = []  # for exterior images
        videos_path = []
        # First check if a record already exists for this vehicle
        existing_images = db.query(Images).filter(Images.fk_vehicle_id == vehicle_id).first()

        # Save interior images files to the uploads directory
        if image_interior is not None:
            for img in image_interior:
                img.filename = format_image_name_int(vehicle_id, img.filename)
                file_location = os.path.join(UPLOAD_DIR_INT, img.filename)
                with open(file_location, "wb") as buffer:
                    shutil.copyfileobj(img.file, buffer)
                image_paths_int.append(file_location)
            images_string_int = ",".join(image_paths_int)

        # Save exterior images files to the uploads directory
        if image_exterior is not None:
            for img in image_exterior:
                img.filename = format_image_name_ext(vehicle_id, img.filename)
                file_location = os.path.join(UPLOAD_DIR_EXT, img.filename)
                with open(file_location, "wb") as buffer:
                    shutil.copyfileobj(img.file, buffer)
                image_paths_ext.append(file_location)
            images_string_ext = ",".join(image_paths_ext)

        # Create or update the single database record
        if existing_images is None:
            # Create new record with all provided data
            new_images = Images(
                image_interior=images_string_int if image_interior is not None else None,
                image_exterior=images_string_ext if image_exterior is not None else None,
                fk_vehicle_id=vehicle_id,
                barcode=barcode_path
            )
            db.add(new_images)
        else:
            # Update existing record with new data
            if image_interior is not None:
                existing_images.image_interior = images_string_int
            if image_exterior is not None:
                existing_images.image_exterior = images_string_ext
            if barcode_path is not None:
                existing_images.barcode = barcode_path

        db.commit()
        db.refresh(existing_images if existing_images else new_images)
            
        # Save video files to the uploads directory
        if video is not None:
            for vid in video:
                vid.filename = str(vehicle_id) + vid.filename
                file_location = os.path.join(UPLOAD_DIR_INT, vid.filename)
                with open(file_location, "wb") as buffer:
                    shutil.copyfileobj(vid.file, buffer)
                videos_path.append(file_location)

            # Convert list of paths to a comma-separated string
            videos_string = ",".join(videos_path)

            veh_video = Videos(
                video = videos_string,
                fk_vehicle_id = vehicle_id
            )
            db.add(veh_video)
            db.commit()
            db.refresh(veh_video)

        """Adding the features to interior table"""
        # check vehicle and then proceed
        checkVehicle = db.query(Vehicle).filter(Vehicle.id == vehicle_id).first()
    
        if checkVehicle is None:
            logging.error(f'The Vehicle is not found in DB')
            raise HTTPException(status_code=404, detail="Vehicle Not Found So the Interior cannot be stored with it")

        # changing types of values from strings to booleans
        if air_conditioner is not None:
            if air_conditioner.lower() in ["true", "1"]:
                air_conditioner = True
            elif air_conditioner.lower() in ["false", "0"]:
                air_conditioner = False
            else:
                raise HTTPException(status_code=400, detail="Invalid boolean value for air_conditioner")

        if digital_odometer is not None:
            if digital_odometer.lower() in ["true", "1"]:
                digital_odometer = True
            elif digital_odometer.lower() in ["false", "0"]:
                digital_odometer = False
            else:
                raise HTTPException(status_code=400, detail="Invalid boolean value for digital_odometer")

        if heater is not None:
            if heater.lower() in ["true", "1"]:
                heater = True
            elif heater.lower() in ["false", "0"]:
                heater = False
            else:
                raise HTTPException(status_code=400, detail="Invalid boolean value for heater")

        if sunroof is not None:
            if sunroof.lower() in ["true", "1"]:
                sunroof = True
            elif sunroof.lower() in ["false", "0"]:
                sunroof = False
            else:
                raise HTTPException(status_code=400, detail="Invalid boolean value for sunroof")

        if power_windows is not None:
            if power_windows.lower() in ["true", "1"]:
                power_windows = True
            elif power_windows.lower() in ["false", "0"]:
                power_windows = False
            else:
                raise HTTPException(status_code=400, detail="Invalid boolean value for power_windows")
        
        if tv_led is not None:
            if tv_led.lower() in ["true", "1"]:
                tv_led = True
            elif tv_led.lower() in ["false", "0"]:
                tv_led = False
            else:
                raise HTTPException(status_code=400, detail="Invalid boolean value for tv_led")

        if leather_seats is not None:
            if leather_seats.lower() in ["true", "1"]:
                leather_seats = True
            elif leather_seats.lower() in ["false", "0"]:
                leather_seats = False
            else:
                raise HTTPException(status_code=400, detail="Invalid boolean value for leather_seats")

        if tachometer is not None:
            if tachometer.lower() in ["true", "1"]:
                tachometer = True
            elif tachometer.lower() in ["false", "0"]:
                tachometer = False
            else:
                raise HTTPException(status_code=400, detail="Invalid boolean value for tachometer")

        if headlight_leveler is not None:
            if headlight_leveler.lower() in ["true", "1"]:
                headlight_leveler = True
            elif headlight_leveler.lower() in ["false", "0"]:
                headlight_leveler = False
            else:
                raise HTTPException(status_code=400, detail="Invalid boolean value for headlight_leveler")

        if am_fm_radio is not None:
            if am_fm_radio.lower() in ["true", "1"]:
                am_fm_radio = True
            elif am_fm_radio.lower() in ["false", "0"]:
                am_fm_radio = False
            else:
                raise HTTPException(status_code=400, detail="Invalid boolean value for am_fm_radio")
            
        if armrest_console is not None:
            if armrest_console.lower() in ["true", "1"]:
                armrest_console = True
            elif armrest_console.lower() in ["false", "0"]:
                armrest_console = False
            else:
                raise HTTPException(status_code=400, detail="Invalid boolean value for armrest_console")

        if rear_seat_armrest_centre_console is not None:
            if rear_seat_armrest_centre_console.lower() in ["true", "1"]:
                rear_seat_armrest_centre_console = True
            elif rear_seat_armrest_centre_console.lower() in ["false", "0"]:
                rear_seat_armrest_centre_console = False
            else:
                raise HTTPException(status_code=400, detail="Invalid boolean value for rear_seat_armrest_centre_console")

        if ambient_lighting_mood_lighting is not None:
            if ambient_lighting_mood_lighting.lower() in ["true", "1"]:
                ambient_lighting_mood_lighting = True
            elif ambient_lighting_mood_lighting.lower() in ["false", "0"]:
                ambient_lighting_mood_lighting = False
            else:
                raise HTTPException(status_code=400, detail="Invalid boolean value for ambient_lighting_mood_lighting")

        if digital_instrument_cluster is not None:
            if digital_instrument_cluster.lower() in ["true", "1"]:
                digital_instrument_cluster = True
            elif digital_instrument_cluster.lower() in ["false", "0"]:
                digital_instrument_cluster = False
            else:
                raise HTTPException(status_code=400, detail="Invalid boolean value for digital_instrument_cluster")

        if head_up_display is not None:
            if head_up_display.lower() in ["true", "1"]:
                head_up_display = True
            elif head_up_display.lower() in ["false", "0"]:
                head_up_display = False
            else:
                raise HTTPException(status_code=400, detail="Invalid boolean value for head_up_display")
            
        if wireless_charging_pad is not None:
            if wireless_charging_pad.lower() in ["true", "1"]:
                wireless_charging_pad = True
            elif wireless_charging_pad.lower() in ["false", "0"]:
                wireless_charging_pad = False
            else:
                raise HTTPException(status_code=400, detail="Invalid boolean value for wireless_charging_pad")
            
        if multi_zone_climate_control is not None:
            if multi_zone_climate_control.lower() in ["true", "1"]:
                multi_zone_climate_control = True
            elif multi_zone_climate_control.lower() in ["false", "0"]:
                multi_zone_climate_control = False
            else:
                raise HTTPException(status_code=400, detail="Invalid boolean value for multi_zone_climate_control")
            
        if premium_sound_system is not None:
            if premium_sound_system.lower() in ["true", "1"]:
                premium_sound_system = True
            elif premium_sound_system.lower() in ["false", "0"]:
                premium_sound_system = False
            else:
                raise HTTPException(status_code=400, detail="Invalid boolean value for premium_sound_system")
            
        if wood_interior is not None:
            if wood_interior.lower() in ["true", "1"]:
                wood_interior = True
            elif wood_interior.lower() in ["false", "0"]:
                wood_interior = False
            else:
                raise HTTPException(status_code=400, detail="Invalid boolean value for wood_interior")
            
        if aluminum_tri_interior is not None:
            if aluminum_tri_interior.lower() in ["true", "1"]:
                aluminum_tri_interior = True
            elif aluminum_tri_interior.lower() in ["false", "0"]:
                aluminum_tri_interior = False
            else:
                raise HTTPException(status_code=400, detail="Invalid boolean value for aluminum_tri_interior")
            
        if ventilated_seats is not None:
            if ventilated_seats.lower() in ["true", "1"]:
                ventilated_seats = True
            elif ventilated_seats.lower() in ["false", "0"]:
                ventilated_seats = False
            else:
                raise HTTPException(status_code=400, detail="Invalid boolean value for ventilated_seats")
            
        if panoramic_sunroof is not None:
            if panoramic_sunroof.lower() in ["true", "1"]:
                panoramic_sunroof = True
            elif panoramic_sunroof.lower() in ["false", "0"]:
                panoramic_sunroof = False
            else:
                raise HTTPException(status_code=400, detail="Invalid boolean value for panoramic_sunroof")
            
        if rear_entertainment_screens is not None:
            if rear_entertainment_screens.lower() in ["true", "1"]:
                rear_entertainment_screens = True
            elif rear_entertainment_screens.lower() in ["false", "0"]:
                rear_entertainment_screens = False
            else:
                raise HTTPException(status_code=400, detail="Invalid boolean value for rear_entertainment_screens")
            
        if power_adjustable_steering_column is not None:
            if power_adjustable_steering_column.lower() in ["true", "1"]:
                power_adjustable_steering_column = True
            elif power_adjustable_steering_column.lower() in ["false", "0"]:
                power_adjustable_steering_column = False
            else:
                raise HTTPException(status_code=400, detail="Invalid boolean value for power_adjustable_steering_column")
            
        if memory_seats is not None:
            if memory_seats.lower() in ["true", "1"]:
                memory_seats = True
            elif memory_seats.lower() in ["false", "0"]:
                memory_seats = False
            else:
                raise HTTPException(status_code=400, detail="Invalid boolean value for memory_seats")
            
        if alcantara_carbon_fiber_trim is not None:
            if alcantara_carbon_fiber_trim.lower() in ["true", "1"]:
                alcantara_carbon_fiber_trim = True
            elif alcantara_carbon_fiber_trim.lower() in ["false", "0"]:
                alcantara_carbon_fiber_trim = False
            else:
                raise HTTPException(status_code=400, detail="Invalid boolean value for alcantara_carbon_fiber_trim")
            
        if alarm is not None:
            if alarm.lower() in ["true", "1"]:
                alarm = True
            elif alarm.lower() in ["false", "0"]:
                alarm = False
            else:
                raise HTTPException(status_code=400, detail="Invalid boolean value for alarm")
            
        if cooled_rear_seat is not None:
            if cooled_rear_seat.lower() in ["true", "1"]:
                cooled_rear_seat = True
            elif cooled_rear_seat.lower() in ["false", "0"]:
                cooled_rear_seat = False
            else:
                raise HTTPException(status_code=400, detail="Invalid boolean value for cooled_rear_seat")
            
        if wireless_smartphone_charger is not None:
            if wireless_smartphone_charger.lower() in ["true", "1"]:
                wireless_smartphone_charger = True
            elif wireless_smartphone_charger.lower() in ["false", "0"]:
                wireless_smartphone_charger = False
            else:
                raise HTTPException(status_code=400, detail="Invalid boolean value for wireless_smartphone_charger")
            
        if usb_type_c_port is not None:
            if usb_type_c_port.lower() in ["true", "1"]:
                usb_type_c_port = True
            elif usb_type_c_port.lower() in ["false", "0"]:
                usb_type_c_port = False
            else:
                raise HTTPException(status_code=400, detail="Invalid boolean value for usb_type_c_port")
            
        if usb_20_port is not None:
            if usb_20_port.lower() in ["true", "1"]:
                usb_20_port = True
            elif usb_20_port.lower() in ["false", "0"]:
                usb_20_port = False
            else:
                raise HTTPException(status_code=400, detail="Invalid boolean value for usb_20_port")
            
        if v12_power_outlet is not None:
            if v12_power_outlet.lower() in ["true", "1"]:
                v12_power_outlet = True
            elif v12_power_outlet.lower() in ["false", "0"]:
                v12_power_outlet = False
            else:
                raise HTTPException(status_code=400, detail="Invalid boolean value for v12_power_outlet")
            
        if rear_charging_ports is not None:
            if rear_charging_ports.lower() in ["true", "1"]:
                rear_charging_ports = True
            elif rear_charging_ports.lower() in ["false", "0"]:
                rear_charging_ports = False
            else:
                raise HTTPException(status_code=400, detail="Invalid boolean value for rear_charging_ports")
            

        # All data converted to boolean now storing the data in the table

        interior_data = VehInterior(air_conditioner=air_conditioner,digital_odometer=digital_odometer,heater=heater,sunroof=sunroof,power_windows=power_windows,tv_led=tv_led,leather_seats=leather_seats,tachometer=tachometer,headlight_leveler=headlight_leveler,am_fm_radio=am_fm_radio,armrest_console=armrest_console,rear_seat_armrest_centre_console=rear_seat_armrest_centre_console,ambient_lighting_mood_lighting=ambient_lighting_mood_lighting,digital_instrument_cluster=digital_instrument_cluster,head_up_display=head_up_display,wireless_charging_pad=wireless_charging_pad,multi_zone_climate_control=multi_zone_climate_control, premium_sound_system=premium_sound_system, wood_interior=wood_interior, aluminum_tri_interior=aluminum_tri_interior, ventilated_seats=ventilated_seats, panoramic_sunroof=panoramic_sunroof, rear_entertainment_screens=rear_entertainment_screens, power_adjustable_steering_column=power_adjustable_steering_column, memory_seats=memory_seats, alcantara_carbon_fiber_trim=alcantara_carbon_fiber_trim, alarm=alarm, cooled_rear_seat=cooled_rear_seat, wireless_smartphone_charger=wireless_smartphone_charger, usb_type_c_port=usb_type_c_port, usb_20_port=usb_20_port, v12_power_outlet=v12_power_outlet, rear_charging_ports=rear_charging_ports)

        interior_data = interior_data.model_dump()
        interior_id = register_interior(db, user_id, vehicle_id, VehInterior(**interior_data))


        """Adding the features to Safety table"""
        # changing types of values from strings to booleans
        if abs_antilock_braking is not None:
            if abs_antilock_braking.lower() in ["true", "1"]:
                abs_antilock_braking = True
            elif abs_antilock_braking.lower() in ["false", "0"]:
                abs_antilock_braking = False
            else:
                raise HTTPException(status_code=400, detail="Invalid boolean value for abs_antilock_braking")

        if child_safety_lock is not None:
            if child_safety_lock.lower() in ["true", "1"]:
                child_safety_lock = True
            elif child_safety_lock.lower() in ["false", "0"]:
                child_safety_lock = False
            else:
                raise HTTPException(status_code=400, detail="Invalid boolean value for child_safety_lock")

        if driver_air_bag is not None:
            if driver_air_bag.lower() in ["true", "1"]:
                driver_air_bag = True
            elif driver_air_bag.lower() in ["false", "0"]:
                driver_air_bag = False
            else:
                raise HTTPException(status_code=400, detail="Invalid boolean value for driver_air_bag")

        if passanger_air_bag is not None:
            if passanger_air_bag.lower() in ["true", "1"]:
                passanger_air_bag = True
            elif passanger_air_bag.lower() in ["false", "0"]:
                passanger_air_bag = False
            else:
                raise HTTPException(status_code=400, detail="Invalid boolean value for passanger_air_bag")

        if rear_seat_air_bag is not None:
            if rear_seat_air_bag.lower() in ["true", "1"]:
                rear_seat_air_bag = True
            elif rear_seat_air_bag.lower() in ["false", "0"]:
                rear_seat_air_bag = False
            else:
                raise HTTPException(status_code=400, detail="Invalid boolean value for rear_seat_air_bag")

        if curtain_air_bag is not None:
            if curtain_air_bag.lower() in ["true", "1"]:
                curtain_air_bag = True
            elif curtain_air_bag.lower() in ["false", "0"]:
                curtain_air_bag = False
            else:
                raise HTTPException(status_code=400, detail="Invalid boolean value for curtain_air_bag")

        if power_door_lock is not None:
            if power_door_lock.lower() in ["true", "1"]:
                power_door_lock = True
            elif power_door_lock.lower() in ["false", "0"]:
                power_door_lock = False
            else:
                raise HTTPException(status_code=400, detail="Invalid boolean value for power_door_lock")

        if traction_control is not None:
            if traction_control.lower() in ["true", "1"]:
                traction_control = True
            elif traction_control.lower() in ["false", "0"]:
                traction_control = False
            else:
                raise HTTPException(status_code=400, detail="Invalid boolean value for traction_control")
    
        if oil_brakes is not None:
            if oil_brakes.lower() in ["true", "1"]:
                oil_brakes = True
            elif oil_brakes.lower() in ["false", "0"]:
                oil_brakes = False
            else:
                raise HTTPException(status_code=400, detail="Invalid boolean value for oil_brakes")

        if air_brakes is not None:
            if air_brakes.lower() in ["true", "1"]:
                air_brakes = True
            elif air_brakes.lower() in ["false", "0"]:
                air_brakes = False
            else:
                raise HTTPException(status_code=400, detail="Invalid boolean value for air_brakes")

        if tool_kit is not None:
            if tool_kit.lower() in ["true", "1"]:
                tool_kit = True
            elif tool_kit.lower() in ["false", "0"]:
                tool_kit = False
            else:
                raise HTTPException(status_code=400, detail="Invalid boolean value for tool_kit")

        if stepney_tyre is not None:
            if stepney_tyre.lower() in ["true", "1"]:
                stepney_tyre = True
            elif stepney_tyre.lower() in ["false", "0"]:
                stepney_tyre = False
            else:
                raise HTTPException(status_code=400, detail="Invalid boolean value for stepney_tyre")

        if foot_parking_brake is not None:
            if foot_parking_brake.lower() in ["true", "1"]:
                foot_parking_brake = True
            elif foot_parking_brake.lower() in ["false", "0"]:
                foot_parking_brake = False
            else:
                raise HTTPException(status_code=400, detail="Invalid boolean value for foot_parking_brake")
            
        if adaptive_cruise_control is not None:
            if adaptive_cruise_control.lower() in ["true", "1"]:
                foot_parkadaptive_cruise_controling_brake = True
            elif adaptive_cruise_control.lower() in ["false", "0"]:
                adaptive_cruise_control = False
            else:
                raise HTTPException(status_code=400, detail="Invalid boolean value for adaptive_cruise_control")
            
        if blind_spot_monitoring is not None:
            if blind_spot_monitoring.lower() in ["true", "1"]:
                blind_spot_monitoring = True
            elif blind_spot_monitoring.lower() in ["false", "0"]:
                blind_spot_monitoring = False
            else:
                raise HTTPException(status_code=400, detail="Invalid boolean value for blind_spot_monitoring")
            
        if lane_keep_assist is not None:
            if lane_keep_assist.lower() in ["true", "1"]:
                lane_keep_assist = True
            elif lane_keep_assist.lower() in ["false", "0"]:
                lane_keep_assist = False
            else:
                raise HTTPException(status_code=400, detail="Invalid boolean value for lane_keep_assist")
            
        if lane_departure_warning is not None:
            if lane_departure_warning.lower() in ["true", "1"]:
                lane_departure_warning = True
            elif lane_departure_warning.lower() in ["false", "0"]:
                lane_departure_warning = False
            else:
                raise HTTPException(status_code=400, detail="Invalid boolean value for lane_departure_warning")
            
        if degree_360_camera is not None:
            if degree_360_camera.lower() in ["true", "1"]:
                degree_360_camera = True
            elif degree_360_camera.lower() in ["false", "0"]:
                degree_360_camera = False
            else:
                raise HTTPException(status_code=400, detail="Invalid boolean value for degree_360_camera")
            
        if front_rear_parking_sensors is not None:
            if front_rear_parking_sensors.lower() in ["true", "1"]:
                front_rear_parking_sensors = True
            elif front_rear_parking_sensors.lower() in ["false", "0"]:
                front_rear_parking_sensors = False
            else:
                raise HTTPException(status_code=400, detail="Invalid boolean value for front_rear_parking_sensors")
            
        if automatic_emergency_braking is not None:
            if automatic_emergency_braking.lower() in ["true", "1"]:
                automatic_emergency_braking = True
            elif automatic_emergency_braking.lower() in ["false", "0"]:
                automatic_emergency_braking = False
            else:
                raise HTTPException(status_code=400, detail="Invalid boolean value for automatic_emergency_braking")
            
        if pedestrian_detection is not None:
            if pedestrian_detection.lower() in ["true", "1"]:
                pedestrian_detection = True
            elif pedestrian_detection.lower() in ["false", "0"]:
                pedestrian_detection = False
            else:
                raise HTTPException(status_code=400, detail="Invalid boolean value for pedestrian_detection")
            
        if cross_traffic_alert_rear is not None:
            if cross_traffic_alert_rear.lower() in ["true", "1"]:
                cross_traffic_alert_rear = True
            elif cross_traffic_alert_rear.lower() in ["false", "0"]:
                cross_traffic_alert_rear = False
            else:
                raise HTTPException(status_code=400, detail="Invalid boolean value for cross_traffic_alert_rear")
            
        if driver_attention_warning is not None:
            if driver_attention_warning.lower() in ["true", "1"]:
                driver_attention_warning = True
            elif driver_attention_warning.lower() in ["false", "0"]:
                driver_attention_warning = False
            else:
                raise HTTPException(status_code=400, detail="Invalid boolean value for driver_attention_warning")
            
        if night_vision_assist is not None:
            if night_vision_assist.lower() in ["true", "1"]:
                night_vision_assist = True
            elif night_vision_assist.lower() in ["false", "0"]:
                night_vision_assist = False
            else:
                raise HTTPException(status_code=400, detail="Invalid boolean value for night_vision_assist")
            
        if tire_pressure_monitoring_system is not None:
            if tire_pressure_monitoring_system.lower() in ["true", "1"]:
                tire_pressure_monitoring_system = True
            elif tire_pressure_monitoring_system.lower() in ["false", "0"]:
                tire_pressure_monitoring_system = False
            else:
                raise HTTPException(status_code=400, detail="Invalid boolean value for tire_pressure_monitoring_system")
            
        if collision_mitigation_system is not None:
            if collision_mitigation_system.lower() in ["true", "1"]:
                collision_mitigation_system = True
            elif collision_mitigation_system.lower() in ["false", "0"]:
                collision_mitigation_system = False
            else:
                raise HTTPException(status_code=400, detail="Invalid boolean value for collision_mitigation_system")
            
        if isofix_child_seat_mounts is not None:
            if isofix_child_seat_mounts.lower() in ["true", "1"]:
                isofix_child_seat_mounts = True
            elif isofix_child_seat_mounts.lower() in ["false", "0"]:
                isofix_child_seat_mounts = False
            else:
                raise HTTPException(status_code=400, detail="Invalid boolean value for isofix_child_seat_mounts")
            
        if adaptive_lighting is not None:
            if adaptive_lighting.lower() in ["true", "1"]:
                adaptive_lighting = True
            elif adaptive_lighting.lower() in ["false", "0"]:
                adaptive_lighting = False
            else:
                raise HTTPException(status_code=400, detail="Invalid boolean value for adaptive_lighting")
            
        if performance_kit_tuned is not None:
            if performance_kit_tuned.lower() in ["true", "1"]:
                performance_kit_tuned = True
            elif performance_kit_tuned.lower() in ["false", "0"]:
                performance_kit_tuned = False
            else:
                raise HTTPException(status_code=400, detail="Invalid boolean value for performance_kit_tuned")
            
        if parking_button is not None:
            if parking_button.lower() in ["true", "1"]:
                parking_button = True
            elif parking_button.lower() in ["false", "0"]:
                parking_button = False
            else:
                raise HTTPException(status_code=400, detail="Invalid boolean value for parking_button")
            
        if manual_handbrake is not None:
            if manual_handbrake.lower() in ["true", "1"]:
                manual_handbrake = True
            elif manual_handbrake.lower() in ["false", "0"]:
                manual_handbrake = False
            else:
                raise HTTPException(status_code=400, detail="Invalid boolean value for manual_handbrake")
            
        if electronic_parking_brake_auto_hold is not None:
            if electronic_parking_brake_auto_hold.lower() in ["true", "1"]:
                electronic_parking_brake_auto_hold = True
            elif electronic_parking_brake_auto_hold.lower() in ["false", "0"]:
                electronic_parking_brake_auto_hold = False
            else:
                raise HTTPException(status_code=400, detail="Invalid boolean value for electronic_parking_brake_auto_hold")

                
        # All data converted to boolean now storing the data in the table

        safety_data = VehSafety(abs_antilock_braking=abs_antilock_braking,child_safety_lock=child_safety_lock,driver_air_bag=driver_air_bag,passanger_air_bag=passanger_air_bag,rear_seat_air_bag=rear_seat_air_bag,curtain_air_bag=curtain_air_bag,power_door_lock=power_door_lock,traction_control=traction_control,oil_brakes=oil_brakes,air_brakes=air_brakes,tool_kit=tool_kit,stepney_tyre=stepney_tyre,foot_parking_brake=foot_parking_brake,adaptive_cruise_control=adaptive_cruise_control,blind_spot_monitoring=blind_spot_monitoring,lane_keep_assist=lane_keep_assist,lane_departure_warning=lane_departure_warning,degree_360_camera=degree_360_camera,front_rear_parking_sensors=front_rear_parking_sensors,automatic_emergency_braking=automatic_emergency_braking,pedestrian_detection=pedestrian_detection,cross_traffic_alert_rear=cross_traffic_alert_rear,driver_attention_warning=driver_attention_warning,night_vision_assist=night_vision_assist,tire_pressure_monitoring_system=tire_pressure_monitoring_system,collision_mitigation_system=collision_mitigation_system,isofix_child_seat_mounts=isofix_child_seat_mounts,adaptive_lighting=adaptive_lighting,performance_kit_tuned=performance_kit_tuned,parking_button=parking_button,manual_handbrake=manual_handbrake,electronic_parking_brake_auto_hold=electronic_parking_brake_auto_hold)
        safety_data = safety_data.model_dump()
        safety_id = register_safety(db, user_id, vehicle_id, VehSafety(**safety_data))


        """Adding the features to Exterior table"""
        # changing types of values from strings to booleans
        if fog_lights_front is not None:
            if fog_lights_front.lower() in ["true", "1"]:
                fog_lights_front = True
            elif fog_lights_front.lower() in ["false", "0"]:
                fog_lights_front = False
            else:
                raise HTTPException(status_code=400, detail="Invalid boolean value for fog_lights_front")

        if alloy_rims is not None:
            if alloy_rims.lower() in ["true", "1"]:
                alloy_rims = True
            elif alloy_rims.lower() in ["false", "0"]:
                alloy_rims = False
            else:
                raise HTTPException(status_code=400, detail="Invalid boolean value for alloy_rims")

        if high_deck is not None:
            if high_deck.lower() in ["true", "1"]:
                high_deck = True
            elif high_deck.lower() in ["false", "0"]:
                high_deck = False
            else:
                raise HTTPException(status_code=400, detail="Invalid boolean value for high_deck")

        if electric_pump is not None:
            if electric_pump.lower() in ["true", "1"]:
                electric_pump = True
            elif electric_pump.lower() in ["false", "0"]:
                electric_pump = False
            else:
                raise HTTPException(status_code=400, detail="Invalid boolean value for electric_pump")

        if justlow is not None:
            if justlow.lower() in ["true", "1"]:
                justlow = True
            elif justlow.lower() in ["false", "0"]:
                justlow = False
            else:
                raise HTTPException(status_code=400, detail="Invalid boolean value for justlow")

        if crane_step is not None:
            if crane_step.lower() in ["true", "1"]:
                crane_step = True
            elif crane_step.lower() in ["false", "0"]:
                crane_step = False
            else:
                raise HTTPException(status_code=400, detail="Invalid boolean value for crane_step")

        if HID_headlights is not None:
            if HID_headlights.lower() in ["true", "1"]:
                HID_headlights = True
            elif HID_headlights.lower() in ["false", "0"]:
                HID_headlights = False
            else:
                raise HTTPException(status_code=400, detail="Invalid boolean value for HID_headlights")

        if rear_wiper is not None:
            if rear_wiper.lower() in ["true", "1"]:
                rear_wiper = True
            elif rear_wiper.lower() in ["false", "0"]:
                rear_wiper = False
            else:
                raise HTTPException(status_code=400, detail="Invalid boolean value for rear_wiper")
        
        if sun_visor is not None:
            if sun_visor.lower() in ["true", "1"]:
                sun_visor = True
            elif sun_visor.lower() in ["false", "0"]:
                sun_visor = False
            else:
                raise HTTPException(status_code=400, detail="Invalid boolean value for sun_visor")
            
        if matrix_led_laser_headlights is not None:
            if matrix_led_laser_headlights.lower() in ["true", "1"]:
                matrix_led_laser_headlights = True
            elif matrix_led_laser_headlights.lower() in ["false", "0"]:
                matrix_led_laser_headlights = False
            else:
                raise HTTPException(status_code=400, detail="Invalid boolean value for matrix_led_laser_headlights")
            
        if automatic_headlight_on_off is not None:
            if automatic_headlight_on_off.lower() in ["true", "1"]:
                automatic_headlight_on_off = True
            elif automatic_headlight_on_off.lower() in ["false", "0"]:
                automatic_headlight_on_off = False
            else:
                raise HTTPException(status_code=400, detail="Invalid boolean value for automatic_headlight_on_off")
            
        if power_tailgate is not None:
            if power_tailgate.lower() in ["true", "1"]:
                power_tailgate = True
            elif power_tailgate.lower() in ["false", "0"]:
                power_tailgate = False
            else:
                raise HTTPException(status_code=400, detail="Invalid boolean value for power_tailgate")

        if roof_rails_roof_rack is not None:
            if roof_rails_roof_rack.lower() in ["true", "1"]:
                roof_rails_roof_rack = True
            elif roof_rails_roof_rack.lower() in ["false", "0"]:
                roof_rails_roof_rack = False
            else:
                raise HTTPException(status_code=400, detail="Invalid boolean value for roof_rails_roof_rack")

        if dual_exhaust_pipes is not None:
            if dual_exhaust_pipes.lower() in ["true", "1"]:
                dual_exhaust_pipes = True
            elif dual_exhaust_pipes.lower() in ["false", "0"]:
                dual_exhaust_pipes = False
            else:
                raise HTTPException(status_code=400, detail="Invalid boolean value for dual_exhaust_pipes")
            
        if sport_exhaust is not None:
            if sport_exhaust.lower() in ["true", "1"]:
                sport_exhaust = True
            elif sport_exhaust.lower() in ["false", "0"]:
                sport_exhaust = False
            else:
                raise HTTPException(status_code=400, detail="Invalid boolean value for sport_exhaust")

        if rear_spoiler is not None:
            if rear_spoiler.lower() in ["true", "1"]:
                rear_spoiler = True
            elif rear_spoiler.lower() in ["false", "0"]:
                rear_spoiler = False
            else:
                raise HTTPException(status_code=400, detail="Invalid boolean value for rear_spoiler")
            
        if led_dlrs_daytime_running_lights is not None:
            if led_dlrs_daytime_running_lights.lower() in ["true", "1"]:
                led_dlrs_daytime_running_lights = True
            elif led_dlrs_daytime_running_lights.lower() in ["false", "0"]:
                led_dlrs_daytime_running_lights = False
            else:
                raise HTTPException(status_code=400, detail="Invalid boolean value for led_dlrs_daytime_running_lights")
            
        if auto_folding_side_mirrors is not None:
            if auto_folding_side_mirrors.lower() in ["true", "1"]:
                auto_folding_side_mirrors = True
            elif auto_folding_side_mirrors.lower() in ["false", "0"]:
                auto_folding_side_mirrors = False
            else:
                raise HTTPException(status_code=400, detail="Invalid boolean value for auto_folding_side_mirrors")

        if frameless_doors is not None:
            if frameless_doors.lower() in ["true", "1"]:
                frameless_doors = True
            elif frameless_doors.lower() in ["false", "0"]:
                frameless_doors = False
            else:
                raise HTTPException(status_code=400, detail="Invalid boolean value for frameless_doors")

        if charging_port is not None:
            if charging_port.lower() in ["true", "1"]:
                charging_port = True
            elif charging_port.lower() in ["false", "0"]:
                charging_port = False
            else:
                raise HTTPException(status_code=400, detail="Invalid boolean value for charging_port")
            
        if soft_close_doors is not None:
            if soft_close_doors.lower() in ["true", "1"]:
                soft_close_doors = True
            elif soft_close_doors.lower() in ["false", "0"]:
                soft_close_doors = False
            else:
                raise HTTPException(status_code=400, detail="Invalid boolean value for soft_close_doors")

        if illuminated_logo_welcome_lights is not None:
            if illuminated_logo_welcome_lights.lower() in ["true", "1"]:
                illuminated_logo_welcome_lights = True
            elif illuminated_logo_welcome_lights.lower() in ["false", "0"]:
                illuminated_logo_welcome_lights = False
            else:
                raise HTTPException(status_code=400, detail="Invalid boolean value for illuminated_logo_welcome_lights")
            
        if rain_sensing_wipers is not None:
            if rain_sensing_wipers.lower() in ["true", "1"]:
                rain_sensing_wipers = True
            elif rain_sensing_wipers.lower() in ["false", "0"]:
                rain_sensing_wipers = False
            else:
                raise HTTPException(status_code=400, detail="Invalid boolean value for rain_sensing_wipers")
            
        if Performance_tyres is not None:
            if Performance_tyres.lower() in ["true", "1"]:
                Performance_tyres = True
            elif Performance_tyres.lower() in ["false", "0"]:
                Performance_tyres = False
            else:
                raise HTTPException(status_code=400, detail="Invalid boolean value for Performance_tyres")
            
        if side_mirrors_indicators is not None:
            if side_mirrors_indicators.lower() in ["true", "1"]:
                side_mirrors_indicators = True
            elif side_mirrors_indicators.lower() in ["false", "0"]:
                side_mirrors_indicators = False
            else:
                raise HTTPException(status_code=400, detail="Invalid boolean value for side_mirrors_indicators")
            
        if sports_suspension is not None:
            if sports_suspension.lower() in ["true", "1"]:
                sports_suspension = True
            elif sports_suspension.lower() in ["false", "0"]:
                sports_suspension = False
            else:
                raise HTTPException(status_code=400, detail="Invalid boolean value for sports_suspension")

        if premium_paint is not None:
            if premium_paint.lower() in ["true", "1"]:
                premium_paint = True
            elif premium_paint.lower() in ["false", "0"]:
                premium_paint = False
            else:
                raise HTTPException(status_code=400, detail="Invalid boolean value for premium_paint")

        if air_deflector is not None:
            if air_deflector.lower() in ["true", "1"]:
                air_deflector = True
            elif air_deflector.lower() in ["false", "0"]:
                air_deflector = False
            else:
                raise HTTPException(status_code=400, detail="Invalid boolean value for air_deflector")



        # All data converted to boolean now storing the data in the table

        exterior_data = VehExterior(fog_lights_front=fog_lights_front,alloy_rims=alloy_rims,high_deck=high_deck,electric_pump=electric_pump,justlow=justlow,crane_step=crane_step,HID_headlights=HID_headlights,rear_wiper=rear_wiper, sun_visor=sun_visor,matrix_led_laser_headlights=matrix_led_laser_headlights,automatic_headlight_on_off=automatic_headlight_on_off,power_tailgate=power_tailgate,roof_rails_roof_rack=roof_rails_roof_rack,dual_exhaust_pipes=dual_exhaust_pipes,sport_exhaust=sport_exhaust,rear_spoiler=rear_spoiler,led_dlrs_daytime_running_lights=led_dlrs_daytime_running_lights,auto_folding_side_mirrors=auto_folding_side_mirrors,frameless_doors=frameless_doors,charging_port=charging_port,soft_close_doors=soft_close_doors,illuminated_logo_welcome_lights=illuminated_logo_welcome_lights,rain_sensing_wipers=rain_sensing_wipers,Performance_tyres=Performance_tyres,side_mirrors_indicators=side_mirrors_indicators,sports_suspension=sports_suspension,premium_paint=premium_paint,air_deflector=air_deflector)
        exterior_data = exterior_data.model_dump()
        exterior_id = register_exterior(db, user_id, vehicle_id, VehExterior(**exterior_data))

        """Adding the features to Comfort table"""
        # changing types of values from strings to booleans
        if power_streeing is not None:
            if power_streeing.lower() in ["true", "1"]:
                power_streeing = True
            elif power_streeing.lower() in ["false", "0"]:
                power_streeing = False
            else:
                raise HTTPException(status_code=400, detail="Invalid boolean value for power_streeing")

        if push_start_smartkey is not None:
            if push_start_smartkey.lower() in ["true", "1"]:
                push_start_smartkey = True
            elif push_start_smartkey.lower() in ["false", "0"]:
                push_start_smartkey = False
            else:
                raise HTTPException(status_code=400, detail="Invalid boolean value for push_start_smartkey")

        if keyless_entry is not None:
            if keyless_entry.lower() in ["true", "1"]:
                keyless_entry = True
            elif keyless_entry.lower() in ["false", "0"]:
                keyless_entry = False
            else:
                raise HTTPException(status_code=400, detail="Invalid boolean value for keyless_entry")

        if key_start is not None:
            if key_start.lower() in ["true", "1"]:
                key_start = True
            elif key_start.lower() in ["false", "0"]:
                key_start = False
            else:
                raise HTTPException(status_code=400, detail="Invalid boolean value for key_start")

        if navigation is not None:
            if navigation.lower() in ["true", "1"]:
                navigation = True
            elif navigation.lower() in ["false", "0"]:
                navigation = False
            else:
                raise HTTPException(status_code=400, detail="Invalid boolean value for navigation")

        if remote_controller is not None:
            if remote_controller.lower() in ["true", "1"]:
                remote_controller = True
            elif remote_controller.lower() in ["false", "0"]:
                remote_controller = False
            else:
                raise HTTPException(status_code=400, detail="Invalid boolean value for remote_controller")

        if android_led is not None:
            if android_led.lower() in ["true", "1"]:
                android_led = True
            elif android_led.lower() in ["false", "0"]:
                android_led = False
            else:
                raise HTTPException(status_code=400, detail="Invalid boolean value for android_led")

        if bluetooth is not None:
            if bluetooth.lower() in ["true", "1"]:
                bluetooth = True
            elif bluetooth.lower() in ["false", "0"]:
                bluetooth = False
            else:
                raise HTTPException(status_code=400, detail="Invalid boolean value for bluetooth")

        if front_door_speaker is not None:
            if front_door_speaker.lower() in ["true", "1"]:
                front_door_speaker = True
            elif front_door_speaker.lower() in ["false", "0"]:
                front_door_speaker = False
            else:
                raise HTTPException(status_code=400, detail="Invalid boolean value for front_door_speaker")

        if rear_door_speaker is not None:
            if rear_door_speaker.lower() in ["true", "1"]:
                rear_door_speaker = True
            elif rear_door_speaker.lower() in ["false", "0"]:
                rear_door_speaker = False
            else:
                raise HTTPException(status_code=400, detail="Invalid boolean value for rear_door_speaker")

        if rear_deck_speaker is not None:
            if rear_deck_speaker.lower() in ["true", "1"]:
                rear_deck_speaker = True
            elif rear_deck_speaker.lower() in ["false", "0"]:
                rear_deck_speaker = False
            else:
                raise HTTPException(status_code=400, detail="Invalid boolean value for rear_deck_speaker")

        if ECO_mode is not None:
            if ECO_mode.lower() in ["true", "1"]:
                ECO_mode = True
            elif ECO_mode.lower() in ["false", "0"]:
                ECO_mode = False
            else:
                raise HTTPException(status_code=400, detail="Invalid boolean value for ECO_mode")

        if heated_seats is not None:
            if heated_seats.lower() in ["true", "1"]:
                heated_seats = True
            elif heated_seats.lower() in ["false", "0"]:
                heated_seats = False
            else:
                raise HTTPException(status_code=400, detail="Invalid boolean value for heated_seats")

        if power_seats is not None:
            if power_seats.lower() in ["true", "1"]:
                power_seats = True
            elif power_seats.lower() in ["false", "0"]:
                power_seats = False
            else:
                raise HTTPException(status_code=400, detail="Invalid boolean value for power_seats")

        if power_side_mirrors is not None:
            if power_side_mirrors.lower() in ["true", "1"]:
                power_side_mirrors = True
            elif power_side_mirrors.lower() in ["false", "0"]:
                power_side_mirrors = False
            else:
                raise HTTPException(status_code=400, detail="Invalid boolean value for power_side_mirrors")

        if electric_rearview_mirror is not None:
            if electric_rearview_mirror.lower() in ["true", "1"]:
                electric_rearview_mirror = True
            elif electric_rearview_mirror.lower() in ["false", "0"]:
                electric_rearview_mirror = False
            else:
                raise HTTPException(status_code=400, detail="Invalid boolean value for electric_rearview_mirror")            
        
        if dashboard_speakers is not None:
            if dashboard_speakers.lower() in ["true", "1"]:
                dashboard_speakers = True
            elif dashboard_speakers.lower() in ["false", "0"]:
                dashboard_speakers = False
            else:
                raise HTTPException(status_code=400, detail="Invalid boolean value for dashboard_speakers") 

        if wireless_apple_carplay_android_auto is not None:
            if wireless_apple_carplay_android_auto.lower() in ["true", "1"]:
                wireless_apple_carplay_android_auto = True
            elif wireless_apple_carplay_android_auto.lower() in ["false", "0"]:
                wireless_apple_carplay_android_auto = False
            else:
                raise HTTPException(status_code=400, detail="Invalid boolean value for wireless_apple_carplay_android_auto") 

        if voice_control_system is not None:
            if voice_control_system.lower() in ["true", "1"]:
                voice_control_system = True
            elif voice_control_system.lower() in ["false", "0"]:
                voice_control_system = False
            else:
                raise HTTPException(status_code=400, detail="Invalid boolean value for voice_control_system") 

        if gesture_control is not None:
            if gesture_control.lower() in ["true", "1"]:
                gesture_control = True
            elif gesture_control.lower() in ["false", "0"]:
                gesture_control = False
            else:
                raise HTTPException(status_code=400, detail="Invalid boolean value for gesture_control") 

        if remote_engine_start is not None:
            if remote_engine_start.lower() in ["true", "1"]:
                remote_engine_start = True
            elif remote_engine_start.lower() in ["false", "0"]:
                remote_engine_start = False
            else:
                raise HTTPException(status_code=400, detail="Invalid boolean value for remote_engine_start") 

        if auto_dimming_rearview_mirror is not None:
            if auto_dimming_rearview_mirror.lower() in ["true", "1"]:
                auto_dimming_rearview_mirror = True
            elif auto_dimming_rearview_mirror.lower() in ["false", "0"]:
                auto_dimming_rearview_mirror = False
            else:
                raise HTTPException(status_code=400, detail="Invalid boolean value for auto_dimming_rearview_mirror") 

        if driver_seat_massager is not None:
            if driver_seat_massager.lower() in ["true", "1"]:
                driver_seat_massager = True
            elif driver_seat_massager.lower() in ["false", "0"]:
                driver_seat_massager = False
            else:
                raise HTTPException(status_code=400, detail="Invalid boolean value for driver_seat_massager") 

        if rear_window_sunshade_manual is not None:
            if rear_window_sunshade_manual.lower() in ["true", "1"]:
                rear_window_sunshade_manual = True
            elif rear_window_sunshade_manual.lower() in ["false", "0"]:
                rear_window_sunshade_manual = False
            else:
                raise HTTPException(status_code=400, detail="Invalid boolean value for rear_window_sunshade_manual") 

        if rear_window_sunshade_electric is not None:
            if rear_window_sunshade_electric.lower() in ["true", "1"]:
                rear_window_sunshade_electric = True
            elif rear_window_sunshade_electric.lower() in ["false", "0"]:
                rear_window_sunshade_electric = False
            else:
                raise HTTPException(status_code=400, detail="Invalid boolean value for rear_window_sunshade_electric") 

        if air_purifier_ionizer is not None:
            if air_purifier_ionizer.lower() in ["true", "1"]:
                air_purifier_ionizer = True
            elif air_purifier_ionizer.lower() in ["false", "0"]:
                air_purifier_ionizer = False
            else:
                raise HTTPException(status_code=400, detail="Invalid boolean value for air_purifier_ionizer") 

        if cabin_noise_cancellation is not None:
            if cabin_noise_cancellation.lower() in ["true", "1"]:
                cabin_noise_cancellation = True
            elif cabin_noise_cancellation.lower() in ["false", "0"]:
                cabin_noise_cancellation = False
            else:
                raise HTTPException(status_code=400, detail="Invalid boolean value for cabin_noise_cancellation") 

        if smart_climate_control_ai_sensing is not None:
            if smart_climate_control_ai_sensing.lower() in ["true", "1"]:
                smart_climate_control_ai_sensing = True
            elif smart_climate_control_ai_sensing.lower() in ["false", "0"]:
                smart_climate_control_ai_sensing = False
            else:
                raise HTTPException(status_code=400, detail="Invalid boolean value for smart_climate_control_ai_sensing") 

        if ota_updates_over_the_air_software is not None:
            if ota_updates_over_the_air_software.lower() in ["true", "1"]:
                ota_updates_over_the_air_software = True
            elif ota_updates_over_the_air_software.lower() in ["false", "0"]:
                ota_updates_over_the_air_software = False
            else:
                raise HTTPException(status_code=400, detail="Invalid boolean value for ota_updates_over_the_air_software") 

        if sports_drive_mode is not None:
            if sports_drive_mode.lower() in ["true", "1"]:
                sports_drive_mode = True
            elif sports_drive_mode.lower() in ["false", "0"]:
                sports_drive_mode = False
            else:
                raise HTTPException(status_code=400, detail="Invalid boolean value for sports_drive_mode") 

        if comfort_drive_mode is not None:
            if comfort_drive_mode.lower() in ["true", "1"]:
                comfort_drive_mode = True
            elif comfort_drive_mode.lower() in ["false", "0"]:
                comfort_drive_mode = False
            else:
                raise HTTPException(status_code=400, detail="Invalid boolean value for comfort_drive_mode") 

        if snow_drive_mode is not None:
            if snow_drive_mode.lower() in ["true", "1"]:
                snow_drive_mode = True
            elif snow_drive_mode.lower() in ["false", "0"]:
                snow_drive_mode = False
            else:
                raise HTTPException(status_code=400, detail="Invalid boolean value for snow_drive_mode") 

        if intelligent_parking_assist_auto_park is not None:
            if intelligent_parking_assist_auto_park.lower() in ["true", "1"]:
                intelligent_parking_assist_auto_park = True
            elif intelligent_parking_assist_auto_park.lower() in ["false", "0"]:
                intelligent_parking_assist_auto_park = False
            else:
                raise HTTPException(status_code=400, detail="Invalid boolean value for intelligent_parking_assist_auto_park") 

        if digital_key_smartphone is not None:
            if digital_key_smartphone.lower() in ["true", "1"]:
                digital_key_smartphone = True
            elif digital_key_smartphone.lower() in ["false", "0"]:
                digital_key_smartphone = False
            else:
                raise HTTPException(status_code=400, detail="Invalid boolean value for digital_key_smartphone") 

        if electric_rear_seat_recline is not None:
            if electric_rear_seat_recline.lower() in ["true", "1"]:
                electric_rear_seat_recline = True
            elif electric_rear_seat_recline.lower() in ["false", "0"]:
                electric_rear_seat_recline = False
            else:
                raise HTTPException(status_code=400, detail="Invalid boolean value for electric_rear_seat_recline") 

        if navigation_system is not None:
            if navigation_system.lower() in ["true", "1"]:
                navigation_system = True
            elif navigation_system.lower() in ["false", "0"]:
                navigation_system = False
            else:
                raise HTTPException(status_code=400, detail="Invalid boolean value for navigation_system") 

        if power_locks is not None:
            if power_locks.lower() in ["true", "1"]:
                power_locks = True
            elif power_locks.lower() in ["false", "0"]:
                power_locks = False
            else:
                raise HTTPException(status_code=400, detail="Invalid boolean value for power_locks") 

        if tinted_windows is not None:
            if tinted_windows.lower() in ["true", "1"]:
                tinted_windows = True
            elif tinted_windows.lower() in ["false", "0"]:
                tinted_windows = False
            else:
                raise HTTPException(status_code=400, detail="Invalid boolean value for tinted_windows") 

        if rear_tv_screens is not None:
            if rear_tv_screens.lower() in ["true", "1"]:
                rear_tv_screens = True
            elif rear_tv_screens.lower() in ["false", "0"]:
                rear_tv_screens = False
            else:
                raise HTTPException(status_code=400, detail="Invalid boolean value for rear_tv_screens") 

        if cd_dvd_player is not None:
            if cd_dvd_player.lower() in ["true", "1"]:
                cd_dvd_player = True
            elif cd_dvd_player.lower() in ["false", "0"]:
                cd_dvd_player = False
            else:
                raise HTTPException(status_code=400, detail="Invalid boolean value for cd_dvd_player") 

        if mp3_interface is not None:
            if mp3_interface.lower() in ["true", "1"]:
                mp3_interface = True
            elif mp3_interface.lower() in ["false", "0"]:
                mp3_interface = False
            else:
                raise HTTPException(status_code=400, detail="Invalid boolean value for dashboard_speakers")            
        
        # All data converted to boolean now storing the data in the table

        comfort_data = ComfortConvenience(power_streeing=power_streeing,push_start_smartkey=push_start_smartkey,keyless_entry=keyless_entry,key_start=key_start,navigation=navigation,remote_controller=remote_controller,android_led=android_led,bluetooth=bluetooth,front_door_speaker=front_door_speaker,rear_door_speaker=rear_door_speaker,rear_deck_speaker=rear_deck_speaker,ECO_mode=ECO_mode,heated_seats=heated_seats, power_seats=power_seats, power_side_mirrors=power_side_mirrors, electric_rearview_mirror=electric_rearview_mirror,dashboard_speakers=dashboard_speakers,wireless_apple_carplay_android_auto=wireless_apple_carplay_android_auto,voice_control_system=voice_control_system,gesture_control=gesture_control,remote_engine_start=remote_engine_start,auto_dimming_rearview_mirror=auto_dimming_rearview_mirror,driver_seat_massager=driver_seat_massager,rear_window_sunshade_manual=rear_window_sunshade_manual,rear_window_sunshade_electric=rear_window_sunshade_electric,air_purifier_ionizer=air_purifier_ionizer,cabin_noise_cancellation=cabin_noise_cancellation,smart_climate_control_ai_sensing=smart_climate_control_ai_sensing,ota_updates_over_the_air_software=ota_updates_over_the_air_software,sports_drive_mode=sports_drive_mode,comfort_drive_mode=comfort_drive_mode,snow_drive_mode=snow_drive_mode,intelligent_parking_assist_auto_park=intelligent_parking_assist_auto_park,digital_key_smartphone=digital_key_smartphone,electric_rear_seat_recline=electric_rear_seat_recline,navigation_system=navigation_system,power_locks=power_locks,tinted_windows=tinted_windows,rear_tv_screens=rear_tv_screens,cd_dvd_player=cd_dvd_player,mp3_interface=mp3_interface)
        comfort_data = comfort_data.model_dump()
        comfort_id = register_comfort(db, user_id, vehicle_id, ComfortConvenience(**comfort_data))


        """Adding the features to dimension table"""

        dimension_data = DimensionCap(max_length=max_length,height=height,wheel_base=wheel_base,height_including_roof_rails=height_including_roof_rails,luggage_capacity_seatsup=luggage_capacity_seatsup,luggage_capacity_seatsdown=luggage_capacity_seatsdown,width=width,width_including_mirrors=width_including_mirrors,gross_vehicle_weight=gross_vehicle_weight,max_loading_weight=max_loading_weight,max_roof_load=max_roof_load,number_of_seats=number_of_seats)
        dimension_data = dimension_data.model_dump()
        dimension_id = register_dimension(db, user_id, vehicle_id, DimensionCap(**dimension_data))


        """Adding the features to engine table"""

        engine_data = EngineTrans(fuel_tank_capacity=fuel_tank_capacity,max_towing_weight_braked=max_towing_weight_braked,max_towing_weight_unbraked=max_towing_weight_unbraked,minimum_kerbweight=minimum_kerbweight,turning_circle_kerb_to_kerb=turning_circle_kerb_to_kerb)
        engine_data = engine_data.model_dump()
        engine_id = register_engine(db, user_id, vehicle_id, EngineTrans(**engine_data))


        """Adding the PerformanceFeature"""
        # changing types of values from strings to booleans
        if desmodromic_engine_technology is not None:
            if desmodromic_engine_technology.lower() in ["true", "1"]:
                desmodromic_engine_technology = True
            elif desmodromic_engine_technology.lower() in ["false", "0"]:
                desmodromic_engine_technology = False
            else:
                raise HTTPException(status_code=400, detail="Invalid boolean value for desmodromic_engine_technology")

        if fuel_injection is not None:
            if fuel_injection.lower() in ["true", "1"]:
                fuel_injection = True
            elif fuel_injection.lower() in ["false", "0"]:
                fuel_injection = False
            else:
                raise HTTPException(status_code=400, detail="Invalid boolean value for fuel_injection")

        if lightweight_design is not None:
            if lightweight_design.lower() in ["true", "1"]:
                lightweight_design = True
            elif lightweight_design.lower() in ["false", "0"]:
                lightweight_design = False
            else:
                raise HTTPException(status_code=400, detail="Invalid boolean value for lightweight_design")

        if high_performance_suspension is not None:
            if high_performance_suspension.lower() in ["true", "1"]:
                high_performance_suspension = True
            elif high_performance_suspension.lower() in ["false", "0"]:
                high_performance_suspension = False
            else:
                raise HTTPException(status_code=400, detail="Invalid boolean value for high_performance_suspension")

        # All data converted to boolean now storing the data in the table

        performance_data = PerformanceFeatureSchema(desmodromic_engine_technology=desmodromic_engine_technology,fuel_injection=fuel_injection,lightweight_design=lightweight_design,high_performance_suspension=high_performance_suspension)
        performance_data = performance_data.model_dump()
        performance_id = register_performancebike(db, user_id, vehicle_id, PerformanceFeatureSchema(**performance_data))

        """Adding the ComfortUsabilityFeaturesSchema"""
        # changing types of values from strings to booleans
        if riding_ergonomics is not None:
            if riding_ergonomics.lower() in ["true", "1"]:
                riding_ergonomics = True
            elif riding_ergonomics.lower() in ["false", "0"]:
                riding_ergonomics = False
            else:
                raise HTTPException(status_code=400, detail="Invalid boolean value for riding_ergonomics")

        if seat is not None:
            if seat.lower() in ["true", "1"]:
                seat = True
            elif seat.lower() in ["false", "0"]:
                seat = False
            else:
                raise HTTPException(status_code=400, detail="Invalid boolean value for seat")

        if instrumentation is not None:
            if instrumentation.lower() in ["true", "1"]:
                instrumentation = True
            elif instrumentation.lower() in ["false", "0"]:
                instrumentation = False
            else:
                raise HTTPException(status_code=400, detail="Invalid boolean value for instrumentation")

        if fuel_capacity is not None:
            if fuel_capacity.lower() in ["true", "1"]:
                fuel_capacity = True
            elif fuel_capacity.lower() in ["false", "0"]:
                fuel_capacity = False
            else:
                raise HTTPException(status_code=400, detail="Invalid boolean value for fuel_capacity")

        # All data converted to boolean now storing the data in the table

        comfortusability_data = ComfortUsabilityFeaturesSchema(riding_ergonomics=riding_ergonomics,seat=seat,instrumentation=instrumentation,fuel_capacity=fuel_capacity)
        comfortusability_data = comfortusability_data.model_dump()
        comfortusability_id = register_comfortusability(db, user_id, vehicle_id, ComfortUsabilityFeaturesSchema(**comfortusability_data))

        """Adding the SafetyFeaturesSchema"""
        # changing types of values from strings to booleans
        if high_performance_brakes is not None:
            if high_performance_brakes.lower() in ["true", "1"]:
                high_performance_brakes = True
            elif high_performance_brakes.lower() in ["false", "0"]:
                high_performance_brakes = False
            else:
                raise HTTPException(status_code=400, detail="Invalid boolean value for high_performance_brakes")

        if high_quality_tires is not None:
            if high_quality_tires.lower() in ["true", "1"]:
                high_quality_tires = True
            elif high_quality_tires.lower() in ["false", "0"]:
                high_quality_tires = False
            else:
                raise HTTPException(status_code=400, detail="Invalid boolean value for high_quality_tires")

        # All data converted to boolean now storing the data in the table

        safetyfeatures_data = SafetyFeaturesSchema(high_performance_brakes=high_performance_brakes,high_quality_tires=high_quality_tires)
        safetyfeatures_data = safetyfeatures_data.model_dump()
        safetyfeatures_id = register_safetyfeatures(db, user_id, vehicle_id, SafetyFeaturesSchema(**safetyfeatures_data))


        """Adding the ConvenienceFeaturesSchema"""
        # changing types of values from strings to booleans
        if lighting is not None:
            if lighting.lower() in ["true", "1"]:
                lighting = True
            elif lighting.lower() in ["false", "0"]:
                lighting = False
            else:
                raise HTTPException(status_code=400, detail="Invalid boolean value for lighting")

        if storage is not None:
            if storage.lower() in ["true", "1"]:
                storage = True
            elif storage.lower() in ["false", "0"]:
                storage = False
            else:
                raise HTTPException(status_code=400, detail="Invalid boolean value for storage")

        if security is not None:
            if security.lower() in ["true", "1"]:
                security = True
            elif security.lower() in ["false", "0"]:
                security = False
            else:
                raise HTTPException(status_code=400, detail="Invalid boolean value for security")

        if adjustable_suspension is not None:
            if adjustable_suspension.lower() in ["true", "1"]:
                adjustable_suspension = True
            elif adjustable_suspension.lower() in ["false", "0"]:
                adjustable_suspension = False
            else:
                raise HTTPException(status_code=400, detail="Invalid boolean value for adjustable_suspension")

        # All data converted to boolean now storing the data in the table

        conveniencefeatures_data = ConvenienceFeaturesSchema(lighting=lighting,storage=storage,security=security,adjustable_suspension=adjustable_suspension)
        conveniencefeatures_data = conveniencefeatures_data.model_dump()
        conveniencefeatures_id = register_conveniencefeatures(db, user_id, vehicle_id, ConvenienceFeaturesSchema(**conveniencefeatures_data))


        retval = {
            "vehicle_id": vehicle_id,
            "interior": interior_id,
            "safety_id": safety_id,
            "exterior_id": exterior_id,
            "comfort_id": comfort_id,
            "dimension_id": dimension_id, 
            "engine_id": engine_id,
            "performance_id": performance_id,
            "comfortusability_id": comfortusability_id,
            "safetyfeatures_id": safetyfeatures_id,
            "conveniencefeatures_id": conveniencefeatures_id
        }
        return {"data": retval}
    except Exception as e:
        print(traceback.format_exc())
        logging.error(f'Error occured while registering vehicle: {str(e)}')
        raise HTTPException(status_code=409, detail=f' Error: {str(e)}')



"""***********************************UPDATE VEHICLE**********************************"""

"""Updating Vehicle"""
# Updating Vehicle as a Whole including all the tables and data

@router.put("/v1/user/vehicles/{vehicle_id}")
def vehicles(vehicle_id: int, fk_bl_number: str = Form(None), body_type: str = Form(None), make: str = Form(None), model: str = Form(None), year: str = Form(None), title: str = Form(None), name: str = Form(None),chassis_number: str = Form(None),mileage: str = Form(None),damage_details: str = Form(None),transmission: str = Form(None), clynder: str = Form(None), location: str = Form(None), intcolor: str = Form(None),extcolor: str = Form(None),fuel: str = Form(None),engine: str = Form(None), status: str = Form(None),description: str = Form(None),grade: str = Form(None),score: str = Form(None),steer: str = Form(None),displacement: str = Form(None),total_price: float = Form(None),sold_price: float = Form(None),recieved_amount: float = Form(None),balance_amount: float = Form(None),auction_result: str = Form(None), condition: str = Form(None), image_interior: list[UploadFile] = File(None), image_exterior: list[UploadFile] = File(None), video: list[UploadFile] = File(None), drive_type: str = Form(None),doors: str = Form(None),engine_name: str = Form(None),supplier: str = Form(None),is_clear: bool = Form(None), report_status: str = Form(None), feature: str = Form(None), motor: str = Form(None), air_conditioner: str = Form(None), digital_odometer: str = Form(None), heater: str = Form(None),sunroof: str = Form(None),power_windows: str = Form(None),tv_led: str = Form(None), leather_seats: str = Form(None), tachometer: str = Form(None), headlight_leveler: str = Form(None), am_fm_radio: str = Form(None),armrest_console: str = Form(None),rear_seat_armrest_centre_console: str = Form(None),abs_antilock_braking: str = Form(None),child_safety_lock: str = Form(None),driver_air_bag: str = Form(None),passanger_air_bag: str = Form(None),rear_seat_air_bag: str = Form(None),curtain_air_bag: str = Form(None),power_door_lock: str = Form(None),traction_control: str = Form(None),oil_brakes: str = Form(None), air_brakes: str = Form(None),tool_kit: str = Form(None),stepney_tyre: str = Form(None),foot_parking_brake: str = Form(None),fog_lights_front: str = Form(None),alloy_rims: str = Form(None),high_deck: str = Form(None),electric_pump: str = Form(None),justlow: str = Form(None),crane_step: str = Form(None),HID_headlights: str = Form(None),rear_wiper: str = Form(None),sun_visor: str = Form(None), power_streeing: str = Form(None),push_start_smartkey: str = Form(None),keyless_entry: str = Form(None),key_start: str = Form(None),navigation: str = Form(None),remote_controller: str = Form(None),android_led: str = Form(None),bluetooth: str = Form(None),front_door_speaker: str = Form(None),rear_door_speaker: str = Form(None),rear_deck_speaker: str = Form(None),ECO_mode: str = Form(None),heated_seats: str = Form(None),power_seats: str = Form(None),power_side_mirrors: str = Form(None),electric_rearview_mirror: str = Form(None),dashboard_speakers: str = Form(None),max_length: str = Form(None),height: str = Form(None),wheel_base: str = Form(None),height_including_roof_rails: str = Form(None),luggage_capacity_seatsup: str = Form(None),luggage_capacity_seatsdown: str = Form(None),width: str = Form(None),width_including_mirrors: str = Form(None),gross_vehicle_weight: str = Form(None),max_loading_weight: str = Form(None),max_roof_load: str = Form(None),number_of_seats: str = Form(None), fuel_tank_capacity: str = Form(None),max_towing_weight_braked: str = Form(None),max_towing_weight_unbraked: str = Form(None),minimum_kerbweight: str = Form(None),turning_circle_kerb_to_kerb: str = Form(None), desmodromic_engine_technology: str = Form(None), fuel_injection: str = Form(None), lightweight_design: str = Form(None), high_performance_suspension: str = Form(None), riding_ergonomics: str = Form(None), seat: str = Form(None), instrumentation: str = Form(None), fuel_capacity: str = Form(None), high_performance_brakes: str = Form(None), high_quality_tires: str = Form(None), lighting: str = Form(None), storage: str = Form(None), security: str = Form(None), adjustable_suspension: str = Form(None), ambient_lighting_mood_lighting: str = Form(None), digital_instrument_cluster: str = Form(None), head_up_display: str = Form(None), wireless_charging_pad: str = Form(None), multi_zone_climate_control: str = Form(None), premium_sound_system: str = Form(None), wood_interior: str = Form(None), aluminum_tri_interior: str = Form(None), ventilated_seats: str = Form(None), panoramic_sunroof: str = Form(None), rear_entertainment_screens: str = Form(None), power_adjustable_steering_column: str = Form(None), memory_seats: str = Form(None), alcantara_carbon_fiber_trim: str = Form(None), alarm: str = Form(None), cooled_rear_seat: str = Form(None), wireless_smartphone_charger: str = Form(None),usb_type_c_port : str = Form(None), usb_20_port: str = Form(None), v12_power_outlet: str = Form(None), rear_charging_ports: str = Form(None), adaptive_cruise_control: str = Form(None), blind_spot_monitoring: str = Form(None), lane_keep_assist: str = Form(None), lane_departure_warning: str = Form(None), degree_360_camera: str = Form(None),front_rear_parking_sensors : str = Form(None), automatic_emergency_braking: str = Form(None), pedestrian_detection: str = Form(None), cross_traffic_alert_rear: str = Form(None), driver_attention_warning: str = Form(None), night_vision_assist: str = Form(None),tire_pressure_monitoring_system : str = Form(None),collision_mitigation_system : str = Form(None),isofix_child_seat_mounts : str = Form(None),adaptive_lighting : str = Form(None), performance_kit_tuned: str = Form(None),parking_button : str = Form(None),manual_handbrake : str = Form(None),electronic_parking_brake_auto_hold : str = Form(None),matrix_led_laser_headlights : str = Form(None),automatic_headlight_on_off: str = Form(None),power_tailgate : str = Form(None), roof_rails_roof_rack: str = Form(None), dual_exhaust_pipes: str = Form(None), sport_exhaust: str = Form(None),rear_spoiler : str = Form(None), led_dlrs_daytime_running_lights: str = Form(None),auto_folding_side_mirrors: str = Form(None), frameless_doors: str = Form(None),charging_port : str = Form(None), soft_close_doors: str = Form(None),illuminated_logo_welcome_lights : str = Form(None),rain_sensing_wipers : str = Form(None),Performance_tyres : str = Form(None), side_mirrors_indicators: str = Form(None), sports_suspension: str = Form(None), premium_paint: str = Form(None), air_deflector: str = Form(None), wireless_apple_carplay_android_auto: str = Form(None), voice_control_system: str = Form(None), gesture_control: str = Form(None), remote_engine_start: str = Form(None), auto_dimming_rearview_mirror: str = Form(None), driver_seat_massager: str = Form(None), rear_window_sunshade_manual: str = Form(None), rear_window_sunshade_electric: str = Form(None),air_purifier_ionizer : str = Form(None), cabin_noise_cancellation: str = Form(None), smart_climate_control_ai_sensing: str = Form(None),ota_updates_over_the_air_software : str = Form(None),sports_drive_mode: str = Form(None), comfort_drive_mode: str = Form(None),snow_drive_mode : str = Form(None),intelligent_parking_assist_auto_park : str = Form(None),digital_key_smartphone : str = Form(None),electric_rear_seat_recline : str = Form(None), navigation_system: str = Form(None), power_locks: str = Form(None), tinted_windows: str = Form(None), rear_tv_screens: str = Form(None),cd_dvd_player : str = Form(None), mp3_interface: str = Form(None), authorization: str = Header(None), db: Session = Depends(get_db)):
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

        user_details = db.query(ModelUser).filter(ModelUser.id==user_id).first()

        check_veh = db.query(Vehicle).filter(Vehicle.id == vehicle_id).first()
        previous_status = check_veh.status  # for notification purpose if previous status is instock and new status will be outofstock then it mean the vehicle is sold I need to display a notification
        print(previous_status)
        if check_veh is None:
            raise HTTPException(status_code=404, detail="Vehicle not found")
        print(f'engine name is: {engine_name}')

        if fk_bl_number:
            print("In if condition")
            container_data = db.query(Container).filter(Container.bl_number == fk_bl_number).first()
            if container_data is None:
                raise HTTPException(status_code=404, detail="Container not found")
            print(f"the id:{container_data.id}")
        
            vehicle_data = Vehicles(fk_container_id=container_data.id, body_type=body_type,make=make,model=model, year=year, title=title, name=name, chassis_number=chassis_number, mileage=mileage, damage_details=damage_details, transmission=transmission, clynder=clynder, location=location, intcolor=intcolor,extcolor=extcolor, fuel=fuel, engine=engine, status=status, description=description, grade=grade, score=score, steer=steer, displacement=displacement, total_price=total_price, sold_price=sold_price,recieved_amount=recieved_amount, balance_amount=balance_amount, auction_result=auction_result, condition=condition, drive_type=drive_type,doors=doors,engine_name=engine_name, is_clear=is_clear, report_status=report_status, feature=feature, motor = motor)
            # vehicle_data = vehicle_data.dict()
            # vehicle_id = upd_vehicle(db, user_id, check_veh.id, vehicle_data)
            vehicle_data = vehicle_data.dict()

            if check_veh.uploaded_by == user_details.firstname:
                vehicle_data["uploaded_by"] = user_details.firstname
            else:
                vehicle_data["uploaded_by"]=check_veh.uploaded_by
            if status == "Outofstock":
                vehicle_data["sold_by"] = user_details.firstname

            for key, value in vehicle_data.items():
                if value is not None:
                    setattr(check_veh, key, value)

            db.commit()
            db.refresh(check_veh)
            new_status = check_veh.status  # for notification purpose if previous status is instock and new status will be outofstock then it mean the vehicle is sold I need to display a notification
            print(new_status)
            if new_status != previous_status and new_status == "Outofstock":
                """Create a notification and store in Notification Table"""
                notification = Notification(
                    fk_user_id=user_id, # in future remember this is user ID not vehicle but here is dummy example for now
                    message=f"{check_veh.name} has been sold by {user_details.firstname} for {check_veh.sold_price} AED.",
                    read = False
                )
                db.add(notification)
                db.commit()
                db.refresh(notification)
            print(1)
            if new_status != previous_status:
                if previous_status=="Intransit" and new_status=="Instock":
                    """Create a notification and store in Notification Table"""
                    notification = Notification(
                        fk_user_id=user_id, # in future remember this is user ID not vehicle but here is dummy example for now
                        message=f'Status for {check_veh.name} has been changed from "in-transit" to "in-stock"',
                        read = False
                    )
                    db.add(notification)
                    db.commit()
                    db.refresh(notification)
                elif previous_status=="Instock" and new_status=="Outofstock":

                    """Create a notification and store in Notification Table"""
                    notification = Notification(
                        fk_user_id=user_id, # in future remember this is user ID not vehicle but here is dummy example for now
                        message=f'Status for {check_veh.name} has been changed from "in-stock" to "out of stock"',
                        read = False
                    )
                    db.add(notification)
                    db.commit()
                    db.refresh(notification)

        elif fk_bl_number is None:
            print("In else condition")
            vehicle_data = Vehicles(body_type=body_type,make=make,model=model, year=year, title=title, name=name, chassis_number=chassis_number, mileage=mileage, damage_details=damage_details, transmission=transmission, clynder=clynder, location=location, intcolor=intcolor,extcolor=extcolor, fuel=fuel, engine=engine, status=status, description=description, grade=grade, score=score, steer=steer, displacement=displacement, total_price=total_price, sold_price=sold_price,recieved_amount = recieved_amount, balance_amount=balance_amount, auction_result=auction_result, condition=condition, drive_type=drive_type,doors=doors,engine_name=engine_name,supplier=supplier, is_clear=is_clear, report_status=report_status, feature=feature, motor=motor)
            vehicle_data = vehicle_data.dict()

            if check_veh.uploaded_by == user_details.firstname:
                vehicle_data["uploaded_by"] = user_details.firstname
            else:
                vehicle_data["uploaded_by"]=check_veh.uploaded_by
            if status == "Outofstock":
                vehicle_data["sold_by"] = user_details.firstname

            for key, value in vehicle_data.items():
                if value is not None:
                    setattr(check_veh, key, value)

            db.commit()
            db.refresh(check_veh)
            new_status = check_veh.status  # for notification purpose if previous status is instock and new status will be outofstock then it mean the vehicle is sold I need to display a notification
            print(new_status)
            if new_status != previous_status and new_status == "Outofstock":
                """Create a notification and store in Notification Table"""
                notification = Notification(
                    fk_user_id=user_id, # in future remember this is user ID not vehicle but here is dummy example for now
                    message=f"{check_veh.name} has been sold by {user_details.firstname} for {check_veh.sold_price} AED.",
                    read = False
                )
                db.add(notification)
                db.commit()
                db.refresh(notification)
            print(2)
            if new_status != previous_status:
                if previous_status=="Intransit" and new_status=="Instock":
                    """Create a notification and store in Notification Table"""
                    notification = Notification(
                        fk_user_id=user_id, # in future remember this is user ID not vehicle but here is dummy example for now
                        message=f'Status for {check_veh.name} has been changed from "in-transit" to "in-stock"',
                        read = False
                    )
                    db.add(notification)
                    db.commit()
                    db.refresh(notification)
                elif previous_status=="Instock" and new_status=="Outofstock":

                    """Create a notification and store in Notification Table"""
                    notification = Notification(
                        fk_user_id=user_id, # in future remember this is user ID not vehicle but here is dummy example for now
                        message=f'Status for {check_veh.name} has been changed from "in-stock" to "out of stock"',
                        read = False
                    )
                    db.add(notification)
                    db.commit()
                    db.refresh(notification)
        """storing images and videos"""
        # Initialize paths
        image_paths = []
        image_paths_int = []  # for interior images
        image_paths_ext = []  # for exterior images
        video_paths = []


        # First check if we have an existing record
        existing_images = db.query(Images).filter(Images.fk_vehicle_id == vehicle_id).first()

        # Handle interior images
        if image_interior is not None:
            print("Processing interior images")
            # Delete existing interior images if they exist
            if existing_images and existing_images.image_interior:
                for old_img_path in existing_images.image_interior.split(','):
                    try:
                        if os.path.exists(old_img_path):
                            os.remove(old_img_path)
                    except Exception as e:
                        print(f"Error deleting old interior image {old_img_path}: {e}")
    
            # Save new interior images
            for img in image_interior:
                img.filename = format_image_name_int(vehicle_id, img.filename)
                file_location = os.path.join(UPLOAD_DIR_INT, img.filename)
                with open(file_location, "wb") as buffer:
                    shutil.copyfileobj(img.file, buffer)
                image_paths_int.append(file_location)
    
            images_string_int = ",".join(image_paths_int)
    
            if existing_images is None:
                existing_images = Images(
                    image_interior=images_string_int,
                    fk_vehicle_id=vehicle_id
                )
                db.add(existing_images)
            else:
                existing_images.image_interior = images_string_int
            db.commit()
        elif image_interior is None and existing_images and existing_images.image_interior:
            print("No interior images provided - clearing if they exist")
            # Delete the physical files
            for old_img_path in existing_images.image_interior.split(','):
                try:
                    if os.path.exists(old_img_path):
                        os.remove(old_img_path)
                except Exception as e:
                    print(f"Error deleting old interior image {old_img_path}: {e}")
    
            existing_images.image_interior = None
            db.commit()

        # Handle exterior images
        if image_exterior is not None:
            print("Processing exterior images")
            # Delete existing exterior images if they exist
            if existing_images and existing_images.image_exterior:
                for old_img_path in existing_images.image_exterior.split(','):
                    try:
                        if os.path.exists(old_img_path):
                            os.remove(old_img_path)
                    except Exception as e:
                        print(f"Error deleting old exterior image {old_img_path}: {e}")
    
            # Save new exterior images
            for img in image_exterior:
                img.filename = format_image_name_ext(vehicle_id, img.filename)
                file_location = os.path.join(UPLOAD_DIR_EXT, img.filename)
                with open(file_location, "wb") as buffer:
                    shutil.copyfileobj(img.file, buffer)
                image_paths_ext.append(file_location)
    
            images_string_ext = ",".join(image_paths_ext)
    
            if existing_images is None:
                existing_images = Images(
                    image_exterior=images_string_ext,
                    fk_vehicle_id=vehicle_id
                )
                db.add(existing_images)
            else:
                existing_images.image_exterior = images_string_ext
            db.commit()
        elif image_exterior is None and existing_images and existing_images.image_exterior:
            print("No exterior images provided - clearing if they exist")
            # Delete the physical files
            for old_img_path in existing_images.image_exterior.split(','):
                try:
                    if os.path.exists(old_img_path):
                        os.remove(old_img_path)
                except Exception as e:
                    print(f"Error deleting old exterior image {old_img_path}: {e}")
    
            existing_images.image_exterior = None
            db.commit()


        # Save video files to the uploads directory
        if video is not None:
            video_paths = []  # Create a separate list for video paths
    
            # First check if we have existing videos
            existing_videos = db.query(Videos).filter(Videos.fk_vehicle_id == vehicle_id).first()
    
            # Delete existing video files if they exist
            if existing_videos and existing_videos.video:
                for old_vid_path in existing_videos.video.split(','):
                    try:
                        if os.path.exists(old_vid_path):
                            os.remove(old_vid_path)
                    except Exception as e:
                        print(f"Error deleting old video {old_vid_path}: {e}")
    
            # Save new videos
            for vid in video:
                vid.filename = str(vehicle_id) + vid.filename
                file_location = os.path.join(UPLOAD_DIR, vid.filename)
                with open(file_location, "wb") as buffer:
                    shutil.copyfileobj(vid.file, buffer)
                video_paths.append(file_location)
    
            videos_string = ",".join(video_paths)
    
            # Use the actual model class (Videos) instead of the schema
            if existing_videos is None:
                new_video = Videos(  # This should be your SQLAlchemy model class
                    video=videos_string,
                    fk_vehicle_id=vehicle_id
                )
                db.add(new_video)
            else:
                existing_videos.video = videos_string
    
            db.commit()
            print(3)

        """Adding the features to interior table"""
        # check vehicle and then proceed
        checkVehicle = db.query(Vehicle).filter(Vehicle.id == vehicle_id).first()
    
        # changing types of values from strings to booleans
        if air_conditioner is not None:
            if air_conditioner.lower() in ["true", "1"]:
                air_conditioner = True
            elif air_conditioner.lower() in ["false", "0"]:
                air_conditioner = False
            else:
                raise HTTPException(status_code=400, detail="Invalid boolean value for air_conditioner")

        if digital_odometer is not None:
            if digital_odometer.lower() in ["true", "1"]:
                digital_odometer = True
            elif digital_odometer.lower() in ["false", "0"]:
                digital_odometer = False
            else:
                raise HTTPException(status_code=400, detail="Invalid boolean value for digital_odometer")

        if heater is not None:
            if heater.lower() in ["true", "1"]:
                heater = True
            elif heater.lower() in ["false", "0"]:
                heater = False
            else:
                raise HTTPException(status_code=400, detail="Invalid boolean value for heater")

        if sunroof is not None:
            if sunroof.lower() in ["true", "1"]:
                sunroof = True
            elif sunroof.lower() in ["false", "0"]:
                sunroof = False
            else:
                raise HTTPException(status_code=400, detail="Invalid boolean value for sunroof")

        if power_windows is not None:
            if power_windows.lower() in ["true", "1"]:
                power_windows = True
            elif power_windows.lower() in ["false", "0"]:
                power_windows = False
            else:
                raise HTTPException(status_code=400, detail="Invalid boolean value for power_windows")
        
        if tv_led is not None:
            if tv_led.lower() in ["true", "1"]:
                tv_led = True
            elif tv_led.lower() in ["false", "0"]:
                tv_led = False
            else:
                raise HTTPException(status_code=400, detail="Invalid boolean value for tv_led")

        if leather_seats is not None:
            if leather_seats.lower() in ["true", "1"]:
                leather_seats = True
            elif leather_seats.lower() in ["false", "0"]:
                leather_seats = False
            else:
                raise HTTPException(status_code=400, detail="Invalid boolean value for leather_seats")

        if tachometer is not None:
            if tachometer.lower() in ["true", "1"]:
                tachometer = True
            elif tachometer.lower() in ["false", "0"]:
                tachometer = False
            else:
                raise HTTPException(status_code=400, detail="Invalid boolean value for tachometer")

        if headlight_leveler is not None:
            if headlight_leveler.lower() in ["true", "1"]:
                headlight_leveler = True
            elif headlight_leveler.lower() in ["false", "0"]:
                headlight_leveler = False
            else:
                raise HTTPException(status_code=400, detail="Invalid boolean value for headlight_leveler")

        if am_fm_radio is not None:
            if am_fm_radio.lower() in ["true", "1"]:
                am_fm_radio = True
            elif am_fm_radio.lower() in ["false", "0"]:
                am_fm_radio = False
            else:
                raise HTTPException(status_code=400, detail="Invalid boolean value for am_fm_radio")


        if armrest_console is not None:
            if armrest_console.lower() in ["true", "1"]:
                armrest_console = True
            elif armrest_console.lower() in ["false", "0"]:
                armrest_console = False
            else:
                raise HTTPException(status_code=400, detail="Invalid boolean value for armrest_console")

        if rear_seat_armrest_centre_console is not None:
            if rear_seat_armrest_centre_console.lower() in ["true", "1"]:
                rear_seat_armrest_centre_console = True
            elif rear_seat_armrest_centre_console.lower() in ["false", "0"]:
                rear_seat_armrest_centre_console = False
            else:
                raise HTTPException(status_code=400, detail="Invalid boolean value for rear_seat_armrest_centre_console")

        if ambient_lighting_mood_lighting is not None:
            if ambient_lighting_mood_lighting.lower() in ["true", "1"]:
                ambient_lighting_mood_lighting = True
            elif ambient_lighting_mood_lighting.lower() in ["false", "0"]:
                ambient_lighting_mood_lighting = False
            else:
                raise HTTPException(status_code=400, detail="Invalid boolean value for ambient_lighting_mood_lighting")

        if digital_instrument_cluster is not None:
            if digital_instrument_cluster.lower() in ["true", "1"]:
                digital_instrument_cluster = True
            elif digital_instrument_cluster.lower() in ["false", "0"]:
                digital_instrument_cluster = False
            else:
                raise HTTPException(status_code=400, detail="Invalid boolean value for digital_instrument_cluster")

        if head_up_display is not None:
            if head_up_display.lower() in ["true", "1"]:
                head_up_display = True
            elif head_up_display.lower() in ["false", "0"]:
                head_up_display = False
            else:
                raise HTTPException(status_code=400, detail="Invalid boolean value for head_up_display")
            
        if wireless_charging_pad is not None:
            if wireless_charging_pad.lower() in ["true", "1"]:
                wireless_charging_pad = True
            elif wireless_charging_pad.lower() in ["false", "0"]:
                wireless_charging_pad = False
            else:
                raise HTTPException(status_code=400, detail="Invalid boolean value for wireless_charging_pad")
            
        if multi_zone_climate_control is not None:
            if multi_zone_climate_control.lower() in ["true", "1"]:
                multi_zone_climate_control = True
            elif multi_zone_climate_control.lower() in ["false", "0"]:
                multi_zone_climate_control = False
            else:
                raise HTTPException(status_code=400, detail="Invalid boolean value for multi_zone_climate_control")
            
        if premium_sound_system is not None:
            if premium_sound_system.lower() in ["true", "1"]:
                premium_sound_system = True
            elif premium_sound_system.lower() in ["false", "0"]:
                premium_sound_system = False
            else:
                raise HTTPException(status_code=400, detail="Invalid boolean value for premium_sound_system")
            
        if wood_interior is not None:
            if wood_interior.lower() in ["true", "1"]:
                wood_interior = True
            elif wood_interior.lower() in ["false", "0"]:
                wood_interior = False
            else:
                raise HTTPException(status_code=400, detail="Invalid boolean value for wood_interior")
            
        if aluminum_tri_interior is not None:
            if aluminum_tri_interior.lower() in ["true", "1"]:
                aluminum_tri_interior = True
            elif aluminum_tri_interior.lower() in ["false", "0"]:
                aluminum_tri_interior = False
            else:
                raise HTTPException(status_code=400, detail="Invalid boolean value for aluminum_tri_interior")
            
        if ventilated_seats is not None:
            if ventilated_seats.lower() in ["true", "1"]:
                ventilated_seats = True
            elif ventilated_seats.lower() in ["false", "0"]:
                ventilated_seats = False
            else:
                raise HTTPException(status_code=400, detail="Invalid boolean value for ventilated_seats")
            
        if panoramic_sunroof is not None:
            if panoramic_sunroof.lower() in ["true", "1"]:
                panoramic_sunroof = True
            elif panoramic_sunroof.lower() in ["false", "0"]:
                panoramic_sunroof = False
            else:
                raise HTTPException(status_code=400, detail="Invalid boolean value for panoramic_sunroof")
            
        if rear_entertainment_screens is not None:
            if rear_entertainment_screens.lower() in ["true", "1"]:
                rear_entertainment_screens = True
            elif rear_entertainment_screens.lower() in ["false", "0"]:
                rear_entertainment_screens = False
            else:
                raise HTTPException(status_code=400, detail="Invalid boolean value for rear_entertainment_screens")
            
        if power_adjustable_steering_column is not None:
            if power_adjustable_steering_column.lower() in ["true", "1"]:
                power_adjustable_steering_column = True
            elif power_adjustable_steering_column.lower() in ["false", "0"]:
                power_adjustable_steering_column = False
            else:
                raise HTTPException(status_code=400, detail="Invalid boolean value for power_adjustable_steering_column")
            
        if memory_seats is not None:
            if memory_seats.lower() in ["true", "1"]:
                memory_seats = True
            elif memory_seats.lower() in ["false", "0"]:
                memory_seats = False
            else:
                raise HTTPException(status_code=400, detail="Invalid boolean value for memory_seats")
            
        if alcantara_carbon_fiber_trim is not None:
            if alcantara_carbon_fiber_trim.lower() in ["true", "1"]:
                alcantara_carbon_fiber_trim = True
            elif alcantara_carbon_fiber_trim.lower() in ["false", "0"]:
                alcantara_carbon_fiber_trim = False
            else:
                raise HTTPException(status_code=400, detail="Invalid boolean value for alcantara_carbon_fiber_trim")
            
        if alarm is not None:
            if alarm.lower() in ["true", "1"]:
                alarm = True
            elif alarm.lower() in ["false", "0"]:
                alarm = False
            else:
                raise HTTPException(status_code=400, detail="Invalid boolean value for alarm")
            
        if cooled_rear_seat is not None:
            if cooled_rear_seat.lower() in ["true", "1"]:
                cooled_rear_seat = True
            elif cooled_rear_seat.lower() in ["false", "0"]:
                cooled_rear_seat = False
            else:
                raise HTTPException(status_code=400, detail="Invalid boolean value for cooled_rear_seat")
            
        if wireless_smartphone_charger is not None:
            if wireless_smartphone_charger.lower() in ["true", "1"]:
                wireless_smartphone_charger = True
            elif wireless_smartphone_charger.lower() in ["false", "0"]:
                wireless_smartphone_charger = False
            else:
                raise HTTPException(status_code=400, detail="Invalid boolean value for wireless_smartphone_charger")
            
        if usb_type_c_port is not None:
            if usb_type_c_port.lower() in ["true", "1"]:
                usb_type_c_port = True
            elif usb_type_c_port.lower() in ["false", "0"]:
                usb_type_c_port = False
            else:
                raise HTTPException(status_code=400, detail="Invalid boolean value for usb_type_c_port")
            
        if usb_20_port is not None:
            if usb_20_port.lower() in ["true", "1"]:
                usb_20_port = True
            elif usb_20_port.lower() in ["false", "0"]:
                usb_20_port = False
            else:
                raise HTTPException(status_code=400, detail="Invalid boolean value for usb_20_port")
            
        if v12_power_outlet is not None:
            if v12_power_outlet.lower() in ["true", "1"]:
                v12_power_outlet = True
            elif v12_power_outlet.lower() in ["false", "0"]:
                v12_power_outlet = False
            else:
                raise HTTPException(status_code=400, detail="Invalid boolean value for v12_power_outlet")
            
        if rear_charging_ports is not None:
            if rear_charging_ports.lower() in ["true", "1"]:
                rear_charging_ports = True
            elif rear_charging_ports.lower() in ["false", "0"]:
                rear_charging_ports = False
            else:
                raise HTTPException(status_code=400, detail="Invalid boolean value for rear_charging_ports")
            

        # All data converted to boolean now storing the data in the table
        check_intr = db.query(VehicleInterior).filter(VehicleInterior.fk_vehicle_id == vehicle_id).first()
        interior_data = VehInterior(air_conditioner=air_conditioner,digital_odometer=digital_odometer,heater=heater,sunroof=sunroof,power_windows=power_windows,tv_led=tv_led,leather_seats=leather_seats,tachometer=tachometer,headlight_leveler=headlight_leveler,am_fm_radio=am_fm_radio,armrest_console=armrest_console,rear_seat_armrest_centre_console=rear_seat_armrest_centre_console,ambient_lighting_mood_lighting=ambient_lighting_mood_lighting,digital_instrument_cluster=digital_instrument_cluster,head_up_display=head_up_display,wireless_charging_pad=wireless_charging_pad,multi_zone_climate_control=multi_zone_climate_control, premium_sound_system=premium_sound_system, wood_interior=wood_interior, aluminum_tri_interior=aluminum_tri_interior, ventilated_seats=ventilated_seats, panoramic_sunroof=panoramic_sunroof, rear_entertainment_screens=rear_entertainment_screens, power_adjustable_steering_column=power_adjustable_steering_column, memory_seats=memory_seats, alcantara_carbon_fiber_trim=alcantara_carbon_fiber_trim, alarm=alarm, cooled_rear_seat=cooled_rear_seat, wireless_smartphone_charger=wireless_smartphone_charger, usb_type_c_port=usb_type_c_port, usb_20_port=usb_20_port, v12_power_outlet=v12_power_outlet, rear_charging_ports=rear_charging_ports)
        
        for key, value in interior_data.model_dump(exclude_unset=True).items():
            setattr(check_intr, key, value)

        db.commit()
        db.refresh(check_intr)
        print(4)

        """Adding the features to Safety table"""
        # changing types of values from strings to booleans
        if abs_antilock_braking is not None:
            if abs_antilock_braking.lower() in ["true", "1"]:
                abs_antilock_braking = True
            elif abs_antilock_braking.lower() in ["false", "0"]:
                abs_antilock_braking = False
            else:
                raise HTTPException(status_code=400, detail="Invalid boolean value for abs_antilock_braking")

        if child_safety_lock is not None:
            if child_safety_lock.lower() in ["true", "1"]:
                child_safety_lock = True
            elif child_safety_lock.lower() in ["false", "0"]:
                child_safety_lock = False
            else:
                raise HTTPException(status_code=400, detail="Invalid boolean value for child_safety_lock")

        if driver_air_bag is not None:
            if driver_air_bag.lower() in ["true", "1"]:
                driver_air_bag = True
            elif driver_air_bag.lower() in ["false", "0"]:
                driver_air_bag = False
            else:
                raise HTTPException(status_code=400, detail="Invalid boolean value for driver_air_bag")

        if passanger_air_bag is not None:
            if passanger_air_bag.lower() in ["true", "1"]:
                passanger_air_bag = True
            elif passanger_air_bag.lower() in ["false", "0"]:
                passanger_air_bag = False
            else:
                raise HTTPException(status_code=400, detail="Invalid boolean value for passanger_air_bag")

        if rear_seat_air_bag is not None:
            if rear_seat_air_bag.lower() in ["true", "1"]:
                rear_seat_air_bag = True
            elif rear_seat_air_bag.lower() in ["false", "0"]:
                rear_seat_air_bag = False
            else:
                raise HTTPException(status_code=400, detail="Invalid boolean value for rear_seat_air_bag")

        if curtain_air_bag is not None:
            if curtain_air_bag.lower() in ["true", "1"]:
                curtain_air_bag = True
            elif curtain_air_bag.lower() in ["false", "0"]:
                curtain_air_bag = False
            else:
                raise HTTPException(status_code=400, detail="Invalid boolean value for curtain_air_bag")

        if power_door_lock is not None:
            if power_door_lock.lower() in ["true", "1"]:
                power_door_lock = True
            elif power_door_lock.lower() in ["false", "0"]:
                power_door_lock = False
            else:
                raise HTTPException(status_code=400, detail="Invalid boolean value for power_door_lock")

        if traction_control is not None:
            if traction_control.lower() in ["true", "1"]:
                traction_control = True
            elif traction_control.lower() in ["false", "0"]:
                traction_control = False
            else:
                raise HTTPException(status_code=400, detail="Invalid boolean value for traction_control")
    
        if oil_brakes is not None:
            if oil_brakes.lower() in ["true", "1"]:
                oil_brakes = True
            elif oil_brakes.lower() in ["false", "0"]:
                oil_brakes = False
            else:
                raise HTTPException(status_code=400, detail="Invalid boolean value for oil_brakes")

        if air_brakes is not None:
            if air_brakes.lower() in ["true", "1"]:
                air_brakes = True
            elif air_brakes.lower() in ["false", "0"]:
                air_brakes = False
            else:
                raise HTTPException(status_code=400, detail="Invalid boolean value for air_brakes")

        if tool_kit is not None:
            if tool_kit.lower() in ["true", "1"]:
                tool_kit = True
            elif tool_kit.lower() in ["false", "0"]:
                tool_kit = False
            else:
                raise HTTPException(status_code=400, detail="Invalid boolean value for tool_kit")

        if stepney_tyre is not None:
            if stepney_tyre.lower() in ["true", "1"]:
                stepney_tyre = True
            elif stepney_tyre.lower() in ["false", "0"]:
                stepney_tyre = False
            else:
                raise HTTPException(status_code=400, detail="Invalid boolean value for stepney_tyre")

        if foot_parking_brake is not None:
            if foot_parking_brake.lower() in ["true", "1"]:
                foot_parking_brake = True
            elif foot_parking_brake.lower() in ["false", "0"]:
                foot_parking_brake = False
            else:
                raise HTTPException(status_code=400, detail="Invalid boolean value for foot_parking_brake")

            
        if adaptive_cruise_control is not None:
            if adaptive_cruise_control.lower() in ["true", "1"]:
                foot_parkadaptive_cruise_controling_brake = True
            elif adaptive_cruise_control.lower() in ["false", "0"]:
                adaptive_cruise_control = False
            else:
                raise HTTPException(status_code=400, detail="Invalid boolean value for adaptive_cruise_control")
            
        if blind_spot_monitoring is not None:
            if blind_spot_monitoring.lower() in ["true", "1"]:
                blind_spot_monitoring = True
            elif blind_spot_monitoring.lower() in ["false", "0"]:
                blind_spot_monitoring = False
            else:
                raise HTTPException(status_code=400, detail="Invalid boolean value for blind_spot_monitoring")
            
        if lane_keep_assist is not None:
            if lane_keep_assist.lower() in ["true", "1"]:
                lane_keep_assist = True
            elif lane_keep_assist.lower() in ["false", "0"]:
                lane_keep_assist = False
            else:
                raise HTTPException(status_code=400, detail="Invalid boolean value for lane_keep_assist")
            
        if lane_departure_warning is not None:
            if lane_departure_warning.lower() in ["true", "1"]:
                lane_departure_warning = True
            elif lane_departure_warning.lower() in ["false", "0"]:
                lane_departure_warning = False
            else:
                raise HTTPException(status_code=400, detail="Invalid boolean value for lane_departure_warning")
            
        if degree_360_camera is not None:
            if degree_360_camera.lower() in ["true", "1"]:
                degree_360_camera = True
            elif degree_360_camera.lower() in ["false", "0"]:
                degree_360_camera = False
            else:
                raise HTTPException(status_code=400, detail="Invalid boolean value for degree_360_camera")
            
        if front_rear_parking_sensors is not None:
            if front_rear_parking_sensors.lower() in ["true", "1"]:
                front_rear_parking_sensors = True
            elif front_rear_parking_sensors.lower() in ["false", "0"]:
                front_rear_parking_sensors = False
            else:
                raise HTTPException(status_code=400, detail="Invalid boolean value for front_rear_parking_sensors")
            
        if automatic_emergency_braking is not None:
            if automatic_emergency_braking.lower() in ["true", "1"]:
                automatic_emergency_braking = True
            elif automatic_emergency_braking.lower() in ["false", "0"]:
                automatic_emergency_braking = False
            else:
                raise HTTPException(status_code=400, detail="Invalid boolean value for automatic_emergency_braking")
            
        if pedestrian_detection is not None:
            if pedestrian_detection.lower() in ["true", "1"]:
                pedestrian_detection = True
            elif pedestrian_detection.lower() in ["false", "0"]:
                pedestrian_detection = False
            else:
                raise HTTPException(status_code=400, detail="Invalid boolean value for pedestrian_detection")
            
        if cross_traffic_alert_rear is not None:
            if cross_traffic_alert_rear.lower() in ["true", "1"]:
                cross_traffic_alert_rear = True
            elif cross_traffic_alert_rear.lower() in ["false", "0"]:
                cross_traffic_alert_rear = False
            else:
                raise HTTPException(status_code=400, detail="Invalid boolean value for cross_traffic_alert_rear")
            
        if driver_attention_warning is not None:
            if driver_attention_warning.lower() in ["true", "1"]:
                driver_attention_warning = True
            elif driver_attention_warning.lower() in ["false", "0"]:
                driver_attention_warning = False
            else:
                raise HTTPException(status_code=400, detail="Invalid boolean value for driver_attention_warning")
            
        if night_vision_assist is not None:
            if night_vision_assist.lower() in ["true", "1"]:
                night_vision_assist = True
            elif night_vision_assist.lower() in ["false", "0"]:
                night_vision_assist = False
            else:
                raise HTTPException(status_code=400, detail="Invalid boolean value for night_vision_assist")
            
        if tire_pressure_monitoring_system is not None:
            if tire_pressure_monitoring_system.lower() in ["true", "1"]:
                tire_pressure_monitoring_system = True
            elif tire_pressure_monitoring_system.lower() in ["false", "0"]:
                tire_pressure_monitoring_system = False
            else:
                raise HTTPException(status_code=400, detail="Invalid boolean value for tire_pressure_monitoring_system")
            
        if collision_mitigation_system is not None:
            if collision_mitigation_system.lower() in ["true", "1"]:
                collision_mitigation_system = True
            elif collision_mitigation_system.lower() in ["false", "0"]:
                collision_mitigation_system = False
            else:
                raise HTTPException(status_code=400, detail="Invalid boolean value for collision_mitigation_system")
            
        if isofix_child_seat_mounts is not None:
            if isofix_child_seat_mounts.lower() in ["true", "1"]:
                isofix_child_seat_mounts = True
            elif isofix_child_seat_mounts.lower() in ["false", "0"]:
                isofix_child_seat_mounts = False
            else:
                raise HTTPException(status_code=400, detail="Invalid boolean value for isofix_child_seat_mounts")
            
        if adaptive_lighting is not None:
            if adaptive_lighting.lower() in ["true", "1"]:
                adaptive_lighting = True
            elif adaptive_lighting.lower() in ["false", "0"]:
                adaptive_lighting = False
            else:
                raise HTTPException(status_code=400, detail="Invalid boolean value for adaptive_lighting")
            
        if performance_kit_tuned is not None:
            if performance_kit_tuned.lower() in ["true", "1"]:
                performance_kit_tuned = True
            elif performance_kit_tuned.lower() in ["false", "0"]:
                performance_kit_tuned = False
            else:
                raise HTTPException(status_code=400, detail="Invalid boolean value for performance_kit_tuned")
            
        if parking_button is not None:
            if parking_button.lower() in ["true", "1"]:
                parking_button = True
            elif parking_button.lower() in ["false", "0"]:
                parking_button = False
            else:
                raise HTTPException(status_code=400, detail="Invalid boolean value for parking_button")
            
        if manual_handbrake is not None:
            if manual_handbrake.lower() in ["true", "1"]:
                manual_handbrake = True
            elif manual_handbrake.lower() in ["false", "0"]:
                manual_handbrake = False
            else:
                raise HTTPException(status_code=400, detail="Invalid boolean value for manual_handbrake")
            
        if electronic_parking_brake_auto_hold is not None:
            if electronic_parking_brake_auto_hold.lower() in ["true", "1"]:
                electronic_parking_brake_auto_hold = True
            elif electronic_parking_brake_auto_hold.lower() in ["false", "0"]:
                electronic_parking_brake_auto_hold = False
            else:
                raise HTTPException(status_code=400, detail="Invalid boolean value for electronic_parking_brake_auto_hold")


        # All data converted to boolean now storing the data in the table
        check_safety = db.query(VehicleSafety).filter(VehicleSafety.fk_vehicle_id == vehicle_id).first()       
        safety_data = VehSafety(abs_antilock_braking=abs_antilock_braking,child_safety_lock=child_safety_lock,driver_air_bag=driver_air_bag,passanger_air_bag=passanger_air_bag,rear_seat_air_bag=rear_seat_air_bag,curtain_air_bag=curtain_air_bag,power_door_lock=power_door_lock,traction_control=traction_control,oil_brakes=oil_brakes,air_brakes=air_brakes,tool_kit=tool_kit,stepney_tyre=stepney_tyre,foot_parking_brake=foot_parking_brake,adaptive_cruise_control=adaptive_cruise_control,blind_spot_monitoring=blind_spot_monitoring,lane_keep_assist=lane_keep_assist,lane_departure_warning=lane_departure_warning,degree_360_camera=degree_360_camera,front_rear_parking_sensors=front_rear_parking_sensors,automatic_emergency_braking=automatic_emergency_braking,pedestrian_detection=pedestrian_detection,cross_traffic_alert_rear=cross_traffic_alert_rear,driver_attention_warning=driver_attention_warning,night_vision_assist=night_vision_assist,tire_pressure_monitoring_system=tire_pressure_monitoring_system,collision_mitigation_system=collision_mitigation_system,isofix_child_seat_mounts=isofix_child_seat_mounts,adaptive_lighting=adaptive_lighting,performance_kit_tuned=performance_kit_tuned,parking_button=parking_button,manual_handbrake=manual_handbrake,electronic_parking_brake_auto_hold=electronic_parking_brake_auto_hold)

        for key, value in safety_data.model_dump(exclude_unset=True).items():
            setattr(check_safety, key, value)

        db.commit()
        db.refresh(check_safety)
        print(5)

        """Adding the features to Exterior table"""
        # changing types of values from strings to booleans
        if fog_lights_front is not None:
            if fog_lights_front.lower() in ["true", "1"]:
                fog_lights_front = True
            elif fog_lights_front.lower() in ["false", "0"]:
                fog_lights_front = False
            else:
                raise HTTPException(status_code=400, detail="Invalid boolean value for fog_lights_front")

        if alloy_rims is not None:
            if alloy_rims.lower() in ["true", "1"]:
                alloy_rims = True
            elif alloy_rims.lower() in ["false", "0"]:
                alloy_rims = False
            else:
                raise HTTPException(status_code=400, detail="Invalid boolean value for alloy_rims")

        if high_deck is not None:
            if high_deck.lower() in ["true", "1"]:
                high_deck = True
            elif high_deck.lower() in ["false", "0"]:
                high_deck = False
            else:
                raise HTTPException(status_code=400, detail="Invalid boolean value for high_deck")

        if electric_pump is not None:
            if electric_pump.lower() in ["true", "1"]:
                electric_pump = True
            elif electric_pump.lower() in ["false", "0"]:
                electric_pump = False
            else:
                raise HTTPException(status_code=400, detail="Invalid boolean value for electric_pump")

        if justlow is not None:
            if justlow.lower() in ["true", "1"]:
                justlow = True
            elif justlow.lower() in ["false", "0"]:
                justlow = False
            else:
                raise HTTPException(status_code=400, detail="Invalid boolean value for justlow")

        if crane_step is not None:
            if crane_step.lower() in ["true", "1"]:
                crane_step = True
            elif crane_step.lower() in ["false", "0"]:
                crane_step = False
            else:
                raise HTTPException(status_code=400, detail="Invalid boolean value for crane_step")

        if HID_headlights is not None:
            if HID_headlights.lower() in ["true", "1"]:
                HID_headlights = True
            elif HID_headlights.lower() in ["false", "0"]:
                HID_headlights = False
            else:
                raise HTTPException(status_code=400, detail="Invalid boolean value for HID_headlights")

        if rear_wiper is not None:
            if rear_wiper.lower() in ["true", "1"]:
                rear_wiper = True
            elif rear_wiper.lower() in ["false", "0"]:
                rear_wiper = False
            else:
                raise HTTPException(status_code=400, detail="Invalid boolean value for rear_wiper")

        if sun_visor is not None:
            if sun_visor.lower() in ["true", "1"]:
                sun_visor = True
            elif sun_visor.lower() in ["false", "0"]:
                sun_visor = False
            else:
                raise HTTPException(status_code=400, detail="Invalid boolean value for sun_visor")

            
        if matrix_led_laser_headlights is not None:
            if matrix_led_laser_headlights.lower() in ["true", "1"]:
                matrix_led_laser_headlights = True
            elif matrix_led_laser_headlights.lower() in ["false", "0"]:
                matrix_led_laser_headlights = False
            else:
                raise HTTPException(status_code=400, detail="Invalid boolean value for matrix_led_laser_headlights")
            
        if automatic_headlight_on_off is not None:
            if automatic_headlight_on_off.lower() in ["true", "1"]:
                automatic_headlight_on_off = True
            elif automatic_headlight_on_off.lower() in ["false", "0"]:
                automatic_headlight_on_off = False
            else:
                raise HTTPException(status_code=400, detail="Invalid boolean value for automatic_headlight_on_off")
            
        if power_tailgate is not None:
            if power_tailgate.lower() in ["true", "1"]:
                power_tailgate = True
            elif power_tailgate.lower() in ["false", "0"]:
                power_tailgate = False
            else:
                raise HTTPException(status_code=400, detail="Invalid boolean value for power_tailgate")

        if roof_rails_roof_rack is not None:
            if roof_rails_roof_rack.lower() in ["true", "1"]:
                roof_rails_roof_rack = True
            elif roof_rails_roof_rack.lower() in ["false", "0"]:
                roof_rails_roof_rack = False
            else:
                raise HTTPException(status_code=400, detail="Invalid boolean value for roof_rails_roof_rack")

        if dual_exhaust_pipes is not None:
            if dual_exhaust_pipes.lower() in ["true", "1"]:
                dual_exhaust_pipes = True
            elif dual_exhaust_pipes.lower() in ["false", "0"]:
                dual_exhaust_pipes = False
            else:
                raise HTTPException(status_code=400, detail="Invalid boolean value for dual_exhaust_pipes")
            
        if sport_exhaust is not None:
            if sport_exhaust.lower() in ["true", "1"]:
                sport_exhaust = True
            elif sport_exhaust.lower() in ["false", "0"]:
                sport_exhaust = False
            else:
                raise HTTPException(status_code=400, detail="Invalid boolean value for sport_exhaust")

        if rear_spoiler is not None:
            if rear_spoiler.lower() in ["true", "1"]:
                rear_spoiler = True
            elif rear_spoiler.lower() in ["false", "0"]:
                rear_spoiler = False
            else:
                raise HTTPException(status_code=400, detail="Invalid boolean value for rear_spoiler")
            
        if led_dlrs_daytime_running_lights is not None:
            if led_dlrs_daytime_running_lights.lower() in ["true", "1"]:
                led_dlrs_daytime_running_lights = True
            elif led_dlrs_daytime_running_lights.lower() in ["false", "0"]:
                led_dlrs_daytime_running_lights = False
            else:
                raise HTTPException(status_code=400, detail="Invalid boolean value for led_dlrs_daytime_running_lights")
            
        if auto_folding_side_mirrors is not None:
            if auto_folding_side_mirrors.lower() in ["true", "1"]:
                auto_folding_side_mirrors = True
            elif auto_folding_side_mirrors.lower() in ["false", "0"]:
                auto_folding_side_mirrors = False
            else:
                raise HTTPException(status_code=400, detail="Invalid boolean value for auto_folding_side_mirrors")

        if frameless_doors is not None:
            if frameless_doors.lower() in ["true", "1"]:
                frameless_doors = True
            elif frameless_doors.lower() in ["false", "0"]:
                frameless_doors = False
            else:
                raise HTTPException(status_code=400, detail="Invalid boolean value for frameless_doors")

        if charging_port is not None:
            if charging_port.lower() in ["true", "1"]:
                charging_port = True
            elif charging_port.lower() in ["false", "0"]:
                charging_port = False
            else:
                raise HTTPException(status_code=400, detail="Invalid boolean value for charging_port")
            
        if soft_close_doors is not None:
            if soft_close_doors.lower() in ["true", "1"]:
                soft_close_doors = True
            elif soft_close_doors.lower() in ["false", "0"]:
                soft_close_doors = False
            else:
                raise HTTPException(status_code=400, detail="Invalid boolean value for soft_close_doors")

        if illuminated_logo_welcome_lights is not None:
            if illuminated_logo_welcome_lights.lower() in ["true", "1"]:
                illuminated_logo_welcome_lights = True
            elif illuminated_logo_welcome_lights.lower() in ["false", "0"]:
                illuminated_logo_welcome_lights = False
            else:
                raise HTTPException(status_code=400, detail="Invalid boolean value for illuminated_logo_welcome_lights")
            
        if rain_sensing_wipers is not None:
            if rain_sensing_wipers.lower() in ["true", "1"]:
                rain_sensing_wipers = True
            elif rain_sensing_wipers.lower() in ["false", "0"]:
                rain_sensing_wipers = False
            else:
                raise HTTPException(status_code=400, detail="Invalid boolean value for rain_sensing_wipers")
            
        if Performance_tyres is not None:
            if Performance_tyres.lower() in ["true", "1"]:
                Performance_tyres = True
            elif Performance_tyres.lower() in ["false", "0"]:
                Performance_tyres = False
            else:
                raise HTTPException(status_code=400, detail="Invalid boolean value for Performance_tyres")
            
        if side_mirrors_indicators is not None:
            if side_mirrors_indicators.lower() in ["true", "1"]:
                side_mirrors_indicators = True
            elif side_mirrors_indicators.lower() in ["false", "0"]:
                side_mirrors_indicators = False
            else:
                raise HTTPException(status_code=400, detail="Invalid boolean value for side_mirrors_indicators")
            
        if sports_suspension is not None:
            if sports_suspension.lower() in ["true", "1"]:
                sports_suspension = True
            elif sports_suspension.lower() in ["false", "0"]:
                sports_suspension = False
            else:
                raise HTTPException(status_code=400, detail="Invalid boolean value for sports_suspension")

        if premium_paint is not None:
            if premium_paint.lower() in ["true", "1"]:
                premium_paint = True
            elif premium_paint.lower() in ["false", "0"]:
                premium_paint = False
            else:
                raise HTTPException(status_code=400, detail="Invalid boolean value for premium_paint")

        if air_deflector is not None:
            if air_deflector.lower() in ["true", "1"]:
                air_deflector = True
            elif air_deflector.lower() in ["false", "0"]:
                air_deflector = False
            else:
                raise HTTPException(status_code=400, detail="Invalid boolean value for air_deflector")

        # All data converted to boolean now storing the data in the table
        check_extr = db.query(VehicleExterior).filter(VehicleExterior.fk_vehicle_id == vehicle_id).first()
        exterior_data = VehExterior(fog_lights_front=fog_lights_front,alloy_rims=alloy_rims,high_deck=high_deck,electric_pump=electric_pump,justlow=justlow,crane_step=crane_step,HID_headlights=HID_headlights,rear_wiper=rear_wiper,sun_visor=sun_visor,matrix_led_laser_headlights=matrix_led_laser_headlights,automatic_headlight_on_off=automatic_headlight_on_off,power_tailgate=power_tailgate,roof_rails_roof_rack=roof_rails_roof_rack,dual_exhaust_pipes=dual_exhaust_pipes,sport_exhaust=sport_exhaust,rear_spoiler=rear_spoiler,led_dlrs_daytime_running_lights=led_dlrs_daytime_running_lights,auto_folding_side_mirrors=auto_folding_side_mirrors,frameless_doors=frameless_doors,charging_port=charging_port,soft_close_doors=soft_close_doors,illuminated_logo_welcome_lights=illuminated_logo_welcome_lights,rain_sensing_wipers=rain_sensing_wipers,Performance_tyres=Performance_tyres,side_mirrors_indicators=side_mirrors_indicators,sports_suspension=sports_suspension,premium_paint=premium_paint,air_deflector=air_deflector)

        for key, value in exterior_data.model_dump(exclude_unset=True).items():
            setattr(check_extr, key, value)

        db.commit()
        db.refresh(check_extr)
        print(6)
        """Adding the features to Comfort table"""
        # changing types of values from strings to booleans
        if power_streeing is not None:
            if power_streeing.lower() in ["true", "1"]:
                power_streeing = True
            elif power_streeing.lower() in ["false", "0"]:
                power_streeing = False
            else:
                raise HTTPException(status_code=400, detail="Invalid boolean value for power_streeing")

        if push_start_smartkey is not None:
            if push_start_smartkey.lower() in ["true", "1"]:
                push_start_smartkey = True
            elif push_start_smartkey.lower() in ["false", "0"]:
                push_start_smartkey = False
            else:
                raise HTTPException(status_code=400, detail="Invalid boolean value for push_start_smartkey")

        if keyless_entry is not None:
            if keyless_entry.lower() in ["true", "1"]:
                keyless_entry = True
            elif keyless_entry.lower() in ["false", "0"]:
                keyless_entry = False
            else:
                raise HTTPException(status_code=400, detail="Invalid boolean value for keyless_entry")

        if key_start is not None:
            if key_start.lower() in ["true", "1"]:
                key_start = True
            elif key_start.lower() in ["false", "0"]:
                key_start = False
            else:
                raise HTTPException(status_code=400, detail="Invalid boolean value for key_start")

        if navigation is not None:
            if navigation.lower() in ["true", "1"]:
                navigation = True
            elif navigation.lower() in ["false", "0"]:
                navigation = False
            else:
                raise HTTPException(status_code=400, detail="Invalid boolean value for navigation")

        if remote_controller is not None:
            if remote_controller.lower() in ["true", "1"]:
                remote_controller = True
            elif remote_controller.lower() in ["false", "0"]:
                remote_controller = False
            else:
                raise HTTPException(status_code=400, detail="Invalid boolean value for remote_controller")

        if android_led is not None:
            if android_led.lower() in ["true", "1"]:
                android_led = True
            elif android_led.lower() in ["false", "0"]:
                android_led = False
            else:
                raise HTTPException(status_code=400, detail="Invalid boolean value for android_led")

        if bluetooth is not None:
            if bluetooth.lower() in ["true", "1"]:
                bluetooth = True
            elif bluetooth.lower() in ["false", "0"]:
                bluetooth = False
            else:
                raise HTTPException(status_code=400, detail="Invalid boolean value for bluetooth")

        if front_door_speaker is not None:
            if front_door_speaker.lower() in ["true", "1"]:
                front_door_speaker = True
            elif front_door_speaker.lower() in ["false", "0"]:
                front_door_speaker = False
            else:
                raise HTTPException(status_code=400, detail="Invalid boolean value for front_door_speaker")

        if rear_door_speaker is not None:
            if rear_door_speaker.lower() in ["true", "1"]:
                rear_door_speaker = True
            elif rear_door_speaker.lower() in ["false", "0"]:
                rear_door_speaker = False
            else:
                raise HTTPException(status_code=400, detail="Invalid boolean value for rear_door_speaker")

        if rear_deck_speaker is not None:
            if rear_deck_speaker.lower() in ["true", "1"]:
                rear_deck_speaker = True
            elif rear_deck_speaker.lower() in ["false", "0"]:
                rear_deck_speaker = False
            else:
                raise HTTPException(status_code=400, detail="Invalid boolean value for rear_deck_speaker")

        if ECO_mode is not None:
            if ECO_mode.lower() in ["true", "1"]:
                ECO_mode = True
            elif ECO_mode.lower() in ["false", "0"]:
                ECO_mode = False
            else:
                raise HTTPException(status_code=400, detail="Invalid boolean value for ECO_mode")

        if heated_seats is not None:
            if heated_seats.lower() in ["true", "1"]:
                heated_seats = True
            elif heated_seats.lower() in ["false", "0"]:
                heated_seats = False
            else:
                raise HTTPException(status_code=400, detail="Invalid boolean value for heated_seats")

        if power_seats is not None:
            if power_seats.lower() in ["true", "1"]:
                power_seats = True
            elif power_seats.lower() in ["false", "0"]:
                power_seats = False
            else:
                raise HTTPException(status_code=400, detail="Invalid boolean value for power_seats")

        if power_side_mirrors is not None:
            if power_side_mirrors.lower() in ["true", "1"]:
                power_side_mirrors = True
            elif power_side_mirrors.lower() in ["false", "0"]:
                power_side_mirrors = False
            else:
                raise HTTPException(status_code=400, detail="Invalid boolean value for power_side_mirrors")

        if electric_rearview_mirror is not None:
            if electric_rearview_mirror.lower() in ["true", "1"]:
                electric_rearview_mirror = True
            elif electric_rearview_mirror.lower() in ["false", "0"]:
                electric_rearview_mirror = False
            else:
                raise HTTPException(status_code=400, detail="Invalid boolean value for electric_rearview_mirror")            

        if dashboard_speakers is not None:
            if dashboard_speakers.lower() in ["true", "1"]:
                dashboard_speakers = True
            elif dashboard_speakers.lower() in ["false", "0"]:
                dashboard_speakers = False
            else:
                raise HTTPException(status_code=400, detail="Invalid boolean value for dashboard_speakers")            


        if wireless_apple_carplay_android_auto is not None:
            if wireless_apple_carplay_android_auto.lower() in ["true", "1"]:
                wireless_apple_carplay_android_auto = True
            elif wireless_apple_carplay_android_auto.lower() in ["false", "0"]:
                wireless_apple_carplay_android_auto = False
            else:
                raise HTTPException(status_code=400, detail="Invalid boolean value for wireless_apple_carplay_android_auto") 

        if voice_control_system is not None:
            if voice_control_system.lower() in ["true", "1"]:
                voice_control_system = True
            elif voice_control_system.lower() in ["false", "0"]:
                voice_control_system = False
            else:
                raise HTTPException(status_code=400, detail="Invalid boolean value for voice_control_system") 

        if gesture_control is not None:
            if gesture_control.lower() in ["true", "1"]:
                gesture_control = True
            elif gesture_control.lower() in ["false", "0"]:
                gesture_control = False
            else:
                raise HTTPException(status_code=400, detail="Invalid boolean value for gesture_control") 

        if remote_engine_start is not None:
            if remote_engine_start.lower() in ["true", "1"]:
                remote_engine_start = True
            elif remote_engine_start.lower() in ["false", "0"]:
                remote_engine_start = False
            else:
                raise HTTPException(status_code=400, detail="Invalid boolean value for remote_engine_start") 

        if auto_dimming_rearview_mirror is not None:
            if auto_dimming_rearview_mirror.lower() in ["true", "1"]:
                auto_dimming_rearview_mirror = True
            elif auto_dimming_rearview_mirror.lower() in ["false", "0"]:
                auto_dimming_rearview_mirror = False
            else:
                raise HTTPException(status_code=400, detail="Invalid boolean value for auto_dimming_rearview_mirror") 

        if driver_seat_massager is not None:
            if driver_seat_massager.lower() in ["true", "1"]:
                driver_seat_massager = True
            elif driver_seat_massager.lower() in ["false", "0"]:
                driver_seat_massager = False
            else:
                raise HTTPException(status_code=400, detail="Invalid boolean value for driver_seat_massager") 

        if rear_window_sunshade_manual is not None:
            if rear_window_sunshade_manual.lower() in ["true", "1"]:
                rear_window_sunshade_manual = True
            elif rear_window_sunshade_manual.lower() in ["false", "0"]:
                rear_window_sunshade_manual = False
            else:
                raise HTTPException(status_code=400, detail="Invalid boolean value for rear_window_sunshade_manual") 

        if rear_window_sunshade_electric is not None:
            if rear_window_sunshade_electric.lower() in ["true", "1"]:
                rear_window_sunshade_electric = True
            elif rear_window_sunshade_electric.lower() in ["false", "0"]:
                rear_window_sunshade_electric = False
            else:
                raise HTTPException(status_code=400, detail="Invalid boolean value for rear_window_sunshade_electric") 

        if air_purifier_ionizer is not None:
            if air_purifier_ionizer.lower() in ["true", "1"]:
                air_purifier_ionizer = True
            elif air_purifier_ionizer.lower() in ["false", "0"]:
                air_purifier_ionizer = False
            else:
                raise HTTPException(status_code=400, detail="Invalid boolean value for air_purifier_ionizer") 

        if cabin_noise_cancellation is not None:
            if cabin_noise_cancellation.lower() in ["true", "1"]:
                cabin_noise_cancellation = True
            elif cabin_noise_cancellation.lower() in ["false", "0"]:
                cabin_noise_cancellation = False
            else:
                raise HTTPException(status_code=400, detail="Invalid boolean value for cabin_noise_cancellation") 

        if smart_climate_control_ai_sensing is not None:
            if smart_climate_control_ai_sensing.lower() in ["true", "1"]:
                smart_climate_control_ai_sensing = True
            elif smart_climate_control_ai_sensing.lower() in ["false", "0"]:
                smart_climate_control_ai_sensing = False
            else:
                raise HTTPException(status_code=400, detail="Invalid boolean value for smart_climate_control_ai_sensing") 

        if ota_updates_over_the_air_software is not None:
            if ota_updates_over_the_air_software.lower() in ["true", "1"]:
                ota_updates_over_the_air_software = True
            elif ota_updates_over_the_air_software.lower() in ["false", "0"]:
                ota_updates_over_the_air_software = False
            else:
                raise HTTPException(status_code=400, detail="Invalid boolean value for ota_updates_over_the_air_software") 

        if sports_drive_mode is not None:
            if sports_drive_mode.lower() in ["true", "1"]:
                sports_drive_mode = True
            elif sports_drive_mode.lower() in ["false", "0"]:
                sports_drive_mode = False
            else:
                raise HTTPException(status_code=400, detail="Invalid boolean value for sports_drive_mode") 

        if comfort_drive_mode is not None:
            if comfort_drive_mode.lower() in ["true", "1"]:
                comfort_drive_mode = True
            elif comfort_drive_mode.lower() in ["false", "0"]:
                comfort_drive_mode = False
            else:
                raise HTTPException(status_code=400, detail="Invalid boolean value for comfort_drive_mode") 

        if snow_drive_mode is not None:
            if snow_drive_mode.lower() in ["true", "1"]:
                snow_drive_mode = True
            elif snow_drive_mode.lower() in ["false", "0"]:
                snow_drive_mode = False
            else:
                raise HTTPException(status_code=400, detail="Invalid boolean value for snow_drive_mode") 

        if intelligent_parking_assist_auto_park is not None:
            if intelligent_parking_assist_auto_park.lower() in ["true", "1"]:
                intelligent_parking_assist_auto_park = True
            elif intelligent_parking_assist_auto_park.lower() in ["false", "0"]:
                intelligent_parking_assist_auto_park = False
            else:
                raise HTTPException(status_code=400, detail="Invalid boolean value for intelligent_parking_assist_auto_park") 

        if digital_key_smartphone is not None:
            if digital_key_smartphone.lower() in ["true", "1"]:
                digital_key_smartphone = True
            elif digital_key_smartphone.lower() in ["false", "0"]:
                digital_key_smartphone = False
            else:
                raise HTTPException(status_code=400, detail="Invalid boolean value for digital_key_smartphone") 

        if electric_rear_seat_recline is not None:
            if electric_rear_seat_recline.lower() in ["true", "1"]:
                electric_rear_seat_recline = True
            elif electric_rear_seat_recline.lower() in ["false", "0"]:
                electric_rear_seat_recline = False
            else:
                raise HTTPException(status_code=400, detail="Invalid boolean value for electric_rear_seat_recline") 

        if navigation_system is not None:
            if navigation_system.lower() in ["true", "1"]:
                navigation_system = True
            elif navigation_system.lower() in ["false", "0"]:
                navigation_system = False
            else:
                raise HTTPException(status_code=400, detail="Invalid boolean value for navigation_system") 

        if power_locks is not None:
            if power_locks.lower() in ["true", "1"]:
                power_locks = True
            elif power_locks.lower() in ["false", "0"]:
                power_locks = False
            else:
                raise HTTPException(status_code=400, detail="Invalid boolean value for power_locks") 

        if tinted_windows is not None:
            if tinted_windows.lower() in ["true", "1"]:
                tinted_windows = True
            elif tinted_windows.lower() in ["false", "0"]:
                tinted_windows = False
            else:
                raise HTTPException(status_code=400, detail="Invalid boolean value for tinted_windows") 

        if rear_tv_screens is not None:
            if rear_tv_screens.lower() in ["true", "1"]:
                rear_tv_screens = True
            elif rear_tv_screens.lower() in ["false", "0"]:
                rear_tv_screens = False
            else:
                raise HTTPException(status_code=400, detail="Invalid boolean value for rear_tv_screens") 

        if cd_dvd_player is not None:
            if cd_dvd_player.lower() in ["true", "1"]:
                cd_dvd_player = True
            elif cd_dvd_player.lower() in ["false", "0"]:
                cd_dvd_player = False
            else:
                raise HTTPException(status_code=400, detail="Invalid boolean value for cd_dvd_player") 

        if mp3_interface is not None:
            if mp3_interface.lower() in ["true", "1"]:
                mp3_interface = True
            elif mp3_interface.lower() in ["false", "0"]:
                mp3_interface = False
            else:
                raise HTTPException(status_code=400, detail="Invalid boolean value for dashboard_speakers")            


        # All data converted to boolean now storing the data in the table
        check_cmft = db.query(VehicleComfortConvenience).filter(VehicleComfortConvenience.fk_vehicle_id == vehicle_id).first()
        comfort_data = ComfortConvenience(power_streeing=power_streeing,push_start_smartkey=push_start_smartkey,keyless_entry=keyless_entry,key_start=key_start,navigation=navigation,remote_controller=remote_controller,android_led=android_led,bluetooth=bluetooth,front_door_speaker=front_door_speaker,rear_door_speaker=rear_door_speaker,rear_deck_speaker=rear_deck_speaker,ECO_mode=ECO_mode,heated_seats=heated_seats, power_seats=power_seats, power_side_mirrors=power_side_mirrors, electric_rearview_mirror=electric_rearview_mirror,dashboard_speakers=dashboard_speakers,wireless_apple_carplay_android_auto=wireless_apple_carplay_android_auto,voice_control_system=voice_control_system,gesture_control=gesture_control,remote_engine_start=remote_engine_start,auto_dimming_rearview_mirror=auto_dimming_rearview_mirror,driver_seat_massager=driver_seat_massager,rear_window_sunshade_manual=rear_window_sunshade_manual,rear_window_sunshade_electric=rear_window_sunshade_electric,air_purifier_ionizer=air_purifier_ionizer,cabin_noise_cancellation=cabin_noise_cancellation,smart_climate_control_ai_sensing=smart_climate_control_ai_sensing,ota_updates_over_the_air_software=ota_updates_over_the_air_software,sports_drive_mode=sports_drive_mode,comfort_drive_mode=comfort_drive_mode,snow_drive_mode=snow_drive_mode,intelligent_parking_assist_auto_park=intelligent_parking_assist_auto_park,digital_key_smartphone=digital_key_smartphone,electric_rear_seat_recline=electric_rear_seat_recline,navigation_system=navigation_system,power_locks=power_locks,tinted_windows=tinted_windows,rear_tv_screens=rear_tv_screens,cd_dvd_player=cd_dvd_player,mp3_interface=mp3_interface)

        for key, value in comfort_data.model_dump(exclude_unset=True).items():
            setattr(check_cmft, key, value)

        db.commit()
        db.refresh(check_cmft)
        print(7)



        """Adding the features to dimension table"""
        check_dim = db.query(DimensionCapicity).filter(DimensionCapicity.fk_vehicle_id == vehicle_id).first()
        dimension_data = DimensionCap(max_length=max_length,height=height,wheel_base=wheel_base,height_including_roof_rails=height_including_roof_rails,luggage_capacity_seatsup=luggage_capacity_seatsup,luggage_capacity_seatsdown=luggage_capacity_seatsdown,width=width,width_including_mirrors=width_including_mirrors,gross_vehicle_weight=gross_vehicle_weight,max_loading_weight=max_loading_weight,max_roof_load=max_roof_load,number_of_seats=number_of_seats)

        for key, value in dimension_data.model_dump(exclude_unset=True).items():
            setattr(check_dim, key, value)

        db.commit()
        db.refresh(check_dim)
        print(8)


        """Adding the features to engine table"""
        check_engine = db.query(EngineTransmisison).filter(EngineTransmisison.fk_vehicle_id == vehicle_id).first()
        engine_data = EngineTrans(fuel_tank_capacity=fuel_tank_capacity,max_towing_weight_braked=max_towing_weight_braked,max_towing_weight_unbraked=max_towing_weight_unbraked,minimum_kerbweight=minimum_kerbweight,turning_circle_kerb_to_kerb=turning_circle_kerb_to_kerb)

        for key, value in engine_data.model_dump(exclude_unset=True).items():
            setattr(check_engine, key, value)

        db.commit()
        db.refresh(check_engine)
        print(9)


        """Adding the PerformanceFeature"""
        # changing types of values from strings to booleans
        if desmodromic_engine_technology is not None:
            if desmodromic_engine_technology.lower() in ["true", "1"]:
                desmodromic_engine_technology = True
            elif desmodromic_engine_technology.lower() in ["false", "0"]:
                desmodromic_engine_technology = False
            else:
                raise HTTPException(status_code=400, detail="Invalid boolean value for desmodromic_engine_technology")

        if fuel_injection is not None:
            if fuel_injection.lower() in ["true", "1"]:
                fuel_injection = True
            elif fuel_injection.lower() in ["false", "0"]:
                fuel_injection = False
            else:
                raise HTTPException(status_code=400, detail="Invalid boolean value for fuel_injection")

        if lightweight_design is not None:
            if lightweight_design.lower() in ["true", "1"]:
                lightweight_design = True
            elif lightweight_design.lower() in ["false", "0"]:
                lightweight_design = False
            else:
                raise HTTPException(status_code=400, detail="Invalid boolean value for lightweight_design")

        if high_performance_suspension is not None:
            if high_performance_suspension.lower() in ["true", "1"]:
                high_performance_suspension = True
            elif high_performance_suspension.lower() in ["false", "0"]:
                high_performance_suspension = False
            else:
                raise HTTPException(status_code=400, detail="Invalid boolean value for high_performance_suspension")

        # All data converted to boolean now storing the data in the table
        check_performance = db.query(PerformanceFeature).filter(PerformanceFeature.fk_vehicle_id == vehicle_id).first()
        performance_data = PerformanceFeatureSchema(desmodromic_engine_technology=desmodromic_engine_technology,fuel_injection=fuel_injection,lightweight_design=lightweight_design,high_performance_suspension=high_performance_suspension)
        
        for key, value in performance_data.model_dump(exclude_unset=True).items():
            setattr(check_performance, key, value)

        db.commit()
        db.refresh(check_performance)
        print(10)

        """Adding the ComfortUsabilityFeaturesSchema"""
        # changing types of values from strings to booleans
        if riding_ergonomics is not None:
            if riding_ergonomics.lower() in ["true", "1"]:
                riding_ergonomics = True
            elif riding_ergonomics.lower() in ["false", "0"]:
                riding_ergonomics = False
            else:
                raise HTTPException(status_code=400, detail="Invalid boolean value for riding_ergonomics")

        if seat is not None:
            if seat.lower() in ["true", "1"]:
                seat = True
            elif seat.lower() in ["false", "0"]:
                seat = False
            else:
                raise HTTPException(status_code=400, detail="Invalid boolean value for seat")

        if instrumentation is not None:
            if instrumentation.lower() in ["true", "1"]:
                instrumentation = True
            elif instrumentation.lower() in ["false", "0"]:
                instrumentation = False
            else:
                raise HTTPException(status_code=400, detail="Invalid boolean value for instrumentation")

        if fuel_capacity is not None:
            if fuel_capacity.lower() in ["true", "1"]:
                fuel_capacity = True
            elif fuel_capacity.lower() in ["false", "0"]:
                fuel_capacity = False
            else:
                raise HTTPException(status_code=400, detail="Invalid boolean value for fuel_capacity")

        # All data converted to boolean now storing the data in the table
        check_comfortusability = db.query(ComfortUsabilityFeatures).filter(ComfortUsabilityFeatures.fk_vehicle_id == vehicle_id).first()
        comfortusability_data = ComfortUsabilityFeaturesSchema(riding_ergonomics=riding_ergonomics,seat=seat,instrumentation=instrumentation,fuel_capacity=fuel_capacity)

        for key, value in comfortusability_data.model_dump(exclude_unset=True).items():
            setattr(check_comfortusability, key, value)

        db.commit()
        db.refresh(check_comfortusability)
        print(11)

        """Adding the SafetyFeaturesSchema"""
        # changing types of values from strings to booleans
        if high_performance_brakes is not None:
            if high_performance_brakes.lower() in ["true", "1"]:
                high_performance_brakes = True
            elif high_performance_brakes.lower() in ["false", "0"]:
                high_performance_brakes = False
            else:
                raise HTTPException(status_code=400, detail="Invalid boolean value for high_performance_brakes")

        if high_quality_tires is not None:
            if high_quality_tires.lower() in ["true", "1"]:
                high_quality_tires = True
            elif high_quality_tires.lower() in ["false", "0"]:
                high_quality_tires = False
            else:
                raise HTTPException(status_code=400, detail="Invalid boolean value for high_quality_tires")

        # All data converted to boolean now storing the data in the table
        check_safetyfeatures = db.query(SafetyFeatures).filter(SafetyFeatures.fk_vehicle_id == vehicle_id).first()
        safetyfeatures_data = SafetyFeaturesSchema(high_performance_brakes=high_performance_brakes,high_quality_tires=high_quality_tires)

        for key, value in safetyfeatures_data.model_dump(exclude_unset=True).items():
            setattr(check_safetyfeatures, key, value)

        db.commit()
        db.refresh(check_safetyfeatures)
        print(12)

        """Adding the ConvenienceFeaturesSchema"""
        # changing types of values from strings to booleans
        if lighting is not None:
            if lighting.lower() in ["true", "1"]:
                lighting = True
            elif lighting.lower() in ["false", "0"]:
                lighting = False
            else:
                raise HTTPException(status_code=400, detail="Invalid boolean value for lighting")

        if storage is not None:
            if storage.lower() in ["true", "1"]:
                storage = True
            elif storage.lower() in ["false", "0"]:
                storage = False
            else:
                raise HTTPException(status_code=400, detail="Invalid boolean value for storage")

        if security is not None:
            if security.lower() in ["true", "1"]:
                security = True
            elif security.lower() in ["false", "0"]:
                security = False
            else:
                raise HTTPException(status_code=400, detail="Invalid boolean value for security")

        if adjustable_suspension is not None:
            if adjustable_suspension.lower() in ["true", "1"]:
                adjustable_suspension = True
            elif adjustable_suspension.lower() in ["false", "0"]:
                adjustable_suspension = False
            else:
                raise HTTPException(status_code=400, detail="Invalid boolean value for adjustable_suspension")

        # All data converted to boolean now storing the data in the table
        check_conveniencefeatures = db.query(ConvenienceFeatures).filter(ConvenienceFeatures.fk_vehicle_id == vehicle_id).first()
        conveniencefeatures_data = ConvenienceFeaturesSchema(lighting=lighting,storage=storage,security=security,adjustable_suspension=adjustable_suspension)

        for key, value in conveniencefeatures_data.model_dump(exclude_unset=True).items():
            setattr(check_conveniencefeatures, key, value)

        db.commit()
        db.refresh(check_conveniencefeatures)
        print(13)

        retval = {
            "data": "Updated Successfully"
        }
        return retval
    except Exception as e:
        print(traceback.format_exc())
        logging.error(f'Error occured while registering vehicle: {str(e)}')
        raise HTTPException(status_code=409, detail=f' Error: {str(e)}')


# deleting vehicle
@router.delete("/v1/vehicle/{veh_id}")
def delete_vehicle(veh_id: int,authorization: str = Header(None), db: Session = Depends(get_db)):
    if authorization is None:
        logging.error('The token entered for the user is either wrong or expired')
        raise HTTPException(status_code=401, detail="Unauthorized")
    token = authorization.split(" ")[1] if authorization.startswith("Bearer ") else authorization
    
    if is_token_blacklisted(token) == True:
        return {'Message': 'Session Expired please Login'}
    
    logging.info('token have two parts some time writen as token "value of token" or directly "token"')
    user_id, retval = decode_token(token)

    logging.info(f'the user id after decoding: {user_id}')
    print(f"user id: {user_id}")

    """This below logic will be used if the image name/link is not in the format I am using now to make the name in the format stored in DB"""
    # print(image_data.image_to_delete)
    # print(image_data.image_to_delete.split("5002/")[1])

    # Fetch the vehicle and update it
    veh = db.query(Vehicle).filter(Vehicle.id == veh_id).first()
    if not veh:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    
    # Delete related records in the `Images` table
    related_images = db.query(Images).filter(Images.fk_vehicle_id == veh_id).all()
    for image in related_images:
        db.delete(image)

    # Delete related records in the `Images` table
    related_videos = db.query(Videos).filter(Videos.fk_vehicle_id == veh_id).all()
    for vid in related_videos:
        db.delete(vid)

    # Delete related records in the `VehicleInterior` table
    checkVehicleInterior = db.query(VehicleInterior).filter(VehicleInterior.fk_vehicle_id == veh_id).all()
    for interior in checkVehicleInterior:
        db.delete(interior)

    # Delete related records in the `VehicleSafety` table
    checkVehicleSafety = db.query(VehicleSafety).filter(VehicleSafety.fk_vehicle_id == veh_id).all()
    for safety in checkVehicleSafety:
        db.delete(safety)

    # Delete related records in the `VehicleExterior` table
    checkVehicleExterior = db.query(VehicleExterior).filter(VehicleExterior.fk_vehicle_id == veh_id).all()
    for exterior in checkVehicleExterior:
        db.delete(exterior)

    # Delete related records in the `VehicleComfortConvenience` table
    checkVehicleComfort = db.query(VehicleComfortConvenience).filter(VehicleComfortConvenience.fk_vehicle_id == veh_id).all()
    for comfort in checkVehicleComfort:
        db.delete(comfort)

    # Delete related records in the `DimensionCapicity` table
    checkVehicleDimension = db.query(DimensionCapicity).filter(DimensionCapicity.fk_vehicle_id == veh_id).all()
    for dimension in checkVehicleDimension:
        db.delete(dimension)

    # Delete related records in the `EngineTransmisison` table
    checkVehicleEngine = db.query(EngineTransmisison).filter(EngineTransmisison.fk_vehicle_id == veh_id).all()
    for engine in checkVehicleEngine:
        db.delete(engine)
    
        # Delete related records in the `PerformanceFeature` table
    checkperformance = db.query(PerformanceFeature).filter(PerformanceFeature.fk_vehicle_id == veh_id).all()
    for perf in checkperformance:
        db.delete(perf)
    
        # Delete related records in the `ComfortUsabilityFeatures` table
    checkcomfortusability = db.query(ComfortUsabilityFeatures).filter(ComfortUsabilityFeatures.fk_vehicle_id == veh_id).all()
    for comusb in checkcomfortusability:
        db.delete(comusb)
    
        # Delete related records in the `SafetyFeatures` table
    checksafetyfeature = db.query(SafetyFeatures).filter(SafetyFeatures.fk_vehicle_id == veh_id).all()
    for safe in checksafetyfeature:
        db.delete(safe)
    
        # Delete related records in the `ConvenienceFeatures` table
    checkconveniencefeatures = db.query(ConvenienceFeatures).filter(ConvenienceFeatures.fk_vehicle_id == veh_id).all()
    for conv in checkconveniencefeatures:
        db.delete(conv)
    
    # Delete related records in the `Price` table
    checkPrice = db.query(Prices).filter(Prices.fk_vehicle_id == veh_id).all()
    for price in checkPrice:
        db.delete(price)
    
    # to store all the new changes in the DB make sure you put the DB commit
    db.commit()

    notification = Notification(
        fk_user_id=user_id, # in future remember this is user ID not sparepart but here is dummy example for now
        message=f"{veh.name} has been deleted from Inventory.",
        read = False
    )
    db.add(notification)
    db.commit()
    db.refresh(notification)
    
    # After all related records are deleted, delete the vehicle itself
    db.delete(veh)
    db.commit()  # Commit once at the end to persist all deletions
     
    return {"data": "Vehicle deleted successfully"}

# adding image
# Adding existing needs form data image variable with image file and authorization token
@router.put("/v1/vehicle/{vehicle_id}/image_adding")
def update_vehicle(vehicle_id: int, image: list[UploadFile] = File(None), authorization: str = Header(None), db: Session = Depends(get_db)):
    if authorization is None:
        logging.error('The token entered for the user is either wrong or expired')
        raise HTTPException(status_code=401, detail="Unauthorized")
    token = authorization.split(" ")[1] if authorization.startswith("Bearer ") else authorization
    
    if is_token_blacklisted(token) == True:
        return {'Message': 'Session Expired please Login'}
    
    logging.info('token have two parts some time writen as token "value of token" or directly "token"')
    user_id, retval = decode_token(token)

    logging.info(f'the user id after decoding: {user_id}')
    print(f"user id: {user_id}")

    # Fetch the vehicle and update it
    vehicle = db.query(Vehicle).filter(Vehicle.id == vehicle_id).first()
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    
    image_paths = []

        # Save image files to the uploads directory
    if image is not None:
        for img in image:
            img.filename = str(vehicle_id) + img.filename
            print(img.filename)
            file_location = os.path.join(UPLOAD_DIR, img.filename)
            with open(file_location, "wb") as buffer:
                shutil.copyfileobj(img.file, buffer)
            print(file_location)
            image_paths.append(file_location)
        # Convert list of paths to a comma-separated string
        images_string = ",".join(image_paths)   
        
        """check if there are images in the folder already"""
        checkVehImages = db.query(Images).filter(Images.fk_vehicle_id == vehicle_id).first()
        if checkVehImages:
            if checkVehImages.image:
                images_string = images_string + "," + checkVehImages.image

            checkVehImages.image = images_string  
        else:  
            new_image_record = Images(fk_vehicle_id=vehicle_id, image=images_string)
            db.add(new_image_record)
        
        db.commit()
        db.refresh(checkVehImages if checkVehImages else new_image_record)

        return {"Message": "Image/s added successfully", "vehicle_id": vehicle_id,"updated_images": images_string}


"""******************REGISTER MAKE, MODEL, BODY TYPE, DRIVE TYPE, TRANSMISSION, DISPLACEMENT, SCORE AND COLOR DYNAMICALLY********************"""
@router.post("/v1/register_make")
def create_languages(data: VehMake, db: Session = Depends(get_db)):
    mk_data = data.model_dump() 
    created_make = create_make(db, VehMake(**mk_data))

    retval = {
        'make': created_make
    }
    return {"Message": "Successful", "data": retval}


@router.post("/v1/register_model")
def create_models(data: VehModel, db: Session = Depends(get_db)):
    md_data = data.model_dump()
    
    created_model = create_model(db, VehModel(**md_data))

    retval = {
        'model': created_model
    }
    return {"Message": "Successful", "data": retval} 

"""update model to add foreign key of make"""
@router.put("/v1/register_model/{model_id}")
def create_models(model_id:int, data: VehModel, db: Session = Depends(get_db)):
    model_check = db.query(VehicleModel).filter(VehicleModel.id==model_id).first()
    if not model_check:
        raise HTTPException(status_code=404, detail="No model found")
    
    for key, value in data.dict(exclude_unset=True).items():
        setattr(model_check, key, value)

    db.commit()
    db.refresh(model_check)

    retval = {
        'model': model_check
    }
    return {"Message": "Model Updated Successfully", "data": retval} 


@router.post("/v1/register_bodytype")
def create_bodytype(data: VehBodyType, db: Session = Depends(get_db)):
    dbt_data = data.model_dump() 
    created_bodytype = create_body(db, VehBodyType(**dbt_data))

    retval = {
        'bodytype': created_bodytype
    }
    return {"Message": "Successful", "data": retval} 

@router.post("/v1/register_transmission")
def create_transmission(data: VehTransmission, db: Session = Depends(get_db)):
    trans_data = data.model_dump() 
    created_transmission = create_trans(db, VehTransmission(**trans_data))

    retval = {
        'transmission': created_transmission
    }
    return {"Message": "Successful", "data": retval} 

@router.post("/v1/register_interior_color")
def create_color(data: VehIntColor, db: Session = Depends(get_db)):
    clr_data = data.model_dump() 
    created_color = create_int_clr(db, VehIntColor(**clr_data))

    retval = {
        'color': created_color
    }
    return {"Message": "Successful", "data": retval} 

@router.post("/v1/register_exterior_color")
def create_color(data: VehExtColor, db: Session = Depends(get_db)):
    clr_data = data.model_dump() 
    created_color = create_ext_clr(db, VehExtColor(**clr_data))

    retval = {
        'color': created_color
    }
    return {"Message": "Successful", "data": retval} 

@router.post("/v1/register_displacement")
def create_displacement(data: VehDisplacement, db: Session = Depends(get_db)):
    data.vehdisplacement = int(data.vehdisplacement)
    data.vehdisplacement = f"{data.vehdisplacement:,}"
    data.vehdisplacement = str(data.vehdisplacement) + " " + "cc"
    # print(data.vehdisplacement)
    disp_data = data.model_dump()
    created_displacement = create_disp(db, VehDisplacement(**disp_data))

    retval = {
        'displacement': created_displacement
    }
    return {"Message": "Successful", "data": retval} 


@router.post("/v1/register_drivetype")
def create_color(data: VehDriveType, db: Session = Depends(get_db)):
    dr_type_data = data.model_dump() 
    created_drivetype = create_drtype(db, VehDriveType(**dr_type_data))

    retval = {
        'drive_type': created_drivetype
    }
    return {"Message": "Successful", "data": retval} 


@router.post("/v1/register_score")
def create_score(data: VehScore, db: Session = Depends(get_db)):
    score_data = data.model_dump() 
    created_score = create_scr(db, VehScore(**score_data))

    retval = {
        'drive_score': created_score
    }
    return {"Message": "Successful", "data": retval}

"""******************DISPLAY MAKE, MODEL, BODY TYPE, DRIVE TYPE, TRANSMISSION, DISPLACEMENT, SCORE AND COLOR DYNAMICALLY********************"""

@router.get("/v1/read_all_make")
def read_make(db: Session = Depends(get_db)):
    make_data = db.query(VehicleMake).all()
    return {"data": make_data}

@router.get("/v1/read_all_model")
def read_model(db: Session = Depends(get_db)):
    model_data = db.query(VehicleModel).all()
    return {"data": model_data}  

@router.get("/v1/read_all_bodytypes")
def read_model(db: Session = Depends(get_db)):
    body_data = db.query(VehicleBodyType).all()
    return {"data": body_data}

@router.get("/v1/read_all_transmissions")
def read_model(db: Session = Depends(get_db)):
    transmission_data = db.query(VehicleTransmission).all()
    return {"data": transmission_data}

@router.get("/v1/read_all_interior_colors")
def read_model(db: Session = Depends(get_db)):
    color_data = db.query(VehicleInteriorColor).all()
    return {"data": color_data}

@router.get("/v1/read_all_exterior_colors")
def read_model(db: Session = Depends(get_db)):
    color_data = db.query(VehicleExteriorColor).all()
    return {"data": color_data}

@router.get("/v1/read_all_displacements")
def read_model(db: Session = Depends(get_db)):
    displacement_data = db.query(VehicleDisplacement).all()
    return {"data": displacement_data}

@router.get("/v1/read_all_drivetypes")
def read_model(db: Session = Depends(get_db)):
    drivetype_data = db.query(VehicleDriveType).all()
    return {"data": drivetype_data}

@router.get("/v1/read_all_scores")
def read_model(db: Session = Depends(get_db)):
    score_data = db.query(VehicleScore).all()
    return {"data": score_data}

"""DOWNLOAD CSV FILE OF THE VEHICLE INVENTORY"""

@router.post("/v1/admin/vehicle_inventory/export/csv")
def export_vehicles_inventory_csv(data: InventoryVehicles, db: Session = Depends(get_db)):
    if data.filter_status == 'Instock':
        veh_data = db.query(Vehicle).filter(Vehicle.status == "Instock").all()

        # Ensure export directory exists
        if not os.path.exists(EXPORT_DIR):
            os.makedirs(EXPORT_DIR)

        file_path = os.path.join(EXPORT_DIR, "vehicle_inventory.csv")

        # Create CSV file and write data to it
        with open(file_path, mode="w", newline="") as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow(['id', 'make', 'model', 'year','title','name','chassis_number','mileage','damage_details','transmission','clynder','location','color','fuel','engine','status','grade','score','steer','displacement','condition','doors','engine_name','supplier','is_clear','report_status', 'created_at'])  # CSV header
            for veh in veh_data:
                writer.writerow([veh.id, veh.make, veh.model, veh.year,veh.title, veh.name,veh.chassis_number,veh.mileage,veh.damage_details,veh.transmission,veh.clynder,veh.location,veh.color,veh.fuel,veh.engine, veh.status,veh.grade,veh.score,veh.steer,veh.displacement,veh.condition,veh.doors,veh.engine_name,veh.supplier,veh.is_clear, veh.report_status, veh.created_at])

        # Return file as a download
        return FileResponse(file_path, filename="vehicle_inventory.csv", media_type="text/csv")

    elif data.filter_status == 'Outofstock':
        veh_data = db.query(Vehicle).filter(Vehicle.status == "Outofstock").all()
    
        # Ensure export directory exists
        if not os.path.exists(EXPORT_DIR):
            os.makedirs(EXPORT_DIR)
    
        file_path = os.path.join(EXPORT_DIR, "vehicle_inventory.csv")
    
        # Create CSV file and write data to it
        with open(file_path, mode="w", newline="") as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow(['id', 'make', 'model', 'year','title','name','chassis_number','mileage','damage_details','transmission','clynder','location','color','fuel','engine','status','grade','score','steer','displacement','condition','doors','engine_name','supplier','is_clear','report_status', 'created_at'])  # CSV header
            for veh in veh_data:
                writer.writerow([veh.id, veh.make, veh.model, veh.year,veh.title, veh.name,veh.chassis_number,veh.mileage,veh.damage_details,veh.transmission,veh.clynder,veh.location,veh.color,veh.fuel,veh.engine, veh.status,veh.grade,veh.score,veh.steer,veh.displacement,veh.condition,veh.doors,veh.engine_name,veh.supplier,veh.is_clear, veh.report_status, veh.created_at])
    
        # Return file as a download
        return FileResponse(file_path, filename="vehicle_inventory.csv", media_type="text/csv")

    elif data.filter_status == 'Intransit':
        veh_data = db.query(Vehicle).filter(Vehicle.status == "Intransit").all()
    
        # Ensure export directory exists
        if not os.path.exists(EXPORT_DIR):
            os.makedirs(EXPORT_DIR)
    
        file_path = os.path.join(EXPORT_DIR, "vehicle_inventory.csv")
    
        # Create CSV file and write data to it
        with open(file_path, mode="w", newline="") as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow(['id', 'make', 'model', 'year','title','name','chassis_number','mileage','damage_details','transmission','clynder','location','color','fuel','engine','status','grade','score','steer','displacement','condition','doors','engine_name','supplier','is_clear','report_status', 'created_at'])  # CSV header
            for veh in veh_data:
                writer.writerow([veh.id, veh.make, veh.model, veh.year,veh.title, veh.name,veh.chassis_number,veh.mileage,veh.damage_details,veh.transmission,veh.clynder,veh.location,veh.color,veh.fuel,veh.engine, veh.status,veh.grade,veh.score,veh.steer,veh.displacement,veh.condition,veh.doors,veh.engine_name,veh.supplier,veh.is_clear, veh.report_status, veh.created_at])
    
        # Return file as a download
        return FileResponse(file_path, filename="vehicle_inventory.csv", media_type="text/csv")
    
    else:
        veh_data = db.query(Vehicle).all()
    
        # Ensure export directory exists
        if not os.path.exists(EXPORT_DIR):
            os.makedirs(EXPORT_DIR)
    
        file_path = os.path.join(EXPORT_DIR, "vehicle_inventory.csv")
    
        # Create CSV file and write data to it
        with open(file_path, mode="w", newline="") as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow(['id', 'make', 'model', 'year','title','name','chassis_number','mileage','damage_details','transmission','clynder','location','color','fuel','engine','status','grade','score','steer','displacement','condition','doors','engine_name','supplier','is_clear','report_status', 'created_at'])  # CSV header
            for veh in veh_data:
                writer.writerow([veh.id, veh.make, veh.model, veh.year,veh.title, veh.name,veh.chassis_number,veh.mileage,veh.damage_details,veh.transmission,veh.clynder,veh.location,veh.color,veh.fuel,veh.engine, veh.status,veh.grade,veh.score,veh.steer,veh.displacement,veh.condition,veh.doors,veh.engine_name,veh.supplier,veh.is_clear, veh.report_status, veh.created_at])
    
        # Return file as a download
        return FileResponse(file_path, filename="vehicle_inventory.csv", media_type="text/csv")


"""SEND EMAIL TO COMPANY FOR QUOTING VEHICLE"""
@router.post("/v1/ask_for_quote")
def ask_for_quote_vehicle(data: QuoteRequest, db: Session = Depends(get_db)):
    
    print("email yes")
    veh_data = db.query(Vehicle).filter(Vehicle.id == data.veh_id).first()
    if not veh_data:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    
    
    # Send quote in email to the company  
    send_quote_to_email(veh_data.chassis_number, veh_data.name, veh_data.title, data)  
    # Implement this function to send the email
    notification = Notification(
        fk_user_id=None, # in future remember this is user ID not vehicle but here is dummy example for now
        message=f"{data.name} has inquired about {veh_data.name}",
        read = False
    )
    db.add(notification)
    db.commit()
    db.refresh(notification)

    return {"message": "Your quote has been sent"}



# *********************** Chassis List for Containers *************************
@router.get("/v1/chassis_list_dropdown")
def get_chassis_list(db: Session = Depends(get_db)):
    chassis_details = db.query(Vehicle).filter(Vehicle.status == "Intransit", Vehicle.fk_container_id.is_(None)).all()
    if not chassis_details:
        chassis_details=[]

    retval = [
        {
            "id": chassis_detail.id,
            "chassis_number": chassis_detail.chassis_number,
            "created_at": chassis_detail.created_at,
            "updated_at": chassis_detail.updated_at,
        }
        for chassis_detail in chassis_details
    ]
    
    return {"data": retval}

# *********************** Chassis List for customer bids *************************
@router.get("/v1/chassis_list_dropdown_vehicle")
def get_chassis_list(db: Session = Depends(get_db)):
    # Ensure we only exclude vehicles currently in BidWon
    subquery = db.query(BidWon.fk_vehicle_id).distinct().subquery()

    chassis_details = db.query(Vehicle).filter(
        ~Vehicle.id.in_(subquery)  # Exclude vehicles still in BidWon
    ).all()

    retval = [
        {
            "id": chassis_detail.id,
            "chassis_number": chassis_detail.chassis_number,
            "created_at": chassis_detail.created_at,
            "updated_at": chassis_detail.updated_at
        }
        for chassis_detail in chassis_details
    ]
    
    return {"data": retval}

# *********************** Chassis List for invoice trucks and vehicles and bikes *************************

@router.get("/v1/chassis_list_dropdown_combine")
def get_chassis_list(db: Session = Depends(get_db)):
    chassis_details = db.query(Vehicle).filter(Vehicle.status == "Outofstock", Vehicle.fk_invoice_id.is_(None)).all()
    if not chassis_details:
        chassis_details=[]
    retval = [
        {
            "id": chassis_detail.id,
            "chassis_number": chassis_detail.chassis_number,
            "created_at": chassis_detail.created_at,
            "updated_at": chassis_detail.updated_at,
            "type": "vehicle"
        }
        for chassis_detail in chassis_details
    ]
    
    return {"data": retval}

# *********************** Chassis Number Details *************************
@router.post("/v1/chassis_detail")
def get_chassis_details(data: ChassisDetail, db: Session = Depends(get_db)):
    chassis_detail = db.query(Vehicle).filter(Vehicle.chassis_number == data.chassis_number).first()
    if not chassis_detail:
        raise HTTPException(status_code=404, detail="No chassis details found")

    retval = {
            "id": chassis_detail.id,
            "chassis_number": chassis_detail.chassis_number,
            "name":chassis_detail.name,
            "make": chassis_detail.make,
            "model": chassis_detail.model,
            "year": chassis_detail.year,
            "intcolor": chassis_detail.intcolor,
            "extcolor": chassis_detail.extcolor,
            "created_at": chassis_detail.created_at,
            "updated_at": chassis_detail.updated_at
        }

    return {"data": retval}


# *********************** Chassis Number Details combine *************************
@router.post("/v1/chassis_detail_combine")
def get_chassis_details(data: ChassisDetail,request: Request, db: Session = Depends(get_db)):
    chassis_detail = db.query(Vehicle).filter(Vehicle.chassis_number == data.chassis_number).first()
    if chassis_detail:
        if chassis_detail.status == "Instock":
            return
        images = db.query(Images).filter(Images.fk_vehicle_id == chassis_detail.id).all()
    if not chassis_detail:
        raise HTTPException(status_code=404, detail="No chassis details found")

            # Retrieve image paths and convert to accessible URLs
    if chassis_detail:
        if images is not None:
            for img in images:
                if img.image:
                    image_paths = img.image.split(",")  # Split comma-separated file paths
                    # Construct URLs to access the images
                    image_urls = [f"{request.base_url}uploads/vehicles/{os.path.basename(path)}" for path in image_paths]
                else:
                    image_urls = []
        retval = {
                "id": chassis_detail.id,
                "chassis_number": chassis_detail.chassis_number,
                "name": chassis_detail.name,
                "sold_price": chassis_detail.sold_price,
                "recieved_amount": chassis_detail.recieved_amount,
                "balance_amount": chassis_detail.balance_amount,
                "images":image_urls,
                "created_at": chassis_detail.created_at,
                "updated_at": chassis_detail.updated_at
            }
        
    return {"data": retval}

"""********************** List Report Generation for Company Retails Vehicles ******************"""
@router.post("/v1/retails_report")
def get_retails_report(data: InventoryRetails, db: Session = Depends(get_db)):
    try:
        start_date = datetime.fromisoformat(data.start_date.replace("Z", "+00:00")).date() if data.start_date else None
        end_date = datetime.fromisoformat(data.end_date.replace("Z", "+00:00")).date() if data.end_date else None
    except ValueError as e:
        raise HTTPException(status_code=400, detail="Invalid date format. Use ISO 8601 format.")
    
    if data.report_type == "vehicle":
        query = db.query(Vehicle).filter(Vehicle.status == "Outofstock")
        
        # Apply date filtering
        if start_date and end_date:
            query = query.filter(
                and_(
                    func.date(Vehicle.created_at) >= start_date,
                    func.date(Vehicle.created_at) <= end_date
                )
            )
        elif start_date:
            query = query.filter(func.date(Vehicle.created_at) >= start_date)
        elif end_date:
            query = query.filter(func.date(Vehicle.created_at) <= end_date)
        
        # Fetch results
        vehicles_retail = query.all()
        if not vehicles_retail:
            raise HTTPException(status_code=404, detail="No retails found")
        
        retval = [{
                "id": retail.id,
                "start_date": start_date,
                "end_date": end_date,
                "created_at": retail.created_at,
                "Name": retail.name,
                "make": retail.make,
                "model": retail.model,
                "chassis_number": retail.chassis_number,
                "category": retail.body_type,
                "condition": retail.condition,
                "sold_price": retail.sold_price,
                "recieved_amount": retail.recieved_amount,
                "balance_amount": retail.balance_amount,
                "status": retail.status
            }
            for retail in vehicles_retail
        ]

    """Create a notification and store in Notification Table"""
    notification = Notification(
        fk_user_id=None,
        message=f"Sales report has been generated by Admin.",
        read = False
    )
    db.add(notification)
    db.commit()
    db.refresh(notification)
    print("notification created in Notification Table")         
    return {"data": retval}



"""************* DOWNLOAD CSV/PDF FILE OF THE INVENTORY RETAILS*****************"""

@router.post("/v1/admin/inventory_retails/export")
def export_vehicles_inventory_csv(data: InventoryRetails, db: Session = Depends(get_db)):
    try:
        start_date = datetime.fromisoformat(data.start_date.replace("Z", "+00:00")).date() if data.start_date else None
        end_date = datetime.fromisoformat(data.end_date.replace("Z", "+00:00")).date() if data.end_date else None
    except ValueError as e:
        raise HTTPException(status_code=400, detail="Invalid date format. Use ISO 8601 format.")
    
    if data.report_type == "vehicle":
        query = db.query(Vehicle).filter(Vehicle.status == "Outofstock")
        
        # Apply date filtering
        if start_date and end_date:
            query = query.filter(
                and_(
                    func.date(Vehicle.created_at) >= start_date,
                    func.date(Vehicle.created_at) <= end_date
                )
            )
        elif start_date:
            query = query.filter(func.date(Vehicle.created_at) >= start_date)
        elif end_date:
            query = query.filter(func.date(Vehicle.created_at) <= end_date)
        
        # Fetch results
        vehicles_retail = query.all()
        if not vehicles_retail:
            raise HTTPException(status_code=404, detail="No retails found")
        # Ensure export directory exists
        if not os.path.exists(EXPORT_DIR):
            os.makedirs(EXPORT_DIR)

        if data.download_type == "csv":
            file_path = os.path.join(EXPORT_DIR, "vehicle_outofstock_report.csv")

            # Create CSV file and write data to it
            with open(file_path, mode="w", newline="") as csv_file:
                writer = csv.writer(csv_file)
                report_duration = f"Vehicle report from duration {start_date or 'N/A'} to {end_date or 'N/A'}"
                writer.writerow([report_duration])  # Write the sentence in a single cell

                # Write an empty row for better readability
                writer.writerow([])
                writer.writerow(['id', 'created_at', 'name', 'make', 'model','chassis_number', 'category/body_type','condition','sold_price'])  # CSV header


                for veh in vehicles_retail:
                    writer.writerow([veh.id, veh.created_at, veh.name, veh.make, veh.model, veh.chassis_number, veh.body_type, veh.condition, veh.sold_price])

            # Return file as a download
            return FileResponse(file_path, filename="vehicle_outofstock_report.csv", media_type="text/csv")
        
        elif data.download_type == "pdf":
            file_path = os.path.join(EXPORT_DIR, "vehicle_outofstock_report.pdf")
            # Create PDF file and write data to it
            c = canvas.Canvas(file_path, pagesize=letter)
            c.setFont("Helvetica", 10)

            # Write header
            c.drawString(50, 750, "Vehicle Outofstock Report")
            c.drawString(50, 730, f"Vehicle report from duration {start_date} to {end_date}")
            
            y_position = 710
            headers = ['ID', 'Created At', 'Name', 'Make', 'Model','chassis_number', 'Category/Body Type', 'Condition', 'Sold Price']
            c.drawString(50, y_position, " | ".join(headers))
            y_position -= 20

            for veh in vehicles_retail:
                line = f"{veh.id} | {veh.created_at} | {veh.name} | {veh.make} | {veh.model} | {veh.chassis_number} | {veh.body_type} | {veh.condition} | {veh.sold_price}"
                c.drawString(50, y_position, line)
                y_position -= 20
                if y_position < 50:  # Create a new page if the content overflows
                    c.showPage()
                    c.setFont("Helvetica", 10)
                    y_position = 750

            c.save()
            # Return file as a download
            return FileResponse(file_path, filename="vehicle_outofstock_report.pdf", media_type="application/pdf")



@router.get("/v1/update_bar_qr")
def generate_qrcodes_for_existing_inventory(db: Session = Depends(get_db)):
    vehs = db.query(Vehicle).all()  # Fetch all vehicle records
    for veh in vehs:
        barcode_data = f"id: {veh.id}, name: {veh.name}, chassis_number:{veh.chassis_number}, make:{veh.make}, model:{veh.model}, year:{veh.year}, color:{veh.color}, fuel: {veh.fuel}, transmission:{veh.transmission}, condition:{veh.condition}, total_price:{veh.total_price}, mileage:{veh.mileage}, sold_price:{veh.sold_price}, status:{veh.status}"
        barcode_path = generate_barcode_vehicle(barcode_data, veh.id)
        print("*****THE PATH}********")
        print(barcode_path)
        print("*****END********")

        # vehicle.qrcode_path = qrcode_path  # Update the vehicle record with the QR code path
        path = db.query(Images).filter(Images.fk_vehicle_id==veh.id).first()
        if path:
            print("Barcode Avaliable Update")
            print(barcode_path)
            path.barcode = barcode_path
            db.commit()
            db.refresh(path)
            print(f"Done for {veh.id}")
        else:
            print("Barcode Not Avaliable Make New")
            add_barcode = Images(
                fk_vehicle_id = veh.id,
                barcode=barcode_path
            )
            db.add(add_barcode)
            db.commit()
            db.refresh(add_barcode)
        db.commit()
        db.refresh(veh)
        print(f"*********************refreshed {veh.id}*********************")


"""*******************Update status outside***************"""

@router.patch("/v1/vehicles/update-status")
def update_vehicle_status(update_data: UpdateVehicleStatus, db: Session = Depends(get_db)):
    # Fetch the vehicle from the database
    if update_data.chassis_no:
        data = db.query(Vehicle).filter(Vehicle.chassis_number == update_data.chassis_no).first()
        if not data:
            raise HTTPException(status_code=404, detail="Vehicle not found")

    # Update only the specified fields
    if update_data.status:
        data.status = update_data.status
    if update_data.sold_price is not None:
        data.sold_price = update_data.sold_price
    if update_data.recieved_amount is not None:
        data.recieved_amount = update_data.recieved_amount
    if update_data.balance_amount is not None:
        data.balance_amount = update_data.balance_amount

    # Save the changes
    db.commit()
    db.refresh(data)
    return {
        "status": data.status,
        "sold_price": data.sold_price,
        "recieved_amount": data.recieved_amount,
        "balance_amount": data.balance_amount,
    }


"""*******************Update status outside***************"""

@router.patch("/v1/vehicles_parts_container/update-status")
def update_vehicle_status(update_data: UpdateVehiclePartsStatusContainer, db: Session = Depends(get_db)):
    # Fetch the vehicle from the database
    if update_data.chassis_no:
        data = db.query(Vehicle).filter(Vehicle.chassis_number == update_data.chassis_no).first()
        if not data:
            raise HTTPException(status_code=404, detail="Vehicle not found")
    # Update only the specified fields
    if update_data.status:
        data.status = update_data.status

    # Save the changes
    db.commit()
    db.refresh(data)
    return {
        "status": data.status
    }



"""****************Google Reviews****************"""
# Your Google API key
GOOGLE_API_KEY = "AIzaSyB7snqxODPiRVEvFChFwdTOGTbh_j_AWpI"

@router.get("/v1/get_google_reviews")
def get_business_reviews(db: Session = Depends(get_db)):
    """
    Fetch reviews for the given Place ID.
    """
    place_id = "ChIJHeWEid9nXz4R4zb0hhzhtJU"
    url = "https://maps.googleapis.com/maps/api/place/details/json"
    params = {
        "place_id": place_id,
        "fields": "name,rating,review",
        "key": GOOGLE_API_KEY
    }

    headers = {
        "Content-Type": "application/json",  # Explicitly specify JSON content type
    }

    response = requests.get(url, params=params, headers=headers)
    if response.status_code == 200:
        data = response.json()
        # print("hello")
        # print(data)
        if "result" in data and "reviews" in data["result"]:
            reviews = data["result"]["reviews"]
            return {"business_name": data["result"]["name"], "reviews": reviews}
        else:
            raise HTTPException(status_code=404, detail="No reviews found for this Place ID.")
    else:
        raise HTTPException(status_code=response.status_code, detail="Failed to fetch reviews from Google.")
