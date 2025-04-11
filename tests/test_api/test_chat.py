from fastapi import FastAPI
from fastapi.testclient import TestClient
from app.api.routes.chat import router as chat_router

app = FastAPI()
app.include_router(chat_router)

client = TestClient(app)

def test_chat_endpoint():
    response = client.post("/chat", json={"query": "Hello, how can I use this assistant?"})
    assert response.status_code == 200
    assert "response" in response.json()