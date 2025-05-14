from pydantic import BaseModel, Field
from typing import Optional, List, Dict

class User(BaseModel):
    firstname: str = Field(None, min_length=3, max_length=50)
    lastname: str = Field(None, min_length=3, max_length=50)
    email: str = Field(None, max_length=255)
    phonenumber: str = Field(None, max_length=15)
    password: str = Field(None, min_length=6)
    role: str = Field(None, max_length=20)
    status: bool
    side: str = Field(None, max_length=20)
    terms_agreement: str = Field(None, max_length=20)
    mfa_enabled: str

    class Config:
        orm_mode = True 

class VehInterior(BaseModel):
    air_conditioner: Optional[bool] = None
    digital_odometer: Optional[bool] = None
    heater: Optional[bool] = None
    sunroof: Optional[bool] = None
    power_windows: Optional[bool] = None
    tv_led: Optional[bool] = None
    leather_seats: Optional[bool] = None
    tachometer: Optional[bool] = None
    headlight_leveler: Optional[bool] = None
    am_fm_radio: Optional[bool] = None
    climate_control: Optional[bool] = None
    armrest_console: Optional[bool] = None
    rear_seat_armrest_centre_console: Optional[bool] = None
    class Config:
        orm_mode = True

class VehSafety(BaseModel):
    abs_antilock_braking: Optional[bool] = None
    child_safety_lock: Optional[bool] = None
    driver_air_bag: Optional[bool] = None
    passanger_air_bag: Optional[bool] = None
    rear_seat_air_bag: Optional[bool] = None
    curtain_air_bag: Optional[bool] = None
    power_door_lock: Optional[bool] = None
    traction_control: Optional[bool] = None
    oil_brakes: Optional[bool] = None
    air_brakes: Optional[bool] = None
    tool_kit: Optional[bool] = None
    stepney_tyre: Optional[bool] = None
    foot_parking_brake: Optional[bool] = None
    class Config:
        orm_mode = True

class VehExterior(BaseModel):
    fog_lights_front: Optional[bool] = None
    alloy_rims: Optional[bool] = None
    high_deck: Optional[bool] = None
    electric_pump: Optional[bool] = None
    justlow: Optional[bool] = None
    crane_step: Optional[bool] = None
    HID_headlights: Optional[bool] = None
    rear_wiper: Optional[bool] = None
    sun_visor: Optional[bool] = None
    class Config:
        orm_mode = True

class ComfortConvenience(BaseModel):
    power_streeing: Optional[bool] = None
    push_start_smartkey: Optional[bool] = None
    keyless_entry: Optional[bool] = None
    key_start: Optional[bool] = None
    navigation: Optional[bool] = None
    remote_controller: Optional[bool] = None
    android_led: Optional[bool] = None
    bluetooth: Optional[bool] = None
    front_door_speaker: Optional[bool] = None
    rear_door_speaker: Optional[bool] = None
    rear_deck_speaker: Optional[bool] = None
    ECO_mode: Optional[bool] = None
    heated_seats: Optional[bool] = None
    power_seats: Optional[bool] = None
    power_side_mirrors: Optional[bool] = None
    electric_rearview_mirror: Optional[bool] = None
    dashboard_speakers: Optional[bool] = None
    class Config:
        orm_mode = True

class DimensionCap(BaseModel):
    max_length: Optional[str] = None
    height: Optional[str] = None
    wheel_base: Optional[str] = None
    height_including_roof_rails: Optional[str] = None
    luggage_capacity_seatsup: Optional[str] = None
    luggage_capacity_seatsdown: Optional[str] = None
    width: Optional[str] = None
    width_including_mirrors: Optional[str] = None
    gross_vehicle_weight: Optional[str] = None
    max_loading_weight: Optional[str] = None
    max_roof_load: Optional[str] = None
    number_of_seats: Optional[str] = None
    class Config:
        orm_mode = True

class EngineTrans(BaseModel):
    fuel_tank_capacity: Optional[str] = None
    max_towing_weight_braked: Optional[str] = None
    max_towing_weight_unbraked: Optional[str] = None
    minimum_kerbweight: Optional[str] = None
    turning_circle_kerb_to_kerb: Optional[str] = None
    class Config:
        orm_mode = True


class UpdateVehicleStatus(BaseModel):
    chassis_no: Optional[str] = None
    part_id: Optional[str] = None
    status: str  # Required to change from 'instock' to 'outstock'
    sold_price: Optional[float] = None
    recieved_amount: Optional[float] = None
    balance_amount: Optional[float] = None


class UpdateVehiclePartsStatusContainer(BaseModel):
    chassis_no: Optional[str] = None
    part_id: Optional[str] = None
    status: str  # Required to change to 'instock'

class UpdateContainerStatus(BaseModel):
    container_id: Optional[str] = None
    status: str  # Required to change from 'upComing' to 'arrived'
