import random
from datetime import datetime, timezone
from typing import List, Optional, Tuple
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from ..models.referral import Referral, ReferralResource
from ..models.resource import HospitalResource, Resource
from ..models.hospital import Hospital
from ..models.patient import Patient
from ..models.phc import PHC
from ..models.ambulance import Ambulance
from ..schemas.referral import ReferralCreateRequest, ResourceRequirementItem
from .audit_service import log_audit_event

VALID_STATUS_TRANSITIONS = {
    "PENDING": ["ACCEPTED", "REJECTED", "CANCELLED"],
    "ACCEPTED": ["AMBULANCE_ASSIGNED", "CANCELLED"],
    "AMBULANCE_ASSIGNED": ["AMBULANCE_EN_ROUTE", "CANCELLED"],
    "AMBULANCE_EN_ROUTE": ["PATIENT_PICKED_UP", "CANCELLED"],
    "PATIENT_PICKED_UP": ["PATIENT_IN_TRANSIT"],
    "PATIENT_IN_TRANSIT": ["ARRIVED"],
    "ARRIVED": ["COMPLETED"],
    "REJECTED": [],
    "COMPLETED": [],
    "CANCELLED": []
}

def generate_referral_number() -> str:
    year = datetime.now().year
    rand_num = random.randint(1000, 9999)
    return f"REF-{year}-{rand_num}"

def create_referral(
    db: Session,
    data: ReferralCreateRequest,
    phc_id: str,
    actor_user_id: Optional[str] = None
) -> Referral:
    # 1. Verify Patient exists
    patient = db.query(Patient).filter(Patient.id == data.patient_id).first()
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Patient with ID '{data.patient_id}' does not exist"
        )

    # 2. Verify PHC exists
    phc = db.query(PHC).filter(PHC.id == phc_id).first()
    if not phc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"PHC with ID '{phc_id}' not found"
        )

    referral_no = generate_referral_number()
    while db.query(Referral).filter(Referral.referral_number == referral_no).first():
        referral_no = generate_referral_number()

    # Create Referral
    referral = Referral(
        referral_number=referral_no,
        patient_id=data.patient_id,
        phc_id=phc_id,
        urgency=data.urgency.upper(),
        clinical_summary=data.clinical_summary,
        specialist_needed=data.specialist_needed or "",
        notes=data.notes or "",
        status="PENDING"
    )
    db.add(referral)
    db.flush()  # populate referral.id

    # 3. Add Resource Requirements
    requirements = list(data.required_resources)
    
    # Check backward compatibility booleans
    existing_res_ids = {r.resource_id for r in requirements}
    if data.needs_icu and "ICU" not in existing_res_ids:
        requirements.append(ResourceRequirementItem(resource_id="ICU", quantity=1))
    if data.needs_ventilator and "VENTILATOR" not in existing_res_ids:
        requirements.append(ResourceRequirementItem(resource_id="VENTILATOR", quantity=1))
    if data.needs_oxygen and "OXYGEN" not in existing_res_ids:
        requirements.append(ResourceRequirementItem(resource_id="OXYGEN", quantity=1))

    for req in requirements:
        ref_res = ReferralResource(
            referral_id=referral.id,
            resource_id=req.resource_id,
            quantity=req.quantity,
            is_critical=req.is_critical
        )
        db.add(ref_res)

    log_audit_event(
        db,
        action="REFERRAL_CREATED",
        entity_type="REFERRAL",
        entity_id=referral.id,
        actor_user_id=actor_user_id,
        metadata={
            "referral_number": referral.referral_number,
            "patient_id": patient.id,
            "patient_name": patient.name,
            "phc_id": phc.id,
            "urgency": referral.urgency,
            "requirements": [{"resource_id": r.resource_id, "quantity": r.quantity} for r in requirements]
        }
    )

    db.commit()
    db.refresh(referral)
    return referral

def send_referral_to_hospital(
    db: Session,
    referral_id: str,
    hospital_id: str,
    actor_user_id: Optional[str] = None
) -> Referral:
    referral = db.query(Referral).filter(Referral.id == referral_id).first()
    if not referral:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Referral not found"
        )
    if referral.status != "PENDING":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot send referral in status '{referral.status}'"
        )

    hospital = db.query(Hospital).filter(Hospital.id == hospital_id, Hospital.is_active == True).first()
    if not hospital:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Target hospital not found or inactive"
        )

    referral.hospital_id = hospital_id
    referral.updated_at = datetime.now(timezone.utc)

    log_audit_event(
        db,
        action="REFERRAL_DISPATCHED",
        entity_type="REFERRAL",
        entity_id=referral.id,
        actor_user_id=actor_user_id,
        metadata={
            "hospital_id": hospital_id,
            "hospital_name": hospital.name
        }
    )

    db.commit()
    db.refresh(referral)
    return referral

