from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..database import get_db
from ..models.patient import Patient
from ..models.referral import Referral
from ..models.ambulance import Ambulance
from ..models.hospital import Hospital
from ..models.resource import HospitalResource
from ..models.user import Profile
from ..schemas.dashboard import DashboardResponse, DashboardStatResponse, DashboardResourceSummary
from .referrals import build_referral_response
from ..dependencies import get_current_user

router = APIRouter(prefix="", tags=["Operations Dashboard"])

@router.get("/dashboard", response_model=DashboardResponse)
def get_command_center_dashboard(
    current_user: Profile = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Counts
    patients_count = db.query(Patient).count()
    pending_referrals_count = db.query(Referral).filter(Referral.status == "PENDING").count()
    active_transfers_count = db.query(Referral).filter(
        Referral.status.in_(["AMBULANCE_ASSIGNED", "AMBULANCE_EN_ROUTE", "PATIENT_PICKED_UP", "PATIENT_IN_TRANSIT"])
    ).count()
    available_ambulances_count = db.query(Ambulance).filter(
        Ambulance.status == "AVAILABLE",
        Ambulance.is_active == True
    ).count()
    total_hospitals_count = db.query(Hospital).filter(Hospital.is_active == True).count()

    # Recent referrals
    ref_query = db.query(Referral)
    if current_user.role == "PHC" and current_user.organization_id:
        ref_query = ref_query.filter(Referral.phc_id == current_user.organization_id)
    elif current_user.role == "HOSPITAL" and current_user.organization_id:
        ref_query = ref_query.filter(
            (Referral.hospital_id == current_user.organization_id) | (Referral.hospital_id == None)
        )
    
    recent_refs = ref_query.order_by(Referral.created_at.desc()).limit(10).all()
    recent_ref_dtos = [build_referral_response(r, db) for r in recent_refs]

    # Hospital capacities
    hospitals = db.query(Hospital).filter(Hospital.is_active == True).all()
    capacities: List[DashboardResourceSummary] = []
    legacy_resources: List[dict] = []

    for h in hospitals:
        invs = db.query(HospitalResource).filter(HospitalResource.hospital_id == h.id).all()
        inv_map = {item.resource_id: item.available_quantity for item in invs}

        icu_avail = inv_map.get("ICU", 0)
        oxygen_avail = inv_map.get("OXYGEN", 0)
        vent_avail = inv_map.get("VENTILATOR", 0)
        blood_avail = inv_map.get("BLOOD_O_POS", 0)

        capacities.append(
            DashboardResourceSummary(
                hospital_id=h.id,
                hospital_name=h.name,
                district=h.district,
                icu_available=icu_avail,
                oxygen_available=oxygen_avail,
                ventilators_available=vent_avail,
                blood_o_pos_available=blood_avail
            )
        )

        legacy_resources.append({
            "hospital": h.name,
            "district": h.district,
            "icu": icu_avail,
            "oxygen": oxygen_avail,
            "ventilators": vent_avail
        })

    stats_dto = DashboardStatResponse(
        patients_count=patients_count,
        pending_referrals_count=pending_referrals_count,
        active_transfers_count=active_transfers_count,
        available_ambulances_count=available_ambulances_count,
        total_hospitals_count=total_hospitals_count
    )

    return DashboardResponse(
        stats=stats_dto,
        recent_referrals=recent_ref_dtos,
        hospital_capacities=capacities,
        patients=patients_count,
        pending_referrals=pending_referrals_count,
        active_transfers=active_transfers_count,
        available_ambulances=available_ambulances_count,
        resources=legacy_resources
    )
