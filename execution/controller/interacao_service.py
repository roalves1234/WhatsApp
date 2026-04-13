import textwrap

from loguru import logger

from execution.controller.agente import Agente
from execution.controller.classes import InteracaoAssistant, InteracaoUser
from execution.controller.uzapi import Uzapi
from execution.controller.version import Version
from execution.dao.dao_interacao import DaoInteracao


class InteracaoService:
    """Serviço responsável pelo fluxo de interações do usuário e do assistente."""

    _agente: Agente = Agente()

    @staticmethod
    async def eliminar_historico(fone: str) -> None:
        await DaoInteracao.delete_by_fone(fone)
        logger.info("HISTÓRICO | Eliminado | fone={fone}", fone=fone)

    @staticmethod
    async def obter_lista_interacao_por_fone(fone: str) -> list[dict]:
        return await DaoInteracao.get_by_fone(fone)

    @staticmethod
    async def salvar_interacao_user(fone: str, nome: str, mensagem: str) -> InteracaoUser:
        interacao_user = InteracaoUser(fone=fone, nome=nome, mensagem=mensagem)
        await DaoInteracao.persistir(interacao_user)
        logger.debug("INTERAÇÃO USER | Persistida | fone={fone} | nome={nome}", fone=fone, nome=nome)
        return interacao_user

    @staticmethod
    async def criar_interacao_assistant(fone: str, nome: str) -> InteracaoAssistant:
        contexto_entrada = await DaoInteracao.get_by_fone(fone)
        interacao_assistant = await InteracaoService._agente.obter_resposta(fone, nome, contexto_entrada)
        await DaoInteracao.persistir(interacao_assistant)

        logger.debug("INTERAÇÃO ASSISTANT | Persistida | fone={fone}", fone=fone)
        return interacao_assistant

    @staticmethod
    async def enviar_resposta_whats(interacao_assistant: InteracaoAssistant) -> None:
        # Mantém o formato de saída enviado no WhatsApp para não causar regressão comportamental.
        texto_resposta = textwrap.dedent(
            f"""
            {interacao_assistant.mensagem}
            🧠 {interacao_assistant.conteudo.raciocinio}
            ⏱ {interacao_assistant.duracao}
            🏷️ v{Version().get()}
            """
        ).strip()

        await Uzapi.enviar_digitando(interacao_assistant.fone, texto_resposta)
        await Uzapi.enviar_texto(interacao_assistant.fone, texto_resposta)

        logger.info(
            "RESPOSTA | fone={fone} | duração={duracao} | tokens_entrada={tin} | tokens_saida={tout}",
            fone=interacao_assistant.fone,
            duracao=interacao_assistant.duracao,
            tin=interacao_assistant.tokens_entrada,
            tout=interacao_assistant.tokens_saida,
        )