"""
Módulo que configura a base de conhecimento (Knowledge) do Agno
usando PgVector conectado ao PostgreSQL do Supabase.

O Agent utiliza esse Knowledge para fazer Agentic RAG:
ele decide quando buscar, formula queries e retorna os trechos relevantes.
"""

from agno.knowledge.embedder.openai import OpenAIEmbedder
from agno.knowledge.knowledge import Knowledge
from agno.vectordb.pgvector import PgVector, SearchType

from execution.controller.const import SupabaseConfig

# Configurações da base vetorial
_NOME_TABELA = "documents"
_MODELO_EMBEDDING = "text-embedding-3-small"
_QUANTIDADE_RESULTADOS = 4


def criar_knowledge() -> Knowledge:
    """Cria e retorna a instância de Knowledge configurada para o Supabase (pgvector)."""
    return Knowledge(
        vector_db=PgVector(
            table_name=_NOME_TABELA,
            db_url=SupabaseConfig.DB_URL,
            search_type=SearchType.vector,
            embedder=OpenAIEmbedder(id=_MODELO_EMBEDDING),
        ),
        num_documents=_QUANTIDADE_RESULTADOS,
    )
