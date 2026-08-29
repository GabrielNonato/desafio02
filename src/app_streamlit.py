"""Comentario V1 - Interface Streamlit mínima - fornece interface web para consultas do sistema RAG."""
import requests
import streamlit as st

# Comentario V1 - Configuração da página Streamlit com título e ícone
st.set_page_config(page_title="Consulta de atendimentos",page_icon="🔎")
st.title("Consulta inteligente de atendimentos")
# Comentario V1 - Cria inputs: área de texto para pergunta e slider para quantidade de fontes a recuperar
question=st.text_area("Pergunta",placeholder="Quais problemas de instalação do Python aparecem com maior frequência?")
top_k=st.slider("Quantidade de fontes",1,10,5)
# Comentario V1 - Botão de consulta habilitado apenas quando pergunta é preenchida
if st.button("Consultar",type="primary",disabled=not question.strip()):
    # Comentario V1 - Faz requisição POST para API e exibe resposta com modo de operação e fontes
    try:
        # Comentario V1 - Exibe resposta do modelo e lista de fontes com protocolo, documento e similaridade
        response=requests.post("http://127.0.0.1:8000/ask",json={"pergunta":question,"top_k":top_k},timeout=60); response.raise_for_status(); data=response.json()
        st.subheader("Resposta"); st.write(data["resposta"]); st.caption(f"Modo: {data.get('modo')}")
        st.subheader("Fontes")
        for source in data.get("fontes",[]): st.markdown(f"**{source.get('protocolo')}** - {source.get('documento')}, página {source.get('pagina')} - similaridade {source.get('similaridade')}")
    # Comentario V1 - Trata erros de conexão com a API e exibe mensagem de erro
    except requests.RequestException as exc: st.error(f"Não foi possível consultar a API: {exc}")
