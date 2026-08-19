from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ..database import get_db
from ..models.ambulance import Ambulance, AmbulanceLocation
from ..models.hospital import Hospital
from ..models.referral import Referral
from ..models.user import Profile
from ..schemas.ambulance import (
    AmbulanceResponse,
    AmbulanceCreate,
    AmbulanceAssignRequest,
    LocationUpdateRequest,
    AmbulanceStatusUpdateRequest,
)
from ..services.ambulance_service import (
    assign_ambulance_to_referral,
    update_ambulance_status,
    record_ambulance_gps,
)
from ..dependencies import get_current_user, require_roles

router = APIRouter(prefix="", tags=["Ambulance Fleet & Coordination"])

def build_ambulance_response(a: Ambulance, db: Session) -> AmbulanceResponse:
    hospital = db.query(Hospital).filter(Hospital.id == a.hospital_id).first()
    return AmbulanceResponse(
        id=a.id,
        hospital_id=a.hospital_id,
        hospital_name=hospital.name if hospital else "Hospital",
        vehicle_number=a.vehicle_number,
        driver_name=a.driver_name,
        driver_phone=a.driver_phone,
        ambulance_type=a.ambulance_type,
        status=a.status,
        current_latitude=a.current_latitude,
        current_longitude=a.current_longitude,
        active_referral_id=a.active_referral_id,
        last_location_update=a.last_location_update,
        is_active=a.is_active
    )

@router.get("/ambulances", response_model=List[AmbulanceResponse])
def list_ambulances(
    status_filter: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(Ambulance).filter(Ambulance.is_active == True)
    if status_filter:
        query = query.filter(Ambulance.status == status_filter.upper())
    ambulances = query.all()
    return [build_ambulance_response(a, db) for a in ambulances]

@router.post("/ambulances", response_model=AmbulanceResponse, status_code=status.HTTP_201_CREATED)
def create_ambulance(
    data: AmbulanceCreate,
    current_user: Profile = Depends(require_roles("HOSPITAL", "ADMIN")),
    db: Session = Depends(get_db)
):
    hospital_id = data.hospital_id
    if current_user.role == "HOSPITAL" and current_user.organization_id:
        hospital_id = current_user.organization_id

    ambulance = Ambulance(
        hospital_id=hospital_id,
        vehicle_number=data.vehicle_number,
        driver_name=data.driver_name,
        driver_phone=data.driver_phone,
        ambulance_type=data.ambulance_type,
        status="AVAILABLE",
        current_latitude=data.initial_latitude,
        current_longitude=data.initial_longitude
    )
    db.add(ambulance)
    db.commit()
    db.refresh(ambulance)
    return build_ambulance_response(ambulance, db)

@router.get("/ambulances/{ambulance_id}", response_model=AmbulanceResponse)
def get_ambulance(ambulance_id: str, db: Session = Depends(get_db)):
    a = db.query(Ambulance).filter(Ambulance.id == ambulance_id).first()
    if not a:
        raise HTTPException(status_code=404, detail="Ambulance not found")
    return build_ambulance_response(a, db)

@router.post("/ambulances/{ambulance_id}/assign", response_model=AmbulanceResponse)
def assign_ambulance_endpoint(
    ambulance_id: str,
    data: AmbulanceAssignRequest,
    current_user: Profile = Depends(require_roles("HOSPITAL", "ADMIN")),
    db: Session = Depends(get_db)
):
    amb = assign_ambulance_to_referral(
        db=db,
        ambulance_id=ambulance_id,
        referral_id=data.referral_id,
        actor_user_id=current_user.id
    )
    return build_ambulance_response(amb, db)

@router.patch("/ambulances/{ambulance_id}/status", response_model=AmbulanceResponse)
def update_status_endpoint(
    ambulance_id: str,
    data: AmbulanceStatusUpdateRequest,
    current_user: Profile = Depends(require_roles("HOSPITAL", "PHC", "ADMIN")),
    db: Session = Depends(get_db)
):
    amb = update_ambulance_status(
        db=db,
        ambulance_id=ambulance_id,
        new_status=data.status,
        actor_user_id=current_user.id
    )
    return build_ambulance_response(amb, db)

@router.post("/ambulances/{ambulance_id}/location", response_model=dict)
@router.patch("/ambulances/{ambulance_id}/location", response_model=dict)
def update_ambulance_location(
    ambulance_id: str,
    data: LocationUpdateRequest,
    db: Session = Depends(get_db)
):
    record = record_ambulance_gps(
        db=db,
        ambulance_id=ambulance_id,
        telemetry=data
    )
    return {
        "status": "success",
        "ambulance_id": ambulance_id,
        "latitude": record.latitude,
        "longitude": record.longitude,
        "timestamp": record.timestamp.isoformat()
    }

@router.post("/ambulances/{ambulance_id}/complete", response_model=dict)
def complete_trip(
    ambulance_id: str,
    current_user: Profile = Depends(require_roles("HOSPITAL", "ADMIN")),
    db: Session = Depends(get_db)
):
    amb = update_ambulance_status(
        db=db,
        ambulance_id=ambulance_id,
        new_status="AVAILABLE",
        actor_user_id=current_user.id
    )
    return {"message": "Ambulance trip completed and vehicle returned to available fleet"}
