from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict

class ResourceRequirementItem(BaseModel):
    resource_id: str
    quantity: int = Field(1, ge=1)
    is_critical: bool = True

class ReferralCreateRequest(BaseModel):
    patient_id: str
    urgency: str = Field("MEDIUM", pattern="^(LOW|MEDIUM|HIGH|CRITICAL|low|medium|high|critical)$")
    clinical_summary: str = Field(..., min_length=3)
    specialist_needed: Optional[str] = ""
    notes: Optional[str] = ""
    required_resources: List[ResourceRequirementItem] = []
    
    # Backward compatibility with prototype booleans
    needs_icu: Optional[bool] = False
    needs_oxygen: Optional[bool] = False
    needs_ventilator: Optional[bool] = False

class ReferralResourceRequirementResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    resource_id: str
    resource_name: Optional[str] = None
    quantity: int
    is_critical: bool

class ReferralAmbulanceSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    vehicle_number: str
    driver_name: str
    driver_phone: str
    status: str
    current_latitude: float
    current_longitude: float
    last_location_update: Optional[datetime] = None

class ReferralResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    referral_number: str
    patient_id: str
    patient_name: str
    patient_age: Optional[int] = None
    patient_gender: Optional[str] = None
    phc_id: str
    phc_name: str
    phc_latitude: Optional[float] = None
    phc_longitude: Optional[float] = None
    hospital_id: Optional[str] = None
    hospital_name: Optional[str] = None
    hospital_latitude: Optional[float] = None
    hospital_longitude: Optional[float] = None
    urgency: str
    clinical_summary: str
    specialist_needed: Optional[str] = ""
    notes: Optional[str] = ""
    status: str
    created_at: datetime
    updated_at: datetime
    accepted_at: Optional[datetime] = None
    rejected_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    requirements: List[ReferralResourceRequirementResponse] = []
    ambulance: Optional[ReferralAmbulanceSummary] = None

class ReferralSendRequest(BaseModel):
    hospital_id: str

class ReferralRejectRequest(BaseModel):
    reason: Optional[str] = "Insufficient capacity"
