def test_login_success(client):
    response = client.post("/api/auth/login", json={
        "email": "doctor@demo.com",
        "password": "demo123"
    })
    assert response.status_code == 200
    data = response.json()
    assert "token" in data
    assert data["user"]["email"] == "doctor@demo.com"
    assert data["user"]["role"] in ("PHC", "doctor")

def test_login_invalid_password(client):
    response = client.post("/api/auth/login", json={
        "email": "doctor@demo.com",
        "password": "wrongpassword"
    })
    assert response.status_code == 401

def test_auth_me_endpoint(client):
    # 1. Login
    login_res = client.post("/api/auth/login", json={
        "email": "hospital@demo.com",
        "password": "demo123"
    })
    token = login_res.json()["token"]

    # 2. Get Profile
    me_res = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me_res.status_code == 200
    assert me_res.json()["email"] == "hospital@demo.com"
    assert me_res.json()["role"] in ("HOSPITAL", "admin")

def test_register_new_phc(client):
    res = client.post("/api/auth/register", json={
        "name": "Dr. Suresh Patil",
        "email": "suresh.patil@ruralreflink.gov",
        "password": "securepassword123",
        "role": "PHC",
        "phone": "+91-9988771122"
    })
    assert res.status_code == 200
    data = res.json()
    assert data["user"]["name"] == "Dr. Suresh Patil"
    assert data["user"]["role"] == "PHC"
