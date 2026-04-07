import textwrap
from collections import deque
from datetime import date
from pathlib import Path

from loguru import logger

from execution.controller.agente import Agente
from execution.controller.classes import InteracaoUser, InteracaoAssistant
from execution.controller.home import Home
from execution.controller.uzapi import Uzapi
from execution.controller.version import Version
from execution.dao.dao_interacao import DaoInteracao


class Controller:
    _agente: Agente = Agente()

    @staticmethod
    def get_home() -> str:
        return Home.get()

    @staticmethod
    def get_lista_log(quantidade: int, data: date, nivel: str | None, fone: str | None) -> str:
        """
        Lê o arquivo de log da data informada e retorna as últimas N linhas,
        com filtragem opcional por nível e fone.
        """
        caminho = Path(f"logs/app_{data}.log")
        if not caminho.exists():
            return f"Arquivo de log não encontrado: {caminho}\n"

        with caminho.open("r", encoding="utf-8") as arquivo:
            linhas = arquivo.readlines()

        # Filtra por nível (ex: INFO, ERROR)
        if nivel:
            linhas = [l for l in linhas if f"| {nivel.upper()}" in l]

        # Filtra por fone — aceita com ou sem formatação
        if fone:
            fone_digitos = ''.join(filter(str.isdigit, fone))
            linhas = [l for l in linhas if fone_digitos in l or fone in l]

        # Retorna as últimas N linhas
        return "".join(deque(linhas, maxlen=quantidade))

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
    async def doInteracaoAssistant(fone: str, nome: str) -> InteracaoAssistant:
        """
        Orquestra o fluxo completo de interação do assistente:
        1. Busca o histórico de interações do fone
        2. Obtém resposta da LLM via enviar_resposta_assistant
        3. Persiste a interação do assistente no banco de dados
        Retorna o objeto InteracaoAssistant persistido.
        """
        contexto_entrada = await DaoInteracao.get_by_fone(fone)
        interacao_assistant = await Controller.enviar_resposta_assistant(fone, nome, contexto_entrada)
        await DaoInteracao.persistir(interacao_assistant)
        logger.debug("INTERAÇÃO ASSISTANT | Persistida | fone={fone}", fone=fone)
        return interacao_assistant

    @staticmethod
    async def enviar_resposta_assistant(fone: str, nome: str, contexto_entrada: list[dict]) -> InteracaoAssistant:
        """
        Orquestra o fluxo completo de resposta inteligente:
        1. Obtém a resposta da LLM via classe Agente (já instanciada no Controller)
        2. Envia a resposta ao remetente via Uzapi.enviar_texto
        """

        # Consulta a LLM com o contexto recebido pelo usuário usando a instância única
        interacao_assistant = await Controller._agente.obter_resposta(fone, nome, contexto_entrada)

        # Resposta da IA, incluindo o tempo de resposta e versão:
        texto_resposta = textwrap.dedent(f"""
                                        {interacao_assistant.mensagem}
                                        🧠 {interacao_assistant.conteudo.raciocinio}
                                        ⏱ {interacao_assistant.duracao}
                                        🏷️ v{Version().get()}
                                        """).strip()

        # Envia para WhatsApp
        await Uzapi.enviar_digitando(fone, texto_resposta)
        await Uzapi.enviar_texto(fone, texto_resposta)

        logger.info(
            "RESPOSTA | fone={fone} | duração={duracao} | tokens_entrada={tin} | tokens_saida={tout}",
            fone=fone,
            duracao=interacao_assistant.duracao,
            tin=interacao_assistant.tokens_entrada,
            tout=interacao_assistant.tokens_saida,
        )

        return interacao_assistant
