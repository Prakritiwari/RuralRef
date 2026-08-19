from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, ForeignKey, Text

from .database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False, index=True)
    password_hash = Column(String, nullable=False)
    role = Column(String, nullable=False)  # patient, doctor, admin
    phone = Column(String, default="")

class Hospital(Base):
    __tablename__ = "hospitals"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    district = Column(String, nullable=False)
    latitude = Column(Float, default=19.076)
    longitude = Column(Float, default=72.8777)
    level = Column(String, default="District Hospital")
    online = Column(Boolean, default=True)

class Resource(Base):
    __tablename__ = "resources"
    id = Column(Integer, primary_key=True)
    hospital_id = Column(Integer, ForeignKey("hospitals.id"), nullable=False)
    icu_total = Column(Integer, default=0)
    icu_available = Column(Integer, default=0)
    oxygen_available = Column(Integer, default=0)
    ventilators_total = Column(Integer, default=0)
    ventilators_available = Column(Integer, default=0)
    updated_at = Column(DateTime, default=datetime.utcnow)

class Specialist(Base):
    __tablename__ = "specialists"
    id = Column(Integer, primary_key=True)
    hospital_id = Column(Integer, ForeignKey("hospitals.id"), nullable=False)
    name = Column(String, nullable=False)
    specialty = Column(String, nullable=False)
    available = Column(Boolean, default=True)
    shift = Column(String, default="24x7")

class Referral(Base):
    __tablename__ = "referrals"
    id = Column(Integer, primary_key=True)
    patient_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    doctor_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    destination_hospital_id = Column(Integer, ForeignKey("hospitals.id"), nullable=True)
    symptoms = Column(Text, default="")
    urgency = Column(String, default="medium")
    needs_icu = Column(Boolean, default=False)
    needs_oxygen = Column(Boolean, default=False)
    needs_ventilator = Column(Boolean, default=False)
    specialist_needed = Column(String, default="")
    notes = Column(Text, default="")
    status = Column(String, default="PENDING")  # PENDING/ACCEPTED/REJECTED/IN_TRANSIT/ARRIVED
    created_at = Column(DateTime, default=datetime.utcnow)

class Ambulance(Base):
    __tablename__ = "ambulances"
    id = Column(Integer, primary_key=True)
    registration = Column(String, unique=True, nullable=False)
    hospital_id = Column(Integer, ForeignKey("hospitals.id"), nullable=True)
    status = Column(String, default="AVAILABLE")
    latitude = Column(Float, default=19.076)
    longitude = Column(Float, default=72.8777)
    driver_name = Column(String, default="")
    phone = Column(String, default="")
    referral_id = Column(Integer, ForeignKey("referrals.id"), nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow)
