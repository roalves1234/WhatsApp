from pydantic import BaseModel
from typing import Optional, Union

class RecebimentoChatPayload(BaseModel):
    phone: Optional[str] = None


class RecebimentoMessagePayload(BaseModel):
    type: str
    text: str
    senderName: str = ""


class RecebimentoPayload(BaseModel):
    """
    Pydantic model representing the incoming webhook payload
    from a WhatsApp API/provider.
    Only fields actually used by the controller are mapped.
    Extra fields in the real payload are ignored by Pydantic.
    """
    chat: Optional[RecebimentoChatPayload] = None
    message: Optional[RecebimentoMessagePayload] = None


class ConhecimentoPayload(BaseModel):
    """Payload recebido no endpoint POST /conhecimento/salvar."""
    texto: str
