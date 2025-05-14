from app.db.db_setup import Base
from sqlalchemy import (
    Float, Column, ForeignKey, Integer, String, DateTime, func, Boolean, Enum, JSON, Text
)


class TimestampMixin:
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

class CMSHome(TimestampMixin, Base):
    __tablename__ = "cms_home"
    
    id = Column(Integer, primary_key=True, index=True)
    heroTitle = Column(String(255))
    mediaItems = Column(JSON)
    brands = Column(JSON)
    priceRanges = Column(JSON)
    bodyTypes = Column(JSON)
    categories = Column(JSON)
    fairTitle = Column(String(255))
    fairDescription = Column(Text)
    fairImage = Column(String(255), nullable=True)
    sliderText = Column(Text)
    dealTitle = Column(String(255))
    dealDescription = Column(Text)
    dealImage = Column(String(255), nullable=True)

class Notification(TimestampMixin, Base):
    __tablename__ = "notifications"
    id = Column(Integer, primary_key=True, index=True)
    fk_user_id = Column(Integer, ForeignKey("users.id"), index=True, nullable=True)
    message = Column(String(255), nullable=False)
    read = Column(Boolean, default=False)


class User(TimestampMixin, Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True, nullable=False)
    firstname = Column(String(255), index=True, nullable=False)
    lastname = Column(String(255), index=True, nullable=False)
    email = Column(String(255), unique=True, nullable=True, index=True)
    uid = Column(String(255), unique=True, nullable=True, index=True)  # new field added
    phonenumber = Column(String(15), unique=True, nullable=True)
    original_password = Column(String(255), nullable=True)  # new field added
    password = Column(String(255), nullable=True)
    role = Column(String(55), nullable=True)
    status = Column(Boolean, default=False)
    side = Column(String(55), nullable=True)
    terms_agreement = Column(String(20), nullable=True)
    mfa_enabled = Column(String(20), nullable=True)
    mfa_secret = Column(String(255), nullable=True)
    emirates_id = Column(String(25), nullable=True)
    address = Column(String(255), nullable=True)


class PersonalDetails(TimestampMixin, Base):
    __tablename__ = "personaldetails"
    id = Column(Integer, primary_key=True, index=True, nullable=False)
    fk_user_id = Column(Integer, ForeignKey("users.id"), index=True, nullable=False)
    firstname = Column(String(255), index=True, nullable=False)
    lastname = Column(String(255), index=True, nullable=False)
    mobilenumber = Column(String(15), unique=True, nullable=False)  # if awais can take this from the User table it will be more good
    ID_number =  Column(String(15), unique=True, nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)

class Container(TimestampMixin, Base):
    __tablename__ = "containers"
    id = Column(Integer, primary_key=True, index=True, nullable=False)
    shipper = Column(String(255), nullable=True)
    shipping_company = Column(String(255), nullable=True)
    bl_number = Column(String(255), unique=True, nullable=True, default=None)
    container_number = Column(String(255), nullable=True, default=None)
    seal_number = Column(String(255), nullable=True, default=None)
    gross_weight = Column(String(255), nullable=True, default=None)
    port_of_discharge = Column(String(255), nullable=True)
    port_of_loading = Column(String(255), nullable=True)
    no_of_units = Column(String(255), nullable=True)
    status = Column(String(255), nullable=True)
    description = Column(String(512), nullable=True)
    eta = Column(String(512), nullable=True)

class Invoice(TimestampMixin, Base):
    __tablename__ = "invoice"
    id = Column(Integer, primary_key=True, index=True, nullable=False)
    first_name = Column(String(55), nullable=True)
    last_name = Column(String(55), nullable=True)
    cell_number = Column(String(55), nullable=True)
    whatsapp_number = Column(String(55), nullable=True)
    email_address = Column(String(55), nullable=True)
    address = Column(String(55), nullable=True)
    vat = Column(String(15), nullable=True)
    tax = Column(Float, nullable=True, default=0.0)
    sub_total = Column(Float, nullable=True, default=0.0)
    total = Column(Float, nullable=True, default=0.0)

