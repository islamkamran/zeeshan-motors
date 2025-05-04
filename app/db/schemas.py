from pydantic import BaseModel, Field
from typing import Optional, List, Dict

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