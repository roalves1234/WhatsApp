"""
Tool customizada de RAG que consulta a base vetorial no Supabase via REST
(SDK oficial), usando a RPC 'match_documents' já definida em base_vetorial.sql.
"""

from agno.tools import tool
from langchain_openai import OpenAIEmbeddings
from loguru import logger

from execution.controller.const import LLM, RAGConfig
from execution.dao.conexao import ConexaoSupabase

# Quantidade máxima de chunks retornados na busca — exclusivo deste módulo
_MAX_RESULTADOS = 6


@tool(
    name="buscar_base_conhecimento",
    description=(
        "Use **sempre** a tool `buscar_base_conhecimento` **antes de responder** se a mensagem mencionar direta ou indiretamente qualquer informação sobre a Piratas Pizzaria, como:"
        "- atrações, ambiente, cardápio, pizzas, produtos, serviços"
        "- funcionamento, regras, reservas, ingressos, eventos"
        "- estrutura, preços, horários, localização, atendimento"
        "- experiência para crianças ou adultos"
        "- qualquer detalhe factual do negócio"
        "Isso inclui perguntas indiretas ou de continuação, como:"
        "“Me fala mais”, “Como funciona?”, “Quanto custa?”, “O que tem aí?”, “Não entendi”, “E esse último item?”, “Quais são as atrações?”"
        "**Se houver dúvida, use a tool.**"
        "**Nunca responda com suposição ou conhecimento próprio sobre a Piratas Pizzaria.**"
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
        model=RAGConfig.MODELO_EMBEDDING,
        api_key=LLM.OPENAI_API_KEY,
    )
    vetor_consulta: list[float] = embeddings.embed_query(consulta)

    # Chama a RPC via REST (PostgREST)
    cliente = ConexaoSupabase.get_cliente()
    resposta = cliente.rpc(
        RAGConfig.NOME_FUNCAO_RPC,
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
