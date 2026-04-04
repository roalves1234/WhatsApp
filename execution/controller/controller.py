import textwrap
from typing import Any

from execution.controller.agente import Agente
from execution.controller.home import Home
from execution.controller.uzapi import Uzapi
from execution.controller.version import Version


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

        # Resposta da IA, incluindo o tempo de resposta e versão:
        texto_resposta = textwrap.dedent(f"""
                                        {resposta_ia.content.resposta}
                                        🧠 {resposta_ia.content.raciocinio}
                                        ⏱ {resposta_ia.time}                                        
                                        🏷️ v{Version().get()}
                                        """).strip()

        # Simula digitação proporcional ao tamanho da resposta (mín. 2s, máx. 8s)
        await Controller.enviar_digitando(numero, texto_resposta)

        # Retorno
        return await Uzapi.enviar_texto(numero, texto_resposta)