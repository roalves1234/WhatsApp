from pydantic import BaseModel
from typing import Optional


class MessagePayload(BaseModel):
    content: Optional[str] = None


class WebhookPayload(BaseModel):
    """
    Pydantic model representing the incoming webhook payload
    from a WhatsApp API/provider.
    """
    senderName: Optional[str] = None
    phone: Optional[str] = None
    message: Optional[MessagePayload] = None


class SendTextPayload(BaseModel):
    """
    Pydantic model representing the request body for
    POST https://free.uazapi.com/send/text
    """
    number: str
    text: str
