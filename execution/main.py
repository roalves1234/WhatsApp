from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from datetime import datetime

from execution.controllers import main_controller

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
    return main_controller.deliver_home_view()

@app.api_route("/webhook_resposta", methods=["POST"])
async def webhook_resposta():
    """
    Webhook endpoint that returns a JSON with the current date and time only.
    """
    now = datetime.now()
    return {
        "data": now.strftime("%Y-%m-%d"),
        "hora": now.strftime("%H:%M:%S"),
        "data_hora": now.strftime("%Y-%m-%d %H:%M:%S")
    }
