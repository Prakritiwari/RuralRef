from typing import List, Optional
from pydantic import BaseModel, ConfigDict
from .resource import HospitalResourceResponse

class HospitalResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    code: str
    district: str
    state: str
    level: str
    address: str
    latitude: float
    longitude: float
    phone: str
    email: str
    emergency_available: bool
    is_active: bool
    distance_km: Optional[float] = None
    estimated_travel_minutes: Optional[int] = None
    available_ambulances_count: Optional[int] = 0
    resources: Optional[List[HospitalResourceResponse]] = []

class HospitalRecommendationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    hospital_id: str
    hospital_name: str
    district: str
    level: str
    distance_km: float
    estimated_travel_minutes: int
    recommendation_score: float
    is_eligible: bool
    emergency_available: bool
    available_ambulances_count: int
    match_reasons: List[str]
    missing_resources: List[str]
    resource_breakdown: List[HospitalResourceResponse]
