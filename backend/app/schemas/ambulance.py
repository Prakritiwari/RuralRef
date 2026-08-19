from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict

class AmbulanceCreate(BaseModel):
    hospital_id: str
    vehicle_number: str
    driver_name: str
    driver_phone: str
    ambulance_type: str = "ADVANCED_LIFE_SUPPORT"
    initial_latitude: float
    initial_longitude: float

class AmbulanceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    hospital_id: str
    hospital_name: Optional[str] = None
    vehicle_number: str
    driver_name: str
    driver_phone: str
    ambulance_type: str
    status: str
    current_latitude: float
    current_longitude: float
    active_referral_id: Optional[str] = None
    last_location_update: datetime
    is_active: bool

class AmbulanceAssignRequest(BaseModel):
    referral_id: str

class LocationUpdateRequest(BaseModel):
    latitude: float = Field(..., ge=-90.0, le=90.0)
    longitude: float = Field(..., ge=-180.0, le=180.0)
    speed: Optional[float] = 0.0
    heading: Optional[float] = 0.0
    accuracy: Optional[float] = 5.0
    timestamp: Optional[datetime] = None

class AmbulanceStatusUpdateRequest(BaseModel):
    status: str = Field(..., pattern="^(AVAILABLE|ASSIGNED|EN_ROUTE_TO_PHC|PATIENT_PICKED_UP|TRANSPORTING|ARRIVED|OFFLINE)$")
    notes: Optional[str] = ""
