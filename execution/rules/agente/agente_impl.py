from dataclasses import dataclass

from loguru import logger

from execution.comum.agente import Agente
from execution.comum.const import LLM
from execution.models.interacao import ConteudoResposta
from execution.rules.agente.toolkit_agno import ToolKitAgno
from execution.rules.agente.agente_comum import SCHEMA_SAIDA
from execution.rules.agente.agente_prompts import Prompts


@dataclass
class RespostaAgenteImpl:
    """Resultado da chamada ao Agno mapeado para os tipos específicos deste fluxo."""
    conteudo: ConteudoResposta
    duracao: str
    tokens_entrada: int | None
    tokens_saida: int | None


class AgenteImpl:
    """
    Agente específico do fluxo de interação com o usuário.
    Utiliza o padrão Singleton para garantir que o Agente seja criado uma única vez.
    """
    _instancia: "AgenteImpl | None" = None
    _agente: Agente

    def __new__(cls) -> "AgenteImpl":
        """
        Garante que apenas uma instância da classe AgenteImpl exista.
        """
        if cls._instancia is None:
            cls._instancia = super(AgenteImpl, cls).__new__(cls)
            cls._instancia._inicializar()
        return cls._instancia

    def _inicializar(self) -> None:
        """
        Configura o Agente com toolkit, prompt e schema específicos (executado apenas uma vez).
        """
        self._agente = (
            Agente()
            .set_toolkit(ToolKitAgno())
            .set_prompt(Prompts.AGENTE)
            .set_output_schema(SCHEMA_SAIDA)
        )
        logger.info("AGENTE | Inicializado | modelo={modelo}", modelo=LLM.MODELO_ID)

    async def obter_resposta(self, contexto_entrada: list[dict]) -> RespostaAgenteImpl:
        """
        Delega a chamada ao Agente e converte o resultado para os tipos deste fluxo.

        :param contexto_entrada: Lista de dicionários com as mensagens do histórico.
        :return: RespostaAgenteImpl com conteudo (ConteudoResposta), duracao e tokens.
        """
        resposta = await self._agente.obter_resposta(contexto_entrada)
        return RespostaAgenteImpl(
            conteudo=ConteudoResposta(**resposta.content),
            duracao=resposta.duracao,
            tokens_entrada=resposta.tokens_entrada,
            tokens_saida=resposta.tokens_saida,
        )
