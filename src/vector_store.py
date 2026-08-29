"""Comentario V1 - Persistência e consulta dos chunks no ChromaDB - abstração para operações vetoriais com ChromaDB."""
from __future__ import annotations
from pathlib import Path

class ChromaStore:
    def __init__(self,directory:str|Path,collection:str):
        # Comentario V1 - Inicializa cliente ChromaDB persistente e cria ou recupera coleção com índice de espaço cosseno
        import chromadb
        self.client=chromadb.PersistentClient(path=str(directory))
        self.collection=self.client.get_or_create_collection(collection,metadata={"hnsw:space":"cosine"})
    def upsert(self,ids:list[str],documents:list[str],metadatas:list[dict],embeddings:list[list[float]]) -> None:
        # Comentario V1 - Insere ou atualiza registros (chunks com embeddings) na coleção ChromaDB
        self.collection.upsert(ids=ids,documents=documents,metadatas=metadatas,embeddings=embeddings)
    def query(self,embedding:list[float],top_k:int=5,where:dict|None=None) -> list[dict]:
        # Comentario V1 - Consulta Chrome com filtro de metadados e retorna top-k resultados com similaridade
        # Comentario V1 - Executa busca no ChromaDB com embedding de query e opcionalmente filtra por metadados
        result=self.collection.query(query_embeddings=[embedding],n_results=top_k,where=where)
        rows=[]
        # Comentario V1 - Itera sobre documentos recuperados (primeiro elemento contém lista de docs)
        for i,doc in enumerate((result.get("documents") or [[]])[0]):
            # Comentario V1 - Constrói dicionário com conteúdo, metadados e calcula similaridade (1 - distância euclidiana normalizada)
            rows.append({"conteudo":doc,"metadata":result["metadatas"][0][i],"distancia":result["distances"][0][i],"similaridade":1-float(result["distances"][0][i])})
        # Comentario V1 - Retorna lista de resultados ordenados por similaridade (já em ordem decrescente do ChromaDB)
        return rows
