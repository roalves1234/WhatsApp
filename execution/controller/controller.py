from typing import Any

from execution.controller.agente import Agente
from execution.controller.home import Home
from execution.controller.uzapi import Uzapi


class Controller:
    _agente: Agente = Agente()

    @staticmethod
    def get_home() -> str:
        return Home.get()

    @staticmethod
    async def enviar_digitando(numero: str, texto: str) -> None:
        await Uzapi.enviar_digitando(numero, texto)

    @staticmethod
    async def enviar_resposta(numero: str, texto: str) -> dict[str, Any]:
        """
        Orquestra o fluxo completo de resposta inteligente:
        1. Obtém a resposta da LLM via classe Agente (já instanciada no Controller)
        2. Envia a resposta ao remetente via Uzapi.enviar_texto
        """
        # Consulta a LLM com o texto recebido pelo usuário usando a instância única
        resposta_ia = Controller._agente.obter_resposta(texto)

        # Simula digitação proporcional ao tamanho da resposta (mín. 2s, máx. 8s)
        await Controller.enviar_digitando(numero, resposta_ia.content)

        # Encaminha a resposta da IA para o número de origem, incluindo o tempo de resposta
        texto_resposta = f"{resposta_ia.content}\n⏱ {resposta_ia.time}"
        return await Uzapi.enviar_texto(numero, texto_resposta)
