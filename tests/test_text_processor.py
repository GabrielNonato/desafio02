# Comentario V1 - Testes de processamento de texto: chunking com sobreposição e remoção de stopwords
from pathlib import Path

from src.pdf_processor import save_extracted_text
from src.text_processor import split_chunks, preprocess


def test_chunks_have_overlap_and_limit():
    # Comentario V1 - Verifica que chunks respeitam tamanho máximo e possuem sobreposição entre eles
    chunks=split_chunks("texto de exemplo "*100,size=120,overlap=20)
    assert len(chunks)>1 and all(len(c)<=120 for c in chunks)


def test_preprocess_removes_common_words():
    # Comentario V1 - Confirma que stopwords comuns em português são removidas durante pré-processamento
    assert "para" not in preprocess("A senha para o ambiente virtual")


def test_save_extracted_text_creates_txt_file(tmp_path):
    # Comentario V1 - Verifica que o texto extraído de um PDF é salvo em um arquivo .txt correspondente
    pdf_path=tmp_path/"arquivo.pdf"
    pdf_path.write_bytes(b"fake")
    txt_path=save_extracted_text(pdf_path,"texto extraído do pdf")
    assert txt_path.exists()
    assert txt_path.read_text(encoding="utf-8") == "texto extraído do pdf"
    assert txt_path.suffix == ".txt"
