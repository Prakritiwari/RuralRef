from typing import List, Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from .database import get_db
from .models.user import Profile
from .utils.security import decode_token

security = HTTPBearer(auto_error=False)

def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db)
) -> Profile:
    if not credentials or not credentials.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication token is missing or malformed",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    token = credentials.credentials
    try:
        payload = decode_token(token)
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token payload is missing subject",
            )
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired authentication token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Query profile
    profile = db.query(Profile).filter((Profile.id == user_id) | (Profile.auth_user_id == user_id)).first()
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User profile not found",
        )
    return profile

def require_roles(*allowed_roles: str):
    """
    Role-based authorization dependency factory.
    Normalizes roles to uppercase (e.g. 'doctor' -> 'PHC', 'admin' -> 'ADMIN').
    """
    normalized_allowed = []
    for r in allowed_roles:
        r_upper = r.upper()
        if r_upper == "DOCTOR":
            normalized_allowed.extend(["PHC", "DOCTOR"])
        elif r_upper == "HOSPITAL":
            normalized_allowed.extend(["HOSPITAL", "ADMIN"])
        else:
            normalized_allowed.append(r_upper)
            
    def role_checker(current_user: Profile = Depends(get_current_user)) -> Profile:
        user_role = current_user.role.upper()
        if user_role not in normalized_allowed and "ADMIN" not in normalized_allowed and user_role != "ADMIN":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied: role '{current_user.role}' is not authorized for this action. Required: {list(set(normalized_allowed))}",
            )
        return current_user
    return role_checker
