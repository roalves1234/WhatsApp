"""
Toolkit de RAG que consulta a base vetorial no Supabase via REST
(SDK oficial), usando a RPC 'match_documents' já definida em base_vetorial.sql.
"""

from agno.tools import Toolkit, tool
from langchain_openai import OpenAIEmbeddings
from loguru import logger

from execution.comum.const import LLM, RagConfig
from execution.dao.conexao import ConexaoSupabase
from execution.rules.agente.agente_prompts import Prompts

# Quantidade máxima de chunks retornados na busca — exclusivo deste módulo
_MAX_RESULTADOS = 6


class ToolBaseConhecimento(Toolkit):
    """
    Toolkit responsável por executar buscas RAG na base vetorial do Supabase.
    Encapsula o fluxo: geração de embedding → consulta RPC → formatação do resultado.
    """

    def __init__(self) -> None:
        # Instância reutilizável do modelo de embedding (evita recriação a cada chamada)
        self._embeddings = OpenAIEmbeddings(
            model=RagConfig.MODELO_EMBEDDING,
            api_key=LLM.OPENAI_API_KEY,
        )
        super().__init__(
            name="base_conhecimento",
            tools=[self.base_conhecimento],
        )

    def _gerar_embedding(self, consulta: str) -> list[float]:
        """Converte a consulta em vetor numérico usando o modelo de embedding configurado."""
        return self._embeddings.embed_query(consulta)

    def _consultar_banco(self, vetor_consulta: list[float]) -> list[dict]:
        """Executa a RPC 'match_documents' no Supabase e retorna os chunks encontrados."""
        cliente = ConexaoSupabase.get_cliente()
        resposta = cliente.rpc(
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
            f"Similaridade={linha['similarity']:.3f}\n{linha['content']}"
            for linha in linhas
        ]
        return "\n\n---\n\n".join(partes)

    @tool(name="base_conhecimento", description=Prompts.TOOL_BASE_CONHECIMENTO)
    def base_conhecimento(self, consulta: str) -> str:
        """
        Executa o fluxo completo de RAG:
        1. Gera o embedding da consulta
        2. Consulta a RPC 'match_documents' no Supabase
        3. Retorna os chunks formatados para o agente
        """
        vetor_consulta = self._gerar_embedding(consulta)
        linhas = self._consultar_banco(vetor_consulta)

        logger.info("RAG | Chunks encontrados | total={n}", n=len(linhas))

        if not linhas:
            return "Nenhum trecho relevante encontrado na base de conhecimento."

        return self._formatar_resultado(linhas)
