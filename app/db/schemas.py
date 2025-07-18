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

class FeedbackCreate(BaseModel):
    rating: int
    comment: str
    class Config:
        orm_mode = True

class FeedbackClientSchema(BaseModel):
    title: str
    description: str
    class Config:
        orm_mode = True


class MessageData(BaseModel):
    name: str
    email: str
    phone: str
    message: str

class SubscriptionData(BaseModel):
    email: str


class SearchInventories(BaseModel):
    search_query: Optional[str] = None


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
    ambient_lighting_mood_lighting: Optional[bool] = None
    digital_instrument_cluster: Optional[bool] = None
    head_up_display: Optional[bool] = None
    wireless_charging_pad: Optional[bool] = None
    multi_zone_climate_control: Optional[bool] = None
    premium_sound_system: Optional[bool] = None
    wood_interior: Optional[bool] = None
    aluminum_tri_interior: Optional[bool] = None
    ventilated_seats: Optional[bool] = None
    panoramic_sunroof: Optional[bool] = None
    rear_entertainment_screens: Optional[bool] = None
    power_adjustable_steering_column: Optional[bool] = None
    memory_seats: Optional[bool] = None
    alcantara_carbon_fiber_trim: Optional[bool] = None
    alarm: Optional[bool] = None
    cooled_rear_seat: Optional[bool] = None
    wireless_smartphone_charger: Optional[bool] = None
    usb_type_c_port: Optional[bool] = None
    usb_20_port: Optional[bool] = None
    v12_power_outlet: Optional[bool] = None
    rear_charging_ports: Optional[bool] = None
    
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
    adaptive_cruise_control: Optional[bool] = None
    blind_spot_monitoring: Optional[bool] = None
    lane_keep_assist: Optional[bool] = None
    lane_departure_warning: Optional[bool] = None
    degree_360_camera: Optional[bool] = None
    front_rear_parking_sensors: Optional[bool] = None
    automatic_emergency_braking: Optional[bool] = None
    pedestrian_detection: Optional[bool] = None
    cross_traffic_alert_rear: Optional[bool] = None
    driver_attention_warning: Optional[bool] = None
    night_vision_assist: Optional[bool] = None
    tire_pressure_monitoring_system: Optional[bool] = None
    collision_mitigation_system: Optional[bool] = None
    isofix_child_seat_mounts: Optional[bool] = None
    adaptive_lighting: Optional[bool] = None
    performance_kit_tuned: Optional[bool] = None
    parking_button: Optional[bool] = None
    manual_handbrake: Optional[bool] = None
    electronic_parking_brake_auto_hold: Optional[bool] = None

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
    matrix_led_laser_headlights: Optional[bool] = None
    automatic_headlight_on_off: Optional[bool] = None
    power_tailgate: Optional[bool] = None
    roof_rails_roof_rack: Optional[bool] = None
    dual_exhaust_pipes: Optional[bool] = None
    sport_exhaust: Optional[bool] = None
    rear_spoiler: Optional[bool] = None
    led_dlrs_daytime_running_lights: Optional[bool] = None
    auto_folding_side_mirrors: Optional[bool] = None
    frameless_doors: Optional[bool] = None
    charging_port: Optional[bool] = None
    soft_close_doors: Optional[bool] = None
    illuminated_logo_welcome_lights: Optional[bool] = None
    rain_sensing_wipers: Optional[bool] = None
    Performance_tyres: Optional[bool] = None
    side_mirrors_indicators: Optional[bool] = None
    sports_suspension: Optional[bool] = None
    premium_paint: Optional[bool] = None
    air_deflector: Optional[bool] = None

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
    wireless_apple_carplay_android_auto: Optional[bool] = None
    voice_control_system: Optional[bool] = None
    gesture_control: Optional[bool] = None
    remote_engine_start: Optional[bool] = None
    auto_dimming_rearview_mirror: Optional[bool] = None
    driver_seat_massager: Optional[bool] = None
    rear_window_sunshade_manual: Optional[bool] = None
    rear_window_sunshade_electric: Optional[bool] = None
    air_purifier_ionizer: Optional[bool] = None
    cabin_noise_cancellation: Optional[bool] = None
    smart_climate_control_ai_sensing: Optional[bool] = None
    ota_updates_over_the_air_software: Optional[bool] = None
    sports_drive_mode: Optional[bool] = None
    comfort_drive_mode: Optional[bool] = None
    snow_drive_mode: Optional[bool] = None
    intelligent_parking_assist_auto_park: Optional[bool] = None
    digital_key_smartphone: Optional[bool] = None
    electric_rear_seat_recline: Optional[bool] = None
    navigation_system: Optional[bool] = None
    power_locks: Optional[bool] = None
    tinted_windows: Optional[bool] = None
    rear_tv_screens: Optional[bool] = None
    cd_dvd_player: Optional[bool] = None
    mp3_interface: Optional[bool] = None

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
    status: str  # Required to change from 'instock' to 'outstock'
    sold_price: Optional[float] = None
    recieved_amount: Optional[float] = None
    balance_amount: Optional[float] = None


