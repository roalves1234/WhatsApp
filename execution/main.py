
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import HTMLResponse, JSONResponse

from execution.controller import controller
from execution.models.webhook import RecebimentoPayload

app = FastAPI(
    title="WhatsApp Project Application",
    description="Application strictly following the DOE architecture instructions.",
    version="1.0.0"
)


# Handler global para erros de validação (ex: payload fora do formato esperado)
@app.exception_handler(RequestValidationError)
async def handler_erro_validacao(request: Request, exc: RequestValidationError):
    """Captura erros de validação do Pydantic e imprime detalhes no terminal."""
    corpo_cru = await request.body()
    print("=" * 60)
    print(f">>> ERRO DE VALIDAÇÃO em {request.url.path}\n")
    print(f">>> Detalhes do erro: {exc.errors()}\n")
    print(f">>> Body recebido: {corpo_cru.decode('utf-8', errors='replace')}\n")
    print("=" * 60)
    print("\n")
    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors()},
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
    print(payload.model_dump())

    if payload.chat.phone == "+55 66 9600-8819":
        print(">>> Chamada do webhook-recebimento")
        return await controller.enviar_texto(payload)
    else:
        print("Número evitado: " + payload.chat.phone)
        return JSONResponse(
            status_code=400,
            content={"detail": "Número de telefone não autorizado"},
        )

