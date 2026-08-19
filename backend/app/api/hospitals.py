from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from ..database import get_db
from ..models.hospital import Hospital
from ..models.user import Profile
from ..schemas.hospital import HospitalResponse, HospitalRecommendationResponse
from ..schemas.resource import HospitalResourceResponse, HospitalResourceUpdate, ResourceQuantityAdjustment
from ..services.hospital_service import get_all_hospitals_summary
from ..services.resource_service import (
    get_hospital_resources,
    update_hospital_resource_inventory,
    adjust_resource_quantity,
)
from ..services.recommendation_service import calculate_hospital_recommendations
from ..dependencies import get_current_user, require_roles

router = APIRouter(prefix="", tags=["Hospitals & Inventory"])

@router.get("/hospitals", response_model=List[HospitalResponse])
def list_hospitals(db: Session = Depends(get_db)):
    return get_all_hospitals_summary(db)

@router.get("/hospitals/{hospital_id}", response_model=HospitalResponse)
def get_hospital_by_id(hospital_id: str, db: Session = Depends(get_db)):
    all_h = get_all_hospitals_summary(db)
    hosp = next((h for h in all_h if h.id == hospital_id), None)
    if not hosp:
        raise HTTPException(status_code=404, detail="Hospital not found")
    return hosp

@router.get("/hospitals/{hospital_id}/resources", response_model=List[HospitalResourceResponse])
def get_hospital_inventory(hospital_id: str, db: Session = Depends(get_db)):
    all_h = get_all_hospitals_summary(db)
    hosp = next((h for h in all_h if h.id == hospital_id), None)
    if not hosp:
        raise HTTPException(status_code=404, detail="Hospital not found")
    return hosp.resources

@router.patch("/hospitals/{hospital_id}/resources/{resource_id}", response_model=HospitalResourceResponse)
def update_specific_resource(
    hospital_id: str,
    resource_id: str,
    update_data: HospitalResourceUpdate,
    current_user: Profile = Depends(require_roles("HOSPITAL", "ADMIN")),
    db: Session = Depends(get_db)
):
    # Enforce that hospital staff can only edit their own hospital unless admin
    if current_user.role == "HOSPITAL" and current_user.organization_id and current_user.organization_id != hospital_id:
        raise HTTPException(status_code=403, detail="You are not authorized to manage inventory for another hospital")

    inv = update_hospital_resource_inventory(
        db=db,
        hospital_id=hospital_id,
        resource_id=resource_id,
        update_data=update_data,
        actor_user_id=current_user.id
    )
    return HospitalResourceResponse.from_orm(inv)

@router.patch("/hospitals/{hospital_id}/resources", response_model=dict)
def update_resources_bulk(
    hospital_id: str,
    data: dict,
    current_user: Profile = Depends(require_roles("HOSPITAL", "ADMIN")),
    db: Session = Depends(get_db)
):
    """
    Backward compatibility endpoint for legacy UI sending icu_available, oxygen_available, ventilators_available
    """
    if "icu_available" in data:
        update_hospital_resource_inventory(
            db, hospital_id, "ICU",
            HospitalResourceUpdate(available_quantity=data["icu_available"]),
            current_user.id
        )
    if "oxygen_available" in data:
        update_hospital_resource_inventory(
            db, hospital_id, "OXYGEN",
            HospitalResourceUpdate(available_quantity=data["oxygen_available"]),
            current_user.id
        )
    if "ventilators_available" in data:
        update_hospital_resource_inventory(
            db, hospital_id, "VENTILATOR",
            HospitalResourceUpdate(available_quantity=data["ventilators_available"]),
            current_user.id
        )
    return {"message": "Hospital inventory updated successfully"}

@router.post("/hospitals/{hospital_id}/resources/adjust", response_model=HospitalResourceResponse)
def adjust_resource_count(
    hospital_id: str,
    adjustment: ResourceQuantityAdjustment,
    current_user: Profile = Depends(require_roles("HOSPITAL", "ADMIN")),
    db: Session = Depends(get_db)
):
    if current_user.role == "HOSPITAL" and current_user.organization_id and current_user.organization_id != hospital_id:
        raise HTTPException(status_code=403, detail="Unauthorized")

    inv = adjust_resource_quantity(
        db=db,
        hospital_id=hospital_id,
        adjustment=adjustment,
        actor_user_id=current_user.id
    )
    return HospitalResourceResponse.from_orm(inv)
