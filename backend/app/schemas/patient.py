from typing import Optional
from pydantic import BaseModel, Field, ConfigDict

class PatientCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    age: int = Field(..., ge=0, le=130)
    gender: str = Field(..., pattern="^(Male|Female|Other)$")
    phone: Optional[str] = ""
    blood_group: Optional[str] = ""
    emergency_summary: Optional[str] = ""

class PatientResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    phc_id: Optional[str] = None
    name: str
    age: int
    gender: str
    phone: str
    blood_group: str
    emergency_summary: str
