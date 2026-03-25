from pydantic import BaseModel
from typing import Optional, Union


class RecebimentoChatPayload(BaseModel):
    phone: Optional[str] = None


class RecebimentoMessagePayload(BaseModel):
    mediaType: str
    content: Optional[Union[str, dict]] = None


class RecebimentoPayload(BaseModel):
    """
    Pydantic model representing the incoming webhook payload
    from a WhatsApp API/provider.
    Only fields actually used by the controller are mapped.
    Extra fields in the real payload are ignored by Pydantic.
    """
    chat: Optional[RecebimentoChatPayload] = None
    message: Optional[RecebimentoMessagePayload] = None


class EnvioPayload(BaseModel):
    """
    Pydantic model representing the request body for
    POST https://free.uazapi.com/send/text
    """
    number: str
    text: str
