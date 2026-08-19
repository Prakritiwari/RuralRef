from datetime import datetime, timezone
from typing import Optional, List, Dict
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from ..models.resource import HospitalResource, Resource
from ..models.hospital import Hospital
from ..schemas.resource import HospitalResourceUpdate, ResourceQuantityAdjustment
from .audit_service import log_audit_event

def get_hospital_resources(db: Session, hospital_id: str) -> List[HospitalResource]:
    return db.query(HospitalResource).filter(HospitalResource.hospital_id == hospital_id).all()

def update_hospital_resource_inventory(
    db: Session,
    hospital_id: str,
    resource_id: str,
    update_data: HospitalResourceUpdate,
    actor_user_id: Optional[str] = None
) -> HospitalResource:
    inv = db.query(HospitalResource).filter(
        HospitalResource.hospital_id == hospital_id,
        HospitalResource.resource_id == resource_id
    ).first()

    if not inv:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Resource '{resource_id}' not found in hospital inventory"
        )

    # Validate updates
    new_total = update_data.total_quantity if update_data.total_quantity is not None else inv.total_quantity
    new_available = update_data.available_quantity if update_data.available_quantity is not None else inv.available_quantity
    new_reserved = update_data.reserved_quantity if update_data.reserved_quantity is not None else inv.reserved_quantity

    if new_available < 0 or new_reserved < 0 or new_total < 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Resource quantities cannot be negative"
        )

    if new_available + new_reserved > new_total:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid inventory counts: Available ({new_available}) + Reserved ({new_reserved}) exceeds Total capacity ({new_total})"
        )

    inv.total_quantity = new_total
    inv.available_quantity = new_available
    inv.reserved_quantity = new_reserved

    # Auto compute status if not explicitly given
    if update_data.status:
        inv.status = update_data.status
    else:
        if new_available == 0:
            inv.status = "UNAVAILABLE"
        elif new_available <= 2:
            inv.status = "LIMITED"
        else:
            inv.status = "AVAILABLE"

    inv.updated_at = datetime.now(timezone.utc)
    
    log_audit_event(
        db,
        action="RESOURCE_INVENTORY_UPDATED",
        entity_type="HOSPITAL_RESOURCE",
        entity_id=inv.id,
        actor_user_id=actor_user_id,
        metadata={
            "hospital_id": hospital_id,
            "resource_id": resource_id,
            "total": new_total,
            "available": new_available,
            "reserved": new_reserved,
            "status": inv.status
        }
    )

    db.commit()
    db.refresh(inv)
    return inv

def adjust_resource_quantity(
    db: Session,
    hospital_id: str,
    adjustment: ResourceQuantityAdjustment,
    actor_user_id: Optional[str] = None
) -> HospitalResource:
    inv = db.query(HospitalResource).filter(
        HospitalResource.hospital_id == hospital_id,
        HospitalResource.resource_id == adjustment.resource_id
    ).first()

    if not inv:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Resource '{adjustment.resource_id}' not found in hospital inventory"
        )

    new_available = inv.available_quantity + adjustment.delta_available
    if new_available < 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot reduce available count below 0. Current available: {inv.available_quantity}"
        )
    if new_available + inv.reserved_quantity > inv.total_quantity:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Available count ({new_available}) plus Reserved count ({inv.reserved_quantity}) exceeds Total ({inv.total_quantity})"
        )

    inv.available_quantity = new_available
    if inv.available_quantity == 0:
        inv.status = "UNAVAILABLE"
    elif inv.available_quantity <= 2:
        inv.status = "LIMITED"
    else:
        inv.status = "AVAILABLE"

    inv.updated_at = datetime.now(timezone.utc)

    log_audit_event(
        db,
        action="RESOURCE_QUANTITY_ADJUSTED",
        entity_type="HOSPITAL_RESOURCE",
        entity_id=inv.id,
        actor_user_id=actor_user_id,
        metadata={
            "delta": adjustment.delta_available,
            "new_available": new_available,
            "resource_id": adjustment.resource_id
        }
    )

    db.commit()
    db.refresh(inv)
    return inv
