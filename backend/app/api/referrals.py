from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from ..database import get_db
from ..models.referral import Referral, ReferralResource
from ..models.patient import Patient
from ..models.phc import PHC
from ..models.hospital import Hospital
from ..models.ambulance import Ambulance
from ..models.user import Profile
from ..schemas.referral import (
    ReferralCreateRequest,
    ReferralResponse,
    ReferralResourceRequirementResponse,
    ReferralAmbulanceSummary,
    ReferralSendRequest,
    ReferralRejectRequest,
)
from ..schemas.hospital import HospitalRecommendationResponse
from ..services.referral_service import (
    create_referral,
    send_referral_to_hospital,
    accept_referral_atomic,
    reject_referral,
    cancel_referral,
)
from ..services.ambulance_service import assign_ambulance_to_referral
from ..services.recommendation_service import calculate_hospital_recommendations
from ..dependencies import get_current_user, require_roles

router = APIRouter(prefix="", tags=["Referrals"])

def build_referral_response(ref: Referral, db: Session) -> ReferralResponse:
    patient = db.query(Patient).filter(Patient.id == ref.patient_id).first()
    phc = db.query(PHC).filter(PHC.id == ref.phc_id).first()
    hospital = db.query(Hospital).filter(Hospital.id == ref.hospital_id).first() if ref.hospital_id else None
    
    # Requirements
    reqs = db.query(ReferralResource).filter(ReferralResource.referral_id == ref.id).all()
    req_dtos = [
        ReferralResourceRequirementResponse(
            resource_id=r.resource_id,
            resource_name=r.resource.name if r.resource else r.resource_id,
            quantity=r.quantity,
            is_critical=r.is_critical
        ) for r in reqs
    ]

    # Ambulance
    ambulance_summary = None
    ambulance = db.query(Ambulance).filter(Ambulance.active_referral_id == ref.id).first()
    if ambulance:
        ambulance_summary = ReferralAmbulanceSummary(
            id=ambulance.id,
            vehicle_number=ambulance.vehicle_number,
            driver_name=ambulance.driver_name,
            driver_phone=ambulance.driver_phone,
            status=ambulance.status,
            current_latitude=ambulance.current_latitude,
            current_longitude=ambulance.current_longitude,
            last_location_update=ambulance.last_location_update
        )

    return ReferralResponse(
        id=ref.id,
        referral_number=ref.referral_number,
        patient_id=ref.patient_id,
        patient_name=patient.name if patient else "Unknown Patient",
        patient_age=patient.age if patient else None,
        patient_gender=patient.gender if patient else None,
        phc_id=ref.phc_id,
        phc_name=phc.name if phc else "PHC",
        phc_latitude=phc.latitude if phc else None,
        phc_longitude=phc.longitude if phc else None,
        hospital_id=ref.hospital_id,
        hospital_name=hospital.name if hospital else None,
        hospital_latitude=hospital.latitude if hospital else None,
        hospital_longitude=hospital.longitude if hospital else None,
        urgency=ref.urgency,
        clinical_summary=ref.clinical_summary,
        specialist_needed=ref.specialist_needed or "",
        notes=ref.notes or "",
        status=ref.status,
        created_at=ref.created_at,
        updated_at=ref.updated_at,
        accepted_at=ref.accepted_at,
        rejected_at=ref.rejected_at,
        completed_at=ref.completed_at,
        requirements=req_dtos,
        ambulance=ambulance_summary
    )

@router.post("/referrals", response_model=ReferralResponse, status_code=status.HTTP_201_CREATED)
def create_new_referral(
    data: ReferralCreateRequest,
    current_user: Profile = Depends(require_roles("PHC", "ADMIN")),
    db: Session = Depends(get_db)
):
    phc_id = current_user.organization_id
    if not phc_id:
        default_phc = db.query(PHC).first()
        phc_id = default_phc.id if default_phc else None
    if not phc_id:
        raise HTTPException(status_code=400, detail="No PHC associated with current doctor profile")

    ref = create_referral(
        db=db,
        data=data,
        phc_id=phc_id,
        actor_user_id=current_user.id
    )
    return build_referral_response(ref, db)

