"""
Tool customizada de RAG que consulta a base vetorial no Supabase via REST
(SDK oficial), usando a RPC 'match_documents' já definida em base_vetorial.sql.
"""

import os

from agno.tools import tool
from langchain_openai import OpenAIEmbeddings
from loguru import logger

from execution.dao.conexao import ConexaoSupabase

# Configurações do RAG
_MODELO_EMBEDDING = "text-embedding-3-small"
_NOME_FUNCAO_RPC = "match_documents"
_MAX_RESULTADOS = 6


@tool(
    name="buscar_base_conhecimento",
    description=(
        "- Caso o usuário fizer perguntas sobre a nossa embarcação ou sobre nossos produtos ou serviços, você deve consultar a nossa base de conhecimento para responder, utilizando a ferramenta `buscar_base_conhecimento`."
"
    ),
    show_result=True,
)
def buscar_base_conhecimento(consulta: str) -> str:
    """
    Executa RAG no Supabase via REST:
    1. Gera o embedding da consulta com OpenAI
    2. Chama a RPC 'match_documents' via SDK Supabase
    3. Retorna os chunks formatados para o agente
    """
    # Gera embedding da consulta
    embeddings = OpenAIEmbeddings(
        model=_MODELO_EMBEDDING,
        api_key=os.getenv("OPENAI_API_KEY", ""),
    )
    vetor_consulta: list[float] = embeddings.embed_query(consulta)

    # Chama a RPC via REST (PostgREST)
    cliente = ConexaoSupabase.get_cliente()
    resposta = cliente.rpc(
        _NOME_FUNCAO_RPC,
        {
            "query_embedding": vetor_consulta,
            "match_count": _MAX_RESULTADOS,
            "filter": {},
        },
    ).execute()

    linhas: list[dict] = resposta.data or []
    logger.info("RAG | Chunks encontrados | total={n}", n=len(linhas))

    if not linhas:
        return "Nenhum trecho relevante encontrado na base de conhecimento."

    # Formata similaridade + conteúdo para o agente
    partes = [
        f"[similaridade={linha['similarity']:.3f}]\n{linha['content']}"
        for linha in linhas
    ]
    return "\n\n---\n\n".join(partes)
