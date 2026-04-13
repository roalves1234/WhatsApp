import asyncio
import time
import json
from pathlib import Path
from datetime import datetime
from loguru import logger
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.run.agent import RunOutput
from execution.comum.const import LLM
from execution.models.interacao import ConteudoResposta, InteracaoAssistant
from execution.rules.agente.tool_base_conhecimento import ToolBaseConhecimento
from execution.rules.agente.agente_comum import SCHEMA_SAIDA
from execution.dao.interacao_dao import InteracaoDao

# Carrega o prompt do agente a partir do arquivo de texto
_PROMPT_PATH = Path(__file__).parent / "agente_prompt.txt"
_INSTRUCOES: list[str] = _PROMPT_PATH.read_text(encoding="utf-8").splitlines()


class Agente:
    """
    Classe que gerencia o agente de IA utilizando o framework Agno.
    Esta classe encapsula a lógica de comunicação com o modelo GPT da OpenAI.
    Utiliza o padrão Singleton para garantir que o Agente seja criado uma única vez.
    """
    _instancia: "Agente | None" = None
    _agente: Agent

    def __new__(cls) -> "Agente":
        """
        Garante que apenas uma instância da classe Agente exista.
        """
        if cls._instancia is None:
            cls._instancia = super(Agente, cls).__new__(cls)
            cls._instancia._inicializar()
        return cls._instancia

    def _inicializar(self) -> None:
        """
        Inicializa o agente com o modelo especificado (executado apenas uma vez).
        """

        # O framework Agno continua buscando a variável de ambiente OPENAI_API_KEY.
        # A constante equivalente da aplicação agora fica centralizada em LLM.
        self._agente = Agent(
            model=OpenAIChat(id=LLM.MODELO_ID),
            tools=[ToolBaseConhecimento()],
            instructions=_INSTRUCOES,
            markdown=False,
        )
        logger.info("AGENTE | Inicializado | modelo={modelo}", modelo=LLM.MODELO_ID)

    async def obter_resposta(self, fone: str, nome: str, contexto_entrada: list[dict]) -> InteracaoAssistant:
        """
        Envia o contexto para a LLM e retorna um objeto estruturado com métricas da resposta.

        :param fone: Número de telefone do remetente.
        :param nome: Nome exibido do remetente.
        :param contexto_entrada: Lista de dicionários com origem e mensagem para contexto da conversa.
        :return: InteracaoAssistant com conteudo (ConteudoResposta), tempo, tokens e métricas.
        """
        # Formata o contexto como JSON para enviar à LLM
        contexto_entrada_json = "Histórico de interações:\n" + json.dumps(contexto_entrada, ensure_ascii=False, indent=2)

        logger.debug(
            "LLM | Chamada iniciada | fone={fone} | mensagens_no_contexto={qtd}",
            fone=fone,
            qtd=len(contexto_entrada),
        )

        inicio: float = time.time()
        try:
            # Executa em thread separada para não bloquear o event loop durante a chamada à OpenAI
            resposta: RunOutput = await asyncio.to_thread(self._agente.run, contexto_entrada_json, output_schema=SCHEMA_SAIDA)
        except Exception:
            logger.exception(
                "LLM | Erro na chamada | fone={fone} | contexto={ctx}",
                fone=fone,
                ctx=contexto_entrada,
            )
            raise

        logger.debug(
            "LLM | Resposta recebida | fone={fone}",
            fone=fone,
        )

        conteudo = ConteudoResposta(**resposta.content)
        return InteracaoAssistant(
            fone=fone,
            nome=nome,
            mensagem=conteudo.sua_resposta,
            conteudo=conteudo,
            duracao=f"{time.time() - inicio:.1f}s",
            tokens_entrada=resposta.metrics.input_tokens,
            tokens_saida=resposta.metrics.output_tokens,
        )
