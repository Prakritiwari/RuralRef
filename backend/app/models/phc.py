import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Float, Boolean, Text, DateTime
from ..database import Base

def generate_uuid() -> str:
    return str(uuid.uuid4())

class PHC(Base):
    __tablename__ = "phcs"

    id = Column(String, primary_key=True, default=generate_uuid)
    name = Column(String, nullable=False)
    code = Column(String, unique=True, nullable=False, index=True)
    address = Column(Text, nullable=False)
    district = Column(String, nullable=False)
    state = Column(String, default="Maharashtra")
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    contact_phone = Column(String, nullable=False)
    contact_email = Column(String, default="")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
