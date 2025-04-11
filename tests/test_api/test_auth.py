from fastapi import FastAPI
from fastapi.testclient import TestClient
from app.api.routes.auth import router as auth_router

app = FastAPI()
app.include_router(auth_router)

client = TestClient(app)

def test_login():
    response = client.post("/auth/login", json={"username": "testuser", "password": "testpass"})
    assert response.status_code == 200
    assert "access_token" in response.json()

def test_register():
    response = client.post("/auth/register", json={"username": "newuser", "password": "newpass"})
    assert response.status_code == 201
    assert response.json()["username"] == "newuser"

def test_login_invalid_credentials():
    response = client.post("/auth/login", json={"username": "invaliduser", "password": "wrongpass"})
    assert response.status_code == 401
    assert "detail" in response.json()