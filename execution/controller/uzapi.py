import asyncio
import inspect
from typing import Any

import httpx

from execution.models.webhook import EnvioPayload
from execution.controller.const import UzapiConfig


class Uzapi:

    @staticmethod
    async def marcar_como_lida(numero: str) -> None:
        """
        Marca o chat como lido no WhatsApp (duplo check azul).
        Utiliza o endpoint /chat/read da Uazapi.
        """
        # Remove espaços e símbolos, deixando apenas dígitos
        numero_puro = ''.join(filter(str.isdigit, numero))
        numero_com_sufixo = f"{numero_puro}@s.whatsapp.net"

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{UzapiConfig.URL}/chat/read",
                json={
                    "number": numero_com_sufixo,
                    "read": True,
                },
                headers={
                    "Accept": "application/json",
                    "Content-Type": "application/json",
                    "token": UzapiConfig.TOKEN,
                },
            )

        if response.status_code >= 400:
            raise Exception(f"Erro: {inspect.currentframe().f_code.co_qualname}: {response.text}")

    @staticmethod
    async def enviar_digitando(numero: str, texto: str) -> None:
        """
        Envia indicação de 'digitando' para o número informado via uazapi.
        A duração é calculada proporcionalmente ao tamanho do texto (mín. 2s, máx. 8s).
        A presença é cancelada automaticamente ao enviar a mensagem.
        Antes de enviar, marca o chat como lido (duplo check azul).
        """
        # Marca a mensagem como visualizada antes de começar a digitar
        await Uzapi.marcar_como_lida(numero)

        duracao_ms = min(max(len(texto) * 30, 2000), 4000)

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{UzapiConfig.URL}/message/presence",
                json={
                    "number": numero,
                    "presence": "composing",
                    "delay": duracao_ms,
                },
                headers={
                    "Accept": "application/json",
                    "Content-Type": "application/json",
                    "token": UzapiConfig.TOKEN,
                },
            )

        if response.status_code >= 400:
            raise Exception(f"Erro: {inspect.currentframe().f_code.co_qualname}: {response.text}")

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

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{UzapiConfig.URL}/send/text",
                json=envio_payload.model_dump(),
                headers={
                    "Accept": "application/json",
                    "Content-Type": "application/json",
                    "token": UzapiConfig.TOKEN,
                },
            )

        if response.status_code >= 400:
            raise Exception(f"Erro: {inspect.currentframe().f_code.co_qualname}: {response.text}")

        return response.json()
