"""Comentario V1 - Orquestração do processamento ponta a ponta - coordena extração de PDFs, OCR, validação, armazenamento e análise de dados."""
from __future__ import annotations
from pathlib import Path
from hashlib import sha256
import json, logging, re
import pandas as pd
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from .config import resolve
from .database import create_session_factory, session_scope, find_by_protocol
from .models import Documento, Atendimento, Chunk, ErroProcessamento
from .pdf_processor import extract_pdf_pages, save_extracted_text
from .ocr_processor import ocr_page
from .validation import extract_fields, validate_record, clean_text
from .text_processor import preprocess, split_chunks, metadata_json
from .analytics import export_results, generate_charts

def configure_logging(path: Path):
    # Comentario V1 - Configura logging em arquivo e console para rastrear processamento e erros
    # Comentario V1 - Cria diretórios pai se não existirem
    path.parent.mkdir(parents=True,exist_ok=True)
    # Comentario V1 - Configura logging com formato timestamp, nível e mensagem
    logging.basicConfig(level=logging.INFO,format="%(asctime)s %(levelname)s %(message)s",handlers=[logging.FileHandler(path,encoding="utf-8"),logging.StreamHandler()])

def split_records(page_text: str) -> list[str]:
    # Comentario V1 - Divide texto de página em registros individuais separando por rótulos de protocolo corrompidos por OCR
    clean=clean_text(page_text)
    pattern=r"(?=(?:Protocol(?:b)?|Protocolo)\s*(?:AT[-\s]?\d{2,3}|AT[O0S]?\d{2,3}|AT\d{2,3}|PROTOCOLO\?))"
    parts=re.split(pattern,clean,flags=re.I)
    return [p.strip() for p in parts if re.search(r"(?:Protocol(?:b)?|Protocolo)\s+",p,re.I)]

