from typing import Dict, Any
from app.models import Conversation
from app.backend_mock import BACKEND

class ResponseEngine:
    def generate(self, conversation: Conversation, intent: str, entities: Dict[str, Any]) -> str:
        user = BACKEND.get_customer(conversation.customer_id)
        if user:
            conversation.context.setdefault("name", user.name)
            conversation.context.setdefault("domain", user.domain)

        name = conversation.context.get("name", "there")

        if intent.startswith("HC_"):
            return self._healthcare(conversation, intent, entities, name)
        else:
            return self._fallback(conversation, name)

    def _healthcare(self, conv: Conversation, intent: str, entities: Dict[str, Any], name: str) -> str:
        if intent == "HC_APPOINTMENT":
            return BACKEND.book_appointment(conv.customer_id, entities.get("provider"), entities.get("date"))
        if intent == "HC_REFILL":
            return BACKEND.refill_prescription(conv.customer_id, entities.get("medication"))
        if intent == "HC_BILLING":
            return BACKEND.explain_billing(conv.customer_id)
        if intent == "HC_PROVIDER":
            return BACKEND.find_provider(entities.get("provider"), entities.get("location"))
        if intent == "HC_INFO":
            return "Our clinic hours are 8 AM to 8 PM, Monday–Saturday. Emergency services are available 24/7."
        return f"Hi {name}, I can help with appointments, prescription refills, billing, and finding providers. How can I assist?"

    def _fallback(self, conv: Conversation, name: str) -> str:
        return f"Hi {name}, I'm your AI assistant. I can help with appointments, prescription refills, billing, and finding providers. What would you like to do?"

ENGINE = ResponseEngine()
