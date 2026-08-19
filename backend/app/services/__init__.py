from .audit_service import log_audit_event
from .resource_service import (
    get_hospital_resources,
    update_hospital_resource_inventory,
    adjust_resource_quantity,
)
from .recommendation_service import calculate_hospital_recommendations
from .referral_service import (
    create_referral,
    send_referral_to_hospital,
    accept_referral_atomic,
    reject_referral,
    cancel_referral,
)
from .ambulance_service import (
    assign_ambulance_to_referral,
    update_ambulance_status,
    record_ambulance_gps,
)
from .hospital_service import get_all_hospitals_summary

__all__ = [
    "log_audit_event",
    "get_hospital_resources",
    "update_hospital_resource_inventory",
    "adjust_resource_quantity",
    "calculate_hospital_recommendations",
    "create_referral",
    "send_referral_to_hospital",
    "accept_referral_atomic",
    "reject_referral",
    "cancel_referral",
    "assign_ambulance_to_referral",
    "update_ambulance_status",
    "record_ambulance_gps",
    "get_all_hospitals_summary",
]
