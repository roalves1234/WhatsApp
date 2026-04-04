import textwrap

from execution.controller.agente import Agente
from execution.controller.classes import InteracaoUser, InteracaoAssistant
from execution.controller.home import Home
from execution.controller.uzapi import Uzapi
from execution.controller.version import Version


class Controller:
    _agente: Agente = Agente()

    @staticmethod
    def get_home() -> str:
        return Home.get()

    @staticmethod
    async def enviar_resposta_assistant(fone: str, nome: str, texto_entrada: str) -> InteracaoAssistant:
        """
        Orquestra o fluxo completo de resposta inteligente:
        1. Obtém a resposta da LLM via classe Agente (já instanciada no Controller)
        2. Envia a resposta ao remetente via Uzapi.enviar_texto
        """

        # Consulta a LLM com o texto recebido pelo usuário usando a instância única
        interacao_assistant = Controller._agente.obter_resposta(fone, nome, texto_entrada)

        # Resposta da IA, incluindo o tempo de resposta e versão:
        texto_resposta = textwrap.dedent(f"""
                                        {interacao_assistant.mensagem}
                                        🧠 {interacao_assistant.conteudo.raciocinio}
                                        ⏱ {interacao_assistant.duracao}
                                        🏷️ v{Version().get()}
                                        """).strip()

        # Envia para WhatsApp
        await Uzapi.enviar_digitando(fone, texto_resposta)
        await Uzapi.enviar_texto(fone, texto_resposta)

        # Retorno
        return interacao_assistant