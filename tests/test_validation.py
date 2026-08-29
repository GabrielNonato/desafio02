# Comentario V1 - Testes de validação de registros de atendimento e normalização de categorias
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