class Vehicle(TimestampMixin, Base):
    __tablename__ = "vehicles"
    id = Column(Integer, primary_key=True, index=True, nullable=False)
    fk_user_id = Column(Integer, ForeignKey("users.id"), index=True, nullable=False)
    fk_container_id = Column(Integer, ForeignKey("containers.id"), index=True, nullable=True)
    fk_invoice_id = Column(Integer, ForeignKey("invoice.id"), index=True, nullable=True)
    body_type = Column(String(55), nullable=True)
    drive_type = Column(String(55), nullable=True)
    make = Column(String(55), nullable=True)
    model = Column(String(55), nullable=True)
    year = Column(String(55), nullable=True)
    title = Column(String(55), nullable=True)
    name = Column(String(55), nullable=True)
    chassis_number = Column(String(55), nullable=True)
    mileage = Column(String(55), nullable=True)
    damage_details = Column(String(255), nullable=True)
    transmission = Column(String(55), nullable=True)
    clynder = Column(String(55), nullable=True)
    location = Column(String(256), nullable=True)
    color = Column(String(55), nullable=True)
    fuel = Column(String(55), nullable=True)
    engine = Column(String(55), nullable=True)
    status = Column(String(55), nullable=True)
    barcode = Column(String(50), nullable=True)
    qrcode = Column(String(50), nullable=True)
    description = Column(String(600), nullable=True)
    grade = Column(String(55), nullable=True) # New field
    score = Column(String(55), nullable=True) # New field
    steer = Column(String(55), nullable=True) # New field
    displacement = Column(String(55), nullable=True) # New field
    total_price = Column(Float, nullable=True, default=0.0) # New field
    sold_price = Column(Float, nullable=True, default=0.0) # New field
    recieved_amount = Column(Float, nullable=True, default=0.0) # New field
    balance_amount = Column(Float, nullable=True, default=0.0) # New field
    auction_result = Column(String(55), nullable=True) # New field
    condition = Column(String(255), nullable=True)  # New field for condition reporting
    doors = Column(String(55), nullable=True)
    engine_name = Column(String(55), nullable=True)
    supplier = Column(String(55), nullable=True)
    is_clear = Column(Boolean, default=False)  # New field to mark as "Clear"
    report_status = Column(String(20), nullable=True, default='draft')  # Status: 'draft', 'confirmed'
    feature = Column(String(55), nullable=True)
    sold_by = Column(String(55), nullable=True)
    uploaded_by = Column(String(55), nullable=True)
    


class VehicleInterior(TimestampMixin, Base):
    __tablename__ = "interior"
    id = Column(Integer, primary_key=True, index=True, nullable=False)
    fk_vehicle_id = Column(Integer, ForeignKey("vehicles.id"), index=True, nullable=False)  
    air_conditioner = Column(Boolean, default=False)
    digital_odometer = Column(Boolean, default=False)
    heater = Column(Boolean, default=False)
    sunroof = Column(Boolean, default=False)
    power_windows = Column(Boolean, default=False)
    tv_led = Column(Boolean, default=False)
    leather_seats = Column(Boolean, default=False)
    tachometer = Column(Boolean, default=False)
    headlight_leveler = Column(Boolean, default=False)
    am_fm_radio = Column(Boolean, default=False)
    climate_control = Column(Boolean, default=False)
    armrest_console = Column(Boolean, default=False)
    rear_seat_armrest_centre_console = Column(Boolean, default=False)

