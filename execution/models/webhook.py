from pydantic import BaseModel
from typing import Optional


class ChatPayload(BaseModel):
    phone: Optional[str] = None


class MessagePayload(BaseModel):
    content: Optional[str] = None


class WebhookPayload(BaseModel):
    """
    Pydantic model representing the incoming webhook payload
    from a WhatsApp API/provider.
    Only fields actually used by the controller are mapped.
    Extra fields in the real payload are ignored by Pydantic.
    """
    chat: Optional[ChatPayload] = None
    message: Optional[MessagePayload] = None


class SendTextPayload(BaseModel):
    """
    Pydantic model representing the request body for
    POST https://free.uazapi.com/send/text
    """
    number: str
    text: str