def process_all(cfg: dict) -> pd.DataFrame:
    # Comentario V1 - Função principal que orquestra todo o pipeline: processa PDFs, executa OCR, valida registros, armazena no BD e gera análises
    # Comentario V1 - Obtém raiz do projeto, diretório de saída e carrega categorias oficiais
    root=Path(cfg["_root"]); output=resolve(root,cfg["saida"]["diretorio"]); output.mkdir(parents=True,exist_ok=True)
    # Comentario V1 - Configura logging para rastrear processamento
    configure_logging(output/cfg["saida"]["log"])
    # Comentario V1 - Carrega arquivo JSON com categorias oficiais e suas variações
    categories=json.loads((root/"data"/"auxiliares"/"categorias.json").read_text(encoding="utf-8"))
    # Comentario V1 - Obtém URL do banco de dados e normaliza caminho relativo para SQLite
    db_url=cfg["banco"]["url"]
    if db_url.startswith("sqlite:/// "): db_url="sqlite:///"+str(root/db_url.removeprefix("sqlite:/// "))
    elif db_url.startswith("sqlite:///") and not db_url.startswith("sqlite:////"): db_url="sqlite:///"+str(root/db_url[10:])
    # Comentario V1 - Cria factory de sessões SQLAlchemy
    factory=create_session_factory(db_url)
    # Comentario V1 - Obtém diretório de PDFs e inicializa lista para armazenar registros processados
    pdf_dir=resolve(root,cfg["entrada"]["diretorio_pdfs"]); rows=[]
    # Comentario V1 - Inicia transação com banco de dados
    with session_scope(factory) as session:
        # Comentario V1 - Itera sobre PDFs encontrados no diretório (ordenados alfabeticamente)
        for pdf in sorted(pdf_dir.glob(cfg["entrada"]["padrao"])):
            # Comentario V1 - Calcula hash SHA256 do PDF para detectar duplicatas e extrai dados de todas as páginas
            digest=sha256(pdf.read_bytes()).hexdigest(); page_data=extract_pdf_pages(pdf,cfg["ocr"]["min_caracteres_extracao_direta"])
            # Comentario V1 - Se PDF já foi processado (mesmo hash), pula para próximo
            if session.scalar(select(Documento).where(Documento.hash_sha256==digest)):
                logging.info("Documento já processado; ignorando: %s",pdf.name)
                continue
            # Comentario V1 - Determina método predominante: OCR se todas as páginas precisam OCR, senão extração direta
            method="ocr" if all(p["metodo"]=="ocr_pendente" for p in page_data) else "extracao_direta"
            # Comentario V1 - Cria registro Documento no banco com metadados do PDF
            doc=Documento(nome_arquivo=pdf.name,hash_sha256=digest,total_paginas=len(page_data),metodo=method); session.add(doc); session.flush()
            extracted_text=[]
            # Comentario V1 - Itera sobre cada página do PDF
            for page in page_data:
                # Comentario V1 - Obtém texto da página (já extraído na fase anterior)
                text=page["texto"]
                # Comentario V1 - Se página precisa OCR, executa Tesseract
                if page["metodo"]=="ocr_pendente":
                    try:
                        # Comentario V1 - Aplica OCR na página e atualiza método
                        text=ocr_page(pdf,page["pagina"],cfg["ocr"]["dpi"],cfg["ocr"]["idioma"]); page["metodo"]="ocr"
                    except Exception as exc:
                        # Comentario V1 - Se OCR falhar, registra erro no banco e continua com próxima página
                        session.add(ErroProcessamento(documento_id=doc.id,pagina=page["pagina"],etapa="ocr",tipo=type(exc).__name__,mensagem=str(exc))); logging.exception("OCR falhou: %s p.%s",pdf.name,page["pagina"]); continue
                if text.strip():
                    extracted_text.append(text.strip())
                # Comentario V1 - Divide página em registros individuais (por protocolo)
                for raw in split_records(text):
                    # Comentario V1 - Extrai campos do registro usando regex e valida contra regras
                    fields=extract_fields(raw); classification,reasons,normalized=validate_record(fields,categories)
                    # Comentario V1 - Obtém protocolo normalizado ou gera ID único para registro inválido
                    protocol=normalized.get("protocolo") or f"INVALIDO-{doc.id}-{page['pagina']}-{len(rows)+1}"
                    # Comentario V1 - Verifica se protocolo já existe no banco (duplicata)
                    if find_by_protocol(session,protocol): classification="duplicado"; reasons.append("protocolo_duplicado")
                    # Comentario V1 - Cria dicionário com todos os dados do registro para DataFrame
                    row={**fields,"protocolo":protocol,"categoria":normalized.get("categoria_normalizada") or fields.get("categoria"),"data":normalized.get("data_obj"),"tempo_minutos":normalized.get("tempo_obj"),"classificacao":classification,"motivos":";".join(reasons),"documento":pdf.name,"pagina":page["pagina"],"metodo":page["metodo"]}
                    # Comentario V1 - Adiciona linha ao resultado
                    rows.append(row)
                    # Comentario V1 - Se registro é duplicado, registra erro e não armazena no BD
                    if classification=="duplicado":
                        session.add(ErroProcessamento(documento_id=doc.id,pagina=page["pagina"],etapa="deduplicacao",tipo="Duplicidade",mensagem=protocol)); continue
                    # Comentario V1 - Se registro não é duplicado, cria objeto Atendimento com dados normalizados
                    item=Atendimento(documento_id=doc.id,pagina=page["pagina"],protocolo=protocol,data=normalized.get("data_obj"),solicitante=fields.get("solicitante"),email=fields.get("email"),categoria=row["categoria"],descricao=fields.get("descricao"),solucao=fields.get("solucao"),tempo_minutos=normalized.get("tempo_obj"),status=fields.get("status"),cep=fields.get("cep"),municipio=None,uf=None,classificacao=classification,motivos=row["motivos"],texto_original=raw,texto_limpo=preprocess(raw))
                    # Comentario V1 - Salva atendimento no banco e obtém ID gerado
                    session.add(item); session.flush()
                    # Comentario V1 - Divide conteúdo em chunks para indexação vetorial (com sobreposição)
                    for idx,content in enumerate(split_chunks(raw,cfg["embeddings"]["tamanho_chunk"],cfg["embeddings"]["sobreposicao"])):
                        # Comentario V1 - Prepara metadados para chunk: protocolo, documento, página e categoria
                        meta={"protocolo":protocol,"documento":pdf.name,"pagina":page["pagina"],"categoria":row["categoria"] or ""}
                        # Comentario V1 - Cria registro Chunk no banco com conteúdo e metadados em JSON
                        session.add(Chunk(atendimento_id=item.id,documento_id=doc.id,pagina=page["pagina"],indice=idx,conteudo=content,metadata_json=metadata_json(**meta)))
            if extracted_text:
                save_extracted_text(pdf, "\n\n".join(extracted_text))
    # Comentario V1 - Converte lista de registros em DataFrame pandas
    df=pd.DataFrame(rows)
    # Comentario V1 - Se há registros, exporta para CSV, gera indicadores em JSON e cria gráficos
    if not df.empty:
        export_results(df,output,cfg["saida"]["csv"],cfg["saida"]["indicadores"]); generate_charts(df,resolve(root,cfg["saida"]["graficos"]))
    # Comentario V1 - Retorna DataFrame com todos os registros processados
    return df
