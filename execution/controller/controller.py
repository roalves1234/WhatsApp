import asyncio
import inspect
from typing import Any

import httpx

from execution.models.webhook import EnvioPayload
from execution.controller.const import Uzapi
from execution.controller.agente import Agente
from execution.controller.home import Home

class Controller:
    _agente: Agente = Agente()

    @staticmethod
    def get_home() -> str:
        return Home.get()

    @staticmethod
    async def enviar_digitando(numero: str, texto: str) -> None:
        """
        Envia indicação de 'digitando' para o número informado via uazapi.
        A duração é calculada proporcionalmente ao tamanho do texto (mín. 2s, máx. 8s).
        A presença é cancelada automaticamente ao enviar a mensagem.
        """
        duracao_ms = min(max(len(texto) * 30, 2000), 8000)

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{Uzapi.URL}/message/presence",
                json={
                    "number": numero,
                    "presence": "composing",
                    "delay": duracao_ms,
                },
                headers={
                    "Accept": "application/json",
                    "Content-Type": "application/json",
                    "token": Uzapi.TOKEN,
                },
            )

        if response.status_code >= 400:
            print(f">>> ERRO {inspect.currentframe().f_code.co_qualname}: {response.text}")

        # Aguarda o tempo de digitação antes de prosseguir
        await asyncio.sleep(duracao_ms / 1000)

    @staticmethod
    async def enviar_texto(numero: str, texto: str) -> dict[str, Any]:
        """
        Envia um texto para um número de telefone via uazapi.
        Imprime erro no console se o status code for >= 400.
        """
        envio_payload = EnvioPayload(
            number=numero,
            text=texto,
        )

        async with httpx.AsyncClient() as client:
            response = await client.post(
                            f"{Uzapi.URL}/send/text",
                            json=envio_payload.model_dump(),
                            headers={
                                "Accept": "application/json",
                                "Content-Type": "application/json",
                                "token": Uzapi.TOKEN,
                            },
                        )

        if response.status_code >= 400:
            print(f">>> ERRO {inspect.currentframe().f_code.co_qualname}: {response.text}")

        return response.json()

    @staticmethod
    async def enviar_resposta(numero: str, texto: str) -> dict[str, Any]:
        """
        Orquestra o fluxo completo de resposta inteligente:
        1. Obtém a resposta da LLM via classe Agente (já instanciada no Controller)
        2. Envia a resposta ao remetente via Controller.enviar_texto
        """
        # Consulta a LLM com o texto recebido pelo usuário usando a instância única
        resposta_ia = Controller._agente.obter_resposta(texto)

        # Simula digitação proporcional ao tamanho da resposta (mín. 2s, máx. 8s)
        await Controller.enviar_digitando(numero, resposta_ia.content)

        # Encaminha a resposta da IA para o número de origem, incluindo o tempo de resposta
        texto_resposta = f"{resposta_ia.content}\n⏱ {resposta_ia.time}"
        return await Controller.enviar_texto(numero, texto_resposta)