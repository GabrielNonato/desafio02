# Comentario V1 - Testes de validação de registros de atendimento e normalização de categorias
from src.pipeline import split_records
from src.validation import validate_record, normalize_category

CATS={"categorias_oficiais":[{"nome":"Python e bibliotecas","variacoes":["python","pip"]}]}

def test_valid_record():
    # Comentario V1 - Valida registro correto com todos os campos obrigatórios e formato adequado
    record={"protocolo":"AT-001","data":"01/08/2026","email":"a@b.com","cep":"78200-000","categoria":"pip","tempo_minutos":"20","solicitante":"Ana","descricao":"Erro"}
    classification,reasons,normalized=validate_record(record,CATS)
    assert classification=="valido" and not reasons
    assert normalized["categoria_normalizada"]=="Python e bibliotecas"

def test_invalid_email():
    # Comentario V1 - Valida que email inválido é detectado e registrado na lista de motivos
    record={"protocolo":"AT-001","data":"01/08/2026","email":"invalido","cep":"78200-000","categoria":"python","tempo_minutos":"20","solicitante":"Ana","descricao":"Erro"}
    assert "email_invalido" in validate_record(record,CATS)[1]


def test_ocr_protocol_variants_are_normalized():
    # Comentario V1 - Simula texto OCR com protocolo quebrado em ATO51 e etiqueta em inglês
    record={"protocolo":"ATO51","data":"17/08/2026","email":"henrique.oliveira@aluno.exemplo.br","cep":"78205-160","categoria":"python","tempo_minutos":"53","solicitante":"Henrique Oliveira Luz","descricao":"Erro no terminal"}
    classification,reasons,normalized=validate_record(record,CATS)
    assert classification == "valido"
    assert normalized["protocolo"] == "AT-051"
    assert "protocolo_invalido" not in reasons


def test_split_records_accepts_ocr_label_variants():
    # Comentario V1 - Verifica que rótulos de protocolo quebrados em OCR continuam gerando registros separados
    page_text = (
        "Protocol ATO51 Data 2026-08-17 Solicitante Henrique Oliveira Luz Email henrique.oliveira@aluno.exemplo.br "
        "Categoria python Status Concluido CEP 78205-160 Tempo 53 min Problema terminal nao reconhecido Solucao Foi ajustado "
        "Observacoes Registro 051 "
        "Protocol ATO52 Data 09/07/2026 Solicitante Otavia Cardoso Leal Email otavia.cardoso@aluno.exemplo.br "
        "Categoria python Status Pendente CEP 78110-000 Tempo 60 min Problema CSV desorganizado Solucao Ainda em andamento Observacoes Registro 052"
    )
    records = split_records(page_text)
    assert len(records) == 2
    assert "ATO51" in records[0] or "AT-051" in records[0]
    assert "ATO52" in records[1] or "AT-052" in records[1]
