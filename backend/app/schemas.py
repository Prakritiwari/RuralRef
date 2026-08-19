from typing import Optional
from pydantic import BaseModel, EmailStr, Field

class RegisterIn(BaseModel):
    name: str
    email: EmailStr
    password: str = Field(min_length=6)
    role: str
    phone: str = ""

class LoginIn(BaseModel):
    email: EmailStr
    password: str

class ReferralIn(BaseModel):
    patient_id: int
    symptoms: str = ""
    urgency: str = "medium"
    needs_icu: bool = False
    needs_oxygen: bool = False
    needs_ventilator: bool = False
    specialist_needed: str = ""
    notes: str = ""

class ResourceUpdate(BaseModel):
    icu_available: int
    oxygen_available: int
    ventilators_available: int

class AmbulanceLocation(BaseModel):
    latitude: float
    longitude: float
