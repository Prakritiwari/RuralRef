import math

def calculate_haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate the great-circle distance between two points on the Earth's surface
    using the Haversine formula (in kilometers).
    
    This is an explainable geometric proximity measure.
    """
    # Earth's radius in kilometers
    R = 6371.0
    
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    
    a = (
        math.sin(dlat / 2.0) ** 2
        + math.cos(math.radians(lat1))
        * math.cos(math.radians(lat2))
        * math.sin(dlon / 2.0) ** 2
    )
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
    
    distance = R * c
    return round(distance, 2)

def estimate_road_travel_time_minutes(distance_km: float, speed_kmh: float = 45.0) -> int:
    """
    Estimates road travel time considering typical rural ambulance driving speeds (40-50 km/h).
    """
    if distance_km <= 0:
        return 0
    # Include 10% road tortuosity factor for rural roads
    effective_road_km = distance_km * 1.15
    hours = effective_road_km / speed_kmh
    return max(1, round(hours * 60))
