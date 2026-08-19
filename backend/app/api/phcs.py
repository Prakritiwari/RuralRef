from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ..database import get_db
from ..models.phc import PHC
from ..models.patient import Patient
from ..models.user import Profile
from ..schemas.phc import PHCResponse, PHCCreate
from ..schemas.patient import PatientResponse, PatientCreate
from ..dependencies import get_current_user, require_roles

router = APIRouter(prefix="", tags=["Primary Health Centres (PHCs)"])

@router.get("/phcs", response_model=List[PHCResponse])
def list_phcs(db: Session = Depends(get_db)):
    return db.query(PHC).filter(PHC.is_active == True).all()

@router.get("/phcs/me", response_model=PHCResponse)
def get_current_phc(
    current_user: Profile = Depends(require_roles("PHC", "ADMIN")),
    db: Session = Depends(get_db)
):
    if current_user.organization_id:
        phc = db.query(PHC).filter(PHC.id == current_user.organization_id).first()
        if phc:
            return phc
    # Fallback to first active PHC
    phc = db.query(PHC).first()
    if not phc:
        raise HTTPException(status_code=404, detail="No PHC configured")
    return phc

@router.get("/phcs/{phc_id}", response_model=PHCResponse)
def get_phc_details(phc_id: str, db: Session = Depends(get_db)):
    phc = db.query(PHC).filter(PHC.id == phc_id).first()
    if not phc:
        raise HTTPException(status_code=404, detail="PHC not found")
    return phc

@router.get("/patients", response_model=List[PatientResponse])
def list_patients(
    current_user: Profile = Depends(require_roles("PHC", "HOSPITAL", "ADMIN")),
    db: Session = Depends(get_db)
):
    # Returns patients registered at current PHC or all for admin
    if current_user.role == "PHC" and current_user.organization_id:
        return db.query(Patient).filter(
            (Patient.phc_id == current_user.organization_id) | (Patient.phc_id == None)
        ).all()
    return db.query(Patient).all()

@router.post("/patients", response_model=PatientResponse, status_code=status.HTTP_201_CREATED)
def create_patient(
    data: PatientCreate,
    current_user: Profile = Depends(require_roles("PHC", "ADMIN")),
    db: Session = Depends(get_db)
):
    phc_id = current_user.organization_id
    if not phc_id:
        default_phc = db.query(PHC).first()
        phc_id = default_phc.id if default_phc else None

    patient = Patient(
        phc_id=phc_id,
        name=data.name,
        age=data.age,
        gender=data.gender,
        phone=data.phone or "",
        blood_group=data.blood_group or "",
        emergency_summary=data.emergency_summary or ""
    )
    db.add(patient)
    db.commit()
    db.refresh(patient)
    return patient
