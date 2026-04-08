from pydantic import BaseModel


class ConhecimentoPayload(BaseModel):
    """Payload recebido no endpoint POST /conhecimento/salvar."""
    texto: str