class ComfortUsabilityFeaturesSchema(BaseModel):
    riding_ergonomics: Optional[bool] = None
    seat: Optional[bool] = None
    instrumentation: Optional[bool] = None
    fuel_capacity: Optional[bool] = None

    class Config:
        orm_mode = True

class SafetyFeaturesSchema(BaseModel):
    high_performance_brakes: Optional[bool] = None
    high_quality_tires: Optional[bool] = None

    class Config:
        orm_mode = True

class ConvenienceFeaturesSchema(BaseModel):
    lighting: Optional[bool] = None
    storage: Optional[bool] = None
    security: Optional[bool] = None
    adjustable_suspension: Optional[bool] = None

    class Config:
        orm_mode = True

class VehMake(BaseModel):
    vehmake: Optional[str]=None

class VehModel(BaseModel):
    fk_vehmake_id: Optional[int] = None
    vehmodel: Optional[str]=None


class VehBodyType(BaseModel):
    vehbodytype: Optional[str]=None

class TruckBodyTypeSchema(BaseModel):
    truckbodytype: Optional[str]=None

class InventoryVehicles(BaseModel):
    filter_status: Optional[str] = None

class QuoteRequest(BaseModel):
    veh_id: int
    name: Optional[str] = None
    country: Optional[str] = None
    city: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    whatsapp: Optional[str] = None
    remarks: Optional[str] = None

class ChassisDetail(BaseModel):
    chassis_number: Optional[str] = None

class InventoryRetails(BaseModel):
    report_type: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    download_type: Optional[str] = None

class VehTransmission(BaseModel):
    vehtransmission: Optional[str]=None

class VehColor(BaseModel):
    vehcolor: Optional[str]=None

class VehDisplacement(BaseModel):
    vehdisplacement: Optional[str]=None

class VehDriveType(BaseModel):
    vehdrivetype: Optional[str]=None

class VehScore(BaseModel):
    vehscore: Optional[str]=None

class Signin(BaseModel):
    email: str = Field(max_length=150)
    password: str = Field(min_length=6)

class Vehicles(BaseModel):
    fk_container_id: Optional[int] = None
    body_type: Optional[str] = None
    drive_type: Optional[str] = None
    make: Optional[str] = None
    model: Optional[str] = None
    year: Optional[str] = None
    title: Optional[str] = None
    name: Optional[str] = None
    chassis_number: Optional[str] = None
    mileage: Optional[str] = None
    damage_details: Optional[str] = None
    transmission: Optional[str] = None
    clynder: Optional[str] = None
    location: Optional[str] = None
    color: Optional[str] = None
    fuel: Optional[str] = None
    engine: Optional[str] = None
    status: Optional[str] = None
    description: Optional[str] = None
    grade: Optional[str]= None
    score: Optional[str]= None
    steer: Optional[str] = None
    displacement: Optional[str]= None
    total_price: Optional[float]= None
    sold_price: Optional[float]= None
    recieved_amount: Optional[float]= None
    balance_amount: Optional[float]= None
    auction_result: Optional[str]= None
    condition: Optional[str]= None
    doors: Optional[str]= None
    engine_name: Optional[str]= None
    supplier: Optional[str]= None
    is_clear: Optional[bool]= None
    report_status: Optional[str]= None
    feature: Optional[str]= None

class PublishVehicle(Vehicles):
    uploaded_by: Optional[str]= None
    sold_by: Optional[str]= None



class VehicleUpdate(Vehicles):
    pass

    class Config:
        orm_mode = True


class CMSHomeBase(BaseModel):
    heroTitle: str
    mediaItems: List[Dict]
    brands: List[Dict]
    priceRanges: List[Dict]
    bodyTypes: List[Dict]
    categories: List[Dict]
    fairTitle: str
    fairDescription: str
    fairImage: Optional[str] = None
    sliderText: str
    dealTitle: str
    dealDescription: str
    dealImage: Optional[str] = None

class CMSHomeCreate(CMSHomeBase):
    pass

class CMSHomeUpdate(CMSHomeBase):
    pass

class CMSHomeResponse(CMSHomeBase):
    id: int
    
    class Config:
        from_attributes = True

class UidUserAdmin(BaseModel):
    firstname: str = Field(None, min_length=3, max_length=50)
    lastname: str = Field(None, min_length=3, max_length=50)
    email: str = Field(None, max_length=255)
    phonenumber: str = Field(None, max_length=15)
    role: str = Field(None, max_length=20)
    status: bool

    class Config:
        orm_mode = True


class SigninUid(BaseModel):
    uid: str = Field(max_length=150)
    password: str = Field(min_length=6)



