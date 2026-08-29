"""Comentario V1 - Recuperação local e resposta RAG opcional com OpenAI/LangChain - implementa pipeline RAG com fallback local."""
from __future__ import annotations
import os

# Comentario V1 - Prompt do sistema que instrui o modelo a responder apenas com base no contexto recuperado
SYSTEM="Responda somente com base no contexto. Se a resposta não estiver sustentada, diga que não há informação suficiente. Cite os protocolos utilizados."

def local_answer(question:str,sources:list[dict]) -> dict:
    # Comentario V1 - Retorna resposta em modo local sem chamada a LLM, apenas listando fontes recuperadas
    return {"resposta":"Modo local: foram recuperados os trechos mais semelhantes. Configure OPENAI_API_KEY para gerar uma síntese.","modo":"recuperacao_local","pergunta":question,"fontes":sources}

def answer(question:str,sources:list[dict],model:str="gpt-4.1-mini") -> dict:
    # Comentario V1 - Gera resposta RAG usando LLM da OpenAI se disponível, com fallback para modo local
    # Comentario V1 - Se chave OpenAI não configurada, retorna resposta em modo local
    if not os.getenv("OPENAI_API_KEY"): return local_answer(question,sources)
    try:
        # Comentario V1 - Importa componentes do LangChain para criar pipeline RAG
        from langchain_openai import ChatOpenAI
        from langchain_core.prompts import ChatPromptTemplate
        # Comentario V1 - Cria template de prompt com sistema e entrada do usuário
        prompt=ChatPromptTemplate.from_messages([("system",SYSTEM),("human","Pergunta: {question}\n\nContexto:\n{context}")])
        # Comentario V1 - Cria cadeia de processamento (prompt -> LLM com temperatura=0 para respostas determinísticas)
        chain=prompt|ChatOpenAI(model=model,temperature=0)
        # Comentario V1 - Formaça contexto: concatena todos os trechos recuperados com protocolo e página de referência
        context="\n\n".join(f"[Fonte {s.get('protocolo')} p.{s.get('pagina')}] {s.get('conteudo')}" for s in sources)
        # Comentario V1 - Invoca a cadeia RAG passando pergunta e contexto
        response=chain.invoke({"question":question,"context":context})
        # Comentario V1 - Retorna resposta gerada pelo modelo com modo RAG ativo
        return {"resposta":response.content,"modo":"rag","fontes":sources}
    except Exception as exc:
        # Comentario V1 - Se erro no LLM, retorna modo local com aviso de falha
        result=local_answer(question,sources); result["aviso"]=f"Falha no modelo: {type(exc).__name__}"; return result
