from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse

from execution.controller import controller
from execution.models.webhook import RecebimentoPayload

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

@app.api_route("/webhook-recebimento", methods=["POST"])
async def webhook_recebimento(payload: RecebimentoPayload):
    if payload.chat.phone == "+55 64 9285-5050":
        print(">>> Chamada do webhook-recebimento")
        return await controller.enviar_texto(payload)
    else:
        print("Número evitado: " + payload.chat.phone)
        return JSONResponse(
            status_code=400,
            content={"detail": "Número de telefone não autorizado"},
        )

