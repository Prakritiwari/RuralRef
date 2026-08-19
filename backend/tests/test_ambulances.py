def test_ambulance_gps_and_status_transitions(client):
    # 1. Login as Hospital Admin
    login_res = client.post("/api/auth/login", json={
        "email": "hospital@demo.com",
        "password": "demo123"
    })
    token = login_res.json()["token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Get Ambulances
    amb_res = client.get("/api/ambulances", headers=headers)
    assert amb_res.status_code == 200
    ambulances = amb_res.json()
    assert len(ambulances) > 0
    ambulance_id = ambulances[0]["id"]

    # 3. Post GPS Location Update
    gps_res = client.post(f"/api/ambulances/{ambulance_id}/location", json={
        "latitude": 19.7050,
        "longitude": 72.7800,
        "speed": 48.5,
        "heading": 90.0,
        "accuracy": 4.0
    })
    assert gps_res.status_code == 200
    assert gps_res.json()["status"] == "success"

    # 4. Check Trail
    trail_res = client.get(f"/api/tracking/ambulance/{ambulance_id}/trail", headers=headers)
    assert trail_res.status_code == 200
    trail_data = trail_res.json()
    assert len(trail_data["trail"]) > 0
    assert trail_data["current_position"]["latitude"] == 19.7050