class UpdateVehiclePartsStatusContainer(BaseModel):
    chassis_no: Optional[str] = None
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

class VehIntColor(BaseModel):
    vehintcolor: Optional[str]=None

class VehExtColor(BaseModel):
    vehextcolor: Optional[str]=None

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
    intcolor: Optional[str] = None
    extcolor: Optional[str] = None
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
    motor: Optional[str]= None

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


class CMSDealBase(BaseModel):
    fairTitle: str
    fairDescription: str
    fairImage: Optional[str] = None
    sliderText: str
    dealTitle: str
    dealDescription: str
    dealImage: Optional[str] = None

class CMSDealCreate(CMSDealBase):
    pass

class CMSDealUpdate(CMSDealBase):
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
        
class PerformanceFeatureSchema(BaseModel):
    desmodromic_engine_technology: Optional[bool] = None
    fuel_injection: Optional[bool] = None
    lightweight_design: Optional[bool] = None
    high_performance_suspension: Optional[bool] = None

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
    right_cms: Optional[bool]= False

    class Config:
        orm_mode = True

class RoleName(BaseModel):
    name: Optional[str] = None

class VehImageSchema(BaseModel):
    image: Optional[str] = None
    fk_vehicle_id: Optional[int] = None
    class Config:
        orm_mode = True

class VehVideoSchema(BaseModel):
    video: Optional[str] = None
    fk_vehicle_id: Optional[int] = None
    class Config:
        orm_mode = True

class PricingData(BaseModel):
    # fk_vehicle_id: Optional[int]
    unit_purchase_price: Optional[float] = 0.0
    auction_fee: Optional[float] = 0.0
    commission: Optional[float] = 0.0
    transportation_cost: Optional[float] = 0.0
    vanning: Optional[float] = 0.0
    drayage: Optional[float] = 0.0
    freight: Optional[float] = 0.0
    interest_charges: Optional[float] = 0.0
    handlinf_fees: Optional[float] = 0.0
    total_fob: Optional[float] = 0.0
    
    # conversion rate of jpy to aed
    conversion_rate: Optional[float] = 0.0

    do_delivery_order: Optional[float] = 0.0
    transport_expense: Optional[float] = 0.0
    dpa_charges: Optional[float] = 0.0
    service_charges: Optional[float] = 0.0
    bank_charges: Optional[float] = 0.0
    export_paper_cost: Optional[float] = 0.0
    local_cost_aed: Optional[float] = 0.0
    total_cnf: Optional[float] = 0.0
    yard_commission: Optional[float] = 0.0
    cost_till_yard: Optional[float] = 0.0
    other_amount: Optional[float] = 0.0

    class Config:
        orm_mode = True


class ContainerBase(BaseModel):
    shipper: Optional[str] = None
    shipping_company: Optional[str] = None
    bl_number: Optional[str] = None
    container_number: Optional[str] = None
    seal_number: Optional[str] = None
    gross_weight: Optional[str] = None
    port_of_discharge: Optional[str] = None
    port_of_loading: Optional[str] = None
    no_of_units: Optional[str] = None
    status: Optional[str] = None
    description: Optional[str] = None
    eta: Optional[str] = None


class ContainerCreate(ContainerBase):
    pass

class ContainerUpdate(ContainerBase):
    pass

class ContainerSchema(ContainerBase):
    id: int

    class Config:
        orm_mode = True

