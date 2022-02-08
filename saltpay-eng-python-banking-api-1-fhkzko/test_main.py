from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_home():
    response = client.get("/ping")
    assert response.status_code == 200
        
def test_home_second():
    response = client.get("/ping")
    assert response.json() == {"msg":"pong"}



  
