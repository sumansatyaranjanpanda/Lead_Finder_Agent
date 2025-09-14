from pydantic import BaseModel,EmailStr, HttpUrl, validator
from typing import List,TypedDict,Optional

class ProcurementContact(BaseModel):
    name: Optional[str]
    designation: Optional[str]
    email: Optional[EmailStr] = None
    linkedin: Optional[HttpUrl] = None


class CompanyInfo(BaseModel):
    company_name: str
    website: Optional[HttpUrl] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    procurement_contacts: List[ProcurementContact] = []


class BuyerState(BaseModel):
    location: str
    product: str
    companies: List[CompanyInfo] = []
    