class VehicleSafety(TimestampMixin, Base):
    __tablename__ = "safety"
    id = Column(Integer, primary_key=True, index=True, nullable=False)
    fk_vehicle_id = Column(Integer, ForeignKey("vehicles.id"), index=True, nullable=False)  
    abs_antilock_braking = Column(Boolean, default=False)
    child_safety_lock = Column(Boolean, default=False)
    driver_air_bag = Column(Boolean, default=False)
    passanger_air_bag = Column(Boolean, default=False)
    rear_seat_air_bag = Column(Boolean, default=False)
    curtain_air_bag = Column(Boolean, default=False)
    power_door_lock = Column(Boolean, default=False)
    traction_control = Column(Boolean, default=False)
    oil_brakes = Column(Boolean, default=False)
    air_brakes = Column(Boolean, default=False)
    tool_kit = Column(Boolean, default=False)
    stepney_tyre = Column(Boolean, default=False)
    foot_parking_brake = Column(Boolean, default=False)



class VehicleExterior(TimestampMixin, Base):
    __tablename__ = "exterior"
    id = Column(Integer, primary_key=True, index=True, nullable=False)
    fk_vehicle_id = Column(Integer, ForeignKey("vehicles.id"), index=True, nullable=False)  
    fog_lights_front = Column(Boolean, default=False)
    alloy_rims = Column(Boolean, default=False)
    high_deck = Column(Boolean, default=False)
    electric_pump = Column(Boolean, default=False)
    justlow = Column(Boolean, default=False)
    crane_step = Column(Boolean, default=False)
    HID_headlights = Column(Boolean, default=False)
    rear_wiper = Column(Boolean, default=False)
    sun_visor = Column(Boolean, default=False)



class VehicleComfortConvenience(TimestampMixin, Base):
    __tablename__ = "comfortconvenience"
    id = Column(Integer, primary_key=True, index=True, nullable=False)
    fk_vehicle_id = Column(Integer, ForeignKey("vehicles.id"), index=True, nullable=False)
    power_streeing = Column(Boolean, default=False)
    push_start_smartkey = Column(Boolean, default=False)
    keyless_entry = Column(Boolean, default=False)
    key_start = Column(Boolean, default=False)
    navigation = Column(Boolean, default=False)
    remote_controller = Column(Boolean, default=False)
    android_led = Column(Boolean, default=False)
    bluetooth = Column(Boolean, default=False)
    front_door_speaker = Column(Boolean, default=False)
    rear_door_speaker = Column(Boolean, default=False)
    rear_deck_speaker = Column(Boolean, default=False)
    ECO_mode = Column(Boolean, default=False)
    heated_seats = Column(Boolean, default=False)
    power_seats = Column(Boolean, default=False)
    power_side_mirrors = Column(Boolean, default=False)
    electric_rearview_mirror = Column(Boolean, default=False)
    dashboard_speakers = Column(Boolean, default=False)


class DimensionCapicity(TimestampMixin, Base):
    __tablename__ = "dimensioncapicity"
    id = Column(Integer, primary_key=True, index=True, nullable=False)
    fk_vehicle_id = Column(Integer, ForeignKey("vehicles.id"), index=True, nullable=False) 
    max_length = Column(String(255), nullable=True)
    height = Column(String(255), nullable=True)
    wheel_base = Column(String(255), nullable=True)
    height_including_roof_rails = Column(String(255), nullable=True)
    luggage_capacity_seatsup = Column(String(255), nullable=True)
    luggage_capacity_seatsdown = Column(String(255), nullable=True)
    width = Column(String(255), nullable=True)
    width_including_mirrors = Column(String(255), nullable=True)
    gross_vehicle_weight = Column(String(255), nullable=True)
    max_loading_weight = Column(String(255), nullable=True)
    max_roof_load = Column(String(255), nullable=True)
    number_of_seats = Column(String(255), nullable=True)


class EngineTransmisison(TimestampMixin, Base):
    __tablename__ = "enginetransmisison"
    id = Column(Integer, primary_key=True, index=True, nullable=False)
    fk_vehicle_id = Column(Integer, ForeignKey("vehicles.id"), index=True, nullable=False) 
    fuel_tank_capacity = Column(String(255), nullable=True)
    max_towing_weight_braked = Column(String(255), nullable=True)
    max_towing_weight_unbraked = Column(String(255), nullable=True)
    minimum_kerbweight = Column(String(255), nullable=True)
    turning_circle_kerb_to_kerb = Column(String(255), nullable=True)


