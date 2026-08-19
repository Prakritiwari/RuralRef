from .auth import RegisterRequest, LoginRequest, UserProfileResponse, AuthResponse
from .phc import PHCCreate, PHCResponse
from .hospital import HospitalResponse, HospitalRecommendationResponse
from .resource import (
    ResourceCatalogResponse,
    HospitalResourceResponse,
    HospitalResourceUpdate,
    ResourceQuantityAdjustment,
)
from .patient import PatientCreate, PatientResponse
from .referral import (
    ReferralCreateRequest,
    ReferralResponse,
    ResourceRequirementItem,
    ReferralSendRequest,
    ReferralRejectRequest,
)
from .ambulance import (
    AmbulanceCreate,
    AmbulanceResponse,
    AmbulanceAssignRequest,
    LocationUpdateRequest,
    AmbulanceStatusUpdateRequest,
)
from .dashboard import DashboardResponse, DashboardStatResponse

__all__ = [
    "RegisterRequest",
    "LoginRequest",
    "UserProfileResponse",
    "AuthResponse",
    "PHCCreate",
    "PHCResponse",
    "HospitalResponse",
    "HospitalRecommendationResponse",
    "ResourceCatalogResponse",
    "HospitalResourceResponse",
    "HospitalResourceUpdate",
    "ResourceQuantityAdjustment",
    "PatientCreate",
    "PatientResponse",
    "ReferralCreateRequest",
    "ReferralResponse",
    "ResourceRequirementItem",
    "ReferralSendRequest",
    "ReferralRejectRequest",
    "AmbulanceCreate",
    "AmbulanceResponse",
    "AmbulanceAssignRequest",
    "LocationUpdateRequest",
    "AmbulanceStatusUpdateRequest",
    "DashboardResponse",
    "DashboardStatResponse",
]