class ContImageSchema(BaseModel):
    image: Optional[str] = None
    fk_container_id: Optional[int] = None
    class Config:
        orm_mode = True

class ContainerLocation(BaseModel):
    id: int
    current_latitude: float
    current_longitude: float
    tracking_status: str

    class Config:
        orm_mode = True


class BLNumber(BaseModel):
    bl_number: Optional[str] = None

class Contblnumber(BaseModel):
    bl_number: Optional[str] = None

class MonthSearch(BaseModel):
    month: Optional[str] = None


class Cont_blnumber(BaseModel):
    item: Optional[str] = None


class ContQuarter(BaseModel):
    quarter: Optional[str] = None
    

class MonthInput(BaseModel):
    month: str  # Example: "June"
    year: int   # Example: 2024

class InvoiceData(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    cell_number: Optional[str] = None
    whatsapp_number: Optional[str] = None
    email_address: Optional[str] = None
    address: Optional[str] = None
    vat: Optional[str] = None
    tax: Optional[float]
    sub_total: Optional[float]
    total: Optional[float]

class ContainerBase(BaseModel):
    shipper: Optional[str] = None
    shipping_company: Optional[str] = None
    bl_number: Optional[str] = None
    container_number: Optional[str] = None
    seal_number: Optional[str] = None
    gross_weight: Optional[str] = None
    port_of_discharge: Optional[str] = None
    port_of_loading: Optional[str] = None
    no_of_units: Optional[str] = None
    status: Optional[str] = None
    description: Optional[str] = None
    eta: Optional[str] = None

    class Config:
        from_attributes = True  # or extra = "ignore" if using Pydantic v1

class ContainerCreate(ContainerBase):
    pass

class ContainerUpdate(ContainerBase):
    pass


class ContainerStatus(BaseModel):
    status: Optional[str] = None


class ContainerLocationUpdate(BaseModel):
    current_latitude: float
    current_longitude: float
    tracking_status: str


class CustomerCreate(BaseModel):
    name: str
    phone_number: str
    email: Optional[str] = None  # Optional field for email

    class Config:
        orm_mode = True


class ItemCreate(BaseModel):
    transaction_id: int
    customer_id: int
    item_type: str
    item_name: str
    chassis_number: Optional[str] = None
    quantity: int = Field(default=1)
    notes: Optional[str] = None
    offer_price: Optional[float] = None
    status: str = Field(default="Reserved")
    category: Optional[str] = Field(default="Other")
    
    class Config:
        orm_mode = True


class TransactionCreate(BaseModel):
    customer_id: int
    item_id: int
    
    class Config:
        orm_mode = True

class StatusUpdate(BaseModel):
    new_status: str  # e.g., Reserved -> Sold

    class Config:
        orm_mode = True

class SearchQuery(BaseModel):
    query_to_search: str

    class Config:
        orm_mode = True

class SearchPrice(BaseModel):
    min_price: float = 0, 
    max_price: float = float("inf")
    class Config:
        orm_mode = True


class CustomerSearch(BaseModel):
    username: Optional[str] = None
    phonenumber: Optional[str] = None
    vehicle_name: Optional[str] = None
    chassis_number: Optional[str] = None
    user_id: Optional[int] = None
    vehicle_id: Optional[int] = None

    
class ContactDetail(BaseModel):
    contact: Optional[str] = None

class VehicleBidPlacing(BaseModel):
    chassis_number: str
    make: str
    model: str
    name: str
    bid_amount: str



class UidCustomerBidAdmin(BaseModel):
    # Customer Adding
    firstname: str = Field(None, min_length=3, max_length=50)
    lastname: str = Field(None, min_length=3, max_length=50)
    email: Optional[str] = None
    phonenumber: str = Field(None, max_length=15)
    role: str = Field(None, max_length=20)
    status: bool
    auction_id: Optional[int] = None
    emirates_id: Optional[str] = None
    address: Optional[str] = None
    vehicles: List[VehicleBidPlacing] = None

class PendingAmountAdding(BaseModel):
    type: str
    chassis_no: str
    part_id: str

    class Config:
        orm_mode = True

class ChangeAdminPassword(BaseModel):
    current_password: str
    password: str
    confirm_password: str