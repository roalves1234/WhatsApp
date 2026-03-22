import os
import random
import string

import httpx

from execution.models.webhook import SendTextPayload, WebhookPayload

# ---------------------------------------------------------------------------
# Main Controller – Home view
# ---------------------------------------------------------------------------
UAZAPI_URL = "https://free.uazapi.com/send/text"
UAZAPI_TOKEN = "08a7938e-c56b-439d-9b69-14cb22312f64"


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


# ---------------------------------------------------------------------------
# Webhook Controller – send text reply
# ---------------------------------------------------------------------------
async def send_text_reply(payload: WebhookPayload) -> dict:
    """
    Build a SendTextPayload using webhook payload values,
    POST it to the uazapi /send/text endpoint,
    and return both the payload sent and the API response.
    """
    send_payload = SendTextPayload(
        number=payload.phone,
        text="Você falou: " + payload.message.content,
    )

    async with httpx.AsyncClient() as client:
        response = await client.post(
            UAZAPI_URL,
            json=send_payload.model_dump(),
            headers={
                "Accept": "application/json",
                "Content-Type": "application/json",
                "token": UAZAPI_TOKEN,
            },
        )

    return {
        "payload_enviado": send_payload.model_dump(),
        "status_code": response.status_code,
        "resposta_api": response.json() if response.headers.get("content-type", "").startswith("application/json") else response.text,
    }
