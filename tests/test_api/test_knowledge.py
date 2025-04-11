from fastapi import FastAPI
from fastapi.testclient import TestClient
from app.api.routes.knowledge import router as knowledge_router

app = FastAPI()
app.include_router(knowledge_router)

client = TestClient(app)

def test_upload_document():
    response = client.post("/knowledge/upload", json={"document": "sample document content"})
    assert response.status_code == 200
    assert response.json() == {"message": "Document uploaded successfully"}

def test_query_document():
    response = client.post("/knowledge/query", json={"query": "What is the content?"})
    assert response.status_code == 200
    assert "sample document content" in response.json()["response"]