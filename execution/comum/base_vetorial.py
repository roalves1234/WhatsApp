"""
Módulo responsável por construir e persistir a base vetorial no Supabase (pgvector)
a partir do texto da base de conhecimento.

Utiliza RecursiveCharacterTextSplitter com separadores de parágrafo para garantir
que chunks respeitem quebras naturais do texto.

Pré-requisitos no Supabase (executar uma única vez):
(veja em base_vetorial.sql)
"""

from langchain_community.vectorstores import SupabaseVectorStore
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from loguru import logger
from supabase import Client

from execution.comum.const import LLM, RagConfig


class BaseVetorial:
    """Gerencia a construção e persistência da base vetorial no Supabase (pgvector)."""

    # Separadores em ordem de prioridade: parágrafo > quebra de linha > espaço > caractere
    _SEPARADORES = ["\n\n", "\n", " ", ""]

    # UUID nulo usado para deletar todas as linhas via neq (nenhuma linha terá esse id)
    _UUID_NULO = "00000000-0000-0000-0000-000000000000"

    def __init__(self) -> None:
        # Parâmetros configuráveis via setters — sem valores padrão para forçar configuração explícita
        self._chunk_size: int | None = None
        self._overlap: int | None = None
        self._nome_tabela: str | None = None
        self._cliente: Client | None = None

    def setChunkSize(self, chunk_size: int) -> "BaseVetorial":
        """Define o tamanho de cada chunk gerado pelo splitter."""
        self._chunk_size = chunk_size
        return self

    def setOverlap(self, overlap: int) -> "BaseVetorial":
        """Define a sobreposição (em caracteres) entre chunks consecutivos."""
        self._overlap = overlap
        return self

    def setNomeTabela(self, nome_tabela: str) -> "BaseVetorial":
        """Define o nome da tabela no Supabase onde os chunks serão persistidos."""
        self._nome_tabela = nome_tabela
        return self

    def setCliente(self, cliente: Client) -> "BaseVetorial":
        """Define o cliente Supabase utilizado para as operações de persistência."""
        self._cliente = cliente
        return self

    def _validar_configuracao(self) -> None:
        """Garante que todos os parâmetros obrigatórios foram configurados via setters."""
        if self._chunk_size is None:
            raise ValueError("BASE VETORIAL | chunk_size não configurado — chame setChunkSize()")
        if self._overlap is None:
            raise ValueError("BASE VETORIAL | overlap não configurado — chame setOverlap()")
        if self._nome_tabela is None:
            raise ValueError("BASE VETORIAL | nome_tabela não configurado — chame setNomeTabela()")
        if self._cliente is None:
            raise ValueError("BASE VETORIAL | cliente não configurado — chame setCliente()")

    def _criar_embeddings(self) -> OpenAIEmbeddings:
        """Instancia o modelo de embeddings da OpenAI."""
        return OpenAIEmbeddings(
            model=RagConfig.MODELO_EMBEDDING,
            api_key=LLM.OPENAI_API_KEY,
        )

    def _dividir_em_chunks(self, texto: str) -> list[str]:
        """Divide o texto em chunks respeitando separadores naturais de parágrafo."""
        splitter = RecursiveCharacterTextSplitter(
            separators=self._SEPARADORES,
            chunk_size=self._chunk_size,
            chunk_overlap=self._overlap,
            length_function=len,
        )
        chunks = splitter.split_text(texto)
        logger.info("BASE VETORIAL | Chunks gerados | total={n}", n=len(chunks))
        return chunks

    def _remover_chunks_anteriores(self) -> None:
        """Remove todos os registros da tabela para evitar duplicação a cada atualização."""
        self._cliente.table(self._nome_tabela).delete().neq("id", self._UUID_NULO).execute()
        logger.debug(
            "BASE VETORIAL | Chunks anteriores removidos da tabela '{tabela}'",
            tabela=self._nome_tabela,
        )

    def _persistir_chunks(self, chunks: list[str], embeddings: OpenAIEmbeddings) -> None:
        """Gera embeddings dos chunks e os persiste no Supabase via pgvector."""
        SupabaseVectorStore.from_texts(
            texts=chunks,
            embedding=embeddings,
            client=self._cliente,
            table_name=self._nome_tabela,
            query_name=RagConfig.NOME_FUNCAO_RPC,
        )
        logger.info(
            "BASE VETORIAL | Chunks gravados no Supabase | tabela={tabela} | total={n}",
            tabela=self._nome_tabela,
            n=len(chunks),
        )

    def atualizar(self, texto: str) -> None:
        """
        Orquestra a atualização completa da base vetorial:
        divide o texto, remove os chunks anteriores e persiste os novos no Supabase.

        Args:
            texto: Conteúdo completo da base de conhecimento.
        """
        self._validar_configuracao()

        if not texto.strip():
            logger.warning("BASE VETORIAL | Texto vazio — nada será gravado no Supabase")
            return

        embeddings = self._criar_embeddings()
        chunks = self._dividir_em_chunks(texto)

        self._remover_chunks_anteriores()
        self._persistir_chunks(chunks, embeddings)
