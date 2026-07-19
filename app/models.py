from datetime import datetime, timezone
from typing import Optional, List, Dict, Any, Literal
from pydantic import BaseModel


class Customer(BaseModel):
    id: str
    name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    domain: Literal["healthcare"]
    authenticated: bool = False


class Message(BaseModel):
    role: Literal["user", "bot", "agent", "system"]
    content: str
    channel: str
    timestamp: datetime
    intent: Optional[str] = None
    confidence: Optional[float] = None
    escalated: bool = False


class Conversation(BaseModel):
    id: str = ""
    customer_id: str
    channel: str
    domain: Literal["healthcare"]
    messages: List[Message] = []
    context: Dict[str, Any] = {}
    created_at: datetime = datetime.now(timezone.utc)
    updated_at: datetime = datetime.now(timezone.utc)
    status: Literal["active", "closed", "escalated"] = "active"


class IncomingEvent(BaseModel):
    channel: Literal["web", "whatsapp", "phone", "email", "in_app"]
    customer_id: str
    domain: Literal["healthcare"]
    message: str
    metadata: Dict[str, Any] = {}
