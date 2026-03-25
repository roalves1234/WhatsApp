import inspect
import os
import random
import string

import httpx

from execution.models.webhook import EnvioPayload, RecebimentoPayload
from execution.controller.const import Uzapi


class Controller:
    @staticmethod
    def deliver_home_view() -> str:
        """
        Reads the HTML view file and returns it.
        Follows MVC: Controller fetching from View.
        """
        base_dir = os.path.join(os.path.dirname(__file__), "..")
        view_path = os.path.join(base_dir, "views", "index.html")
        version_path = os.path.join(base_dir, "version.txt")

        try:
            with open(view_path, "r", encoding="utf-8") as file:
                html_content = file.read()

            version = "Desconhecida"
            if os.path.exists(version_path):
                with open(version_path, "r", encoding="utf-8") as v_file:
                    version = v_file.read().strip()

            html_content = html_content.replace("{{VERSION}}", version)
            return html_content
        except Exception as e:
            return f"<h1>Error loading view: {str(e)}</h1>"

    @staticmethod
    async def enviar_texto(payload_recebimento: RecebimentoPayload) -> dict:
        """
        Monta um EnvioPayload com os dados do webhook recebido,
        envia via POST ao endpoint /send/text da uazapi.
        Imprime erro se o status code for >= 400.
        """
        envio_payload = EnvioPayload(
            number=payload_recebimento.chat.phone,
            text="Você falou: " + payload_recebimento.message.text,
        )

        async with httpx.AsyncClient() as client:
            response = await client.post(
                            Uzapi.URL,
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