@router.get("/referrals", response_model=List[ReferralResponse])
def list_referrals(
    status_filter: Optional[str] = Query(None, alias="status"),
    current_user: Profile = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    query = db.query(Referral)

    # Scoped authorization by role
    if current_user.role == "PHC" and current_user.organization_id:
        query = query.filter(Referral.phc_id == current_user.organization_id)
    elif current_user.role == "HOSPITAL" and current_user.organization_id:
        query = query.filter((Referral.hospital_id == current_user.organization_id) | (Referral.hospital_id == None))
    elif current_user.role == "PATIENT":
        patient_record = db.query(Patient).filter(Patient.phone == current_user.phone).first()
        if patient_record:
            query = query.filter(Referral.patient_id == patient_record.id)

    if status_filter:
        query = query.filter(Referral.status == status_filter.upper())

    referrals = query.order_by(Referral.created_at.desc()).all()
    return [build_referral_response(r, db) for r in referrals]

@router.get("/referrals/{referral_id}", response_model=ReferralResponse)
def get_referral(
    referral_id: str,
    current_user: Profile = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    ref = db.query(Referral).filter(Referral.id == referral_id).first()
    if not ref:
        raise HTTPException(status_code=404, detail="Referral not found")
    return build_referral_response(ref, db)

@router.get("/referrals/{referral_id}/recommendations", response_model=List[HospitalRecommendationResponse])
def get_referral_hospital_recommendations(
    referral_id: str,
    current_user: Profile = Depends(require_roles("PHC", "ADMIN")),
    db: Session = Depends(get_db)
):
    ref = db.query(Referral).filter(Referral.id == referral_id).first()
    if not ref:
        raise HTTPException(status_code=404, detail="Referral not found")

    phc = db.query(PHC).filter(PHC.id == ref.phc_id).first()
    if not phc:
        raise HTTPException(status_code=404, detail="PHC not found for this referral")

    reqs = db.query(ReferralResource).filter(ReferralResource.referral_id == ref.id).all()
    required_resources = [(r.resource_id, r.quantity) for r in reqs]

    return calculate_hospital_recommendations(
        db=db,
        phc_latitude=phc.latitude,
        phc_longitude=phc.longitude,
        required_resources=required_resources,
        specialist_needed=ref.specialist_needed or ""
    )

@router.post("/referrals/{referral_id}/send", response_model=ReferralResponse)
def send_referral(
    referral_id: str,
    hospital_id: Optional[str] = Query(None),
    payload: Optional[ReferralSendRequest] = None,
    current_user: Profile = Depends(require_roles("PHC", "ADMIN")),
    db: Session = Depends(get_db)
):
    target_hospital_id = hospital_id or (payload.hospital_id if payload else None)
    if not target_hospital_id:
        raise HTTPException(status_code=400, detail="Target hospital_id is required")

    ref = send_referral_to_hospital(
        db=db,
        referral_id=referral_id,
        hospital_id=target_hospital_id,
        actor_user_id=current_user.id
    )
    return build_referral_response(ref, db)

@router.post("/referrals/{referral_id}/accept", response_model=ReferralResponse)
def accept_referral(
    referral_id: str,
    current_user: Profile = Depends(require_roles("HOSPITAL", "ADMIN")),
    db: Session = Depends(get_db)
):
    ref = db.query(Referral).filter(Referral.id == referral_id).first()
    if not ref:
        raise HTTPException(status_code=404, detail="Referral not found")

    target_hospital_id = current_user.organization_id or ref.hospital_id
    if not target_hospital_id:
        raise HTTPException(status_code=400, detail="No hospital associated with current user or referral")

    # Enforce authorization
    if current_user.role == "HOSPITAL" and current_user.organization_id and ref.hospital_id and ref.hospital_id != current_user.organization_id:
        raise HTTPException(status_code=403, detail="Cannot accept referral directed to another hospital")

    updated_ref = accept_referral_atomic(
        db=db,
        referral_id=referral_id,
        hospital_id=target_hospital_id,
        actor_user_id=current_user.id
    )
    return build_referral_response(updated_ref, db)

@router.post("/referrals/{referral_id}/reject", response_model=ReferralResponse)
def reject_referral_endpoint(
    referral_id: str,
    payload: Optional[ReferralRejectRequest] = None,
    current_user: Profile = Depends(require_roles("HOSPITAL", "ADMIN")),
    db: Session = Depends(get_db)
):
    ref = db.query(Referral).filter(Referral.id == referral_id).first()
    if not ref:
        raise HTTPException(status_code=404, detail="Referral not found")

    target_hospital_id = current_user.organization_id or ref.hospital_id or "UNKNOWN"
    reason = payload.reason if payload else "Insufficient capacity"

    updated_ref = reject_referral(
        db=db,
        referral_id=referral_id,
        hospital_id=target_hospital_id,
        reason=reason,
        actor_user_id=current_user.id
    )
    return build_referral_response(updated_ref, db)

@router.post("/referrals/{referral_id}/cancel", response_model=ReferralResponse)
def cancel_referral_endpoint(
    referral_id: str,
    current_user: Profile = Depends(require_roles("PHC", "ADMIN")),
    db: Session = Depends(get_db)
):
    updated_ref = cancel_referral(
        db=db,
        referral_id=referral_id,
        actor_user_id=current_user.id
    )
    return build_referral_response(updated_ref, db)

@router.post("/referrals/{referral_id}/ambulance", response_model=ReferralResponse)
def allocate_ambulance_to_referral_endpoint(
    referral_id: str,
    current_user: Profile = Depends(require_roles("HOSPITAL", "ADMIN")),
    db: Session = Depends(get_db)
):
    """
    Allocates the first available ambulance from the accepting hospital.
    """
    ref = db.query(Referral).filter(Referral.id == referral_id).first()
    if not ref:
        raise HTTPException(status_code=404, detail="Referral not found")
    if ref.status != "ACCEPTED":
        raise HTTPException(status_code=400, detail="Referral must be in ACCEPTED status first")

    # Find available ambulance
    hospital_id = ref.hospital_id or current_user.organization_id
    ambulance = db.query(Ambulance).filter(
        Ambulance.hospital_id == hospital_id,
        Ambulance.status == "AVAILABLE",
        Ambulance.is_active == True
    ).first()

    if not ambulance:
        raise HTTPException(status_code=409, detail="No available ambulance on station for this hospital")

    assign_ambulance_to_referral(
        db=db,
        ambulance_id=ambulance.id,
        referral_id=ref.id,
        actor_user_id=current_user.id
    )
    db.refresh(ref)
    return build_referral_response(ref, db)
