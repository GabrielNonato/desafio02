"""Comentario V1 - OCR das páginas rasterizadas com dependências carregadas sob demanda - executa Tesseract em imagens de PDF para extração de texto."""
from __future__ import annotations
from pathlib import Path

def ocr_page(pdf_path: str | Path, page_number: int, dpi: int = 300, language: str = "por") -> str:
    # Comentario V1 - Converte página PDF em imagem e aplica OCR usando Tesseract com fallback para inglês em caso de erro
    try:
        # Comentario V1 - Importa bibliotecas de conversão PDF para imagem e OCR (lazy loading)
        from pdf2image import convert_from_path
        import pytesseract
    except ImportError as exc:
        # Comentario V1 - Se bibliotecas não estiverem instaladas, levanta erro indicando que são necessárias
        raise RuntimeError("Instale pdf2image e pytesseract para executar OCR") from exc
    # Comentario V1 - Converte página específica do PDF para imagem com resolução configurada (DPI)
    images=convert_from_path(str(pdf_path),dpi=dpi,first_page=page_number,last_page=page_number)
    # Comentario V1 - Se falhar na conversão, retorna string vazia
    if not images: return ""
    try:
        # Comentario V1 - Aplica OCR na imagem com idioma especificado (português por padrão)
        return pytesseract.image_to_string(images[0],lang=language)
    except pytesseract.TesseractError:
        # Comentario V1 - Se OCR falhar com idioma configurado, tenta novamente com inglês como fallback
        return pytesseract.image_to_string(images[0],lang="eng")
