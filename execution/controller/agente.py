from datetime import timedelta
from typing import Any
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from execution.controller.const import LLM
import os

class Agente:
    """
    Classe que gerencia o agente de IA utilizando o framework Agno.
    Esta classe encapsula a lógica de comunicação com o modelo GPT da OpenAI.
    Utiliza o padrão Singleton para garantir que o Agente seja criado uma única vez.
    """
    _instancia = None

    def __new__(cls):
        """
        Garante que apenas uma instância da classe Agente exista.
        """
        if cls._instancia is None:
            cls._instancia = super(Agente, cls).__new__(cls)
            cls._instancia._inicializar()
        return cls._instancia

    def _inicializar(self):
        """
        Inicializa o agente com o modelo especificado (executado apenas uma vez).
        """
        # O framework Agno busca automaticamente a variável de ambiente OPENAI_API_KEY
        self._agente = Agent(
            model=OpenAIChat(id=LLM.MODELO_ID),
            instructions=[
                "Você é um assistente virtual integrado ao WhatsApp.",
                "Responda de forma concisa e amigável.",
                "Sempre utilize formatação Markdown quando apropriado."
            ],
            markdown=True
        )

    def obter_resposta(self, texto_entrada: str) -> dict[str, Any]:
        """
        Envia o texto para a LLM e retorna um objeto com métricas da resposta.

        :param texto_entrada: O texto enviado pelo usuário.
        :return: Dict com content, time (segundos), input_tokens e output_tokens.
        """
        resposta = self._agente.run(texto_entrada)
        duracao = resposta.metrics.duration or 0

        return {
            "content": resposta.content,
            "time": str(timedelta(seconds=duracao)).split(".")[0],
            "input_tokens": resposta.metrics.input_tokens,
            "output_tokens": resposta.metrics.output_tokens,
        }