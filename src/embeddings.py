"""Comentario V1 - Geração de embeddings e comparação por cosseno - cria representações vetoriais de textos usando sentence-transformers."""
from __future__ import annotations
import numpy as np

class EmbeddingService:
    def __init__(self, model_name: str):
        # Comentario V1 - Inicializa modelo SentenceTransformer para geração de embeddings multilinguîs
        from sentence_transformers import SentenceTransformer
        self.model=SentenceTransformer(model_name)
    def encode(self,texts:list[str]) -> np.ndarray:
        # Comentario V1 - Gera embeddings normalizados para lista de textos, retorna matriz numpy
        return np.asarray(self.model.encode(texts,normalize_embeddings=True),dtype=float)

def cosine_scores(query_vector: np.ndarray, matrix: np.ndarray) -> np.ndarray:
    # Comentario V1 - Calcula similaridade cosseno entre vetor de query e matriz de vetores, normalizados no espaco L2
    # Comentario V1 - Converte query para array numpy 1D
    query=np.asarray(query_vector,dtype=float).reshape(-1)
    # Comentario V1 - Converte matriz de dados para array numpy
    data=np.asarray(matrix,dtype=float)
    # Comentario V1 - Calcula normas L2: para query (escalar) e para cada linha de data (vetor)
    qn=np.linalg.norm(query); dn=np.linalg.norm(data,axis=1)
    # Comentario V1 - Similaridade cosseno = (data @ query) / (||data|| * ||query||), com proteção contra divisão por zero
    return (data@query)/np.where(dn*qn==0,1,dn*qn)

def top_k(query:str,texts:list[str],service:EmbeddingService,k:int=5) -> list[tuple[int,float]]:
    # Comentario V1 - Encontra os k textos mais similares à query usando similaridade cosseno
    if not texts: return []
    # Comentario V1 - Gera embeddings para query e todos os textos (query como primeiro elemento)
    vectors=service.encode([query,*texts])
    # Comentario V1 - Calcula scores de similaridade cosseno entre query (primeiro vetor) e textos (demais vetores)
    scores=cosine_scores(vectors[0],vectors[1:])
    # Comentario V1 - Retorna índices dos k textos com maior similaridade, ordenados em ordem decrescente
    return [(int(i),float(scores[i])) for i in np.argsort(scores)[::-1][:k]]
