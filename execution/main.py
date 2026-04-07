from dotenv import load_dotenv
load_dotenv()

from typing import Any
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import HTMLResponse, JSONResponse
from datetime import datetime
from execution.controller.controller import Controller
from execution.controller.classes import InteracaoAssistant
from execution.models.webhook import RecebimentoPayload

app = FastAPI(
    title="WhatsApp Project Application",
    description="Application strictly following the DOE architecture instructions.",
    version="1.0.0"
)


# Handler global para erros de validação (ex: payload fora do formato esperado)
@app.exception_handler(RequestValidationError)
async def handler_erro_validacao(request: Request, exc: RequestValidationError) -> JSONResponse:
    """Captura erros de validação do Pydantic e imprime detalhes no terminal."""
    body = await request.body()
    print(f"""
          {'=' * 60}
          >>> ERRO DE VALIDAÇÃO em {request.url.path}
          >>> Detalhes do erro: {exc.errors()}
          >>> Body recebido: {body.decode('utf-8', errors='replace')}
          {'=' * 60}
          """)
    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors()},
    )


@app.get("/", response_class=HTMLResponse)
async def read_root() -> str:
    """
    Deliver the main view.
    Control delegated to the Controller layer.
    """
    return Controller.get_home()


@app.get("/interacoes/{fone}")
async def get_interacoes(fone: str) -> dict[str, Any]:
    """
    Retorna interações filtradas por número de fone.
    """
    interacoes = await DaoInteracao.get_by_fone(fone)
    return {"fone": fone, "interacoes": interacoes}

@app.api_route("/webhook-recebimento", methods=["POST"])
async def webhook_recebimento(request: Request, payload: RecebimentoPayload) -> InteracaoAssistant | dict[str, Any]:
    body = await request.body()
    print(f"\n\n")
    print(f">>> DATA/HORA: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    print(f">>> PAYLOAD: " + body.decode('utf-8', errors='replace'))

    if (
        payload.chat is not None
        and payload.chat.phone == "+55 66 9600-8819"
        and payload.message is not None
        and payload.message.type == "text"
    ):
        mensagem = payload.message.text

        if mensagem.strip().lower() == "reiniciar":
            await Controller.eliminar_historico(payload.chat.phone)
            mensagem = "Olá"

        interacao_user = await Controller.salvarInteracaoUser(payload.chat.phone, payload.message.senderName, mensagem)
        interacao_assistant = await Controller.doInteracaoAssistant(payload.chat.phone, payload.message.senderName)

        return interacao_assistant
    else:
        return {"detail": "Número rejeitado"}