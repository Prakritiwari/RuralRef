from math import sqrt
from sqlalchemy.orm import Session
from .models import Hospital, Resource, Specialist

def distance_km(lat1, lon1, lat2, lon2):
    # Lightweight approximation; production should use a routing provider.
    return sqrt(((lat1-lat2)*111)**2 + ((lon1-lon2)*105)**2)

def recommend(db: Session, referral):
    hospitals = db.query(Hospital).filter(Hospital.online == True).all()
    results = []
    for h in hospitals:
        r = db.query(Resource).filter(Resource.hospital_id == h.id).first()
        specs = db.query(Specialist).filter(
            Specialist.hospital_id == h.id,
            Specialist.available == True
        ).all()
        spec_match = (not referral.specialist_needed) or any(
            referral.specialist_needed.lower() in s.specialty.lower() for s in specs
        )
        resource_ok = (
            (not referral.needs_icu or (r and r.icu_available > 0)) and
            (not referral.needs_oxygen or (r and r.oxygen_available > 0)) and
            (not referral.needs_ventilator or (r and r.ventilators_available > 0))
        )
        score = 0
        reasons = []
        if referral.needs_icu:
            if r and r.icu_available > 0: score += 30; reasons.append(f"{r.icu_available} ICU bed(s) available")
            else: reasons.append("No ICU bed currently available")
        if referral.needs_oxygen:
            if r and r.oxygen_available > 0: score += 20; reasons.append(f"{r.oxygen_available} oxygen unit(s) available")
            else: reasons.append("Oxygen resource unavailable")
        if referral.needs_ventilator:
            if r and r.ventilators_available > 0: score += 25; reasons.append(f"{r.ventilators_available} ventilator(s) available")
            else: reasons.append("No ventilator available")
        if referral.specialist_needed:
            if spec_match: score += 20; reasons.append("Required specialist available")
            else: reasons.append("Required specialist not currently available")
        if resource_ok and spec_match:
            score += 15
        dist = distance_km(19.10, 72.83, h.latitude, h.longitude)
        score += max(0, 10 - min(10, dist))
        reasons.append(f"Approx. {dist:.1f} km away")
        results.append({
            "hospital_id": h.id, "hospital": h.name, "district": h.district,
            "score": round(score, 1), "eligible": bool(resource_ok and spec_match),
            "reasons": reasons,
            "icu_available": r.icu_available if r else 0,
            "oxygen_available": r.oxygen_available if r else 0,
            "ventilators_available": r.ventilators_available if r else 0,
            "specialists": [s.specialty for s in specs]
        })
    return sorted(results, key=lambda x: (x["eligible"], x["score"]), reverse=True)
