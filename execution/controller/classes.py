from datetime import datetime
from pydantic import BaseModel, Field


class ConteudoResposta(BaseModel):
    """Estrutura da resposta obtida da LLM"""
    contexto_entrada: str = Field(description="Resumo do que foi solicitado pelo usuário")
    raciocinio: str = Field(description="Passo a passo utilizado para se chegar à resposta")
    resposta: str = Field(description="A resposta final ao usuário")


class InteracaoBase(BaseModel):
    """Classe base para interações, com campos comuns"""
    origem: str  # "user" | "assistant" | "owner"
    criado_em: datetime = Field(default_factory=datetime.now)
    mensagem: str


class InteracaoUser(InteracaoBase):
    """Interação gerada pelo usuário"""
    origem: str = "user"


class InteracaoAssistant(InteracaoBase):
    """Interação gerada pelo assistente (LLM)"""
    origem: str = "assistant"
    conteudo: ConteudoResposta
    duracao: str
    tokens_entrada: int | None = None
    tokens_saida: int | None = None


class InteracaoOwner(InteracaoBase):
    """Interação gerada pelo proprietário"""
    origem: str = "owner"
