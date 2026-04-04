import time
from datetime import datetime
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.run.agent import RunOutput
from pydantic import BaseModel, Field
from execution.controller.const import LLM


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


class ConteudoResposta(BaseModel):
    contexto_entrada: str = Field(description="Resumo do que foi solicitado pelo usuário")
    raciocinio: str = Field(description="Passo a passo utilizado para se chegar à resposta")
    resposta: str = Field(description="A resposta final ao usuário")


class Interacao(BaseModel):
    entrada: str
    resposta: ConteudoResposta
    duration: str
    input_tokens: int | None
    output_tokens: int | None
    data_hora: datetime


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
            instructions=[
                "Você é um assistente virtual integrado ao WhatsApp.",
                "Responda de forma concisa e amigável.",
                "Sempre retorne sua resposta no formato JSON definido, preenchendo os campos:",
                "  - contexto_entrada: um resumo do que foi solicitado pelo usuário",
                "  - raciocinio: o passo a passo utilizado para se chegar à resposta",
                "  - resposta: a resposta final ao usuário",
            ],
            markdown=False,
        )

    def obter_resposta(self, texto_entrada: str) -> Interacao:
        """
        Envia o texto para a LLM e retorna um objeto estruturado com métricas da resposta.

        :param texto_entrada: O texto enviado pelo usuário.
        :return: Objeto com content (ConteudoResposta), time (segundos), input_tokens e output_tokens.
        """
        inicio: float = time.time()
        resposta: RunOutput = self._agente.run(texto_entrada, output_schema=SCHEMA_SAIDA)
        duracao: float = time.time() - inicio

        return Interacao(
            entrada=texto_entrada,
            resposta=ConteudoResposta(**resposta.content),
            duration=f"{duracao:.1f}s",
            input_tokens=resposta.metrics.input_tokens,
            output_tokens=resposta.metrics.output_tokens,
            data_hora=datetime.now(),
        )
