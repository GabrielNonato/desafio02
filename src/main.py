"""Comentario V1 - Entrada de linha de comando - módulo principal que orquestra a execução do pipeline de processamento via CLI."""
from __future__ import annotations
import argparse
from .config import load_config
from .pipeline import process_all
from .indexer import build_index, semantic_query
from .rag import answer

def main():
    # Comentario V1 - Função principal que processa argumentos CLI e executa o pipeline ou consultas semânticas
    parser=argparse.ArgumentParser(description="Processa e consulta os atendimentos")
    # Comentario V1 - Define argumentos opcionais: --indexar para construir índice vetorial, --pergunta para consulta semântica, --top-k para limitar resultados
    parser.add_argument("--indexar",action="store_true"); parser.add_argument("--pergunta"); parser.add_argument("--top-k",type=int,default=5)
    # Comentario V1 - Faz parse dos argumentos e carrega configuração do arquivo config.json
    args=parser.parse_args(); cfg=load_config()
    # Comentario V1 - Executa pipeline completo de processamento (OCR, validação, armazenamento) e armazena resultado em DataFrame
    df=process_all(cfg); print(f"Registros encontrados: {len(df)}")
    # Comentario V1 - Se flag --indexar ativa, constrói índice vetorial com embeddings dos chunks
    if args.indexar: print(f"Chunks indexados: {build_index(cfg)}")
    # Comentario V1 - Se pergunta foi fornecida, faz busca semântica e gera resposta via RAG ou modo local
    if args.pergunta:
        sources=semantic_query(cfg,args.pergunta,args.top_k); print(answer(args.pergunta,sources))

if __name__=="__main__": main()
