import asyncio
import inspect
from typing import Any

import httpx

from execution.models.webhook import EnvioPayload
from execution.controller.const import Uzapi


class Uzapi:

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
