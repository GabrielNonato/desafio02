"""Comentario V1 - Limpeza linguística e divisão de texto em chunks - normaliza, lematiza e segmenta textos com sobreposição."""
from __future__ import annotations
import json, re, unicodedata

# Comentario V1 - Lista de stopwords em português para remover durante processamento de texto
STOPWORDS={"a","o","as","os","de","da","do","das","dos","e","em","um","uma","para","por","com","que","no","na"}

def normalize_text(text: str) -> str:
    # Comentario V1 - Remove caracteres nulos e normaliza espaços em branco do texto
    return re.sub(r"\s+"," ",text.replace("\x00"," ")).strip()

def tokens(text: str) -> list[str]:
    # Comentario V1 - Tokeniza e normaliza texto: remove acentos, converte para minúscula e filtra stopwords
    plain=unicodedata.normalize("NFKD",text.lower()).encode("ascii","ignore").decode()
    return [t for t in re.findall(r"[a-z0-9]+",plain) if t not in STOPWORDS]

def lemma_light(token: str) -> str:
    # Comentario V1 - Lematização leve: remove sufixos comuns (mente, coes, ando, ado, s, etc)
    for suffix in ("mente","coes","cao","ando","endo","idos","adas","ado","ida","s"):
        if token.endswith(suffix) and len(token)>len(suffix)+3: return token[:-len(suffix)]
    return token

def preprocess(text: str) -> str:
    # Comentario V1 - Processa texto aplicando tokenização, remoção de stopwords e lematização leve
    return " ".join(lemma_light(t) for t in tokens(text))

def split_chunks(text: str, size: int=500, overlap: int=80) -> list[str]:
    # Comentario V1 - Divide texto em chunks de tamanho fixo com sobreposição, mantendo limites em espaços
    # Comentario V1 - Normaliza o texto removendo caracteres especiais e espaços extras
    text=normalize_text(text)
    # Comentario V1 - Valida parâmetros: tamanho deve ser positivo, overlap não-negativo e menor que tamanho
    if size<=0 or overlap<0 or overlap>=size: raise ValueError("Parametros de chunk invalidos")
    chunks=[]; start=0
    # Comentario V1 - Itera criando chunks até alcançar fim do texto
    while start<len(text):
        # Comentario V1 - Define fim do chunk como posição atual + tamanho desejado, limitado ao comprimento total
        end=min(len(text),start+size)
        # Comentario V1 - Se não chegou ao fim, tenta quebrar em espaço em branco para não cortar palavras
        if end<len(text):
            # Comentario V1 - Busca espaço mais próximo do fim do chunk (no mínimo na metade)
            boundary=text.rfind(" ",start,end)
            # Comentario V1 - Se encontrou espaço válido, usa ele como limite
            if boundary>start+size//2: end=boundary
        # Comentario V1 - Adiciona chunk após remover espaços das extremidades
        chunks.append(text[start:end].strip())
        # Comentario V1 - Se chegou ao fim, interrompe
        if end>=len(text): break
        # Comentario V1 - Move posição inicial recuando pelo tamanho da sobreposição desejada
        start=end-overlap
    # Comentario V1 - Retorna apenas chunks não-vazios
    return [c for c in chunks if c]

def metadata_json(**kwargs) -> str:
    # Comentario V1 - Serializa dicionário de metadados em JSON preservando caracteres especiais
    return json.dumps(kwargs,ensure_ascii=False,sort_keys=True)
