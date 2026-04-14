import asyncio
import time
import json
from dataclasses import dataclass
from loguru import logger
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.run.agent import RunOutput
from execution.comum.const import LLM
from execution.models.interacao import ConteudoResposta
from execution.rules.agente.toolkit_agno import ToolKitAgno
from execution.rules.agente.agente_comum import SCHEMA_SAIDA
from execution.rules.agente.agente_prompts import Prompts


@dataclass
class RespostaAgente:
    """Resultado puro da chamada ao Agno, sem dados de identificação do usuário."""
    conteudo: ConteudoResposta
    duracao: str
    tokens_entrada: int | None
    tokens_saida: int | None


class Agente:
    """
    Classe que gerencia o agente de IA utilizando o framework Agno.
    Esta classe encapsula a lógica de comunicação com o modelo GPT da OpenAI.
    Utiliza o padrão Singleton para garantir que o Agente seja criado uma única vez.
    """
    _instancia: "Agente | None" = None
    _agente: Agent

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
        Inicializa o agente com o modelo especificado (executado apenas uma vez).
        """

        self._agente = Agent(
            model=OpenAIChat(id=LLM.MODELO_ID),
            tools=[ToolKitAgno()],
            instructions=Prompts.AGENTE,
        )
        logger.info("AGENTE | Inicializado | modelo={modelo}", modelo=LLM.MODELO_ID)

    async def obter_resposta(self, contexto_entrada: list[dict]) -> RespostaAgente:
        """
        Envia o contexto para a LLM e retorna o resultado puro da chamada ao Agno.

        :param contexto_entrada: Lista de dicionários com origem e mensagem para contexto da conversa.
        :return: RespostaAgente com conteudo (ConteudoResposta), duração e tokens.
        """
        # Formata o contexto como JSON para enviar à LLM
        contexto_entrada_json = "Histórico de interações:\n" + json.dumps(contexto_entrada, ensure_ascii=False, indent=2)

        logger.debug(
            "LLM | Chamada iniciada | mensagens_no_contexto={qtd}",
            qtd=len(contexto_entrada),
        )

        inicio: float = time.time()
        try:
            # Executa em thread separada para não bloquear o event loop durante a chamada à OpenAI
            resposta: RunOutput = await asyncio.to_thread(self._agente.run, contexto_entrada_json, output_schema=SCHEMA_SAIDA)
        except Exception:
            logger.exception(
                "LLM | Erro na chamada | contexto={ctx}",
                ctx=contexto_entrada,
            )
            raise

        logger.debug("LLM | Resposta recebida")

        return RespostaAgente(
            conteudo=ConteudoResposta(**resposta.content),
            duracao=f"{time.time() - inicio:.1f}s",
            tokens_entrada=resposta.metrics.input_tokens,
            tokens_saida=resposta.metrics.output_tokens,
        )
