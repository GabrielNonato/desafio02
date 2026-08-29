"""Comentario V1 - Carregamento centralizado das configurações - gerencia variáveis de ambiente e arquivo config.json."""
from __future__ import annotations
from pathlib import Path
import json
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]

def load_config(path: str | Path | None = None) -> dict:
    # Comentario V1 - Carrega configurações de arquivo JSON e variáveis de ambiente (.env)
    # Comentario V1 - Carrega variáveis de ambiente do arquivo .env se existir
    load_dotenv(ROOT / ".env")
    # Comentario V1 - Usa arquivo config.json ou caminho fornecido
    target = Path(path) if path else ROOT / "config.json"
    # Comentario V1 - Abre e parseia arquivo JSON em encoding UTF-8
    with target.open(encoding="utf-8") as stream:
        cfg = json.load(stream)
    # Comentario V1 - Adiciona raiz do projeto ao dicionário de configuração
    cfg["_root"] = str(ROOT)
    # Comentario V1 - Retorna dicionário com configurações
    return cfg

def resolve(root: str | Path, relative: str | Path) -> Path:
    # Comentario V1 - Resolve caminhos relativos considerando o diretório raiz do projeto
    path = Path(relative)
    return path if path.is_absolute() else Path(root) / path
