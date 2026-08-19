from typing import Any, Dict, Optional
from sqlalchemy.orm import Session
from ..models.audit import AuditLog

def log_audit_event(
    db: Session,
    action: str,
    entity_type: str,
    entity_id: str,
    actor_user_id: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None
) -> AuditLog:
    """
    Records an immutable audit event for healthcare coordination actions.
    """
    event = AuditLog(
        actor_user_id=actor_user_id,
        action=action,
        entity_type=entity_type,
        entity_id=str(entity_id),
        audit_metadata=metadata or {}
    )
    db.add(event)
    # Commit or let the calling transaction commit
    return event