def accept_referral_atomic(
    db: Session,
    referral_id: str,
    hospital_id: str,
    actor_user_id: Optional[str] = None
) -> Referral:
    """
    Critically executes an atomic reservation of hospital resources.
    Uses row-level locking (with_for_update) to guarantee no two PHCs can overbook
    the same capacity concurrently.
    """
    # 1. Lock the referral row
    referral = db.query(Referral).with_for_update().filter(Referral.id == referral_id).first()
    if not referral:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Referral not found"
        )

    if referral.status != "PENDING":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Referral has already transitioned to '{referral.status}' and cannot be accepted again"
        )

    # 2. Lock required hospital resource rows
    requirements = db.query(ReferralResource).filter(ReferralResource.referral_id == referral.id).all()
    
    # If hospital was not attached yet, attach it now
    referral.hospital_id = hospital_id

    # Verify every critical required resource is strictly available
    insufficient_items = []
    locked_inventories: List[HospitalResource] = []

    for req in requirements:
        inv = db.query(HospitalResource).with_for_update().filter(
            HospitalResource.hospital_id == hospital_id,
            HospitalResource.resource_id == req.resource_id
        ).first()

        if not inv or inv.available_quantity < req.quantity:
            avail = inv.available_quantity if inv else 0
            insufficient_items.append(f"{req.resource_id} (needed {req.quantity}, available {avail})")
        else:
            locked_inventories.append((inv, req.quantity))

    if insufficient_items:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Cannot accept referral: The following resources are no longer available at this hospital: {', '.join(insufficient_items)}"
        )

    # 3. Atomically reserve resources
    for inv, qty in locked_inventories:
        inv.available_quantity -= qty
        inv.reserved_quantity += qty
        if inv.available_quantity == 0:
            inv.status = "UNAVAILABLE"
        elif inv.available_quantity <= 2:
            inv.status = "LIMITED"
        else:
            inv.status = "AVAILABLE"
        inv.updated_at = datetime.now(timezone.utc)

    # 4. Update referral status
    referral.status = "ACCEPTED"
    referral.accepted_at = datetime.now(timezone.utc)
    referral.updated_at = datetime.now(timezone.utc)

    log_audit_event(
        db,
        action="REFERRAL_ACCEPTED_AND_RESOURCES_RESERVED",
        entity_type="REFERRAL",
        entity_id=referral.id,
        actor_user_id=actor_user_id,
        metadata={
            "hospital_id": hospital_id,
            "reserved_items": [{"resource_id": inv.resource_id, "quantity": qty} for inv, qty in locked_inventories]
        }
    )

    db.commit()
    db.refresh(referral)
    return referral

def reject_referral(
    db: Session,
    referral_id: str,
    hospital_id: str,
    reason: str = "Insufficient capacity",
    actor_user_id: Optional[str] = None
) -> Referral:
    referral = db.query(Referral).filter(Referral.id == referral_id).first()
    if not referral:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Referral not found"
        )
    if referral.status != "PENDING":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot reject referral currently in status '{referral.status}'"
        )

    referral.status = "REJECTED"
    referral.rejected_at = datetime.now(timezone.utc)
    referral.updated_at = datetime.now(timezone.utc)
    referral.notes = (referral.notes or "") + f"\n[Rejection reason: {reason}]"

    log_audit_event(
        db,
        action="REFERRAL_REJECTED",
        entity_type="REFERRAL",
        entity_id=referral.id,
        actor_user_id=actor_user_id,
        metadata={
            "hospital_id": hospital_id,
            "reason": reason
        }
    )

    db.commit()
    db.refresh(referral)
    return referral

def cancel_referral(
    db: Session,
    referral_id: str,
    reason: str = "Referral cancelled by PHC",
    actor_user_id: Optional[str] = None
) -> Referral:
    referral = db.query(Referral).with_for_update().filter(Referral.id == referral_id).first()
    if not referral:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Referral not found"
        )
    
    if referral.status in ("COMPLETED", "CANCELLED", "REJECTED"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Referral already in terminal status '{referral.status}'"
        )

    # If resources were previously reserved (e.g. status was ACCEPTED or AMBULANCE_ASSIGNED), release them!
    if referral.status in ("ACCEPTED", "AMBULANCE_ASSIGNED", "AMBULANCE_EN_ROUTE") and referral.hospital_id:
        reqs = db.query(ReferralResource).filter(ReferralResource.referral_id == referral.id).all()
        for req in reqs:
            inv = db.query(HospitalResource).with_for_update().filter(
                HospitalResource.hospital_id == referral.hospital_id,
                HospitalResource.resource_id == req.resource_id
            ).first()
            if inv:
                qty_to_release = min(inv.reserved_quantity, req.quantity)
                inv.reserved_quantity -= qty_to_release
                inv.available_quantity += qty_to_release
                if inv.available_quantity > 2:
                    inv.status = "AVAILABLE"
                elif inv.available_quantity > 0:
                    inv.status = "LIMITED"
                inv.updated_at = datetime.now(timezone.utc)

    # Release any assigned ambulance
    ambulance = db.query(Ambulance).filter(Ambulance.active_referral_id == referral.id).first()
    if ambulance:
        ambulance.active_referral_id = None
        ambulance.status = "AVAILABLE"
        ambulance.updated_at = datetime.now(timezone.utc)

    referral.status = "CANCELLED"
    referral.updated_at = datetime.now(timezone.utc)

    log_audit_event(
        db,
        action="REFERRAL_CANCELLED",
        entity_type="REFERRAL",
        entity_id=referral.id,
        actor_user_id=actor_user_id,
        metadata={"reason": reason}
    )

    db.commit()
    db.refresh(referral)
    return referral
