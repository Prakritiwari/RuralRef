from datetime import datetime, timezone
from typing import List, Optional
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from ..models.ambulance import Ambulance, AmbulanceLocation
from ..models.referral import Referral
from ..models.hospital import Hospital
from ..schemas.ambulance import AmbulanceCreate, LocationUpdateRequest
from .audit_service import log_audit_event

VALID_AMBULANCE_TRANSITIONS = {
    "AVAILABLE": ["ASSIGNED", "OFFLINE"],
    "ASSIGNED": ["EN_ROUTE_TO_PHC", "AVAILABLE", "OFFLINE"],
    "EN_ROUTE_TO_PHC": ["PATIENT_PICKED_UP", "AVAILABLE", "OFFLINE"],
    "PATIENT_PICKED_UP": ["TRANSPORTING", "AVAILABLE"],
    "TRANSPORTING": ["ARRIVED"],
    "ARRIVED": ["AVAILABLE"],
    "OFFLINE": ["AVAILABLE"]
}

def assign_ambulance_to_referral(
    db: Session,
    ambulance_id: str,
    referral_id: str,
    actor_user_id: Optional[str] = None
) -> Ambulance:
    ambulance = db.query(Ambulance).filter(Ambulance.id == ambulance_id).first()
    if not ambulance:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ambulance not found"
        )
    if ambulance.status != "AVAILABLE":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Ambulance '{ambulance.vehicle_number}' is not available (current status: {ambulance.status})"
        )

    referral = db.query(Referral).filter(Referral.id == referral_id).first()
    if not referral:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Referral not found"
        )
    if referral.status not in ("ACCEPTED", "AMBULANCE_ASSIGNED"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Referral must be in ACCEPTED status before dispatching an ambulance (current: {referral.status})"
        )

    if referral.hospital_id and referral.hospital_id != ambulance.hospital_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Ambulance does not belong to the hospital handling this referral"
        )

    # Assign
    ambulance.status = "ASSIGNED"
    ambulance.active_referral_id = referral.id
    ambulance.updated_at = datetime.now(timezone.utc)

    referral.status = "AMBULANCE_ASSIGNED"
    referral.updated_at = datetime.now(timezone.utc)

    log_audit_event(
        db,
        action="AMBULANCE_ASSIGNED",
        entity_type="AMBULANCE",
        entity_id=ambulance.id,
        actor_user_id=actor_user_id,
        metadata={
            "vehicle_number": ambulance.vehicle_number,
            "referral_id": referral.id,
            "referral_number": referral.referral_number
        }
    )

    db.commit()
    db.refresh(ambulance)
    return ambulance

def update_ambulance_status(
    db: Session,
    ambulance_id: str,
    new_status: str,
    actor_user_id: Optional[str] = None
) -> Ambulance:
    ambulance = db.query(Ambulance).filter(Ambulance.id == ambulance_id).first()
    if not ambulance:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ambulance not found"
        )

    current_status = ambulance.status
    allowed_transitions = VALID_AMBULANCE_TRANSITIONS.get(current_status, [])
    
    if new_status not in allowed_transitions and new_status != current_status:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid ambulance status transition from '{current_status}' to '{new_status}'. Allowed: {allowed_transitions}"
        )

    ambulance.status = new_status
    ambulance.updated_at = datetime.now(timezone.utc)

    # Sync referral status if active
    if ambulance.active_referral_id:
        referral = db.query(Referral).filter(Referral.id == ambulance.active_referral_id).first()
        if referral:
            if new_status == "EN_ROUTE_TO_PHC":
                referral.status = "AMBULANCE_EN_ROUTE"
            elif new_status == "PATIENT_PICKED_UP":
                referral.status = "PATIENT_PICKED_UP"
            elif new_status == "TRANSPORTING":
                referral.status = "PATIENT_IN_TRANSIT"
            elif new_status == "ARRIVED":
                referral.status = "ARRIVED"
            elif new_status == "AVAILABLE":
                # Trip complete, mark referral COMPLETED
                referral.status = "COMPLETED"
                referral.completed_at = datetime.now(timezone.utc)
                ambulance.active_referral_id = None
            referral.updated_at = datetime.now(timezone.utc)

    log_audit_event(
        db,
        action="AMBULANCE_STATUS_UPDATED",
        entity_type="AMBULANCE",
        entity_id=ambulance.id,
        actor_user_id=actor_user_id,
        metadata={
            "previous_status": current_status,
            "new_status": new_status,
            "referral_id": ambulance.active_referral_id
        }
    )

    db.commit()
    db.refresh(ambulance)
    return ambulance

def record_ambulance_gps(
    db: Session,
    ambulance_id: str,
    telemetry: LocationUpdateRequest,
    actor_user_id: Optional[str] = None
) -> AmbulanceLocation:
    ambulance = db.query(Ambulance).filter(Ambulance.id == ambulance_id).first()
    if not ambulance:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ambulance not found"
        )

    # Update current position
    ambulance.current_latitude = telemetry.latitude
    ambulance.current_longitude = telemetry.longitude
    ambulance.last_location_update = datetime.now(timezone.utc)
    ambulance.updated_at = datetime.now(timezone.utc)

    # Record trail
    location_entry = AmbulanceLocation(
        ambulance_id=ambulance.id,
        referral_id=ambulance.active_referral_id,
        latitude=telemetry.latitude,
        longitude=telemetry.longitude,
        speed=telemetry.speed or 0.0,
        heading=telemetry.heading or 0.0,
        accuracy=telemetry.accuracy or 5.0,
        timestamp=telemetry.timestamp or datetime.now(timezone.utc)
    )
    db.add(location_entry)
    db.commit()
    db.refresh(location_entry)
    return location_entry
