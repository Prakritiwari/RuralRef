import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Integer, Boolean, Text, DateTime, ForeignKey, UniqueConstraint, CheckConstraint
from sqlalchemy.orm import relationship
from ..database import Base

def generate_uuid() -> str:
    return str(uuid.uuid4())

class Resource(Base):
    __tablename__ = "resources"

    id = Column(String, primary_key=True)  # e.g. ICU, VENTILATOR, OXYGEN, BLOOD_O_POS, CT_SCAN
    name = Column(String, nullable=False)
    category = Column(String, nullable=False)  # BED, EQUIPMENT, SPECIALTY, DIAGNOSTIC, BLOOD
    unit = Column(String, default="UNIT")  # BED, CYLINDER, UNIT, DOCTOR
    description = Column(Text, default="")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

class HospitalResource(Base):
    __tablename__ = "hospital_resources"

    id = Column(String, primary_key=True, default=generate_uuid)
    hospital_id = Column(String, ForeignKey("hospitals.id", ondelete="CASCADE"), nullable=False, index=True)
    resource_id = Column(String, ForeignKey("resources.id", ondelete="RESTRICT"), nullable=False, index=True)
    total_quantity = Column(Integer, default=0, nullable=False)
    available_quantity = Column(Integer, default=0, nullable=False)
    reserved_quantity = Column(Integer, default=0, nullable=False)
    status = Column(String, default="AVAILABLE")  # AVAILABLE, LIMITED, UNAVAILABLE
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    __table_args__ = (
        UniqueConstraint("hospital_id", "resource_id", name="uq_hospital_resource"),
        CheckConstraint("available_quantity >= 0", name="chk_available_non_negative"),
        CheckConstraint("reserved_quantity >= 0", name="chk_reserved_non_negative"),
        CheckConstraint("total_quantity >= 0", name="chk_total_non_negative"),
        CheckConstraint("available_quantity + reserved_quantity <= total_quantity", name="chk_quantity_sum"),
    )

    # Relationships
    hospital = relationship("Hospital", back_populates="resources")
    resource = relationship("Resource")
