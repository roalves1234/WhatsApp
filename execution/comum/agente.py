"""
Classe genérica para execução de agentes Agno.
Pode ser reutilizada para qualquer fluxo que receba contexto_entrada (list[dict])
e retorne content, duracao, tokens_entrada e tokens_saida.
"""

import asyncio
import json
import time
from dataclasses import dataclass

from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.run.agent import RunOutput
from agno.tools import Toolkit
from loguru import logger

from execution.comum.const import LLM


@dataclass
class RespostaAgente:
    """Resultado puro da chamada ao Agno, sem dados específicos de nenhum fluxo."""
    content: dict
    duracao: str
    tokens_entrada: int | None
    tokens_saida: int | None


class Agente:
    """
    Classe genérica que encapsula a chamada ao framework Agno.
    Configurada via padrão builder (set_toolkit, set_prompt, set_output_schema).
    O Agent é instanciado lazily no primeiro obter_resposta.
    """

    def __init__(self) -> None:
        self._toolkit: Toolkit | None = None
        self._prompt: str = ""
        self._output_schema: dict = {}
        self._agente: Agent | None = None

    def set_toolkit(self, toolkit: Toolkit) -> "Agente":
        """Define o toolkit de ferramentas disponíveis para o agente."""
        self._toolkit = toolkit
        return self

    def set_prompt(self, prompt: str) -> "Agente":
        """Define as instruções (system prompt) do agente."""
        self._prompt = prompt
        return self

    def set_output_schema(self, schema: dict) -> "Agente":
        """Define o schema JSON de saída esperado do agente."""
        self._output_schema = schema
        return self

    async def obter_resposta(self, contexto_entrada: list[dict]) -> RespostaAgente:
        """
        Envia o contexto para o Agno e retorna o resultado puro da chamada.

        :param contexto_entrada: Lista de dicionários com as mensagens do histórico.
        :return: RespostaAgente com content, duracao e tokens.
        """
        # Instancia o Agent na primeira chamada, após todos os setters terem sido aplicados
        if self._agente is None:
            tools = [self._toolkit] if self._toolkit is not None else []
            self._agente = Agent(
                model=OpenAIChat(id=LLM.MODELO_ID),
                tools=tools,
                instructions=self._prompt,
            )

        contexto_entrada_json = "Histórico de interações:\n" + json.dumps(
            contexto_entrada, ensure_ascii=False, indent=2
        )

        logger.debug(
            "LLM | Chamada iniciada | mensagens_no_contexto={qtd}",
            qtd=len(contexto_entrada),
        )

        inicio: float = time.time()
        try:
            # Executa em thread separada para não bloquear o event loop durante a chamada à OpenAI
            resposta: RunOutput = await asyncio.to_thread(
                self._agente.run, contexto_entrada_json, output_schema=self._output_schema
            )
        except Exception:
            logger.exception(
                "LLM | Erro na chamada | contexto={ctx}",
                ctx=contexto_entrada,
            )
            raise

        logger.debug("LLM | Resposta recebida")

        return RespostaAgente(
            content=resposta.content,
            duracao=f"{time.time() - inicio:.1f}s",
            tokens_entrada=resposta.metrics.input_tokens,
            tokens_saida=resposta.metrics.output_tokens,
        )
