from typing import Optional
from pydantic import BaseModel, EmailStr, Field, ConfigDict

class RegisterRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=6)
    role: str = Field("PHC", pattern="^(PHC|HOSPITAL|ADMIN|PATIENT|doctor|admin|patient)$")
    phone: str = ""
    organization_id: Optional[str] = None

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class UserProfileResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    auth_user_id: Optional[str] = None
    role: str
    name: str
    email: str
    phone: str
    organization_id: Optional[str] = None
    organization_name: Optional[str] = None

class AuthResponse(BaseModel):
    token: str
    user: UserProfileResponse
    token_type: str = "bearer"
