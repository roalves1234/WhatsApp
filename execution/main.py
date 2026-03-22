from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse

from execution.controller import controller
from execution.models.webhook import WebhookPayload

app = FastAPI(
    title="WhatsApp Project Application",
    description="Application strictly following the DOE architecture instructions.",
    version="1.0.0"
)

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    print(f">>> Erro global capturado: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": str(exc)},
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
