from typing import List, Dict, Any, Tuple
from sqlalchemy.orm import Session
from ..models.hospital import Hospital
from ..models.resource import HospitalResource, Resource
from ..models.phc import PHC
from ..models.ambulance import Ambulance
from ..models.referral import Referral, ReferralResource
from ..schemas.hospital import HospitalRecommendationResponse
from ..schemas.resource import HospitalResourceResponse
from ..utils.distance import calculate_haversine_distance, estimate_road_travel_time_minutes

def calculate_hospital_recommendations(
    db: Session,
    phc_latitude: float,
    phc_longitude: float,
    required_resources: List[Tuple[str, int]],  # List of (resource_id, quantity)
    specialist_needed: str = "",
    max_search_radius_km: float = 120.0
) -> List[HospitalRecommendationResponse]:
    """
    Computes explainable logistics-based recommendations for nearby hospitals.
    
    Safety Note: This is purely an operational logistics and resource matching tool.
    It does not diagnose conditions or determine medical treatments.
    """
    hospitals = db.query(Hospital).filter(Hospital.is_active == True).all()
    recommendations: List[HospitalRecommendationResponse] = []

    # Map catalog for fast lookup
    catalog_map = {r.id: r for r in db.query(Resource).all()}

    for hospital in hospitals:
        # 1. Geographic distance
        distance_km = calculate_haversine_distance(
            phc_latitude, phc_longitude,
            hospital.latitude, hospital.longitude
        )
        travel_time = estimate_road_travel_time_minutes(distance_km)

        # 2. Inventory map
        inventory_items = db.query(HospitalResource).filter(
            HospitalResource.hospital_id == hospital.id
        ).all()
        inv_map = {item.resource_id: item for item in inventory_items}

        # 3. Available Ambulances
        avail_ambulances = db.query(Ambulance).filter(
            Ambulance.hospital_id == hospital.id,
            Ambulance.status == "AVAILABLE",
            Ambulance.is_active == True
        ).count()

        # 4. Check Hard Resource Requirements & build explanation
        is_eligible = True
        match_reasons = []
        missing_resources = []
        resource_surplus_total = 0

        for res_id, req_qty in required_resources:
            inv = inv_map.get(res_id)
            res_meta = catalog_map.get(res_id)
            res_label = res_meta.name if res_meta else res_id

            if not inv or inv.available_quantity < req_qty:
                is_eligible = False
                avail = inv.available_quantity if inv else 0
                missing_resources.append(f"{res_label} (Need: {req_qty}, Available: {avail})")
            else:
                surplus = inv.available_quantity - req_qty
                resource_surplus_total += min(surplus, 5)
                match_reasons.append(f"{inv.available_quantity} {res_label} available (Requirement: {req_qty})")

        # 5. Specialist matching if specified
        if specialist_needed:
            # Check if hospital offers this specialty or has related resource
            spec_upper = specialist_needed.upper()
            has_spec = any(spec_upper in item.resource_id.upper() for item in inventory_items if item.available_quantity > 0)
            if has_spec or hospital.level == "Tertiary Care":
                match_reasons.append(f"Specialist/Department available: {specialist_needed}")
            else:
                match_reasons.append(f"General referral capacity for {specialist_needed}")

        # 6. Scoring Components (0 to 100)
        # A. Proximity Score (35% weight)
        proximity_score = max(0.0, 100.0 - (distance_km / max_search_radius_km) * 100.0)
        match_reasons.append(f"Proximity: ~{distance_km:.1f} km (est. {travel_time} mins by road)")

        # B. Resource Depth & Surplus Score (45% weight)
        if is_eligible:
            resource_score = min(100.0, 60.0 + resource_surplus_total * 8.0)
        else:
            resource_score = max(0.0, 30.0 - len(missing_resources) * 10.0)

        # C. Emergency & Fleet Readiness Score (20% weight)
        emergency_score = 0.0
        if hospital.emergency_available:
            emergency_score += 60.0
            match_reasons.append("Emergency department active & accepting cases")
        else:
            match_reasons.append("Emergency department limited")

        if avail_ambulances > 0:
            emergency_score += min(40.0, 20.0 + avail_ambulances * 10.0)
            match_reasons.append(f"{avail_ambulances} emergency ambulance(s) on station")
        else:
            match_reasons.append("No ambulance currently idling on station")

        # Combined Weighted Score
        raw_score = (
            resource_score * 0.45
            + proximity_score * 0.35
            + emergency_score * 0.20
        )
        
        # Penalize ineligible hospitals so eligible ones always score significantly higher
        if not is_eligible:
            final_score = round(min(raw_score * 0.35, 38.0), 1)
        else:
            final_score = round(raw_score, 1)

        # Build Resource Breakdown DTOs
        breakdown = []
        for inv in inventory_items:
            res_meta = catalog_map.get(inv.resource_id)
            breakdown.append(
                HospitalResourceResponse(
                    id=inv.id,
                    hospital_id=inv.hospital_id,
                    resource_id=inv.resource_id,
                    resource_name=res_meta.name if res_meta else inv.resource_id,
                    resource_category=res_meta.category if res_meta else "GENERAL",
                    resource_unit=res_meta.unit if res_meta else "UNIT",
                    total_quantity=inv.total_quantity,
                    available_quantity=inv.available_quantity,
                    reserved_quantity=inv.reserved_quantity,
                    status=inv.status
                )
            )

        recommendations.append(
            HospitalRecommendationResponse(
                hospital_id=hospital.id,
                hospital_name=hospital.name,
                district=hospital.district,
                level=hospital.level,
                distance_km=distance_km,
                estimated_travel_minutes=travel_time,
                recommendation_score=final_score,
                is_eligible=is_eligible,
                emergency_available=hospital.emergency_available,
                available_ambulances_count=avail_ambulances,
                match_reasons=match_reasons[:5],
                missing_resources=missing_resources,
                resource_breakdown=breakdown
            )
        )

    # Sort: Eligible hospitals first, then by highest recommendation score, then by closest distance
    return sorted(
        recommendations,
        key=lambda r: (1 if r.is_eligible else 0, r.recommendation_score, -r.distance_km),
        reverse=True
    )
