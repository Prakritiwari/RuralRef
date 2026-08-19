from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, DateTime, JSON, BigInteger
from ..database import Base

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer().with_variant(BigInteger, "postgresql"), primary_key=True, autoincrement=True)
    actor_user_id = Column(String, nullable=True, index=True)
    action = Column(String, nullable=False, index=True)  # REFERRAL_CREATED, REFERRAL_ACCEPTED, RESOURCE_RESERVED, AMBULANCE_ASSIGNED, etc.
    entity_type = Column(String, nullable=False)  # REFERRAL, HOSPITAL_RESOURCE, AMBULANCE, etc.
    entity_id = Column(String, nullable=False)
    audit_metadata = Column(JSON, default=dict)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)
