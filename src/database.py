"""Comentario V1 - Criação do banco, sessão e operações CRUD - gerencia conexão SQLAlchemy e transações com o banco de dados."""
from __future__ import annotations
from contextlib import contextmanager
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker, Session
from .models import Base, Atendimento

def create_session_factory(url: str):
    # Comentario V1 - Cria factory de sessões SQLAlchemy e inicializa tabelas do banco de dados
    # Comentario V1 - Cria engine de conexão com future mode para compatibilidade
    engine = create_engine(url, future=True)
    # Comentario V1 - Cria todas as tabelas definidas em Base.metadata (se não existirem)
    Base.metadata.create_all(engine)
    # Comentario V1 - Retorna factory configurada para criar sessões sem expirar objetos após commit
    return sessionmaker(bind=engine, expire_on_commit=False)

@contextmanager
def session_scope(factory):
    # Comentario V1 - Context manager que fornece sessão SQLAlchemy com commit automático e rollback em exceções
    # Comentario V1 - Cria nova sessão a partir da factory
    session: Session = factory()
    try:
        # Comentario V1 - Fornece sessão para código dentro do bloco with
        yield session
        # Comentario V1 - Após saída normal do bloco, faz commit de todas as mudanças
        session.commit()
    except Exception:
        # Comentario V1 - Se ocorrer exceção, desfaz todas as mudanças não confirmadas
        session.rollback()
        raise
    finally:
        # Comentario V1 - Sempre fecha a sessão, mesmo que ocorra erro
        session.close()

def find_by_protocol(session: Session, protocol: str) -> Atendimento | None:
    # Comentario V1 - Busca atendimento por protocolo, retorna None se não encontrado
    return session.scalar(select(Atendimento).where(Atendimento.protocolo == protocol))

def delete_by_protocol(session: Session, protocol: str) -> bool:
    # Comentario V1 - Deleta atendimento por protocolo, retorna True se deletado, False se não encontrado
    item = find_by_protocol(session, protocol)
    if not item:
        return False
    session.delete(item)
    return True
