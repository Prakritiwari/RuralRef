import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Integer, Boolean, Text, DateTime, ForeignKey, UniqueConstraint, CheckConstraint
from sqlalchemy.orm import relationship
from ..database import Base

def generate_uuid() -> str:
    return str(uuid.uuid4())

class Referral(Base):
    __tablename__ = "referrals"

    id = Column(String, primary_key=True, default=generate_uuid)
    referral_number = Column(String, unique=True, nullable=False, index=True)
    patient_id = Column(String, ForeignKey("patients.id", ondelete="RESTRICT"), nullable=False, index=True)
    phc_id = Column(String, ForeignKey("phcs.id", ondelete="RESTRICT"), nullable=False, index=True)
    hospital_id = Column(String, ForeignKey("hospitals.id", ondelete="SET NULL"), nullable=True, index=True)
    urgency = Column(String, default="MEDIUM", nullable=False)  # LOW, MEDIUM, HIGH, CRITICAL
    clinical_summary = Column(Text, default="", nullable=False)
    specialist_needed = Column(String, default="")
    notes = Column(Text, default="")
    status = Column(String, default="PENDING", nullable=False, index=True)
    # Status lifecycle:
    # PENDING -> ACCEPTED / REJECTED -> AMBULANCE_ASSIGNED -> AMBULANCE_EN_ROUTE -> PATIENT_PICKED_UP -> PATIENT_IN_TRANSIT -> ARRIVED -> COMPLETED (or CANCELLED)
    
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    accepted_at = Column(DateTime, nullable=True)
    rejected_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)

    # Relationships
    patient = relationship("Patient")
    phc = relationship("PHC")
    hospital = relationship("Hospital")
    requirements = relationship("ReferralResource", back_populates="referral", cascade="all, delete-orphan")
    ambulance = relationship("Ambulance", back_populates="active_referral", uselist=False)

class ReferralResource(Base):
    __tablename__ = "referral_resources"

    id = Column(String, primary_key=True, default=generate_uuid)
    referral_id = Column(String, ForeignKey("referrals.id", ondelete="CASCADE"), nullable=False, index=True)
    resource_id = Column(String, ForeignKey("resources.id", ondelete="RESTRICT"), nullable=False, index=True)
    quantity = Column(Integer, default=1, nullable=False)
    is_critical = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    __table_args__ = (
        UniqueConstraint("referral_id", "resource_id", name="uq_referral_resource"),
        CheckConstraint("quantity > 0", name="chk_req_qty_positive")
    )

    # Relationships
    referral = relationship("Referral", back_populates="requirements")
    resource = relationship("Resource")
