from dotenv import load_dotenv
load_dotenv()

import execution.logger  # noqa: F401 — configura os handlers do loguru

from datetime import date
from typing import Any
from fastapi import FastAPI, Query, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import HTMLResponse, JSONResponse
from loguru import logger
from execution.controller.controller import Controller
from execution.models.interacao import InteracaoAssistant
from execution.models.webhook import RecebimentoPayload, ConhecimentoPayload
from execution.comum.log_agno import LogAgno

# Direciona os logs de debug do Agno para arquivos dedicados
LogAgno()

app = FastAPI(
    title="WhatsApp Project Application",
    description="Application strictly following the DOE architecture instructions.",
    version="1.0.0"
)


# Handler global para erros de validação (ex: payload fora do formato esperado)
@app.exception_handler(RequestValidationError)
async def handler_erro_validacao(request: Request, exc: RequestValidationError) -> JSONResponse:
    """Captura erros de validação do Pydantic e registra detalhes no log."""
    body = await request.body()
    logger.warning(
        "VALIDAÇÃO | path={path} | erros={erros} | body={body}",
        path=request.url.path,
        erros=exc.errors(),
        body=body.decode("utf-8", errors="replace"),
    )
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


@app.get("/logs", response_class=HTMLResponse)
async def get_logs(
    quantidade: int = Query(default=100, ge=1, le=5000, description="Número de linhas a retornar"),
    nivel: str | None = Query(default=None, description="Filtrar por nível: DEBUG, INFO, WARNING, ERROR, CRITICAL"),
    fone: str | None = Query(default=None, description="Filtrar por número de fone"),
    data: date = Query(default_factory=date.today, description="Data do log (padrão: hoje)"),
) -> str:
    """
    Retorna grid HTML navegável com os logs filtrados.
    """
    return Controller.get_lista_log(quantidade=quantidade, data=data, nivel=nivel, fone=fone)


@app.get("/teste-supabase")
async def teste_supabase() -> dict[str, Any]:
    """Testa a conexão com o PostgreSQL do Supabase (PgVector)."""
    return Controller.testar_conexao_supabase()


@app.get("/conhecimento", response_class=HTMLResponse)
async def get_conhecimento() -> str:
    """
    Exibe a interface de edição da base de conhecimento.
    O texto é carregado diretamente do Supabase.
    """
    return await Controller.get_conhecimento()


@app.post("/conhecimento/salvar")
async def salvar_conhecimento(payload: ConhecimentoPayload) -> dict[str, bool]:
    """
    Persiste o texto da base de conhecimento no Supabase.
    """
    return await Controller.salvar_conhecimento(payload.texto)


@app.get("/visualizador-arquivos", response_class=HTMLResponse)
async def get_visualizador_arquivos(
    arquivo: str | None = Query(default=None, description="Nome do arquivo a exibir"),
) -> str:
    """Exibe a interface de visualização dos arquivos .log e .agno da pasta logs/."""
    return Controller.get_visualizador_arquivos(arquivo=arquivo)


@app.get("/interacoes/{fone}")
async def get_interacoes(fone: str) -> dict[str, Any]:
    """
    Retorna interações filtradas por número de fone.
    """
    interacoes = await Controller.get_lista_interacao_by_fone(fone)
    return {"fone": fone, "interacoes": interacoes}


@app.api_route("/webhook-recebimento", methods=["POST"])
async def webhook_recebimento(request: Request, payload: RecebimentoPayload) -> InteracaoAssistant | dict[str, Any]:
    fone = payload.chat.phone if payload.chat else "N/A"
    nome = payload.message.senderName if payload.message else "N/A"
    mensagem = payload.message.text if payload.message else "N/A"

    logger.info("WEBHOOK | fone={fone} | nome={nome} | mensagem={mensagem}", fone=fone, nome=nome, mensagem=mensagem)

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

        try:
            await Controller.salvarInteracaoUser(payload.chat.phone, payload.message.senderName, mensagem)
            interacao_assistant = await Controller.doInteracaoAssistant(payload.chat.phone, payload.message.senderName)
            return interacao_assistant
        except Exception:
            logger.exception(
                "WEBHOOK | Erro ao processar mensagem | fone={fone} | nome={nome} | mensagem={mensagem}",
                fone=fone,
                nome=nome,
                mensagem=mensagem,
            )
            return JSONResponse(status_code=500, content={"detail": "Erro interno ao processar mensagem."})
    else:
        logger.debug("WEBHOOK | Número rejeitado | fone={fone}", fone=fone)
        return {"detail": "Número rejeitado"}
