"""
Módulo responsável por construir e persistir a base vetorial no Supabase (pgvector)
a partir do texto da base de conhecimento.

Utiliza RecursiveCharacterTextSplitter com separadores de parágrafo para garantir
que chunks respeitem quebras naturais do texto.

Pré-requisitos no Supabase (executar uma única vez):
(veja em base_vetorial.sql)
"""

import os

from langchain_community.vectorstores import SupabaseVectorStore
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from loguru import logger
from supabase import Client, create_client

# Configurações dos chunks
_CHUNK_SIZE = 400
_CHUNK_OVERLAP = 80

# Separadores em ordem de prioridade: parágrafo > quebra de linha > espaço > caractere
_SEPARADORES = ["\n\n", "\n", " ", ""]

# Nome da tabela e da função RPC no Supabase
_NOME_TABELA = "documents"
_NOME_FUNCAO = "match_documents"


def construir_base_vetorial(texto: str) -> None:
    """
    Divide o texto em chunks respeitando parágrafos inteiros, gera embeddings
    via OpenAI e armazena no Supabase (pgvector).

    Remove todos os chunks anteriores antes de inserir os novos para evitar
    duplicação de conteúdo.

    Args:
        texto: Conteúdo completo da base de conhecimento.
    """
    if not texto.strip():
        logger.warning("BASE VETORIAL | Texto vazio — nada será gravado no Supabase")
        return

    supabase_url = os.getenv("SUPABASE_URL", "")
    supabase_key = os.getenv("SUPABASE_KEY", "")
    cliente: Client = create_client(supabase_url, supabase_key)

    splitter = RecursiveCharacterTextSplitter(
        separators=_SEPARADORES,
        chunk_size=_CHUNK_SIZE,
        chunk_overlap=_CHUNK_OVERLAP,
        length_function=len,
    )

    chunks = splitter.split_text(texto)
    logger.info("BASE VETORIAL | Chunks gerados | total={n}", n=len(chunks))

    embeddings = OpenAIEmbeddings(
        model="text-embedding-3-small",
        api_key=os.getenv("OPENAI_API_KEY", ""),
    )

    # Remove todos os chunks anteriores para evitar duplicação a cada atualização
    # Usa neq com UUID nulo — exclui todas as linhas pois nenhuma terá esse id
    _UUID_NULO = "00000000-0000-0000-0000-000000000000"
    cliente.table(_NOME_TABELA).delete().neq("id", _UUID_NULO).execute()
    logger.debug("BASE VETORIAL | Chunks anteriores removidos da tabela '{tabela}'", tabela=_NOME_TABELA)

    SupabaseVectorStore.from_texts(
        texts=chunks,
        embedding=embeddings,
        client=cliente,
        table_name=_NOME_TABELA,
        query_name=_NOME_FUNCAO,
    )

    logger.info(
        "BASE VETORIAL | Chunks gravados no Supabase | tabela={tabela} | total={n}",
        tabela=_NOME_TABELA,
        n=len(chunks),
    )
