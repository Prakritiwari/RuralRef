from app.services.recommendation_service import calculate_hospital_recommendations

def test_recommendation_filters_ineligible_hospitals(db_session):
    """
    Hospital 3 (JanSeva) has 0 available ventilators in the seed data.
    When a referral requires a ventilator, Hospital 3 must be marked is_eligible=False.
    """
    # PHC Palghar coordinates: 19.6967, 72.7699
    results = calculate_hospital_recommendations(
        db=db_session,
        phc_latitude=19.6967,
        phc_longitude=72.7699,
        required_resources=[("ICU", 1), ("VENTILATOR", 1)],
        specialist_needed=""
    )
    assert len(results) > 0

    # Locate JanSeva
    janseva = next((h for h in results if "JanSeva" in h.hospital_name), None)
    assert janseva is not None
    assert janseva.is_eligible is False
    assert any("Ventilator" in msg or "VENTILATOR" in msg for msg in janseva.missing_resources)

    # Locate Sahyadri (eligible)
    sahyadri = next((h for h in results if "Sahyadri" in h.hospital_name), None)
    assert sahyadri is not None
    assert sahyadri.is_eligible is True
    assert sahyadri.recommendation_score > janseva.recommendation_score
