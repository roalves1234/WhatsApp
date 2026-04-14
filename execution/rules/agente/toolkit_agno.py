"""
Toolkit principal do agente — expõe as tools disponíveis para o agente Agno.
"""

from agno.tools import Toolkit, tool

from execution.comum.rag import RAG
from execution.dao.conexao import ConexaoSupabase
from execution.rules.agente.agente_prompts import Prompts


class ToolKitAgno(Toolkit):
    """
    Toolkit responsável por expor a busca RAG como tool do agente.
    A lógica de embedding, consulta e formatação está encapsulada em RAG.
    """

    def __init__(self) -> None:
        super().__init__(
            name="base_conhecimento",
            tools=[self.base_conhecimento],
        )

    @tool(name="base_conhecimento", description=Prompts.TOOL_BASE_CONHECIMENTO)
    def base_conhecimento(self, consulta: str) -> str:
        """
        Busca trechos relevantes na base de conhecimento usando RAG.

        Args:
            consulta (str): Pergunta ou termo a ser buscado na base vetorial.
        Returns:
            str: Chunks relevantes formatados ou mensagem de ausência de resultado.
        """
        return RAG().setCliente(ConexaoSupabase.get_cliente()).buscar(consulta)
