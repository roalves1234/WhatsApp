
from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import HTMLResponse, JSONResponse

# Carrega as variáveis de ambiente do arquivo .env antes de qualquer inicialização
load_dotenv()

from execution.controller.controller import Controller
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
async def read_root():
    """
    Deliver the main view.
    Control delegated to the Controller layer.
    """
    return Controller.deliver_home_view()


def do_erro(mensagem: str) -> JSONResponse:
    print(">>> ERRO: " + mensagem)  
    return JSONResponse(
        status_code=400,
        content={"detail": mensagem},
    )

@app.api_route("/webhook-recebimento", methods=["POST"])
async def webhook_recebimento(request: Request, payload: RecebimentoPayload):
    body = await request.body()
    print(">>> PAYLOAD: " + body.decode('utf-8', errors='replace'))

    if (payload.chat.phone == "+55 66 9600-8819") and (payload.message.type == "text"):
        return await Controller.enviar_resposta(payload.chat.phone, payload.message.text)
    else:
        do_erro("Número de telefone não autorizado ou não é texto")

