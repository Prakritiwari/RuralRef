from typing import List, Optional
from pydantic import BaseModel
from .referral import ReferralResponse
from .hospital import HospitalResponse

class DashboardStatResponse(BaseModel):
    patients_count: int
    pending_referrals_count: int
    active_transfers_count: int
    available_ambulances_count: int
    total_hospitals_count: int

class DashboardResourceSummary(BaseModel):
    hospital_id: str
    hospital_name: str
    district: str
    icu_available: int
    oxygen_available: int
    ventilators_available: int
    blood_o_pos_available: Optional[int] = 0

class DashboardResponse(BaseModel):
    stats: DashboardStatResponse
    recent_referrals: List[ReferralResponse]
    hospital_capacities: List[DashboardResourceSummary]
    
    # Backward compatible fields for original UI
    patients: int
    pending_referrals: int
    active_transfers: int
    available_ambulances: int
    resources: List[dict]
