from security import hash_password, verify_password

USER = {"username": "student", "email": "student@example.com", "password": "secret123"}


def test_password_hash():
    hashed = hash_password(USER["password"])
    assert hashed != USER["password"]
    assert verify_password(USER["password"], hashed)
    assert not verify_password("wrong", hashed)


def test_login_and_profile(client):
    registered = client.post("/auth/register", json=USER)
    assert registered.status_code == 201
    assert set(registered.json()) == {"id", "username", "email"}
    login = client.post("/auth/login", json=USER)
    assert login.status_code == 200
    token = login.json()["access_token"]
    profile = client.get("/profile/me", headers={"Authorization": f"Bearer {token}"})
    assert profile.status_code == 200
    assert profile.json() == registered.json()

def test_login_with_wrong_password(client):
    registered = client.post("/auth/register", json=USER)
    assert registered.status_code == 201
    login = client.post("/auth/login", json={"email": USER["email"], "password": "wrong"})
    assert login.status_code == 401
    assert login.json() == {"detail": "Invalid email or password"}

def test_profile_requires_token(client):
    response = client.get("/profile/me")
    assert response.status_code == 401
    assert response.json() == {"detail": "Not authenticated"}

def test_invalid_data(client):
    # Test registration with invalid data
    response = client.post("/auth/register", json={"username": "ab", "email": "invalid", "password": "123"})
    assert response.status_code == 422  # Unprocessable Entity    

def test_duplicate_registration(client):
    # Register the user for the first time
    response1 = client.post("/auth/register", json=USER)
    assert response1.status_code == 201

    # Attempt to register the same user again
    response2 = client.post("/auth/register", json=USER)
    assert response2.status_code == 409  # Conflict
    assert response2.json() == {"detail": "Email already registered"}