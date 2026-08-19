from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ..database import get_db
from ..models.user import Profile
from ..models.phc import PHC
from ..models.hospital import Hospital
from ..schemas.auth import RegisterRequest, LoginRequest, AuthResponse, UserProfileResponse
from ..utils.security import hash_password, verify_password, create_access_token
from ..dependencies import get_current_user

router = APIRouter(prefix="", tags=["Authentication"])

def build_profile_response(profile: Profile, db: Session) -> UserProfileResponse:
    org_name = None
    if profile.organization_id:
        if profile.role in ("PHC", "doctor"):
            phc = db.query(PHC).filter(PHC.id == profile.organization_id).first()
            if phc:
                org_name = phc.name
        elif profile.role in ("HOSPITAL", "admin"):
            hosp = db.query(Hospital).filter(Hospital.id == profile.organization_id).first()
            if hosp:
                org_name = hosp.name

    return UserProfileResponse(
        id=profile.id,
        auth_user_id=profile.auth_user_id,
        role=profile.role,
        name=profile.name,
        email=profile.email,
        phone=profile.phone or "",
        organization_id=profile.organization_id,
        organization_name=org_name
    )

@router.post("/auth/register", response_model=AuthResponse)
def register_user(data: RegisterRequest, db: Session = Depends(get_db)):
    # Check if email exists
    existing = db.query(Profile).filter(Profile.email == data.email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A user with this email address is already registered."
        )

    # Normalize role
    normalized_role = data.role.upper()
    if normalized_role in ("DOCTOR", "PHC"):
        normalized_role = "PHC"
        # Auto-link to default demo PHC if not given
        if not data.organization_id:
            phc = db.query(PHC).first()
            if phc:
                data.organization_id = phc.id
    elif normalized_role in ("HOSPITAL", "ADMIN"):
        normalized_role = "HOSPITAL" if data.role.lower() == "hospital" else "ADMIN"
        if not data.organization_id:
            hosp = db.query(Hospital).first()
            if hosp:
                data.organization_id = hosp.id

    profile = Profile(
        name=data.name,
        email=data.email,
        password_hash=hash_password(data.password),
        role=normalized_role,
        phone=data.phone,
        organization_id=data.organization_id
    )
    db.add(profile)
    db.commit()
    db.refresh(profile)

    token = create_access_token({"sub": profile.id, "role": profile.role})
    return AuthResponse(
        token=token,
        user=build_profile_response(profile, db)
    )

@router.post("/auth/login", response_model=AuthResponse)
def login_user(data: LoginRequest, db: Session = Depends(get_db)):
    profile = db.query(Profile).filter(Profile.email == data.email).first()
    if not profile or not verify_password(data.password, profile.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password. Please verify your credentials."
        )

    token = create_access_token({"sub": profile.id, "role": profile.role})
    return AuthResponse(
        token=token,
        user=build_profile_response(profile, db)
    )

@router.get("/auth/me", response_model=UserProfileResponse)
@router.get("/me", response_model=UserProfileResponse)
def get_authenticated_user_profile(
    current_user: Profile = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return build_profile_response(current_user, db)
