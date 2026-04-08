from datetime import date

from execution.controller.classes import InteracaoAssistant, InteracaoUser
from execution.controller.conhecimento_service import ConhecimentoService
from execution.controller.home_service import HomeService
from execution.controller.interacao_service import InteracaoService
from execution.controller.log_service import LogService


class Controller:
    @staticmethod
    def get_home() -> str:
        return HomeService.obter_home()

    @staticmethod
    def get_lista_log(quantidade: int, data: date, nivel: str | None, fone: str | None) -> str:
        return LogService.obter_lista_log(quantidade=quantidade, data=data, nivel=nivel, fone=fone)

    @staticmethod
    async def eliminar_historico(fone: str) -> None:
        await InteracaoService.eliminar_historico(fone)

    @staticmethod
    async def get_lista_interacao_by_fone(fone: str) -> list[dict]:
        return await InteracaoService.obter_lista_interacao_por_fone(fone)

    @staticmethod
    async def salvarInteracaoUser(fone: str, nome: str, mensagem: str) -> InteracaoUser:
        return await InteracaoService.salvar_interacao_user(fone=fone, nome=nome, mensagem=mensagem)

    @staticmethod
    async def get_conhecimento() -> str:
        return await ConhecimentoService.obter_conhecimento()

    @staticmethod
    def get_lista_arquivos_log() -> dict[str, list[dict]]:
        return LogService.obter_lista_arquivos_log()

    @staticmethod
    async def salvar_conhecimento(texto: str) -> dict[str, bool]:
        return await ConhecimentoService.salvar_conhecimento(texto=texto)

    @staticmethod
    async def doInteracaoAssistant(fone: str, nome: str) -> InteracaoAssistant:
        interacaoAssistant = await InteracaoService.criar_interacao_assistant(fone=fone, nome=nome)
        await InteracaoService.enviar_resposta_whats(interacaoAssistant)
        return interacaoAssistant