"""Comentario V1 - Cliente tolerante a falhas para consulta de CEP - integra-se à API ViaCEP para enriquecimento de dados geográficos."""
from __future__ import annotations
import requests

def lookup_cep(cep: str, base_url: str, timeout: int=8) -> dict | None:
    # Comentario V1 - Consulta API ViaCEP e retorna município, UF e logradouro ou None se falhar
    # Comentario V1 - Extrai apenas dígitos do CEP (remove hífens e outros caracteres)
    digits="".join(ch for ch in cep if ch.isdigit())
    # Comentario V1 - Valida se CEP tem 8 dígitos, retorna None se inválido
    if len(digits)!=8: return None
    try:
        # Comentario V1 - Faz requisição GET para API ViaCEP com timeout configurável
        response=requests.get(f"{base_url.rstrip('/')}/{digits}/json/",timeout=timeout,headers={"User-Agent":"fic-dev-desafio/1.0"})
        # Comentario V1 - Levanta exceção se status HTTP não for 2xx
        response.raise_for_status()
        # Comentario V1 - Parseia resposta JSON da API
        data=response.json()
        # Comentario V1 - Verifica campo "erro" que indica CEP não encontrado
        if data.get("erro"): return None
        # Comentario V1 - Extrai dados de interesse (município, UF, logradouro) da resposta
        return {"municipio":data.get("localidade"),"uf":data.get("uf"),"logradouro":data.get("logradouro")}
    # Comentario V1 - Retorna None em caso de erro de rede ou parsing de JSON
    except (requests.RequestException,ValueError):
        return None
