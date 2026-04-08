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


class BaseVetorial:
    """Gerencia a construção e persistência da base vetorial no Supabase (pgvector)."""

    # Configurações dos chunks
    _CHUNK_SIZE = 400
    _CHUNK_OVERLAP = 80

    # Separadores em ordem de prioridade: parágrafo > quebra de linha > espaço > caractere
    _SEPARADORES = ["\n\n", "\n", " ", ""]

    # Nome da tabela e da função RPC no Supabase
    _NOME_TABELA = "documents"
    _NOME_FUNCAO = "match_documents"

    # UUID nulo usado para deletar todas as linhas via neq (nenhuma linha terá esse id)
    _UUID_NULO = "00000000-0000-0000-0000-000000000000"

    def _criar_cliente_supabase(self) -> Client:
        """Cria e retorna o cliente Supabase a partir das variáveis de ambiente."""
        url = os.getenv("SUPABASE_URL", "")
        key = os.getenv("SUPABASE_KEY", "")
        return create_client(url, key)

    def _criar_embeddings(self) -> OpenAIEmbeddings:
        """Instancia o modelo de embeddings da OpenAI."""
        return OpenAIEmbeddings(
            model="text-embedding-3-small",
            api_key=os.getenv("OPENAI_API_KEY", ""),
        )

    def _dividir_em_chunks(self, texto: str) -> list[str]:
        """Divide o texto em chunks respeitando separadores naturais de parágrafo."""
        splitter = RecursiveCharacterTextSplitter(
            separators=self._SEPARADORES,
            chunk_size=self._CHUNK_SIZE,
            chunk_overlap=self._CHUNK_OVERLAP,
            length_function=len,
        )
        chunks = splitter.split_text(texto)
        logger.info("BASE VETORIAL | Chunks gerados | total={n}", n=len(chunks))
        return chunks

    def _remover_chunks_anteriores(self, cliente: Client) -> None:
        """Remove todos os registros da tabela para evitar duplicação a cada atualização."""
        cliente.table(self._NOME_TABELA).delete().neq("id", self._UUID_NULO).execute()
        logger.debug(
            "BASE VETORIAL | Chunks anteriores removidos da tabela '{tabela}'",
            tabela=self._NOME_TABELA,
        )

    def _persistir_chunks(self, chunks: list[str], embeddings: OpenAIEmbeddings, cliente: Client) -> None:
        """Gera embeddings dos chunks e os persiste no Supabase via pgvector."""
        SupabaseVectorStore.from_texts(
            texts=chunks,
            embedding=embeddings,
            client=cliente,
            table_name=self._NOME_TABELA,
            query_name=self._NOME_FUNCAO,
        )
        logger.info(
            "BASE VETORIAL | Chunks gravados no Supabase | tabela={tabela} | total={n}",
            tabela=self._NOME_TABELA,
            n=len(chunks),
        )

    def atualizar(self, texto: str) -> None:
        """
        Orquestra a atualização completa da base vetorial:
        divide o texto, remove os chunks anteriores e persiste os novos no Supabase.

        Args:
            texto: Conteúdo completo da base de conhecimento.
        """
        if not texto.strip():
            logger.warning("BASE VETORIAL | Texto vazio — nada será gravado no Supabase")
            return

        cliente = self._criar_cliente_supabase()
        embeddings = self._criar_embeddings()
        chunks = self._dividir_em_chunks(texto)

        self._remover_chunks_anteriores(cliente)
        self._persistir_chunks(chunks, embeddings, cliente)
