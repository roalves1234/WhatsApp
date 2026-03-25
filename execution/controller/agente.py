from agno.agent import Agent
from agno.models.openai import OpenAIChat
from execution.controller.const import LLM
import os

class Agente:
    """
    Classe que gerencia o agente de IA utilizando o framework Agno.
    Esta classe encapsula a lógica de comunicação com o modelo GPT da OpenAI.
    """
    def __init__(self):
        """
        Inicializa o agente com o modelo especificado.
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

    def obter_resposta(self, texto_entrada: str) -> str:
        """
        Envia o texto para a LLM e retorna o conteúdo da resposta.
        
        :param texto_entrada: O texto enviado pelo usuário.
        :return: A resposta processada pela IA.
        """
        # O método run do Agno retorna um objeto de resposta
        resultado = "Resposta IA: " + self._agente.run(texto_entrada).content
        
        return resultado