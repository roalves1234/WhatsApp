from fastapi import FastAPI
from fastapi.responses import HTMLResponse

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
