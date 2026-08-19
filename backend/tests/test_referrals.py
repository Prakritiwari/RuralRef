def test_full_referral_lifecycle(client):
    # 1. Login as PHC doctor
    login_res = client.post("/api/auth/login", json={
        "email": "doctor@demo.com",
        "password": "demo123"
    })
    doctor_token = login_res.json()["token"]
    doctor_headers = {"Authorization": f"Bearer {doctor_token}"}

    # 2. Get Patients
    patients_res = client.get("/api/patients", headers=doctor_headers)
    assert patients_res.status_code == 200
    patients = patients_res.json()
    assert len(patients) > 0
    patient_id = patients[0]["id"]

    # 3. Create Critical Referral
    ref_payload = {
        "patient_id": patient_id,
        "urgency": "CRITICAL",
        "clinical_summary": "Acute bilateral pneumonia with respiratory distress",
        "specialist_needed": "Pulmonology",
        "notes": "Patient requires immediate oxygen and ICU admission",
        "required_resources": [
            {"resource_id": "ICU", "quantity": 1, "is_critical": True},
            {"resource_id": "VENTILATOR", "quantity": 1, "is_critical": True},
            {"resource_id": "OXYGEN", "quantity": 1, "is_critical": True}
        ]
    }
    create_res = client.post("/api/referrals", json=ref_payload, headers=doctor_headers)
    assert create_res.status_code == 201
    referral = create_res.json()
    assert referral["status"] == "PENDING"
    referral_id = referral["id"]

    # 4. Get Recommendations
    rec_res = client.get(f"/api/referrals/{referral_id}/recommendations", headers=doctor_headers)
    assert rec_res.status_code == 200
    recs = rec_res.json()
    assert len(recs) > 0
    # Top hospital should be eligible
    assert recs[0]["is_eligible"] is True
    target_hospital_id = recs[0]["hospital_id"]

    # 5. Dispatch Referral to Hospital
    send_res = client.post(f"/api/referrals/{referral_id}/send?hospital_id={target_hospital_id}", headers=doctor_headers)
    assert send_res.status_code == 200
    assert send_res.json()["hospital_id"] == target_hospital_id

    # 6. Login as Hospital Admin
    hosp_login = client.post("/api/auth/login", json={
        "email": "hospital@demo.com",
        "password": "demo123"
    })
    hosp_token = hosp_login.json()["token"]
    hosp_headers = {"Authorization": f"Bearer {hosp_token}"}

    # 7. Hospital Accepts Referral -> Atomic Resource Reservation
    accept_res = client.post(f"/api/referrals/{referral_id}/accept", headers=hosp_headers)
    assert accept_res.status_code == 200
    assert accept_res.json()["status"] == "ACCEPTED"

    # 8. Allocate Ambulance
    amb_res = client.post(f"/api/referrals/{referral_id}/ambulance", headers=hosp_headers)
    assert amb_res.status_code == 200
    assert amb_res.json()["status"] == "AMBULANCE_ASSIGNED"
    assert amb_res.json()["ambulance"] is not None
