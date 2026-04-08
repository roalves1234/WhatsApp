import textwrap
from datetime import date

from loguru import logger

from execution.controller.agente import Agente
from execution.controller.base_vetorial import construir_base_vetorial
from execution.controller.classes import InteracaoUser, InteracaoAssistant
from execution.controller.conhecimento_view import ConhecimentoView
from execution.controller.home import Home
from execution.controller.logs import LogFile
from execution.controller.uzapi import Uzapi
from execution.controller.version import Version
from execution.dao.dao_interacao import DaoInteracao
from execution.dao.dao_conhecimento import DaoConhecimento


class Controller:
    _agente: Agente = Agente()

    @staticmethod
    def get_home() -> str:
        return Home.get()

    @staticmethod
    def get_lista_log(quantidade: int, data: date, nivel: str | None, fone: str | None) -> str:
        return LogFile.listar(quantidade=quantidade, data=data, nivel=nivel, fone=fone)

    @staticmethod
    async def eliminar_historico(fone: str) -> None:
        """
        Apaga o histórico do fone.
        """
        await DaoInteracao.delete_by_fone(fone)
        logger.info("HISTÓRICO | Eliminado | fone={fone}", fone=fone)

    @staticmethod
    async def get_lista_interacao_by_fone(fone: str) -> list[dict]:
        return await DaoInteracao.get_by_fone(fone)

    @staticmethod
    async def salvarInteracaoUser(fone: str, nome: str, mensagem: str) -> InteracaoUser:
        """
        Cria e persiste uma interação do usuário no banco de dados.
        Retorna o objeto InteracaoUser persistido.
        """
        interacao_user = InteracaoUser(fone=fone, nome=nome, mensagem=mensagem)
        await DaoInteracao.persistir(interacao_user)

        logger.debug("INTERAÇÃO USER | Persistida | fone={fone} | nome={nome}", fone=fone, nome=nome)
        return interacao_user

    @staticmethod
    async def get_conhecimento() -> str:
        """Carrega o texto da base de conhecimento e retorna a página HTML do editor."""
        texto = await DaoConhecimento.buscar_texto()
        return ConhecimentoView.get(texto)

    @staticmethod
    def get_lista_arquivos_log() -> dict[str, list[dict]]:
        return LogFile.listar_arquivos()

    @staticmethod
    async def salvar_conhecimento(texto: str) -> dict[str, bool]:
        """Persiste o texto da base de conhecimento no Supabase e reconstrói a base vetorial."""
        await DaoConhecimento.salvar_texto(texto)
        construir_base_vetorial(texto)
        return {"sucesso": True}

    @staticmethod
    async def doInteracaoAssistant(fone: str, nome: str) -> InteracaoAssistant:
        """
        Orquestra o fluxo completo de interação do assistente:
        1. Busca o histórico de interações do fone
        2. Consulta a LLM via Agente
        3. Envia a resposta ao remetente via enviar_resposta_assistant
        4. Persiste a interação do assistente no banco de dados
        Retorna o objeto InteracaoAssistant persistido.
        """
        contexto_entrada = await DaoInteracao.get_by_fone(fone)

        # Consulta a LLM com o contexto recebido pelo usuário usando a instância única
        interacao_assistant = await Controller._agente.obter_resposta(fone, nome, contexto_entrada)

        await Controller.enviar_resposta_assistant(interacao_assistant)
        await DaoInteracao.persistir(interacao_assistant)

        logger.debug("INTERAÇÃO ASSISTANT | Persistida | fone={fone}", fone=fone)
        return interacao_assistant

    @staticmethod
    async def enviar_resposta_assistant(interacao_assistant: InteracaoAssistant) -> None:
        """
        Formata e envia a resposta do assistente ao remetente via WhatsApp.
        """
        texto_resposta = textwrap.dedent(f"""
                                        {interacao_assistant.mensagem}
                                        🧠 {interacao_assistant.conteudo.raciocinio}
                                        ⏱ {interacao_assistant.duracao}
                                        🏷️ v{Version().get()}
                                        """).strip()

        # Envia para WhatsApp
        await Uzapi.enviar_digitando(interacao_assistant.fone, texto_resposta)
        await Uzapi.enviar_texto(interacao_assistant.fone, texto_resposta)

        logger.info(
            "RESPOSTA | fone={fone} | duração={duracao} | tokens_entrada={tin} | tokens_saida={tout}",
            fone=interacao_assistant.fone,
            duracao=interacao_assistant.duracao,
            tin=interacao_assistant.tokens_entrada,
            tout=interacao_assistant.tokens_saida,
        )
