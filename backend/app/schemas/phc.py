from typing import Optional
from pydantic import BaseModel, ConfigDict

class PHCCreate(BaseModel):
    name: str
    code: str
    address: str
    district: str
    state: str = "Maharashtra"
    latitude: float
    longitude: float
    contact_phone: str
    contact_email: Optional[str] = ""

class PHCResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    code: str
    address: str
    district: str
    state: str
    latitude: float
    longitude: float
    contact_phone: str
    contact_email: str
    is_active: bool
