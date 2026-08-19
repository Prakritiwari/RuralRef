from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from ..database import get_db
from ..models.ambulance import AmbulanceLocation, Ambulance

router = APIRouter(prefix="/tracking", tags=["Live Tracking & Telemetry"])

@router.get("/ambulance/{ambulance_id}/trail")
def get_ambulance_trail(
    ambulance_id: str,
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db)
):
    amb = db.query(Ambulance).filter(Ambulance.id == ambulance_id).first()
    if not amb:
        raise HTTPException(status_code=404, detail="Ambulance not found")

    points = db.query(AmbulanceLocation).filter(
        AmbulanceLocation.ambulance_id == ambulance_id
    ).order_by(AmbulanceLocation.timestamp.desc()).limit(limit).all()

    return {
        "ambulance_id": ambulance_id,
        "current_position": {
            "latitude": amb.current_latitude,
            "longitude": amb.current_longitude,
            "status": amb.status,
            "last_update": amb.last_location_update.isoformat()
        },
        "trail": [
            {
                "latitude": p.latitude,
                "longitude": p.longitude,
                "speed": p.speed,
                "heading": p.heading,
                "timestamp": p.timestamp.isoformat()
            } for p in points
        ]
    }
