"""
Módulo responsável pela execução do fluxo RAG (Retrieval-Augmented Generation):
geração de embedding → consulta RPC no Supabase → formatação dos chunks retornados.
"""

from langchain_openai import OpenAIEmbeddings
from loguru import logger
from supabase import Client

from execution.comum.const import LLM, RagConfig

# Quantidade máxima de chunks retornados na busca
_MAX_RESULTADOS = 6


class RAG:
    """
    Encapsula o fluxo de busca RAG na base vetorial do Supabase.
    Responsável por: gerar embedding → consultar RPC → formatar resultado.
    """

    def __init__(self) -> None:
        # Instância reutilizável do modelo de embedding (evita recriação a cada chamada)
        self._embeddings = OpenAIEmbeddings(
            model=RagConfig.MODELO_EMBEDDING,
            api_key=LLM.OPENAI_API_KEY,
        )
        self._client: Client | None = None

    def set_client(self, client: Client) -> "RAG":
        """Define o cliente Supabase utilizado na consulta vetorial."""
        self._client = client
        return self

    def _gerar_embedding(self, consulta: str) -> list[float]:
        """Converte a consulta em vetor numérico usando o modelo de embedding configurado."""
        return self._embeddings.embed_query(consulta)

    def _consultar_banco(self, vetor_consulta: list[float]) -> list[dict]:
        """Executa a RPC 'match_documents' no Supabase e retorna os chunks encontrados."""
        if self._client is None:
            raise RuntimeError("RAG | Cliente Supabase não configurado — chame setCliente()")
        resposta = self._client.rpc(
            RagConfig.NOME_FUNCAO_RPC,
            {
                "query_embedding": vetor_consulta,
                "match_count": _MAX_RESULTADOS,
                "filter": {},
            },
        ).execute()
        return resposta.data or []

    def _formatar_resultado(self, linhas: list[dict]) -> str:
        """Formata os chunks retornados em texto estruturado para consumo do agente."""
        partes = [
            f"[similaridade={linha['similarity']:.3f}\n{linha['content']}]"
            for linha in linhas
        ]
        return "\n\n---\n\n".join(partes)

    def buscar(self, consulta: str) -> str:
        """
        Executa o fluxo completo de RAG:
        1. Gera o embedding da consulta
        2. Consulta a RPC 'match_documents' no Supabase
        3. Retorna os chunks formatados

        Args:
            consulta: Texto da pergunta a ser buscada na base vetorial.

        Returns:
            Chunks relevantes formatados ou mensagem de ausência de resultado.
        """
        vetor_consulta = self._gerar_embedding(consulta)
        linhas = self._consultar_banco(vetor_consulta)

        logger.info("RAG | Chunks encontrados | total={n}", n=len(linhas))

        if not linhas:
            return "Nenhum trecho relevante encontrado na base de conhecimento."

        return self._formatar_resultado(linhas)
