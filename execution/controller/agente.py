import asyncio
import time
import json
from datetime import datetime
from loguru import logger
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.run.agent import RunOutput
from execution.controller.const import LLM
from execution.controller.classes import ConteudoResposta, InteracaoAssistant
from execution.controller.agente_tool_rag import buscar_base_conhecimento
from execution.dao.dao_interacao import DaoInteracao


# Schema JSON que define a estrutura de saída esperada da LLM
SCHEMA_SAIDA: dict = {
    "type": "json_schema",
    "json_schema": {
        "name": "RespostaEstruturada",
        "schema": {
            "type": "object",
            "properties": {
                "contexto_entrada": {"type": "string", "description": "Resumo do que foi solicitado pelo usuário"},
                "raciocinio": {"type": "string", "description": "Passo a passo utilizado para se chegar à resposta"},
                "resposta":   {"type": "string", "description": "A resposta final ao usuário"},
            },
            "required": ["contexto_entrada", "raciocinio", "resposta"],
            "additionalProperties": False,
        },
    },
}


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
        # O framework Agno busca automaticamente a variável de ambiente OPENAI_API_KEY
        self._agente = Agent(
            model=OpenAIChat(id=LLM.MODELO_ID),
            tools=[buscar_base_conhecimento],
            instructions=[
                "Você é um assistente virtual integrado ao WhatsApp.",
                "Responda de forma concisa e amigável.",
                "Sempre que a pergunta depender de informações específicas do domínio do usuário, "
                "chame a tool 'buscar_base_conhecimento' para recuperar trechos relevantes antes de responder.",
                "Para perguntas triviais ou de conhecimento geral, responda diretamente sem chamar a tool.",
                "Sempre retorne sua resposta no formato JSON definido, preenchendo os campos:",
                "  - contexto_entrada: um resumo do que foi solicitado pelo usuário",
                "  - raciocinio: o passo a passo utilizado para se chegar à resposta",
                "  - resposta: a resposta final ao usuário",
            ],
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

        duracao: float = time.time() - inicio

        logger.debug(
            "LLM | Resposta recebida | fone={fone} | duração={duracao:.1f}s | tokens_entrada={tin} | tokens_saida={tout}",
            fone=fone,
            duracao=duracao,
            tin=resposta.metrics.input_tokens,
            tout=resposta.metrics.output_tokens,
        )

        conteudo = ConteudoResposta(**resposta.content)
        return InteracaoAssistant(
            fone=fone,
            nome=nome,
            mensagem=conteudo.resposta,
            conteudo=conteudo,
            duracao=f"{duracao:.1f}s",
            tokens_entrada=resposta.metrics.input_tokens,
            tokens_saida=resposta.metrics.output_tokens,
        )
