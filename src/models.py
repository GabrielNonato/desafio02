"""Comentario V1 - Modelos SQLAlchemy do domínio - define tabelas de Documentos, Atendimentos, Chunks e Erros de processamento."""
from __future__ import annotations
from datetime import datetime, date
from sqlalchemy import String, Text, Integer, Float, Date, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

class Base(DeclarativeBase):
    pass

class Documento(Base):
    # Comentario V1 - Tabela de documentos: rastreia PDFs processados, metadados e método de extração utilizado
    __tablename__ = "documentos"
    # Comentario V1 - Identificador único do documento
    id: Mapped[int] = mapped_column(primary_key=True)
    # Comentario V1 - Nome do arquivo PDF
    nome_arquivo: Mapped[str] = mapped_column(String(255), unique=True)
    # Comentario V1 - Hash SHA256 para detectar duplicata de arquivos
    hash_sha256: Mapped[str] = mapped_column(String(64), unique=True)
    # Comentario V1 - Total de páginas no documento
    total_paginas: Mapped[int] = mapped_column(Integer)
    # Comentario V1 - Método predominante de extração: extracao_direta ou ocr
    metodo: Mapped[str] = mapped_column(String(30))
    # Comentario V1 - Timestamp de quando o documento foi processado
    processado_em: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    # Comentario V1 - Relação com atendimentos deste documento (um-para-muitos)
    atendimentos: Mapped[list["Atendimento"]] = relationship(back_populates="documento", cascade="all, delete-orphan")

class Atendimento(Base):
    # Comentario V1 - Tabela principal de atendimentos: armazena registros extraídos, validados e classificados de solicitantes
    __tablename__ = "atendimentos"
    # Comentario V1 - Constraint de unicidade do protocolo
    __table_args__ = (UniqueConstraint("protocolo", name="uq_atendimento_protocolo"),)
    # Comentario V1 - Identificador único do atendimento
    id: Mapped[int] = mapped_column(primary_key=True)
    # Comentario V1 - Chave estrangeira para documento de origem
    documento_id: Mapped[int] = mapped_column(ForeignKey("documentos.id"))
    # Comentario V1 - Número da página dentro do documento
    pagina: Mapped[int] = mapped_column(Integer)
    # Comentario V1 - Protocolo único do atendimento (formato AT-###)
    protocolo: Mapped[str] = mapped_column(String(30))
    # Comentario V1 - Data do atendimento (opcional)
    data: Mapped[date | None] = mapped_column(Date, nullable=True)
    # Comentario V1 - Nome de quem solicitou o atendimento
    solicitante: Mapped[str | None] = mapped_column(String(160), nullable=True)
    # Comentario V1 - Email do solicitante
    email: Mapped[str | None] = mapped_column(String(180), nullable=True)
    # Comentario V1 - Categoria normalizada do atendimento (ex: Python e bibliotecas)
    categoria: Mapped[str | None] = mapped_column(String(100), nullable=True)
    # Comentario V1 - Descrição do problema relatado
    descricao: Mapped[str | None] = mapped_column(Text, nullable=True)
    # Comentario V1 - Solução fornecida
    solucao: Mapped[str | None] = mapped_column(Text, nullable=True)
    # Comentario V1 - Tempo de atendimento em minutos
    tempo_minutos: Mapped[float | None] = mapped_column(Float, nullable=True)
    # Comentario V1 - Status do atendimento (Concluido, Pendente, Em atendimento)
    status: Mapped[str | None] = mapped_column(String(40), nullable=True)
    # Comentario V1 - CEP do local do solicitante
    cep: Mapped[str | None] = mapped_column(String(10), nullable=True)
    # Comentario V1 - Município do solicitante (pode ser preenchido via API ViaCEP)
    municipio: Mapped[str | None] = mapped_column(String(100), nullable=True)
    # Comentario V1 - Unidade federativa do solicitante
    uf: Mapped[str | None] = mapped_column(String(2), nullable=True)
    # Comentario V1 - Classificação do registro: valido, incompleto, invalido ou duplicado
    classificacao: Mapped[str] = mapped_column(String(30), default="valido")
    # Comentario V1 - Lista de motivos de invalidade (separada por ponto-vírgula)
    motivos: Mapped[str | None] = mapped_column(Text, nullable=True)
    # Comentario V1 - Texto original extraído do PDF
    texto_original: Mapped[str] = mapped_column(Text)
    # Comentario V1 - Texto limpo e preprocessado para indexação
    texto_limpo: Mapped[str] = mapped_column(Text)
    # Comentario V1 - Relação com documento de origem
    documento: Mapped[Documento] = relationship(back_populates="atendimentos")
    # Comentario V1 - Relação com chunks para indexação vetorial
    chunks: Mapped[list["Chunk"]] = relationship(back_populates="atendimento", cascade="all, delete-orphan")

class Chunk(Base):
    # Comentario V1 - Tabela de chunks de texto: armazena fragmentos de atendimentos com metadados para índice vetorial
    __tablename__ = "chunks"
    # Comentario V1 - Identificador único do chunk
    id: Mapped[int] = mapped_column(primary_key=True)
    # Comentario V1 - Chave estrangeira para atendimento de origem
    atendimento_id: Mapped[int] = mapped_column(ForeignKey("atendimentos.id"))
    # Comentario V1 - Chave estrangeira para documento de origem
    documento_id: Mapped[int] = mapped_column(ForeignKey("documentos.id"))
    # Comentario V1 - Número da página
    pagina: Mapped[int] = mapped_column(Integer)
    # Comentario V1 - Índice sequencial do chunk dentro do atendimento
    indice: Mapped[int] = mapped_column(Integer)
    # Comentario V1 - Conteúdo de texto do chunk (será indexado com embedding)
    conteudo: Mapped[str] = mapped_column(Text)
    # Comentario V1 - Metadados em JSON (protocolo, documento, página, categoria)
    metadata_json: Mapped[str] = mapped_column(Text)
    # Comentario V1 - Relação com atendimento de origem
    atendimento: Mapped[Atendimento] = relationship(back_populates="chunks")
    atendimento_id: Mapped[int] = mapped_column(ForeignKey("atendimentos.id"))
    documento_id: Mapped[int] = mapped_column(ForeignKey("documentos.id"))
    pagina: Mapped[int] = mapped_column(Integer)
    indice: Mapped[int] = mapped_column(Integer)
    conteudo: Mapped[str] = mapped_column(Text)
    metadata_json: Mapped[str] = mapped_column(Text)
    atendimento: Mapped[Atendimento] = relationship(back_populates="chunks")

class ErroProcessamento(Base):
    # Comentario V1 - Tabela de rastreamento de erros: registra falhas em OCR, dedução, validação para auditoría
    __tablename__ = "erros_processamento"
    id: Mapped[int] = mapped_column(primary_key=True)
    documento_id: Mapped[int | None] = mapped_column(ForeignKey("documentos.id"), nullable=True)
    pagina: Mapped[int | None] = mapped_column(Integer, nullable=True)
    etapa: Mapped[str] = mapped_column(String(80))
    tipo: Mapped[str] = mapped_column(String(80))
    mensagem: Mapped[str] = mapped_column(Text)
    registrado_em: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
