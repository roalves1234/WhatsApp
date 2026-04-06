from typing import Any
from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import HTMLResponse, JSONResponse
from datetime import datetime


# Carrega as variáveis de ambiente do arquivo .env antes de qualquer inicialização
load_dotenv()

from execution.controller.controller import Controller
from execution.controller.classes import InteracaoAssistant, InteracaoUser
from execution.models.webhook import RecebimentoPayload
from execution.dao.dao_interacao import DaoInteracao

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
    interacoes = DaoInteracao.get_by_fone(fone)
    return {"fone": fone, "interacoes": interacoes}


def do_erro(mensagem: str) -> dict[str, Any]:
    print(">>> ERRO: " + mensagem)
    return {"detail": mensagem}

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
            Controller.eliminar_historico(payload.chat.phone)
            mensagem = "Olá"

        interacao_user = InteracaoUser(
            fone=payload.chat.phone,
            nome=payload.message.senderName,
            mensagem=mensagem,
        )
        DaoInteracao.persistir(interacao_user)

        contexto_entrada = DaoInteracao.get_by_fone(payload.chat.phone)
        interacao_assistant = await Controller.enviar_resposta_assistant(payload.chat.phone, payload.message.senderName, contexto_entrada)
        DaoInteracao.persistir(interacao_assistant)

        return interacao_assistant
    else:
        return do_erro("Número de telefone não autorizado ou não é texto")