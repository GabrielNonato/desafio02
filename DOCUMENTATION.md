# Comentario V1 - Documentação do Projeto FIC_DEV - Sistema de Processamento e Consulta de Atendimentos

## Visão Geral
Este projeto implementa um sistema completo de processamento de documentos PDF contendo atendimentos, com extração de dados via OCR, validação, armazenamento em banco de dados SQL e busca semântica (RAG) usando embeddings e ChromaDB.

## Arquitetura do Projeto

### Fluxo Principal de Processamento
1. **Entrada**: PDFs com registros de atendimento localizados em `data/pdfs/`
2. **Extração**: Tentativa de extração de texto direto; páginas com pouco texto são marcadas para OCR
3. **OCR**: Processamento com Tesseract das páginas que não tiveram sucesso na extração
4. **Segmentação**: Divisão do texto em registros individuais (por protocolo)
5. **Validação**: Validação de campos obrigatórios e normalização de dados
6. **Armazenamento**: Persistência em SQLite com tabelas de documentos, atendimentos, chunks e erros
7. **Indexação**: Geração de embeddings e criação de índice vetorial no ChromaDB
8. **Consulta**: Buscas semânticas com síntese automática via OpenAI (ou modo local)

## Estrutura de Arquivos

### Configuração
- **config.json**: Comentario V1 - Arquivo central de configuração com caminhos de entrada/saída, parâmetros de OCR, embeddings, banco de dados e API
- **requirements.txt**: Comentario V1 - Lista de dependências Python incluindo FastAPI, SQLAlchemy, Tesseract, ChromaDB, LangChain e Streamlit
- **.env**: Variáveis de ambiente (ex: OPENAI_API_KEY) carregadas automaticamente

### Código-fonte (src/)
- **main.py**: Comentario V1 - Interface CLI para executar pipeline ou consultas semânticas
- **api.py**: Comentario V1 - API REST FastAPI com endpoints /health e /ask
- **app_streamlit.py**: Comentario V1 - Interface web de consulta com Streamlit
- **config.py**: Comentario V1 - Carregamento centralizado de configurações
- **pipeline.py**: Comentario V1 - Orquestração principal do processamento de documentos
- **pdf_processor.py**: Comentario V1 - Extração de texto de PDFs usando pypdf
- **ocr_processor.py**: Comentario V1 - OCR com Tesseract para páginas sem texto extraível
- **validation.py**: Comentario V1 - Validação e normalização de campos de atendimento
- **text_processor.py**: Comentario V1 - Limpeza, tokenização e chunking de texto
- **database.py**: Comentario V1 - Gerenciamento de sessões SQLAlchemy e operações CRUD
- **models.py**: Comentario V1 - Modelos SQLAlchemy: Documento, Atendimento, Chunk, ErroProcessamento
- **embeddings.py**: Comentario V1 - Geração de embeddings com SentenceTransformer
- **indexer.py**: Comentario V1 - Construção de índices vetoriais e buscas semânticas
- **rag.py**: Comentario V1 - Pipeline RAG com fallback local (sem OpenAI)
- **vector_store.py**: Comentario V1 - Abstração para operações com ChromaDB
- **analytics.py**: Comentario V1 - Geração de indicadores, exportação de dados e criação de gráficos
- **cep_client.py**: Comentario V1 - Integração com API ViaCEP para consulta de CEP

### Testes (tests/)
- **test_validation.py**: Comentario V1 - Testes de validação e normalização de registros
- **test_text_processor.py**: Comentario V1 - Testes de chunking com sobreposição e preprocessamento
- **test_api.py**: Comentario V1 - Testes de endpoints HTTP da API

## Configuração (config.json)

### Comentario V1 - Campos Principais

**entrada**: Comentario V1 - Diretório de entrada e padrão de busca de PDFs
- `diretorio_pdfs`: Caminho para pasta com PDFs
- `padrao`: Padrão glob para arquivos (ex: *.pdf)

**saida**: Comentario V1 - Diretório e nomes de arquivos de saída
- `diretorio`: Pasta para resultados
- `csv`: Nome do arquivo CSV com atendimentos processados
- `indicadores`: Nome do arquivo JSON com estatísticas
- `log`: Arquivo de log do processamento
- `graficos`: Pasta para gráficos em PNG

