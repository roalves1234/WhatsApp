from fastapi import FastAPI
from fastapi.responses import HTMLResponse

from execution.controllers import controller
from execution.models.webhook import WebhookPayload

app = FastAPI(
    title="WhatsApp Project Application",
    description="Application strictly following the DOE architecture instructions.",
    version="1.0.0"
)

@app.get("/", response_class=HTMLResponse)
async def read_root():
    """
    Deliver the main view.
    Control delegated to the Controller layer.
    """
    print(">>> Chamada do index.html")
    return controller.deliver_home_view()

@app.api_route("/webhook_resposta", methods=["POST"])
async def webhook_resposta(payload: WebhookPayload):
    print(">>> Chamada do webhook_resposta")
    return await controller.send_text_reply(payload)
