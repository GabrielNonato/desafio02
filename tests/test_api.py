# Comentario V1 - Testes de endpoints HTTP da API: health check e validação de entrada
from fastapi.testclient import TestClient
from src.api import app

def test_health():
    # Comentario V1 - Verifica endpoint de health check retorna status OK
    response=TestClient(app).get("/health")
    assert response.status_code==200 and response.json()["status"]=="ok"

def test_ask_validation():
    # Comentario V1 - Valida que pergunta com tamanho inferior ao mínimo retorna erro 422
    response=TestClient(app).post("/ask",json={"pergunta":"x"})
    assert response.status_code==422