**banco**: Comentario V1 - Configuração do banco de dados SQLite
- `url`: URL de conexão (ex: sqlite:///database/atendimentos.db)

**ocr**: Comentario V1 - Parâmetros de processamento OCR
- `idioma`: Idioma para Tesseract (ex: por para português)
- `dpi`: Resolução de rasterização do PDF
- `min_caracteres_extracao_direta`: Threshold para classificar página como com/sem OCR

**embeddings**: Comentario V1 - Configuração de embeddings e chunking
- `modelo`: Nome do modelo SentenceTransformer multilíngue
- `tamanho_chunk`: Tamanho máximo de cada chunk em caracteres
- `sobreposicao`: Número de caracteres de overlap entre chunks

**chromadb**: Comentario V1 - Configuração do armazenamento vetorial
- `diretorio`: Pasta para dados persistidos do ChromaDB
- `colecao`: Nome da coleção de embeddings

**api**: Comentario V1 - Configuração de APIs externas
- `cep_base_url`: URL base da API ViaCEP
- `timeout_segundos`: Timeout para requisições HTTP

**rag**: Comentario V1 - Configuração do sistema RAG
- `top_k`: Número de chunks a recuperar em buscas semânticas
- `modo_sem_chave`: Modo de operação quando OpenAI key não está presente

## Como Usar

### Comentario V1 - Linha de Comando
```bash
# Processar todos os PDFs
python -m src.main

# Indexar chunks no ChromaDB
python -m src.main --indexar

# Consultar sistema
python -m src.main --pergunta "Qual é o problema mais comum?" --top-k 3
```

### Comentario V1 - API REST
```bash
# Iniciar servidor
uvicorn src.api:app --reload

# Health check
curl http://localhost:8000/health

# Consultar
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"pergunta": "Problemas com Python", "top_k": 5}'
```

### Comentario V1 - Interface Streamlit
```bash
streamlit run src/app_streamlit.py
```

### Comentario V1 - Testes
```bash
pytest tests/
```

## Modelos de Dados

### Comentario V1 - Tabelas do Banco de Dados

**documentos**: Comentario V1 - Rastreia cada PDF processado
- id (PK), nome_arquivo, hash_sha256, total_paginas, metodo (extracao_direta/ocr), processado_em

**atendimentos**: Comentario V1 - Registros individuais de atendimento
- id (PK), documento_id (FK), pagina, protocolo (UNIQUE), data, solicitante, email, categoria, descricao, solucao, tempo_minutos, status, cep, municipio, uf, classificacao (valido/incompleto/invalido/duplicado), motivos, texto_original, texto_limpo

**chunks**: Comentario V1 - Segmentos de texto para indexação vetorial
- id (PK), atendimento_id (FK), documento_id (FK), pagina, indice, conteudo, metadata_json

**erros_processamento**: Comentario V1 - Registro de falhas durante processamento
- id (PK), documento_id (FK), pagina, etapa (ocr/deduplicacao), tipo, mensagem, registrado_em

## Classificações de Registros

### Comentario V1 - Estados de Validação
- **valido**: Todos os campos obrigatórios preenchidos com valores válidos
- **incompleto**: Faltam campos obrigatórios (solicitante, descricao)
- **invalido**: Campos com formato inválido (email, CEP, data, categoria, tempo)
- **duplicado**: Protocolo já existe no banco de dados

## Variáveis de Ambiente

### Comentario V1 - Configurações Opcionais
- `OPENAI_API_KEY`: Chave da API OpenAI para síntese de respostas (opcional, sem ela usa modo local)
- `OPENAI_MODEL`: Modelo OpenAI a usar (padrão: gpt-4.1-mini)

## Dependências Principais

### Comentario V1 - Bibliotecas Utilizadas
- **FastAPI/Uvicorn**: Framework web e servidor
- **SQLAlchemy**: ORM para banco de dados
- **ChromaDB**: Armazenamento de vetores e busca semântica
- **SentenceTransformers**: Geração de embeddings multilíngues
- **Pytesseract/pdf2image**: OCR de documentos
- **Pandas/NumPy**: Processamento de dados
- **Matplotlib**: Geração de gráficos
- **Streamlit**: Interface web
- **LangChain/LangChain-OpenAI**: Pipeline RAG
- **Pytest**: Framework de testes

## Notas de Implementação

### Comentario V1 - Características Importantes
1. **Tolerância a Falhas**: OCR falha graciosamente; validação classifica registros em vez de rejeitar
2. **Deduplicação**: Detecta protocolos duplicados automaticamente
3. **Modo Offline**: Sistema funciona completamente sem chave OpenAI (modo recuperação_local)
4. **Logging Estruturado**: Rastreia todas as etapas de processamento
5. **Chunking com Overlap**: Mantém contexto ao dividir textos grandes
6. **Busca Multilíngue**: Embeddings treinados em múltiplos idiomas

---
**Versão**: 1.0.0
**Última Atualização**: 2026-08-29
