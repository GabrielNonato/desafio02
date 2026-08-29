"""Comentario V1 - API HTTP de consulta - fornece endpoints FastAPI para health check e consultas RAG sobre atendimentos."""
from __future__ import annotations
import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from .config import load_config
from .indexer import semantic_query
from .rag import answer

app=FastAPI(title="Atendimentos FIC_DEV",version="1.0.0")
cfg=load_config()

# Comentario V1 - Modelo Pydantic para requisi\u00e7\u00e3o de consulta: pergunta, top-k de resultados e categoria opcional
class AskRequest(BaseModel):
    pergunta:str=Field(min_length=3,max_length=500)
    top_k:int=Field(default=5,ge=1,le=20)
    categoria:str|None=None

@app.get("/health")
def health():
    # Comentario V1 - Endpoint de verificação de saúde que retorna modo de operação (RAG com OpenAI ou recuperação local)
    # Comentario V1 - Checa presença de OPENAI_API_KEY para determinar se usar LLM ou modo local
    return {"status":"ok","modo":"rag" if os.getenv("OPENAI_API_KEY") else "recuperacao_local"}

@app.post("/ask")
def ask(payload:AskRequest):
    # Comentario V1 - Endpoint principal de consulta que realiza busca semântica e gera resposta via RAG ou modo local
    try:
        # Comentario V1 - Executa busca semântica no ChromaDB com filtro de categoria se fornecido
        sources=semantic_query(cfg,payload.pergunta,payload.top_k,payload.categoria)
        # Comentario V1 - Chama função answer que sintetiza resposta com LLM ou retorna modo local
        return answer(payload.pergunta,sources,os.getenv("OPENAI_MODEL","gpt-4.1-mini"))
    # Comentario V1 - Retorna erro 503 se ocorrer qualquer exceção durante processamento
    except Exception as exc:
        raise HTTPException(status_code=503,detail=f"Consulta indisponível: {type(exc).__name__}") from exc
