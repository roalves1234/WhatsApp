"""
Toolkit Agno que implementa busca RAG na base vetorial do Supabase (pgvector).

Quando o agente identifica que o usuário tem uma dúvida, ele chama esta tool
para recuperar trechos relevantes da base de conhecimento antes de responder.
"""

import os

from agno.tools import Toolkit
from langchain_community.vectorstores import SupabaseVectorStore
from langchain_openai import OpenAIEmbeddings
from loguru import logger

from execution.dao.conexao import ConexaoSupabase


class RagTool(Toolkit):
    """Toolkit de busca semântica na base vetorial (Supabase + pgvector)."""

    # Mesmas configurações usadas na criação da base vetorial
    _NOME_TABELA = "documents"
    _NOME_FUNCAO = "match_documents"
    _QUANTIDADE_RESULTADOS = 4

    def __init__(self, **kwargs):
        tools = [self.consultar_base_conhecimento]
        super().__init__(name="rag_tool", tools=tools, **kwargs)

        self._embeddings = OpenAIEmbeddings(
            model="text-embedding-3-small",
            api_key=os.getenv("OPENAI_API_KEY", ""),
        )
        self._vector_store = SupabaseVectorStore(
            client=ConexaoSupabase.get_cliente(),
            embedding=self._embeddings,
            table_name=self._NOME_TABELA,
            query_name=self._NOME_FUNCAO,
        )
        logger.info("RAG TOOL | Inicializada | tabela={tabela}", tabela=self._NOME_TABELA)

    def consultar_base_conhecimento(self, pergunta: str) -> str:
        """
        Consulta a base de conhecimento para encontrar informações relevantes à pergunta do usuário.
        Use esta ferramenta SEMPRE que o usuário fizer uma pergunta ou tiver uma dúvida.

        Args:
            pergunta: A pergunta ou dúvida do usuário.

        Returns:
            Trechos relevantes encontrados na base de conhecimento.
        """
        logger.debug("RAG TOOL | Buscando | pergunta={p}", p=pergunta)

        resultados = self._vector_store.similarity_search(
            query=pergunta,
            k=self._QUANTIDADE_RESULTADOS,
        )

        if not resultados:
            logger.debug("RAG TOOL | Nenhum resultado encontrado")
            return "Nenhuma informação relevante encontrada na base de conhecimento."

        # Monta o contexto concatenando os chunks encontrados
        trechos = [doc.page_content for doc in resultados]
        contexto = "\n---\n".join(trechos)

        logger.debug(
            "RAG TOOL | Resultados encontrados | total={n}",
            n=len(resultados),
        )
        return f"Informações encontradas na base de conhecimento:\n\n{contexto}"
