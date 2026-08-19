import pytest
from app.models.resource import HospitalResource
from app.models.referral import Referral, ReferralResource
from app.models.patient import Patient
from app.models.phc import PHC
from app.models.hospital import Hospital
from app.services.referral_service import accept_referral_atomic
from fastapi import HTTPException

def test_concurrent_resource_reservation_constraint(db_session):
    """
    Explicit test verifying that when only 1 ICU bed is available,
    only one referral can successfully reserve it, and the second
    is rejected with a 409 Conflict error without driving capacity negative.
    """
    # 1. Setup hospital with exactly 1 available ICU bed
    hosp = db_session.query(Hospital).first()
    icu_inv = db_session.query(HospitalResource).filter(
        HospitalResource.hospital_id == hosp.id,
        HospitalResource.resource_id == "ICU"
    ).first()
    icu_inv.total_quantity = 5
    icu_inv.available_quantity = 1
    icu_inv.reserved_quantity = 4
    icu_inv.status = "LIMITED"
    db_session.commit()

    # 2. Setup two patients
    phc = db_session.query(PHC).first()
    p1 = Patient(name="Patient A", age=45, gender="Male", phc_id=phc.id)
    p2 = Patient(name="Patient B", age=52, gender="Female", phc_id=phc.id)
    db_session.add_all([p1, p2])
    db_session.commit()

    # 3. Create two pending referrals both requesting 1 ICU bed
    ref1 = Referral(
        referral_number="REF-CONC-001",
        patient_id=p1.id,
        phc_id=phc.id,
        hospital_id=hosp.id,
        urgency="CRITICAL",
        clinical_summary="Severe acute condition A",
        status="PENDING"
    )
    ref2 = Referral(
        referral_number="REF-CONC-002",
        patient_id=p2.id,
        phc_id=phc.id,
        hospital_id=hosp.id,
        urgency="CRITICAL",
        clinical_summary="Severe acute condition B",
        status="PENDING"
    )
    db_session.add_all([ref1, ref2])
    db_session.flush()

    req1 = ReferralResource(referral_id=ref1.id, resource_id="ICU", quantity=1, is_critical=True)
    req2 = ReferralResource(referral_id=ref2.id, resource_id="ICU", quantity=1, is_critical=True)
    db_session.add_all([req1, req2])
    db_session.commit()

    # 4. First referral accepts
    accepted_ref1 = accept_referral_atomic(db_session, ref1.id, hosp.id)
    assert accepted_ref1.status == "ACCEPTED"

    # Verify ICU inventory decreased to 0 and reserved increased to 5
    db_session.refresh(icu_inv)
    assert icu_inv.available_quantity == 0
    assert icu_inv.reserved_quantity == 5
    assert icu_inv.status == "UNAVAILABLE"

    # 5. Second referral attempts to accept -> MUST raise 409 Conflict
    with pytest.raises(HTTPException) as exc_info:
        accept_referral_atomic(db_session, ref2.id, hosp.id)

    assert exc_info.value.status_code == 409
    assert "no longer available" in exc_info.value.detail

    # 6. Crucial check: Available ICU quantity must NEVER be negative
    db_session.refresh(icu_inv)
    assert icu_inv.available_quantity == 0
    assert icu_inv.reserved_quantity == 5
    assert icu_inv.available_quantity + icu_inv.reserved_quantity <= icu_inv.total_quantity
