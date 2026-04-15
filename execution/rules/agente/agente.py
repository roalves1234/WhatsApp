from dataclasses import dataclass

from loguru import logger

from execution.comum.agente_comum import AgenteComum
from execution.comum.const import LLM
from execution.models.interacao import ConteudoResposta
from execution.rules.agente.toolkit_agno import ToolKitAgno
from execution.rules.agente.agente_comum import SCHEMA_SAIDA
from execution.rules.agente.agente_prompts import Prompts


@dataclass
class RespostaAgente:
    """Resultado da chamada ao Agno mapeado para os tipos específicos deste fluxo."""
    conteudo: ConteudoResposta
    duracao: str
    tokens_entrada: int | None
    tokens_saida: int | None


class Agente:
    """
    Agente específico do fluxo de interação com o usuário.
    Utiliza o padrão Singleton para garantir que o AgenteComum seja criado uma única vez.
    """
    _instancia: "Agente | None" = None
    _agente_comum: AgenteComum

    def __new__(cls) -> "Agente":
        """
        Garante que apenas uma instância da classe Agente exista.
        """
        if cls._instancia is None:
            cls._instancia = super(Agente, cls).__new__(cls)
            cls._instancia._inicializar()
        return cls._instancia

    def _inicializar(self) -> None:
        """
        Configura o AgenteComum com toolkit, prompt e schema específicos (executado apenas uma vez).
        """
        self._agente_comum = (
            AgenteComum()
            .set_toolkit(ToolKitAgno())
            .set_prompt(Prompts.AGENTE)
            .set_output_schema(SCHEMA_SAIDA)
        )
        logger.info("AGENTE | Inicializado | modelo={modelo}", modelo=LLM.MODELO_ID)

    async def obter_resposta(self, contexto_entrada: list[dict]) -> RespostaAgente:
        """
        Delega a chamada ao AgenteComum e converte o resultado para os tipos deste fluxo.

        :param contexto_entrada: Lista de dicionários com as mensagens do histórico.
        :return: RespostaAgente com conteudo (ConteudoResposta), duracao e tokens.
        """
        resposta = await self._agente_comum.obter_resposta(contexto_entrada)
        return RespostaAgente(
            conteudo=ConteudoResposta(**resposta.content),
            duracao=resposta.duracao,
            tokens_entrada=resposta.tokens_entrada,
            tokens_saida=resposta.tokens_saida,
        )