class UidUser(BaseModel):
    firstname: str = Field(None, min_length=3, max_length=50)
    lastname: str = Field(None, min_length=3, max_length=50)
    email: str = Field(None, max_length=255)
    phonenumber: str = Field(None, max_length=15)
    role: str = Field(None, max_length=20)
    status: bool
    side: str = Field(None, max_length=20)
    terms_agreement: str = Field(None, max_length=20)
    mfa_enabled: str

    class Config:
        orm_mode = True
        
class PublishDataUid(UidUser):
    original_password: str = Field(None, min_length=6)
    password: str = Field(None, min_length=6)
    uid: Optional[str]
    mfa_secret: Optional[str]

class PublishDataUidAdmin(UidUser):
    side: str = Field(None, max_length=20)
    terms_agreement: str = Field(None, max_length=20)   
    original_password: str = Field(None, min_length=6)
    password: str = Field(None, min_length=6)
    uid: Optional[str]
    mfa_enabled: str
    mfa_secret: Optional[str]

class UidCustomerAdmin(BaseModel):
    firstname: str = Field(None, min_length=3, max_length=50)
    lastname: str = Field(None, min_length=3, max_length=50)
    email: Optional[str] = None
    phonenumber: str = Field(None, max_length=15)
    role: str = Field(None, max_length=20)
    status: bool
    emirates_id: Optional[str]
    address: Optional[str]

    class Config:
        orm_mode = True

class PublishDataUidCustomerAdmin(UidCustomerAdmin):
    side: str = Field(None, max_length=20)
    terms_agreement: str = Field(None, max_length=20)   
    original_password: str = Field(None, min_length=6)
    password: str = Field(None, min_length=6)
    uid: Optional[str]
    mfa_enabled: str
    mfa_secret: Optional[str]


class SignupUpdateUid(BaseModel):
    firstname: str = Field(None, min_length=3, max_length=50)
    lastname: str = Field(None, min_length=3, max_length=50)
    email: str = Field(None, max_length=255)
    phonenumber: str = Field(None, max_length=15)
    # password: str = Field(None, min_length=8)
    role: str = Field(None, max_length=20)
    status: bool
    emirates_id: Optional[str]
    address: Optional[str]
    side: str = Field(None, max_length=20)
    terms_agreement: str = Field(None, max_length=20)
    mfa_enabled: str

    class Config: 
        orm_mode = True

class CustomerReports(BaseModel):
    download_type: Optional[str] = None


# About Us Schema
class CMSAboutUsBase(BaseModel):
    sectionOneTitle: str
    sectionOneDescription: str
    sectionTwoTitle: str
    sectionTwoDescription: str
    sectionTwoImage: Optional[str] = None
    sectionThreeTitle: str
    sectionThreeH1: str
    sectionThreeD1: str
    sectionThreeH2: str
    sectionThreeD2: str
    sectionThreeH3: str
    sectionThreeD3: str
    sectionFourTitle: str
    sectionFourDescription: str

class CMSAboutUsResponse(CMSAboutUsBase):
    id: int

# Inventory Schema
class CMSInventoryBase(BaseModel):
    title: str
    description: str
    image: Optional[str] = None

class CMSInventoryResponse(CMSInventoryBase):
    id: int

# Product Detail Schema
class CMSProductDetailBase(BaseModel):
    title: str
    description: str
    h1: str
    h1Description: str
    h2: str
    h2Description: str
    h3: str
    h3Description: str
    title2: str
    description2: str
    image: Optional[str] = None

class CMSProductDetailResponse(CMSProductDetailBase):
    id: int

# Contact Schema
class CMSContactBase(BaseModel):
    title: str
    description: str
    phone: str
    email: str
    location: str
    hours: str
    map_url: str

class CMSContactResponse(CMSContactBase):
    id: int


class Roles(BaseModel):
    name: Optional[str] = None
    right_read: Optional[bool]= False
    right_write: Optional[bool]= False
    right_edit: Optional[bool]= False
    right_delete: Optional[bool]= False
    right_dashboard: Optional[bool]= False
    right_container: Optional[bool]= False
    right_product: Optional[bool]= False
    right_employee_management: Optional[bool]= False
    right_reports: Optional[bool]= False
    right_invoices: Optional[bool]= False
    right_setting: Optional[bool]= False
    right_help_center: Optional[bool]= False
    right_feed_back: Optional[bool]= False
    right_status_permission: Optional[bool]= False
    right_generate: Optional[bool]= False
    right_overseas_employee: Optional[bool]= False
    right_customer_management: Optional[bool]= False
    right_customer_management_read: Optional[bool]= False
    right_customer_management_write: Optional[bool]= False
    right_customer_management_edit: Optional[bool]= False
    right_customer_management_delete: Optional[bool]= False
    right_auction_management: Optional[bool]= False
    right_auction_management_read: Optional[bool]= False
    right_auction_management_write: Optional[bool]= False
    right_auction_management_edit: Optional[bool]= False
    right_auction_management_delete: Optional[bool]= False

    class Config:
        orm_mode = True