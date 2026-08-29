"""Comentario V1 - Extração direta de texto e encaminhamento de páginas para OCR - processa PDFs e identifica páginas que precisam OCR."""
from __future__ import annotations
from pathlib import Path
from pypdf import PdfReader

def extract_pdf_pages(path: str | Path, min_chars: int = 40) -> list[dict]:
    # Comentario V1 - Extrai texto de cada página do PDF e classifica como extracao_direta ou ocr_pendente conforme quantidade de caracteres
    # Comentario V1 - Cria leitor PDF a partir do caminho fornecido
    reader=PdfReader(str(path)); pages=[]
    # Comentario V1 - Itera sobre cada página do PDF usando enumerate para rastrear número da página (começa em 1)
    for number,page in enumerate(reader.pages,1):
        # Comentario V1 - Extrai texto da página ou retorna string vazia se falhar
        text=(page.extract_text() or "").strip()
        # Comentario V1 - Classifica página: se tem mínimo de caracteres, marca como sucesso direto; senão marca para OCR
        pages.append({"pagina":number,"texto":text,"metodo":"extracao_direta" if len(text)>=min_chars else "ocr_pendente"})
    # Comentario V1 - Retorna lista de dicionários com metadados de cada página
    return pages
