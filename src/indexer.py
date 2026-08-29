"""Comentario V1 - Indexação dos chunks persistidos no ChromaDB - constrói índices vetoriais e realiza buscas semânticas."""
from __future__ import annotations
from pathlib import Path
import json
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session
from .models import Chunk
from .embeddings import EmbeddingService
from .vector_store import ChromaStore

def build_index(cfg: dict) -> int:
    # Comentario V1 - Constrói índice vetorial ChromaDB contendo todos os chunks com embeddings
    # Comentario V1 - Obtém raiz do projeto e URL do banco de dados
    root=Path(cfg["_root"]); url=cfg["banco"]["url"]
    # Comentario V1 - Normaliza path relativo do SQLite para caminho absoluto
    if url.startswith("sqlite:///") and not url.startswith("sqlite:////"): url="sqlite:///"+str(root/url[10:])
    # Comentario V1 - Recupera todos os chunks persistidos do banco de dados
    with Session(create_engine(url)) as session: chunks=list(session.scalars(select(Chunk)).all())
    # Comentario V1 - Se não há chunks, retorna 0
    if not chunks: return 0
    # Comentario V1 - Cria serviço de embeddings e extrai conteúdo de todos os chunks
    service=EmbeddingService(cfg["embeddings"]["modelo"]); docs=[c.conteudo for c in chunks]
    # Comentario V1 - Gera embeddings para todos os documentos
    vectors=service.encode(docs)
    # Comentario V1 - Cria store ChromaDB e insere/atualiza chunks com embeddings
    store=ChromaStore(root/cfg["chromadb"]["diretorio"],cfg["chromadb"]["colecao"])
    store.upsert([str(c.id) for c in chunks],docs,[json.loads(c.metadata_json) for c in chunks],vectors.tolist())
    # Comentario V1 - Retorna quantidade de chunks indexados
    return len(chunks)

def semantic_query(cfg:dict,question:str,top_k:int=5,category:str|None=None) -> list[dict]:
    # Comentario V1 - Realiza busca semântica no ChromaDB e retorna top-k chunks mais similares à pergunta
    # Comentario V1 - Inicializa serviço de embeddings e gera embedding para a pergunta
    root=Path(cfg["_root"]); service=EmbeddingService(cfg["embeddings"]["modelo"]); query=service.encode([question])[0].tolist()
    # Comentario V1 - Cria store ChromaDB para consulta
    store=ChromaStore(root/cfg["chromadb"]["diretorio"],cfg["chromadb"]["colecao"])
    # Comentario V1 - Prepara filtro de categoria se fornecido
    where={"categoria":category} if category else None
    # Comentario V1 - Executa busca vetorial no ChromaDB
    rows=store.query(query,top_k,where)
    # Comentario V1 - Retorna resultados combinando metadados, conteúdo e similaridade arredondada
    return [{**r["metadata"],"conteudo":r["conteudo"],"similaridade":round(r["similaridade"],4)} for r in rows]
