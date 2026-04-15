import textwrap

from loguru import logger

from execution.rules.agente.agente_impl import AgenteImpl
from execution.models.interacao import InteracaoAssistant, InteracaoUser
from execution.comum.uzapi import Uzapi
from execution.rules.version import Version
from execution.dao.interacao_dao import InteracaoDao


class InteracaoService:
    """Serviço responsável pelo fluxo de interações do usuário e do assistente."""

    _agente: AgenteImpl = AgenteImpl()

    @staticmethod
    async def eliminar_historico(fone: str) -> None:
        await InteracaoDao.delete_by_fone(fone)
        logger.info("HISTÓRICO | Eliminado | fone={fone}", fone=fone)

    @staticmethod
    async def obter_lista_interacao_por_fone(fone: str) -> list[dict]:
        return await InteracaoDao.get_by_fone(fone)

    @staticmethod
    async def salvar_interacao_user(fone: str, nome: str, mensagem: str) -> InteracaoUser:
        interacao_user = InteracaoUser(fone=fone, nome=nome, mensagem=mensagem)
        await InteracaoDao.persistir(interacao_user)
        logger.debug("INTERAÇÃO USER | Persistida | fone={fone} | nome={nome}", fone=fone, nome=nome)
        return interacao_user

    @staticmethod
    async def criar_interacao_assistant(fone: str, nome: str) -> InteracaoAssistant:
        contexto_entrada = await InteracaoDao.get_by_fone(fone)
        resposta_agente = await InteracaoService._agente.obter_resposta(contexto_entrada)
        interacao_assistant = InteracaoAssistant(
            fone=fone,
            nome=nome,
            mensagem=resposta_agente.conteudo.sua_resposta,
            conteudo=resposta_agente.conteudo,
            duracao=resposta_agente.duracao,
            tokens_entrada=resposta_agente.tokens_entrada,
            tokens_saida=resposta_agente.tokens_saida,
        )
        await InteracaoDao.persistir(interacao_assistant)

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