class Images(TimestampMixin, Base):
    __tablename__ = "images"
    id = Column(Integer, primary_key=True, index=True, nullable=False)
    fk_vehicle_id = Column(Integer, ForeignKey("vehicles.id"), index=True, nullable=True)
    fk_personal_id = Column(Integer, ForeignKey("personaldetails.id"), index=True, nullable=True)
    fk_user_id = Column(Integer, ForeignKey("users.id"), index=True, nullable=True)
    fk_container_id = Column(Integer, ForeignKey("containers.id"), index=True, nullable=True)
    image = Column(String(2000), nullable=True)  # Make this long enough for multiple paths
    barcode = Column(String(255), nullable=True)


class CMSAboutUs(Base):
    __tablename__ = "cms_about_us"
    
    id = Column(Integer, primary_key=True, index=True)
    sectionOneTitle = Column(String(255))
    sectionOneDescription = Column(Text)
    sectionTwoTitle = Column(String(255))
    sectionTwoDescription = Column(Text)
    sectionTwoImage = Column(String(255), nullable=True)
    sectionThreeTitle = Column(String(255))
    sectionThreeH1 = Column(String(255))
    sectionThreeD1 = Column(Text)
    sectionThreeH2 = Column(String(255))
    sectionThreeD2 = Column(Text)
    sectionThreeH3 = Column(String(255))
    sectionThreeD3 = Column(Text)
    sectionFourTitle = Column(String(255))
    sectionFourDescription = Column(Text)

class CMSInventory(Base):
    __tablename__ = "cms_inventory"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255))
    description = Column(Text)
    image = Column(String(255), nullable=True)

class CMSProductDetail(Base):
    __tablename__ = "cms_product_detail"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255))
    description = Column(Text)
    h1 = Column(String(255))
    h1Description = Column(Text)
    h2 = Column(String(255))
    h2Description = Column(Text)
    h3 = Column(String(255))
    h3Description = Column(Text)
    title2 = Column(String(255))
    description2 = Column(Text)
    image = Column(String(255), nullable=True)

class CMSContact(Base):
    __tablename__ = "cms_contact"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255))
    description = Column(Text)
    phone = Column(String(50))
    email = Column(String(255))
    location = Column(Text)
    hours = Column(Text)
    map_url = Column(Text)


class Role(TimestampMixin, Base):
    __tablename__ = "roles"
    id = Column(Integer, primary_key=True, index=True, nullable=False)
    name = Column(String(255), index=True, nullable=False)
    right_read = Column(Boolean, default=False)
    right_write = Column(Boolean, default=False)
    right_edit = Column(Boolean, default=False)
    right_delete = Column(Boolean, default=False)
    right_dashboard = Column(Boolean, default=False)
    right_container = Column(Boolean, default=False)
    right_product = Column(Boolean, default=False)
    right_employee_management = Column(Boolean, default=False)
    right_reports = Column(Boolean, default=False)
    right_invoices = Column(Boolean, default=False)
    right_setting = Column(Boolean, default=False)
    right_help_center = Column(Boolean, default=False)
    right_feed_back = Column(Boolean, default=False)
    right_status_permission = Column(Boolean, default=False)
    right_generate = Column(Boolean, default=False)
    right_overseas_employee = Column(Boolean, default=False)
    right_customer_management = Column(Boolean, default=False)
    right_customer_management_read = Column(Boolean, default=False)
    right_customer_management_write = Column(Boolean, default=False)
    right_customer_management_edit = Column(Boolean, default=False)
    right_customer_management_delete = Column(Boolean, default=False)
    right_auction_management = Column(Boolean, default=False)
    right_auction_management_read = Column(Boolean, default=False)
    right_auction_management_write = Column(Boolean, default=False)
    right_auction_management_edit = Column(Boolean, default=False)
    right_auction_management_delete = Column(Boolean, default=False)
    
    created_by = Column(String(255), index=True, nullable=True)
