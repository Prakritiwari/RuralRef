import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, ForeignKey, BigInteger
from sqlalchemy.orm import relationship
from ..database import Base

def generate_uuid() -> str:
    return str(uuid.uuid4())

class Ambulance(Base):
    __tablename__ = "ambulances"

    id = Column(String, primary_key=True, default=generate_uuid)
    hospital_id = Column(String, ForeignKey("hospitals.id", ondelete="CASCADE"), nullable=False, index=True)
    vehicle_number = Column(String, unique=True, nullable=False, index=True)
    driver_name = Column(String, nullable=False)
    driver_phone = Column(String, nullable=False)
    ambulance_type = Column(String, default="ADVANCED_LIFE_SUPPORT")  # BASIC_LIFE_SUPPORT, ADVANCED_LIFE_SUPPORT, PATIENT_TRANSPORT
    status = Column(String, default="AVAILABLE", nullable=False, index=True)
    # Status: AVAILABLE, ASSIGNED, EN_ROUTE_TO_PHC, PATIENT_PICKED_UP, TRANSPORTING, ARRIVED, OFFLINE
    
    current_latitude = Column(Float, nullable=False)
    current_longitude = Column(Float, nullable=False)
    active_referral_id = Column(String, ForeignKey("referrals.id", ondelete="SET NULL"), nullable=True, index=True)
    last_location_update = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Relationships
    hospital = relationship("Hospital", back_populates="ambulances")
    active_referral = relationship("Referral", back_populates="ambulance")

class AmbulanceLocation(Base):
    __tablename__ = "ambulance_locations"

    id = Column(Integer().with_variant(BigInteger, "postgresql"), primary_key=True, autoincrement=True)
    ambulance_id = Column(String, ForeignKey("ambulances.id", ondelete="CASCADE"), nullable=False, index=True)
    referral_id = Column(String, ForeignKey("referrals.id", ondelete="SET NULL"), nullable=True, index=True)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    speed = Column(Float, default=0.0)
    heading = Column(Float, default=0.0)
    accuracy = Column(Float, default=5.0)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)
