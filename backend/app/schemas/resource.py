from typing import Optional
from pydantic import BaseModel, Field, ConfigDict

class ResourceCatalogResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    category: str
    unit: str
    description: str
    is_active: bool

class HospitalResourceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    hospital_id: str
    resource_id: str
    resource_name: Optional[str] = None
    resource_category: Optional[str] = None
    resource_unit: Optional[str] = None
    total_quantity: int
    available_quantity: int
    reserved_quantity: int
    status: str

class HospitalResourceUpdate(BaseModel):
    total_quantity: Optional[int] = Field(None, ge=0)
    available_quantity: Optional[int] = Field(None, ge=0)
    reserved_quantity: Optional[int] = Field(None, ge=0)
    status: Optional[str] = None

class ResourceQuantityAdjustment(BaseModel):
    resource_id: str
    delta_available: int  # +1 or -1 or custom adjustment
